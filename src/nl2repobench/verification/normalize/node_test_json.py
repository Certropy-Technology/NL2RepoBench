"""Normalize verifier-owned ``node:test`` JSON into canonical leaves."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from nl2repobench.verification.leaf_report import (
    LeafCase,
    LeafCollectionError,
    LeafReport,
    ReportNormalizationError,
)
from nl2repobench.verification.taxonomy import VerificationReason

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
    expected_keys = {
        "schema_version",
        "framework",
        "report_format",
        "collected",
        "tests",
        "collection_errors",
        "runner_exit_code",
    }
    if set(payload) != expected_keys or payload.get("schema_version") != "1.0":
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Node report has an invalid canonical shape",
        )
    if payload.get("framework") != "node:test" or payload.get(
        "report_format"
    ) != "node-test-json-v1":
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Node report framework or format is invalid",
        )
    raw_tests = payload["tests"]
    raw_errors = payload["collection_errors"]
    collected = payload["collected"]
    runner_exit = payload["runner_exit_code"]
    if (
        not isinstance(raw_tests, list)
        or not isinstance(raw_errors, list)
        or not isinstance(collected, int)
        or isinstance(collected, bool)
        or not isinstance(runner_exit, int)
        or isinstance(runner_exit, bool)
    ):
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Node report has invalid test, error, or exit fields",
        )
    try:
        cases = []
        for item in raw_tests:
            if not isinstance(item, dict) or not set(item).issubset(
                {"schema_version", "test_id", "status", "duration_ms", "details"}
            ):
                raise ValueError("Node test case has unexpected fields")
            if item.get("schema_version", "1.0") != "1.0":
                raise ValueError("Node test case schema version is invalid")
            cases.append({"leaf_id": item.get("test_id"), "status": item.get("status"),
                          "duration_ms": item.get("duration_ms", 0.0),
                          "details": item.get("details")})
        errors = []
        for item in raw_errors:
            if not isinstance(item, dict) or not set(item).issubset(
                {"schema_version", "message", "test_id"}
            ):
                raise ValueError("Node collection error has unexpected fields")
            if item.get("schema_version", "1.0") != "1.0":
                raise ValueError("Node collection error schema version is invalid")
            errors.append(item)
    except ValueError as exc:
        raise ReportNormalizationError(VerificationReason.REPORT_MALFORMED, str(exc)) from exc
    effective_exit = runner_exit
    if trusted_runner_exit_code is not None:
        if runner_exit != trusted_runner_exit_code:
            raise ReportNormalizationError(
                VerificationReason.REPORT_EXIT_MISMATCH,
                f"report runner_exit_code {runner_exit} != trusted exit "
                f"{trusted_runner_exit_code}",
            )
        effective_exit = trusted_runner_exit_code
    try:
        leaves = tuple(LeafCase.model_validate(case) for case in cases)
        collection_errors = tuple(
            LeafCollectionError.model_validate(
                {"message": item.get("message"), "leaf_id": item.get("test_id")}
            )
            for item in errors
        )
    except ValueError as exc:
        raise ReportNormalizationError(VerificationReason.REPORT_MALFORMED, str(exc)) from exc
    return LeafReport(
        framework="node:test",
        report_format="node-test-json-v1",
        collected=collected,
        leaves=leaves,
        collection_errors=collection_errors,
        trusted_runner_exit_code=effective_exit,
        frozen_total=frozen_total,
    )


__all__ = ["MAX_NODE_REPORT_BYTES", "normalize_node_test_json"]
