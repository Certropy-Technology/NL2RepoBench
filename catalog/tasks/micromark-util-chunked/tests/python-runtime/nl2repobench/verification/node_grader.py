"""Compatibility wrapper for the common evaluator and Node report normalizer."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nl2repobench.domain.canonical import canonical_json

from .evaluator import (
    EvaluationResult,
    evaluate_leaf_report,
    failure_result_for_reason,
    metric_contract_from_legacy,
)
from .leaf_report import ReportNormalizationError
from .metric_contract import MetricContract
from .node_models import (
    NodeCollectionErrorV2,
    NodeGradingResultV2,
    NodeTestCaseV2,
    NodeTestCountsV2,
    NodeTestReportV2,
    NodeVerificationReason,
)
from .normalize.node_test_json import MAX_NODE_REPORT_BYTES, normalize_node_test_json
from .taxonomy import VerificationReason, canonical_reason, legacy_node_reason

NODE_MODEL_FAILURES = {
    NodeVerificationReason.CANDIDATE_WORKSPACE_REJECTED,
    NodeVerificationReason.CANDIDATE_INSTALLATION_FAILED,
    NodeVerificationReason.CANDIDATE_CALL_FAILED,
}


def _node_report(report: EvaluationResult) -> NodeTestReportV2 | None:
    if report.report is None:
        return None
    return NodeTestReportV2(
        collected=report.report.collected,
        tests=tuple(
            NodeTestCaseV2(
                test_id=leaf.leaf_id,
                status=leaf.status,  # type: ignore[arg-type]
                duration_ms=leaf.duration_ms,
                details=leaf.details,
            )
            for leaf in report.report.leaves
        ),
        collection_errors=tuple(
            NodeCollectionErrorV2(message=error.message, test_id=error.leaf_id)
            for error in report.report.collection_errors
        ),
        runner_exit_code=report.report.trusted_runner_exit_code or 0,
    )


def _as_node_result(
    result: EvaluationResult, *, metric_contract_id: str | None = None
) -> NodeGradingResultV2:
    return NodeGradingResultV2(
        metric_contract=metric_contract_id or result.metric_contract,
        valid=result.valid,
        reward=result.reward,
        expected_total=result.frozen_total,
        counts=NodeTestCountsV2(
            collected=result.counts.collected,
            passed=result.counts.passed,
            failed=result.counts.failed,
            errors=result.counts.errors,
            skipped=result.counts.skipped,
            todo=result.counts.todo + result.counts.xfail,
        ),
        report=_node_report(result),
        runner_exit_code=result.runner_exit_code,
        failure_class=result.failure_class,
        failure_reason=(
            legacy_node_reason(result.failure_reason)
            if result.failure_reason is not None
            else None
        ),
        details=result.details,
    )


def grade_node_test_report(
    *,
    expected_total: int,
    report_data: bytes | Mapping[str, Any] | None,
    runner_exit_code: int | None = None,
    metric_contract: MetricContract | str = "node-test-leaf-pass-rate-v1",
    explicit_reason: NodeVerificationReason | None = None,
) -> NodeGradingResultV2:
    """Grade Node JSON through the same evaluator used by pytest."""

    if expected_total <= 0:
        raise ValueError("expected_total must be positive")
    contract = metric_contract_from_legacy(metric_contract)

    def as_node_result(result: EvaluationResult) -> NodeGradingResultV2:
        requested_id = metric_contract if isinstance(metric_contract, str) else None
        return _as_node_result(result, metric_contract_id=requested_id)
    if explicit_reason is not None:
        canonical_explicit_reason = canonical_reason(explicit_reason)
        return as_node_result(
            failure_result_for_reason(
                contract=contract,
                expected_total=expected_total,
                reason=canonical_explicit_reason,
                runner_exit_code=runner_exit_code,
            )
        )
    if runner_exit_code is not None and runner_exit_code not in {0, 1}:
        return as_node_result(
            failure_result_for_reason(
                contract=contract,
                expected_total=expected_total,
                reason=VerificationReason.RUNNER_ABNORMAL_EXIT,
                runner_exit_code=runner_exit_code,
            )
        )
    try:
        report = normalize_node_test_json(
            report_data=report_data,
            frozen_total=expected_total,
            trusted_runner_exit_code=runner_exit_code,
        )
    except ReportNormalizationError as exc:
        return as_node_result(
            failure_result_for_reason(
                contract=contract,
                expected_total=expected_total,
                reason=exc.reason,
                runner_exit_code=runner_exit_code,
                details=exc.details,
            )
        )
    return as_node_result(evaluate_leaf_report(report, contract))


def write_node_grading_outputs(result: NodeGradingResultV2, output_dir: Path) -> None:
    """Write the numeric reward and canonical v2-shaped compatibility record."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "reward.json").write_text(
        json.dumps(
            {"reward": result.reward, "test_pass_rate": result.reward},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "grading.json").write_bytes(canonical_json(result) + b"\n")


__all__ = [
    "MAX_NODE_REPORT_BYTES",
    "grade_node_test_report",
    "write_node_grading_outputs",
]
