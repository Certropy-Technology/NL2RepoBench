from __future__ import annotations

from nl2repobench.domain.models import DependencyBundle
from nl2repobench.package_managers.dependency_artifacts import (
    LOCK_MEDIA_TYPE,
    STORE_MEDIA_TYPE,
    load_dependency_inventory,
    materialize_dependency_archive,
    put_dependency_archive,
    put_dependency_inventory,
)
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.canonical_ustar import CanonicalEntry


def test_dependency_artifacts_are_hash_bound_and_materialized(tmp_path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    lock_entries = (CanonicalEntry("lock.txt", "file", 0o444, b"locked\n"),)
    store_entries = (
        CanonicalEntry("cache/", "directory", 0o555),
        CanonicalEntry("cache/value", "file", 0o444, b"cached\n"),
    )
    lock_ref = put_dependency_archive(store, lock_entries, media_type=LOCK_MEDIA_TYPE)
    store_ref = put_dependency_archive(store, store_entries, media_type=STORE_MEDIA_TYPE)
    inventory_ref = put_dependency_inventory(
        store,
        identity="java+maven",
        adapter_version="maven-v1",
        toolchain_digest="sha256:" + "a" * 64,
        lock_ref=lock_ref,
        lock_entries=lock_entries,
        store_ref=store_ref,
        store_entries=store_entries,
        smoke_command_id="maven-offline-v1",
    )
    bundle = DependencyBundle(
        status="known",
        package_manager="maven",
        lock=lock_ref,
        offline_store=store_ref,
        inventory=inventory_ref,
    )
    resolver = LocalArtifactResolver(store, allow_private=True).scoped(
        frozenset({lock_ref.digest, store_ref.digest, inventory_ref.digest})
    )

    inventory = load_dependency_inventory(
        bundle,
        resolver=resolver,
        expected_identity="java+maven",
        expected_toolchain_digest="sha256:" + "a" * 64,
        expected_adapter_version="maven-v1",
    )
    materialize_dependency_archive(
        store_ref,
        inventory.store,
        tmp_path / "materialized",
        resolver=resolver,
    )

    assert (tmp_path / "materialized/cache/value").read_bytes() == b"cached\n"
