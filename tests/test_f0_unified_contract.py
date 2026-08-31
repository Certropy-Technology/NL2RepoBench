from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tarfile
import tomllib
import unicodedata
from copy import deepcopy
from io import BytesIO
from pathlib import Path

import pytest
import tomli_w
from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate as validate_json_schema
from pydantic import ValidationError as PydanticValidationError

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.canonical_contract import (
    DependencyBundle,
    EnvironmentLock,
    PackageManager,
    TaskManifest,
    TaskMetadata,
    TaskSource,
)
from nl2repobench.domain.canonical_contract import TestManifest as CanonicalTestManifest
from nl2repobench.domain.canonical_models import ArtifactRef, Visibility
from nl2repobench.domain.command_plan import CommandPlan
from nl2repobench.harbor.bundle_io import BundleLimits
from nl2repobench.harbor.models import load_command_plan
from nl2repobench.harbor.private_artifacts import (
    categorized_private_artifacts,
    compile_authorization,
)
from nl2repobench.harbor.task_writer import extract_private_bundle
from nl2repobench.storage.artifacts import (
    ArtifactStoreError,
    FileArtifactStore,
    LocalArtifactResolver,
    MigrationArtifactAuthorization,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.canonical_ustar import (
    EMPTY_TREE_DIGEST,
    TreeEntry,
    decode_archive,
    encode_files,
    tree_digest,
)
from nl2repobench.storage.materialize import ArchiveKind, MaterializationLimits, materialize_archive
from nl2repobench.verification.command_plan import load_python_command_plan
from nl2repobench.verification.go_command_plan import load_go_command_plan
from nl2repobench.verification.node_command_plan import load_node_command_plan


def _migration_module():
    path = Path(__file__).parents[1] / "tools/migrations/unified_runtime_contract_20260830.py"
    spec = importlib.util.spec_from_file_location("f0_migration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_empty_ustar_and_tree_digest_are_canonical() -> None:
    archive = encode_files({})
    assert len(archive) == 10240
    assert hashlib.sha256(archive).hexdigest() == (
        "84ff92691f909a05b224e1c56abb4864f01b4f8e3c854e4bb4c7baf1d3f6d652"
    )
    assert tree_digest([]) == EMPTY_TREE_DIGEST


def test_nonempty_tree_digest_uses_uppercase_type_bytes() -> None:
    assert tree_digest([TreeEntry("a", "file", 0o444, 1, hashlib.sha256(b"x").hexdigest())]) == (
        "sha256:646454cea29bdf7b6b2c80e13ee22da5c519091809e8e797363a89e6cd0c92cb"
    )
    assert tree_digest([TreeEntry("d", "directory", 0o555, 0, None)]) == (
        "sha256:7c5c7c08bf6dab47616c5dbb54e5b6bb0f115fdaf90d60f5ea2b1b9c60bbdfb9"
    )


@pytest.mark.parametrize(
    ("files", "executable", "digest"),
    [
        (
            {"a": b"x"},
            frozenset(),
            "30e1785c730dbfd5f9dd429402876d85278f55a41f6837bce1f8fe5ab0c94ade",
        ),
        (
            {"bin/run": b"#!/bin/sh\n"},
            frozenset({"bin/run"}),
            "6b16641492e9e8863bb416093216ecbdbed09f2e5d10f73fa21788dd94ad4dee",
        ),
        (
            {"a" * 99 + "/b": b"z"},
            frozenset(),
            "9be3294b9fa45040b07b5694c604ac86bc59c990009bc20598b019ab02c8b1da",
        ),
    ],
)
def test_ustar_golden_shapes(
    files: dict[str, bytes], executable: frozenset[str], digest: str
) -> None:
    assert hashlib.sha256(encode_files(files, executable)).hexdigest() == digest


@pytest.mark.parametrize("name", ["empty", "single-file", "directory-executable", "prefix-split"])
def test_checked_in_ustar_fixtures(name: str) -> None:
    root = Path(__file__).parent / "fixtures/canonical_ustar"
    archive = (root / f"{name}.tar").read_bytes()
    expected = (root / f"{name}.tar.sha256").read_text(encoding="ascii").strip()
    assert hashlib.sha256(archive).hexdigest() == expected
    decode_archive(archive)


def test_private_resolution_requires_matching_task_capability(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "cas")
    reference = store.put_bytes(b"private", visibility=Visibility.PRIVATE)
    with pytest.raises(ArtifactStoreError, match="not authorized"):
        LocalArtifactResolver(store).resolve(reference)
    authorization = PrivateArtifactAuthorization(
        task_id="task-a",
        manifest_digest="sha256:" + "a" * 64,
        purpose="compile",
        allowed_digests=frozenset({reference.digest}),
        staging_root=tmp_path / "compiled" / "task-a",
    )
    resolver = LocalArtifactResolver.scoped_private(
        store,
        authorization,
        task_id="task-a",
        manifest_digest=authorization.manifest_digest,
        purpose="compile",
        staging_root=authorization.staging_root,
    )
    assert resolver.resolve(reference).is_file()
    denied = PrivateArtifactAuthorization(
        task_id="task-b",
        manifest_digest=authorization.manifest_digest,
        purpose="compile",
        allowed_digests=frozenset({"sha256:" + "b" * 64}),
        staging_root=tmp_path / "compiled" / "task-b",
    )
    with pytest.raises(ArtifactStoreError, match="not authorized"):
        LocalArtifactResolver(store, denied).resolve(reference)
    with pytest.raises(ArtifactStoreError, match="scope does not match"):
        LocalArtifactResolver.scoped_private(
            store,
            authorization,
            task_id="task-a",
            manifest_digest="sha256:" + "c" * 64,
            purpose="compile",
            staging_root=authorization.staging_root,
        )


def _bundle_archive(*, tree: str | None = None) -> bytes:
    data = b"payload"
    entries = [TreeEntry("data.txt", "file", 0o444, len(data), hashlib.sha256(data).hexdigest())]
    inventory = {
        "schema_version": "1.0",
        "archive_kind": "test-bundle",
        "tree_digest": tree or tree_digest(entries),
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
        "file_count": 1,
        "directory_count": 0,
        "total_bytes": len(data),
    }
    return encode_files(
        {
            "_nl2repo.bundle-inventory.json": json.dumps(
                inventory, sort_keys=True, separators=(",", ":")
            ).encode()
            + b"\n",
            "data.txt": data,
        }
    )


def _materializer(tmp_path: Path, archive: bytes):
    store = FileArtifactStore(tmp_path / "cas")
    reference = store.put_bytes(
        archive,
        media_type="application/vnd.nl2repobench.test-bundle.tar",
        visibility=Visibility.PRIVATE,
    )
    authorization = PrivateArtifactAuthorization(
        task_id="task-a",
        manifest_digest="sha256:" + "a" * 64,
        purpose="compile",
        allowed_digests=frozenset({reference.digest}),
        staging_root=(tmp_path / "compiled/task-a/private/aaaaaaaaaaaaaaaa").resolve(),
    )
    resolver = LocalArtifactResolver.scoped_private(
        store,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )
    return reference, authorization, resolver


def test_materializer_verifies_tree_and_preserves_destination_on_failure(tmp_path: Path) -> None:
    reference, authorization, resolver = _materializer(
        tmp_path, _bundle_archive(tree="sha256:" + "0" * 64)
    )
    destination = authorization.staging_root / "tests"
    destination.mkdir(parents=True)
    (destination / "existing").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="tree digest"):
        materialize_archive(
            reference,
            ArchiveKind.TEST_BUNDLE,
            destination,
            None,
            authorization,
            resolver=resolver,
        )
    assert (destination / "existing").read_text(encoding="utf-8") == "keep"
    assert not list(destination.parent.glob(".tests-*"))


def test_materializer_atomically_extracts_valid_canonical_bundle(tmp_path: Path) -> None:
    reference, authorization, resolver = _materializer(tmp_path, _bundle_archive())
    destination = authorization.staging_root / "tests"
    result = materialize_archive(
        reference,
        ArchiveKind.TEST_BUNDLE,
        destination,
        None,
        authorization,
        resolver=resolver,
    )
    assert result.destination == destination
    assert result.file_count == 1
    assert result.total_bytes == len(b"payload")
    assert result.inventory_digest is not None
    assert (destination / "data.txt").read_bytes() == b"payload"
    assert (destination / "data.txt").stat().st_mode & 0o777 == 0o444


def test_task_writer_uses_scoped_canonical_materializer(tmp_path: Path) -> None:
    reference, authorization, resolver = _materializer(tmp_path, _bundle_archive())
    destination = authorization.staging_root / "tests"
    extract_private_bundle(
        reference,
        destination,
        artifact_resolver=resolver,
        limits=BundleLimits(10, 1024, 4096),
        kind=ArchiveKind.TEST_BUNDLE,
    )
    assert (destination / "data.txt").read_bytes() == b"payload"
    assert not (destination / "_nl2repo.bundle-inventory.json").exists()


def test_migration_repackages_runtime_bundle_with_internal_inventory(tmp_path: Path) -> None:
    module = _migration_module()
    payload = BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        for name, data, mode in (
            ("test.sh", b"#!/bin/sh\nexit 0\n", 0o755),
            ("fixtures/data.txt", b"payload", 0o644),
        ):
            member = tarfile.TarInfo(name)
            member.size = len(data)
            member.mode = mode
            archive.addfile(member, BytesIO(data))
    store = FileArtifactStore(tmp_path / "cas")
    reference = module.repackage_runtime_bundle(
        store, payload.getvalue(), kind=ArchiveKind.TEST_BUNDLE
    )
    assert reference.media_type == "application/vnd.nl2repobench.test-bundle.tar"
    authorization = MigrationArtifactAuthorization(
        migration_id="test-migration",
        allowed_digests=frozenset({reference.digest}),
        workspace_root=tmp_path.resolve(),
    )
    members = decode_archive(store.read_bytes(reference, authorization))
    inventory_member = next(
        item for item in members if item.entry.path == "_nl2repo.bundle-inventory.json"
    )
    inventory = json.loads(inventory_member.data)
    assert inventory["archive_kind"] == "test-bundle"
    assert [item["path"] for item in inventory["entries"]] == [
        "fixtures",
        "fixtures/data.txt",
        "test.sh",
    ]
    assert next(item for item in members if item.entry.path == "test.sh").entry.mode == 0o555


def test_migration_converts_legacy_artifact_backed_command_and_paths(tmp_path: Path) -> None:
    module = _migration_module()
    store = FileArtifactStore(tmp_path / "cas")
    command = store.put_bytes(
        json.dumps({"runner": "legacy", "candidate_install": "legacy"}).encode(),
        visibility=Visibility.PRIVATE,
    )
    protected = store.put_bytes(
        json.dumps({"paths": ["/tests/private/contract.mjs"]}).encode(),
        visibility=Visibility.PRIVATE,
    )
    converted = module._migrate_command_reference(
        store,
        command.model_dump(mode="json"),
        identity="node+npm",
        report_format="node-test-json-v1",
        task_id="legacy-task",
        workspace_root=tmp_path,
    )
    converted_paths = module._migrate_protected_reference(
        store,
        protected.model_dump(mode="json"),
        task_id="legacy-task",
        workspace_root=tmp_path,
    )
    assert converted is not None and converted["media_type"].endswith("command-plan+json")
    assert converted_paths is not None and converted_paths["media_type"].endswith(
        "protected-paths+json"
    )
    converted_ref = ArtifactRef.model_validate(converted)
    converted_auth = module.MigrationArtifactAuthorization(
        migration_id=module.ROOT_NAME,
        allowed_digests=frozenset({converted["digest"]}),
        workspace_root=tmp_path,
    )
    command_payload = json.loads(store.read_bytes(converted_ref, converted_auth))
    assert command_payload["identity"] == "node+npm"
    assert command_payload["steps"] == []


@pytest.mark.parametrize(
    ("identity", "runner", "candidate_install"),
    [
        ("python+uv", "pytest-subprocess-boundary-v1", "pip-target-no-deps-v1"),
        ("node+npm", "node-test-subprocess-boundary-v1", "npm-pack-offline-v1"),
        ("node+pnpm", "node-test-subprocess-boundary-v1", "pnpm-pack-offline-v1"),
        ("go+go-modules", "go-test-subprocess-boundary-v1", "go-modules-offline-v1"),
    ],
)
def test_migrated_command_plan_uses_adapter_contract(
    identity: str, runner: str, candidate_install: str
) -> None:
    module = _migration_module()
    report_format = (
        "node-test-json-v1"
        if identity.startswith("node+")
        else "pytest-junit-xml-v1"
        if identity.startswith("python+")
        else "go-test-json-v1"
    )
    plan_data = module._canonical_command_plan(  # noqa: SLF001
        [], identity=identity, report_format=report_format
    )
    assert plan_data["runner"] == runner
    assert plan_data["candidate_install"] == candidate_install
    data = json.dumps(plan_data, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    CommandPlan.model_validate(plan_data)
    if identity.startswith("node+"):
        load_node_command_plan(data, candidate_install=candidate_install)  # type: ignore[arg-type]
    else:
        load_command_plan(data)


def test_generic_plan_accepts_bounded_steps_but_executable_adapters_reject() -> None:
    steps = [
        {
            "step_id": f"step-{index:04d}",
            "argv": ["runner", "x" * 160],
            "cwd": ".",
            "environment": {"CASE": str(index)},
            "timeout_sec": 600,
        }
        for index in range(32)
    ]
    plans = (
        (
            {
                "identity": "python+uv",
                "runner": "pytest-subprocess-boundary-v1",
                "candidate_install": "pip-target-no-deps-v1",
                "report_format": "pytest-junit-xml-v1",
                "steps": steps,
            },
            load_python_command_plan,
        ),
        (
            {
                "identity": "go+go-modules",
                "runner": "go-test-subprocess-boundary-v1",
                "candidate_install": "go-modules-offline-v1",
                "report_format": "go-test-json-v1",
                "steps": steps,
            },
            load_go_command_plan,
        ),
    )
    for payload, loader in plans:
        plan = CommandPlan.model_validate(payload)
        data = canonical_json(plan) + b"\n"
        assert 4096 < len(data) <= 4 * 1024 * 1024
        assert load_command_plan(data) == plan
        with pytest.raises(ValueError, match="setup steps are not supported") as raised:
            loader(data)
        assert raised.value.code == "plan-invalid"  # type: ignore[attr-defined]
        assert raised.value.stage == "setup-not-supported"  # type: ignore[attr-defined]

    node_payload = {
        "identity": "node+npm",
        "runner": "node-test-subprocess-boundary-v1",
        "candidate_install": "npm-pack-offline-v1",
        "report_format": "node-test-json-v1",
        "steps": steps,
    }
    node_plan = CommandPlan.model_validate(node_payload)
    node_data = canonical_json(node_plan) + b"\n"
    assert load_command_plan(node_data) == node_plan
    with pytest.raises(ValueError, match="setup steps are not supported"):
        load_node_command_plan(node_data, candidate_install="npm-pack-offline-v1")


def test_node_runtime_validators_reject_nonempty_steps(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    root = Path(__file__).parents[1] / "src/nl2repobench/verification/node"
    for manager, validator, install in (
        ("npm", "validate-command-plan.mjs", "npm-pack-offline-v1"),
        ("pnpm", "validate-pnpm-command-plan.mjs", "pnpm-pack-offline-v1"),
    ):
        plan = CommandPlan(
            identity=f"node+{manager}",
            runner="node-test-subprocess-boundary-v1",
            candidate_install=install,
            report_format="node-test-json-v1",
            steps=(
                {
                    "step_id": "setup",
                    "argv": ("runner",),
                    "cwd": ".",
                    "environment": {},
                    "timeout_sec": 60,
                },
            ),
        )
        path = tmp_path / f"{manager}.json"
        path.write_bytes(canonical_json(plan) + b"\n")
        result = subprocess.run(
            [node, str(root / validator), "--path", str(path)],
            check=False,
        )
        assert result.returncode != 0


def test_migration_rejects_legacy_nonempty_command_steps() -> None:
    module = _migration_module()
    with pytest.raises(module.MigrationError, match="candidate supervisor") as raised:
        module._canonical_command_plan(  # noqa: SLF001
            ["pytest -q"],
            identity="python+uv",
            report_format="pytest-junit-xml-v1",
        )
    assert raised.value.code == "plan-invalid"
    assert raised.value.stage == "setup-not-supported"


def test_shared_command_plan_loader_rejects_more_than_four_mib() -> None:
    plan = CommandPlan.model_validate(
        {
            "identity": "python+uv",
            "runner": "pytest-subprocess-boundary-v1",
            "candidate_install": "pip-target-no-deps-v1",
            "report_format": "pytest-junit-xml-v1",
            "steps": [
                {
                    "step_id": "large",
                    "argv": ["runner", "x" * (4 * 1024 * 1024)],
                    "cwd": ".",
                    "environment": {},
                    "timeout_sec": 600,
                }
            ],
        }
    )
    data = canonical_json(plan) + b"\n"
    assert len(data) > 4 * 1024 * 1024

    with pytest.raises(ValueError, match="exceeds size limit"):
        load_command_plan(data)


def test_command_plan_bounds_and_deduplicates_step_ids() -> None:
    step = {
        "step_id": "same",
        "argv": ["pytest"],
        "cwd": ".",
        "environment": {},
        "timeout_sec": 600,
    }
    with pytest.raises(PydanticValidationError, match="unique"):
        CommandPlan.model_validate(
            {
                "identity": "python+uv",
                "runner": "pytest-subprocess-boundary-v1",
                "candidate_install": "pip-target-no-deps-v1",
                "report_format": "pytest-junit-xml-v1",
                "steps": [step, step],
            }
        )
    with pytest.raises(PydanticValidationError, match="4096"):
        CommandPlan.model_validate(
            {
                "identity": "python+uv",
                "runner": "pytest-subprocess-boundary-v1",
                "candidate_install": "pip-target-no-deps-v1",
                "report_format": "pytest-junit-xml-v1",
                "steps": [
                    {**step, "step_id": f"step-{index}"} for index in range(4097)
                ],
            }
        )


def _legacy_json_tar(*members: tuple[str, bytes, str | None]) -> bytes:
    payload = BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        for name, data, member_type in members:
            member = tarfile.TarInfo(name)
            member.size = len(data)
            if member_type == "symlink":
                member.type = tarfile.SYMTYPE
                member.linkname = "payload.json"
                member.size = 0
            archive.addfile(member, BytesIO(data) if member_type is None else None)
    return payload.getvalue()


def test_legacy_json_archive_rejects_ambiguous_payloads() -> None:
    module = _migration_module()
    archive = _legacy_json_tar(
        ("first.json", b'{"paths":["one"]}', None),
        ("second.json", b'{"paths":["two"]}', None),
    )
    with pytest.raises(module.MigrationError, match="ambiguous"):
        module._legacy_json_payload(archive)  # noqa: SLF001


def test_legacy_json_archive_rejects_compression_bombs_and_unsafe_types() -> None:
    module = _migration_module()
    bomb = _legacy_json_tar(("bomb.json", b"0" * (module.MAX_LEGACY_JSON_MEMBER_BYTES + 1), None))
    with pytest.raises(module.MigrationError, match="unsupported member|size limit"):
        module._legacy_json_payload(bomb)  # noqa: SLF001
    symlink = _legacy_json_tar(("link.json", b"", "symlink"))
    with pytest.raises(module.MigrationError, match="unsafe member"):
        module._legacy_json_payload(symlink)  # noqa: SLF001


def test_private_artifact_manifest_is_strict_and_excludes_oracle_from_verify(
    tmp_path: Path,
) -> None:
    store = FileArtifactStore(tmp_path / "cas")
    refs = [
        store.put_bytes(str(index).encode(), visibility=Visibility.PRIVATE) for index in range(6)
    ]
    instruction = store.put_bytes(
        b"instruction",
        media_type="text/markdown; charset=utf-8",
        visibility=Visibility.PUBLIC,
    )
    manifest = TaskManifest(
        task_id="contract-test",
        metadata=TaskMetadata(language="python"),
        instruction=instruction,
        environment_lock=EnvironmentLock(status="unknown"),
        dependency_bundle=DependencyBundle(
            status="known",
            package_manager=PackageManager.UV,
            lock=refs[0],
            offline_store=refs[1],
            inventory=refs[2],
        ),
        tests=CanonicalTestManifest(
            framework="pytest",
            report_format="pytest-junit-xml-v1",
            commands_artifact=refs[3],
            test_bundle=refs[4],
        ),
        oracle_bundle=refs[5],
    )
    categorized = categorized_private_artifacts(manifest)
    assert refs[5].digest in categorized.compile_digests()
    assert refs[5].digest not in categorized.verify_digests()
    authorization = compile_authorization(manifest, compiled_root=(tmp_path / "compiled").resolve())
    prefix = manifest.content_digest().removeprefix("sha256:")[:16]
    assert (
        authorization.staging_root
        == (tmp_path / "compiled/contract-test/private" / prefix).resolve()
    )


def _canonical_source_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "task_id": "schema-parity",
        "metadata": {"language": "python"},
        "environment": {"status": "unknown"},
        "dependencies": {"status": "unknown", "package_manager": "uv"},
        "tests": {
            "framework": "pytest",
            "report_format": "pytest-junit-xml-v1",
        },
    }


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data.update(environment={"status": "known"}),
        lambda data: data.update(dependencies={"status": "known", "package_manager": "uv"}),
        lambda data: data.update(
            environment={
                "status": "unknown",
                "runtime": {
                    "language": "python",
                    "runtime": "node",
                    "version": "3.12",
                    "package_manager": "uv",
                    "package_manager_version": "0.8",
                },
            }
        ),
        lambda data: data.update(
            environment={
                "status": "unknown",
                "runtime": {
                    "language": "python",
                    "runtime": "cpython",
                    "version": "3.12",
                    "package_manager": "uv",
                    "package_manager_version": "0.8",
                },
            },
            dependencies={"status": "unknown", "package_manager": "pip"},
        ),
        lambda data: data.update(
            metadata={"language": "node"},
            environment={
                "status": "unknown",
                "runtime": {
                    "language": "python",
                    "runtime": "cpython",
                    "version": "3.12",
                    "package_manager": "uv",
                    "package_manager_version": "0.8",
                },
            },
        ),
        lambda data: data.update(
            environment={
                "status": "unknown",
                "runtime": {
                    "language": "python",
                    "runtime": "cpython",
                    "version": "3.12",
                    "package_manager": "uv",
                    "package_manager_version": "0.8",
                },
            },
            tests={"framework": "node:test", "report_format": "node-test-json-v1"},
        ),
        lambda data: data.update(lifecycle={"status": "packaged"}),
        lambda data: data.update(tests={"framework": "custom", "report_format": "custom-json-v1"}),
    ],
)
def test_task_source_model_and_schema_reject_same_cross_field_gaps(mutate) -> None:
    payload = deepcopy(_canonical_source_payload())
    mutate(payload)
    with pytest.raises(PydanticValidationError):
        TaskSource.model_validate(payload)
    with pytest.raises(JsonSchemaValidationError):
        validate_json_schema(payload, TaskSource.model_json_schema())


