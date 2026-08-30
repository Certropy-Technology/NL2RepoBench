"""Python report adapter delegating to the canonical evaluator."""

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
from .normalize.pytest_junit import normalize_pytest_junit
from .taxonomy import VerificationReason


def grade_verification(
    *,
    expected_total: int,
    metric_contract: MetricContract | str = "fixed-test-pass-rate-v1",
    junit_data: bytes | None,
    collection_data: bytes | None,
    pytest_exit_code: int | None,
    explicit_reason: VerificationReason | None = None,
) -> EvaluationResult:
    """Grade pytest output into the canonical evaluation result."""

    if expected_total <= 0:
        raise ValueError("expected_total must be positive")
    contract = canonical_metric_contract(metric_contract)
    if explicit_reason is not None:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=explicit_reason,
            runner_exit_code=pytest_exit_code,
        )
    if pytest_exit_code is not None and pytest_exit_code not in {0, 1}:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=VerificationReason.RUNNER_ABNORMAL_EXIT,
            runner_exit_code=pytest_exit_code,
        )
    try:
        report = normalize_pytest_junit(
            junit_data=junit_data,
            collection_data=collection_data,
            frozen_total=expected_total,
            trusted_runner_exit_code=pytest_exit_code,
        )
    except ReportNormalizationError as exc:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=exc.reason,
            runner_exit_code=pytest_exit_code,
            details=exc.details,
        )
    return evaluate_leaf_report(report, contract)


def write_grading_outputs(result: EvaluationResult, output_dir: Path) -> None:
    """Write verifier-owned canonical grading and numeric reward outputs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    reward = {"reward": result.reward, "test_pass_rate": result.reward}
    (output_dir / "reward.json").write_text(
        json.dumps(reward, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "grading.json").write_bytes(canonical_json(result) + b"\n")


__all__ = ["grade_verification", "write_grading_outputs"]
