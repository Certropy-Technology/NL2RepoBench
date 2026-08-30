"""Archive-only records for the historical four-file importer."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from nl2repobench.domain.canonical_models import (
    ArtifactRef,
    CanonicalRecord,
    HarborExecutionProfile,
    SourceLock,
    TaskLifecycleRecord,
    TaskVerifierSpec,
)


class LegacyEnvironmentLock(CanonicalRecord):
    status: Literal["known", "unknown"] = "unknown"
    python_version: str | None = None
    runtime_version: str | None = None
    os_name: str | None = None
    base_image: str | None = None
    base_image_digest: str | None = None
    system_packages: tuple[str, ...] = ()
    build_command: str | None = None
    network_mode: Literal["public", "no-network", "allowlist"] | None = None


class LegacyDependencyBundle(CanonicalRecord):
    status: Literal["known", "unknown"] = "unknown"
    lock_artifact: ArtifactRef | None = None
    module_bundle: ArtifactRef | None = None
    artifact: ArtifactRef | None = None
    installer: Literal["uv", "pip", "system", "unknown"] = "unknown"
    packages: tuple[str, ...] = ()


class LegacyTestManifest(CanonicalRecord):
    framework: Literal["pytest"] = "pytest"
    expected_total: Annotated[int, Field(ge=0)] = 0
    expected_total_source: Literal["frozen-collection", "legacy-file", "unknown"] = "unknown"
    commands: tuple[str, ...] = ()
    commands_artifact: ArtifactRef | None = None
    protected_paths: tuple[str, ...] = ()
    protected_paths_artifact: ArtifactRef | None = None
    test_bundle: ArtifactRef | None = None


class LegacyMetricContract(CanonicalRecord):
    contract_id: str = "fixed-test-pass-rate-v1"
    passed_statuses: tuple[Literal["passed"], ...] = ("passed",)
    excluded_statuses: tuple[Literal["skipped", "xfail"], ...] = ("skipped",)
    collection_mismatch: Literal["fail", "record-only"] = "fail"
    formula: str = "clamp(passed / frozen_total, 0, 1)"


class LegacyTaskMetadata(CanonicalRecord):
    difficulty: Literal["easy", "medium", "hard", "unknown"] = "unknown"
    category: str = "unknown"
    tags: tuple[str, ...] = ()
    language: str = "python"


class LegacyProjection(CanonicalRecord):
    source_root: str
    instruction_path: str
    count_path: str
    commands_path: str
    protected_paths_path: str


class LegacyTaskManifest(CanonicalRecord):
    task_id: str
    version: str = "1.0.0"
    metadata: LegacyTaskMetadata = Field(default_factory=LegacyTaskMetadata)
    instruction: ArtifactRef
    source_lock: SourceLock = Field(default_factory=SourceLock)
    environment_lock: LegacyEnvironmentLock = Field(default_factory=LegacyEnvironmentLock)
    dependency_bundle: LegacyDependencyBundle = Field(default_factory=LegacyDependencyBundle)
    tests: LegacyTestManifest
    metric: LegacyMetricContract = Field(default_factory=LegacyMetricContract)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None
    verifier: TaskVerifierSpec | None = None
    legacy_projection: LegacyProjection | None = None


__all__ = [
    "LegacyDependencyBundle",
    "LegacyEnvironmentLock",
    "LegacyMetricContract",
    "LegacyProjection",
    "LegacyTaskManifest",
    "LegacyTaskMetadata",
    "LegacyTestManifest",
]