def test_task_manifest_mirrors_source_production_invariants() -> None:
    source = TaskSource.model_validate(_canonical_source_payload())
    instruction = {
        "digest": "sha256:" + "1" * 64,
        "size_bytes": 1,
        "media_type": "text/markdown",
        "uri": "artifact://public/sha256:" + "1" * 64,
        "visibility": "public",
    }
    manifest = source.to_manifest(ArtifactRef.model_validate(instruction)).model_dump(mode="json")
    manifest["lifecycle"] = {"status": "packaged"}
    with pytest.raises(PydanticValidationError):
        TaskManifest.model_validate(manifest)
    with pytest.raises(JsonSchemaValidationError):
        validate_json_schema(manifest, TaskManifest.model_json_schema())


def test_production_lifecycle_requires_known_immutable_source_provenance() -> None:
    payload = _canonical_source_payload()
    payload["lifecycle"] = {"status": "packaged"}
    payload["environment"] = {
        "status": "known",
        "runtime": {
            "language": "python",
            "runtime": "cpython",
            "version": "3.12",
            "package_manager": "uv",
            "package_manager_version": "0.8.15",
        },
        "os_name": "linux",
        "base_image": "python@sha256:" + "a" * 64,
        "base_image_digest": "sha256:" + "a" * 64,
        "network_policy": {
            "mode": "no-network",
            "offline_dependencies": "private-artifact",
            "reason": "private closure",
        },
    }
    private = {
        "digest": "sha256:" + "b" * 64,
        "size_bytes": 1,
        "media_type": "application/octet-stream",
        "uri": "artifact://private/sha256:" + "b" * 64,
        "visibility": "private",
    }
    payload["dependencies"] = {
        "status": "known",
        "package_manager": "uv",
        "lock": private,
        "offline_store": private,
        "inventory": private,
    }
    payload["tests"] = {
        "framework": "pytest",
        "report_format": "pytest-junit-xml-v1",
        "expected_total": 1,
        "expected_total_source": "frozen-collection",
        "commands_artifact": private,
        "test_bundle": private,
    }
    with pytest.raises(PydanticValidationError, match="source provenance"):
        TaskSource.model_validate(payload)


