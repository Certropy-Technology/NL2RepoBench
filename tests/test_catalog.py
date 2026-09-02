from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.authoring.catalog import (
    CatalogCompiler,
    CatalogError,
    scaffold_task,
    validate_compiled_dataset,
)
from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.canonical_contract import TaskManifest
from nl2repobench.storage.artifacts import FileArtifactStore
from nl2repobench.storage.files import UnsafePathError
from nl2repobench.storage.state import StateStore

ROOT = Path(__file__).parents[1]


def _artifact(character: str, visibility: str = "private") -> dict[str, object]:
    return {
        "digest": "sha256:" + character * 64,
        "size_bytes": 1,
        "uri": f"artifact://{visibility}/sha256:{character * 64}",
        "visibility": visibility,
    }


def _published_manifest(task_id: str) -> TaskManifest:
    return TaskManifest.model_validate(
        {
            "task_id": task_id,
            "metadata": {"difficulty": "easy", "category": "example", "language": "python"},
            "instruction": _artifact("1", "public"),
            "source_lock": {
                "status": "known",
                "upstream_url": "https://example.invalid/repo",
                "revision": "2" * 40,
                "license_spdx": "MIT",
                "source_digest": "sha256:" + "3" * 64,
            },
            "environment_lock": {
                "status": "known",
                "os_name": "linux",
                "base_image": "example",
                "base_image_digest": "sha256:" + "4" * 64,
                "runtime": {
                    "language": "python",
                    "runtime": "cpython",
                    "version": "3.12",
                    "package_manager": "uv",
                    "package_manager_version": "0.8.15",
                },
                "network_policy": {
                    "mode": "no-network",
                    "offline_dependencies": "preinstalled-image",
                    "reference_source_fetch": "forbidden",
                    "reason": "Dependencies are installed during the Docker build phase.",
                },
            },
            "dependency_bundle": {
                "status": "known",
                "package_manager": "uv",
                "lock": _artifact("5"),
                "offline_store": _artifact("a"),
                "inventory": _artifact("b"),
            },
            "tests": {
                "framework": "pytest",
                "report_format": "pytest-junit-xml-v1",
                "expected_total": 1,
                "expected_total_source": "frozen-collection",
                "commands_artifact": _artifact("6"),
                "test_bundle": _artifact("7"),
            },
            "harbor": {
                "description": "Published task",
                "keywords": ["python", "pytest", "nl2repobench"],
            },
            "oracle_bundle": _artifact("9"),
            "lifecycle": {
                "status": "published",
                "owner": "reviewer",
                "evidence": [_artifact("8", "public")],
                "approval_refs": ["review:1"],
            },
        }
    )


def test_repository_example_remains_pending_live_migration() -> None:
    source = CatalogCompiler.load_task(ROOT / "catalog/sources/ministats")
    assert source.task_id == "ministats"


def test_task_compiler_is_deterministic(tmp_path) -> None:
    source_dir = scaffold_task(tmp_path / "sources", "demo")
    first_output = tmp_path / "first"
    second_output = tmp_path / "second"
    first_store = FileArtifactStore(tmp_path / "artifacts")
    second_store = FileArtifactStore(tmp_path / "artifacts")

    first = CatalogCompiler(first_store).compile_task(source_dir, first_output)
    second = CatalogCompiler(second_store).compile_task(source_dir, second_output)

    assert first.reference.manifest_digest == second.reference.manifest_digest
    assert (first_output / "demo/manifest.json").read_bytes() == (
        second_output / "demo/manifest.json"
    ).read_bytes()


def test_dataset_compiler_resolves_task_ids_from_catalog_root(tmp_path) -> None:
    catalog = tmp_path / "catalog"
    dataset_dir = catalog / "datasets/example"
    dataset_dir.mkdir(parents=True)
    scaffold_task(catalog / "sources", "demo")
    (dataset_dir / "dataset.toml").write_text(
        """schema_version = "1.0"
dataset_id = "example"
version = "0.1.0"
description = "Example dataset"
tasks = ["demo"]
""",
        encoding="utf-8",
    )

    with StateStore(tmp_path / "state.db") as state:
        dataset = CatalogCompiler(
            FileArtifactStore(tmp_path / "artifacts"), state_store=state
        ).compile_dataset(dataset_dir / "dataset.toml", tmp_path / "build")

    assert dataset.dataset_id == "example"
    assert len(dataset.tasks) == 1
    assert (tmp_path / "build/dataset.manifest.json").is_file()
    assert validate_compiled_dataset(tmp_path / "build") == []

    second = CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_dataset(
        dataset_dir / "dataset.toml", tmp_path / "other-build"
    )
    assert dataset.content_digest() == second.content_digest()
    assert (tmp_path / "build/dataset.manifest.json").read_bytes() == (
        tmp_path / "other-build/dataset.manifest.json"
    ).read_bytes()


def test_dataset_validation_detects_task_digest_drift(tmp_path) -> None:
    catalog = tmp_path / "catalog"
    scaffold_task(catalog / "sources", "demo")
    dataset_dir = catalog / "datasets/example"
    dataset_dir.mkdir(parents=True)
    dataset_path = dataset_dir / "dataset.toml"
    dataset_path.write_text(
        """dataset_id = "example"
description = "Digest validation"
tasks = ["demo"]
""",
        encoding="utf-8",
    )
    output = tmp_path / "build"
    CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_dataset(dataset_path, output)
    task_path = output / "demo/manifest.json"
    task = TaskManifest.model_validate_json(task_path.read_bytes())
    changed = task.model_copy(
        update={"metadata": task.metadata.model_copy(update={"category": "changed"})}
    )
    task_path.write_bytes(canonical_json(changed) + b"\n")

    errors = validate_compiled_dataset(output)
    assert any("digest" in error for error in errors)


