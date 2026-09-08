"""Rust bridge report adapter delegating scoring to the shared evaluator."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from .evaluator import (
    EvaluationResult,
    evaluate_leaf_report,
    failure_result_for_reason,
    metric_contract_from_legacy,
)
from .leaf_report import LeafCase, LeafReport, ReportNormalizationError
from .metric_contract import MetricContract
from .normalize.rust_bridge_json import normalize_rust_bridge_json
from .taxonomy import VerificationReason, canonical_reason


def grade_rust_test_exit(
    *,
    expected_total: int,
    runner_exit_code: int | None,
    metric_contract: MetricContract | str = "fixed-test-pass-rate-v1",
    explicit_reason: VerificationReason | None = None,
) -> EvaluationResult:
    contract = metric_contract_from_legacy(metric_contract)
    if explicit_reason is not None:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=canonical_reason(explicit_reason),
            runner_exit_code=runner_exit_code,
        )
    if runner_exit_code not in {0, 1}:
        return failure_result_for_reason(
            contract=contract,
            expected_total=expected_total,
            reason=VerificationReason.RUNNER_ABNORMAL_EXIT,
            runner_exit_code=runner_exit_code,
        )
    status: Literal["passed", "failed"] = "passed" if runner_exit_code == 0 else "failed"
    report = LeafReport(
        framework="rust",
        report_format="rust-cargo-test-exit-v1",
        collected=expected_total,
        leaves=tuple(
            LeafCase(leaf_id=f"cargo.leaf.{index}", status=status)
            for index in range(expected_total)
        ),
        trusted_runner_exit_code=runner_exit_code,
        frozen_total=expected_total,
    )
    return evaluate_leaf_report(report, contract)


def grade_rust_report(
    *,
    expected_total: int,
    report_data: bytes | Mapping[str, object] | None,
    runner_exit_code: int | None,
    metric_contract: MetricContract | str = "fixed-test-pass-rate-v1",
    explicit_reason: VerificationReason | None = None,
) -> EvaluationResult:
    """Normalize one native Rust bridge report and apply the fixed metric."""

    contract = metric_contract_from_legacy(metric_contract)
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
        report = normalize_rust_bridge_json(
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


def write_rust_grading_outputs(result: EvaluationResult, output_dir: Path) -> None:
    """Write verifier-owned Rust grading and reward records."""

    from nl2repobench.domain.canonical import canonical_json

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "reward.json").write_text(
        json.dumps({"reward": result.reward, "test_pass_rate": result.reward}, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "grading.json").write_bytes(canonical_json(result) + b"\n")


__all__ = [
    "grade_rust_report",
    "grade_rust_test_exit",
    "write_rust_grading_outputs",
]
