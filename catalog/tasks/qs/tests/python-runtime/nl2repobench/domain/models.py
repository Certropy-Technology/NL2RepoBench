"""Versioned Pydantic models for NL2RepoBench metadata.

The models intentionally allow incomplete legacy imports by marking their
provenance as ``unknown``. Publishing validation can then require known values
without pretending that the old four-file format contained information it did
not actually contain.
"""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetJsonSchemaHandler,
    JsonValue,
    field_validator,
    model_validator,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

from .canonical import content_digest
from .network_policy import (
    OFFLINE_DEPENDENCY_SOURCES,
    NetworkPolicyMode,
    admissible_hosts,
    host_category,
    validate_allowed_hosts,
)

SCHEMA_VERSION: Literal["1.0"] = "1.0"
SHA256_PATTERN = r"^sha256:[0-9a-f]{64}$"
TASK_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
Difficulty = Literal["easy", "medium", "hard", "unknown"]


class ProvenanceStatus(StrEnum):
    KNOWN = "known"
    UNKNOWN = "unknown"


class TaskStatus(StrEnum):
    DISCOVERED = "discovered"
    FROZEN = "frozen"
    INVENTORIED = "inventoried"
    SPECIFIED = "specified"
    PACKAGED = "packaged"
    ORACLE_PASSED = "oracle-passed"
    CONTROLS_PASSED = "controls-passed"
    REVIEWED = "reviewed"
    PILOTED = "piloted"
    PUBLISHED = "published"
    BLOCKED = "blocked"
    EXCLUDED = "excluded"


class FailureClass(StrEnum):
    SOURCE = "source"
    SPEC = "spec"
    ENVIRONMENT = "environment"
    VERIFIER = "verifier"
    MODEL = "model"
    INFRASTRUCTURE = "infrastructure"


class Visibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class RecordModel(BaseModel):
    """Common strict model policy for persisted records."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    schema_version: Literal["1.0"] = SCHEMA_VERSION

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
        """Hash this record without adding a self-referential hash field."""

        return content_digest(self)


class ArtifactRef(RecordModel):
    """A content-addressed artifact without embedding its bytes."""

    digest: Annotated[str, Field(pattern=SHA256_PATTERN)]
    size_bytes: Annotated[int, Field(ge=0)]
    media_type: str = "application/octet-stream"
    uri: str
    visibility: Visibility = Visibility.PUBLIC

    @model_validator(mode="after")
    def validate_content_addressed_uri(self) -> ArtifactRef:
        if self.uri.startswith("artifact://"):
            expected = f"artifact://{self.visibility.value}/{self.digest}"
            if self.uri != expected:
                raise ValueError(f"artifact URI must match visibility and digest: {expected}")
        return self


class SourceLock(RecordModel):
    """Frozen upstream provenance, or an explicit unknown legacy record."""

    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "required": ["status"],
                        "properties": {"status": {"const": "known"}},
                    },
                    "then": {
                        "required": [
                            "upstream_url",
                            "revision",
                            "license_spdx",
                            "source_digest",
                        ],
                        "properties": {
                            "upstream_url": {"type": "string", "minLength": 1},
                            "revision": {
                                "type": "string",
                                "pattern": "^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$",
                            },
                            "license_spdx": {"type": "string", "minLength": 1},
                            "source_digest": {
                                "type": "string",
                                "pattern": SHA256_PATTERN,
                            },
                        },
                    },
                }
            ]
        }
    )

    status: ProvenanceStatus = ProvenanceStatus.UNKNOWN
    upstream_url: str | None = None
    revision: str | None = None
    license_spdx: str | None = None
    source_digest: str | None = Field(default=None, pattern=SHA256_PATTERN)
    submodules: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_known_provenance(self) -> SourceLock:
        if self.status is ProvenanceStatus.KNOWN:
            missing = [
                name
                for name, value in {
                    "upstream_url": self.upstream_url,
                    "revision": self.revision,
                    "license_spdx": self.license_spdx,
                    "source_digest": self.source_digest,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"known source provenance is missing: {', '.join(missing)}")
        if self.revision and not re.fullmatch(
            r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", self.revision
        ):
            raise ValueError("revision must be a complete 40- or 64-character Git commit")
        return self


_ADMISSIBLE_HOST_ENUM: list[JsonValue] = list(sorted(admissible_hosts()))
_OFFLINE_DEPENDENCY_ENUM: list[JsonValue] = list(OFFLINE_DEPENDENCY_SOURCES)


class NetworkPolicy(RecordModel):
    """Declared run-time egress policy for one task.

    The dependency closure is installed at image build time, where Docker still
    has network, so ``no-network`` is the preferred run-time mode. ``allowlist``
    covers what cannot be preinstalled: primarily the model provider endpoint an
    in-container agent needs to reach, and per-task registry hosts for packages
    that resist baking. Code hosts, raw file endpoints, wildcard suffixes and
    generic source mirrors are rejected by
    :mod:`nl2repobench.domain.network_policy` so that an agent cannot fetch the
    frozen upstream implementation it is asked to reproduce.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "required": ["mode"],
                        "properties": {"mode": {"const": "allowlist"}},
                    },
                    "then": {
                        "required": ["allowed_hosts", "reason"],
                        "properties": {
                            "allowed_hosts": {
                                "type": "array",
                                "minItems": 1,
                                "items": {"enum": _ADMISSIBLE_HOST_ENUM},
                            },
                            "reason": {"type": "string", "minLength": 1},
                        },
                    },
                    "else": {"properties": {"allowed_hosts": {"maxItems": 0}}},
                },
                {"properties": {"offline_dependencies": {"enum": _OFFLINE_DEPENDENCY_ENUM}}},
            ]
        }
    )

    mode: NetworkPolicyMode = "no-network"
    allowed_hosts: tuple[str, ...] = ()
    offline_dependencies: Literal["preinstalled-image", "private-artifact", "missing"] = "missing"
    reference_source_fetch: Literal["forbidden"] = "forbidden"
    reason: str | None = None

    @property
    def registry_hosts(self) -> tuple[str, ...]:
        """Allowed package registry hosts, which should stay empty when possible."""

        return tuple(h for h in self.allowed_hosts if host_category(h) == "registry")

    @property
    def model_provider_hosts(self) -> tuple[str, ...]:
        """Allowed model inference endpoints for an in-container agent."""

        return tuple(h for h in self.allowed_hosts if host_category(h) == "model-provider")

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def normalize_hosts(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        return validate_allowed_hosts(value)

    @model_validator(mode="after")
    def validate_policy(self) -> NetworkPolicy:
        if self.mode == "allowlist":
            if not self.allowed_hosts:
                raise ValueError(
                    "allowlist mode requires at least one exact registry hostname; "
                    "prefer mode='no-network' with preinstalled dependencies"
                )
            if not (self.reason or "").strip():
                raise ValueError(
                    "allowlist mode requires a reason recording why the dependency "
                    "closure cannot be preinstalled"
                )
        elif self.allowed_hosts:
            raise ValueError("allowed_hosts is only valid when mode='allowlist'")
        if self.mode == "no-network" and self.offline_dependencies == "missing":
            if not (self.reason or "").strip():
                raise ValueError(
                    "no-network with offline_dependencies='missing' requires a reason "
                    "naming the dependency lock or package cache that is still absent"
                )
        return self


class EnvironmentLock(RecordModel):
    """Reproducible execution environment metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "required": ["status"],
                        "properties": {"status": {"const": "known"}},
                    },
                    "then": {
                        "required": [
                            "python_version",
                            "os_name",
                            "base_image",
                            "base_image_digest",
                        ],
                        "properties": {
                            "python_version": {"type": "string", "minLength": 1},
                            "os_name": {"type": "string", "minLength": 1},
                            "base_image": {"type": "string", "minLength": 1},
                            "base_image_digest": {
                                "type": "string",
                                "pattern": SHA256_PATTERN,
                            },
                        },
                    },
                }
            ]
        }
    )

    status: ProvenanceStatus = ProvenanceStatus.UNKNOWN
    python_version: str | None = None
    os_name: str | None = None
    base_image: str | None = None
    base_image_digest: str | None = Field(default=None, pattern=SHA256_PATTERN)
    system_packages: tuple[str, ...] = ()
    build_command: str | None = None
    network_mode: Literal["public", "no-network", "allowlist"] | None = None
    network_policy: NetworkPolicy | None = None

    @model_validator(mode="after")
    def validate_network_policy_consistency(self) -> EnvironmentLock:
        policy = self.network_policy
        if policy is None:
            return self
        if self.network_mode is not None and self.network_mode != policy.mode:
            raise ValueError(
                f"network_mode={self.network_mode!r} contradicts "
                f"network_policy.mode={policy.mode!r}"
            )
        return self

    @model_validator(mode="after")
    def validate_known_environment(self) -> EnvironmentLock:
        if self.status is ProvenanceStatus.KNOWN:
            missing = [
                name
                for name, value in {
                    "python_version": self.python_version,
                    "os_name": self.os_name,
                    "base_image": self.base_image,
                    "base_image_digest": self.base_image_digest,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"known environment is missing: {', '.join(missing)}")
        return self


class DependencyBundle(RecordModel):
    """Hash-locked build-time dependencies for Python task images.

    Python Harbor images install candidate dependencies from the package index
    during the Docker build.  The final task never carries a wheelhouse and
    the verifier never uses ``--no-index``.  ``lock_artifact`` contains only a
    requirements lock file with hashes; ``artifact`` is retained solely so
    older catalog records can be diagnosed and rejected during publication.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "required": ["status"],
                        "properties": {"status": {"const": "known"}},
                    },
                    "then": {
                        "required": ["lock_artifact"],
                        "properties": {"lock_artifact": {"not": {"type": "null"}}},
                    },
                }
            ]
        }
    )

    status: ProvenanceStatus = ProvenanceStatus.UNKNOWN
    lock_artifact: ArtifactRef | None = None
    """Private raw ``requirements.lock.txt`` used for network installation."""

    # Legacy field.  It points to a wheelhouse and is intentionally not used
    # by the Python Harbor compiler anymore.  Keeping it in the model lets us
    # produce a precise publication gap for stale catalog records instead of
    # silently treating vendor installation as valid.
    artifact: ArtifactRef | None = None
    installer: Literal["uv", "pip", "system", "unknown"] = "unknown"
    packages: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_known_bundle(self) -> DependencyBundle:
        if self.status is ProvenanceStatus.KNOWN and self.lock_artifact is None:
            raise ValueError("known dependency bundle requires lock_artifact")
        return self


