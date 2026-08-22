"""Additive v2 records for the Node/npm pilot.

The v1 models deliberately remain in ``models.py``. This module has its own
record base and schema version so adding Node fields cannot change v1 JSON
schemas, manifests, or content digests.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    GetJsonSchemaHandler,
    model_validator,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

from .canonical import content_digest
from .models import (
    ArtifactRef,
    Difficulty,
    HarborExecutionProfile,
    SourceLock,
    TaskLifecycleRecord,
)

SCHEMA_VERSION_V2: Literal["2.0"] = "2.0"
NODE_VERSION_PATTERN = r"^22\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$"
SEMVER_PATTERN = r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$"


class V2RecordModel(BaseModel):
    """Strict persisted-record policy for the additive v2 contract."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    schema_version: Literal["2.0"] = SCHEMA_VERSION_V2

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema["x-nl2repobench-runtime-validation"] = True
        schema["x-nl2repobench-model"] = cls.__name__
        return schema

    def content_digest(self) -> str:
        """Hash this record using the same canonical JSON rules as v1."""

        return content_digest(self)


class RuntimeProfileV2(V2RecordModel):
    """Exact runtime and package-manager identity for a v2 task."""

    language: Literal["python", "node"]
    runtime: Literal["cpython", "node"]
    version: str = Field(min_length=1)
    package_manager: Literal["uv", "pip", "npm", "none"]
    package_manager_version: str | None = None
    architecture: Literal["linux/amd64"] = "linux/amd64"
    libc: Literal["glibc", "musl"]

    @model_validator(mode="after")
    def validate_runtime_identity(self) -> RuntimeProfileV2:
        if self.language == "node":
            if self.runtime != "node":
                raise ValueError("Node language requires the node runtime")
            if not re.fullmatch(NODE_VERSION_PATTERN, self.version):
                raise ValueError("Node runtime version must be an exact 22.x.y version")
            if self.package_manager not in {"npm", "none"}:
                raise ValueError("Node runtime supports npm or no package manager")
            if self.package_manager == "npm":
                if self.package_manager_version is None or not re.fullmatch(
                    SEMVER_PATTERN, self.package_manager_version
                ):
                    raise ValueError("npm requires an exact semantic version")
            elif self.package_manager_version is not None:
                raise ValueError("package manager version is only valid with a package manager")
        else:
            if self.runtime != "cpython":
                raise ValueError("Python language requires the cpython runtime")
            if self.package_manager == "npm":
                raise ValueError("Python runtime cannot use npm")
        return self


class EnvironmentLockV2(V2RecordModel):
    """Reproducible OS/runtime metadata for a v2 task."""

    status: Literal["known", "unknown"] = "unknown"
    os_name: str | None = None
    base_image: str | None = None
    base_image_digest: Annotated[str | None, Field(pattern=r"^sha256:[0-9a-f]{64}$")] = None
    runtime: RuntimeProfileV2 | None = None
    network_mode: Literal["public", "no-network", "allowlist"] | None = None

    @model_validator(mode="after")
    def validate_known_environment(self) -> EnvironmentLockV2:
        if self.status == "known":
            missing = [
                name
                for name, value in {
                    "os_name": self.os_name,
                    "base_image": self.base_image,
                    "base_image_digest": self.base_image_digest,
                    "runtime": self.runtime,
                    "network_mode": self.network_mode,
                }.items()
                if value is None or value == ""
            ]
            if missing:
                raise ValueError(f"known Node environment is missing: {', '.join(missing)}")
        return self


class DependencyBundleV2(V2RecordModel):
    """Offline dependency closure with an explicit npm consumer contract."""

    status: Literal["known", "unknown"] = "unknown"
    ecosystem: Literal["python", "npm"]
    consumer: Literal["candidate-runtime", "verifier-runtime"]
    artifact: ArtifactRef | None = None
    lockfile_name: Literal["requirements.lock.txt", "package-lock.json"]
    lockfile_version: str
    package_manager: Literal["uv", "pip", "npm"]
    package_manager_version: str
    install_mode: Literal["offline"] = "offline"
    lifecycle_scripts: Literal["ignore-scripts"] = "ignore-scripts"
    packages: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_dependency_identity(self) -> DependencyBundleV2:
        if self.ecosystem == "npm":
            if self.lockfile_name != "package-lock.json":
                raise ValueError("npm dependency bundles require package-lock.json")
            if self.lockfile_version != "3":
                raise ValueError("npm dependency bundles require lockfile version 3")
            if self.package_manager != "npm":
                raise ValueError("npm dependency bundles require npm as package manager")
            if not re.fullmatch(SEMVER_PATTERN, self.package_manager_version):
                raise ValueError("npm dependency bundles require an exact npm version")
        else:
            if self.lockfile_name == "package-lock.json" or self.package_manager == "npm":
                raise ValueError("Python dependency bundles cannot use npm metadata")
        if self.status == "known" and self.artifact is None:
            raise ValueError("known dependency bundle requires an artifact")
        return self


class TestManifestV2(V2RecordModel):
    """Frozen private ``node:test`` collection and report contract."""

    framework: Literal["node:test"] = "node:test"
    report_format: Literal["node-test-json-v1"] = "node-test-json-v1"
    expected_total: Annotated[int, Field(gt=0)]
    expected_total_source: Literal["frozen-collection"] = "frozen-collection"
    commands_artifact: ArtifactRef | None = None
    test_bundle: ArtifactRef | None = None

    @model_validator(mode="after")
    def validate_private_artifacts(self) -> TestManifestV2:
        for field_name, reference in {
            "commands_artifact": self.commands_artifact,
            "test_bundle": self.test_bundle,
        }.items():
            if reference is not None and reference.visibility.value != "private":
                raise ValueError(f"{field_name} must be private")
        return self


