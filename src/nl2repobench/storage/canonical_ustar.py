"""Deterministic POSIX ustar archives and content-tree inventories."""

from __future__ import annotations

import hashlib
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal

RECORD_BYTES = 10_240
BLOCK_BYTES = 512
TREE_PREFIX = b"nl2repobench-tree-v1\0"
EntryType = Literal["file", "directory"]


class CanonicalUstarError(ValueError):
    """A tree cannot be represented by the canonical archive contract."""


@dataclass(frozen=True)
class CanonicalEntry:
    """One normalized archive member."""

    path: str
    type: EntryType
    mode: int
    data: bytes = b""

    @property
    def size(self) -> int:
        return len(self.data) if self.type == "file" else 0

    @property
    def sha256(self) -> str | None:
        return hashlib.sha256(self.data).hexdigest() if self.type == "file" else None


def _validated_path(value: str, *, directory: bool) -> str:
    if unicodedata.normalize("NFC", value) != value:
        raise CanonicalUstarError(f"archive path is not NFC: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise CanonicalUstarError(f"archive path is unsafe: {value!r}")
    normalized = path.as_posix() + ("/" if directory else "")
    if len(normalized.encode("utf-8")) > 255:
        raise CanonicalUstarError(f"archive path exceeds 255 UTF-8 bytes: {value!r}")
    return normalized


def entries_from_tree(
    root: Path, *, executable_paths: frozenset[str] = frozenset()
) -> tuple[CanonicalEntry, ...]:
    """Read a regular tree into normalized deterministic archive entries."""

    if root.is_symlink() or not root.is_dir():
        raise CanonicalUstarError(f"archive root must be a regular directory: {root}")
    entries: list[CanonicalEntry] = []
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().encode()
    ):
        relative = path.relative_to(root).as_posix()
        metadata = path.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not (
            stat.S_ISDIR(metadata.st_mode) or stat.S_ISREG(metadata.st_mode)
        ):
            raise CanonicalUstarError(f"archive tree contains an unsafe path: {relative}")
        if path.is_dir():
            entries.append(
                CanonicalEntry(
                    _validated_path(relative, directory=True), "directory", 0o555
                )
            )
        else:
            mode = 0o555 if relative in executable_paths else 0o444
            entries.append(
                CanonicalEntry(
                    _validated_path(relative, directory=False),
                    "file",
                    mode,
                    path.read_bytes(),
                )
            )
    return tuple(sorted(entries, key=lambda entry: (entry.path.encode("utf-8"), entry.type)))


def _split_name(path: str) -> tuple[bytes, bytes]:
    raw = path.encode("utf-8")
    if len(raw) <= 100:
        return raw, b""
    stripped = path[:-1] if path.endswith("/") else path
    suffix = "/" if path.endswith("/") else ""
    parts = stripped.split("/")
    for index in range(1, len(parts)):
        prefix = "/".join(parts[:index]).encode("utf-8")
        name = ("/".join(parts[index:]) + suffix).encode("utf-8")
        if len(prefix) <= 155 and len(name) <= 100:
            return name, prefix
    raise CanonicalUstarError(f"archive path cannot be split into ustar fields: {path!r}")


def _octal(value: int, length: int) -> bytes:
    digits = f"{value:0{length - 1}o}".encode("ascii")
    if len(digits) >= length:
        raise CanonicalUstarError(f"ustar numeric field exceeds {length} bytes: {value}")
    return digits + b"\0"


def _header(entry: CanonicalEntry) -> bytes:
    name, prefix = _split_name(entry.path)
    header = bytearray(BLOCK_BYTES)
    header[0 : len(name)] = name
    header[100:108] = _octal(entry.mode, 8)
    header[108:116] = _octal(0, 8)
    header[116:124] = _octal(0, 8)
    header[124:136] = _octal(entry.size, 12)
    header[136:148] = _octal(0, 12)
    header[148:156] = b"        "
    header[156:157] = b"5" if entry.type == "directory" else b"0"
    header[257:263] = b"ustar\0"
    header[263:265] = b"00"
    header[329:337] = _octal(0, 8)
    header[337:345] = _octal(0, 8)
    header[345 : 345 + len(prefix)] = prefix
    checksum = sum(header)
    header[148:156] = f"{checksum:06o}".encode("ascii") + b"\0 "
    return bytes(header)


def encode_ustar(entries: tuple[CanonicalEntry, ...]) -> bytes:
    """Encode a sorted closed-world entry sequence as canonical ustar bytes."""

    ordered = tuple(sorted(entries, key=lambda item: (item.path.encode("utf-8"), item.type)))
    if entries != ordered or len({entry.path for entry in entries}) != len(entries):
        raise CanonicalUstarError("archive entries must be sorted and unique")
    output = bytearray()
    for entry in entries:
        expected_mode = 0o555 if entry.type == "directory" else entry.mode
        if entry.type == "directory" and (entry.data or entry.mode != expected_mode):
            raise CanonicalUstarError("directory archive entries must be empty mode 0555")
        if entry.type == "file" and entry.mode not in {0o444, 0o555}:
            raise CanonicalUstarError("file archive mode must be 0444 or 0555")
        _validated_path(entry.path.removesuffix("/"), directory=entry.type == "directory")
        output.extend(_header(entry))
        if entry.type == "file":
            output.extend(entry.data)
            output.extend(b"\0" * ((-len(entry.data)) % BLOCK_BYTES))
    output.extend(b"\0" * (2 * BLOCK_BYTES))
    output.extend(b"\0" * ((-len(output)) % RECORD_BYTES))
    return bytes(output)


def tree_digest(entries: tuple[CanonicalEntry, ...]) -> str:
    """Hash normalized entry metadata and file contents independent of tar bytes."""

    digest = hashlib.sha256(TREE_PREFIX)
    for entry in entries:
        path = entry.path.encode("utf-8")
        digest.update(b"F" if entry.type == "file" else b"D")
        digest.update(len(path).to_bytes(8, "big"))
        digest.update(path)
        digest.update(entry.mode.to_bytes(4, "big"))
        digest.update(entry.size.to_bytes(8, "big"))
        digest.update(hashlib.sha256(entry.data).digest() if entry.type == "file" else b"\0" * 32)
    return "sha256:" + digest.hexdigest()


def inventory_entries(entries: tuple[CanonicalEntry, ...]) -> list[dict[str, object]]:
    """Project canonical entries into the persisted dependency inventory shape."""

    return [
        {
            "path": entry.path,
            "type": entry.type,
            "mode": f"{entry.mode:04o}",
            "size": entry.size,
            "sha256": "sha256:" + entry.sha256 if entry.sha256 is not None else None,
        }
        for entry in entries
    ]


__all__ = [
    "CanonicalEntry",
    "CanonicalUstarError",
    "encode_ustar",
    "entries_from_tree",
    "inventory_entries",
    "tree_digest",
]
