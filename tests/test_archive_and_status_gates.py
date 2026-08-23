from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_script(name: str):
    path = Path(__file__).parents[1] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


archive = _load_script("verify_oss_archive")
status = _load_script("reconcile_task_status")
uploader = _load_script("upload_runs_to_oss")


def test_archive_manifest_rejects_duplicate_keys(tmp_path: Path) -> None:
    manifest = tmp_path / "objects.json"
    row = {"key": "nl2repobench/runs/gpt/demo/trial/result", "size": 1, "sha256": "a" * 64}
    manifest.write_text(
        json.dumps({"hash_algorithm": "sha256", "objects": [row, row]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate key"):
        archive.load_object_manifest(manifest)


def test_archive_local_verification_matches_uploader_manifest(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    path = runs / "batch" / "gpt56-demo" / "2026-08-23__00-00-00" / "harbor__abc" / "result.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")
    items = list(uploader.iter_run_uploads(runs))
    manifest = tmp_path / "objects.json"
    uploader.write_manifest(items, manifest)
    records = archive.load_object_manifest(manifest)

    assert archive.validate_local_runs(records, runs) == []
    path.write_text('{"changed": true}', encoding="utf-8")
    assert archive.validate_local_runs(records, runs)


def test_archive_secret_scan_returns_paths_only(tmp_path: Path) -> None:
    secret_path = tmp_path / "log.txt"
    secret_path.write_text("token=sk-" + "a" * 48, encoding="utf-8")

    findings = archive.scan_for_secrets(tmp_path)

    assert findings == [str(secret_path)]


class _RemoteResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.headers = {}

    def read(self, size: int | None = None) -> bytes:
        if size is None:
            payload, self.payload = self.payload, b""
            return payload
        payload, self.payload = self.payload[:size], self.payload[size:]
        return payload


class _RemoteBucket:
    def __init__(self, payloads: dict[str, bytes]) -> None:
        self.payloads = payloads

    def get_object(self, key: str) -> _RemoteResponse:
        return _RemoteResponse(self.payloads[key])


def test_archive_remote_verification_hashes_payload_bytes() -> None:
    record = archive.ObjectRecord("nl2repobench/runs/demo/result", 7, "0" * 64)
    bucket = _RemoteBucket({record.key: b"payload"})

    errors = archive.verify_remote_objects(bucket, (record,))

    assert any("checksum mismatch" in error for error in errors)


def test_archive_cleanup_is_contained_under_repo_runs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    runs = repo / ".nl2repo" / "runs" / "campaign"
    runs.mkdir(parents=True)
    (runs / "artifact").write_text("x", encoding="utf-8")

    archive.remove_local_runs(runs, repo_root=repo)

    assert not runs.exists()
    with pytest.raises(ValueError, match="unsafe or missing"):
        archive.remove_local_runs(tmp_path / "outside", repo_root=repo)


def test_status_reconciliation_marks_dependency_block_as_repairable(tmp_path: Path) -> None:
    task = tmp_path / "demo"
    task.mkdir()
    (task / "task.toml").write_text(
        '[lifecycle]\nstatus = "blocked"\nreason = "missing dependency lock"\n',
        encoding="utf-8",
    )

    report = status.reconcile(tmp_path)

    assert report["counts"] == {"repairable": 1}
    assert len(status.invalid_blockers(report)) == 1


def test_status_reconciliation_allows_only_no_test_blockers(tmp_path: Path) -> None:
    task = tmp_path / "demo"
    task.mkdir()
    (task / "task.toml").write_text(
        '[lifecycle]\n'
        'status = "blocked"\n'
        'reason = "no executable tests are available"\n'
        'owner = "integrator"\n'
        'evidence = ["audit.md"]\n'
        'approval_refs = ["decision-1"]\n',
        encoding="utf-8",
    )

    report = status.reconcile(tmp_path)

    assert report["counts"] == {"no-tests": 1}
    assert status.invalid_blockers(report) == []


def test_status_reconciliation_finds_nested_blocked_audit_without_task_source(
    tmp_path: Path,
) -> None:
    evidence = tmp_path / "candidate" / "evidence"
    evidence.mkdir(parents=True)
    (evidence / "audit.md").write_text(
        "# Candidate\n\nStatus: `blocked` / audit-only.\n\n"
        "Publication is blocked because the npm lockfile is missing.\n",
        encoding="utf-8",
    )

    report = status.reconcile(tmp_path)

    record = report["records"][0]
    assert record["task_id"] == "candidate"
    assert record["blocked_docs"] == ["evidence/audit.md"]
    assert record["reason_kind"] == "repairable"
    assert status.invalid_blockers(report)


def test_status_reconciliation_rejects_published_without_evidence(tmp_path: Path) -> None:
    task = tmp_path / "demo"
    task.mkdir()
    (task / "task.toml").write_text(
        '[lifecycle]\nstatus = "published"\nowner = "integrator"\n',
        encoding="utf-8",
    )

    report = status.reconcile(tmp_path)

    assert any(
        "missing lifecycle.evidence" in error
        for error in report["records"][0]["integrity_errors"]
    )