def test_known_source_rejects_mutable_url_shape() -> None:
    with pytest.raises(PydanticValidationError, match="immutable HTTPS URL"):
        TaskSource.model_validate(
            {
                **_canonical_source_payload(),
                "source": {
                    "status": "known",
                    "upstream_url": "http://example.test/repo?branch=main",
                    "revision": "a" * 40,
                    "license_spdx": "MIT",
                    "source_digest": "sha256:" + "a" * 64,
                },
            }
        )


def test_materializer_rejects_noncanonical_tar_and_member_limits(tmp_path: Path) -> None:
    malformed = bytearray(_bundle_archive())
    malformed[257:263] = b"ustar "
    reference, authorization, resolver = _materializer(tmp_path, bytes(malformed))
    with pytest.raises(ValueError, match="canonical|POSIX ustar"):
        materialize_archive(
            reference,
            ArchiveKind.TEST_BUNDLE,
            authorization.staging_root / "noncanonical",
            None,
            authorization,
            resolver=resolver,
        )

    reference, authorization, resolver = _materializer(tmp_path / "limited", _bundle_archive())
    with pytest.raises(ValueError, match="too many members"):
        materialize_archive(
            reference,
            ArchiveKind.TEST_BUNDLE,
            authorization.staging_root / "limited",
            MaterializationLimits(1, 1024, 4096),
            authorization,
            resolver=resolver,
        )


