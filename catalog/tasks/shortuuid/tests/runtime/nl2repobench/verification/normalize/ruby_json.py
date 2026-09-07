"""Normalize verifier-owned Ruby contract reports into canonical leaves."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from ..leaf_report import LeafCase, LeafCollectionError, LeafReport, ReportNormalizationError
from ..taxonomy import VerificationReason

MAX_RUBY_REPORT_BYTES = 8 * 1024 * 1024


def normalize_ruby_json(
    *,
    report_data: bytes | Mapping[str, Any] | None,
    frozen_total: int,
    trusted_runner_exit_code: int | None,
) -> LeafReport:
    """Convert the Ruby contract runner's report to canonical leaf records."""

    if frozen_total <= 0:
        raise ValueError("frozen_total must be positive")
    if report_data is None:
        raise ReportNormalizationError(VerificationReason.REPORT_MISSING, "Ruby report is missing")
    if isinstance(report_data, Mapping):
        payload: object = dict(report_data)
    else:
        if len(report_data) > MAX_RUBY_REPORT_BYTES:
            raise ReportNormalizationError(
                VerificationReason.REPORT_MALFORMED, "Ruby report exceeds the size limit"
            )
        try:
            payload = json.loads(report_data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReportNormalizationError(
                VerificationReason.REPORT_MALFORMED, f"invalid Ruby report JSON: {exc}"
            ) from exc
    if not isinstance(payload, dict):
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED, "Ruby report must be a JSON object"
        )
    if (
        payload.get("framework") != "ruby"
        or payload.get("report_format") != "ruby-contract-json-v1"
    ):
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Ruby report framework or format is invalid",
        )
    raw_tests = payload.get("tests")
    if isinstance(raw_tests, list):
        seen: set[str] = set()
        for item in raw_tests:
            if isinstance(item, Mapping) and isinstance(item.get("test_id"), str):
                test_id = item["test_id"]
                if test_id in seen:
                    raise ReportNormalizationError(
                        VerificationReason.DUPLICATE_LEAF_ID,
                        f"duplicate test_id: {test_id}",
                    )
                seen.add(test_id)
        collected = payload.get("collected")
        if isinstance(collected, int) and not isinstance(collected, bool):
            if len(raw_tests) != collected:
                raise ReportNormalizationError(
                    VerificationReason.REPORT_COUNT_MISMATCH,
                    f"report has {len(raw_tests)} tests, collected says {collected}",
                )
    try:
        collected = payload["collected"]
        if (
            not isinstance(collected, int)
            or isinstance(collected, bool)
            or not isinstance(raw_tests, list)
        ):
            raise ValueError("collected/tests have invalid types")
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
        exit_code = payload["runner_exit_code"]
        if not isinstance(exit_code, int) or isinstance(exit_code, bool):
            raise ValueError("runner_exit_code must be an integer")
        if trusted_runner_exit_code is not None and exit_code != trusted_runner_exit_code:
            raise ReportNormalizationError(
                VerificationReason.REPORT_EXIT_MISMATCH,
                f"report runner_exit_code {exit_code} != trusted exit {trusted_runner_exit_code}",
            )
        return LeafReport(
            framework="ruby",
            report_format="ruby-contract-json-v1",
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


__all__ = ["MAX_RUBY_REPORT_BYTES", "normalize_ruby_json"]
