"""Canonical dependency lock/store/inventory artifact operations."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.models import (
    ArchiveInventory,
    ArtifactRef,
    DependencyBundle,
    DependencyInventory,
    DependencyOfflineSmoke,
    InventoryEntry,
    Visibility,
)
from nl2repobench.harbor.bundle_io import BundleLimits, extract_bundle_archive
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.canonical_ustar import (
    CanonicalEntry,
    encode_ustar,
    entries_from_tree,
    inventory_entries,
    tree_digest,
)

from .base import PackageManagerError

LOCK_MEDIA_TYPE = "application/vnd.nl2repobench.package-lock.tar"
STORE_MEDIA_TYPE = "application/vnd.nl2repobench.offline-store.tar"
INVENTORY_MEDIA_TYPE = "application/vnd.nl2repobench.inventory+json"
DEPENDENCY_LIMITS = BundleLimits(
    max_members=100_000,
    max_member_bytes=512 * 1024 * 1024,
    max_total_bytes=2 * 1024 * 1024 * 1024,
)


def archive_inventory(
    kind: str, reference: ArtifactRef, entries: tuple[CanonicalEntry, ...]
) -> ArchiveInventory:
    return ArchiveInventory(
        archive_kind=kind,  # type: ignore[arg-type]
        archive_digest=reference.digest,
        tree_digest=tree_digest(entries),
        entries=tuple(
            InventoryEntry.model_validate(item) for item in inventory_entries(entries)
        ),
        file_count=sum(entry.type == "file" for entry in entries),
        directory_count=sum(entry.type == "directory" for entry in entries),
        total_bytes=sum(entry.size for entry in entries if entry.type == "file"),
    )


def put_dependency_archive(
    store: FileArtifactStore,
    entries: tuple[CanonicalEntry, ...],
    *,
    media_type: str,
) -> ArtifactRef:
    return store.put_bytes(
        encode_ustar(entries),
        media_type=media_type,
        visibility=Visibility.PRIVATE,
    )


def put_dependency_inventory(
    store: FileArtifactStore,
    *,
    identity: str,
    adapter_version: str,
    toolchain_digest: str,
    lock_ref: ArtifactRef,
    lock_entries: tuple[CanonicalEntry, ...],
    store_ref: ArtifactRef,
    store_entries: tuple[CanonicalEntry, ...],
    smoke_command_id: str,
) -> ArtifactRef:
    inventory = DependencyInventory(
        identity=identity,
        adapter_version=adapter_version,
        toolchain_digest=toolchain_digest,
        lock=archive_inventory("dependency-lock", lock_ref, lock_entries),
        store=archive_inventory("offline-store", store_ref, store_entries),
        offline_smoke=DependencyOfflineSmoke(
            status="passed", command_id=smoke_command_id
        ),
    )
    return store.put_bytes(
        canonical_json(inventory) + b"\n",
        media_type=INVENTORY_MEDIA_TYPE,
        visibility=Visibility.PRIVATE,
    )


def load_dependency_inventory(
    bundle: DependencyBundle,
    *,
    resolver: LocalArtifactResolver,
    expected_identity: str,
    expected_toolchain_digest: str,
    expected_adapter_version: str,
) -> DependencyInventory:
    if bundle.lock is None or bundle.offline_store is None or bundle.inventory is None:
        raise PackageManagerError("dependency lock/store/inventory refs are required")
    if bundle.lock.media_type != LOCK_MEDIA_TYPE:
        raise PackageManagerError("dependency lock media type is invalid")
    if bundle.offline_store.media_type != STORE_MEDIA_TYPE:
        raise PackageManagerError("dependency store media type is invalid")
    if bundle.inventory.media_type != INVENTORY_MEDIA_TYPE:
        raise PackageManagerError("dependency inventory media type is invalid")
    try:
        data = resolver.resolve(bundle.inventory).read_bytes()
        inventory = DependencyInventory.model_validate_json(data)
    except (OSError, ValueError) as exc:
        raise PackageManagerError(f"cannot load dependency inventory: {exc}") from exc
    if data != canonical_json(inventory) + b"\n":
        raise PackageManagerError("dependency inventory is not canonical JSON")
    if inventory.identity != expected_identity:
        raise PackageManagerError("dependency inventory runtime identity does not match")
    if inventory.adapter_version != expected_adapter_version:
        raise PackageManagerError("dependency inventory adapter version does not match")
    if inventory.toolchain_digest != expected_toolchain_digest:
        raise PackageManagerError("dependency inventory toolchain digest does not match")
    if inventory.lock.archive_digest != bundle.lock.digest:
        raise PackageManagerError("dependency lock archive digest does not match inventory")
    if inventory.store.archive_digest != bundle.offline_store.digest:
        raise PackageManagerError("dependency store archive digest does not match inventory")
    return inventory


def _validate_tree(root: Path, expected: ArchiveInventory) -> None:
    executable = frozenset(
        entry.path for entry in expected.entries if entry.type == "file" and entry.mode == "0555"
    )
    actual = entries_from_tree(root, executable_paths=executable)
    if inventory_entries(actual) != [entry.model_dump(mode="json") for entry in expected.entries]:
        raise PackageManagerError("materialized dependency archive inventory does not match")
    if tree_digest(actual) != expected.tree_digest:
        raise PackageManagerError("materialized dependency archive tree digest does not match")


def materialize_dependency_archive(
    reference: ArtifactRef,
    expected: ArchiveInventory,
    destination: Path,
    *,
    resolver: LocalArtifactResolver,
) -> None:
    if destination.exists() or destination.is_symlink():
        raise PackageManagerError(f"dependency destination already exists: {destination}")
    temporary = destination.with_name(f".{destination.name}-tmp")
    shutil.rmtree(temporary, ignore_errors=True)
    try:
        archive = resolver.resolve(reference)
        if "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest() != reference.digest:
            raise PackageManagerError("dependency archive digest changed during materialization")
        extract_bundle_archive(archive, temporary, limits=DEPENDENCY_LIMITS)
        _validate_tree(temporary, expected)
        for path in sorted(temporary.rglob("*"), reverse=True):
            path.chmod(0o555 if path.is_dir() else 0o444)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


__all__ = [
    "INVENTORY_MEDIA_TYPE",
    "LOCK_MEDIA_TYPE",
    "STORE_MEDIA_TYPE",
    "archive_inventory",
    "load_dependency_inventory",
    "materialize_dependency_archive",
    "put_dependency_archive",
    "put_dependency_inventory",
]
