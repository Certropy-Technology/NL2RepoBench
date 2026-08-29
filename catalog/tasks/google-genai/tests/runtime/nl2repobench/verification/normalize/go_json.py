"""Normalize verifier-owned Go bridge leaf JSON."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from ..leaf_report import LeafCase, LeafCollectionError, LeafReport, ReportNormalizationError
from ..taxonomy import VerificationReason

MAX_GO_REPORT_BYTES = 8 * 1024 * 1024


def normalize_go_json(
    *,
    report_data: bytes | Mapping[str, Any] | None,
    frozen_total: int,
    trusted_runner_exit_code: int | None,
) -> LeafReport:
    """Convert a Go bridge report to the canonical leaf report."""

    if report_data is None:
        raise ReportNormalizationError(VerificationReason.REPORT_MISSING, "Go report is missing")
    if isinstance(report_data, Mapping):
        payload: object = dict(report_data)
    else:
        if len(report_data) > MAX_GO_REPORT_BYTES:
            raise ReportNormalizationError(
                VerificationReason.REPORT_MALFORMED, "Go report exceeds the size limit"
            )
        try:
            payload = json.loads(report_data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReportNormalizationError(VerificationReason.REPORT_MALFORMED, str(exc)) from exc
    if not isinstance(payload, dict):
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Go report must be an object",
        )
    if payload.get("framework") != "go" or payload.get("report_format") != "go-test-json-v1":
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Go report framework or format is invalid",
        )
    try:
        collected = payload["collected"]
        raw_tests = payload["tests"]
        if (
            not isinstance(collected, int)
            or isinstance(collected, bool)
            or not isinstance(raw_tests, list)
        ):
            raise ValueError("collected/tests have invalid types")
        if len(raw_tests) != collected:
            raise ValueError(f"report has {len(raw_tests)} tests, collected says {collected}")
        leaves = tuple(
            LeafCase(
                leaf_id=str(item["test_id"]),
                status=item["status"],
                duration_ms=float(item.get("duration_ms", 0.0)),
                details=item.get("details"),
            )
            for item in raw_tests
        )
        errors = tuple(
            LeafCollectionError(message=str(item["message"]), leaf_id=item.get("test_id"))
            for item in payload.get("collection_errors", [])
        )
        exit_code = payload.get("runner_exit_code")
        if trusted_runner_exit_code is not None and exit_code != trusted_runner_exit_code:
            raise ReportNormalizationError(
                VerificationReason.REPORT_EXIT_MISMATCH,
                f"report runner_exit_code {exit_code} != trusted exit {trusted_runner_exit_code}",
            )
        return LeafReport(
            framework="go",
            report_format="go-test-json-v1",
            collected=collected,
            leaves=leaves,
            collection_errors=errors,
            trusted_runner_exit_code=exit_code,
            frozen_total=frozen_total,
        )
    except ReportNormalizationError:
        raise
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        reason = (
            VerificationReason.REPORT_COUNT_MISMATCH
            if "collected" in str(exc) or "report has" in str(exc)
            else VerificationReason.REPORT_MALFORMED
        )
        raise ReportNormalizationError(reason, str(exc)) from exc


__all__ = ["MAX_GO_REPORT_BYTES", "normalize_go_json"]
