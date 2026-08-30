"""In-memory validation of canonical dependency lock/store/inventory artifacts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from nl2repobench.domain.canonical_contract import DependencyBundle, PackageManager
from nl2repobench.storage.artifacts import ArtifactStoreError, LocalArtifactResolver
from nl2repobench.storage.canonical_ustar import ArchiveMember, decode_archive, tree_digest
from nl2repobench.storage.materialize import TARGET_MEDIA_TYPES, ArchiveKind


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

    if bundle.package_manager is PackageManager.NONE:
        if bundle.status != "known" or any(
            reference is not None
            for reference in (bundle.lock, bundle.offline_store, bundle.inventory)
        ):
            raise DependencyContractError(
                "package_manager=none requires known status and no dependency artifacts"
            )
        return ValidatedDependencyArtifacts({}, 0, None)
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


__all__ = [
    "DependencyContractError",
    "ValidatedDependencyArtifacts",
    "validate_dependency_artifacts",
]
