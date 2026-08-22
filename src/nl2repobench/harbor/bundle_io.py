"""Bounded, deterministic filesystem operations for Harbor bundles.

The compiler-specific modules keep ownership of artifact resolution and bundle
serialization.  This module owns the shared filesystem boundary: archive
members are kept below the destination, symlinks and special files are never
materialized, and declared/expanded sizes are checked before bytes are
written.
"""

from __future__ import annotations

import os
import stat
import tarfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from nl2repobench.storage.files import atomic_copy, atomic_write


class BundleIOError(ValueError):
    """Base error for a rejected or unreadable Harbor bundle filesystem input."""


class BundleArchiveError(BundleIOError):
    """Raised when an archive member violates the bundle contract."""


class BundleArchiveIOError(BundleArchiveError):
    """Raised when an archive cannot be opened or materialized safely."""


class BundleArchiveMemberCountError(BundleArchiveError):
    """Raised when an archive contains more than the configured member limit."""


class BundleArchivePathError(BundleArchiveError):
    """Raised when an archive member path is absolute or traverses a parent."""


class BundleArchiveLinkError(BundleArchiveError):
    """Raised when an archive contains a link or device member."""


class BundleArchiveDuplicateError(BundleArchiveError):
    """Raised when an archive contains the same normalized path more than once."""


class BundleArchiveMemberSizeError(BundleArchiveError):
    """Raised when one archive member exceeds the configured byte limit."""

    def __init__(self, member_name: str) -> None:
        self.member_name = member_name
        super().__init__(f"archive member size exceeds limit: {member_name}")


class BundleArchiveTotalSizeError(BundleArchiveError):
    """Raised when the expanded regular-file total exceeds its byte limit."""


class BundleArchiveMemberReadError(BundleArchiveError):
    """Raised when tarfile cannot provide the bytes declared for a regular file."""


class BundleArchiveMemberTypeError(BundleArchiveError):
    """Raised when an archive member is neither a directory nor a regular file."""


class BundleTreeError(BundleIOError):
    """Raised when a source tree cannot be copied under bundle invariants."""


class BundleTreeSourceError(BundleTreeError):
    """Raised when the source tree is missing or is itself a symlink."""


class BundleTreePathError(BundleTreeError):
    """Raised when a source or destination tree path is unsafe."""


@dataclass(frozen=True, slots=True)
class BundleLimits:
    """Limits applied while streaming a private archive into a bundle."""

    max_members: int
    max_member_bytes: int
    max_total_bytes: int


def extract_bundle_archive(archive: Path, destination: Path, *, limits: BundleLimits) -> None:
    """Extract a tar archive while enforcing bundle path, link, and size invariants.

    Member names are interpreted as POSIX paths and must be relative without
    ``..`` components.  Archive links and devices are rejected so extraction
    cannot redirect writes outside ``destination``.  Members are processed in
    archive order, while each regular file is copied atomically and bounded by
    both its declared size and the expanded archive total.  Existing symlink
    components in the destination are rejected as well.
    """

    try:
        _prepare_destination(destination, error_type=BundleArchivePathError)
        with tarfile.open(archive, mode="r:*") as handle:
            seen: set[PurePosixPath] = set()
            total_bytes = 0
            for member_count, member in enumerate(handle, start=1):
                if member_count > limits.max_members:
                    raise BundleArchiveMemberCountError(
                        "private bundle contains too many members"
                    )

                relative = PurePosixPath(member.name)
                if relative.is_absolute() or ".." in relative.parts:
                    raise BundleArchivePathError(f"archive path escapes bundle: {member.name}")
                if member.issym() or member.islnk() or member.isdev():
                    raise BundleArchiveLinkError(
                        f"archive links/devices are forbidden: {member.name}"
                    )
                if relative in seen:
                    raise BundleArchiveDuplicateError(
                        f"duplicate archive path: {member.name}"
                    )
                seen.add(relative)
                if member.size < 0 or member.size > limits.max_member_bytes:
                    raise BundleArchiveMemberSizeError(member.name)

                target = destination.joinpath(*relative.parts)
                _assert_no_symlink_components(
                    destination, target, error_type=BundleArchivePathError
                )
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    total_bytes += member.size
                    if total_bytes > limits.max_total_bytes:
                        raise BundleArchiveTotalSizeError(
                            "private bundle expanded size exceeds limit"
                        )
                    extracted = handle.extractfile(member)
                    if extracted is None:
                        raise BundleArchiveMemberReadError(
                            f"cannot read archive member: {member.name}"
                        )
                    atomic_copy(
                        target,
                        extracted,
                        expected_size=member.size,
                        max_size=limits.max_member_bytes,
                    )
                    os.chmod(target, stat.S_IMODE(member.mode) & 0o777)
                else:
                    raise BundleArchiveMemberTypeError(
                        f"unsupported archive member type: {member.name}"
                    )
    except BundleArchiveError:
        raise
    except (OSError, RuntimeError, tarfile.TarError) as exc:
        raise BundleArchiveIOError(str(exc)) from exc


def copy_bundle_tree(source: Path, destination: Path) -> None:
    """Copy a regular source tree deterministically without following symlinks.

    The source directory and every traversed entry must remain inside the
    resolved source root; symlinks are rejected rather than followed.  Entries
    are visited in sorted path order, regular-file bytes are written atomically,
    and their permission bits are copied.  Destination symlink components are
    rejected so a pre-existing output path cannot redirect the copy.
    """

    if not source.is_dir() or source.is_symlink():
        raise BundleTreeSourceError(f"fixture directory is missing: {source}")
    source_root = source.resolve()
    try:
        _prepare_destination(destination, error_type=BundleTreePathError)
        for path in sorted(source.rglob("*")):
            if path.is_symlink() or not path.resolve().is_relative_to(source_root):
                raise BundleTreePathError(f"fixture path escapes source root: {path}")
            relative = path.relative_to(source)
            target = destination / relative
            _assert_no_symlink_components(destination, target, error_type=BundleTreePathError)
            if path.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif path.is_file():
                atomic_write(target, path.read_bytes())
                os.chmod(target, stat.S_IMODE(path.stat().st_mode))
    except BundleTreeError:
        raise
    except OSError as exc:
        raise BundleTreePathError(str(exc)) from exc


def _prepare_destination(
    destination: Path, *, error_type: type[BundleIOError]
) -> None:
    """Create a destination after rejecting symlink components in its path."""

    _assert_no_symlink_components(destination, destination, error_type=error_type)
    destination.mkdir(parents=True, exist_ok=True)


def _assert_no_symlink_components(
    root: Path, path: Path, *, error_type: type[BundleIOError]
) -> None:
    """Reject symlink components while keeping ``path`` below ``root`` lexically."""

    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise error_type(f"bundle path escapes destination root: {path}") from exc

    current = root
    if current.is_symlink():
        raise error_type(f"bundle destination must not be a symlink: {current}")
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise error_type(f"bundle destination must not be a symlink: {current}")
