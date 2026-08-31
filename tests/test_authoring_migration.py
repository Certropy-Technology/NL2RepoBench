# ruff: noqa: E501
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

import nl2repobench.authoring.migration as migration
from nl2repobench.authoring.backup import (
    activate_database,
    backup_database,
    issue_development_quiescence_receipt,
    issue_quiescence_receipt,
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
    assert result["counts"]["handoff_ready"] == 3
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT count(*) FROM controllers").fetchone()[0] == 0
        assert connection.execute("SELECT authoring_attempts FROM tasks WHERE state='handoff_ready'").fetchone()[0] == 2
        assert connection.execute("SELECT count(*) FROM orphan_claim_evidence").fetchone()[0] >= 3
    with pytest.raises(MigrationError, match="fresh"):
        import_manifest(manifest, tmp_path, db_path=db, dry_run=False)


def test_import_preserves_legacy_receipt_chronology(tmp_path: Path) -> None:
    _live(tmp_path)
    state_path = tmp_path / "queues/python-wave2-20260828.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["items"]["python-candidate"]["receipts"] = [
        {
            "operation_kind": "integration",
            "status": "pushed",
            "operation_attempt": 1,
            "retry_no": 0,
            "commit_sha": "1" * 40,
            "external_ref": "refs/heads/main",
            "started_at": "2026-01-01T00:00:00+00:00",
            "finished_at": "2026-01-01T00:00:01+00:00",
        },
        {
            "operation_kind": "archive",
            "status": "verified",
            "operation_attempt": 1,
            "retry_no": 0,
            "manifest_key": "archive/manifest.json",
            "manifest_sha256": "2" * 64,
            "source_snapshot_sha256": "3" * 64,
            "object_count": 1,
            "byte_count": 1,
            "evidence_sha256": "4" * 64,
            "started_at": "2026-01-01T00:00:02+00:00",
            "finished_at": "2026-01-01T00:00:03+00:00",
        },
        {
            "operation_kind": "cleanup",
            "status": "applied",
            "operation_attempt": 1,
            "retry_no": 0,
            "evidence_path": "cleanup.json",
            "evidence_sha256": "5" * 64,
            "started_at": "2026-01-01T00:00:04+00:00",
            "finished_at": "2026-01-01T00:00:05+00:00",
        },
    ]
    state_path.write_text(json.dumps(state), encoding="utf-8")
    manifest = generate_manifest(tmp_path, cutover_id="receipt-chronology")
    database = tmp_path.parent / "receipt-chronology.sqlite3"

    import_manifest(manifest, tmp_path, db_path=database, dry_run=False)

    with sqlite3.connect(database) as db:
        rows = db.execute(
            "SELECT operation_kind,started_at,finished_at FROM operation_receipts r "
            "JOIN tasks t ON t.task_id=r.task_id WHERE t.candidate_id='python-candidate' "
            "ORDER BY started_at"
        ).fetchall()
    assert rows == [
        ("integration", "2026-01-01T00:00:00.000000+00:00", "2026-01-01T00:00:01.000000+00:00"),
        ("archive", "2026-01-01T00:00:02.000000+00:00", "2026-01-01T00:00:03.000000+00:00"),
        ("cleanup", "2026-01-01T00:00:04.000000+00:00", "2026-01-01T00:00:05.000000+00:00"),
    ]


def _live_case(tmp_path: Path, name: str) -> Path:
    """Build an isolated live tree so each evidence-identity case imports on its own."""
    root = tmp_path / name
    root.mkdir()
    _live(root)
    return root


def _mirror_claim_files(root: Path, batch: str, package: str, claim_name: str) -> tuple[str, str]:
    """Recreate the frozen live pattern: a state claim plus its byte-identical worktree mirror."""
    state_claim = root / "state" / batch / "claims" / f"{claim_name}.json"
    state_claim.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"claim": {"candidate_id": claim_name, "package": package,
                                    "status": "handoff_ready", "attempts": 1}})
    state_claim.write_text(payload, encoding="utf-8")
    worktree_claim = root / "worktrees" / batch / package / ".nl2repo" / "authoring-claim.json"
    worktree_claim.parent.mkdir(parents=True, exist_ok=True)
    worktree_claim.write_text(payload, encoding="utf-8")
    return str(state_claim), str(worktree_claim)


def _attach_artifacts(root: Path, language: str, artifacts: list[object]) -> None:
    state_path = root / "queues" / f"{language}-wave2-20260828.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["items"][f"{language}-candidate"]["artifacts"] = artifacts
    state_path.write_text(json.dumps(state), encoding="utf-8")


def _import_case(root: Path, name: str) -> sqlite3.Connection:
    database = root.parent / f"{name}.sqlite3"
    import_manifest(generate_manifest(root, cutover_id=name), root, db_path=database, dry_run=False)
    return sqlite3.connect(database)


