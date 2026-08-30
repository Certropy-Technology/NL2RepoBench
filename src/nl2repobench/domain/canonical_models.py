"""Shared records for the single active canonical runtime contract."""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

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

SHA256_PATTERN = r"^sha256:[0-9a-f]{64}$"
TASK_ID_PATTERN = (
    r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*|@[A-Za-z0-9][A-Za-z0-9._-]*/"
    r"[A-Za-z0-9][A-Za-z0-9._-]*)$"
)
TaskId = Annotated[str, Field(pattern=TASK_ID_PATTERN)]
Difficulty = Literal["easy", "medium", "hard", "unknown"]
MetricStatus = Literal["passed", "failed", "error", "skipped", "todo", "xfail"]


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


class CanonicalRecord(BaseModel):
    """Strict persisted-record policy for every active runtime record."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
    schema_version: Literal["1.0"] = "1.0"

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
        return content_digest(self)


class ArtifactRef(CanonicalRecord):
    digest: Annotated[str, Field(pattern=SHA256_PATTERN)]
    size_bytes: Annotated[int, Field(ge=0)]
    media_type: str = "application/octet-stream"
    uri: str
    visibility: Visibility = Visibility.PUBLIC

    @model_validator(mode="after")
    def validate_content_addressed_uri(self) -> ArtifactRef:
        expected = f"artifact://{self.visibility.value}/{self.digest}"
        if self.uri != expected:
            raise ValueError(f"artifact URI must match visibility and digest: {expected}")
        return self


class SourceLock(CanonicalRecord):
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
                        ]
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


class NetworkPolicy(CanonicalRecord):
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
                            }
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
        return tuple(host for host in self.allowed_hosts if host_category(host) == "registry")

    @property
    def model_provider_hosts(self) -> tuple[str, ...]:
        return tuple(
            host for host in self.allowed_hosts if host_category(host) == "model-provider"
        )

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
                raise ValueError("allowlist mode requires at least one exact hostname")
            if not (self.reason or "").strip():
                raise ValueError("allowlist mode requires a reason")
        elif self.allowed_hosts:
            raise ValueError("allowed_hosts is only valid when mode='allowlist'")
        if (
            self.mode == "no-network"
            and self.offline_dependencies == "missing"
            and not (self.reason or "").strip()
        ):
            raise ValueError("missing offline dependencies require a reason")
        return self


class MetricContract(CanonicalRecord):
    """The only active fixed-denominator score contract."""

    contract_id: Literal["fixed-test-pass-rate-v1"] = "fixed-test-pass-rate-v1"
    passed_statuses: tuple[MetricStatus, ...] = ("passed",)
    denominator_statuses: tuple[MetricStatus, ...] = (
        "passed",
        "failed",
        "error",
        "skipped",
        "todo",
        "xfail",
    )
    collection_mismatch: Literal["fail", "record-only"] = "fail"
    formula: Literal["clamp(passed / frozen_total, 0, 1)"] = (
        "clamp(passed / frozen_total, 0, 1)"
    )

    @model_validator(mode="after")
    def validate_status_sets(self) -> Self:
        if not self.passed_statuses or len(set(self.passed_statuses)) != len(
            self.passed_statuses
        ):
            raise ValueError("metric passed statuses must be nonempty and unique")
        if len(set(self.denominator_statuses)) != len(self.denominator_statuses):
            raise ValueError("metric denominator statuses must be unique")
        if not set(self.passed_statuses).issubset(self.denominator_statuses):
            raise ValueError("passed statuses must be in denominator statuses")
        return self


class TaskVerifierSpec(CanonicalRecord):
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
                raise ValueError(f"verifier environment name is invalid: {name}")
            if name in forbidden:
                raise ValueError(f"verifier environment cannot override {name}")
            if len(value) > 512:
                raise ValueError("verifier environment values are too long")
        return self


class HarborExecutionProfile(CanonicalRecord):
    description: str
    keywords: Annotated[tuple[str, ...], Field(min_length=3, max_length=8)]
    agent_timeout_sec: Annotated[float, Field(gt=0)] = 600.0
    verifier_timeout_sec: Annotated[float, Field(gt=0)] = 600.0
    candidate_install_timeout_sec: Annotated[float, Field(gt=0)] = 90.0
    candidate_total_timeout_sec: Annotated[float, Field(gt=0)] = 300.0
    agent_network_mode: Literal["public", "no-network", "allowlist"] = "public"
    agent_allowed_hosts: tuple[str, ...] = ()
    verifier_network_mode: Literal["no-network"] = "no-network"
    cpus: Annotated[int, Field(gt=0)] = 2
    memory_mb: Annotated[int, Field(ge=512)] = 2048
    storage_mb: Annotated[int, Field(ge=1024)] = 4096
    workspace_artifact: str = "/workspace"

    @field_validator("agent_allowed_hosts", mode="before")
    @classmethod
    def normalize_agent_hosts(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        return validate_allowed_hosts(value)

    @model_validator(mode="after")
    def validate_profile(self) -> HarborExecutionProfile:
        if self.agent_network_mode == "allowlist" and not self.agent_allowed_hosts:
            raise ValueError("allowlist mode requires agent_allowed_hosts")
        if self.agent_allowed_hosts and self.agent_network_mode != "allowlist":
            raise ValueError("agent_allowed_hosts requires allowlist mode")
        required = (
            self.candidate_install_timeout_sec + self.candidate_total_timeout_sec + 60.0
        )
        if required >= self.verifier_timeout_sec:
            raise ValueError(
                "candidate install + call budgets + 60s reserve must be below verifier_timeout_sec"
            )
        return self

    def apply_network_policy(self, policy: NetworkPolicy | None) -> HarborExecutionProfile:
        if policy is None:
            return self
        return self.model_copy(
            update={
                "agent_network_mode": policy.mode,
                "agent_allowed_hosts": policy.allowed_hosts,
            }
        )


class TaskLifecycleRecord(CanonicalRecord):
    status: TaskStatus = TaskStatus.DISCOVERED
    owner: str | None = None
    reason: str | None = None
    evidence: tuple[ArtifactRef, ...] = ()
    approval_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_terminal_status(self) -> TaskLifecycleRecord:
        if self.status in {TaskStatus.BLOCKED, TaskStatus.EXCLUDED} and not self.reason:
            raise ValueError(f"{self.status} tasks require a reason")
        if self.status is TaskStatus.PUBLISHED:
            missing = [
                name
                for name, value in {
                    "owner": self.owner,
                    "evidence": self.evidence,
                    "approval_refs": self.approval_refs,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"published lifecycle is missing: {', '.join(missing)}")
        return self


class TaskRef(CanonicalRecord):
    task_id: TaskId
    version: str
    manifest_digest: Annotated[str, Field(pattern=SHA256_PATTERN)]
    manifest_uri: str


class DatasetManifest(CanonicalRecord):
    dataset_id: TaskId
    version: str = "0.1.0"
    description: str
    metric_contract: Literal["fixed-test-pass-rate-v1"] = "fixed-test-pass-rate-v1"
    tasks: Annotated[tuple[TaskRef, ...], Field(min_length=1)]
    source_format: str = "canonical"

    @model_validator(mode="after")
    def validate_unique_tasks(self) -> DatasetManifest:
        task_ids = [task.task_id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("dataset task IDs must be unique")
        return self


class MetadataGapTask(CanonicalRecord):
    task_id: TaskId
    missing_fields: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class MetadataGapReport(CanonicalRecord):
    dataset_id: str
    task_count: Annotated[int, Field(ge=0)]
    complete_task_count: Annotated[int, Field(ge=0)]
    gap_counts: dict[str, int]
    tasks: tuple[MetadataGapTask, ...]


__all__ = [
    "ArtifactRef",
    "CanonicalRecord",
    "DatasetManifest",
    "Difficulty",
    "FailureClass",
    "HarborExecutionProfile",
    "MetadataGapReport",
    "MetadataGapTask",
    "MetricContract",
    "MetricStatus",
    "NetworkPolicy",
    "ProvenanceStatus",
    "SourceLock",
    "TaskId",
    "TaskLifecycleRecord",
    "TaskRef",
    "TaskStatus",
    "TaskVerifierSpec",
    "Visibility",
]
