from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
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

from nl2repobench.domain.canonical_contract import (
    DependencyBundle,
    EnvironmentLock,
    PackageManager,
    TaskManifest,
    TaskMetadata,
    TaskSource,
)
from nl2repobench.domain.canonical_contract import (
    TestManifest as CanonicalTestManifest,
)
from nl2repobench.domain.canonical_models import ArtifactRef, Visibility
from nl2repobench.harbor.bundle_io import BundleLimits
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
