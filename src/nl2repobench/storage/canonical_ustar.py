"""Canonical POSIX ustar archives used by the unified artifact contract.

The encoder is intentionally small and does not delegate format decisions to
``tarfile``.  Archive bytes are part of the task identity, so every header,
path, mode, and padding byte is specified here.
"""

from __future__ import annotations

import hashlib
import io
import os
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class CanonicalArchiveError(ValueError):
    """Raised when a tree cannot be represented by the canonical archive."""


EMPTY_TREE_DIGEST = "sha256:56b0e6f8e2ffbf069c1319192b76aee5bcc431328aca04d4835abeeaed461579"
_TREE_PREFIX = b"nl2repobench-tree-v1\0"


@dataclass(frozen=True, slots=True)
class TreeEntry:
    path: str
    type: str
    mode: int
    size: int
    sha256: str | None


@dataclass(frozen=True, slots=True)
class ArchiveMember:
    """One fully validated member from a canonical USTAR archive."""

    entry: TreeEntry
    data: bytes | None


def _path(path: str) -> PurePosixPath:
    if not isinstance(path, str) or not path or "\\" in path:
        raise CanonicalArchiveError(f"invalid archive path: {path!r}")
    if unicodedata.normalize("NFC", path) != path:
        raise CanonicalArchiveError(f"archive path is not NFC normalized: {path!r}")
    encoded = path.encode("utf-8")
    if len(encoded) > 255:
        raise CanonicalArchiveError("archive path exceeds 255 UTF-8 bytes")
    value = PurePosixPath(path)
    if value.is_absolute() or any(part in {"", ".", ".."} for part in value.parts):
        raise CanonicalArchiveError(f"archive path is not a normalized relative path: {path!r}")
    # POSIX path strings in the source contract must already be NFC.  Avoid
    # normalizing here because normalization would change content identity.
    return value


def tree_digest(entries: tuple[TreeEntry, ...] | list[TreeEntry]) -> str:
    """Hash a tree using the byte-level digest algorithm from the F0 contract."""

    digest = hashlib.sha256(_TREE_PREFIX)
    ordered = sorted(entries, key=lambda item: (item.path.encode("utf-8"), item.type))
    for entry in ordered:
        path = _path(entry.path).as_posix().encode("utf-8")
        if entry.type not in {"file", "directory"}:
            raise CanonicalArchiveError(f"unsupported tree entry type: {entry.type}")
        if entry.mode not in {0o444, 0o555}:
            raise CanonicalArchiveError(f"unsupported normalized mode: {entry.mode:o}")
        if entry.size < 0:
            raise CanonicalArchiveError("tree entry size cannot be negative")
        digest.update(b"F" if entry.type == "file" else b"D")
        digest.update(len(path).to_bytes(8, "big"))
        digest.update(path)
        digest.update(entry.mode.to_bytes(4, "big"))
        digest.update(entry.size.to_bytes(8, "big"))
        if entry.type == "file":
            if entry.sha256 is None or len(entry.sha256) != 64:
                raise CanonicalArchiveError(f"file entry has no SHA-256: {entry.path}")
            try:
                digest.update(bytes.fromhex(entry.sha256))
            except ValueError as exc:
                raise CanonicalArchiveError(
                    f"file entry has invalid SHA-256: {entry.path}"
                ) from exc
        else:
            if entry.size != 0 or entry.sha256 is not None:
                raise CanonicalArchiveError(f"directory entry has file metadata: {entry.path}")
            digest.update(b"\0" * 32)
    return f"sha256:{digest.hexdigest()}"


def tree_entries(root: Path) -> tuple[TreeEntry, ...]:
    """Scan a regular tree without following links or special files."""

    if root.is_symlink() or not root.is_dir():
        raise CanonicalArchiveError(f"tree root must be a regular directory: {root}")
    result: list[TreeEntry] = []
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().encode()
    ):
        relative = path.relative_to(root).as_posix()
        _path(relative)
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise CanonicalArchiveError(f"tree contains unsafe member: {relative}")
        if stat.S_ISDIR(mode):
            result.append(TreeEntry(relative, "directory", 0o555, 0, None))
        else:
            data = path.read_bytes()
            file_mode = 0o555 if mode & 0o111 else 0o444
            result.append(
                TreeEntry(relative, "file", file_mode, len(data), hashlib.sha256(data).hexdigest())
            )
    return tuple(result)


def _octal(value: int, width: int) -> bytes:
    text = format(value, "o").encode("ascii")
    if len(text) > width - 1:
        raise CanonicalArchiveError("ustar numeric field overflow")
    return b"0" * (width - len(text) - 1) + text + b"\0"


def _split_path(path: str, *, directory: bool = False) -> tuple[bytes, bytes]:
    value = _path(path)
    encoded = value.as_posix().encode("utf-8")
    suffix = b"/" if directory else b""
    if len(encoded) + len(suffix) <= 100:
        return b"", encoded + suffix
    components = value.parts
    for index in range(1, len(components)):
        prefix = "/".join(components[:index]).encode("utf-8")
        name = "/".join(components[index:]).encode("utf-8") + suffix
        if len(prefix) <= 155 and len(name) <= 100:
            return prefix, name
    raise CanonicalArchiveError(f"path cannot be represented in ustar header: {path}")


