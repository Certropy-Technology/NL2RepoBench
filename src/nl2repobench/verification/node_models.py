"""v2 verifier contracts for verifier-owned Node test reports."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from nl2repobench.domain.models import FailureClass
from nl2repobench.domain.models_v2 import V2RecordModel

NodeTestStatus = Literal["passed", "failed", "error", "skipped", "todo"]


class NodeVerificationReason(StrEnum):
    """Failure reasons kept separate from the v1 pytest/JUnit enum."""

    REPORT_MISSING = "node-report-missing"
    REPORT_MALFORMED = "node-report-malformed"
    DUPLICATE_TEST_ID = "node-duplicate-test-id"
    COLLECTION_ERROR = "node-collection-error"
    COLLECTION_MISMATCH = "node-collection-mismatch"
    REPORT_COUNT_MISMATCH = "node-report-count-mismatch"
    RUNNER_ABNORMAL_EXIT = "node-runner-abnormal-exit"
    REPORT_EXIT_MISMATCH = "node-report-exit-mismatch"
    CANDIDATE_WORKSPACE_REJECTED = "candidate-workspace-rejected"
    CANDIDATE_INSTALLATION_FAILED = "candidate-installation-failed"
    CANDIDATE_CALL_FAILED = "candidate-call-failed"
    VERIFIER_NETWORK_AVAILABLE = "verifier-network-available"
    VERIFIER_INTERNAL_ERROR = "verifier-internal-error"
    INTEGRITY_FAILURE = "integrity-failure"

    # Descriptive aliases support callers that use the longer v2 names.
    NODE_REPORT_MISSING = REPORT_MISSING
    NODE_REPORT_MALFORMED = REPORT_MALFORMED
    NODE_DUPLICATE_TEST_ID = DUPLICATE_TEST_ID
    NODE_COLLECTION_ERROR = COLLECTION_ERROR
    NODE_COLLECTION_MISMATCH = COLLECTION_MISMATCH
    NODE_REPORT_COUNT_MISMATCH = REPORT_COUNT_MISMATCH
    NODE_RUNNER_ABNORMAL_EXIT = RUNNER_ABNORMAL_EXIT
    NODE_REPORT_EXIT_MISMATCH = REPORT_EXIT_MISMATCH


class NodeTestCaseV2(V2RecordModel):
    """One frozen leaf test result; aggregate reporter fields are ignored."""

    test_id: Annotated[str, Field(min_length=1, max_length=512)]
    status: NodeTestStatus
    duration_ms: Annotated[float, Field(ge=0)] = 0.0
    details: str | None = None


class NodeCollectionErrorV2(V2RecordModel):
    """A trusted runner collection failure that invalidates the result."""

    message: Annotated[str, Field(min_length=1, max_length=4096)]
    test_id: str | None = None


class NodeTestReportV2(V2RecordModel):
    """Verifier-owned JSON report for a ``node:test`` run."""

    framework: Literal["node:test"] = "node:test"
    report_format: Literal["node-test-json-v1"] = "node-test-json-v1"
    collected: Annotated[int, Field(ge=0)]
    tests: tuple[NodeTestCaseV2, ...] = ()
    collection_errors: tuple[NodeCollectionErrorV2, ...] = ()
    runner_exit_code: int

    @model_validator(mode="after")
    def validate_leaf_collection(self) -> NodeTestReportV2:
        if len(self.tests) != self.collected:
            raise ValueError("node report test count does not match collected")
        test_ids = [case.test_id for case in self.tests]
        if len(set(test_ids)) != len(test_ids):
            raise ValueError("node report test IDs must be unique")
        return self


class NodeTestCountsV2(V2RecordModel):
    """Counts derived solely from individual leaf cases."""

    collected: Annotated[int, Field(ge=0)] = 0
    passed: Annotated[int, Field(ge=0)] = 0
    failed: Annotated[int, Field(ge=0)] = 0
    errors: Annotated[int, Field(ge=0)] = 0
    skipped: Annotated[int, Field(ge=0)] = 0
    todo: Annotated[int, Field(ge=0)] = 0

    @model_validator(mode="after")
    def validate_total(self) -> NodeTestCountsV2:
        total = self.passed + self.failed + self.errors + self.skipped + self.todo
        if total != self.collected:
            raise ValueError(f"node status total {total} != collected {self.collected}")
        return self


class NodeGradingResultV2(V2RecordModel):
    """Canonical reward and verifier classification for a Node run."""

    metric_contract: str = "node-test-leaf-pass-rate-v1"
    valid: bool
    reward: Annotated[float, Field(ge=0.0, le=1.0)]
    expected_total: Annotated[int, Field(gt=0)]
    counts: NodeTestCountsV2
    report: NodeTestReportV2 | None = None
    runner_exit_code: int | None = None
    failure_class: FailureClass | None = None
    failure_reason: NodeVerificationReason | None = None
    details: tuple[str, ...] = ()
