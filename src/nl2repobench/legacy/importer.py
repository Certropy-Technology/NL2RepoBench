"""Import the historical ``test_files/<task>`` layout into canonical manifests.

The importer is intentionally conservative: it preserves bytes and records
what is unknown instead of inferring upstream provenance, licenses, images, or
dependency locks from a README. Private command and protected-path JSON files
are stored as private artifact references, never embedded in public manifests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import polars as pl

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.models import (
    ArtifactRef,
    DatasetManifest,
    DependencyBundle,
    Difficulty,
    EnvironmentLock,
    LegacyProjection,
    MetadataGapReport,
    MetadataGapTask,
    MetricContract,
    ProvenanceStatus,
    SourceLock,
    TaskLifecycleRecord,
    TaskManifest,
    TaskMetadata,
    TaskRef,
    TaskStatus,
    TestManifest,
    Visibility,
)
from nl2repobench.storage.artifacts import FileArtifactStore
from nl2repobench.storage.files import (
    UnsafePathError,
    assert_manifest_writable,
    atomic_write,
    safe_child_directory,
)
from nl2repobench.storage.state import StateStore


class LegacyImportError(ValueError):
    """Raised when a legacy task cannot be imported safely."""


@dataclass(frozen=True)
class ImportSummary:
    """Machine-friendly result returned by the importer and CLI."""

    dataset_manifest: Path
    gap_report: Path
    imported_tasks: int
    manifest_digests: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset_manifest": str(self.dataset_manifest),
            "gap_report": str(self.gap_report),
            "imported_tasks": self.imported_tasks,
            "manifest_digests": list(self.manifest_digests),
        }


class LegacyImporter:
    """Convert legacy task directories into immutable canonical records."""

    def __init__(
        self,
        legacy_root: Path,
        output_root: Path,
        artifact_store: FileArtifactStore,
        *,
        difficulty_file: Path | None = None,
        state_store: StateStore | None = None,
    ) -> None:
        self.legacy_root = legacy_root
        self.output_root = output_root
        self.artifact_store = artifact_store
        self.difficulty_file = difficulty_file
        self.state_store = state_store
        self._difficulty = self._load_difficulty()

    def _load_difficulty(self) -> dict[str, str]:
        if self.difficulty_file is None or not self.difficulty_file.is_file():
            return {}
        frame = pl.read_csv(self.difficulty_file)
        required = {"task-name", "Level"}
        if not required.issubset(frame.columns):
            raise LegacyImportError(
                f"difficulty file must contain {sorted(required)}, got {frame.columns}"
            )
        return {
            str(row["task-name"]).casefold(): str(row["Level"]).lower()
            for row in frame.to_dicts()
            if row.get("task-name") is not None and row.get("Level") is not None
        }

    @staticmethod
    def _read_json_list(path: Path, *, field: str) -> list[Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LegacyImportError(f"cannot read {field}: {path}: {exc}") from exc
        if not isinstance(value, list):
            raise LegacyImportError(f"{field} must be a JSON list: {path}")
        return value

    def _put(self, path: Path, *, media_type: str, visibility: Visibility) -> ArtifactRef:
        try:
            return self.artifact_store.put_file(
                path,
                media_type=media_type,
                visibility=visibility,
            )
        except OSError as exc:
            raise LegacyImportError(f"cannot ingest artifact {path}: {exc}") from exc

    def _import_task(self, task_dir: Path) -> tuple[TaskManifest, MetadataGapTask]:
        task_id = task_dir.name
        resolved_root = self.legacy_root.resolve()
        resolved_task = task_dir.resolve()
        if not resolved_task.is_relative_to(resolved_root):
            raise LegacyImportError(f"task directory escapes legacy root: {task_dir}")
        required = {
            "start.md": task_dir / "start.md",
            "test_case_count.txt": task_dir / "test_case_count.txt",
            "test_commands.json": task_dir / "test_commands.json",
            "test_files.json": task_dir / "test_files.json",
        }
        missing_files = [name for name, path in required.items() if not path.is_file()]
        if missing_files:
            raise LegacyImportError(f"{task_id} is missing: {', '.join(missing_files)}")
        escaped_files = [
            name
            for name, path in required.items()
            if not path.resolve().is_relative_to(resolved_task)
        ]
        if escaped_files:
            raise LegacyImportError(
                f"{task_id} contains files outside its task root: {', '.join(escaped_files)}"
            )

        try:
            expected_total = int(
                required["test_case_count.txt"].read_text(encoding="utf-8").strip()
            )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise LegacyImportError(f"invalid test count for {task_id}") from exc
        if expected_total <= 0:
            raise LegacyImportError(f"test count must be positive for {task_id}")

        commands = self._read_json_list(required["test_commands.json"], field="test commands")
        if not all(isinstance(command, str) and command.strip() for command in commands):
            raise LegacyImportError(f"test commands must be non-empty strings for {task_id}")
        protected_paths = self._read_json_list(
            required["test_files.json"], field="protected test paths"
        )
        if not all(isinstance(path, str) and path.strip() for path in protected_paths):
            raise LegacyImportError(f"protected paths must be non-empty strings for {task_id}")

        instruction_ref = self._put(
            required["start.md"],
            media_type="text/markdown; charset=utf-8",
            visibility=Visibility.PUBLIC,
        )
        commands_ref = self._put(
            required["test_commands.json"],
            media_type="application/json",
            visibility=Visibility.PRIVATE,
        )
        protected_ref = self._put(
            required["test_files.json"],
            media_type="application/json",
            visibility=Visibility.PRIVATE,
        )

        raw_difficulty = self._difficulty.get(task_id.casefold(), "unknown")
        if raw_difficulty not in {"easy", "medium", "hard", "unknown"}:
            raw_difficulty = "unknown"
        difficulty = cast(Difficulty, raw_difficulty)

        manifest = TaskManifest(
            task_id=task_id,
            metadata=TaskMetadata(difficulty=difficulty),
            instruction=instruction_ref,
            source_lock=SourceLock(status=ProvenanceStatus.UNKNOWN),
            environment_lock=EnvironmentLock(status=ProvenanceStatus.UNKNOWN),
            dependency_bundle=DependencyBundle(status=ProvenanceStatus.UNKNOWN),
            tests=TestManifest(
                expected_total=expected_total,
                expected_total_source="legacy-file",
                commands_artifact=commands_ref,
                protected_paths_artifact=protected_ref,
            ),
            metric=MetricContract(),
            lifecycle=TaskLifecycleRecord(status=TaskStatus.DISCOVERED),
            legacy_projection=LegacyProjection(
                source_root=task_id,
                instruction_path=f"{task_id}/start.md",
                count_path=f"{task_id}/test_case_count.txt",
                commands_path=f"{task_id}/test_commands.json",
                protected_paths_path=f"{task_id}/test_files.json",
            ),
        )

        missing = [
            "source_lock.upstream_url",
            "source_lock.revision",
            "source_lock.license_spdx",
            "environment_lock.python_version",
            "environment_lock.base_image_digest",
            "dependency_bundle.artifact",
            "tests.test_bundle",
            "tests.expected_total_source=frozen-collection",
        ]
        if difficulty == "unknown":
            missing.append("metadata.difficulty")
        warnings = (
            "legacy commands and protected paths remain private artifact refs",
            "difficulty is imported from task_difficulty.csv when available",
        )
        return manifest, MetadataGapTask(
            task_id=task_id,
            missing_fields=tuple(missing),
            warnings=warnings,
        )

    def run(
        self,
        *,
        dataset_id: str = "nl2repobench-legacy",
        dataset_version: str = "0.1.0",
        gap_report_path: Path | None = None,
    ) -> ImportSummary:
        if not self.legacy_root.is_dir():
            raise LegacyImportError(f"legacy root does not exist: {self.legacy_root}")
        self.output_root.mkdir(parents=True, exist_ok=True)
        gaps: list[MetadataGapTask] = []
        task_refs: list[TaskRef] = []
        digests: list[str] = []

        task_dirs = sorted(path for path in self.legacy_root.iterdir() if path.is_dir())
        for task_dir in task_dirs:
            manifest, gap = self._import_task(task_dir)
            try:
                task_output = safe_child_directory(self.output_root, task_dir.name)
            except UnsafePathError as exc:
                raise LegacyImportError(str(exc)) from exc
            manifest_bytes = canonical_json(manifest)
            manifest_path = task_output / "manifest.json"
            try:
                assert_manifest_writable(manifest_path, manifest)
            except UnsafePathError as exc:
                raise LegacyImportError(str(exc)) from exc
            if self.state_store is not None:
                self.state_store.assert_task_writable(manifest)
            manifest_ref = self.artifact_store.put_bytes(
                manifest_bytes,
                media_type="application/json",
                visibility=Visibility.PUBLIC,
            )
            if self.state_store is not None:
                self.state_store.upsert_task(manifest)
            atomic_write(manifest_path, manifest_bytes + b"\n")
            task_refs.append(
                TaskRef(
                    task_id=manifest.task_id,
                    version=manifest.version,
                    manifest_digest=manifest_ref.digest,
                    manifest_uri=manifest_ref.uri,
                )
            )
            digests.append(manifest_ref.digest)
            gaps.append(gap)

        dataset = DatasetManifest(
            dataset_id=dataset_id,
            version=dataset_version,
            description="Canonical import of the historical NL2RepoBench task layout.",
            tasks=tuple(task_refs),
            source_format="legacy-import",
        )
        dataset_path = self.output_root / "dataset.manifest.json"
        atomic_write(dataset_path, canonical_json(dataset) + b"\n")

        gap_counts = self._aggregate_gap_counts(gaps)
        report = MetadataGapReport(
            dataset_id=dataset_id,
            task_count=len(gaps),
            complete_task_count=sum(not gap.missing_fields for gap in gaps),
            gap_counts=gap_counts,
            tasks=tuple(gaps),
        )
        report_path = gap_report_path or (self.output_root / "metadata-gap-report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(report_path, canonical_json(report) + b"\n")
        return ImportSummary(
            dataset_manifest=dataset_path,
            gap_report=report_path,
            imported_tasks=len(gaps),
            manifest_digests=tuple(digests),
        )

    @staticmethod
    def _aggregate_gap_counts(gaps: list[MetadataGapTask]) -> dict[str, int]:
        if not gaps:
            return {}
        frame = pl.DataFrame(
            {
                "task_id": [gap.task_id for gap in gaps],
                "missing_fields": [list(gap.missing_fields) for gap in gaps],
            }
        )
        counts = (
            frame.explode("missing_fields", empty_as_null=True)
            .filter(pl.col("missing_fields").is_not_null())
            .group_by("missing_fields")
            .len()
            .sort("missing_fields")
        )
        return {str(row["missing_fields"]): int(row["len"]) for row in counts.to_dicts()}
