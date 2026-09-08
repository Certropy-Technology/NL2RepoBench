"""Normalize the trusted Rust bridge report into the shared leaf contract."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any, cast

from ..leaf_report import (
    LeafCase,
    LeafCollectionError,
    LeafReport,
    LeafStatus,
    ReportNormalizationError,
)
from ..taxonomy import VerificationReason

MAX_RUST_REPORT_BYTES = 8 * 1024 * 1024
MAX_RUST_LEAVES = 10_000
REPORT_FIELDS = {
    "schema_version",
    "framework",
    "report_format",
    "collected",
    "leaves",
    "collection_errors",
    "runner_exit_code",
}
LEAF_FIELDS = {"leaf_id", "status", "duration_ms", "details"}
ERROR_FIELDS = {"message", "leaf_id"}


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _load_payload(data: bytes | Mapping[str, Any]) -> object:
    if isinstance(data, Mapping):
        return dict(data)
    if len(data) > MAX_RUST_REPORT_BYTES:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Rust bridge report exceeds the size limit",
        )
    try:
        return json.loads(
            data,
            object_pairs_hook=_no_duplicate_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            f"invalid Rust bridge report: {exc}",
        ) from exc


def normalize_rust_bridge_json(
    *,
    report_data: bytes | Mapping[str, Any] | None,
    frozen_total: int,
    trusted_runner_exit_code: int | None,
) -> LeafReport:
    """Validate a native ``rust-bridge-json-v1`` report without scoring it."""

    if frozen_total <= 0:
        raise ValueError("frozen_total must be positive")
    if report_data is None:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MISSING,
            "Rust bridge report is missing",
        )
    payload = _load_payload(report_data)
    if not isinstance(payload, dict) or set(payload) != REPORT_FIELDS:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Rust bridge report fields are invalid",
        )
    if (
        payload.get("schema_version") != "1.0"
        or payload.get("framework") != "rust-harness"
        or payload.get("report_format") != "rust-bridge-json-v1"
    ):
        raise ReportNormalizationError(
            VerificationReason.REPORT_MALFORMED,
            "Rust bridge report framework or format is invalid",
        )
    try:
        collected = payload["collected"]
        raw_leaves = payload["leaves"]
        raw_errors = payload["collection_errors"]
        exit_code = payload["runner_exit_code"]
        if (
            not isinstance(collected, int)
            or isinstance(collected, bool)
            or collected < 0
            or collected > MAX_RUST_LEAVES
            or not isinstance(raw_leaves, list)
            or not isinstance(raw_errors, list)
            or not isinstance(exit_code, int)
            or isinstance(exit_code, bool)
        ):
            raise ValueError("collected/leaves/errors/runner_exit_code have invalid types")
        if len(raw_leaves) != collected:
            raise ValueError(
                f"Rust bridge report has {len(raw_leaves)} leaves, collected says {collected}"
            )
        leaves: list[LeafCase] = []
        for item in raw_leaves:
            if not isinstance(item, dict) or set(item) != LEAF_FIELDS:
                raise ValueError("Rust bridge leaf fields are invalid")
            duration = item["duration_ms"]
            status = item["status"]
            if (
                not isinstance(duration, (int, float))
                or isinstance(duration, bool)
                or not math.isfinite(duration)
                or not isinstance(item["leaf_id"], str)
                or status not in {"passed", "failed", "error", "skipped", "todo", "xfail"}
                or (item["details"] is not None and not isinstance(item["details"], str))
            ):
                raise ValueError("Rust bridge leaf values are invalid")
            leaves.append(
                LeafCase(
                    leaf_id=item["leaf_id"],
                    status=cast(LeafStatus, status),
                    duration_ms=float(duration),
                    details=item["details"],
                )
            )
        errors: list[LeafCollectionError] = []
        for item in raw_errors:
            if not isinstance(item, dict) or set(item) != ERROR_FIELDS:
                raise ValueError("Rust bridge collection-error fields are invalid")
            if not isinstance(item["message"], str) or (
                item["leaf_id"] is not None and not isinstance(item["leaf_id"], str)
            ):
                raise ValueError("Rust bridge collection-error values are invalid")
            errors.append(
                LeafCollectionError(message=item["message"], leaf_id=item["leaf_id"])
            )
        if trusted_runner_exit_code is not None and exit_code != trusted_runner_exit_code:
            raise ReportNormalizationError(
                VerificationReason.REPORT_EXIT_MISMATCH,
                f"report runner_exit_code {exit_code} != trusted exit "
                f"{trusted_runner_exit_code}",
            )
        return LeafReport(
            framework="rust-harness",
            report_format="rust-bridge-json-v1",
            collected=collected,
            leaves=tuple(leaves),
            collection_errors=tuple(errors),
            trusted_runner_exit_code=exit_code,
            frozen_total=frozen_total,
        )
    except ReportNormalizationError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        reason = (
            VerificationReason.REPORT_COUNT_MISMATCH
            if "collected says" in str(exc)
            else VerificationReason.REPORT_MALFORMED
        )
        raise ReportNormalizationError(reason, str(exc)) from exc


__all__ = ["MAX_RUST_REPORT_BYTES", "normalize_rust_bridge_json"]
