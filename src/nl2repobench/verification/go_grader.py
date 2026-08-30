"""Go report adapter delegating scoring to the canonical evaluator."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nl2repobench.domain.canonical import canonical_json

from .evaluator import (
    EvaluationResult,
    canonical_metric_contract,
    evaluate_leaf_report,
    failure_result_for_reason,
)
from .leaf_report import ReportNormalizationError
from .metric_contract import MetricContract
from .normalize.go_json import MAX_GO_REPORT_BYTES, normalize_go_json
from .taxonomy import VerificationReason, canonical_reason


def grade_go_report(
    *,
    expected_total: int,
    report_data: bytes | Mapping[str, Any] | None,
    runner_exit_code: int | None = None,
    metric_contract: MetricContract | str = "fixed-test-pass-rate-v1",
    explicit_reason: VerificationReason | None = None,
) -> EvaluationResult:
    contract = canonical_metric_contract(metric_contract)
    if explicit_reason is not None:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=canonical_reason(explicit_reason),
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
        report = normalize_go_json(
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


def write_go_grading_outputs(result: EvaluationResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "reward.json").write_text(
        json.dumps(
            {"reward": result.reward, "test_pass_rate": result.reward}, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "grading.json").write_bytes(canonical_json(result) + b"\n")


__all__ = ["MAX_GO_REPORT_BYTES", "grade_go_report", "write_go_grading_outputs"]
