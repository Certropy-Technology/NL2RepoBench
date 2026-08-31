from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from nl2repobench.domain.canonical_contract import DependencyBundle, RuntimeProfile
from nl2repobench.domain.canonical_models import Visibility
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.harbor.dependency_contract import materialize_dependency_bundle
from nl2repobench.package_managers import PackageManagerError, PackageManagerErrorCode
from nl2repobench.package_managers.maven import (
    MavenPackageManager,
    load_maven_lock,
    maven_repository_path,
    validate_candidate_pom,
)
from nl2repobench.storage.artifacts import (
    FileArtifactStore,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.canonical_ustar import encode_files, tree_digest, tree_entries


def _lock_bytes(payload_data: bytes = b"jar") -> bytes:
    payload = {
        "schema_version": "1.0",
        "maven_version": "3.9.9",
        "jdk_version": "temurin-21.0.5+11",
        "effective_project": {
            "group_id": "example.synthetic",
            "artifact_id": "harness",
            "version": "1.0.0",
            "packaging": "jar",
            "release": 21,
            "pom_sha256": "0" * 64,
        },
        "artifacts": [
            {
                "group_id": "example.fake",
                "artifact_id": "tiny",
                "version": "1.2.3",
                "type": "jar",
                "classifier": None,
                "scope": "test",
                "sha256": hashlib.sha256(payload_data).hexdigest(),
                "size": len(payload_data),
            }
        ],
        "plugins": [],
        "repositories": [
            {
                "id": "central",
                "url": "https://repo.maven.apache.org/maven2",
                "releases_enabled": True,
                "snapshots_enabled": False,
            }
        ],
        "offline_smoke": {
            "status": "passed",
            "command_id": "maven-offline-compile-discovery-v1",
        },
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _inventory(store: Path) -> dict[str, object]:
    entries = tree_entries(store)
    return {
        "schema_version": "1.0",
        "identity": "java+maven",
        "adapter_version": "maven-lock-v1",
        "toolchain_digest": "sha256:" + "1" * 64,
        "lock": {
            "schema_version": "1.0",
            "archive_kind": "dependency-lock",
            "archive_digest": "sha256:" + "0" * 64,
        },
        "store": {
            "schema_version": "1.0",
            "archive_kind": "offline-store",
            "archive_digest": "sha256:" + "2" * 64,
            "tree_digest": tree_digest(entries),
            "file_count": sum(entry.type == "file" for entry in entries),
            "directory_count": sum(entry.type == "directory" for entry in entries),
            "total_bytes": sum(entry.size for entry in entries),
            "entries": [
                {
                    "path": entry.path,
                    "type": entry.type,
                    "mode": entry.mode,
                    "size": entry.size,
                    "sha256": entry.sha256,
                }
                for entry in entries
            ],
        },
        "offline_smoke": {
            "status": "passed",
            "command_id": "maven-offline-compile-discovery-v1",
        },
    }


def test_maven_lock_and_repository_path_are_strict(tmp_path: Path) -> None:
    lock_root = tmp_path / "lock"
    lock_root.mkdir()
    data = _lock_bytes()
    (lock_root / "maven-lock-v1.json").write_bytes(data)
    lock = load_maven_lock(data)
    summary = MavenPackageManager().validate_lock(
        lock_root,
        "3.9.9",
        expected_jdk_version="temurin-21.0.5+11",
    )
    assert summary.resolved[0].name == "example.fake:tiny:1.2.3:jar"
    assert str(maven_repository_path(lock.artifacts[0])) == (
        "example/fake/tiny/1.2.3/tiny-1.2.3.jar"
    )


@pytest.mark.parametrize("version", ["1.0-SNAPSHOT", "[1,2)", "LATEST", "RELEASE"])
def test_maven_lock_rejects_dynamic_versions(version: str) -> None:
    payload = json.loads(_lock_bytes())
    payload["artifacts"][0]["version"] = version
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    with pytest.raises(PackageManagerError, match="dynamic or snapshot"):
        load_maven_lock(data)


def test_maven_store_requires_exact_locked_inventory(tmp_path: Path) -> None:
    lock_root = tmp_path / "lock"
    store = tmp_path / "store"
    lock_root.mkdir()
    store.mkdir()
    data = _lock_bytes()
    (lock_root / "maven-lock-v1.json").write_bytes(data)
    lock = load_maven_lock(data)
    payload = store / maven_repository_path(lock.artifacts[0])
    payload.parent.mkdir(parents=True)
    payload.write_bytes(b"jar")
    adapter = MavenPackageManager()
    summary = adapter.validate_lock(
        lock_root,
        "3.9.9",
        expected_jdk_version="temurin-21.0.5+11",
    )
    inventory = _inventory(store)
    store_summary = adapter.validate_offline_store(
        store,
        summary,
        inventory,
        "3.9.9",
        expected_jdk_version="temurin-21.0.5+11",
    )
    assert store_summary.offline_smoke is True
    (store / "unexpected.txt").write_text("forged", encoding="utf-8")
    forged_inventory = _inventory(store)
    with pytest.raises(PackageManagerError, match="paths do not match"):
        adapter.validate_offline_store(
            store,
            summary,
            forged_inventory,
            "3.9.9",
            expected_jdk_version="temurin-21.0.5+11",
        )


def test_generic_java_materialization_validates_canonical_triple_with_profile(
    tmp_path: Path,
) -> None:
    data = _lock_bytes()
    lock_archive = encode_files({"maven-lock-v1.json": data})
    store_payload = {"example/fake/tiny/1.2.3/tiny-1.2.3.jar": b"jar"}
    store_archive = encode_files(store_payload)
    backing = FileArtifactStore(tmp_path / "cas")
    lock_ref = backing.put_bytes(
        lock_archive,
        media_type="application/vnd.nl2repobench.package-lock.tar",
        visibility=Visibility.PRIVATE,
    )
    store_ref = backing.put_bytes(
        store_archive,
        media_type="application/vnd.nl2repobench.offline-store.tar",
        visibility=Visibility.PRIVATE,
    )
    lock_root = tmp_path / "lock-inspect"
    lock_root.mkdir()
    (lock_root / "maven-lock-v1.json").write_bytes(data)
    store_root = tmp_path / "store-inspect"
    store_root.mkdir()
    payload_path = store_root / "example/fake/tiny/1.2.3/tiny-1.2.3.jar"
    payload_path.parent.mkdir(parents=True)
    payload_path.write_bytes(b"jar")
    inventory_payload = _inventory(store_root)
    inventory_payload["lock"] = {
        "schema_version": "1.0",
        "archive_kind": "dependency-lock",
        "archive_digest": lock_ref.digest,
        "tree_digest": tree_digest(tree_entries(lock_root)),
        "file_count": 1,
        "directory_count": 0,
        "total_bytes": len(data),
        "entries": [
            {
                "path": "maven-lock-v1.json",
                "type": "file",
                "mode": 0o444,
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        ],
    }
    store_section = inventory_payload["store"]
    assert isinstance(store_section, dict)
    store_section["archive_digest"] = store_ref.digest
    assert "jdk_version" not in inventory_payload["lock"]
    inventory_ref = backing.put_bytes(
        json.dumps(inventory_payload, sort_keys=True, separators=(",", ":")).encode() + b"\n",
        media_type="application/vnd.nl2repobench.inventory+json",
        visibility=Visibility.PRIVATE,
    )
    authorization = PrivateArtifactAuthorization(
        task_id="java-maven",
        manifest_digest="sha256:" + "1" * 64,
        purpose="compile",
        allowed_digests=frozenset({lock_ref.digest, store_ref.digest, inventory_ref.digest}),
        staging_root=(tmp_path / "staging").resolve(),
    )
    resolver = LocalArtifactResolver.scoped_private(
        backing,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )
    profile = RuntimeProfile(
        language="java",
        runtime="jdk",
        version="temurin-21.0.5+11",
        package_manager="maven",
        package_manager_version="3.9.9",
    )
    bundle = DependencyBundle(
        status="known",
        package_manager="maven",
        lock=lock_ref,
        offline_store=store_ref,
        inventory=inventory_ref,
    )
    summary, store_summary = materialize_dependency_bundle(
        bundle,
        identity=RuntimeDiscriminator(language="java", package_manager="maven"),
        expected_toolchain="3.9.9",
        runtime_profile=profile,
        resolver=resolver,
        destination=tmp_path / "staging",
    )
    assert summary.jdk_version == profile.version
    assert store_summary.offline_smoke is True


def test_maven_lock_rejects_a_different_valid_jdk_identity(tmp_path: Path) -> None:
    lock_root = tmp_path / "lock"
    lock_root.mkdir()
    (lock_root / "maven-lock-v1.json").write_bytes(_lock_bytes())
    with pytest.raises(PackageManagerError, match="JDK identity") as raised:
        MavenPackageManager().validate_lock(
            lock_root,
            "3.9.9",
            expected_jdk_version="zulu-21.0.5+11",
        )
    assert raised.value.code is PackageManagerErrorCode.TOOLCHAIN_MISMATCH


def test_maven_lock_requires_selected_jdk_identity(tmp_path: Path) -> None:
    lock_root = tmp_path / "lock"
    lock_root.mkdir()
    (lock_root / "maven-lock-v1.json").write_bytes(_lock_bytes())
    with pytest.raises(PackageManagerError, match="requires the selected exact JDK"):
        MavenPackageManager().validate_lock(lock_root, "3.9.9")


def test_maven_runtime_profile_is_propagated_and_rejects_wrong_identity(tmp_path: Path) -> None:
    lock_root = tmp_path / "lock"
    lock_root.mkdir()
    (lock_root / "maven-lock-v1.json").write_bytes(_lock_bytes())
    adapter = MavenPackageManager()
    profile = RuntimeProfile(
        language="java",
        runtime="jdk",
        version="temurin-21.0.5+11",
        package_manager="maven",
        package_manager_version="3.9.9",
    )
    summary = adapter.validate_lock(lock_root, "3.9.9", runtime_profile=profile)
    assert summary.jdk_version == profile.version
    with pytest.raises(PackageManagerError, match="selected JDK"):
        adapter.validate_lock(
            lock_root,
            "3.9.9",
            runtime_profile=RuntimeProfile(
                language="java",
                runtime="jdk",
                version="zulu-21.0.5+11",
                package_manager="maven",
                package_manager_version="3.9.9",
            ),
        )


def test_maven_store_rejects_malformed_jdk_identity_values(tmp_path: Path) -> None:
    lock_root = tmp_path / "lock"
    store = tmp_path / "store"
    lock_root.mkdir()
    store.mkdir()
    data = _lock_bytes()
    (lock_root / "maven-lock-v1.json").write_bytes(data)
    adapter = MavenPackageManager()
    summary = adapter.validate_lock(
        lock_root,
        "3.9.9",
        expected_jdk_version="temurin-21.0.5+11",
    )
    malformed_summary = replace(summary, jdk_version="not-a-jdk")
    with pytest.raises(PackageManagerError, match="JDK identity"):
        adapter.validate_offline_store(
            store,
            malformed_summary,
            {},
            "3.9.9",
            expected_jdk_version="not-a-jdk",
        )


def test_candidate_pom_is_metadata_only() -> None:
    pom = b"""<project xmlns="http://maven.apache.org/POM/4.0.0">
      <modelVersion>4.0.0</modelVersion>
      <groupId>example.fake</groupId><artifactId>candidate</artifactId>
      <version>1.0.0</version><packaging>jar</packaging>
      <properties><maven.compiler.release>17</maven.compiler.release></properties>
    </project>"""
    metadata = validate_candidate_pom(pom)
    assert metadata is not None and metadata.release == 17
    with pytest.raises(PackageManagerError, match="dependencies is forbidden"):
        validate_candidate_pom(
            pom.replace(b"</project>", b"<dependencies /></project>")
        )
    with pytest.raises(PackageManagerError, match="DTD and entities"):
        validate_candidate_pom(b'<!DOCTYPE project [<!ENTITY x "x">]><project>&x;</project>')


def test_maven_build_activation_remains_typed_unsupported() -> None:
    adapter = MavenPackageManager()
    with pytest.raises(PackageManagerError, match="future candidate supervisor") as raised:
        adapter.build_commands({})
    assert raised.value.code is PackageManagerErrorCode.UNSUPPORTED_PROFILE
    assert adapter.offline_environment({})["MAVEN_ARGS"].startswith("--offline")