def _artifact_rows(db: sqlite3.Connection, candidate_id: str) -> list[tuple[str, ...]]:
    return list(db.execute(
        "SELECT a.artifact_id, a.path, a.sha256, a.size_bytes, a.secret_scan_status, "
        "a.task_id IS NOT NULL FROM artifacts a JOIN tasks t ON t.task_id=a.task_id "
        "WHERE t.candidate_id=? ORDER BY a.path",
        (candidate_id,),
    ))


PYTHON_TASK = "base-python-python-author-wave2-20260828:python-candidate:legacy"
PYTHON_BATCH = "python-author-wave2-20260828"


def _legacy_artifact_id(task_id: str, path: str, digest: str) -> str:
    """Independent copy of the pinned contract: legacy:<sha256 of canonical JSON>."""
    canonical = json.dumps(
        {"path": path, "sha256": digest, "task_id": task_id},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return "legacy:" + hashlib.sha256(canonical).hexdigest()


def test_import_keeps_mirror_claim_evidence_as_distinct_task_scoped_artifacts(tmp_path: Path) -> None:
    """The frozen failure: two byte-identical claim mirrors in one task both persist."""
    root = _live_case(tmp_path, "mirror")
    state_claim, worktree_claim = _mirror_claim_files(root, PYTHON_BATCH, "python-pkg", "python-candidate")
    _attach_artifacts(root, "python", [state_claim, worktree_claim])
    rows = _artifact_rows(_import_case(root, "mirror"), "python-candidate")

    assert [row[1] for row in rows] == sorted([worktree_claim, state_claim])
    digest = hashlib.sha256(Path(state_claim).read_bytes()).hexdigest()
    assert {row[0] for row in rows} == {
        _legacy_artifact_id(PYTHON_TASK, state_claim, digest),
        _legacy_artifact_id(PYTHON_TASK, worktree_claim, digest),
    }
    assert {row[2] for row in rows} == {digest}
    for artifact_id, _, _, size_bytes, scan, bound in rows:
        assert artifact_id.startswith("legacy:") and len(artifact_id) == 71
        assert size_bytes == Path(state_claim).stat().st_size > 0
        assert scan == "passed" and bound == 1


def test_import_deduplicates_exact_duplicate_evidence_in_one_task(tmp_path: Path) -> None:
    """A repeated (task, path, digest) binding is one artifact, even when spelled differently."""
    root = _live_case(tmp_path, "duplicate")
    state_claim, worktree_claim = _mirror_claim_files(root, PYTHON_BATCH, "python-pkg", "python-candidate")
    misspelled = str(root / "state" / PYTHON_BATCH / "claims" / ".." / "claims" / "python-candidate.json")
    _attach_artifacts(root, "python", [state_claim, state_claim, misspelled, worktree_claim])
    rows = _artifact_rows(_import_case(root, "duplicate"), "python-candidate")

    assert [row[1] for row in rows] == sorted([worktree_claim, state_claim])


def test_import_rejects_one_artifact_path_carrying_two_digests(tmp_path: Path) -> None:
    """Two different digests for one task path is a contradiction, not a dedupe."""
    root = _live_case(tmp_path, "conflict")
    retired = str(root / "state" / PYTHON_BATCH / "claims" / "python-candidate.json")
    _attach_artifacts(root, "python", [
        {"path": retired, "sha256": "a" * 64, "size_bytes": 4},
        {"path": retired, "sha256": "b" * 64, "size_bytes": 4},
    ])
    with pytest.raises(MigrationError, match="carries two digests"):
        _import_case(root, "conflict")


def test_import_rejects_artifact_paths_without_a_usable_identity(tmp_path: Path) -> None:
    """Evidence identity needs a non-empty, NUL-free, file-scoped path."""
    declared = "c" * 64
    cases = (
        ({"path": "", "sha256": declared, "size_bytes": 1}, "empty"),
        ({"path": "   ", "sha256": declared, "size_bytes": 1}, "empty"),
        ({"path": "/tmp/nul\x00claim.json", "sha256": declared, "size_bytes": 1}, "NUL"),
        ("/", "file-scoped"),
    )
    for index, (artifact, message) in enumerate(cases):
        name = f"bad-path-{index}"
        root = _live_case(tmp_path, name)
        _attach_artifacts(root, "python", [artifact])
        with pytest.raises(MigrationError, match=message):
            _import_case(root, name)


def test_import_keeps_shared_evidence_bound_to_every_task_that_references_it(tmp_path: Path) -> None:
    """One physical path used by two tasks must not collapse task association."""
    root = _live_case(tmp_path, "shared")
    node_batch = "node-author-wave2-20260828"
    shared = root / "state" / PYTHON_BATCH / "claims" / "python-candidate.json"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text(json.dumps({"claim": {"candidate_id": "shared"}}), encoding="utf-8")
    mirror = root / "worktrees" / node_batch / "node-pkg" / ".nl2repo" / "authoring-claim.json"
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_text(json.dumps({"claim": {"candidate_id": "other"}}), encoding="utf-8")
    _attach_artifacts(root, "python", [str(shared)])
    _attach_artifacts(root, "node", [str(shared), str(mirror)])
    db = _import_case(root, "shared")
    rows = list(db.execute(
        "SELECT t.candidate_id, a.task_id, a.sha256 FROM artifacts a JOIN tasks t ON t.task_id=a.task_id "
        "WHERE a.path=? ORDER BY t.candidate_id", (str(shared),),
    ))

    assert len(rows) == 2
    assert {row[0] for row in rows} == {"node-candidate", "python-candidate"}
    assert len({row[1] for row in rows}) == 2
    assert len({row[2] for row in rows}) == 1


def test_taskless_artifact_identity_stays_globally_unique(tmp_path: Path) -> None:
    """Task-scoped uniqueness must not let an unbound evidence row be attached twice."""
    scheduler = Scheduler(tmp_path / "artifacts.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    insert = (
        "INSERT INTO artifacts(artifact_id,task_id,trial_id,kind,path,sha256,size_bytes,"
        "secret_scan_status,created_at) VALUES(?,NULL,NULL,'legacy-reference',?,?,'0','passed',datetime('now'))"
    )
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed: artifacts.path"):
        with scheduler.connect() as db:
            db.execute(insert, ("legacy-unbound-1", "/tmp/unbound.json", "d" * 64))
            db.execute(insert, ("legacy-unbound-2", "/tmp/unbound.json", "d" * 64))
    with scheduler.connect() as db:
        db.execute(insert, ("legacy-unbound-3", "/tmp/other.json", "d" * 64))
        db.execute(insert, ("legacy-unbound-4", "/tmp/unbound.json", "e" * 64))
    with scheduler.connect() as db:
        assert sorted(str(row[0]) for row in db.execute("SELECT artifact_id FROM artifacts")) == [
            "legacy-unbound-1", "legacy-unbound-3", "legacy-unbound-4",
        ]


def test_backup_verify_tamper_restore_dry_run_and_activation_guard(tmp_path: Path) -> None:
    scheduler = Scheduler(tmp_path / "source.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    backup_dir = tmp_path / "backup"
    backup_database(scheduler.path, backup_dir)
    assert verify_backup(backup_dir)["verified"] is True
    target = tmp_path / "restored.sqlite3"
    marker = issue_development_quiescence_receipt(backup_dir, target, tmp_path / "authority")
    dry = restore_database(backup_dir, target, quiescence_marker=marker)
    assert dry["dry_run"] is True and not target.exists()
    with pytest.raises(MigrationError, match="explicit"):
        activate_database(backup_dir / "database.sqlite3", target)
    restore_database(backup_dir, target, quiescence_marker=marker, activate=True)
    with pytest.raises(MigrationError, match="already used"):
        restore_database(backup_dir, target, quiescence_marker=marker, activate=True)
    assert verify_backup(backup_dir)["verified"] is True
    (backup_dir / "database.sqlite3").write_bytes(b"tampered")
    with pytest.raises(MigrationError, match="checksum"):
        verify_backup(backup_dir)


def test_uncheckpointed_wal_is_included_in_online_backup(tmp_path: Path) -> None:
    source = Scheduler(tmp_path / "wal.sqlite3", supplied_root=tmp_path)
    source.init()
    with source.connect() as db:
        db.execute("INSERT INTO schema_meta(key,value) VALUES('wal_test','present')")
    backup_dir = tmp_path / "wal-backup"
    backup_database(source.path, backup_dir)
    with sqlite3.connect(backup_dir / "database.sqlite3") as db:
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


def test_production_receipt_refuses_unobserved_quiescence(tmp_path: Path) -> None:
    scheduler = Scheduler(tmp_path / "source.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    backup_dir = tmp_path / "backup"
    backup_database(scheduler.path, backup_dir)
    with pytest.raises(MigrationError, match="cutover-grade evidence"):
        issue_quiescence_receipt(backup_dir, tmp_path / "target.sqlite3")


def test_quiescence_receipt_hmac_and_backup_destination_safety(tmp_path: Path) -> None:
    scheduler = Scheduler(tmp_path / "source.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    backup_dir = tmp_path / "backup"
    backup_database(scheduler.path, backup_dir)
    target = tmp_path / "target.sqlite3"
    receipt = issue_development_quiescence_receipt(backup_dir, target, tmp_path / "authority")
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["generation"] = 1
    receipt.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(MigrationError, match="HMAC"):
        restore_database(backup_dir, target, quiescence_marker=receipt)
    outside = tmp_path / "outside"
    outside.write_text("outside", encoding="utf-8")
    destination = tmp_path / "backup-link"
    destination.symlink_to(outside)
    with pytest.raises(MigrationError, match="new directory"):
        backup_database(scheduler.path, destination)