class NodeMetricContractV2(V2RecordModel):
    """Fixed-denominator leaf-test score semantics for Node tasks."""

    contract_id: Literal["node-test-leaf-pass-rate-v1"] = "node-test-leaf-pass-rate-v1"
    passed_statuses: tuple[Literal["passed"], ...] = ("passed",)
    denominator_statuses: tuple[Literal["passed", "failed", "error", "skipped", "todo"], ...] = (
        "passed",
        "failed",
        "error",
        "skipped",
        "todo",
    )
    collection_mismatch: Literal["fail", "record-only"] = "fail"
    formula: str = "clamp(passed / frozen_total, 0, 1)"


class TaskMetadataV2(V2RecordModel):
    """Node-specific discoverability metadata."""

    difficulty: Difficulty = "unknown"
    category: str = "unknown"
    tags: tuple[str, ...] = ()
    language: Literal["node"] = "node"


class DeclarativeTaskSourceV2(V2RecordModel):
    """Human-maintained v2 task definition loaded from ``task.toml``."""

    task_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    version: str = "2.0.0"
    instruction: str = "instruction.md"
    metadata: TaskMetadataV2 = Field(default_factory=TaskMetadataV2)
    source: SourceLock = Field(default_factory=SourceLock)
    environment: EnvironmentLockV2 = Field(default_factory=EnvironmentLockV2)
    dependencies: DependencyBundleV2
    tests: TestManifestV2
    metric: NodeMetricContractV2 = Field(default_factory=NodeMetricContractV2)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None

    @model_validator(mode="after")
    def validate_relative_instruction(self) -> DeclarativeTaskSourceV2:
        from pathlib import PurePosixPath

        path = PurePosixPath(self.instruction)
        if path.is_absolute() or ".." in path.parts or self.instruction in {"", "."}:
            raise ValueError("instruction must be a non-empty relative path without '..'")
        return self


class TaskRefV2(V2RecordModel):
    """Stable reference to a v2 canonical task manifest."""

    task_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    version: str
    manifest_digest: Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
    manifest_uri: str


class TaskManifestV2(V2RecordModel):
    """Canonical Node task record produced by the additive catalog path."""

    task_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    version: str = "2.0.0"
    metadata: TaskMetadataV2 = Field(default_factory=TaskMetadataV2)
    instruction: ArtifactRef
    source_lock: SourceLock = Field(
        default_factory=SourceLock,
        validation_alias=AliasChoices("source_lock", "source"),
    )
    environment_lock: EnvironmentLockV2 = Field(
        default_factory=EnvironmentLockV2,
        validation_alias=AliasChoices("environment_lock", "environment"),
    )
    dependency_bundle: DependencyBundleV2
    tests: TestManifestV2
    metric: NodeMetricContractV2 = Field(default_factory=NodeMetricContractV2)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None

    @model_validator(mode="after")
    def validate_node_contract(self) -> TaskManifestV2:
        runtime = self.environment_lock.runtime
        if runtime is not None and runtime.language != self.metadata.language:
            raise ValueError("metadata language must match runtime language")
        if runtime is not None and runtime.runtime != "node":
            raise ValueError("Node task requires the node runtime")
        if self.dependency_bundle.ecosystem != "npm":
            raise ValueError("Node task requires an npm dependency bundle")
        if self.tests.framework != "node:test":
            raise ValueError("Node task requires the node:test framework")
        if self.metric.contract_id != "node-test-leaf-pass-rate-v1":
            raise ValueError("Node task requires node-test-leaf-pass-rate-v1")
        return self

    def publication_gaps(self) -> tuple[str, ...]:
        """Return stable field paths that block Node production publication."""

        gaps: list[str] = []
        if self.metadata.language != "node":
            gaps.append("metadata.language=node")
        if self.metadata.difficulty == "unknown":
            gaps.append("metadata.difficulty")
        if self.metadata.category == "unknown":
            gaps.append("metadata.category")
        if self.instruction.visibility.value != "public":
            gaps.append("instruction.visibility=public")
        if self.environment_lock.status != "known":
            gaps.append("environment.status=known")
        else:
            runtime = self.environment_lock.runtime
            if runtime is None:
                gaps.append("environment.runtime")
            elif runtime.version.split(".", 1)[0] != "22":
                gaps.append("environment.runtime.version=node-22")
            if self.environment_lock.base_image_digest is None:
                gaps.append("environment.base_image_digest")
        if self.dependency_bundle.status != "known":
            gaps.append("dependency_bundle.status=known")
        if self.dependency_bundle.artifact is None:
            gaps.append("dependency_bundle.artifact")
        if self.tests.expected_total_source != "frozen-collection":
            gaps.append("tests.expected_total_source=frozen-collection")
        if self.tests.commands_artifact is None:
            gaps.append("tests.commands_artifact")
        if self.tests.test_bundle is None:
            gaps.append("tests.test_bundle")
        if (
            self.tests.commands_artifact is not None
            and self.tests.commands_artifact.visibility.value != "private"
        ):
            gaps.append("tests.commands_artifact.visibility=private")
        if (
            self.tests.test_bundle is not None
            and self.tests.test_bundle.visibility.value != "private"
        ):
            gaps.append("tests.test_bundle.visibility=private")
        if self.oracle_bundle is None:
            gaps.append("oracle_bundle")
        elif self.oracle_bundle.visibility.value != "private":
            gaps.append("oracle_bundle.visibility=private")
        if self.harbor is None:
            gaps.append("harbor")
        if self.metric.contract_id != "node-test-leaf-pass-rate-v1":
            gaps.append("metric.contract_id=node-test-leaf-pass-rate-v1")
        return tuple(gaps)
