"""Bounded CAS archive materialization for compiler and verifier staging."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import cast

from nl2repobench.domain.models import ArtifactRef

from .artifacts import (
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
    PublicArtifactAuthorization,
)
from .canonical_ustar import CanonicalArchiveError, TreeEntry, decode_archive, tree_digest


class ArchiveKind(StrEnum):
    DEPENDENCY_LOCK = "dependency-lock"
    OFFLINE_STORE = "offline-store"
    TEST_BUNDLE = "test-bundle"
    VERIFIER_BUNDLE = "verifier-bundle"
    ORACLE_BUNDLE = "oracle-bundle"


@dataclass(frozen=True, slots=True)
class MaterializationLimits:
    max_members: int
    max_member_bytes: int
    max_total_bytes: int
    max_path_bytes: int = 255


@dataclass(frozen=True, slots=True)
class MaterializationResult:
    destination: Path
    file_count: int
    total_bytes: int
    tree_digest: str
    inventory_digest: str | None = None


HARD_LIMITS: dict[ArchiveKind, MaterializationLimits] = {
    ArchiveKind.DEPENDENCY_LOCK: MaterializationLimits(64, 4 * 1024 * 1024, 16 * 1024 * 1024),
    ArchiveKind.OFFLINE_STORE: MaterializationLimits(100_000, 512 * 1024 * 1024, 2 * 1024**3),
    ArchiveKind.TEST_BUNDLE: MaterializationLimits(10_000, 512 * 1024 * 1024, 2 * 1024**3),
    ArchiveKind.VERIFIER_BUNDLE: MaterializationLimits(10_000, 512 * 1024 * 1024, 2 * 1024**3),
    ArchiveKind.ORACLE_BUNDLE: MaterializationLimits(10_000, 512 * 1024 * 1024, 2 * 1024**3),
}
TARGET_MEDIA_TYPES = {
    ArchiveKind.DEPENDENCY_LOCK: "application/vnd.nl2repobench.package-lock.tar",
    ArchiveKind.OFFLINE_STORE: "application/vnd.nl2repobench.offline-store.tar",
    ArchiveKind.TEST_BUNDLE: "application/vnd.nl2repobench.test-bundle.tar",
    ArchiveKind.VERIFIER_BUNDLE: "application/vnd.nl2repobench.verifier-bundle.tar",
    ArchiveKind.ORACLE_BUNDLE: "application/vnd.nl2repobench.oracle-bundle.tar",
}
INTERNAL_INVENTORY = "_nl2repo.bundle-inventory.json"


def _bounded_limits(
    kind: ArchiveKind, limits: MaterializationLimits | None
) -> MaterializationLimits:
    hard = HARD_LIMITS[kind]
    if limits is None:
        return hard
    if any(
        actual > maximum
        for actual, maximum in zip(
            (
                limits.max_members,
                limits.max_member_bytes,
                limits.max_total_bytes,
                limits.max_path_bytes,
            ),
            (hard.max_members, hard.max_member_bytes, hard.max_total_bytes, hard.max_path_bytes),
            strict=True,
        )
    ):
        raise ValueError("materialization limits cannot exceed hard ceilings")
    return limits


def _member_path(name: str, max_bytes: int) -> PurePosixPath:
    if unicodedata.normalize("NFC", name) != name:
        raise ValueError(f"archive member path is not NFC normalized: {name}")
    raw = name.rstrip("/")
    path = PurePosixPath(raw)
    if len(name.encode("utf-8")) > max_bytes or path.is_absolute() or not raw or ".." in path.parts:
        raise ValueError(f"unsafe archive member path: {name}")
    if any(part in {"", "."} for part in path.parts):
        raise ValueError(f"non-normalized archive member path: {name}")
    return path


def _inventory_tree_digest(payload: object) -> str:
    if not isinstance(payload, dict) or not isinstance(payload.get("tree_digest"), str):
        raise ValueError("bundle inventory tree digest is malformed")
    value = cast(str, payload["tree_digest"])
    if len(value) != 71 or not value.startswith("sha256:"):
        raise ValueError("bundle inventory tree digest is malformed")
    try:
        bytes.fromhex(value.removeprefix("sha256:"))
    except ValueError as exc:
        raise ValueError("bundle inventory tree digest is malformed") from exc
    return value


def _inventory_entries(payload: object, kind: ArchiveKind) -> tuple[dict[str, object], ...]:
    required = {
        "schema_version",
        "archive_kind",
        "tree_digest",
        "entries",
        "file_count",
        "directory_count",
        "total_bytes",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        raise ValueError("bundle inventory has unexpected fields")
    if payload["schema_version"] != "1.0" or payload["archive_kind"] != kind.value:
        raise ValueError("bundle inventory identity is invalid")
    entries = payload["entries"]
    if not isinstance(entries, list):
        raise ValueError("bundle inventory entries must be an array")
    result: list[dict[str, object]] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "type", "mode", "size", "sha256"}:
            raise ValueError("bundle inventory entry is malformed")
        if not isinstance(entry["path"], str) or not isinstance(entry["type"], str):
            raise ValueError("bundle inventory entry identity is malformed")
        _member_path(entry["path"], 255)
        if entry["type"] not in {"file", "directory"}:
            raise ValueError("bundle inventory entry type is invalid")
        if (
            entry["mode"] not in {0o444, 0o555}
            or not isinstance(entry["size"], int)
            or entry["size"] < 0
        ):
            raise ValueError("bundle inventory entry metadata is invalid")
        if entry["type"] == "file":
            if not isinstance(entry["sha256"], str) or len(entry["sha256"]) != 64:
                raise ValueError("bundle inventory file hash is invalid")
            try:
                bytes.fromhex(entry["sha256"])
            except ValueError as exc:
                raise ValueError("bundle inventory file hash is invalid") from exc
        elif entry["size"] != 0 or entry["sha256"] is not None:
            raise ValueError("bundle inventory directory metadata is invalid")
        result.append(entry)
    if result != sorted(result, key=lambda item: (str(item["path"]).encode(), str(item["type"]))):
        raise ValueError("bundle inventory entries are not sorted")
    if len({str(entry["path"]) for entry in result}) != len(result):
        raise ValueError("bundle inventory contains duplicate paths")
    if payload["file_count"] != sum(entry["type"] == "file" for entry in result):
        raise ValueError("bundle inventory file count is incorrect")
    if payload["directory_count"] != sum(entry["type"] == "directory" for entry in result):
        raise ValueError("bundle inventory directory count is incorrect")
    if payload["total_bytes"] != sum(cast(int, entry["size"]) for entry in result):
        raise ValueError("bundle inventory total size is incorrect")
    _inventory_tree_digest(payload)
    return tuple(result)


def _entry_payload(entries: list[TreeEntry]) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "path": entry.path,
            "type": entry.type,
            "mode": entry.mode,
            "size": entry.size,
            "sha256": entry.sha256,
        }
        for entry in sorted(entries, key=lambda item: (item.path.encode(), item.type))
    )


def _extract_with_openat(root: Path, entries: list[tuple[TreeEntry, bytes | None]]) -> None:
    """Write a validated tree without following any path component."""

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    root_fd = os.open(root, os.O_RDONLY | directory | nofollow)
    try:
        for entry, data in entries:
            parts = PurePosixPath(entry.path).parts
            parent_fd = os.dup(root_fd)
            try:
                for component in parts[:-1]:
                    try:
                        child_fd = os.open(
                            component, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd
                        )
                    except FileNotFoundError:
                        os.mkdir(component, 0o700, dir_fd=parent_fd)
                        child_fd = os.open(
                            component, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd
                        )
                    os.close(parent_fd)
                    parent_fd = child_fd
                leaf = parts[-1]
                if entry.type == "directory":
                    try:
                        os.mkdir(leaf, 0o700, dir_fd=parent_fd)
                    except FileExistsError:
                        child_fd = os.open(
                            leaf, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd
                        )
                        os.close(child_fd)
                    continue
                assert data is not None
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow
                file_fd = os.open(leaf, flags, 0o600, dir_fd=parent_fd)
                try:
                    view = memoryview(data)
                    while view:
                        written = os.write(file_fd, view)
                        view = view[written:]
                    os.fsync(file_fd)
                    os.fchmod(file_fd, entry.mode)
                finally:
                    os.close(file_fd)
            finally:
                os.close(parent_fd)
    finally:
        os.close(root_fd)


def materialize_archive(
    ref: ArtifactRef,
    kind: ArchiveKind,
    destination: Path,
    limits: MaterializationLimits | None,
    authorization: PrivateArtifactAuthorization | PublicArtifactAuthorization | None,
    *,
    resolver: LocalArtifactResolver | None = None,
    inventory_ref: ArtifactRef | None = None,
    inventory_section: str | None = None,
) -> MaterializationResult:
    """Extract one verified archive atomically into ``destination``."""

    bounded = _bounded_limits(kind, limits)
    if ref.media_type != TARGET_MEDIA_TYPES[kind]:
        raise ValueError(f"artifact media type does not match {kind.value}")
    if resolver is None:
        raise ValueError("a local artifact resolver is required")
    archive_limit = bounded.max_total_bytes + bounded.max_members * 1024 + 10240
    archive = resolver.read_bytes(ref, authorization, max_bytes=archive_limit)
    if isinstance(authorization, PrivateArtifactAuthorization):
        if not destination.resolve().is_relative_to(authorization.staging_root.resolve()):
            raise ValueError("private materialization destination is outside scoped staging root")
    cursor = destination.parent
    while cursor != cursor.parent:
        if cursor.is_symlink():
            raise ValueError("materialization destination parent must not contain symlinks")
        cursor = cursor.parent
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{destination.name}-", dir=destination.parent))
    try:
        entries: list[TreeEntry] = []
        extracted: list[tuple[TreeEntry, bytes | None]] = []
        total = 0
        internal_inventory: bytes | None = None
        try:
            members = decode_archive(archive)
        except CanonicalArchiveError as exc:
            raise ValueError(str(exc)) from exc
        if len(members) > bounded.max_members:
            raise ValueError("archive contains too many members")
        for member in members:
            entry = member.entry
            _member_path(entry.path, bounded.max_path_bytes)
            if entry.path == INTERNAL_INVENTORY:
                if entry.type != "file" or entry.size > bounded.max_member_bytes:
                    raise ValueError("bundle inventory must be a bounded regular file")
                internal_inventory = member.data
                continue
            if (
                entry.type == "file"
                and entry.mode == 0o555
                and Path(entry.path).name
                not in {"test.sh", "solve.sh", "run.py", "contract.sh", "verifier.sh"}
            ):
                raise ValueError(f"executable archive member is not allowlisted: {entry.path}")
            if (
                entry.size > bounded.max_member_bytes
                or total + entry.size > bounded.max_total_bytes
            ):
                raise ValueError(f"archive member exceeds size limits: {entry.path}")
            total += entry.size
            entries.append(entry)
            extracted.append((entry, member.data))
        entry_types = {entry.path: entry.type for entry in entries}
        for entry in entries:
            parent = PurePosixPath(entry.path).parent
            while parent != PurePosixPath("."):
                if entry_types.get(parent.as_posix()) != "directory":
                    raise ValueError(f"archive omits declared parent directory: {parent}")
                parent = parent.parent

        if (
            kind
            in {
                ArchiveKind.TEST_BUNDLE,
                ArchiveKind.VERIFIER_BUNDLE,
                ArchiveKind.ORACLE_BUNDLE,
            }
            and inventory_ref is not None
        ):
            raise ValueError("external inventory is forbidden for test/verifier/oracle bundles")
        if (
            kind not in {ArchiveKind.DEPENDENCY_LOCK, ArchiveKind.OFFLINE_STORE}
            and internal_inventory is None
        ):
            raise ValueError("bundle inventory is missing")
        if (
            kind not in {ArchiveKind.DEPENDENCY_LOCK, ArchiveKind.OFFLINE_STORE}
            and internal_inventory is not None
        ):
            payload = json.loads(internal_inventory)
            canonical_inventory = (
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
            )
            if internal_inventory != canonical_inventory:
                raise ValueError("internal bundle inventory is not canonical JSON")
            declared = _inventory_entries(payload, kind)
            if declared != _entry_payload(entries):
                raise ValueError("internal bundle inventory does not match archive")
            declared_tree_digest = _inventory_tree_digest(payload)
            inventory_digest = f"sha256:{hashlib.sha256(internal_inventory).hexdigest()}"
        else:
            declared_tree_digest = None
            inventory_digest = None
        if inventory_ref is not None:
            if inventory_section not in {"lock", "store"}:
                raise ValueError("dependency inventory section must be lock or store")
            if inventory_ref.media_type != "application/vnd.nl2repobench.inventory+json":
                raise ValueError("external inventory has invalid media type")
            inventory = resolver.read_bytes(inventory_ref, authorization, max_bytes=4 * 1024 * 1024)
            payload = json.loads(inventory)
            canonical_inventory = (
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
            )
            if inventory != canonical_inventory:
                raise ValueError("external inventory is not canonical JSON")
            if not isinstance(payload, dict) or set(payload) != {
                "schema_version",
                "identity",
                "adapter_version",
                "toolchain_digest",
                "lock",
                "store",
                "offline_smoke",
            }:
                raise ValueError("external inventory has unexpected fields")
            if payload["schema_version"] != "1.0":
                raise ValueError("external inventory schema is invalid")
            if not isinstance(payload["identity"], str) or "+" not in payload["identity"]:
                raise ValueError("external inventory identity is invalid")
            if not isinstance(payload["adapter_version"], str) or not payload["adapter_version"]:
                raise ValueError("external inventory adapter version is invalid")
            if (
                not isinstance(payload["toolchain_digest"], str)
                or not payload["toolchain_digest"].startswith("sha256:")
                or len(payload["toolchain_digest"]) != 71
            ):
                raise ValueError("external inventory toolchain digest is invalid")
            try:
                bytes.fromhex(payload["toolchain_digest"].removeprefix("sha256:"))
            except ValueError as exc:
                raise ValueError("external inventory toolchain digest is invalid") from exc
            if (
                not isinstance(payload["offline_smoke"], dict)
                or set(payload["offline_smoke"]) != {"status", "command_id"}
                or payload["offline_smoke"].get("status") != "passed"
                or not isinstance(payload["offline_smoke"].get("command_id"), str)
                or not payload["offline_smoke"].get("command_id")
            ):
                raise ValueError("external inventory offline smoke is invalid")
            section = payload[inventory_section]
            if not isinstance(section, dict):
                raise ValueError("external inventory section is malformed")
            declared = _inventory_entries(
                {
                    "schema_version": "1.0",
                    **{key: value for key, value in section.items() if key != "archive_digest"},
                },
                kind,
            )
            if section["archive_digest"] != ref.digest or declared != _entry_payload(entries):
                raise ValueError("external inventory does not match archive")
            declared_tree_digest = _inventory_tree_digest(section)
            inventory_digest = inventory_ref.digest
        elif kind in {ArchiveKind.DEPENDENCY_LOCK, ArchiveKind.OFFLINE_STORE}:
            raise ValueError("dependency archive requires an external inventory")
        result_digest = tree_digest(entries)
        if declared_tree_digest != result_digest:
            raise ValueError("inventory tree digest does not match materialized archive")
        _extract_with_openat(temporary, extracted)
        for output_path in temporary.rglob("*"):
            if output_path.is_dir():
                os.chmod(output_path, 0o555)
        os.chmod(temporary, 0o555)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"materialization destination already exists: {destination}")
        os.replace(temporary, destination)
        return MaterializationResult(
            destination,
            sum(item.type == "file" for item in entries),
            total,
            result_digest,
            inventory_digest,
        )
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


__all__ = [
    "ArchiveKind",
    "HARD_LIMITS",
    "MaterializationLimits",
    "MaterializationResult",
    "materialize_archive",
]
