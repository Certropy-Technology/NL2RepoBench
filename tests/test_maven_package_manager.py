from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from nl2repobench.package_managers import PackageManagerError
from nl2repobench.package_managers.maven import (
    MavenPackageManager,
    load_maven_lock,
    maven_repository_path,
    validate_candidate_pom,
)


def _lock_bytes(payload: bytes = b"jar") -> bytes:
    lock = {
        "schema_version": "1.0",
        "maven_version": "3.9.11",
        "jdk_version": "temurin-21.0.12+8",
        "effective_project": {
            "group_id": "example.synthetic",
            "artifact_id": "harness",
            "version": "1.0.0",
            "packaging": "jar",
            "release": 21,
        },
        "artifacts": [
            {
                "group_id": "example.fake",
                "artifact_id": "tiny",
                "version": "1.2.3",
                "type": "jar",
                "classifier": None,
                "scope": "test",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
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
        "offline_smoke": {"status": "passed"},
    }
    return json.dumps(lock, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def test_maven_lock_and_store_require_the_exact_locked_closure(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    lock_path = bundle / "maven-lock-v1.json"
    lock_path.write_bytes(_lock_bytes())
    lock = load_maven_lock(lock_path.read_bytes())
    payload = bundle / maven_repository_path(lock["artifacts"][0])
    payload.parent.mkdir(parents=True)
    payload.write_bytes(b"jar")
    manifest = bundle / "maven-store.manifest.json"
    inventory = MavenPackageManager().build_inventory(
        bundle,
        lockfile=lock_path,
        manifest=manifest,
        expected_version="3.9.11",
    )
    manifest.write_bytes(
        json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    MavenPackageManager().validate_offline_store(
        bundle,
        lockfile=lock_path,
        manifest=manifest,
        expected_version="3.9.11",
    )

    (bundle / "unexpected.txt").write_text("forged", encoding="utf-8")
    with pytest.raises(PackageManagerError, match="paths do not match"):
        MavenPackageManager().validate_offline_store(
            bundle,
            lockfile=lock_path,
            manifest=manifest,
            expected_version="3.9.11",
        )


def test_maven_inventory_rejects_lock_only_manifest(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    lock_path = bundle / "maven-lock-v1.json"
    lock_path.write_bytes(_lock_bytes())
    lock = load_maven_lock(lock_path.read_bytes())
    payload = bundle / maven_repository_path(lock["artifacts"][0])
    payload.parent.mkdir(parents=True)
    payload.write_bytes(b"jar")
    summary = MavenPackageManager().validate_lock(lock_path, expected_version="3.9.11")
    manifest = bundle / "maven-store.manifest.json"
    manifest.write_text(
        json.dumps({"lock_sha256": summary.digest}, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(PackageManagerError, match="inventory schema"):
        MavenPackageManager().validate_offline_store(
            bundle,
            lockfile=lock_path,
            manifest=manifest,
            expected_version="3.9.11",
        )


@pytest.mark.parametrize("version", ["1.0-SNAPSHOT", "[1,2)", "LATEST", "RELEASE"])
def test_maven_lock_rejects_mutable_versions(version: str) -> None:
    lock = json.loads(_lock_bytes())
    lock["artifacts"][0]["version"] = version
    data = json.dumps(lock, sort_keys=True, separators=(",", ":")).encode() + b"\n"

    with pytest.raises(PackageManagerError, match="dynamic version"):
        load_maven_lock(data)


def test_maven_lock_rejects_unrecognized_fields() -> None:
    lock = json.loads(_lock_bytes())
    lock["unreviewed"] = True
    data = json.dumps(lock, sort_keys=True, separators=(",", ":")).encode() + b"\n"

    with pytest.raises(PackageManagerError, match="schema_version"):
        load_maven_lock(data)


def test_maven_lock_rejects_invalid_scope_and_repository_metadata() -> None:
    lock = json.loads(_lock_bytes())
    lock["artifacts"][0]["scope"] = "system"
    data = json.dumps(lock, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    with pytest.raises(PackageManagerError, match="scope"):
        load_maven_lock(data)

    lock = json.loads(_lock_bytes())
    lock["repositories"] = [
        {
            "id": "central",
            "url": "https://repo.maven.apache.org/maven2",
            "releases_enabled": False,
            "snapshots_enabled": False,
        }
    ]
    data = json.dumps(lock, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    with pytest.raises(PackageManagerError, match="repository metadata"):
        load_maven_lock(data)


def test_candidate_pom_is_metadata_only_and_cannot_define_build_behavior() -> None:
    pom = b"""<project xmlns="http://maven.apache.org/POM/4.0.0">
      <modelVersion>4.0.0</modelVersion>
      <groupId>example.fake</groupId><artifactId>candidate</artifactId>
      <version>1.0.0</version><packaging>jar</packaging>
      <properties><maven.compiler.release>17</maven.compiler.release></properties>
    </project>"""

    assert validate_candidate_pom(pom) == {
        "group_id": "example.fake",
        "artifact_id": "candidate",
        "version": "1.0.0",
        "release": 17,
    }
    with pytest.raises(PackageManagerError, match="forbidden build or dependency"):
        validate_candidate_pom(pom.replace(b"</project>", b"<dependencies /></project>"))
    with pytest.raises(PackageManagerError, match="DTD and entities"):
        validate_candidate_pom(b'<!DOCTYPE project [<!ENTITY x "x">]><project>&x;</project>')


def test_candidate_pom_accepts_standard_schema_location() -> None:
    pom = (
        b'<project xmlns="http://maven.apache.org/POM/4.0.0" '
        b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 '
        b'https://maven.apache.org/xsd/maven-4.0.0.xsd">'
        b"<artifactId>candidate</artifactId></project>"
    )

    assert validate_candidate_pom(pom)["artifact_id"] == "candidate"


def test_candidate_pom_accepts_standard_source_encoding_property() -> None:
    pom = b"""<project>
      <artifactId>candidate</artifactId>
      <properties>
        <maven.compiler.release>21</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
      </properties>
    </project>"""

    assert validate_candidate_pom(pom)["release"] == 21


def test_candidate_pom_accepts_standard_project_metadata() -> None:
    pom = b'''<project xmlns="http://maven.apache.org/POM/4.0.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
      <modelVersion>4.0.0</modelVersion>
      <groupId>example</groupId><artifactId>candidate</artifactId><version>1.0.0</version>
      <name>candidate</name><description>candidate project</description>
      <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <maven.compiler.release>21</maven.compiler.release>
      </properties>
    </project>'''

    assert validate_candidate_pom(pom)["release"] == 21


def test_maven_command_is_always_offline_and_verifier_owned() -> None:
    assert MavenPackageManager().install_command(store_dir="/opt/maven/repository") == (
        "/opt/maven/bin/mvn",
        "--offline",
        "--batch-mode",
        "--no-transfer-progress",
        "--strict-checksums",
        "-Dmaven.repo.local=/opt/maven/repository",
        "test",
    )
