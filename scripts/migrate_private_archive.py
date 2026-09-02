#!/usr/bin/env python3
"""Convert a historical private tar artifact to the canonical USTAR form.

The conversion helper is intentionally byte-oriented so migration workers can
call it without granting the helper access to a CAS or a source tree.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import stat
import tarfile
import tempfile
from pathlib import Path
from typing import Any, cast

from nl2repobench.storage.canonical_ustar import (
    CanonicalArchiveError,
    TreeEntry,
    decode_archive,
    encode_entries,
    tree_digest,
)
from nl2repobench.storage.materialize import TARGET_MEDIA_TYPES, ArchiveKind

MAX_ARCHIVE_BYTES = 2 * 1024 * 1024 * 1024
MAX_MEMBERS = 100_000
MAX_MEMBER_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BYTES = 2 * 1024**3
MAX_PATH_BYTES = 255
EXECUTABLE_MEMBER_NAMES = frozenset(
    {"test.sh", "solve.sh", "run.py", "contract.sh", "verifier.sh"}
)
INTERNAL_INVENTORY = "_nl2repo.bundle-inventory.json"


class PrivateArchiveMigrationError(ValueError):
    """Raised when a historical archive cannot be safely canonicalized."""


class MigrationLimits:
    """Resource ceilings for one archive conversion."""

    __slots__ = (
        "max_archive_bytes",
        "max_members",
        "max_member_bytes",
        "max_total_bytes",
        "max_path_bytes",
    )

    def __init__(
        self,
        max_archive_bytes: int = MAX_ARCHIVE_BYTES,
        max_members: int = MAX_MEMBERS,
        max_member_bytes: int = MAX_MEMBER_BYTES,
        max_total_bytes: int = MAX_TOTAL_BYTES,
        max_path_bytes: int = MAX_PATH_BYTES,
    ) -> None:
        self.max_archive_bytes = max_archive_bytes
        self.max_members = max_members
        self.max_member_bytes = max_member_bytes
        self.max_total_bytes = max_total_bytes
        self.max_path_bytes = max_path_bytes
        self._validate()

    def _validate(self) -> None:
        values = (
            self.max_archive_bytes,
            self.max_members,
            self.max_member_bytes,
            self.max_total_bytes,
            self.max_path_bytes,
        )
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
            for value in values
        ):
            raise ValueError("migration limits must be positive integers")
        if self.max_archive_bytes > MAX_ARCHIVE_BYTES:
            raise ValueError("max_archive_bytes exceeds hard ceiling")
        if self.max_members > MAX_MEMBERS:
            raise ValueError("max_members exceeds hard ceiling")
        if self.max_member_bytes > MAX_MEMBER_BYTES:
            raise ValueError("max_member_bytes exceeds hard ceiling")
        if self.max_total_bytes > MAX_TOTAL_BYTES:
            raise ValueError("max_total_bytes exceeds hard ceiling")
        if self.max_path_bytes > MAX_PATH_BYTES:
            raise ValueError("max_path_bytes exceeds hard ceiling")


class MigrationResult:
    """Canonical archive bytes and metadata safe for migration receipts."""

    __slots__ = (
        "archive",
        "old_sha256",
        "old_size",
        "new_sha256",
        "new_size",
        "file_count",
        "tree_digest",
        "media_type",
    )

    def __init__(
        self,
        archive: bytes,
        old_sha256: str,
        old_size: int,
        new_sha256: str,
        new_size: int,
        file_count: int,
        tree_digest: str,
        media_type: str,
    ) -> None:
        self.archive = archive
        self.old_sha256 = old_sha256
        self.old_size = old_size
        self.new_sha256 = new_sha256
        self.new_size = new_size
        self.file_count = file_count
        self.tree_digest = tree_digest
        self.media_type = media_type

    def metadata(self) -> dict[str, object]:
        """Return metadata without exposing archive bytes."""

        return {
            "old_sha256": self.old_sha256,
            "old_size": self.old_size,
            "new_sha256": self.new_sha256,
            "new_size": self.new_size,
            "file_count": self.file_count,
            "tree_digest": self.tree_digest,
            "media_type": self.media_type,
        }


class _BoundedReader:
    """Limit decompressed stream bytes while retaining tar stream semantics."""

    def __init__(self, source: io.BufferedIOBase | gzip.GzipFile, limit: int) -> None:
        self.source = source
        self.limit = limit
        self.consumed = 0
        self.last_nonzero = -1

    def read(self, size: int = -1) -> bytes:
        if size < 0 or size > self.limit - self.consumed:
            size = self.limit - self.consumed + 1
        if size <= 0:
            raise PrivateArchiveMigrationError("archive exceeds decompressed size limit")
        chunk = self.source.read(size)
        self.consumed += len(chunk)
        if self.consumed > self.limit:
            raise PrivateArchiveMigrationError("archive exceeds decompressed size limit")
        if chunk:
            nonzero_prefix = chunk.rstrip(b"\0")
            if nonzero_prefix:
                self.last_nonzero = self.consumed - len(chunk) + len(nonzero_prefix) - 1
        return chunk


def _normalize_member_name(name: str, *, directory: bool, max_path_bytes: int) -> str:
    if not isinstance(name, str) or not name:
        raise PrivateArchiveMigrationError("archive member has an empty name")
    import unicodedata

    if unicodedata.normalize("NFC", name) != name:
        raise PrivateArchiveMigrationError("archive member path is not NFC normalized")
    if "\x00" in name or "\\" in name:
        raise PrivateArchiveMigrationError("archive member path is ambiguous")
    if name.startswith("/"):
        raise PrivateArchiveMigrationError("archive member path is absolute")
    if name.startswith("./"):
        name = name[2:]
        if not name or name.startswith("./"):
            raise PrivateArchiveMigrationError("archive member has ambiguous leading './'")
    if name.endswith("/"):
        if not directory or name.endswith("//"):
            raise PrivateArchiveMigrationError("archive member path has ambiguous trailing slash")
        name = name[:-1]
    if not name or name.startswith("/"):
        raise PrivateArchiveMigrationError("archive member has an unsafe empty name")
    parts = name.split("/")
    if any(not part or part in {".", ".."} for part in parts):
        raise PrivateArchiveMigrationError("archive member path is not normalized")
    if len(name.encode("utf-8")) > max_path_bytes:
        raise PrivateArchiveMigrationError("archive member path exceeds size limit")
    return name


def _check_path_conflict(path: str, member_type: str, entries: dict[str, str]) -> None:
    if path in entries:
        raise PrivateArchiveMigrationError(f"duplicate archive path: {path}")
    components = path.split("/")
    for index in range(1, len(components)):
        if entries.get("/".join(components[:index])) == "file":
            raise PrivateArchiveMigrationError(f"archive path conflicts with a file: {path}")
    if member_type == "file" and any(existing.startswith(path + "/") for existing in entries):
        raise PrivateArchiveMigrationError(f"archive path conflicts with a child: {path}")


def _open_stream(
    data: bytes, limits: MigrationLimits
) -> tuple[_BoundedReader, io.BytesIO | gzip.GzipFile]:
    raw = io.BytesIO(data)
    if data.startswith(b"\x1f\x8b"):
        source: io.BytesIO | gzip.GzipFile = gzip.GzipFile(fileobj=raw, mode="rb")
    else:
        source = raw
    # Every member requires a header and padding, in addition to the payload.
    decompressed_limit = min(
        MAX_ARCHIVE_BYTES,
        limits.max_total_bytes + limits.max_members * 1024 + 10 * 1024,
    )
    return _BoundedReader(source, decompressed_limit), source


def migrate_private_archive(
    data: bytes,
    kind: ArchiveKind | str,
    limits: MigrationLimits | None = None,
) -> MigrationResult:
    """Safely convert POSIX/GNU tar bytes to canonical USTAR bytes.

    This function has no filesystem or CAS side effects.  It accepts an
    uncompressed tar or a gzip-compressed tar and rejects every non-regular
    member type before producing output.
    """

    bounded = limits or MigrationLimits()
    if not isinstance(data, bytes):
        raise TypeError("archive input must be bytes")
    if len(data) > bounded.max_archive_bytes:
        raise PrivateArchiveMigrationError("archive exceeds input size limit")
    try:
        archive_kind = ArchiveKind(kind)
    except (TypeError, ValueError) as exc:
        raise PrivateArchiveMigrationError(f"unsupported archive kind: {kind!r}") from exc

    files: dict[str, bytes] = {}
    executable: set[str] = set()
    entries: dict[str, str] = {}
    member_ends: list[int] = []
    total_bytes = 0
    stream, source = _open_stream(data, bounded)
    try:
        try:
            archive = tarfile.open(fileobj=cast(Any, stream), mode="r|")
        except (tarfile.TarError, OSError, EOFError, ValueError) as exc:
            raise PrivateArchiveMigrationError("malformed tar archive") from exc
        with archive:
            try:
                for index, member in enumerate(archive, start=1):
                    if index > bounded.max_members:
                        raise PrivateArchiveMigrationError("archive contains too many members")
                    if member.isdir():
                        member_type = "directory"
                    elif member.type in {tarfile.REGTYPE, tarfile.AREGTYPE} and member.isfile():
                        member_type = "file"
                    else:
                        raise PrivateArchiveMigrationError("archive contains an unsafe member type")
                    # GNU tar commonly emits ``./`` as a container marker.
                    # It has no representable path in the canonical tree.
                    if member_type == "directory" and member.name in {".", "./"}:
                        if member.size != 0:
                            raise PrivateArchiveMigrationError(
                                "directory member has payload bytes"
                            )
                        member_ends.append(
                            member.offset + 512 + ((member.size + 511) // 512) * 512
                        )
                        continue
                    path = _normalize_member_name(
                        member.name,
                        directory=member_type == "directory",
                        max_path_bytes=bounded.max_path_bytes,
                    )
                    if path == INTERNAL_INVENTORY:
                        raise PrivateArchiveMigrationError(
                            "archive contains the reserved bundle inventory path"
                        )
                    _check_path_conflict(path, member_type, entries)
                    entries[path] = member_type
                    member_ends.append(
                        member.offset + 512 + ((member.size + 511) // 512) * 512
                    )
                    if member_type == "directory":
                        if member.size != 0:
                            raise PrivateArchiveMigrationError("directory member has payload bytes")
                        continue
                    if member.sparse:
                        raise PrivateArchiveMigrationError("sparse files are not supported")
                    if member.mode & 0o111 and Path(path).name not in EXECUTABLE_MEMBER_NAMES:
                        raise PrivateArchiveMigrationError(
                            f"executable archive member is not allowlisted: {path}"
                        )
                    if member.size < 0 or member.size > bounded.max_member_bytes:
                        raise PrivateArchiveMigrationError("archive member exceeds size limit")
                    if total_bytes + member.size > bounded.max_total_bytes:
                        raise PrivateArchiveMigrationError("archive exceeds total payload limit")
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        raise PrivateArchiveMigrationError("regular member payload is unavailable")
                    payload = extracted.read(member.size + 1)
                    if len(payload) != member.size:
                        raise PrivateArchiveMigrationError("regular member payload is truncated")
                    if extracted.read(1):
                        raise PrivateArchiveMigrationError("regular member payload is oversized")
                    files[path] = payload
                    total_bytes += len(payload)
                    if member.mode & 0o111:
                        executable.add(path)
            except PrivateArchiveMigrationError:
                raise
            except (tarfile.TarError, OSError, EOFError, gzip.BadGzipFile, ValueError) as exc:
                raise PrivateArchiveMigrationError("malformed tar archive") from exc
            stream.read()
            trailer_end = max(member_ends, default=0)
            if (
                stream.consumed - trailer_end < 2 * 512
                or stream.last_nonzero >= trailer_end
            ):
                raise PrivateArchiveMigrationError("malformed tar trailer")
        # Reading through EOF validates gzip trailers and rejects hidden bytes.
        if source.read(1):
            raise PrivateArchiveMigrationError("gzip stream has trailing data")
    except PrivateArchiveMigrationError:
        raise
    except (tarfile.TarError, OSError, EOFError, gzip.BadGzipFile, ValueError) as exc:
        raise PrivateArchiveMigrationError("malformed tar archive") from exc
    finally:
        source.close()

    try:
        # Legacy tar files are allowed to omit parent directory records, but
        # canonical materialization requires every parent to be explicit.
        for file_path in tuple(files) + tuple(
            path for path, member_type in entries.items() if member_type == "directory"
        ):
            parent = Path(file_path).parent
            while parent != Path("."):
                parent_name = parent.as_posix()
                if entries.get(parent_name) == "file":
                    raise PrivateArchiveMigrationError(
                        f"archive path conflicts with a file: {file_path}"
                    )
                entries.setdefault(parent_name, "directory")
                parent = parent.parent
        payload_entries = tuple(
            TreeEntry(
                path,
                member_type,
                0o555 if member_type == "directory" or path in executable else 0o444,
                0 if member_type == "directory" else len(files[path]),
                None if member_type == "directory" else hashlib.sha256(files[path]).hexdigest(),
            )
            for path, member_type in entries.items()
        )
        payload_pairs = tuple(
            (entry, None if entry.type == "directory" else files[entry.path])
            for entry in payload_entries
        )
        if archive_kind in {
            ArchiveKind.TEST_BUNDLE,
            ArchiveKind.VERIFIER_BUNDLE,
            ArchiveKind.ORACLE_BUNDLE,
        }:
            inventory = {
                "schema_version": "1.0",
                "archive_kind": archive_kind.value,
                "tree_digest": tree_digest(payload_entries),
                "entries": [
                    {
                        "path": entry.path,
                        "type": entry.type,
                        "mode": entry.mode,
                        "size": entry.size,
                        "sha256": entry.sha256,
                    }
                    for entry in sorted(
                        payload_entries, key=lambda item: (item.path.encode(), item.type)
                    )
                ],
                "file_count": sum(entry.type == "file" for entry in payload_entries),
                "directory_count": sum(entry.type == "directory" for entry in payload_entries),
                "total_bytes": sum(entry.size for entry in payload_entries),
            }
            inventory_data = (
                json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
                + b"\n"
            )
            inventory_entry = TreeEntry(
                INTERNAL_INVENTORY,
                "file",
                0o444,
                len(inventory_data),
                hashlib.sha256(inventory_data).hexdigest(),
            )
            output_pairs = (*payload_pairs, (inventory_entry, inventory_data))
        else:
            output_pairs = payload_pairs
        canonical = encode_entries(output_pairs)
        decode_archive(canonical)
    except CanonicalArchiveError as exc:
        raise PrivateArchiveMigrationError(
            "archive cannot be represented as canonical USTAR"
        ) from exc
    return MigrationResult(
        archive=canonical,
        old_sha256=f"sha256:{hashlib.sha256(data).hexdigest()}",
        old_size=len(data),
        new_sha256=f"sha256:{hashlib.sha256(canonical).hexdigest()}",
        new_size=len(canonical),
        file_count=sum(entry.type == "file" for entry in payload_entries),
        tree_digest=tree_digest(payload_entries),
        media_type=TARGET_MEDIA_TYPES[archive_kind],
    )


def _read_regular(path: Path, max_bytes: int) -> bytes:
    cursor = path.parent
    while cursor != cursor.parent:
        if cursor.is_symlink():
            raise PrivateArchiveMigrationError("input path parent must not contain symlinks")
        cursor = cursor.parent
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise PrivateArchiveMigrationError(f"cannot open input archive: {path}") from exc
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise PrivateArchiveMigrationError("input archive must be a regular file")
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            data = handle.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise PrivateArchiveMigrationError("input archive exceeds size limit")
        return data
    finally:
        if descriptor != -1:
            os.close(descriptor)


def _write_regular(path: Path, data: bytes) -> None:
    parent = path.parent
    cursor = parent
    while cursor != cursor.parent:
        if cursor.is_symlink():
            raise PrivateArchiveMigrationError("output parent must not contain symlinks")
        cursor = cursor.parent
    parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise PrivateArchiveMigrationError("output must not be a symlink")
    if path.exists():
        raise PrivateArchiveMigrationError(f"output already exists: {path}")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise PrivateArchiveMigrationError(f"output already exists: {path}") from exc
        os.unlink(temporary)
    finally:
        if descriptor != -1:
            os.close(descriptor)
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--kind", choices=tuple(kind.value for kind in ArchiveKind), required=True)
    parser.add_argument("--max-archive-bytes", type=int, default=MAX_ARCHIVE_BYTES)
    parser.add_argument("--max-members", type=int, default=MAX_MEMBERS)
    parser.add_argument("--max-member-bytes", type=int, default=MAX_MEMBER_BYTES)
    parser.add_argument("--max-total-bytes", type=int, default=MAX_TOTAL_BYTES)
    parser.add_argument("--max-path-bytes", type=int, default=MAX_PATH_BYTES)
    args = parser.parse_args()
    try:
        limits = MigrationLimits(
            max_archive_bytes=args.max_archive_bytes,
            max_members=args.max_members,
            max_member_bytes=args.max_member_bytes,
            max_total_bytes=args.max_total_bytes,
            max_path_bytes=args.max_path_bytes,
        )
        source = _read_regular(args.input, limits.max_archive_bytes)
        result = migrate_private_archive(source, args.kind, limits)
        _write_regular(args.output, result.archive)
    except (OSError, PrivateArchiveMigrationError, TypeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps(result.metadata(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MAX_ARCHIVE_BYTES",
    "MAX_MEMBERS",
    "MAX_MEMBER_BYTES",
    "MAX_PATH_BYTES",
    "MAX_TOTAL_BYTES",
    "MigrationLimits",
    "MigrationResult",
    "PrivateArchiveMigrationError",
    "migrate_private_archive",
]
