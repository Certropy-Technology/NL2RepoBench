"""The single fixed-denominator evaluator for normalized leaf reports."""

from __future__ import annotations

from typing import Any, Self

from pydantic import Field, model_validator

from nl2repobench.domain.models import FailureClass, RecordModel

from .leaf_report import LeafReport
from .metric_contract import MetricContract
from .taxonomy import VerificationReason

CURRENT_CONTRACT_ID = "fixed-test-pass-rate-v1"

MODEL_FAILURES = frozenset(
    {
        VerificationReason.CANDIDATE_WORKSPACE_REJECTED,
        VerificationReason.CANDIDATE_INSTALLATION_FAILED,
        VerificationReason.CANDIDATE_CALL_FAILED,
        VerificationReason.CANDIDATE_TIMEOUT,
        VerificationReason.SETUP_COMMAND_FAILED,
    }
)


class LeafCounts(RecordModel):
    """Counts derived from individual canonical leaves, never aggregates."""

    collected: int = Field(ge=0)
    passed: int = Field(ge=0, default=0)
    failed: int = Field(ge=0, default=0)
    errors: int = Field(ge=0, default=0)
    skipped: int = Field(ge=0, default=0)
    todo: int = Field(ge=0, default=0)
    xfail: int = Field(ge=0, default=0)

    @model_validator(mode="after")
    def validate_total(self) -> Self:
        total = self.passed + self.failed + self.errors + self.skipped + self.todo + self.xfail
        if total != self.collected:
            raise ValueError(f"leaf status total {total} != collected {self.collected}")
        return self


class EvaluationResult(RecordModel):
    """Canonical reward and classification emitted by the evaluator."""

    metric_contract: str
    valid: bool
    reward: float = Field(ge=0.0, le=1.0)
    frozen_total: int = Field(gt=0)
    counts: LeafCounts
    report: LeafReport | None = None
    runner_exit_code: int | None = None
    failure_class: FailureClass | None = None
    failure_reason: VerificationReason | None = None
    details: tuple[str, ...] = ()


def metric_contract_from_legacy(value: MetricContract | str | Any) -> MetricContract:
    """Convert old string or Node-v2 contracts into the current object.

    This is an input migration boundary only. The evaluator itself receives a
    ``MetricContract`` instance and never dispatches on report framework names.
    The old Node contract ID is deliberately mapped to the current metric ID;
    it is not emitted as a new score family.
    """

    if isinstance(value, MetricContract):
        return value
    if isinstance(value, str):
        if value in {CURRENT_CONTRACT_ID, "node-test-leaf-pass-rate-v1"}:
            return MetricContract()
        raise ValueError(f"unsupported metric contract: {value}")

    try:
        contract_id = value.contract_id
        if contract_id not in {CURRENT_CONTRACT_ID, "node-test-leaf-pass-rate-v1"}:
            raise ValueError(f"unsupported metric contract: {contract_id}")
        excluded = tuple(getattr(value, "excluded_statuses", ()))
        if excluded:
            raise ValueError(
                "legacy excluded_statuses cannot enter the current fixed-denominator evaluator"
            )
        return MetricContract(
            passed_statuses=tuple(value.passed_statuses),
            denominator_statuses=tuple(
                getattr(
                    value,
                    "denominator_statuses",
                    ("passed", "failed", "error", "skipped", "todo", "xfail"),
                )
            ),
            collection_mismatch=value.collection_mismatch,
        )
    except (AttributeError, TypeError, ValueError) as exc:
        raise TypeError("metric contract must be a MetricContract object") from exc


def _counts(report: LeafReport) -> LeafCounts:
    values = {
        "passed": 0,
        "failed": 0,
        "error": 0,
        "skipped": 0,
        "todo": 0,
        "xfail": 0,
    }
    for leaf in report.leaves:
        values[leaf.status] += 1
    return LeafCounts(
        collected=report.collected,
        passed=values["passed"],
        failed=values["failed"],
        errors=values["error"],
        skipped=values["skipped"],
        todo=values["todo"],
        xfail=values["xfail"],
    )