def test_canonical_decoder_rejects_non_nfc_paths() -> None:
    decomposed = unicodedata.normalize("NFD", "caf\u00e9")
    assert decomposed != unicodedata.normalize("NFC", decomposed)
    with pytest.raises(ValueError, match="NFC"):
        encode_files({decomposed: b"x"})


def test_migration_plan_requires_all_selected_ids(tmp_path: Path) -> None:
    module = _migration_module()

    root = tmp_path / "sources"
    root.mkdir()
    (root / "ministats").mkdir()
    (root / "ministats" / "task.toml").write_text('schema_version="1.0"\ntask_id="ministats"\n')
    with pytest.raises(module.MigrationError, match="selected migration tasks are missing"):
        module.make_plan(root, tmp_path / "artifacts", tmp_path / "plan.json")


def test_migration_fails_closed_without_private_staging_contract(tmp_path: Path) -> None:
    module = _migration_module()
    root = tmp_path / "sources"
    root.mkdir()
    for task_id in ("ministats", "canonicalize", "node-pnpm-synthetic", "go-google-uuid"):
        task = root / task_id
        task.mkdir()
        (task / "task.toml").write_text(f'task_id="{task_id}"\n', encoding="utf-8")
    with pytest.raises(module.MigrationError, match="private-staging-contract-missing"):
        module.make_plan(root, tmp_path / "artifacts", tmp_path / "plan.json")
    selected = module._validate_selected_compiles(root, tmp_path / "artifacts")
    assert {item["status"] for item in selected} == {"blocked"}
    assert {item["reason"] for item in selected} == {"private-staging-contract-missing"}


