from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import cast

import pytest

_SCRIPT = Path(__file__).parents[1] / "scripts/validate_private_artifact_migration.py"
_SPEC = importlib.util.spec_from_file_location("private_artifact_migration_validator", _SCRIPT)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
validate = _MODULE.validate


OLD_ARTIFACT = "sha256:" + "a" * 64
NEW_ARTIFACT = "sha256:" + "b" * 64
OLD_MANIFEST = "sha256:" + "c" * 64
NEW_MANIFEST = "sha256:" + "d" * 64
REVISION = "e" * 40


def _receipt(task: str, version: str, manifest: str, artifact: str) -> dict[str, object]:
    return {
        "task_id": task,
        "release_version": version,
        "manifest_digest": manifest,
        "artifact_digest": artifact,
        "command": "python3 scripts/check_candidate_spawn_boundary.py report.json",
        "exit_code": 0,
        "cleanup_complete": True,
        "started_at": "2026-09-01T10:00:00+00:00",
        "finished_at": "2026-09-01T10:00:01+00:00",
        "status": "passed",
    }


def _report() -> dict[str, object]:
    task = "demo-task"
    version = "2.0.0"
    return {
        "schema_version": "1.0",
        "migration_id": "migration-20260901",
        "task_id": task,
        "old_task_version": "1.0.0",
        "new_task_version": version,
        "source_revision": REVISION,
        "old_artifact_digest": OLD_ARTIFACT,
        "new_artifact_digest": NEW_ARTIFACT,
        "old_manifest_digest": OLD_MANIFEST,
        "new_manifest_digest": NEW_MANIFEST,
        "old_artifact_ref": f"artifact://private/{OLD_ARTIFACT}",
        "new_artifact_ref": f"artifact://private/{NEW_ARTIFACT}",
        "old_manifest_ref": f"artifact://private/{OLD_MANIFEST}",
        "new_manifest_ref": f"artifact://private/{NEW_MANIFEST}",
        "artifact_kind": "test-bundle",
        "visibility": "verifier-only",
        "agent_visible": False,
        "old_release": {
            "preserved": True,
            "task_version": "1.0.0",
            "artifact_digest": OLD_ARTIFACT,
            "manifest_digest": OLD_MANIFEST,
            "artifact_ref": f"artifact://private/{OLD_ARTIFACT}",
            "manifest_ref": f"artifact://private/{OLD_MANIFEST}",
        },
        "scan_evidence": {
            **_receipt(task, version, NEW_MANIFEST, NEW_ARTIFACT),
            "status": "passed",
            "violations": 0,
            "scan_digest": "sha256:" + "f" * 64,
        },
        "oracle_receipt": _receipt(task, version, NEW_MANIFEST, NEW_ARTIFACT),
        "controls_receipts": {
            name: _receipt(task, version, NEW_MANIFEST, NEW_ARTIFACT)
            for name in ("empty", "stub", "forgery", "offline")
        },
        "reviewer_signoff": {
            "reviewer": "sol-reviewer",
            "status": "approved",
            "task_id": task,
            "release_version": version,
            "signed_at": "2026-09-01T10:01:00+00:00",
        },
        "audit_receipt": {
            **_receipt(task, version, NEW_MANIFEST, NEW_ARTIFACT),
            "migration_id": "migration-20260901",
            "old_task_version": "1.0.0",
            "old_artifact_digest": OLD_ARTIFACT,
            "old_manifest_digest": OLD_MANIFEST,
        },
    }


def _mapping(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def test_valid_report_is_accepted_without_reading_cas() -> None:
    assert validate(_report()) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_revision", "not-a-revision"),
        ("new_artifact_digest", "sha256:" + "A" * 64),
        ("new_manifest_digest", "placeholder"),
        ("new_artifact_ref", "https://example.invalid/private"),
        ("visibility", "public"),
        ("agent_visible", True),
        ("artifact_kind", "unknown-bundle"),
    ],
)
def test_identity_and_visibility_fields_are_strict(field: str, value: object) -> None:
    report = _report()
    report[field] = value
    errors = validate(report)
    assert errors
    assert any(field in error or "verifier-only" in error for error in errors)


