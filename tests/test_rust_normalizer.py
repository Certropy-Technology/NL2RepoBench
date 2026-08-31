from __future__ import annotations

import pytest

from nl2repobench.domain.canonical_models import FailureClass
from nl2repobench.verification.evaluator import (
    CURRENT_CONTRACT_ID,
    canonical_metric_contract,
    evaluate_leaf_report,
)
from nl2repobench.verification.leaf_report import ReportNormalizationError
from nl2repobench.verification.normalize.rust_bridge_json import (
    normalize_rust_bridge_json,
)
from nl2repobench.verification.taxonomy import VerificationReason


def _report(*, status: str = "passed", errors: list[dict[str, object]] | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "framework": "rust-harness",
        "report_format": "rust-bridge-json-v1",
        "collected": 1,
        "leaves": [
            {
                "leaf_id": "leaf.one",
                "status": status,
                "duration_ms": 1.0,
                "details": "ok",
            }
        ],
        "collection_errors": errors or [],
        "runner_exit_code": 0 if status == "passed" and not errors else 1,
    }


def test_rust_report_normalizes_to_unchanged_leaf_report_and_metric() -> None:
    report = normalize_rust_bridge_json(
        report_data=_report(), frozen_total=1, trusted_runner_exit_code=0
    )

    assert set(type(report).model_fields) == {
        "schema_version",
        "framework",
        "report_format",
        "collected",
        "leaves",
        "collection_errors",
        "trusted_runner_exit_code",
        "frozen_total",
    }
    result = evaluate_leaf_report(report, canonical_metric_contract(CURRENT_CONTRACT_ID))
    assert result.valid is True
    assert result.reward == 1.0


def test_rust_trusted_transport_failure_stays_verifier_invalid() -> None:
    report = normalize_rust_bridge_json(
        report_data=_report(
            status="error",
            errors=[{"message": "trusted-transport-schema:bad line", "leaf_id": None}],
        ),
        frozen_total=1,
        trusted_runner_exit_code=1,
    )

    result = evaluate_leaf_report(report, canonical_metric_contract(CURRENT_CONTRACT_ID))
    assert result.valid is False
    assert result.failure_class is FailureClass.VERIFIER
    assert result.failure_reason is VerificationReason.COLLECTION_ERROR
    assert result.reward == 0.0


def test_rust_candidate_failure_keeps_fixed_denominator_valid() -> None:
    payload = _report(status="failed")
    payload["leaves"][0]["details"] = "candidate-call-failed:panic"
    report = normalize_rust_bridge_json(
        report_data=payload, frozen_total=1, trusted_runner_exit_code=1
    )

    result = evaluate_leaf_report(report, canonical_metric_contract(CURRENT_CONTRACT_ID))
    assert result.valid is True
    assert result.reward == 0.0
    assert result.failure_class is None


def test_rust_report_rejects_exit_count_and_extra_field_drift() -> None:
    with pytest.raises(ReportNormalizationError) as exit_mismatch:
        normalize_rust_bridge_json(
            report_data=_report(), frozen_total=1, trusted_runner_exit_code=1
        )
    assert exit_mismatch.value.reason is VerificationReason.REPORT_EXIT_MISMATCH

    payload = _report()
    payload["collected"] = 2
    with pytest.raises(ReportNormalizationError) as count_mismatch:
        normalize_rust_bridge_json(
            report_data=payload, frozen_total=2, trusted_runner_exit_code=0
        )
    assert count_mismatch.value.reason is VerificationReason.REPORT_COUNT_MISMATCH

    payload = _report()
    payload["valid"] = True
    with pytest.raises(ReportNormalizationError, match="fields"):
        normalize_rust_bridge_json(
            report_data=payload, frozen_total=1, trusted_runner_exit_code=0
        )