def test_migration_never_attests_an_unprepared_closure(tmp_path: Path) -> None:
    module = _migration_module()
    with pytest.raises(module.MigrationError, match="offline dependency closure was not prepared"):
        module.transform_lock_artifact(
            tmp_path / "artifacts",
            b"demo==1 --hash=sha256:" + b"0" * 64 + b"\n",
            identity="python+uv",
            toolchain_digest="sha256:" + "1" * 64,
            store_files=None,
            offline_smoke_command_id="python-uv-offline-install-v1",
            expected_toolchain="1.0.0",
        )


def test_migration_staged_validation_runs_canonical_and_network_gates(tmp_path: Path) -> None:
    module = _migration_module()
    staged = tmp_path / "sources"
    task = staged / "blocked-task"
    task.mkdir(parents=True)
    payload = _canonical_source_payload()
    payload["task_id"] = "blocked-task"
    payload["environment"] = {
        "status": "unknown",
        "network_policy": {
            "mode": "no-network",
            "offline_dependencies": "missing",
            "reference_source_fetch": "forbidden",
            "reason": "Dependency closure is not yet prepared.",
        },
    }
    payload["lifecycle"] = {"status": "blocked", "reason": "F0 migration fixture"}
    (task / "task.toml").write_text(tomli_w.dumps(payload), encoding="utf-8")
    (task / "instruction.md").write_text("# Blocked task\n", encoding="utf-8")
    report = module.validate_staged_tree(
        staged, tmp_path / "artifacts", run_selected_compiles=False
    )
    assert report["status"] == "passed"
    assert report["model"] == {"status": "passed", "task_count": 1}
    assert report["network_lint"]["error_count"] == 0