@pytest.mark.parametrize(
    "field",
    [
        "old_task_version",
        "new_task_version",
        "old_artifact_digest",
        "new_artifact_digest",
        "old_manifest_digest",
        "new_manifest_digest",
    ],
)
def test_old_and_new_values_must_be_distinct(field: str) -> None:
    report = _report()
    pairs = {
        "old_task_version": "new_task_version",
        "new_task_version": "old_task_version",
        "old_artifact_digest": "new_artifact_digest",
        "new_artifact_digest": "old_artifact_digest",
        "old_manifest_digest": "new_manifest_digest",
        "new_manifest_digest": "old_manifest_digest",
    }
    report[field] = report[pairs[field]]
    assert any("mint" in error for error in validate(report))


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("old_release", "preserved"), False),
        (("old_release", "artifact_digest"), NEW_ARTIFACT),
        (("old_release", "artifact_ref"), f"artifact://private/{NEW_ARTIFACT}"),
        (("scan_evidence", "violations"), 1),
        (("scan_evidence", "status"), "failed"),
        (("reviewer_signoff", "status"), "pending"),
        (("audit_receipt", "migration_id"), "other-migration"),
    ],
)
def test_release_preservation_and_evidence_are_bound(
    path: tuple[str, str], replacement: object
) -> None:
    report = _report()
    _mapping(report[path[0]])[path[1]] = replacement
    assert validate(report)


@pytest.mark.parametrize("name", ["empty", "stub", "forgery", "offline"])
def test_each_control_receipt_is_required_and_bound(name: str) -> None:
    report = _report()
    controls = _mapping(report["controls_receipts"])
    del controls[name]
    assert any("exactly empty/stub/forgery/offline" in error for error in validate(report))

    report = _report()
    controls = _mapping(report["controls_receipts"])
    _mapping(controls[name])["task_id"] = "other-task"
    assert any("does not match" in error for error in validate(report))


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("exit_code", 256),
        ("cleanup_complete", False),
        ("started_at", "2026-09-01T10:00:00"),
        ("finished_at", "2026-08-01T10:00:00+00:00"),
        ("command", "TODO"),
        ("status", "started"),
    ],
)
def test_receipts_require_bounded_successful_execution(name: str, value: object) -> None:
    report = _report()
    _mapping(report["oracle_receipt"])[name] = value
    assert validate(report)


def test_unknown_and_nested_oversized_report_fields_are_rejected() -> None:
    report = _report()
    report["unexpected"] = True
    assert any("unknown migration field" in error for error in validate(report))

    report = _report()
    _mapping(report["oracle_receipt"])["nested"] = {
        "x": {"y": {"z": {"q": {"r": {"s": {"t": {"u": 1}}}}}}}
    }
    assert any("nesting limit" in error for error in validate(report))


def test_cli_validates_a_report_without_cas_access(tmp_path: Path) -> None:
    report_path = tmp_path / "migration.json"
    report_path.write_text(json.dumps(_report()), encoding="utf-8")
    script = Path(__file__).parents[1] / "scripts/validate_private_artifact_migration.py"
    completed = subprocess.run(
        [sys.executable, str(script), str(report_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert json.loads(completed.stdout) == {"errors": [], "passed": True}


def test_cli_rejects_oversized_report(tmp_path: Path) -> None:
    report_path = tmp_path / "oversized.json"
    report_path.write_text(json.dumps({"padding": "x" * (4 * 1024 * 1024)}), encoding="utf-8")
    script = Path(__file__).parents[1] / "scripts/validate_private_artifact_migration.py"
    completed = subprocess.run(
        [sys.executable, str(script), str(report_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    assert "size limit" in completed.stdout