def _failure(
    *,
    contract: MetricContract,
    report: LeafReport | None,
    counts: LeafCounts,
    reason: VerificationReason,
    runner_exit_code: int | None,
    details: tuple[str, ...] = (),
) -> EvaluationResult:
    model_failure = reason in MODEL_FAILURES
    return EvaluationResult(
        metric_contract=contract.contract_id,
        valid=model_failure,
        reward=0.0,
        frozen_total=report.frozen_total if report is not None else 1,
        counts=counts,
        report=report,
        runner_exit_code=runner_exit_code,
        failure_class=FailureClass.MODEL if model_failure else FailureClass.VERIFIER,
        failure_reason=reason,
        details=details,
    )


def evaluate_leaf_report(report: LeafReport, contract: MetricContract) -> EvaluationResult:
    """Evaluate one normalized report under an explicit metric contract."""

    counts = _counts(report)
    if contract.contract_id != CURRENT_CONTRACT_ID:
        return _failure(
            contract=contract,
            report=report,
            counts=counts,
            reason=VerificationReason.VERIFIER_INTERNAL_ERROR,
            runner_exit_code=report.trusted_runner_exit_code,
            details=(f"unsupported metric contract: {contract.contract_id}",),
        )
    if (
        report.trusted_runner_exit_code is not None
        and report.trusted_runner_exit_code not in {0, 1}
    ):
        return _failure(
            contract=contract,
            report=report,
            counts=counts,
            reason=VerificationReason.RUNNER_ABNORMAL_EXIT,
            runner_exit_code=report.trusted_runner_exit_code,
        )
    if report.collection_errors:
        return _failure(
            contract=contract,
            report=report,
            counts=counts,
            reason=VerificationReason.COLLECTION_ERROR,
            runner_exit_code=report.trusted_runner_exit_code,
            details=tuple(error.message for error in report.collection_errors),
        )
    if report.collected != report.frozen_total and contract.collection_mismatch == "fail":
        return _failure(
            contract=contract,
            report=report,
            counts=counts,
            reason=VerificationReason.COLLECTION_MISMATCH,
            runner_exit_code=report.trusted_runner_exit_code,
            details=(f"collected {report.collected}, expected {report.frozen_total}",),
        )
    unsupported = sorted(
        {leaf.status for leaf in report.leaves if leaf.status not in contract.denominator_statuses}
    )
    if unsupported:
        return _failure(
            contract=contract,
            report=report,
            counts=counts,
            reason=VerificationReason.REPORT_COUNT_MISMATCH,
            runner_exit_code=report.trusted_runner_exit_code,
            details=("statuses outside denominator: " + ", ".join(unsupported),),
        )
    expected_exit = 1 if counts.failed or counts.errors else 0
    if (
        report.trusted_runner_exit_code is not None
        and report.trusted_runner_exit_code != expected_exit
    ):
        return _failure(
            contract=contract,
            report=report,
            counts=counts,
            reason=VerificationReason.REPORT_EXIT_MISMATCH,
            runner_exit_code=report.trusted_runner_exit_code,
            details=(
                f"runner exited {report.trusted_runner_exit_code}, but leaf statuses require "
                f"{expected_exit}",
            ),
        )
    passed = sum(
        1 for leaf in report.leaves if leaf.status in contract.passed_statuses
    )
    reward = max(0.0, min(passed / report.frozen_total, 1.0))
    return EvaluationResult(
        metric_contract=contract.contract_id,
        valid=True,
        reward=reward,
        frozen_total=report.frozen_total,
        counts=counts,
        report=report,
        runner_exit_code=report.trusted_runner_exit_code,
    )


def failure_result_for_reason(
    *,
    contract: MetricContract,
    expected_total: int,
    reason: VerificationReason,
    runner_exit_code: int | None = None,
    details: tuple[str, ...] = (),
) -> EvaluationResult:
    """Build a canonical result for setup/model failures before normalization."""

    if expected_total <= 0:
        raise ValueError("expected_total must be positive")
    counts = LeafCounts(collected=0)
    return EvaluationResult(
        metric_contract=contract.contract_id,
        valid=reason in MODEL_FAILURES,
        reward=0.0,
        frozen_total=expected_total,
        counts=counts,
        runner_exit_code=runner_exit_code,
        failure_class=FailureClass.MODEL if reason in MODEL_FAILURES else FailureClass.VERIFIER,
        failure_reason=reason,
        details=details,
    )


__all__ = [
    "CURRENT_CONTRACT_ID",
    "EvaluationResult",
    "LeafCounts",
    "MODEL_FAILURES",
    "evaluate_leaf_report",
    "failure_result_for_reason",
    "metric_contract_from_legacy",
]