def test_migration_transaction_is_idempotent(tmp_path: Path) -> None:
    module = _migration_module()

    root = tmp_path / "sources"
    root.mkdir()
    for task_id in ("ministats", "canonicalize", "node-pnpm-synthetic", "go-google-uuid"):
        task = root / task_id
        task.mkdir()
        (task / "task.toml").write_text(
            f'schema_version="1.0"\ntask_id="{task_id}"\n'
            '[metadata]\nlanguage="python"\n'
            '[dependencies]\ninstaller="uv"\n'
            '[tests]\nframework="pytest"\nexpected_total=0\n'
        )
        (task / "instruction.md").write_text("instruction")
        harbor = task / "harbor"
        harbor.mkdir()
        (harbor / "task.toml").write_text('schema_version="1.4"\n')
    scoped = root / "@scope" / "package"
    scoped.mkdir(parents=True)
    (scoped / "task.toml").write_text(
        'schema_version="1.0"\ntask_id="@scope/package"\n'
        '[metadata]\nlanguage="python"\n'
        '[dependencies]\ninstaller="uv"\n'
        '[tests]\nframework="pytest"\nexpected_total=0\n'
    )
    (scoped / "instruction.md").write_text("scoped instruction")
    records = []
    for source_dir in module._source_dirs(root):
        task_file = source_dir / "task.toml"
        relative = task_file.parent.relative_to(root).as_posix()
        data = task_file.read_text(encoding="utf-8") + "# migrated\n"
        records.append(
            {
                "task_id": tomllib.loads(task_file.read_text())["task_id"],
                "source_path": str(task_file.parent),
                "relative_path": relative,
                "old_digest": module.digest_bytes(task_file.read_bytes()),
                "new_toml": data,
            }
        )
    mirror = tmp_path / "mirror"
    import shutil

    shutil.copytree(root, mirror)
    for record in records:
        (mirror / record["relative_path"] / "task.toml").write_text(record["new_toml"])
    plan_path = tmp_path / "migration" / "plan.json"
    plan_path.parent.mkdir()
    plan = {
        "schema_version": "1.0",
        "input_tree_digest": module.digest_tree(root),
        "output_tree_digest": module.digest_tree(mirror),
        "source_root": str(root.resolve()),
        "artifact_root": str((tmp_path / "artifacts").resolve()),
        "staged_path": str(tmp_path / ".sources.unified-test"),
        "previous_path": str(plan_path.parent / "previous-sources"),
        "task_count": len(records),
        "task_mapping_digest": module.digest_bytes(
            json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
        ),
        "records": records,
    }
    plan["plan_digest"] = module.digest_bytes(
        json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
    )
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    transaction = module.apply_plan(plan_path)
    assert transaction["state"] == "complete"
    assert module.recover(plan_path.parent / "transaction.json")["state"] == "complete"
    assert tomllib.loads((root / "ministats" / "task.toml").read_text())["task_id"] == "ministats"