class TaskVerifierSpec(RecordModel):
    """Private task-specific verifier protocol descriptor."""

    protocol: Literal["custom-json-v1"] = "custom-json-v1"
    bundle: ArtifactRef
    entrypoint: str = "run.py"
    environment: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_private_entrypoint(self) -> TaskVerifierSpec:
        path = PurePosixPath(self.entrypoint)
        if path.is_absolute() or not self.entrypoint or "." in path.parts or ".." in path.parts:
            raise ValueError("verifier.entrypoint must be a safe relative path")
        if self.bundle.visibility is not Visibility.PRIVATE:
            raise ValueError("verifier.bundle must be private")
        forbidden = {"PATH", "PYTHONPATH", "LD_PRELOAD", "LD_LIBRARY_PATH"}
        for name, value in self.environment.items():
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", name):
                raise ValueError("verifier environment names must be uppercase shell names")
            if name in forbidden:
                raise ValueError(f"verifier environment cannot override {name}")
            if len(value) > 512:
                raise ValueError("verifier environment values are too long")
        return self


class TestManifest(RecordModel):
    """Frozen test contract; hidden command bytes may be private artifacts."""

    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "oneOf": [
                        {
                            "required": ["commands"],
                            "properties": {"commands": {"minItems": 1}},
                            "not": {"required": ["commands_artifact"]},
                        },
                        {
                            "required": ["commands_artifact"],
                            "properties": {"commands": {"maxItems": 0}},
                        },
                    ]
                },
                {"not": {"required": ["protected_paths", "protected_paths_artifact"]}},
            ]
        }
    )

    framework: Literal["pytest"] = "pytest"
    # Blocked/excluded descriptors may have no frozen collection yet. Runtime
    # publication validation still requires a positive frozen denominator.
    expected_total: Annotated[int, Field(ge=0)] = 0
    expected_total_source: Literal["frozen-collection", "legacy-file", "unknown"] = "unknown"
    commands: tuple[str, ...] = ()
    commands_artifact: ArtifactRef | None = None
    protected_paths: tuple[str, ...] = ()
    protected_paths_artifact: ArtifactRef | None = None
    test_bundle: ArtifactRef | None = None

    @model_validator(mode="after")
    def validate_command_source(self) -> TestManifest:
        if (
            not self.commands
            and self.commands_artifact is None
            and not (self.expected_total == 0 and self.expected_total_source == "unknown")
        ):
            raise ValueError("test commands must be embedded or referenced by an artifact")
        if self.commands and self.commands_artifact is not None:
            raise ValueError("test commands must not be embedded and referenced simultaneously")
        if self.protected_paths and self.protected_paths_artifact is not None:
            raise ValueError("protected paths must not be embedded and referenced simultaneously")
        return self


