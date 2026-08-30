"""Canonical runtime-neutral failure taxonomy."""

from __future__ import annotations

from enum import StrEnum


class VerificationReason(StrEnum):
    ARTIFACT_COPY_FAILED = "artifact-copy-failed"
    CANDIDATE_WORKSPACE_REJECTED = "candidate-workspace-rejected"
    CANDIDATE_INSTALLATION_FAILED = "candidate-installation-failed"
    CANDIDATE_CALL_FAILED = "candidate-call-failed"
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


__all__ = ["VerificationReason"]