def test_migration_recovery_restores_input_after_exchange_crash(tmp_path: Path) -> None:
    module = _migration_module()
    catalog = tmp_path / "catalog"
    current = catalog / "sources"
    staged = catalog / ".sources.unified-test"
    current.mkdir(parents=True)
    staged.mkdir()
    (current / "input").write_text("old", encoding="utf-8")
    (staged / "output").write_text("new", encoding="utf-8")
    input_digest = module.digest_tree(current)
    output_digest = module.digest_tree(staged)
    module._exchange(current, staged)

    migration = tmp_path / "migration"
    migration.mkdir()
    plan_path = migration / "plan.json"
    plan_path.write_text("{}\n", encoding="utf-8")
    transaction_path = migration / "transaction.json"
    transaction = {
        "schema_version": "1.0",
        "transaction_id": "a" * 32,
        "state": "exchanged-unverified",
        "plan_path": str(plan_path.resolve()),
        "allowed_root": str(tmp_path.resolve()),
        "plan_digest": "sha256:" + "a" * 64,
        "current_path": str(current.resolve()),
        "staged_path": str(staged.resolve()),
        "previous_path": str((migration / "previous-sources").resolve()),
        "input_tree_digest": input_digest,
        "output_tree_digest": output_digest,
        "previous_tree_digest": None,
        "task_mapping_digest": "sha256:" + "b" * 64,
        "task_count": 1,
        "filesystem_device": current.stat().st_dev,
        "owner_uid": os.getuid(),
        "owner_gid": os.getgid(),
        "retention_status": "not-started",
        "last_error": None,
    }
    transaction_path.write_text(json.dumps(transaction), encoding="utf-8")
    recovered = module.recover(transaction_path)
    assert recovered["state"] == "rolled-back"
    assert module.digest_tree(current) == input_digest
    assert not staged.exists()
    assert module.recover(transaction_path)["state"] == "rolled-back"


