"""Versioned data contracts emitted by a separate verifier."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, model_validator

from nl2repobench.domain.models import FailureClass, RecordModel


class VerificationReason(StrEnum):
    ARTIFACT_COPY_FAILED = "artifact-copy-failed"
    CANDIDATE_WORKSPACE_REJECTED = "candidate-workspace-rejected"
    CANDIDATE_INSTALLATION_FAILED = "candidate-installation-failed"
    SETUP_COMMAND_FAILED = "setup-command-failed"
    COLLECTION_REPORT_MISSING = "collection-report-missing"
    COLLECTION_REPORT_MALFORMED = "collection-report-malformed"
    COLLECTION_ERROR = "collection-error"
    COLLECTION_MISMATCH = "collection-mismatch"
    JUNIT_MISSING = "junit-missing"
    JUNIT_MALFORMED = "junit-malformed"
    JUNIT_COUNT_MISMATCH = "junit-count-mismatch"
    PYTEST_ABNORMAL_EXIT = "pytest-abnormal-exit"
    PYTEST_REPORT_MISMATCH = "pytest-report-mismatch"
    VERIFIER_TIMEOUT = "verifier-timeout"
    VERIFIER_NETWORK_AVAILABLE = "verifier-network-available"
    VERIFIER_INTERNAL_ERROR = "verifier-internal-error"


class TestCounts(RecordModel):
    collected: Annotated[int, Field(ge=0)] = 0
    passed: Annotated[int, Field(ge=0)] = 0
    failed: Annotated[int, Field(ge=0)] = 0
    errors: Annotated[int, Field(ge=0)] = 0
    skipped: Annotated[int, Field(ge=0)] = 0

    @model_validator(mode="after")
    def validate_total(self) -> TestCounts:
        total = self.passed + self.failed + self.errors + self.skipped
        if total != self.collected:
            raise ValueError(f"test status total {total} != collected {self.collected}")
        return self


class CollectionError(RecordModel):
    nodeid: str
    message: str


class CollectionReport(RecordModel):
    collected: Annotated[int, Field(ge=0)]
    nodeids: tuple[str, ...] = ()
    collection_errors: tuple[CollectionError, ...] = ()

    @model_validator(mode="after")
    def validate_nodeids(self) -> CollectionReport:
        if self.nodeids and len(self.nodeids) != self.collected:
            raise ValueError("collection nodeid count does not match collected")
        if len(set(self.nodeids)) != len(self.nodeids):
            raise ValueError("collection nodeids must be unique")
        return self


class GradingResult(RecordModel):
    metric_contract: str
    valid: bool
    reward: Annotated[float, Field(ge=0.0, le=1.0)]
    expected_total: Annotated[int, Field(gt=0)]
    counts: TestCounts
    collection: CollectionReport | None = None
    pytest_exit_code: int | None = None
    failure_class: FailureClass | None = None
    failure_reason: VerificationReason | None = None
    details: tuple[str, ...] = ()
