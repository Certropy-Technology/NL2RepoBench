"""Normalize verifier-owned ``node:test`` JSON into canonical leaves."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from nl2repobench.verification.leaf_report import (
    LeafCase,
    LeafCollectionError,
    LeafReport,
    ReportNormalizationError,
)
from nl2repobench.verification.taxonomy import VerificationReason

from ..node_models import NodeTestReport

MAX_NODE_REPORT_BYTES = 8 * 1024 * 1024


def _payload(data: bytes | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(data, Mapping):
        return dict(data)
    if len(data) > MAX_NODE_REPORT_BYTES:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED, "Node report exceeds the size limit"
        )
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED, f"invalid Node report JSON: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED, "Node report must be a JSON object"
        )
    return value


def normalize_node_test_json(
    *,
    report_data: bytes | Mapping[str, Any] | None,
    frozen_total: int,
    trusted_runner_exit_code: int | None,
) -> LeafReport:
    """Map Node report leaves without evaluating reward or failure class."""

    if frozen_total <= 0:
        raise ValueError("frozen_total must be positive")
    if report_data is None:
        raise ReportNormalizationError(VerificationReason.REPORT_MISSING, "Node report is missing")
    payload = _payload(report_data)
    tests = payload.get("tests")
    if isinstance(tests, list):
        seen: set[str] = set()
        for item in tests:
            if isinstance(item, dict) and isinstance(item.get("test_id"), str):
                test_id = item["test_id"]
                if test_id in seen:
                    raise ReportNormalizationError(
                        VerificationReason.DUPLICATE_LEAF_ID,
                        f"duplicate test_id: {test_id}",
                    )
                seen.add(test_id)
        collected = payload.get("collected")
        if (
            isinstance(collected, int)
            and not isinstance(collected, bool)
            and len(tests) != collected
        ):
            raise ReportNormalizationError(
                VerificationReason.REPORT_COUNT_MISMATCH,
                f"report has {len(tests)} tests, collected says {collected}",
            )
    try:
        report = NodeTestReport.model_validate(payload)
    except (ValidationError, ValueError) as exc:
        raise ReportNormalizationError(VerificationReason.REPORT_MALFORMED, str(exc)) from exc
    effective_exit = report.runner_exit_code
    if trusted_runner_exit_code is not None:
        if report.runner_exit_code != trusted_runner_exit_code:
            raise ReportNormalizationError(
                VerificationReason.REPORT_EXIT_MISMATCH,
                f"report runner_exit_code {report.runner_exit_code} != trusted exit "
                f"{trusted_runner_exit_code}",
            )
        effective_exit = trusted_runner_exit_code
    leaves = tuple(
        LeafCase(
            leaf_id=case.test_id,
            status=case.status,
            duration_ms=case.duration_ms,
            details=case.details,
        )
        for case in report.tests
    )
    errors = tuple(
        LeafCollectionError(message=error.message, leaf_id=error.test_id)
        for error in report.collection_errors
    )
    return LeafReport(
        framework="node:test",
        report_format=report.report_format,
        collected=report.collected,
        leaves=leaves,
        collection_errors=errors,
        trusted_runner_exit_code=effective_exit,
        frozen_total=frozen_total,
    )


__all__ = ["MAX_NODE_REPORT_BYTES", "normalize_node_test_json"]