def _retention_transaction(tmp_path: Path, state: str) -> tuple[object, Path, Path, Path, Path]:
    module = _migration_module()
    catalog = tmp_path / "catalog"
    current = catalog / "sources"
    current.mkdir(parents=True)
    (current / "output").write_text("new", encoding="utf-8")
    input_tree = tmp_path / "input-tree"
    input_tree.mkdir()
    (input_tree / "input").write_text("old", encoding="utf-8")
    input_digest = module.digest_tree(input_tree)
    output_digest = module.digest_tree(current)
    migration = tmp_path / "migration"
    migration.mkdir()
    staged = catalog / ".sources.unified-test"
    previous = migration / "previous-sources"
    target = previous if state == "old-tree-retained" else staged
    shutil.copytree(input_tree, target)
    shutil.rmtree(input_tree)
    plan_path = migration / "plan.json"
    plan_path.write_text("{}\n", encoding="utf-8")
    transaction_path = migration / "transaction.json"
    transaction_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "transaction_id": "c" * 32,
                "state": state,
                "plan_path": str(plan_path.resolve()),
                "allowed_root": str(tmp_path.resolve()),
                "plan_digest": "sha256:" + "a" * 64,
                "current_path": str(current.resolve()),
                "staged_path": str(staged.resolve()),
                "previous_path": str(previous.resolve()),
                "input_tree_digest": input_digest,
                "output_tree_digest": output_digest,
                "previous_tree_digest": input_digest if previous.exists() else None,
                "task_mapping_digest": "sha256:" + "b" * 64,
                "task_count": 1,
                "filesystem_device": current.stat().st_dev,
                "owner_uid": os.getuid(),
                "owner_gid": os.getgid(),
                "retention_status": "retained" if previous.exists() else "moving",
                "last_error": None,
            }
        ),
        encoding="utf-8",
    )
    return module, transaction_path, current, staged, previous


@pytest.mark.parametrize("state", ["verified", "old-tree-retained"])
def test_migration_recovery_completes_retention_crash_windows(tmp_path: Path, state: str) -> None:
    module, transaction_path, current, staged, previous = _retention_transaction(tmp_path, state)
    recovered = module.recover(transaction_path)
    assert recovered["state"] == "complete"
    assert module.digest_tree(current) == recovered["output_tree_digest"]
    assert module.digest_tree(previous) == recovered["input_tree_digest"]
    assert not staged.exists()


def test_migration_recovery_records_rollback_exchange_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, transaction_path, current, staged, previous = _retention_transaction(
        tmp_path, "verified"
    )
    transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
    transaction["state"] = "exchange-intent"
    transaction_path.write_text(json.dumps(transaction), encoding="utf-8")

    def fail_exchange(_current: Path, _staged: Path) -> None:
        raise OSError("injected rollback exchange failure")

    monkeypatch.setattr(module, "_exchange", fail_exchange)
    with pytest.raises(module.MigrationError, match="injected rollback exchange failure"):
        module.recover(transaction_path)
    record = json.loads(transaction_path.read_text(encoding="utf-8"))
    assert record["state"] == "recovery-required"
    assert record["last_error"]["code"] == "rollback-failed"
    assert module.digest_tree(current) == record["output_tree_digest"]
    assert module.digest_tree(staged) == record["input_tree_digest"]
    assert not previous.exists()


def test_migration_recovery_records_rollback_fsync_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, transaction_path, current, staged, previous = _retention_transaction(
        tmp_path, "verified"
    )
    transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
    transaction["state"] = "exchange-intent"
    transaction_path.write_text(json.dumps(transaction), encoding="utf-8")

    def fail_fsync(_path: Path) -> None:
        raise OSError("injected rollback fsync failure")

    monkeypatch.setattr(module, "_fsync_directory", fail_fsync)
    with pytest.raises(module.MigrationError, match="injected rollback fsync failure"):
        module.recover(transaction_path)
    record = json.loads(transaction_path.read_text(encoding="utf-8"))
    assert record["state"] == "recovery-required"
    assert record["last_error"]["code"] == "rollback-failed"
    assert module.digest_tree(current) == record["input_tree_digest"]
    assert module.digest_tree(staged) == record["output_tree_digest"]
    assert not previous.exists()


def test_migration_recovery_rejects_current_tree_outside_allowed_root(tmp_path: Path) -> None:
    module, transaction_path, current, staged, previous = _retention_transaction(
        tmp_path, "verified"
    )
    del current, staged, previous
    transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
    external = tmp_path.parent / "external-current"
    transaction["current_path"] = str(external.resolve())
    transaction_path.write_text(json.dumps(transaction), encoding="utf-8")

    with pytest.raises(module.MigrationError, match="allowed root"):
        module.recover(transaction_path)


def test_migration_retention_fsync_failure_preserves_both_trees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, transaction_path, current, staged, previous = _retention_transaction(
        tmp_path, "verified"
    )

    def fail_fsync(_path: Path) -> None:
        raise OSError("injected retention fsync failure")

    monkeypatch.setattr(module, "_fsync_directory", fail_fsync)
    with pytest.raises(module.MigrationError, match="retention move"):
        module.recover(transaction_path)
    record = json.loads(transaction_path.read_text(encoding="utf-8"))
    assert record["state"] == "recovery-required"
    assert module.digest_tree(current) == record["output_tree_digest"]
    assert module.digest_tree(previous) == record["input_tree_digest"]
    assert not staged.exists()