class MetricContract(RecordModel):
    """Versioned score semantics shared by every task in a dataset."""

    contract_id: str = "fixed-test-pass-rate-v1"
    passed_statuses: tuple[Literal["passed"], ...] = ("passed",)
    # Legacy v1 schema field. The current runtime contract is defined by
    # verification.metric_contract and rejects this historical exclusion field
    # at the evaluator boundary rather than silently applying it.
    excluded_statuses: tuple[Literal["skipped", "xfail"], ...] = ("skipped",)
    collection_mismatch: Literal["fail", "record-only"] = "fail"
    formula: str = "clamp(passed / frozen_total, 0, 1)"


class TaskMetadata(RecordModel):
    """Search and reporting metadata. Unknown is explicit, not guessed."""

    difficulty: Difficulty = "unknown"
    category: str = "unknown"
    tags: tuple[str, ...] = ()
    language: str = "python"


class HarborExecutionProfile(RecordModel):
    """Execution settings deterministically projected into Harbor task.toml."""

    description: str
    keywords: Annotated[tuple[str, ...], Field(min_length=3, max_length=8)]
    agent_timeout_sec: Annotated[float, Field(gt=0)] = 600.0
    verifier_timeout_sec: Annotated[float, Field(gt=0)] = 600.0
    candidate_install_timeout_sec: Annotated[float, Field(gt=0)] = 90.0
    candidate_total_timeout_sec: Annotated[float, Field(gt=0)] = 300.0
    agent_network_mode: Literal["public", "no-network", "allowlist"] = "public"
    agent_allowed_hosts: tuple[str, ...] = ()
    verifier_network_mode: Literal["no-network"] = "no-network"

    @field_validator("agent_allowed_hosts", mode="before")
    @classmethod
    def normalize_agent_hosts(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        return validate_allowed_hosts(value)

    @model_validator(mode="after")
    def validate_agent_allowlist(self) -> HarborExecutionProfile:
        if self.agent_network_mode == "allowlist" and not self.agent_allowed_hosts:
            raise ValueError("agent_network_mode='allowlist' requires agent_allowed_hosts")
        if self.agent_allowed_hosts and self.agent_network_mode != "allowlist":
            raise ValueError(
                "agent_allowed_hosts is only valid with agent_network_mode='allowlist'"
            )
        return self

    cpus: Annotated[int, Field(gt=0)] = 2
    memory_mb: Annotated[int, Field(ge=512)] = 2048
    storage_mb: Annotated[int, Field(ge=1024)] = 4096
    workspace_artifact: str = "/workspace"

    def apply_network_policy(self, policy: NetworkPolicy | None) -> HarborExecutionProfile:
        """Return the Harbor profile resolved from the catalog policy.

        ``network_policy`` is the human-facing authority. The legacy Harbor
        fields remain accepted for compatibility, but a declared policy always
        wins when the compiler projects a runtime bundle.
        """

        if policy is None:
            return self
        return self.model_copy(
            update={
                "agent_network_mode": policy.mode,
                "agent_allowed_hosts": policy.allowed_hosts,
            }
        )

    @model_validator(mode="after")
    def validate_candidate_time_budget(self) -> HarborExecutionProfile:
        reserved_verifier_sec = 60.0
        required = (
            self.candidate_install_timeout_sec
            + self.candidate_total_timeout_sec
            + reserved_verifier_sec
        )
        if required >= self.verifier_timeout_sec:
            raise ValueError(
                "candidate install + call budgets + 60s reserve must be below verifier_timeout_sec"
            )
        return self


class TaskLifecycleRecord(RecordModel):
    """Auditable task status and evidence references."""

    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "required": ["status"],
                        "properties": {"status": {"enum": ["blocked", "excluded"]}},
                    },
                    "then": {
                        "required": ["reason"],
                        "properties": {"reason": {"type": "string", "minLength": 1}},
                    },
                },
                {
                    "if": {
                        "required": ["status"],
                        "properties": {"status": {"const": "published"}},
                    },
                    "then": {
                        "required": ["owner", "evidence", "approval_refs"],
                        "properties": {
                            "owner": {"type": "string", "minLength": 1},
                            "evidence": {"minItems": 1},
                            "approval_refs": {"minItems": 1},
                        },
                    },
                },
            ]
        }
    )

    status: TaskStatus = TaskStatus.DISCOVERED
    owner: str | None = None
    reason: str | None = None
    evidence: tuple[ArtifactRef, ...] = ()
    approval_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_terminal_reason(self) -> TaskLifecycleRecord:
        if self.status in {TaskStatus.BLOCKED, TaskStatus.EXCLUDED} and not self.reason:
            raise ValueError(f"{self.status} tasks require a reason")
        if self.status is TaskStatus.PUBLISHED:
            missing = []
            if not self.owner:
                missing.append("owner")
            if not self.evidence:
                missing.append("evidence")
            if not self.approval_refs:
                missing.append("approval_refs")
            if missing:
                raise ValueError(f"published lifecycle is missing: {', '.join(missing)}")
        return self


