from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from nl2repobench.package_managers import PackageManagerError, PackageManagerErrorCode
from nl2repobench.package_managers.maven import (
    MavenPackageManager,
    load_maven_lock,
    maven_repository_path,
    validate_candidate_pom,
)
from nl2repobench.storage.canonical_ustar import tree_digest, tree_entries


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
            "archive_digest": "sha256:" + "0" * 64,
        },
        "store": {
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
    summary = MavenPackageManager().validate_lock(lock_root, "3.9.9")
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
    summary = adapter.validate_lock(lock_root, "3.9.9")
    inventory = _inventory(store)
    lock_inventory = inventory["lock"]
    assert isinstance(lock_inventory, dict)
    lock_inventory["archive_digest"] = summary.lock_digest
    store_summary = adapter.validate_offline_store(
        store, summary, inventory, "3.9.9"
    )
    assert store_summary.offline_smoke is True
    (store / "unexpected.txt").write_text("forged", encoding="utf-8")
    forged_inventory = _inventory(store)
    forged_lock = forged_inventory["lock"]
    assert isinstance(forged_lock, dict)
    forged_lock["archive_digest"] = summary.lock_digest
    with pytest.raises(PackageManagerError, match="paths do not match"):
        adapter.validate_offline_store(store, summary, forged_inventory, "3.9.9")


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