def _header(entry: TreeEntry) -> bytes:
    header_path = entry.path.rstrip("/")
    prefix, name = _split_path(header_path, directory=entry.type == "directory")
    header = bytearray(512)
    header[0:100] = name.ljust(100, b"\0")
    header[100:108] = _octal(entry.mode, 8)
    header[108:116] = _octal(0, 8)
    header[116:124] = _octal(0, 8)
    header[124:136] = _octal(entry.size, 12)
    header[136:148] = _octal(0, 12)
    header[148:156] = b" " * 8
    header[156:157] = b"5" if entry.type == "directory" else b"0"
    header[257:263] = b"ustar\0"
    header[263:265] = b"00"
    header[345:500] = prefix.ljust(155, b"\0")
    checksum = sum(header)
    header[148:156] = format(checksum, "06o").encode("ascii") + b"\0 "
    return bytes(header)


def decode_archive(data: bytes) -> tuple[ArchiveMember, ...]:
    """Decode only the exact canonical USTAR encoding emitted by this module."""

    if len(data) < 10240 or len(data) % 10240:
        raise CanonicalArchiveError("canonical ustar size must be a positive 10240-byte multiple")
    members: list[ArchiveMember] = []
    seen: set[str] = set()
    offset = 0
    while offset + 512 <= len(data):
        header = data[offset : offset + 512]
        if header == b"\0" * 512:
            if data[offset:] != b"\0" * (len(data) - offset):
                raise CanonicalArchiveError("canonical ustar trailer contains non-zero bytes")
            if len(data) - offset < 1024:
                raise CanonicalArchiveError("canonical ustar trailer is incomplete")
            break
        if header[257:263] != b"ustar\0" or header[263:265] != b"00":
            raise CanonicalArchiveError("archive is not canonical POSIX ustar")
        try:
            name = header[0:100].split(b"\0", 1)[0]
            prefix = header[345:500].split(b"\0", 1)[0]
            raw_path = prefix + (b"/" if prefix else b"") + name
            path_text = raw_path.decode("utf-8")
            member_type = header[156:157]
            entry_type = "directory" if member_type == b"5" else "file"
            if member_type not in {b"0", b"5"}:
                raise CanonicalArchiveError("canonical ustar member type is invalid")
            if entry_type == "directory":
                if not path_text.endswith("/"):
                    raise CanonicalArchiveError("canonical directory member must end in slash")
                path_text = path_text[:-1]
            mode = int(header[100:108].rstrip(b"\0") or b"0", 8)
            size = int(header[124:136].rstrip(b"\0") or b"0", 8)
        except (UnicodeDecodeError, ValueError) as exc:
            raise CanonicalArchiveError("canonical ustar header is malformed") from exc
        normalized = _path(path_text).as_posix()
        if normalized in seen:
            raise CanonicalArchiveError(f"duplicate archive path: {normalized}")
        seen.add(normalized)
        payload_start = offset + 512
        payload_end = payload_start + size
        padded_end = payload_start + ((size + 511) // 512) * 512
        if padded_end > len(data):
            raise CanonicalArchiveError("canonical ustar payload is truncated")
        payload = data[payload_start:payload_end]
        if data[payload_end:padded_end] != b"\0" * (padded_end - payload_end):
            raise CanonicalArchiveError("canonical ustar payload padding is non-zero")
        if entry_type == "directory" and size != 0:
            raise CanonicalArchiveError("canonical directory member has payload bytes")
        if (entry_type == "directory" and mode != 0o555) or (
            entry_type == "file" and mode not in {0o444, 0o555}
        ):
            raise CanonicalArchiveError("canonical ustar member mode is invalid")
        entry = TreeEntry(
            normalized,
            entry_type,
            mode,
            size,
            hashlib.sha256(payload).hexdigest() if entry_type == "file" else None,
        )
        if header != _header(entry):
            raise CanonicalArchiveError("archive header is not in canonical USTAR form")
        members.append(ArchiveMember(entry, payload if entry_type == "file" else None))
        offset = padded_end
    else:
        raise CanonicalArchiveError("canonical ustar trailer is missing")
    ordered = sorted(members, key=lambda item: (item.entry.path.encode("utf-8"), item.entry.type))
    if members != ordered:
        raise CanonicalArchiveError("canonical ustar members are not sorted")
    return tuple(members)


def encode_tree(root: Path) -> bytes:
    """Encode ``root`` as deterministic ustar bytes, including empty trees."""

    entries = tree_entries(root)
    output = io.BytesIO()
    for entry in sorted(entries, key=lambda item: (item.path.encode("utf-8"), item.type)):
        output.write(_header(entry))
        if entry.type == "file":
            data = (root / entry.path).read_bytes()
            output.write(data)
            output.write(b"\0" * ((-len(data)) % 512))
    output.write(b"\0" * 1024)
    data = output.getvalue()
    data += b"\0" * ((-len(data)) % 10240)
    return data


def encode_files(files: dict[str, bytes], executable: frozenset[str] = frozenset()) -> bytes:
    """Encode an in-memory tree, useful for migration and golden fixtures."""

    import tempfile

    with tempfile.TemporaryDirectory(prefix="nl2repo-ustar-") as temporary:
        root = Path(temporary)
        for name, data in files.items():
            relative = _path(name)
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            if name in executable:
                os.chmod(target, 0o755)
        return encode_tree(root)


__all__ = [
    "ArchiveMember",
    "CanonicalArchiveError",
    "EMPTY_TREE_DIGEST",
    "TreeEntry",
    "decode_archive",
    "encode_files",
    "encode_tree",
    "tree_digest",
    "tree_entries",
]