class LegacyProjection(RecordModel):
    """Pointers to the four-file legacy input, never the canonical source."""

    source_root: str
    instruction_path: str
    count_path: str
    commands_path: str
    protected_paths_path: str


class TaskManifest(RecordModel):
    """Canonical task record produced by authoring stages."""

    task_id: Annotated[str, Field(pattern=TASK_ID_PATTERN)]
    version: str = "1.0.0"
    metadata: TaskMetadata = Field(default_factory=TaskMetadata)
    instruction: ArtifactRef
    source_lock: SourceLock = Field(default_factory=SourceLock)
    environment_lock: EnvironmentLock = Field(default_factory=EnvironmentLock)
    dependency_bundle: DependencyBundle = Field(default_factory=DependencyBundle)
    tests: TestManifest
    metric: MetricContract = Field(default_factory=MetricContract)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None
    verifier: TaskVerifierSpec | None = None
    legacy_projection: LegacyProjection | None = None

    def publication_gaps(self) -> tuple[str, ...]:
        """Return stable field paths that prevent a production publication."""

        gaps: list[str] = []
        if self.metadata.difficulty == "unknown":
            gaps.append("metadata.difficulty")
        if self.metadata.category == "unknown":
            gaps.append("metadata.category")
        if self.instruction.visibility is not Visibility.PUBLIC:
            gaps.append("instruction.visibility=public")
        if self.source_lock.status is not ProvenanceStatus.KNOWN:
            gaps.append("source_lock.status=known")
        if self.environment_lock.status is not ProvenanceStatus.KNOWN:
            gaps.append("environment_lock.status=known")
        if self.dependency_bundle.status is not ProvenanceStatus.KNOWN:
            gaps.append("dependency_bundle.status=known")
        if self.dependency_bundle.lock_artifact is None:
            gaps.append("dependency_bundle.lock_artifact")
        if self.dependency_bundle.artifact is not None:
            gaps.append("dependency_bundle.artifact=forbidden")
        if self.tests.expected_total_source != "frozen-collection":
            gaps.append("tests.expected_total_source=frozen-collection")
        if self.tests.expected_total <= 0:
            gaps.append("tests.expected_total>0")
        if self.verifier is None:
            if self.tests.test_bundle is None:
                gaps.append("tests.test_bundle")
            elif self.tests.test_bundle.visibility is not Visibility.PRIVATE:
                gaps.append("tests.test_bundle.visibility=private")
            if self.tests.commands_artifact is None:
                gaps.append("tests.commands_artifact")
            elif self.tests.commands_artifact.visibility is not Visibility.PRIVATE:
                gaps.append("tests.commands_artifact.visibility=private")
        if self.metric.contract_id != "fixed-test-pass-rate-v1":
            gaps.append("metric.contract_id=fixed-test-pass-rate-v1")
        if self.harbor is None:
            gaps.append("harbor")
        if self.oracle_bundle is None:
            gaps.append("oracle_bundle")
        elif self.oracle_bundle.visibility is not Visibility.PRIVATE:
            gaps.append("oracle_bundle.visibility=private")
        return tuple(gaps)

    @model_validator(mode="after")
    def validate_published_manifest(self) -> TaskManifest:
        if self.lifecycle.status is TaskStatus.PUBLISHED:
            gaps = self.publication_gaps()
            if gaps:
                raise ValueError(f"published task is not publishable: {', '.join(gaps)}")
        return self


