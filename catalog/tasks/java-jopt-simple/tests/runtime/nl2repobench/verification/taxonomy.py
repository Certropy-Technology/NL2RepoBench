"""Canonical runtime-neutral failure taxonomy.

Legacy v1/v2 enums stay in their original modules so historical schemas and
grading bytes remain readable. This enum is the only one used by the new
normalizer/evaluator path.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class VerificationReason(StrEnum):
    ARTIFACT_COPY_FAILED = "artifact-copy-failed"
    CANDIDATE_WORKSPACE_REJECTED = "candidate-workspace-rejected"
    CANDIDATE_INSTALLATION_FAILED = "candidate-installation-failed"
    CANDIDATE_CALL_FAILED = "candidate-call-failed"
    CANDIDATE_TIMEOUT = "candidate-timeout"
    SETUP_COMMAND_FAILED = "setup-command-failed"
    REPORT_MISSING = "report-missing"
    REPORT_MALFORMED = "report-malformed"
    DUPLICATE_LEAF_ID = "duplicate-leaf-id"
    COLLECTION_ERROR = "collection-error"
    COLLECTION_MISMATCH = "collection-mismatch"
    REPORT_COUNT_MISMATCH = "report-count-mismatch"
    RUNNER_ABNORMAL_EXIT = "runner-abnormal-exit"
    REPORT_EXIT_MISMATCH = "report-exit-mismatch"
    VERIFIER_TIMEOUT = "verifier-timeout"
    VERIFIER_NETWORK_AVAILABLE = "verifier-network-available"
    VERIFIER_INTERNAL_ERROR = "verifier-internal-error"
    INTEGRITY_FAILURE = "integrity-failure"


_ALIASES = {
    "collection-report-missing": VerificationReason.REPORT_MISSING,
    "collection-report-malformed": VerificationReason.REPORT_MALFORMED,
    "junit-missing": VerificationReason.REPORT_MISSING,
    "junit-malformed": VerificationReason.REPORT_MALFORMED,
    "junit-count-mismatch": VerificationReason.REPORT_COUNT_MISMATCH,
    "pytest-abnormal-exit": VerificationReason.RUNNER_ABNORMAL_EXIT,
    "pytest-report-mismatch": VerificationReason.REPORT_EXIT_MISMATCH,
    "node-report-missing": VerificationReason.REPORT_MISSING,
    "node-report-malformed": VerificationReason.REPORT_MALFORMED,
    "node-duplicate-test-id": VerificationReason.DUPLICATE_LEAF_ID,
    "node-collection-error": VerificationReason.COLLECTION_ERROR,
    "node-collection-mismatch": VerificationReason.COLLECTION_MISMATCH,
    "node-report-count-mismatch": VerificationReason.REPORT_COUNT_MISMATCH,
    "node-runner-abnormal-exit": VerificationReason.RUNNER_ABNORMAL_EXIT,
    "node-report-exit-mismatch": VerificationReason.REPORT_EXIT_MISMATCH,
}


def canonical_reason(value: object) -> VerificationReason:
    """Normalize a current or historical enum/string to the canonical enum."""

    raw = value.value if isinstance(value, StrEnum) else value
    if not isinstance(raw, str):
        raise ValueError(f"invalid verification reason: {value!r}")
    try:
        return VerificationReason(raw)
    except ValueError:
        try:
            return _ALIASES[raw]
        except KeyError as exc:
            raise ValueError(f"unknown verification reason: {raw}") from exc


def legacy_python_reason(reason: VerificationReason) -> Any:
    """Map a canonical reason to the unchanged v1 enum."""

    from .models import VerificationReason as LegacyReason

    mapping = {
        VerificationReason.REPORT_MISSING: LegacyReason.COLLECTION_REPORT_MISSING,
        VerificationReason.REPORT_MALFORMED: LegacyReason.COLLECTION_REPORT_MALFORMED,
        VerificationReason.DUPLICATE_LEAF_ID: LegacyReason.COLLECTION_REPORT_MALFORMED,
        VerificationReason.REPORT_COUNT_MISMATCH: LegacyReason.JUNIT_COUNT_MISMATCH,
        VerificationReason.RUNNER_ABNORMAL_EXIT: LegacyReason.PYTEST_ABNORMAL_EXIT,
        VerificationReason.REPORT_EXIT_MISMATCH: LegacyReason.PYTEST_REPORT_MISMATCH,
        VerificationReason.CANDIDATE_CALL_FAILED: LegacyReason.SETUP_COMMAND_FAILED,
        VerificationReason.INTEGRITY_FAILURE: LegacyReason.VERIFIER_INTERNAL_ERROR,
    }
    if reason in mapping:
        return mapping[reason]
    return LegacyReason(reason.value)


def legacy_node_reason(reason: VerificationReason) -> Any:
    """Map a canonical reason to the unchanged Node v2 enum."""

    from .node_models import NodeVerificationReason

    mapping = {
        VerificationReason.REPORT_MISSING: NodeVerificationReason.REPORT_MISSING,
        VerificationReason.REPORT_MALFORMED: NodeVerificationReason.REPORT_MALFORMED,
        VerificationReason.DUPLICATE_LEAF_ID: NodeVerificationReason.DUPLICATE_TEST_ID,
        VerificationReason.REPORT_COUNT_MISMATCH: NodeVerificationReason.REPORT_COUNT_MISMATCH,
        VerificationReason.RUNNER_ABNORMAL_EXIT: NodeVerificationReason.RUNNER_ABNORMAL_EXIT,
        VerificationReason.REPORT_EXIT_MISMATCH: NodeVerificationReason.REPORT_EXIT_MISMATCH,
        VerificationReason.COLLECTION_ERROR: NodeVerificationReason.COLLECTION_ERROR,
        VerificationReason.COLLECTION_MISMATCH: NodeVerificationReason.COLLECTION_MISMATCH,
    }
    if reason in mapping:
        return mapping[reason]
    return NodeVerificationReason(reason.value)


__all__ = ["VerificationReason", "canonical_reason", "legacy_node_reason", "legacy_python_reason"]
