"""Validate a versioned, verifier-only private artifact migration report.

This validator checks report authority and binding only.  It deliberately does
not resolve CAS URIs or read private bytes; the compiler/release owner performs
those operations under task-scoped authorization.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

MAX_REPORT_BYTES = 4 * 1024 * 1024
MAX_STRING_BYTES = 4096
MAX_COMMAND_BYTES = 4096
MAX_DEPTH = 8
MAX_MAPPING_ITEMS = 128
MAX_RECEIPT_COUNT = 16
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REVISION = re.compile(r"^[0-9a-f]{40}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
CAS_REF = re.compile(r"^artifact://private/(sha256:[0-9a-f]{64})$")
PLACEHOLDER = re.compile(
    r"(?:^|[\s<_])(todo|tbd|placeholder|replace[-_ ]?me|dummy|example|your[-_ ]?value)(?:$|[\s>_])",
    re.IGNORECASE,
)

REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "migration_id",
        "task_id",
        "old_task_version",
        "new_task_version",
        "source_revision",
        "old_artifact_digest",
        "new_artifact_digest",
        "old_manifest_digest",
        "new_manifest_digest",
        "old_artifact_ref",
        "new_artifact_ref",
        "old_manifest_ref",
        "new_manifest_ref",
        "artifact_kind",
        "visibility",
        "agent_visible",
        "old_release",
        "scan_evidence",
        "oracle_receipt",
        "controls_receipts",
        "reviewer_signoff",
        "audit_receipt",
    }
)
ALLOWED_FIELDS = REQUIRED_FIELDS
CONTROL_NAMES = frozenset({"empty", "stub", "forgery", "offline"})


def _text(
    value: object,
    field: str,
    errors: list[str],
    *,
    pattern: re.Pattern[str] | None = None,
) -> str | None:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > MAX_STRING_BYTES:
        errors.append(f"{field} must be a bounded non-empty string")
        return None
    if PLACEHOLDER.search(value):
        errors.append(f"{field} contains a placeholder")
    if pattern is not None and pattern.fullmatch(value) is None:
        errors.append(f"{field} has an invalid format")
        return None
    return value


def _digest(value: object, field: str, errors: list[str]) -> str | None:
    return _text(value, field, errors, pattern=SHA256)


def _cas_ref(value: object, field: str, expected_digest: str | None, errors: list[str]) -> None:
    ref = _text(value, field, errors)
    if ref is None:
        return
    match = CAS_REF.fullmatch(ref)
    if match is None:
        errors.append(f"{field} must be an immutable private CAS reference")
    elif expected_digest is not None and match.group(1) != expected_digest:
        errors.append(f"{field} does not match its digest")


def _exit_code(value: object, field: str, errors: list[str]) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 255:
        errors.append(f"{field}.exit_code must be an integer from 0 through 255")


def _timestamp(value: object, field: str, errors: list[str]) -> datetime | None:
    raw = _text(value, field, errors)
    if raw is None:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field} must be an ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{field} must include a timezone")
        return None
    return parsed


def _receipt(
    value: object,
    field: str,
    *,
    task_id: str,
    release_version: str,
    manifest_digest: str,
    artifact_digest: str,
    errors: list[str],
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return
    if len(value) > MAX_MAPPING_ITEMS:
        errors.append(f"{field} has too many fields")
        return
    for key in ("task_id", "release_version", "manifest_digest", "artifact_digest", "command"):
        if key not in value:
            errors.append(f"{field}.{key} is required")
    if _text(value.get("task_id"), f"{field}.task_id", errors) != task_id:
        errors.append(f"{field}.task_id does not match migration task")
    if _text(value.get("release_version"), f"{field}.release_version", errors) != release_version:
        errors.append(f"{field}.release_version does not match new task version")
    if _digest(value.get("manifest_digest"), f"{field}.manifest_digest", errors) != manifest_digest:
        errors.append(f"{field}.manifest_digest does not match new manifest")
    if _digest(value.get("artifact_digest"), f"{field}.artifact_digest", errors) != artifact_digest:
        errors.append(f"{field}.artifact_digest does not match new artifact")
    command = _text(value.get("command"), f"{field}.command", errors)
    if command is not None and len(command.encode("utf-8")) > MAX_COMMAND_BYTES:
        errors.append(f"{field}.command exceeds the size limit")
    _exit_code(value.get("exit_code"), field, errors)
    cleanup = value.get("cleanup_complete")
    if cleanup is not True:
        errors.append(f"{field}.cleanup_complete must be true")
    started = _timestamp(value.get("started_at"), f"{field}.started_at", errors)
    finished = _timestamp(value.get("finished_at"), f"{field}.finished_at", errors)
    if started is not None and finished is not None and finished < started:
        errors.append(f"{field}.finished_at precedes started_at")
    if value.get("status") not in {"passed", "approved", "complete"}:
        errors.append(f"{field}.status must be a successful terminal status")


def _check_shape(value: object, depth: int, path: str, errors: list[str]) -> None:
    if depth > MAX_DEPTH:
        errors.append(f"{path} exceeds nesting limit")
        return
    if isinstance(value, dict):
        if len(value) > MAX_MAPPING_ITEMS:
            errors.append(f"{path} has too many fields")
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                errors.append(f"{path} has an invalid key")
            _check_shape(item, depth + 1, f"{path}.{key}", errors)
    elif isinstance(value, list):
        if len(value) > MAX_RECEIPT_COUNT:
            errors.append(f"{path} has too many entries")
        for index, item in enumerate(value):
            _check_shape(item, depth + 1, f"{path}[{index}]", errors)
    elif isinstance(value, str) and len(value.encode("utf-8")) > MAX_STRING_BYTES:
        errors.append(f"{path} contains an oversized string")


def validate(payload: object) -> list[str]:
    """Return deterministic validation errors without touching referenced artifacts."""

    if not isinstance(payload, dict):
        return ["migration report must be an object"]
    errors: list[str] = []
    _check_shape(payload, 0, "report", errors)
    missing = sorted(REQUIRED_FIELDS - payload.keys())
    errors.extend(f"missing required migration field: {field}" for field in missing)
    unknown = sorted(payload.keys() - ALLOWED_FIELDS)
    errors.extend(f"unknown migration field: {field}" for field in unknown)
    if errors:
        return sorted(set(errors))

    if payload["schema_version"] != "1.0":
        errors.append("schema_version must be 1.0")
    task_id = _text(payload["task_id"], "task_id", errors, pattern=IDENTIFIER)
    migration_id = _text(payload["migration_id"], "migration_id", errors, pattern=IDENTIFIER)
    old_version = _text(payload["old_task_version"], "old_task_version", errors, pattern=VERSION)
    new_version = _text(payload["new_task_version"], "new_task_version", errors, pattern=VERSION)
    revision = _text(payload["source_revision"], "source_revision", errors, pattern=REVISION)
    old_artifact = _digest(payload["old_artifact_digest"], "old_artifact_digest", errors)
    new_artifact = _digest(payload["new_artifact_digest"], "new_artifact_digest", errors)
    old_manifest = _digest(payload["old_manifest_digest"], "old_manifest_digest", errors)
    new_manifest = _digest(payload["new_manifest_digest"], "new_manifest_digest", errors)
    if old_version is not None and new_version is not None and old_version == new_version:
        errors.append("migration must mint a new task version")
    if old_artifact is not None and new_artifact is not None and old_artifact == new_artifact:
        errors.append("migration must mint a new artifact digest")
    if old_manifest is not None and new_manifest is not None and old_manifest == new_manifest:
        errors.append("migration must mint a new manifest digest")
    if payload["schema_version"] == "1.0" and revision is None:
        errors.append("source_revision is required for immutable traceability")
    _cas_ref(payload["old_artifact_ref"], "old_artifact_ref", old_artifact, errors)
    _cas_ref(payload["new_artifact_ref"], "new_artifact_ref", new_artifact, errors)
    _cas_ref(payload["old_manifest_ref"], "old_manifest_ref", old_manifest, errors)
    _cas_ref(payload["new_manifest_ref"], "new_manifest_ref", new_manifest, errors)
    kind = _text(payload["artifact_kind"], "artifact_kind", errors, pattern=IDENTIFIER)
    if kind not in {"test-bundle", "verifier-bundle", "oracle-bundle"}:
        errors.append("artifact_kind is not an allowed private artifact kind")
    if payload["visibility"] != "verifier-only":
        errors.append("migrated private artifact must remain verifier-only")
    if payload["agent_visible"] is not False:
        errors.append("agent_visible must be false for a verifier-only artifact")

    old_release = payload["old_release"]
    if not isinstance(old_release, dict):
        errors.append("old_release must be an object")
    else:
        if old_release.get("preserved") is not True:
            errors.append("old_release must explicitly be preserved")
        for key, expected in (
            ("task_version", old_version),
            ("artifact_digest", old_artifact),
            ("manifest_digest", old_manifest),
        ):
            if old_release.get(key) != expected:
                errors.append(f"old_release.{key} does not match the old release")
        _cas_ref(old_release.get("artifact_ref"), "old_release.artifact_ref", old_artifact, errors)
        _cas_ref(old_release.get("manifest_ref"), "old_release.manifest_ref", old_manifest, errors)

    scan = payload["scan_evidence"]
    if not isinstance(scan, dict):
        errors.append("scan_evidence must be an object")
    else:
        if scan.get("status") != "passed" or scan.get("violations") != 0:
            errors.append("scan_evidence must prove zero bypass violations")
        _digest(scan.get("scan_digest"), "scan_evidence.scan_digest", errors)
        if (
            task_id is not None
            and new_version is not None
            and new_manifest is not None
            and new_artifact is not None
        ):
            _receipt(
                scan,
                "scan_evidence",
                task_id=task_id,
                release_version=new_version,
                manifest_digest=new_manifest,
                artifact_digest=new_artifact,
                errors=errors,
            )

    if (
        task_id is not None
        and new_version is not None
        and new_manifest is not None
        and new_artifact is not None
    ):
        _receipt(
            payload["oracle_receipt"],
            "oracle_receipt",
            task_id=task_id,
            release_version=new_version,
            manifest_digest=new_manifest,
            artifact_digest=new_artifact,
            errors=errors,
        )
        controls = payload["controls_receipts"]
        if not isinstance(controls, dict) or set(controls) != CONTROL_NAMES:
            errors.append("migration requires exactly empty/stub/forgery/offline control receipts")
        elif len(controls) > MAX_RECEIPT_COUNT:
            errors.append("controls_receipts has too many entries")
        else:
            for name in sorted(CONTROL_NAMES):
                _receipt(
                    controls[name],
                    f"controls_receipts.{name}",
                    task_id=task_id,
                    release_version=new_version,
                    manifest_digest=new_manifest,
                    artifact_digest=new_artifact,
                    errors=errors,
                )
        reviewer = payload["reviewer_signoff"]
        if not isinstance(reviewer, dict):
            errors.append("reviewer_signoff must be an object")
        else:
            reviewer_id = _text(reviewer.get("reviewer"), "reviewer_signoff.reviewer", errors)
            if reviewer_id is None:
                errors.append("reviewer_signoff.reviewer is required")
            if reviewer.get("status") != "approved":
                errors.append("reviewer_signoff.status must be approved")
            _timestamp(reviewer.get("signed_at"), "reviewer_signoff.signed_at", errors)
            if reviewer.get("task_id") != task_id or reviewer.get("release_version") != new_version:
                errors.append("reviewer_signoff is not bound to the new release")
        _receipt(
            payload["audit_receipt"],
            "audit_receipt",
            task_id=task_id,
            release_version=new_version,
            manifest_digest=new_manifest,
            artifact_digest=new_artifact,
            errors=errors,
        )
        audit = payload["audit_receipt"]
        if isinstance(audit, dict):
            if audit.get("migration_id") != migration_id:
                errors.append("audit_receipt.migration_id does not match migration")
            if (
                audit.get("old_artifact_digest") != old_artifact
                or audit.get("old_manifest_digest") != old_manifest
            ):
                errors.append("audit_receipt does not bind the old release")
            if audit.get("old_task_version") != old_version:
                errors.append("audit_receipt.old_task_version does not match old release")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        raw = args.report.read_bytes()
        if len(raw) > MAX_REPORT_BYTES:
            raise ValueError("migration report exceeds size limit")
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, sort_keys=True))
        return 1
    errors = validate(payload)
    print(json.dumps({"passed": not errors, "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
