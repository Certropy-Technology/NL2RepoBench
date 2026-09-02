from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tarfile
import tomllib
from pathlib import Path
from typing import cast

import pytest
import tomli_w

from nl2repobench.domain.canonical_models import ArtifactRef
from nl2repobench.storage.artifacts import (
    FileArtifactStore,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.canonical_ustar import decode_archive
from nl2repobench.storage.materialize import ArchiveKind, materialize_archive

SCRIPT = Path(__file__).parents[1] / "scripts/prepare_private_release.py"
SPEC = importlib.util.spec_from_file_location("prepare_private_release", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _legacy_tar(*members: tuple[str, bytes]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w", format=tarfile.GNU_FORMAT) as archive:
        for name, payload in members:
            info = tarfile.TarInfo(name)
            info.mode = 0o644
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    return output.getvalue()


def _ref(data: bytes) -> tuple[str, int]:
    return f"sha256:{hashlib.sha256(data).hexdigest()}", len(data)


def _write_cas(cas: Path, data: bytes) -> tuple[str, int]:
    digest, size = _ref(data)
    target = cas / digest.removeprefix("sha256:")[:2] / digest.removeprefix("sha256:")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return digest, size


def _source(tmp_path: Path, *, packages: list[str] | None = None) -> tuple[Path, Path, Path]:
    task_root = tmp_path / "demo"
    task_root.mkdir(parents=True)
    cas = tmp_path / "cas"
    cas.mkdir()
    command_data = _legacy_tar(
        (
            "command-plan.json",
            json.dumps(
                {
                    "schema_version": "2.0",
                    "runner": "node-test-subprocess-boundary-v1",
                    "candidate_install": "npm-pack-offline-v1",
                    "report_format": "node-test-json-v1",
                    "test_root": "/tests/private",
                },
                separators=(",", ":"),
            ).encode(),
        )
    )
    test_data = _legacy_tar(("contract.test.mjs", b"test"))
    oracle_data = _legacy_tar(("solve.sh", b"#!/bin/sh\n"))
    command_digest, command_size = _write_cas(cas, command_data)
    test_digest, test_size = _write_cas(cas, test_data)
    oracle_digest, oracle_size = _write_cas(cas, oracle_data)
    def private_ref(digest: str, size: int, media: str) -> dict[str, object]:
        return {
            "digest": digest,
            "size_bytes": size,
            "media_type": media,
            "uri": f"artifact://private/{digest}",
            "visibility": "private",
        }
    payload = {
        "schema_version": "1.0",
        "task_id": "demo",
        "version": "1.0.0",
        "instruction": "instruction.md",
        "metadata": {
            "difficulty": "easy",
            "category": "demo",
            "tags": ["node", "npm"],
            "language": "node",
        },
        "source": {
            "status": "known",
            "upstream_url": "https://example.invalid/demo",
            "revision": "a" * 40,
            "license_spdx": "MIT",
            "source_digest": "sha256:" + "b" * 64,
        },
        "environment": {
            "status": "known",
            "os_name": "debian-bookworm",
            "base_image": "node@sha256:" + "c" * 64,
            "base_image_digest": "sha256:" + "c" * 64,
            "network_policy": {
                "mode": "no-network",
                "offline_dependencies": "preinstalled-image",
                "reference_source_fetch": "forbidden",
                "reason": "test",
            },
            "runtime": {
                "language": "node",
                "runtime": "node",
                "version": "24.19.0",
                "package_manager": "npm",
                "package_manager_version": "11.17.0",
            },
        },
        "dependencies": {"status": "unknown", "package_manager": "npm", "packages": packages or []},
        "tests": {
            "framework": "node:test",
            "report_format": "node-test-json-v1",
            "expected_total": 1,
            "expected_total_source": "frozen-collection",
            "commands_artifact": private_ref(
                command_digest,
                command_size,
                "application/vnd.nl2repobench.node-commands+tar",
            ),
            "test_bundle": private_ref(
                test_digest, test_size, "application/vnd.nl2repobench.node-tests+tar"
            ),
        },
        "lifecycle": {"status": "blocked", "reason": "staging test"},
        "oracle_bundle": private_ref(
            oracle_digest, oracle_size, "application/vnd.nl2repobench.oracle+tar"
        ),
    }
    (task_root / "task.toml").write_text(tomli_w.dumps(payload), encoding="utf-8")
    (task_root / "instruction.md").write_text("Build demo.\n", encoding="utf-8")
    toolchain = tmp_path / "toolchain.lock.toml"
    toolchain.write_text("schema_version = '1.0'\n", encoding="utf-8")
    return task_root, cas, toolchain


def _prepare(
    tmp_path: Path,
    *,
    packages: list[str] | None = None,
    staging_name: str = "stage",
) -> dict[str, object]:
    task, cas, toolchain = _source(tmp_path, packages=packages)
    return cast(
        dict[str, object],
        MODULE.prepare_private_release(
            task_root=task,
            cas_root=cas,
            staging_root=tmp_path / staging_name,
            toolchain=toolchain,
            new_version="2.0.0",
            empty_npm_closure=True,
        ),
    )


def test_preparer_does_not_overwrite_old_cas_and_is_repeatable(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path)
    old_bytes = next(path for path in cas.rglob("*") if path.is_file())
    original = old_bytes.read_bytes()
    kwargs = dict(
        task_root=task,
        cas_root=cas,
        staging_root=tmp_path / "stage",
        toolchain=toolchain,
        new_version="2.0.0",
        empty_npm_closure=True,
    )
    first = MODULE.prepare_private_release(**kwargs)
    second = MODULE.prepare_private_release(**kwargs)
    assert first == second
    assert old_bytes.read_bytes() == original


def test_preparer_output_is_deterministic(tmp_path: Path) -> None:
    first = _prepare(tmp_path / "one", staging_name="stage")
    second = _prepare(tmp_path / "two", staging_name="stage")
    assert first == second


def test_missing_cas_is_rejected(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path)
    missing = next(path for path in cas.rglob("*") if path.is_file())
    missing.unlink()
    with pytest.raises(MODULE.PrivateReleasePreparationError, match="CAS"):
        MODULE.prepare_private_release(
            task_root=task,
            cas_root=cas,
            staging_root=tmp_path / "stage",
            toolchain=toolchain,
            new_version="2.0.0",
            empty_npm_closure=True,
        )


def test_unknown_or_nonempty_dependency_case_is_rejected(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path, packages=["left-pad"])
    with pytest.raises(
        MODULE.PrivateReleasePreparationError,
        match="empty npm package list|empty packages",
    ):
        MODULE.prepare_private_release(
            task_root=task,
            cas_root=cas,
            staging_root=tmp_path / "stage",
            toolchain=toolchain,
            new_version="2.0.0",
            empty_npm_closure=True,
        )


def test_empty_npm_closure_has_canonical_archives_and_inventory(tmp_path: Path) -> None:
    metadata = _prepare(tmp_path)
    dependencies = metadata["dependencies"]
    assert isinstance(dependencies, dict)
    stage = tmp_path / "stage" / "artifacts" / "private" / "sha256"
    lock_digest = dependencies["lock"]["digest"].removeprefix("sha256:")
    store_digest = dependencies["offline_store"]["digest"].removeprefix("sha256:")
    inventory_digest = dependencies["inventory"]["digest"].removeprefix("sha256:")
    lock = (stage / lock_digest[:2] / lock_digest).read_bytes()
    store = (stage / store_digest[:2] / store_digest).read_bytes()
    inventory = json.loads((stage / inventory_digest[:2] / inventory_digest).read_bytes())
    assert [(item.entry.path, item.data) for item in decode_archive(lock)] == [
        ("package-lock.json", b'{"lockfileVersion":3,"packages":{"":{}}}\n')
    ]
    assert decode_archive(store) == ()
    assert inventory["lock"]["file_count"] == 1
    assert inventory["store"]["file_count"] == 0
    assert inventory["offline_smoke"] == {
        "status": "not-run",
        "command_id": "node-npm-offline-install-v1",
    }
    assert metadata["status"] == "blocked"
    assert metadata["oracle_receipt"] is None
    assert metadata["controls_receipts"] == {}
    plan = cast(dict[str, object], metadata["source_update_plan"])
    operations = cast(list[dict[str, object]], plan["operations"])
    assert not any(
        cast(str, operation["path"]).startswith("dependencies") for operation in operations
    )
    assert "dependencies remain unknown pending exact node-npm-offline-install-v1 receipt" in cast(
        str, plan["reason"]
    )


def test_source_update_requires_evidence_even_with_explicit_opt_in(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path)
    original = (task / "task.toml").read_bytes()
    with pytest.raises(MODULE.PrivateReleasePreparationError, match="release evidence"):
        MODULE.prepare_private_release(
            task_root=task,
            cas_root=cas,
            staging_root=tmp_path / "stage",
            toolchain=toolchain,
            new_version="2.0.0",
            empty_npm_closure=True,
            apply_source_update=True,
            allow_source_update=True,
        )
    assert (task / "task.toml").read_bytes() == original


def test_cli_requires_source_update_opt_in(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path)
    with pytest.raises(SystemExit, match="2"):
        MODULE.main(
            [
                "--task-root",
                str(task),
                "--cas-root",
                str(cas),
                "--staging-root",
                str(tmp_path / "stage"),
                "--toolchain",
                str(toolchain),
                "--new-version",
                "2.0.0",
                "--empty-npm-closure",
                "--apply-source-update",
            ]
        )


def test_preparer_rejects_symlinked_staging_ancestor(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path)
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    with pytest.raises(MODULE.PrivateReleasePreparationError, match="symlinks"):
        MODULE.prepare_private_release(
            task_root=task,
            cas_root=cas,
            staging_root=link / "stage",
            toolchain=toolchain,
            new_version="2.0.0",
            empty_npm_closure=True,
        )


def test_preparer_rejects_symlinked_task_root_ancestor(tmp_path: Path) -> None:
    real_parent = tmp_path / "real"
    task, cas, toolchain = _source(real_parent)
    alias = tmp_path / "alias"
    alias.symlink_to(real_parent, target_is_directory=True)
    with pytest.raises(MODULE.PrivateReleasePreparationError, match="symlinks"):
        MODULE.prepare_private_release(
            task_root=alias / task.name,
            cas_root=cas,
            staging_root=tmp_path / "stage",
            toolchain=toolchain,
            new_version="2.0.0",
            empty_npm_closure=True,
        )


def test_preparer_emits_canonical_command_plan_media(tmp_path: Path) -> None:
    metadata = _prepare(tmp_path)
    artifacts = metadata["artifacts"]
    assert isinstance(artifacts, list)
    command = cast(dict[str, object], artifacts[0])
    assert command["media_type"] == "application/vnd.nl2repobench.command-plan+json"
    assert command["tree_digest"] is None


def test_preparer_materializes_staged_test_and_oracle_with_scoped_resolver(
    tmp_path: Path,
) -> None:
    metadata = _prepare(tmp_path)
    stage = tmp_path / "stage"
    store = FileArtifactStore(stage / "artifacts")
    artifact_records = cast(list[dict[str, object]], metadata["artifacts"])
    refs = [
        ArtifactRef.model_validate(
            {
                "digest": record["new_sha256"],
                "size_bytes": record["new_size"],
                "media_type": record["media_type"],
                "uri": record["new_ref"],
                "visibility": "private",
            }
        )
        for record in artifact_records
    ]
    dependencies = cast(dict[str, dict[str, object]], metadata["dependencies"])
    refs.extend(
        ArtifactRef.model_validate(
            {
                "digest": value["digest"],
                "size_bytes": value["size"],
                "uri": value["ref"],
                "media_type": (
                    "application/vnd.nl2repobench.inventory+json"
                    if name == "inventory"
                    else (
                        "application/vnd.nl2repobench.package-lock.tar"
                        if name == "lock"
                        else "application/vnd.nl2repobench.offline-store.tar"
                    )
                ),
                "visibility": "private",
            }
        )
        for name, value in dependencies.items()
    )
    authorization = PrivateArtifactAuthorization(
        task_id="demo",
        manifest_digest="sha256:" + "a" * 64,
        purpose="compile",
        allowed_digests=frozenset(reference.digest for reference in refs),
        staging_root=stage.resolve(),
    )
    resolver = LocalArtifactResolver.scoped_private(
        store,
        authorization,
        task_id="demo",
        manifest_digest=authorization.manifest_digest,
        purpose="compile",
        staging_root=stage,
    )
    for record, kind, name in (
        (artifact_records[1], ArchiveKind.TEST_BUNDLE, "tests"),
        (artifact_records[2], ArchiveKind.ORACLE_BUNDLE, "oracle"),
    ):
        reference = refs[artifact_records.index(record)]
        result = materialize_archive(
            reference,
            kind,
            stage / name,
            None,
            authorization,
            resolver=resolver,
        )
        assert result.file_count == 1
        assert result.tree_digest == record["tree_digest"]


def test_preparer_accepts_legacy_json_command_media_type(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path)
    payload = tomllib.loads((task / "task.toml").read_text(encoding="utf-8"))
    command_payload = {
        "schema_version": "2.0",
        "runner": "node-test-subprocess-boundary-v1",
        "candidate_install": "npm-pack-offline-v1",
        "report_format": "node-test-json-v1",
        "test_root": "/tests/private",
    }
    command_data = json.dumps(command_payload, separators=(",", ":")).encode()
    digest, size = _write_cas(cas, command_data)
    payload["tests"]["commands_artifact"] = {
        "digest": digest,
        "size_bytes": size,
        "media_type": "application/json",
        "uri": f"artifact://private/{digest}",
        "visibility": "private",
    }
    (task / "task.toml").write_text(tomli_w.dumps(payload), encoding="utf-8")
    metadata = MODULE.prepare_private_release(
        task_root=task,
        cas_root=cas,
        staging_root=tmp_path / "stage",
        toolchain=toolchain,
        new_version="2.0.0",
        empty_npm_closure=True,
    )
    assert cast(dict[str, object], cast(list[object], metadata["artifacts"])[0])["media_type"] == (
        "application/vnd.nl2repobench.command-plan+json"
    )


def test_preparer_rejects_conflicting_existing_staging_leaf(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path)
    stage = tmp_path / "stage"
    MODULE.prepare_private_release(
        task_root=task,
        cas_root=cas,
        staging_root=stage,
        toolchain=toolchain,
        new_version="2.0.0",
        empty_npm_closure=True,
    )
    leaf = next(path for path in (stage / "artifacts").rglob("*") if path.is_file())
    leaf.write_bytes(b"conflict")
    with pytest.raises(MODULE.PrivateReleasePreparationError, match="already differs"):
        MODULE.prepare_private_release(
            task_root=task,
            cas_root=cas,
            staging_root=stage,
            toolchain=toolchain,
            new_version="2.0.0",
            empty_npm_closure=True,
        )


def test_metadata_publication_rejects_concurrent_conflicting_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "release-metadata.json"
    data = b'{"status":"blocked"}\n'

    def link_with_conflict(source: Path, target: Path) -> None:
        target.write_bytes(b"conflict\n")
        raise FileExistsError

    monkeypatch.setattr(MODULE.os, "link", link_with_conflict)
    with pytest.raises(MODULE.PrivateReleasePreparationError, match="metadata race differs"):
        MODULE._write_staging_metadata(path, data)
    assert path.read_bytes() == b"conflict\n"


def test_empty_npm_closure_requires_unknown_dependency_status(tmp_path: Path) -> None:
    task, cas, toolchain = _source(tmp_path)
    payload = tomllib.loads((task / "task.toml").read_text(encoding="utf-8"))
    payload["dependencies"]["status"] = "known"
    (task / "task.toml").write_text(tomli_w.dumps(payload), encoding="utf-8")
    with pytest.raises(
        MODULE.PrivateReleasePreparationError,
        match="invalid canonical task source",
    ):
        MODULE.prepare_private_release(
            task_root=task,
            cas_root=cas,
            staging_root=tmp_path / "stage",
            toolchain=toolchain,
            new_version="2.0.0",
            empty_npm_closure=True,
        )