def test_dataset_validation_rejects_trailing_whitespace(tmp_path) -> None:
    catalog = tmp_path / "catalog"
    scaffold_task(catalog / "sources", "demo")
    dataset_dir = catalog / "datasets/example"
    dataset_dir.mkdir(parents=True)
    dataset_path = dataset_dir / "dataset.toml"
    dataset_path.write_text(
        """dataset_id = "example"
description = "Canonical bytes"
tasks = ["demo"]
""",
        encoding="utf-8",
    )
    output = tmp_path / "build"
    CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_dataset(dataset_path, output)
    manifest_path = output / "dataset.manifest.json"
    manifest_path.write_bytes(manifest_path.read_bytes()[:-1] + b" \n")

    assert any("non-canonical JSON" in error for error in validate_compiled_dataset(output))


def test_dataset_validation_rejects_symlinked_task_directory(tmp_path) -> None:
    catalog = tmp_path / "catalog"
    scaffold_task(catalog / "sources", "demo")
    dataset_dir = catalog / "datasets/example"
    dataset_dir.mkdir(parents=True)
    dataset_path = dataset_dir / "dataset.toml"
    dataset_path.write_text(
        """dataset_id = "example"
description = "Symlink validation"
tasks = ["demo"]
""",
        encoding="utf-8",
    )
    output = tmp_path / "build"
    CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_dataset(dataset_path, output)
    outside = tmp_path / "outside-task"
    (output / "demo").rename(outside)
    (output / "demo").symlink_to(outside, target_is_directory=True)

    assert any(
        "escapes compiled dataset root" in error for error in validate_compiled_dataset(output)
    )


def test_scaffold_source_is_parseable(tmp_path) -> None:
    source_dir = scaffold_task(tmp_path / "tasks", "new-task")

    parsed = CatalogCompiler.load_task(source_dir)
    assert parsed.task_id == "new-task"
    assert (source_dir / "instruction.md").is_file()


def test_dataset_rejects_metric_contract_mismatch(tmp_path) -> None:
    catalog = tmp_path / "catalog"
    scaffold_task(catalog / "sources", "demo")
    dataset_dir = catalog / "datasets/example"
    dataset_dir.mkdir(parents=True)
    dataset_path = dataset_dir / "dataset.toml"
    dataset_path.write_text(
        """dataset_id = "example"
description = "Mismatched metric"
metric_contract = "different-contract"
tasks = ["demo"]
""",
        encoding="utf-8",
    )

    with pytest.raises(CatalogError, match="fixed-test-pass-rate-v1"):
        CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_dataset(
            dataset_path, tmp_path / "build"
        )
    assert not (tmp_path / "build").exists()


def test_source_rejects_path_traversal(tmp_path) -> None:
    source_dir = scaffold_task(tmp_path / "tasks", "unsafe")
    task_toml = source_dir / "task.toml"
    task_toml.write_text(
        task_toml.read_text(encoding="utf-8").replace(
            'instruction = "instruction.md"', 'instruction = "../secret.md"'
        ),
        encoding="utf-8",
    )
    (tmp_path / "secret.md").write_text("secret", encoding="utf-8")

    with pytest.raises(CatalogError, match="safe relative path"):
        CatalogCompiler.load_task(source_dir)


def test_source_rejects_instruction_symlink_escape(tmp_path) -> None:
    source_dir = scaffold_task(tmp_path / "tasks", "symlink-task")
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    (source_dir / "instruction.md").unlink()
    (source_dir / "instruction.md").symlink_to(outside)

    with pytest.raises(CatalogError, match="escapes task source"):
        CatalogCompiler.load_task(source_dir)


def test_source_rejects_task_toml_symlink(tmp_path) -> None:
    source_dir = scaffold_task(tmp_path / "tasks", "symlink-toml")
    outside = tmp_path / "outside.toml"
    outside.write_bytes((source_dir / "task.toml").read_bytes())
    (source_dir / "task.toml").unlink()
    (source_dir / "task.toml").symlink_to(outside)

    with pytest.raises(CatalogError, match="must not be a symlink"):
        CatalogCompiler.load_task(source_dir)


def test_compiler_rejects_symlinked_output_directory(tmp_path) -> None:
    source_dir = scaffold_task(tmp_path / "tasks", "demo")
    output = tmp_path / "build"
    outside = tmp_path / "outside"
    output.mkdir()
    outside.mkdir()
    (output / "demo").symlink_to(outside, target_is_directory=True)

    with pytest.raises(UnsafePathError, match="must not be a symlink"):
        CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_task(source_dir, output)


def test_compiler_cannot_overwrite_published_filesystem_manifest(tmp_path) -> None:
    source_dir = scaffold_task(tmp_path / "tasks", "demo")
    output = tmp_path / "build"
    manifest_dir = output / "demo"
    manifest_dir.mkdir(parents=True)
    published = _published_manifest("demo")
    (manifest_dir / "manifest.json").write_bytes(canonical_json(published) + b"\n")

    with pytest.raises(UnsafePathError, match="filesystem manifest is immutable"):
        CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_task(source_dir, output)
