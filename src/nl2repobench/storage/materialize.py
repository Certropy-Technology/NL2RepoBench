"""Bounded CAS archive materialization for compiler and verifier staging."""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import tarfile
import tempfile
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
from .canonical_ustar import TreeEntry, tree_digest


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
    raw = name.rstrip("/")
    path = PurePosixPath(raw)
    if len(name.encode("utf-8")) > max_bytes or path.is_absolute() or not raw or ".." in path.parts:
        raise ValueError(f"unsafe archive member path: {name}")
    if any(part in {"", "."} for part in path.parts):
        raise ValueError(f"non-normalized archive member path: {name}")
    return path


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
    archive = resolver.read_bytes(ref, authorization, max_bytes=bounded.max_total_bytes * 2)
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
        seen: set[str] = set()
        total = 0
        internal_inventory: bytes | None = None
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as handle:
            member_count = 0
            for member in handle:
                member_count += 1
                if member_count > bounded.max_members:
                    raise ValueError("archive contains too many members")
                path = _member_path(member.name, bounded.max_path_bytes)
                name = path.as_posix()
                if name in seen:
                    raise ValueError(f"duplicate archive path: {name}")
                seen.add(name)
                if name == INTERNAL_INVENTORY:
                    if not member.isfile():
                        raise ValueError("bundle inventory must be a regular file")
                    if member.size > bounded.max_member_bytes:
                        raise ValueError("bundle inventory exceeds member limit")
                    source = handle.extractfile(member)
                    internal_inventory = source.read(member.size + 1) if source else None
                    if internal_inventory is None or len(internal_inventory) != member.size:
                        raise ValueError("bundle inventory cannot be read")
                    continue
                mode = member.mode & 0o777
                if (
                    member.issym()
                    or member.islnk()
                    or member.isdev()
                    or not (member.isdir() or member.isfile())
                ):
                    raise ValueError(f"unsafe archive member type: {name}")
                if (
                    member.isfile()
                    and mode & 0o111
                    and Path(name).name
                    not in {"test.sh", "solve.sh", "run.py", "contract.sh", "verifier.sh"}
                ):
                    raise ValueError(f"executable archive member is not allowlisted: {name}")
                target = temporary / path
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=False)
                    entries.append(TreeEntry(name, "directory", 0o555, 0, None))
                    continue
                if (
                    member.size > bounded.max_member_bytes
                    or total + member.size > bounded.max_total_bytes
                ):
                    raise ValueError(f"archive member exceeds size limits: {name}")
                source = handle.extractfile(member)
                if source is None:
                    raise ValueError(f"archive member cannot be read: {name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                data = source.read(member.size + 1)
                if len(data) != member.size:
                    raise ValueError(f"archive member size mismatch: {name}")
                target.write_bytes(data)
                os.chmod(target, 0o555 if mode & 0o111 else 0o444)
                total += len(data)
                entries.append(
                    TreeEntry(
                        name,
                        "file",
                        0o555 if mode & 0o111 else 0o444,
                        len(data),
                        hashlib.sha256(data).hexdigest(),
                    )
                )

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
            declared = _inventory_entries(payload, kind)
            if declared != _entry_payload(entries):
                raise ValueError("internal bundle inventory does not match archive")
        if inventory_ref is not None:
            if inventory_section not in {"lock", "store"}:
                raise ValueError("dependency inventory section must be lock or store")
            if inventory_ref.media_type != "application/vnd.nl2repobench.inventory+json":
                raise ValueError("external inventory has invalid media type")
            inventory = resolver.read_bytes(inventory_ref, authorization, max_bytes=4 * 1024 * 1024)
            payload = json.loads(inventory)
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
            section = payload[inventory_section]
            declared = _inventory_entries(
                {
                    "schema_version": "1.0",
                    **{key: value for key, value in section.items() if key != "archive_digest"},
                },
                kind,
            )
            if section["archive_digest"] != ref.digest or declared != _entry_payload(entries):
                raise ValueError("external inventory does not match archive")
        elif kind in {ArchiveKind.DEPENDENCY_LOCK, ArchiveKind.OFFLINE_STORE}:
            raise ValueError("dependency archive requires an external inventory")
        result_digest = tree_digest(entries)
        for output_path in temporary.rglob("*"):
            if output_path.is_dir():
                os.chmod(output_path, 0o555)
        os.chmod(temporary, 0o555)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"materialization destination already exists: {destination}")
        os.replace(temporary, destination)
        return MaterializationResult(
            destination, sum(item.type == "file" for item in entries), total, result_digest
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
