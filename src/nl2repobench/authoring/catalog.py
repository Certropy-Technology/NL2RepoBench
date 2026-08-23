"""Compile human-friendly TOML/Markdown sources into canonical JSON.

Humans edit catalog sources. Machines consume canonical manifests. Keeping the
two representations separate gives reviewers readable diffs while preserving
deterministic hashes and strict validation at execution boundaries.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, cast

from pydantic import Field, model_validator

from nl2repobench.domain.canonical import canonical_file_payload, canonical_json
from nl2repobench.domain.models import (
    ArtifactRef,
    DatasetManifest,
    DependencyBundle,
    EnvironmentLock,
    HarborExecutionProfile,
    MetricContract,
    RecordModel,
    SourceLock,
    TaskLifecycleRecord,
    TaskManifest,
    TaskMetadata,
    TaskRef,
    TaskVerifierSpec,
    TestManifest,
    Visibility,
)
from nl2repobench.domain.runtime import RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.storage.artifacts import FileArtifactStore
from nl2repobench.storage.files import (
    UnsafePathError,
    assert_manifest_writable,
    atomic_write,
    safe_child_directory,
)
from nl2repobench.storage.state import StateStore

if TYPE_CHECKING:
    from nl2repobench.domain.models_v2 import (
        DeclarativeTaskSourceV2,
        TaskManifestV2,
        TaskRefV2,
    )


class CatalogError(ValueError):
    """Raised when a declarative source is unsafe or cannot be compiled."""


def _validate_relative_path(value: str, field_name: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value in {"", "."}:
        raise ValueError(f"{field_name} must be a non-empty relative path without '..'")
    return value


class DeclarativeTaskSource(RecordModel):
    """Human-maintained task definition loaded from ``task.toml``."""

    task_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    version: str = "1.0.0"
    instruction: str = "instruction.md"
    metadata: TaskMetadata = Field(default_factory=TaskMetadata)
    source: SourceLock = Field(default_factory=SourceLock)
    environment: EnvironmentLock = Field(default_factory=EnvironmentLock)
    dependencies: DependencyBundle = Field(default_factory=DependencyBundle)
    tests: TestManifest
    metric: MetricContract = Field(default_factory=MetricContract)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None
    verifier: TaskVerifierSpec | None = None

    @model_validator(mode="after")
    def validate_paths(self) -> DeclarativeTaskSource:
        _validate_relative_path(self.instruction, "instruction")
        return self


class DeclarativeDatasetSource(RecordModel):
    """Human-maintained dataset definition loaded from ``dataset.toml``."""

    dataset_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    version: str = "0.1.0"
    description: str
    metric_contract: str = "fixed-test-pass-rate-v1"
    tasks: tuple[str, ...]

    @model_validator(mode="after")
    def validate_task_paths(self) -> DeclarativeDatasetSource:
        if not self.tasks:
            raise ValueError("a dataset must contain at least one task source")
        for task_id in self.tasks:
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id):
                raise ValueError(f"invalid task id in dataset: {task_id}")
        if len(set(self.tasks)) != len(self.tasks):
            raise ValueError("dataset task IDs must be unique")
        return self


@dataclass(frozen=True)
class CompiledTask:
    manifest: TaskManifest
    path: Path
    reference: TaskRef


@dataclass(frozen=True)
class CompiledTaskV2:
    manifest: TaskManifestV2
    path: Path
    reference: TaskRefV2


class CatalogCompiler:
    """Validate and deterministically compile declarative catalog sources."""

    def __init__(
        self,
        artifact_store: FileArtifactStore,
        *,
        state_store: StateStore | None = None,
    ) -> None:
        self.artifact_store = artifact_store
        self.state_store = state_store

    @staticmethod
    def load_task(source_dir: Path) -> DeclarativeTaskSource | DeclarativeTaskSourceV2:
        resolved_source = source_dir.resolve()
        path = source_dir / "task.toml"
        if path.is_symlink():
            raise CatalogError(f"task.toml must not be a symlink: {path}")
        if not path.resolve().is_relative_to(resolved_source):
            raise CatalogError(f"task.toml escapes task source directory: {path}")
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            schema_version = data.get("schema_version", "1.0")
            source: DeclarativeTaskSource | DeclarativeTaskSourceV2
            if schema_version == "2.0":
                from nl2repobench.domain.models_v2 import DeclarativeTaskSourceV2

                source = DeclarativeTaskSourceV2.model_validate(data)
            elif schema_version == "1.0":
                source = DeclarativeTaskSource.model_validate(data)
            else:
                raise ValueError(f"unsupported task source schema version: {schema_version}")
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
            raise CatalogError(f"invalid task source {path}: {exc}") from exc
        instruction = source_dir / source.instruction
        if not instruction.is_file():
            raise CatalogError(f"instruction does not exist: {instruction}")
        if not instruction.resolve().is_relative_to(resolved_source):
            raise CatalogError(f"instruction escapes task source directory: {instruction}")
        return source

    @staticmethod
    def load_dataset(path: Path) -> DeclarativeDatasetSource:
        if path.is_symlink():
            raise CatalogError(f"dataset.toml must not be a symlink: {path}")
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            return DeclarativeDatasetSource.model_validate(data)
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
            raise CatalogError(f"invalid dataset source {path}: {exc}") from exc

    def compile_task(self, source_dir: Path, output_root: Path) -> CompiledTask | CompiledTaskV2:
        source = self.load_task(source_dir)
        runtime = RuntimeDiscriminator.from_catalog_source(source.model_dump(mode="python"))
        if runtime.language is RuntimeLanguage.NODE:
            from nl2repobench.domain.models_v2 import DeclarativeTaskSourceV2

            if not isinstance(source, DeclarativeTaskSourceV2):
                raise CatalogError("Node runtime requires the unified Node task source")
            return self._compile_task_v2(source_dir, source, output_root)
        python_source = cast(DeclarativeTaskSource, source)
        instruction_path = source_dir / python_source.instruction
        instruction_ref = self.artifact_store.put_file(
            instruction_path,
            media_type="text/markdown; charset=utf-8",
            visibility=Visibility.PUBLIC,
        )
        manifest = TaskManifest(
            task_id=python_source.task_id,
            version=python_source.version,
            metadata=python_source.metadata,
            instruction=instruction_ref,
            source_lock=python_source.source,
            environment_lock=python_source.environment,
            dependency_bundle=python_source.dependencies,
            tests=python_source.tests,
            metric=python_source.metric,
            lifecycle=python_source.lifecycle,
            harbor=python_source.harbor,
            oracle_bundle=python_source.oracle_bundle,
            verifier=python_source.verifier,
        )
        payload = canonical_json(manifest)
        output_dir = safe_child_directory(output_root, source.task_id)
        if self.state_store is not None:
            self.state_store.assert_task_writable(manifest)
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "manifest.json"
        assert_manifest_writable(manifest_path, manifest)
        manifest_ref = self.artifact_store.put_bytes(
            payload,
            media_type="application/json",
            visibility=Visibility.PUBLIC,
        )
        if self.state_store is not None:
            self.state_store.upsert_task(manifest)
        atomic_write(manifest_path, payload + b"\n")
        reference = TaskRef(
            task_id=manifest.task_id,
            version=manifest.version,
            manifest_digest=manifest_ref.digest,
            manifest_uri=manifest_ref.uri,
        )
        return CompiledTask(manifest=manifest, path=manifest_path, reference=reference)

    def _compile_task_v2(
        self,
        source_dir: Path,
        source: DeclarativeTaskSourceV2,
        output_root: Path,
    ) -> CompiledTaskV2:
        """Compile a Node source without sending it through v1 state/index code."""

        from nl2repobench.domain.models_v2 import (
            TaskManifestV2,
            TaskRefV2,
        )

        instruction_path = source_dir / source.instruction
        instruction_ref = self.artifact_store.put_file(
            instruction_path,
            media_type="text/markdown; charset=utf-8",
            visibility=Visibility.PUBLIC,
        )
        manifest = TaskManifestV2(
            task_id=source.task_id,
            version=source.version,
            metadata=source.metadata,
            instruction=instruction_ref,
            source_lock=source.source,
            environment_lock=source.environment,
            dependency_bundle=source.dependencies,
            tests=source.tests,
            metric=source.metric,
            lifecycle=source.lifecycle,
            harbor=source.harbor,
            oracle_bundle=source.oracle_bundle,
        )
        payload = canonical_json(manifest)
        output_dir = safe_child_directory(output_root, source.task_id)
        manifest_path = output_dir / "manifest.json"
        if manifest_path.exists() or manifest_path.is_symlink():
            if manifest_path.is_symlink():
                raise UnsafePathError(f"generated manifest must not be a symlink: {manifest_path}")
            try:
                existing = TaskManifestV2.model_validate_json(
                    canonical_file_payload(manifest_path.read_bytes())
                )
            except (OSError, ValueError) as exc:
                raise UnsafePathError(
                    f"existing generated manifest is invalid: {manifest_path}"
                ) from exc
            if (
                existing.lifecycle.status.value == "published"
                and existing.content_digest() != manifest.content_digest()
            ):
                raise UnsafePathError(
                    "published filesystem manifest is immutable: "
                    f"{manifest.task_id}@{manifest.version}"
                )
        manifest_ref = self.artifact_store.put_bytes(
            payload,
            media_type="application/json",
            visibility=Visibility.PUBLIC,
        )
        atomic_write(manifest_path, payload + b"\n")
        reference = TaskRefV2(
            task_id=manifest.task_id,
            version=manifest.version,
            manifest_digest=manifest_ref.digest,
            manifest_uri=manifest_ref.uri,
        )
        return CompiledTaskV2(manifest=manifest, path=manifest_path, reference=reference)

    def compile_dataset(self, source_path: Path, output_root: Path) -> DatasetManifest:
        source = self.load_dataset(source_path)
        catalog_root = next(
            (parent for parent in source_path.parents if (parent / "tasks").is_dir()),
            None,
        )
        if catalog_root is None:
            raise CatalogError(f"cannot find catalog/tasks above {source_path}")
        task_dirs: list[Path] = []
        seen_ids: set[str] = set()
        for task_id in source.tasks:
            tasks_root = (catalog_root / "tasks").resolve()
            task_dir = (tasks_root / task_id).resolve()
            if not task_dir.is_relative_to(tasks_root):
                raise CatalogError(f"task source escapes catalog root: {task_id}")
            task_source = self.load_task(task_dir)
            if task_source.schema_version == "2.0":
                raise CatalogError(
                    "v2 Node tasks require the separate nl2repobench-node-pilot-v1 dataset"
                )
            if task_source.task_id != task_id:
                raise CatalogError(
                    f"dataset task ID {task_id} does not match source {task_source.task_id}"
                )
            if task_source.metric.contract_id != source.metric_contract:
                raise CatalogError(
                    f"metric contract mismatch for {task_id}: "
                    f"{task_source.metric.contract_id} != {source.metric_contract}"
                )
            if task_source.task_id in seen_ids:
                raise CatalogError(f"duplicate task_id in dataset: {task_source.task_id}")
            seen_ids.add(task_source.task_id)
            task_dirs.append(task_dir)

        compiled = [self.compile_task(task_dir, output_root) for task_dir in task_dirs]
        dataset = DatasetManifest(
            dataset_id=source.dataset_id,
            version=source.version,
            description=source.description,
            metric_contract=source.metric_contract,
            tasks=tuple(cast(TaskRef, task.reference) for task in compiled),
            source_format="declarative-catalog",
        )
        output_root.mkdir(parents=True, exist_ok=True)
        atomic_write(output_root / "dataset.manifest.json", canonical_json(dataset) + b"\n")
        return dataset


def validate_compiled_dataset(root: Path) -> list[str]:
    """Validate a compiled dataset index and every referenced task digest."""

    errors: list[str] = []
    resolved_root = root.resolve()
    dataset_path = root / "dataset.manifest.json"
    if not dataset_path.resolve().is_relative_to(resolved_root):
        return [f"{dataset_path}: escapes compiled dataset root"]
    try:
        dataset_raw = canonical_file_payload(dataset_path.read_bytes())
        dataset = DatasetManifest.model_validate_json(dataset_raw)
        if dataset_raw != canonical_json(dataset):
            errors.append(f"{dataset_path}: non-canonical JSON")
    except (OSError, ValueError) as exc:
        return [f"{dataset_path}: {exc}"]

    manifests: dict[str, tuple[Path, TaskManifest]] = {}
    for path in sorted(root.glob("*/manifest.json")):
        try:
            if not path.resolve().is_relative_to(resolved_root):
                errors.append(f"{path}: escapes compiled dataset root")
                continue
            raw = canonical_file_payload(path.read_bytes())
            task = TaskManifest.model_validate_json(raw)
            if raw != canonical_json(task):
                errors.append(f"{path}: non-canonical JSON")
            if task.task_id in manifests:
                errors.append(f"{path}: duplicate task_id {task.task_id}")
            manifests[task.task_id] = (path, task)
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: {exc}")

    referenced_ids: set[str] = set()
    for reference in dataset.tasks:
        referenced_ids.add(reference.task_id)
        entry = manifests.get(reference.task_id)
        if entry is None:
            errors.append(f"dataset references missing task: {reference.task_id}")
            continue
        path, task = entry
        if task.version != reference.version:
            errors.append(
                f"{path}: version {task.version} != dataset reference {reference.version}"
            )
        digest = task.content_digest()
        if digest != reference.manifest_digest:
            errors.append(
                f"{path}: digest {digest} != dataset reference {reference.manifest_digest}"
            )
        expected_uri = f"artifact://public/{reference.manifest_digest}"
        if reference.manifest_uri != expected_uri:
            errors.append(f"{path}: manifest_uri {reference.manifest_uri} != {expected_uri}")
        if task.metric.contract_id != dataset.metric_contract:
            errors.append(
                f"{path}: metric {task.metric.contract_id} != dataset {dataset.metric_contract}"
            )

    for task_id in sorted(set(manifests) - referenced_ids):
        errors.append(f"compiled task is not referenced by dataset: {task_id}")
    return errors


def scaffold_task(root: Path, task_id: str) -> Path:
    """Create a minimal reviewable task source without inventing provenance."""

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id):
        raise CatalogError("task_id must contain only letters, numbers, '.', '_' or '-'")
    target = root / task_id
    target.mkdir(parents=True, exist_ok=False)
    (target / "instruction.md").write_text(
        f"# Build `{task_id}`\n\nDescribe the complete public behavior here.\n",
        encoding="utf-8",
    )
    (target / "task.toml").write_text(
        f'''schema_version = "1.0"
task_id = "{task_id}"
version = "1.0.0"
instruction = "instruction.md"

[metadata]
difficulty = "unknown"
category = "unknown"
tags = []
language = "python"

[source]
status = "unknown"

[environment]
status = "unknown"

[dependencies]
status = "unknown"
installer = "uv"

[tests]
framework = "pytest"
expected_total = 1
expected_total_source = "unknown"
commands = ["uv run pytest -q"]

[metric]
contract_id = "fixed-test-pass-rate-v1"
collection_mismatch = "fail"

[lifecycle]
status = "discovered"
''',
        encoding="utf-8",
    )
    return target
