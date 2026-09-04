from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from nl2repobench.domain.models import Visibility
from nl2repobench.package_managers.dependency_artifacts import (
    LOCK_MEDIA_TYPE,
    STORE_MEDIA_TYPE,
    put_dependency_archive,
    put_dependency_inventory,
)
from nl2repobench.storage.artifacts import FileArtifactStore
from nl2repobench.storage.canonical_ustar import CanonicalEntry, encode_ustar
from nl2repobench.verification import java_private_artifacts
from nl2repobench.verification.java_private_artifacts import (
    JavaPrivateArtifactError,
    materialize,
)


def test_java_private_inputs_are_materialized_from_scoped_cas(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "cas")
    toolchain_digest = "sha256:" + "a" * 64
    lock_data = (
        b'{"artifacts":[],"effective_project":{"artifact_id":"harness",'
        b'"group_id":"example","packaging":"jar","release":21,"version":"1.0.0"},'
        b'"jdk_version":"temurin-21.0.12+8","maven_version":"3.9.11",'
        b'"offline_smoke":{"status":"passed"},"plugins":[],"repositories":[],'
        b'"schema_version":"1.0"}\n'
    )
    lock_entries = (CanonicalEntry("maven-lock-v1.json", "file", 0o444, lock_data),)
    store_entries = (CanonicalEntry("maven-repository/", "directory", 0o555),)
    lock = put_dependency_archive(store, lock_entries, media_type=LOCK_MEDIA_TYPE)
    offline_store = put_dependency_archive(
        store, store_entries, media_type=STORE_MEDIA_TYPE
    )
    inventory = put_dependency_inventory(
        store,
        identity="java+maven",
        adapter_version="maven-offline-v1",
        toolchain_digest=toolchain_digest,
        lock_ref=lock,
        lock_entries=lock_entries,
        store_ref=offline_store,
        store_entries=store_entries,
        smoke_command_id="maven-test-offline-v1",
    )
    verifier = store.put_bytes(
        encode_ustar(
            (
                CanonicalEntry("harness/", "directory", 0o555),
                CanonicalEntry(
                    "harness/src/main/java/nl2repobench/harness/ContractMain.java",
                    "file",
                    0o444,
                    b"class ContractMain {}\n",
                ),
            )
        ),
        media_type="application/vnd.nl2repobench.verifier+tar",
        visibility=Visibility.PRIVATE,
    )
    refs = {
        "schema_version": "1.0",
        "toolchain_digest": toolchain_digest,
        "maven_version": "3.9.11",
        "dependency_refs": {
            "lock": lock.model_dump(mode="json"),
            "offline_store": offline_store.model_dump(mode="json"),
            "inventory": inventory.model_dump(mode="json"),
        },
        "verifier_ref": verifier.model_dump(mode="json"),
    }
    refs_path = tmp_path / "private-artifact-refs.json"
    refs_path.write_text(
        json.dumps(refs, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    dependencies = tmp_path / "dependencies"
    verifier_root = tmp_path / "verifier"
    materialize(refs_path, store.root, dependencies, verifier_root)

    assert (dependencies / "maven-lock-v1.json").read_bytes() == lock_data
    assert (dependencies / "maven-repository").is_dir()
    assert (
        verifier_root
        / "harness/src/main/java/nl2repobench/harness/ContractMain.java"
    ).is_file()


@pytest.mark.parametrize(
    ("reference", "message"),
    [
        ({}, "malformed"),
        (
            {
                "schema_version": "1.0",
                "digest": "bad",
                "size_bytes": 0,
                "media_type": "application/vnd.nl2repobench.package-lock.tar",
                "uri": "artifact://private/bad",
                "visibility": "private",
            },
            "digest is invalid",
        ),
        (
            {
                "schema_version": "1.0",
                "digest": "sha256:" + "a" * 64,
                "size_bytes": 0,
                "media_type": "application/vnd.nl2repobench.package-lock.tar",
                "uri": "artifact://public/sha256:" + "a" * 64,
                "visibility": "public",
            },
            "visibility or URI",
        ),
        (
            {
                "schema_version": "1.0",
                "digest": "sha256:" + "a" * 64,
                "size_bytes": -1,
                "media_type": "wrong",
                "uri": "artifact://private/sha256:" + "a" * 64,
                "visibility": "private",
            },
            "media type",
        ),
    ],
)
def test_java_private_ref_rejects_invalid_contract(
    tmp_path: Path, reference: dict[str, object], message: str
) -> None:
    with pytest.raises(JavaPrivateArtifactError, match=message):
        java_private_artifacts._ref_path(  # noqa: SLF001
            tmp_path, reference, reference_kind="lock"
        )


@pytest.mark.parametrize("name", ["/absolute", "../escape", ".", "a/../b"])
def test_java_private_archive_rejects_unsafe_paths(tmp_path: Path, name: str) -> None:
    with pytest.raises(JavaPrivateArtifactError, match="path is unsafe"):
        java_private_artifacts._safe_target(tmp_path, name)  # noqa: SLF001


def test_java_private_refs_reject_invalid_json_and_schema(tmp_path: Path) -> None:
    refs = tmp_path / "refs.json"
    refs.write_text("not-json", encoding="utf-8")
    with pytest.raises(JavaPrivateArtifactError, match="refs are invalid"):
        java_private_artifacts._load_refs(refs)  # noqa: SLF001
    refs.write_text('{"schema_version":"1.0"}', encoding="utf-8")
    with pytest.raises(JavaPrivateArtifactError, match="refs schema"):
        java_private_artifacts._load_refs(refs)  # noqa: SLF001


def test_java_private_artifact_cli_returns_bounded_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "java-private-artifacts",
            "--refs",
            str(tmp_path / "missing.json"),
            "--cas",
            str(tmp_path / "cas"),
            "--dependencies",
            str(tmp_path / "dependencies"),
            "--verifier",
            str(tmp_path / "verifier"),
        ],
    )

    assert java_private_artifacts.main() == 20
    assert "private artifact refs are invalid" in capsys.readouterr().out


def test_java_private_ref_checks_missing_size_and_digest(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "cas")
    reference = store.put_bytes(
        b"abc",
        media_type="application/vnd.nl2repobench.verifier+tar",
        visibility=Visibility.PRIVATE,
    ).model_dump(mode="json")
    missing = dict(reference)
    missing["digest"] = "sha256:" + "a" * 64
    missing["uri"] = f"artifact://private/{missing['digest']}"
    with pytest.raises(JavaPrivateArtifactError, match="artifact is missing"):
        java_private_artifacts._ref_path(  # noqa: SLF001
            store.root, missing, reference_kind="verifier"
        )

    wrong_size = dict(reference)
    wrong_size["size_bytes"] = 4
    with pytest.raises(JavaPrivateArtifactError, match="size mismatch"):
        java_private_artifacts._ref_path(  # noqa: SLF001
            store.root, wrong_size, reference_kind="verifier"
        )

    artifact = java_private_artifacts._ref_path(  # noqa: SLF001
        store.root, reference, reference_kind="verifier"
    )
    artifact.write_bytes(b"abd")
    with pytest.raises(JavaPrivateArtifactError, match="digest mismatch"):
        java_private_artifacts._ref_path(  # noqa: SLF001
            store.root, reference, reference_kind="verifier"
        )
