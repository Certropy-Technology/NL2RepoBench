"""Strict F0 canonical records.

This module is the migration target.  It intentionally has no decoder for the
historical v1/v2 records; decoding belongs exclusively to the migration tool.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .canonical import content_digest
from .models import (
    ArtifactRef,
    HarborExecutionProfile,
    MetricContract,
    NetworkPolicy,
    SourceLock,
    TaskLifecycleRecord,
    TaskStatus,
    TaskVerifierSpec,
    Visibility,
)

SHA256 = r"^sha256:[0-9a-f]{64}$"
TaskId = Annotated[
    str,
    Field(
        pattern=r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*|@[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)$"
    ),
]


class CanonicalRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
    schema_version: Literal["1.0"] = "1.0"

    def content_digest(self) -> str:
        return content_digest(self)


class RuntimeLanguage(StrEnum):
    PYTHON = "python"
    NODE = "node"
    GO = "go"


class PackageManager(StrEnum):
    UV = "uv"
    PIP = "pip"
    NPM = "npm"
    PNPM = "pnpm"
    GO_MODULES = "go-modules"
    NONE = "none"


class RuntimeProfile(CanonicalRecord):
    language: RuntimeLanguage
    runtime: Literal["cpython", "node", "go"]
    version: str = Field(min_length=1)
    package_manager: PackageManager
    package_manager_version: str | None = None

    @model_validator(mode="after")
    def validate_identity(self) -> RuntimeProfile:
        expected = {"python": "cpython", "node": "node", "go": "go"}[self.language.value]
        if self.runtime != expected:
            raise ValueError("runtime does not match language")
        if self.package_manager is PackageManager.NONE and self.package_manager_version is not None:
            raise ValueError("none package manager must not have a version")
        if self.package_manager is not PackageManager.NONE and not self.package_manager_version:
            raise ValueError("package manager version is required")
        allowed = {
            "python": {PackageManager.UV, PackageManager.PIP, PackageManager.NONE},
            "node": {PackageManager.NPM, PackageManager.PNPM, PackageManager.NONE},
            "go": {PackageManager.GO_MODULES},
        }
        if self.package_manager not in allowed[self.language.value]:
            raise ValueError("package manager is not valid for runtime")
        return self


class EnvironmentLock(CanonicalRecord):
    status: Literal["known", "unknown"] = "unknown"
    runtime: RuntimeProfile | None = None
    os_name: str | None = None
    base_image: str | None = None
    base_image_digest: Annotated[str | None, Field(pattern=SHA256)] = None
    system_packages: tuple[str, ...] = ()
    build_command: str | None = None
    network_policy: NetworkPolicy | None = None

    @model_validator(mode="after")
    def validate_known(self) -> EnvironmentLock:
        if self.status == "known":
            if (
                not self.runtime
                or not self.os_name
                or not self.base_image
                or not self.base_image_digest
            ):
                raise ValueError("known environment requires runtime, OS, image, and digest")
            if self.network_policy is None:
                raise ValueError("known environment requires network policy")
        return self


class DependencyBundle(CanonicalRecord):
    status: Literal["known", "unknown"] = "unknown"
    package_manager: PackageManager
    lock: ArtifactRef | None = None
    offline_store: ArtifactRef | None = None
    inventory: ArtifactRef | None = None
    packages: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_refs(self) -> DependencyBundle:
        refs = (self.lock, self.offline_store, self.inventory)
        if self.status == "known" and any(ref is None for ref in refs):
            raise ValueError("known dependency bundle requires lock, offline_store, and inventory")
        if self.status == "unknown" and any(ref is not None for ref in refs):
            raise ValueError("unknown dependency bundle must not claim artifact references")
        for name, ref in zip(("lock", "offline_store", "inventory"), refs, strict=True):
            if ref is not None and ref.visibility.value != "private":
                raise ValueError(f"dependencies.{name} must be private")
        if (
            self.package_manager is PackageManager.NONE
            and self.status == "known"
            and any(ref is None for ref in refs)
        ):
            raise ValueError(
                "known none dependency bundle still requires canonical empty artifacts"
            )
        if self.package_manager is PackageManager.NONE and self.status == "known":
            # node+none is rejected at the TaskSource runtime-pair boundary.
            if self.packages:
                raise ValueError("known none dependency bundle cannot declare packages")
        return self


class TestManifest(CanonicalRecord):
    framework: Literal["pytest", "node:test", "go-bridge", "custom"]
    report_format: Literal[
        "pytest-junit-xml-v1", "node-test-json-v1", "go-test-json-v1", "custom-json-v1"
    ]
    expected_total: Annotated[int, Field(ge=0)] = 0
    expected_total_source: Literal["frozen-collection", "unknown"] = "unknown"
    commands_artifact: ArtifactRef | None = None
    protected_paths_artifact: ArtifactRef | None = None
    test_bundle: ArtifactRef | None = None

    @model_validator(mode="after")
    def validate_contract(self) -> TestManifest:
        if self.framework == "pytest" and self.report_format != "pytest-junit-xml-v1":
            raise ValueError("pytest requires pytest-junit-xml-v1")
        if self.framework == "node:test" and self.report_format != "node-test-json-v1":
            raise ValueError("node:test requires node-test-json-v1")
        if self.framework == "go-bridge" and self.report_format != "go-test-json-v1":
            raise ValueError("go-bridge requires go-test-json-v1")
        if self.framework == "custom" and self.report_format != "custom-json-v1":
            raise ValueError("custom requires custom-json-v1")
        for name, ref in (
            ("commands_artifact", self.commands_artifact),
            ("protected_paths_artifact", self.protected_paths_artifact),
            ("test_bundle", self.test_bundle),
        ):
            if ref is not None and ref.visibility is not Visibility.PRIVATE:
                raise ValueError(f"tests.{name} must be private")
        if self.expected_total_source == "frozen-collection" and self.expected_total <= 0:
            raise ValueError("frozen test collection must have a positive expected_total")
        return self


class TaskMetadata(CanonicalRecord):
    difficulty: Literal["easy", "medium", "hard", "unknown"] = "unknown"
    category: str = "unknown"
    tags: tuple[str, ...] = ()
    language: RuntimeLanguage


class TaskSource(CanonicalRecord):
    task_id: TaskId
    version: str = "1.0.0"
    instruction: str = "instruction.md"
    metadata: TaskMetadata
    source: SourceLock = Field(default_factory=SourceLock)
    environment: EnvironmentLock
    dependencies: DependencyBundle
    tests: TestManifest
    metric: MetricContract = Field(default_factory=MetricContract)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None
    verifier: TaskVerifierSpec | None = None

    @model_validator(mode="after")
    def validate_instruction(self) -> TaskSource:
        if (
            not self.instruction
            or self.instruction.startswith("/")
            or ".." in self.instruction.split("/")
        ):
            raise ValueError("instruction must be a safe relative path")
        if self.environment.runtime is not None:
            if self.environment.runtime.language != self.metadata.language:
                raise ValueError("metadata language must match environment runtime")
            if self.environment.runtime.package_manager != self.dependencies.package_manager:
                raise ValueError("dependency package manager must match environment runtime")
        if self.tests.framework == "custom" and self.verifier is None:
            raise ValueError("custom tests require a typed verifier specification")
        if self.tests.framework != "custom" and self.verifier is not None:
            raise ValueError("typed verifier is only valid for custom tests")
        if self.environment.runtime is not None:
            expected_tests = {
                RuntimeLanguage.PYTHON: ("pytest", "custom"),
                RuntimeLanguage.NODE: ("node:test",),
                RuntimeLanguage.GO: ("go-bridge",),
            }[self.environment.runtime.language]
            if self.tests.framework not in expected_tests:
                raise ValueError("test framework does not match runtime language")
            if (
                self.environment.runtime.language is RuntimeLanguage.NODE
                and self.environment.runtime.package_manager is PackageManager.NONE
                and self.dependencies.status == "known"
            ):
                raise ValueError("node+none cannot have a known dependency closure")
        production = self.lifecycle.status in {
            TaskStatus.PACKAGED,
            TaskStatus.ORACLE_PASSED,
            TaskStatus.CONTROLS_PASSED,
            TaskStatus.REVIEWED,
            TaskStatus.PILOTED,
            TaskStatus.PUBLISHED,
        }
        if production:
            if self.environment.status != "known" or self.dependencies.status != "known":
                raise ValueError("production lifecycle requires known environment and dependencies")
            if (
                self.tests.expected_total_source != "frozen-collection"
                or self.tests.expected_total <= 0
                or self.tests.commands_artifact is None
            ):
                raise ValueError("production lifecycle requires a frozen test command plan")
            if self.verifier is None and self.tests.test_bundle is None:
                raise ValueError("production lifecycle requires a private test or verifier bundle")
        if (
            self.oracle_bundle is not None
            and self.oracle_bundle.visibility is not Visibility.PRIVATE
        ):
            raise ValueError("oracle_bundle must be private")
        return self

    def to_manifest(self, instruction: ArtifactRef) -> TaskManifest:
        """Project a validated source into the single canonical manifest shape."""

        if instruction.visibility is not Visibility.PUBLIC:
            raise ValueError("compiled instruction artifact must be public")
        return TaskManifest(
            task_id=self.task_id,
            version=self.version,
            metadata=self.metadata,
            instruction=instruction,
            source_lock=self.source,
            environment_lock=self.environment,
            dependency_bundle=self.dependencies,
            tests=self.tests,
            metric=self.metric,
            lifecycle=self.lifecycle,
            harbor=self.harbor,
            oracle_bundle=self.oracle_bundle,
            verifier=self.verifier,
        )


class TaskManifest(CanonicalRecord):
    """Canonical compiled manifest with public instruction artifact."""

    task_id: TaskId
    version: str = "1.0.0"
    metadata: TaskMetadata
    instruction: ArtifactRef
    source_lock: SourceLock = Field(default_factory=SourceLock)
    environment_lock: EnvironmentLock
    dependency_bundle: DependencyBundle
    tests: TestManifest
    metric: MetricContract = Field(default_factory=MetricContract)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None
    verifier: TaskVerifierSpec | None = None

    @model_validator(mode="after")
    def validate_runtime_contract(self) -> TaskManifest:
        runtime = self.environment_lock.runtime
        if runtime is None:
            return self
        if runtime.language.value != self.metadata.language.value:
            raise ValueError("metadata language must match environment runtime")
        if runtime.package_manager != self.dependency_bundle.package_manager:
            raise ValueError("dependency package manager must match environment runtime")
        if self.tests.framework == "custom" and self.verifier is None:
            raise ValueError("custom tests require a typed verifier specification")
        if self.tests.framework != "custom" and self.verifier is not None:
            raise ValueError("typed verifier is only valid for custom tests")
        expected_tests = {
            RuntimeLanguage.PYTHON: ("pytest", "custom"),
            RuntimeLanguage.NODE: ("node:test",),
            RuntimeLanguage.GO: ("go-bridge",),
        }[runtime.language]
        if self.tests.framework not in expected_tests:
            raise ValueError("test framework does not match runtime language")
        if (
            runtime.language is RuntimeLanguage.NODE
            and runtime.package_manager is PackageManager.NONE
            and self.dependency_bundle.status == "known"
        ):
            raise ValueError("node+none cannot have a known dependency closure")
        if (
            self.oracle_bundle is not None
            and self.oracle_bundle.visibility is not Visibility.PRIVATE
        ):
            raise ValueError("oracle_bundle must be private")
        return self


__all__ = [
    "DependencyBundle",
    "EnvironmentLock",
    "PackageManager",
    "RuntimeLanguage",
    "RuntimeProfile",
    "TaskManifest",
    "TaskMetadata",
    "TaskSource",
    "TestManifest",
]
