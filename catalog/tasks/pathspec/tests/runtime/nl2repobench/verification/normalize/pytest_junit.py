"""Normalize pytest collection JSON and JUnit XML into canonical leaves."""

from __future__ import annotations

import json
from typing import Any

from defusedxml import ElementTree

from nl2repobench.verification.leaf_report import (
    LeafCase,
    LeafCollectionError,
    LeafReport,
    ReportNormalizationError,
)
from nl2repobench.verification.models import CollectionReport
from nl2repobench.verification.taxonomy import VerificationReason

MAX_COLLECTION_BYTES = 4 * 1024 * 1024
MAX_JUNIT_BYTES = 64 * 1024 * 1024


def _load_collection(data: bytes | None) -> CollectionReport:
    if data is None:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MISSING, "pytest collection report is missing"
        )
    if len(data) > MAX_COLLECTION_BYTES:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED, "pytest collection report exceeds the size limit"
        )
    try:
        return CollectionReport.model_validate_json(data)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            f"invalid pytest collection report: {exc}",
        ) from exc


def _case_id(attributes: dict[str, str], index: int) -> str:
    classname = attributes.get("classname", "")
    name = attributes.get("name", "")
    value = f"{classname}::{name}" if classname else name
    return value or f"junit-case-{index}"


def _case_status(case: Any) -> tuple[str, str | None]:
    error = case.find("error")
    if error is not None:
        return "error", error.text
    failure = case.find("failure")
    if failure is not None:
        return "failed", failure.text
    skipped = case.find("skipped")
    if skipped is not None:
        if skipped.attrib.get("type", "").casefold() == "pytest.xfail":
            return "xfail", skipped.text
        return "skipped", skipped.text
    return "passed", None


def normalize_pytest_junit(
    *,
    junit_data: bytes | None,
    collection_data: bytes | None,
    frozen_total: int,
    trusted_runner_exit_code: int | None,
) -> LeafReport:
    """Map framework output only; scoring remains in :mod:`evaluator`."""

    if frozen_total <= 0:
        raise ValueError("frozen_total must be positive")
    collection = _load_collection(collection_data)
    if junit_data is None:
        raise ReportNormalizationError(VerificationReason.REPORT_MISSING, "JUnit report is missing")
    if len(junit_data) > MAX_JUNIT_BYTES:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED, "JUnit report exceeds the size limit"
        )
    if not junit_data.strip():
        raise ReportNormalizationError(VerificationReason.REPORT_MALFORMED, "JUnit report is empty")
    try:
        root = ElementTree.fromstring(junit_data)
    except Exception as exc:  # defusedxml has multiple parser-specific errors
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED, f"cannot parse JUnit XML: {exc}"
        ) from exc

    cases = list(root.iter("testcase"))
    if collection.nodeids and len(collection.nodeids) != len(cases):
        raise ReportNormalizationError(
            VerificationReason.REPORT_COUNT_MISMATCH,
            f"collection has {len(collection.nodeids)} IDs but JUnit has {len(cases)} cases",
        )
    ids = collection.nodeids or tuple(
        _case_id(dict(case.attrib), index) for index, case in enumerate(cases)
    )
    leaves: list[LeafCase] = []
    for index, case in enumerate(cases):
        status, details = _case_status(case)
        duration = 0.0
        raw_duration = case.attrib.get("time")
        if raw_duration is not None:
            try:
                duration = max(0.0, float(raw_duration) * 1000.0)
            except ValueError:
                raise ReportNormalizationError(
                    VerificationReason.REPORT_MALFORMED,
                    f"JUnit testcase {index} has a non-numeric duration",
                ) from None
        leaves.append(
            LeafCase(
                leaf_id=ids[index],
                status=status,  # type: ignore[arg-type]
                duration_ms=duration,
                details=details,
            )
        )
    errors = tuple(
        LeafCollectionError(message=error.message, leaf_id=error.nodeid)
        for error in collection.collection_errors
    )
    try:
        return LeafReport(
            framework="pytest",
            report_format="pytest-junit-v1",
            collected=len(leaves),
            leaves=tuple(leaves),
            collection_errors=errors,
            trusted_runner_exit_code=trusted_runner_exit_code,
            frozen_total=frozen_total,
        )
    except ValueError as exc:
        reason = (
            VerificationReason.DUPLICATE_LEAF_ID
            if "IDs must be unique" in str(exc)
            else VerificationReason.REPORT_MALFORMED
        )
        raise ReportNormalizationError(reason, str(exc)) from exc


__all__ = ["normalize_pytest_junit"]
