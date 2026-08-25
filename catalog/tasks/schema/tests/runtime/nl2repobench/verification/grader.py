"""Fixed-denominator grading and machine-readable verifier outputs."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.models import FailureClass

from .junit import JUnitError, parse_junit
from .models import CollectionReport, GradingResult, TestCounts, VerificationReason

ZERO_COUNTS = TestCounts()
MODEL_FAILURES = {
    VerificationReason.CANDIDATE_WORKSPACE_REJECTED,
    VerificationReason.CANDIDATE_INSTALLATION_FAILED,
    VerificationReason.SETUP_COMMAND_FAILED,
}


def _failure_result(
    *,
    expected_total: int,
    metric_contract: str,
    reason: VerificationReason,
    counts: TestCounts = ZERO_COUNTS,
    collection: CollectionReport | None = None,
    pytest_exit_code: int | None = None,
    details: tuple[str, ...] = (),
) -> GradingResult:
    model_failure = reason in MODEL_FAILURES
    return GradingResult(
        metric_contract=metric_contract,
        valid=model_failure,
        reward=0.0,
        expected_total=expected_total,
        counts=counts,
        collection=collection,
        pytest_exit_code=pytest_exit_code,
        failure_class=FailureClass.MODEL if model_failure else FailureClass.VERIFIER,
        failure_reason=reason,
        details=details,
    )


def grade_verification(
    *,
    expected_total: int,
    metric_contract: str = "fixed-test-pass-rate-v1",
    junit_data: bytes | None,
    collection_data: bytes | None,
    pytest_exit_code: int | None,
    explicit_reason: VerificationReason | None = None,
) -> GradingResult:
    """Grade one verifier run without parsing human console output."""

    if expected_total <= 0:
        raise ValueError("expected_total must be positive")
    if explicit_reason is not None:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=explicit_reason,
            pytest_exit_code=pytest_exit_code,
        )
    if pytest_exit_code is not None and pytest_exit_code not in {0, 1}:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.PYTEST_ABNORMAL_EXIT,
            pytest_exit_code=pytest_exit_code,
        )
    if collection_data is None:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.COLLECTION_REPORT_MISSING,
            pytest_exit_code=pytest_exit_code,
        )
    try:
        collection = CollectionReport.model_validate_json(collection_data)
    except (ValidationError, ValueError) as exc:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.COLLECTION_REPORT_MALFORMED,
            pytest_exit_code=pytest_exit_code,
            details=(str(exc),),
        )
    if junit_data is None:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.JUNIT_MISSING,
            collection=collection,
            pytest_exit_code=pytest_exit_code,
        )
    try:
        counts = parse_junit(junit_data)
    except JUnitError as exc:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.JUNIT_MALFORMED,
            collection=collection,
            pytest_exit_code=pytest_exit_code,
            details=(str(exc),),
        )

    if collection.collection_errors:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.COLLECTION_ERROR,
            counts=counts,
            collection=collection,
            pytest_exit_code=pytest_exit_code,
            details=tuple(error.message for error in collection.collection_errors),
        )
    if collection.collected != expected_total:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.COLLECTION_MISMATCH,
            counts=counts,
            collection=collection,
            pytest_exit_code=pytest_exit_code,
            details=(f"collected {collection.collected}, expected {expected_total}",),
        )
    if counts.collected != expected_total:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.JUNIT_COUNT_MISMATCH,
            counts=counts,
            collection=collection,
            pytest_exit_code=pytest_exit_code,
            details=(f"JUnit has {counts.collected}, expected {expected_total}",),
        )
    expected_exit_code = 1 if counts.failed or counts.errors else 0
    if pytest_exit_code is not None and pytest_exit_code != expected_exit_code:
        return _failure_result(
            expected_total=expected_total,
            metric_contract=metric_contract,
            reason=VerificationReason.PYTEST_REPORT_MISMATCH,
            counts=counts,
            collection=collection,
            pytest_exit_code=pytest_exit_code,
            details=(
                f"pytest exited {pytest_exit_code}, but JUnit statuses require "
                f"{expected_exit_code}",
            ),
        )
    reward = max(0.0, min(counts.passed / expected_total, 1.0))
    return GradingResult(
        metric_contract=metric_contract,
        valid=True,
        reward=reward,
        expected_total=expected_total,
        counts=counts,
        collection=collection,
        pytest_exit_code=pytest_exit_code,
    )


def write_grading_outputs(result: GradingResult, output_dir: Path) -> None:
    """Write Harbor numeric rewards separately from detailed grading metadata."""

    output_dir.mkdir(parents=True, exist_ok=True)
    reward = {"reward": result.reward, "test_pass_rate": result.reward}
    (output_dir / "reward.json").write_text(
        json.dumps(reward, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "grading.json").write_bytes(canonical_json(result) + b"\n")
