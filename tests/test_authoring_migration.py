# ruff: noqa: E501
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

import nl2repobench.authoring.migration as migration
from nl2repobench.authoring.backup import (
    activate_database,
    backup_database,
    restore_database,
    verify_backup,
)
from nl2repobench.authoring.migration import (
    MigrationError,
    generate_manifest,
    import_manifest,
    validate_manifest,
)
from nl2repobench.authoring.scheduler import Scheduler


def _live(root: Path) -> None:
    (root / "plans").mkdir()
    (root / "queues").mkdir()
    (root / "external").mkdir()
    (root / "state").mkdir()
    (root / "supervisor" / "queues").mkdir(parents=True)
    for language in ("python", "node", "go"):
        batch = f"{language}-author-wave2-20260828"
        queue_batch = f"{language}-wave2-20260828"
        plan = {"batch_id": batch, "language": language, "candidate_input": str(root / "external" / f"{queue_batch}.json")}
        (root / "plans" / f"{batch}.json").write_text(json.dumps(plan), encoding="utf-8")
        queue = {"queue": [{"candidate_id": f"{language}-candidate", "package": f"{language}-pkg", "selection": {"revision": "a" * 40, "upstream_url": "https://example.invalid/repo", "source_kind": "test"}}]}
        (root / "external" / f"{queue_batch}.json").write_text(json.dumps(queue), encoding="utf-8")
        (root / "queues" / f"{queue_batch}.json").write_text(json.dumps({"items": {f"{language}-candidate": {"status": "complete", "attempts": 2}}}), encoding="utf-8")
    descriptors = []
    for index, language in enumerate(("python", "node", "go", "go")):
        batch = f"{language}-author-discover-20260829T17350{index}Z"
        source = root / "supervisor" / "queues" / f"{batch}.json"
        state = root / "queues" / f"{batch}.json"
        plan = root / "plans" / f"{batch}.json"
        plan.write_text(json.dumps({"batch_id": batch, "language": language}), encoding="utf-8")
        source.write_text(json.dumps({"queue": [{"candidate_id": f"{language}-{index}", "package": f"pkg-{index}", "selection": {"revision": "b" * 40, "upstream_url": "https://example.invalid/repo"}}]}), encoding="utf-8")
        state.write_text(json.dumps({"items": {f"{language}-{index}": {"status": "pending"}}}), encoding="utf-8")
        descriptors.append({"batch_id": batch, "language": language, "queue": str(source), "queue_state": str(state), "plan": str(plan)})
    (root / "supervisor" / "generated-lanes.json").write_text(json.dumps(descriptors), encoding="utf-8")


def test_manifest_has_exact_lanes_and_rejects_drift_and_symlink(tmp_path: Path) -> None:
    _live(tmp_path)
    manifest = generate_manifest(tmp_path, cutover_id="cutover-1")
    assert len(manifest["lanes"]) == 7
    assert {lane["kind"] for lane in manifest["lanes"]} == {"base", "generated"}
    validate_manifest(manifest, tmp_path)
    manifest["lanes"][0]["queue"]["sha256"] = "0" * 64
    with pytest.raises(MigrationError, match="digest mismatch"):
        validate_manifest(manifest, tmp_path)
    manifest = generate_manifest(tmp_path, cutover_id="cutover-1")
    queue = tmp_path / manifest["lanes"][0]["queue_source"]
    moved = queue.with_name("real.json")
    queue.rename(moved)
    queue.symlink_to(moved)
    with pytest.raises(MigrationError, match="symlink"):
        validate_manifest(manifest, tmp_path)


def test_import_preserves_status_attempts_and_orphan_evidence_without_controllers(tmp_path: Path) -> None:
    _live(tmp_path)
    manifest = generate_manifest(tmp_path, cutover_id="cutover-2")
    db = tmp_path.parent / "import.sqlite3"
    result = import_manifest(manifest, tmp_path, db_path=db, dry_run=False)
    assert result["counts"]["complete"] == 3
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT count(*) FROM controllers").fetchone()[0] == 0
        assert connection.execute("SELECT authoring_attempts FROM tasks WHERE state='complete'").fetchone()[0] == 2
        assert connection.execute("SELECT count(*) FROM orphan_claim_evidence").fetchone()[0] >= 3
    with pytest.raises(MigrationError, match="fresh"):
        import_manifest(manifest, tmp_path, db_path=db, dry_run=False)


def test_backup_verify_tamper_restore_dry_run_and_activation_guard(tmp_path: Path) -> None:
    scheduler = Scheduler(tmp_path / "source.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    backup_dir = tmp_path / "backup"
    backup_database(scheduler.path, backup_dir)
    assert verify_backup(backup_dir)["verified"] is True
    target = tmp_path / "restored.sqlite3"
    marker = tmp_path / "quiesced.json"
    marker.write_text('{"quiesced": true, "receipt_id": "r1", "generation": 1, "database": "restored.sqlite3", "observed_at": "2026-08-30T00:00:00Z"}', encoding="utf-8")
    dry = restore_database(backup_dir, target, quiescence_marker=marker)
    assert dry["dry_run"] is True and not target.exists()
    with pytest.raises(MigrationError, match="explicit"):
        activate_database(backup_dir / "source.sqlite3", target)
    restore_database(backup_dir, target, quiescence_marker=marker, activate=True)
    assert verify_backup(backup_dir)["verified"] is True
    (backup_dir / "source.sqlite3").write_bytes(b"tampered")
    with pytest.raises(MigrationError, match="checksum"):
        verify_backup(backup_dir)


def test_uncheckpointed_wal_is_included_in_online_backup(tmp_path: Path) -> None:
    source = Scheduler(tmp_path / "wal.sqlite3", supplied_root=tmp_path)
    source.init()
    with source.connect() as db:
        db.execute("INSERT INTO schema_meta(key,value) VALUES('wal_test','present')")
    backup_dir = tmp_path / "wal-backup"
    backup_database(source.path, backup_dir)
    with sqlite3.connect(backup_dir / "wal.sqlite3") as db:
        assert db.execute("SELECT value FROM schema_meta WHERE key='wal_test'").fetchone()[0] == "present"


def test_import_rollback_removes_staging_and_import_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _live(tmp_path)
    manifest = migration.generate_manifest(tmp_path, cutover_id="rollback")
    db = tmp_path.parent / "rollback.sqlite3"
    calls = 0
    original = migration._classify_failure

    def fail_midway(item: dict[str, object]) -> str | None:
        nonlocal calls
        calls += 1
        if calls > 1:
            raise migration.MigrationError("synthetic mid-import failure")
        return original(item)

    monkeypatch.setattr(migration, "_classify_failure", fail_midway)
    with pytest.raises(migration.MigrationError, match="mid-import"):
        migration.import_manifest(manifest, tmp_path, db_path=db, dry_run=False)
    assert not db.exists()
    assert not (tmp_path.parent / ".rollback.sqlite3.lock").is_symlink()


def test_static_quiescence_marker_is_not_a_restore_receipt(tmp_path: Path) -> None:
    scheduler = Scheduler(tmp_path / "source.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    backup_dir = tmp_path / "backup"
    backup_database(scheduler.path, backup_dir)
    marker = tmp_path / "stale.json"
    marker.write_text('{"quiesced": true}', encoding="utf-8")
    with pytest.raises(MigrationError, match="generation-bound"):
        restore_database(backup_dir, tmp_path / "target.sqlite3", quiescence_marker=marker)
