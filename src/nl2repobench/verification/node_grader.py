"""Fixed-denominator grading for verifier-owned Node test reports."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.models import FailureClass

from .node_models import (
    NodeGradingResultV2,
    NodeTestCountsV2,
    NodeTestReportV2,
    NodeTestStatus,
    NodeVerificationReason,
)

MAX_NODE_REPORT_BYTES = 8 * 1024 * 1024
NODE_MODEL_FAILURES = {
    NodeVerificationReason.CANDIDATE_WORKSPACE_REJECTED,
    NodeVerificationReason.CANDIDATE_INSTALLATION_FAILED,
    NodeVerificationReason.CANDIDATE_CALL_FAILED,
}


def _failure_result(
    *,
    expected_total: int,
    metric_contract: str,
    reason: NodeVerificationReason,
    counts: NodeTestCountsV2 | None = None,
    report: NodeTestReportV2 | None = None,
    runner_exit_code: int | None = None,
    details: tuple[str, ...] = (),
) -> NodeGradingResultV2:
    model_failure = reason in NODE_MODEL_FAILURES
    return NodeGradingResultV2(
        metric_contract=metric_contract,
        valid=model_failure,
        reward=0.0,
        expected_total=expected_total,
        counts=counts or NodeTestCountsV2(),
        report=report,
        runner_exit_code=runner_exit_code,
        failure_class=FailureClass.MODEL if model_failure else FailureClass.VERIFIER,
        failure_reason=reason,
        details=details,
    )


def _decode_report(
    report_data: bytes | Mapping[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    if isinstance(report_data, Mapping):
        payload: object = dict(report_data)
    else:
        if len(report_data) > MAX_NODE_REPORT_BYTES:
            return None, "node report exceeds the size limit"
        try:
            payload = json.loads(report_data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, f"invalid node report JSON: {exc}"
    if not isinstance(payload, dict):
        return None, "node report must be a JSON object"
    return payload, None


def _raw_count_mismatch(payload: Mapping[str, Any]) -> str | None:
    collected = payload.get("collected")
    tests = payload.get("tests")
    if isinstance(collected, bool) or not isinstance(collected, int) or collected < 0:
        return "collected must be a non-negative integer"
    if not isinstance(tests, list):
        return "tests must be a JSON array"
    if len(tests) != collected:
        return f"report has {len(tests)} tests, collected says {collected}"
    return None


def _duplicate_test_id(payload: Mapping[str, Any]) -> str | None:
    tests = payload.get("tests")
    if not isinstance(tests, list):
        return None
    seen: set[str] = set()
    for item in tests:
        if not isinstance(item, dict):
            continue
        test_id = item.get("test_id")
        if isinstance(test_id, str):
            if test_id in seen:
                return test_id
            seen.add(test_id)
    return None


def _counts(report: NodeTestReportV2) -> NodeTestCountsV2:
    values: dict[NodeTestStatus, int] = {
        "passed": 0,
        "failed": 0,
        "error": 0,
        "skipped": 0,
        "todo": 0,
    }
    for case in report.tests:
        values[case.status] += 1
    return NodeTestCountsV2(
        collected=report.collected,
        passed=values["passed"],
        failed=values["failed"],
        errors=values["error"],
        skipped=values["skipped"],
        todo=values["todo"],
    )


def grade_node_test_report(
    *,
    expected_total: int,
    report_data: bytes | Mapping[str, Any] | None,
    runner_exit_code: int | None = None,
    metric_contract: str = "node-test-leaf-pass-rate-v1",
    explicit_reason: NodeVerificationReason | None = None,
) -> NodeGradingResultV2:
    """Grade a Node report without trusting aggregate reporter fields."""

    if expected_total <= 0:
        raise ValueError("expected_total must be positive")
    if explicit_reason is not None:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=explicit_reason,
            runner_exit_code=runner_exit_code,
        )
    if runner_exit_code is not None and runner_exit_code not in {0, 1}:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.RUNNER_ABNORMAL_EXIT,
            runner_exit_code=runner_exit_code,
        )
    if report_data is None:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.REPORT_MISSING,
            runner_exit_code=runner_exit_code,
        )
    payload, decode_error = _decode_report(report_data)
    if payload is None:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.REPORT_MALFORMED,
            runner_exit_code=runner_exit_code,
            details=(decode_error or "invalid report",),
        )
    duplicate = _duplicate_test_id(payload)
    if duplicate is not None:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.DUPLICATE_TEST_ID,
            runner_exit_code=runner_exit_code,
            details=(f"duplicate test_id: {duplicate}",),
        )
    count_error = _raw_count_mismatch(payload)
    if count_error is not None:
        reason = (
            NodeVerificationReason.REPORT_COUNT_MISMATCH
            if count_error.startswith("report has")
            else NodeVerificationReason.REPORT_MALFORMED
        )
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=reason,
            runner_exit_code=runner_exit_code,
            details=(count_error,),
        )
    try:
        report = NodeTestReportV2.model_validate(payload)
    except (ValidationError, ValueError) as exc:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.REPORT_MALFORMED,
            runner_exit_code=runner_exit_code,
            details=(str(exc),),
        )
    effective_exit = report.runner_exit_code if runner_exit_code is None else runner_exit_code
    if runner_exit_code is not None and report.runner_exit_code != runner_exit_code:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.REPORT_EXIT_MISMATCH,
            report=report,
            runner_exit_code=runner_exit_code,
            details=(
                f"report runner_exit_code {report.runner_exit_code} != trusted exit "
                f"{runner_exit_code}",
            ),
        )
    if report.collection_errors:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.COLLECTION_ERROR,
            report=report,
            runner_exit_code=effective_exit,
            details=tuple(error.message for error in report.collection_errors),
        )
    if report.collected != expected_total:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.COLLECTION_MISMATCH,
            report=report,
            runner_exit_code=effective_exit,
            details=(f"collected {report.collected}, expected {expected_total}",),
        )
    counts = _counts(report)
    expected_exit = 1 if counts.failed or counts.errors else 0
    if effective_exit not in {0, 1}:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.RUNNER_ABNORMAL_EXIT,
            counts=counts,
            report=report,
            runner_exit_code=effective_exit,
        )
    if effective_exit != expected_exit:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=NodeVerificationReason.REPORT_EXIT_MISMATCH,
            counts=counts,
            report=report,
            runner_exit_code=effective_exit,
            details=(f"runner exited {effective_exit}, but leaf statuses require {expected_exit}",),
        )
    return NodeGradingResultV2(
        metric_contract=metric_contract,
        valid=True,
        reward=max(0.0, min(counts.passed / expected_total, 1.0)),
        expected_total=expected_total,
        counts=counts,
        report=report,
        runner_exit_code=effective_exit,
    )


def write_node_grading_outputs(result: NodeGradingResultV2, output_dir: Path) -> None:
    """Write Harbor's numeric reward and the canonical v2 grading record."""

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


# A concise alias is useful for callers that name the report rather than the
# framework in their integration code.
grade_node_report = grade_node_test_report