class TaskRef(RecordModel):
    """Stable reference to a task manifest in a dataset."""

    task_id: Annotated[str, Field(pattern=TASK_ID_PATTERN)]
    version: str
    manifest_digest: Annotated[str, Field(pattern=SHA256_PATTERN)]
    manifest_uri: str


class DatasetManifest(RecordModel):
    """Dataset index compiled from immutable task manifest references."""

    dataset_id: Annotated[str, Field(pattern=TASK_ID_PATTERN)]
    version: str = "0.1.0"
    description: str
    metric_contract: str = "fixed-test-pass-rate-v1"
    tasks: Annotated[tuple[TaskRef, ...], Field(min_length=1)]
    source_format: str = "canonical"

    @model_validator(mode="after")
    def validate_unique_tasks(self) -> DatasetManifest:
        task_ids = [task.task_id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("dataset task IDs must be unique")
        return self


class MetadataGapTask(RecordModel):
    """One task's explicit migration gaps, suitable for tabular reporting."""

    task_id: Annotated[str, Field(pattern=TASK_ID_PATTERN)]
    missing_fields: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class MetadataGapReport(RecordModel):
    """Deterministic summary of information absent from a legacy task."""

    dataset_id: str
    task_count: Annotated[int, Field(ge=0)]
    complete_task_count: Annotated[int, Field(ge=0)]
    gap_counts: dict[str, int]
    tasks: tuple[MetadataGapTask, ...]
