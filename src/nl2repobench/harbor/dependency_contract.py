"""In-memory validation of canonical dependency lock/store/inventory artifacts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from nl2repobench.domain.canonical_contract import (
    DependencyBundle,
    PackageManager,
    RuntimeLanguage,
    RuntimeProfile,
)
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.package_managers.base import LockSummary, StoreSummary
from nl2repobench.package_managers.registry import PackageManagerRegistry
from nl2repobench.storage.artifacts import (
    ArtifactStoreError,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.canonical_ustar import ArchiveMember, decode_archive, tree_digest
from nl2repobench.storage.materialize import (
    TARGET_MEDIA_TYPES,
    ArchiveKind,
    MaterializationLimits,
    materialize_archive,
)


class DependencyContractError(ValueError):
    """Canonical dependency artifacts are absent, inconsistent, or unauthorized."""


@dataclass(frozen=True, slots=True)
class ValidatedDependencyArtifacts:
    lock_files: dict[str, bytes]
    store_file_count: int
    inventory: dict[str, object] | None


def _entry_payload(members: tuple[ArchiveMember, ...]) -> list[dict[str, object]]:
    return [
        {
            "path": member.entry.path,
            "type": member.entry.type,
            "mode": member.entry.mode,
            "size": member.entry.size,
            "sha256": member.entry.sha256,
        }
        for member in members
    ]


def _validate_section(
    payload: object,
    *,
    name: str,
    archive_digest: str,
    members: tuple[ArchiveMember, ...],
) -> None:
    if not isinstance(payload, dict) or set(payload) != {
        "archive_kind",
        "archive_digest",
        "tree_digest",
        "entries",
        "file_count",
        "directory_count",
        "total_bytes",
    }:
        raise DependencyContractError(f"dependency inventory {name} section is malformed")
    if payload["archive_kind"] != name or payload["archive_digest"] != archive_digest:
        raise DependencyContractError(f"dependency inventory {name} identity mismatch")
    entries = _entry_payload(members)
    if payload["entries"] != entries:
        raise DependencyContractError(f"dependency inventory {name} entries mismatch")
    if payload["tree_digest"] != tree_digest([member.entry for member in members]):
        raise DependencyContractError(f"dependency inventory {name} tree digest mismatch")
    if payload["file_count"] != sum(member.entry.type == "file" for member in members):
        raise DependencyContractError(f"dependency inventory {name} file count mismatch")
    if payload["directory_count"] != sum(
        member.entry.type == "directory" for member in members
    ):
        raise DependencyContractError(f"dependency inventory {name} directory count mismatch")
    if payload["total_bytes"] != sum(member.entry.size for member in members):
        raise DependencyContractError(f"dependency inventory {name} byte count mismatch")


def validate_dependency_artifacts(
    bundle: DependencyBundle,
    *,
    identity: str,
    toolchain_digest: str,
    resolver: LocalArtifactResolver,
) -> ValidatedDependencyArtifacts:
    """Validate all three canonical dependency artifacts under one scoped resolver."""

    if bundle.status != "known":
        raise DependencyContractError("dependency closure status must be known")
    lock = bundle.lock
    store = bundle.offline_store
    inventory = bundle.inventory
    if lock is None or store is None or inventory is None:
        raise DependencyContractError("canonical dependency artifact triple is incomplete")
    if lock.media_type != TARGET_MEDIA_TYPES[ArchiveKind.DEPENDENCY_LOCK]:
        raise DependencyContractError("dependency lock media type is not canonical")
    if store.media_type != TARGET_MEDIA_TYPES[ArchiveKind.OFFLINE_STORE]:
        raise DependencyContractError("offline store media type is not canonical")
    if inventory.media_type != "application/vnd.nl2repobench.inventory+json":
        raise DependencyContractError("dependency inventory media type is not canonical")
    try:
        lock_bytes = resolver.read_bytes(lock, max_bytes=16 * 1024 * 1024)
        store_bytes = resolver.read_bytes(store, max_bytes=2 * 1024**3)
        inventory_bytes = resolver.read_bytes(inventory, max_bytes=4 * 1024 * 1024)
        lock_members = decode_archive(lock_bytes)
        store_members = decode_archive(store_bytes)
    except (ArtifactStoreError, OSError, ValueError) as exc:
        raise DependencyContractError(
            f"cannot resolve canonical dependency artifacts: {exc}"
        ) from exc
    try:
        payload = json.loads(inventory_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DependencyContractError("dependency inventory is not valid JSON") from exc
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    if inventory_bytes != canonical:
        raise DependencyContractError("dependency inventory JSON is not canonical")
    required = {
        "schema_version",
        "identity",
        "adapter_version",
        "toolchain_digest",
        "lock",
        "store",
        "offline_smoke",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        raise DependencyContractError("dependency inventory has unexpected fields")
    if payload["schema_version"] != "1.0" or payload["identity"] != identity:
        raise DependencyContractError("dependency inventory runtime identity mismatch")
    if not isinstance(payload["adapter_version"], str) or not payload["adapter_version"]:
        raise DependencyContractError("dependency inventory adapter version is missing")
    recorded_toolchain = payload["toolchain_digest"]
    if not isinstance(recorded_toolchain, str) or not re.fullmatch(
        r"sha256:[0-9a-f]{64}", recorded_toolchain
    ):
        raise DependencyContractError("dependency inventory toolchain digest is malformed")
    if toolchain_digest != recorded_toolchain:
        raise DependencyContractError("dependency inventory toolchain digest mismatch")
    offline_smoke = payload["offline_smoke"]
    if (
        not isinstance(offline_smoke, dict)
        or set(offline_smoke) != {"status", "command_id"}
        or offline_smoke.get("status") != "passed"
        or not isinstance(offline_smoke.get("command_id"), str)
        or not offline_smoke["command_id"]
    ):
        raise DependencyContractError("dependency inventory lacks a passed offline smoke")
    _validate_section(
        payload["lock"],
        name="dependency-lock",
        archive_digest=lock.digest,
        members=lock_members,
    )
    _validate_section(
        payload["store"],
        name="offline-store",
        archive_digest=store.digest,
        members=store_members,
    )
    if bundle.package_manager is PackageManager.NONE:
        if lock_bytes != b"\0" * 10240 or store_bytes != b"\0" * 10240:
            raise DependencyContractError(
                "known none dependency closure must use canonical empty archives"
            )
        if payload["offline_smoke"] != {
            "status": "passed",
            "command_id": "none-noop-v1",
        }:
            raise DependencyContractError(
                "known none dependency closure requires the canonical offline smoke"
            )
        for name in ("lock", "store"):
            section = payload[name]
            if section["entries"] or section["file_count"] != 0 or section["directory_count"] != 0:
                raise DependencyContractError(
                    "known none dependency closure inventory must be empty"
                )
    lock_files = {
        member.entry.path: member.data
        for member in lock_members
        if member.entry.type == "file" and member.data is not None
    }
    return ValidatedDependencyArtifacts(
        lock_files=lock_files,
        store_file_count=sum(member.entry.type == "file" for member in store_members),
        inventory=payload,
    )


def materialize_dependency_bundle(
    bundle: DependencyBundle,
    *,
    identity: RuntimeDiscriminator,
    expected_toolchain: str,
    resolver: LocalArtifactResolver,
    destination: Path,
    runtime_profile: RuntimeProfile | None = None,
) -> tuple[LockSummary, StoreSummary]:
    """Materialize and validate the canonical triple through its adapter.

    This is intentionally a compiler-side staging operation. It does not
    install dependencies or provide a fallback to an online package index.
    """

    if bundle.lock is None or bundle.offline_store is None or bundle.inventory is None:
        raise DependencyContractError("canonical dependency artifact triple is incomplete")
    if identity.package_manager.value != bundle.package_manager.value:
        raise DependencyContractError("dependency identity does not match the bundle")
    if identity.language is RuntimeLanguage.JAVA and runtime_profile is None:
        raise DependencyContractError(
            "Java dependency staging requires the selected runtime profile"
        )
    if runtime_profile is not None and (
        runtime_profile.language is not identity.language
        or runtime_profile.package_manager is not identity.package_manager
    ):
        raise DependencyContractError(
            "selected runtime profile does not match dependency identity"
        )
    authorization = resolver.authorization
    if not isinstance(authorization, PrivateArtifactAuthorization):
        raise DependencyContractError("private artifact authorization is required")
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    lock_root = destination / "lock"
    store_root = destination / "store"
    try:
        materialize_archive(
            bundle.lock,
            ArchiveKind.DEPENDENCY_LOCK,
            lock_root,
            MaterializationLimits(64, 4 * 1024 * 1024, 16 * 1024 * 1024),
            authorization,
            resolver=resolver,
            inventory_ref=bundle.inventory,
            inventory_section="lock",
        )
        materialize_archive(
            bundle.offline_store,
            ArchiveKind.OFFLINE_STORE,
            store_root,
            MaterializationLimits(100_000, 512 * 1024 * 1024, 2 * 1024**3),
            authorization,
            resolver=resolver,
            inventory_ref=bundle.inventory,
            inventory_section="store",
        )
        inventory_bytes = resolver.read_bytes(bundle.inventory, max_bytes=4 * 1024 * 1024)
        inventory = json.loads(inventory_bytes)
        adapter = PackageManagerRegistry.default().resolve(identity)
        lock_summary = adapter.validate_lock(
            lock_root,
            expected_toolchain,
            runtime_profile=runtime_profile,
        )
        store_summary = adapter.validate_offline_store(
            store_root,
            lock_summary,
            inventory,
            expected_toolchain,
            runtime_profile=runtime_profile,
        )
    except (ArtifactStoreError, OSError, ValueError) as exc:
        raise DependencyContractError(f"cannot stage dependency closure: {exc}") from exc
    return lock_summary, store_summary


__all__ = [
    "DependencyContractError",
    "ValidatedDependencyArtifacts",
    "validate_dependency_artifacts",
]
