"""Java report adapter delegating scoring to the shared evaluator."""

from __future__ import annotations

import json
from pathlib import Path

from nl2repobench.domain.canonical import canonical_json

from .evaluator import (
    EvaluationResult,
    evaluate_leaf_report,
    failure_result_for_reason,
    metric_contract_from_legacy,
)
from .leaf_report import ReportNormalizationError
from .metric_contract import MetricContract
from .models import GradingResult, TestCounts
from .models import VerificationReason as LegacyReason
from .normalize.junit_open_test_report import normalize_junit_open_test_report
from .taxonomy import VerificationReason


def grade_java_report(
    *,
    expected_total: int,
    report_data: bytes | None,
    runner_exit_code: int | None = None,
    metric_contract: MetricContract | str = "fixed-test-pass-rate-v1",
    explicit_reason: VerificationReason | None = None,
) -> EvaluationResult:
    """Normalize a trusted JUnit report and score it using the common metric."""

    contract = metric_contract_from_legacy(metric_contract)
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


def write_java_grading_outputs(result: EvaluationResult, output_dir: Path) -> None:
    """Write verifier-owned outputs in the same shape as Go and Node lanes."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "reward.json").write_text(
        json.dumps({"reward": result.reward, "test_pass_rate": result.reward}, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    failure_reason = None
    if result.failure_reason is not None:
        try:
            failure_reason = LegacyReason(result.failure_reason.value)
        except ValueError:
            # The current taxonomy is richer than the legacy report enum.
            pass
    grading = GradingResult(
        metric_contract=result.metric_contract,
        valid=result.valid,
        reward=result.reward,
        expected_total=result.frozen_total,
        counts=TestCounts(
            collected=result.counts.collected,
            passed=result.counts.passed,
            failed=result.counts.failed,
            errors=result.counts.errors,
            skipped=result.counts.skipped + result.counts.todo + result.counts.xfail,
        ),
        pytest_exit_code=result.runner_exit_code,
        failure_class=result.failure_class,
        failure_reason=failure_reason,
        details=result.details,
    )
    (output_dir / "grading.json").write_bytes(canonical_json(grading) + b"\n")


__all__ = ["grade_java_report", "write_java_grading_outputs"]
