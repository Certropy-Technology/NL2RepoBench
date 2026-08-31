"""Java report adapter delegating scoring to the canonical evaluator."""

from __future__ import annotations

from nl2repobench.verification.evaluator import (
    EvaluationResult,
    canonical_metric_contract,
    evaluate_leaf_report,
    failure_result_for_reason,
)
from nl2repobench.verification.leaf_report import ReportNormalizationError
from nl2repobench.verification.metric_contract import MetricContract
from nl2repobench.verification.normalize.junit_open_test_report import (
    normalize_junit_open_test_report,
)
from nl2repobench.verification.taxonomy import VerificationReason


def grade_java_report(
    *,
    expected_total: int,
    report_data: bytes | None,
    runner_exit_code: int | None = None,
    metric_contract: MetricContract | str = "fixed-test-pass-rate-v1",
    explicit_reason: VerificationReason | None = None,
) -> EvaluationResult:
    contract = canonical_metric_contract(metric_contract)
    if isinstance(expected_total, bool) or expected_total <= 0:
        return failure_result_for_reason(
            contract=contract,
            expected_total=1,
            reason=VerificationReason.REPORT_MALFORMED,
            runner_exit_code=runner_exit_code,
            details=(f"expected_total must be positive (got {expected_total!r})",),
        )
    if explicit_reason is not None:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=explicit_reason,
            runner_exit_code=runner_exit_code,
        )
    if runner_exit_code is not None and runner_exit_code not in {0, 1}:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=VerificationReason.RUNNER_ABNORMAL_EXIT,
            runner_exit_code=runner_exit_code,
        )
    try:
        report = normalize_junit_open_test_report(
            report_data=report_data,
            frozen_total=expected_total,
            trusted_runner_exit_code=runner_exit_code,
        )
    except ReportNormalizationError as exc:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=exc.reason,
            runner_exit_code=runner_exit_code,
            details=exc.details,
        )
    return evaluate_leaf_report(report, contract)


__all__ = ["grade_java_report"]
