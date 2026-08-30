"""Compatibility wrapper around the runtime-neutral leaf evaluator."""

from __future__ import annotations

import json
from pathlib import Path

from nl2repobench.domain.canonical import canonical_json

from .evaluator import (
    EvaluationResult,
    canonical_metric_contract,
    evaluate_leaf_report,
    failure_result_for_reason,
)
from .leaf_report import ReportNormalizationError
from .metric_contract import MetricContract
from .models import (
    CollectionError,
    CollectionReport,
    GradingResult,
    TestCounts,
)
from .models import (
    VerificationReason as LegacyVerificationReason,
)
from .normalize.pytest_junit import normalize_pytest_junit
from .taxonomy import VerificationReason, canonical_reason, legacy_python_reason

ZERO_COUNTS = TestCounts()


def _as_legacy_result(result: EvaluationResult) -> GradingResult:
    counts = TestCounts(
        collected=result.counts.collected,
        passed=result.counts.passed,
        failed=result.counts.failed,
        errors=result.counts.errors,
        # v1 has no separate todo/xfail fields. Both are non-passed leaves.
        skipped=result.counts.skipped + result.counts.todo + result.counts.xfail,
    )
    collection = None
    if result.report is not None:
        collection = CollectionReport(
            collected=result.report.collected,
            nodeids=tuple(leaf.leaf_id for leaf in result.report.leaves),
            collection_errors=tuple(
                CollectionError(
                    nodeid=error.leaf_id or "<collection>",
                    message=error.message,
                )
                for error in result.report.collection_errors
            ),
        )
    return GradingResult(
        metric_contract=result.metric_contract,
        valid=result.valid,
        reward=result.reward,
        expected_total=result.frozen_total,
        counts=counts,
        collection=collection,
        pytest_exit_code=result.runner_exit_code,
        failure_class=result.failure_class,
        failure_reason=(
            legacy_python_reason(result.failure_reason)
            if result.failure_reason is not None
            else None
        ),
        details=result.details,
    )


def _failure_result(
    *,
    expected_total: int,
    metric_contract: MetricContract,
    reason: VerificationReason,
    pytest_exit_code: int | None = None,
    details: tuple[str, ...] = (),
) -> GradingResult:
    return _as_legacy_result(
        failure_result_for_reason(
            contract=metric_contract,
            expected_total=expected_total,
            reason=reason,
            runner_exit_code=pytest_exit_code,
            details=details,
        )
    )


def grade_verification(
    *,
    expected_total: int,
    metric_contract: MetricContract | str = "fixed-test-pass-rate-v1",
    junit_data: bytes | None,
    collection_data: bytes | None,
    pytest_exit_code: int | None,
    explicit_reason: VerificationReason | None = None,
) -> GradingResult:
    """Grade pytest output through the common evaluator.

    ``metric_contract`` accepts a legacy string only at this compatibility
    boundary. The evaluator receives a validated ``MetricContract`` object.
    """

    if expected_total <= 0:
        raise ValueError("expected_total must be positive")
    contract = canonical_metric_contract(metric_contract)
    if explicit_reason is not None:
        explicit_reason = canonical_reason(explicit_reason)
        return _failure_result(
            expected_total=expected_total,
            metric_contract=contract,
            reason=explicit_reason,
            pytest_exit_code=pytest_exit_code,
        )
    if pytest_exit_code is not None and pytest_exit_code not in {0, 1}:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=contract,
            reason=VerificationReason.RUNNER_ABNORMAL_EXIT,
            pytest_exit_code=pytest_exit_code,
        )
    if junit_data is None and collection_data is not None:
        result = _failure_result(
            expected_total=expected_total,
            metric_contract=contract,
            reason=VerificationReason.REPORT_MISSING,
            pytest_exit_code=pytest_exit_code,
        )
        return result.model_copy(update={"failure_reason": LegacyVerificationReason.JUNIT_MISSING})
    try:
        report = normalize_pytest_junit(
            junit_data=junit_data,
            collection_data=collection_data,
            frozen_total=expected_total,
            trusted_runner_exit_code=pytest_exit_code,
        )
    except ReportNormalizationError as exc:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=contract,
            reason=exc.reason,
            pytest_exit_code=pytest_exit_code,
            details=exc.details,
        )
    return _as_legacy_result(evaluate_leaf_report(report, contract))


def write_grading_outputs(result: GradingResult, output_dir: Path) -> None:
    """Write Harbor numeric rewards separately from detailed grading metadata."""

    output_dir.mkdir(parents=True, exist_ok=True)
    reward = {"reward": result.reward, "test_pass_rate": result.reward}
    (output_dir / "reward.json").write_text(
        json.dumps(reward, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "grading.json").write_bytes(canonical_json(result) + b"\n")


__all__ = ["grade_verification", "write_grading_outputs"]
