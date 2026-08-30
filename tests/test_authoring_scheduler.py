# ruff: noqa: E501
from __future__ import annotations

import multiprocessing
import sqlite3
import time
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path

import pytest

from nl2repobench.authoring.scheduler import (
    BusyError,
    ConflictError,
    Identity,
    LostLeaseError,
    Scheduler,
    ValidationError,
)


def _identity(name: str, language: str = "python") -> Identity:
    return Identity(
        sha256(name.encode()).hexdigest(),
        language,
        name,
        "https://example.invalid/repo",
        "test",
        "b" * 40,
    )


def _scheduler(tmp_path: Path) -> Scheduler:
    scheduler = Scheduler(tmp_path / "state/scheduler.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(enabled=True)
    scheduler.add_lane("lane", "batch", "python")
    for unit, kind, key, limit in (
        ("active_claim", "global", "claims", 10),
        ("active_claim", "agent", "authoring", 10),
        ("active_claim", "language", "python", 10),
        ("active_claim", "controller", "controller", 10),
        ("controller_slot", "global", "controllers", 3),
        ("controller_slot", "language", "python", 3),
    ):
        scheduler.capacity(unit, kind, key, limit)
    reservation = scheduler.reserve_controller("lane", "owner", 0)
    scheduler.register_controller(
        "controller", "owner", "lane", "python", 0, reservation_token=reservation
    )
    return scheduler


def _task(
    scheduler: Scheduler, name: str = "candidate", release: str = "r1", *, retry_limit: int = 3,
    release_limit: int = 3,
) -> str:
    identity = _identity(name)
    with scheduler.connect() as db:
        exists = db.execute(
            "SELECT 1 FROM candidates WHERE candidate_id=? AND lane_id=?", (name, "lane")
        ).fetchone()
    if exists is None:
        scheduler.add_identity(identity)
        scheduler.add_candidate(name, "lane", identity.digest, 0)
    task_id = f"task-{name}-{release}"
    scheduler.add_task(task_id, name, "lane", release, retry_limit=retry_limit, release_limit=release_limit)
    return task_id


def _claim_process(db: str, root: str, queue: multiprocessing.Queue[object]) -> None:
    scheduler = Scheduler(db, supplied_root=root)
    try:
        queue.put([claim.task_id for claim in scheduler.claim_next("controller", "owner")])
    except Exception as exc:  # pragma: no cover - the parent asserts details
        queue.put(type(exc).__name__)


def test_schema_executes_and_guards_terminal_insert(tmp_path: Path) -> None:
    schema = (
        Path(__file__).parents[1] / "src/nl2repobench/authoring/scheduler_schema.sql"
    ).read_text()
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(schema)
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    with pytest.raises(sqlite3.IntegrityError, match="terminal task insert forbidden"):
        db.execute(
            "INSERT INTO tasks(task_id,candidate_id,lane_id,task_release,state,attempt_limit,retry_limit,created_at,updated_at,terminal_reason) VALUES('x','x','x','x','complete',1,0,'x','x','x')"
        )


def test_release_identity_allows_new_terminal_release(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    first = _task(scheduler, "same", "r1")
    scheduler.transition(first, "blocked", reason="operator decision")
    second = _task(scheduler, "same", "r2")
    assert second != first


def test_claim_prepare_start_heartbeat_finish_and_priority(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    one, two = _task(scheduler, "one"), _task(scheduler, "two")
    with scheduler.connect() as db:
        db.execute(
            "UPDATE tasks SET priority_until=? WHERE task_id=?",
            ((datetime.now(UTC) + timedelta(hours=1)).isoformat(), two),
        )
    claim = scheduler.claim_next("controller", "owner")[0]
    assert claim.task_id == two
    assert claim.generation == 1
    with scheduler.connect() as db:
        trial = db.execute(
            "SELECT state,started_at FROM trials WHERE trial_id=?", (claim.trial_id,)
        ).fetchone()
        assert tuple(trial) == ("created", None)
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.heartbeat(claim.claim_id, "owner", "controller")
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    with scheduler.connect() as db:
        released = db.execute(
            "SELECT released_at,release_reason,updated_at FROM claims WHERE claim_id=?",
            (claim.claim_id,),
        ).fetchone()
        assert released[0] is not None and released[1] == "finished"
        assert released[2] is not None
        assert (
            db.execute("SELECT state FROM tasks WHERE task_id=?", (two,)).fetchone()[0]
            == "handoff_ready"
        )
        assert (
            db.execute("SELECT state FROM tasks WHERE task_id=?", (one,)).fetchone()[0] == "pending"
        )


def test_multiprocess_claim_has_one_winner(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler)
    queue: multiprocessing.Queue[object] = multiprocessing.Queue()
    workers = [
        multiprocessing.Process(
            target=_claim_process, args=(str(scheduler.path), str(tmp_path), queue)
        )
        for _ in range(4)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(10)
    received = [queue.get(timeout=2) for _ in workers]
    assert sum(item == [task_id] for item in received) == 1
    assert sum(item == [] for item in received) == 3


def test_reservation_capacity_and_lane_only_event(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    token = scheduler.reserve_controller("lane", "spawn-owner", 1)
    with scheduler.connect() as db:
        assert (
            db.execute(
                "SELECT count(*) FROM events WHERE lane_id='lane' AND task_id IS NULL"
            ).fetchone()[0]
            == 2
        )
        assert (
            db.execute(
                "SELECT used_count FROM capacity_rows WHERE capacity_unit='controller_slot' AND capacity_kind='global'"
            ).fetchone()[0]
            == 2
        )
    scheduler.activate_controller(
        token,
        "spawned",
        "spawn-owner",
        pid=2,
        process_starttime_ticks=2,
        boot_id="boot",
        executable_digest="c" * 64,
        argv_digest="d" * 64,
    )
    with pytest.raises(ConflictError):
        scheduler.reserve_controller("lane", "another", 1)


def test_singleton_history_and_reservation_expiry(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    scheduler.register_actor("supervisor", "supervisor-owner", "supervisor")
    first, generation = scheduler.acquire_singleton("supervisor", "supervisor", "supervisor-owner")
    assert generation == 1
    with pytest.raises(ConflictError):
        scheduler.acquire_singleton("supervisor", "supervisor", "supervisor-owner")
    token = scheduler.reserve_controller("lane", "reserver", 2, ttl_seconds=5)
    del token
    assert scheduler.reconcile_reservations(now="2999-01-01T00:00:00+00:00") == 1
    with scheduler.connect() as db:
        assert (
            db.execute(
                "SELECT count(*) FROM scheduler_leases WHERE lease_id=?", (first,)
            ).fetchone()[0]
            == 1
        )
        assert (
            db.execute(
                "SELECT used_count FROM capacity_rows WHERE capacity_unit='controller_slot' AND capacity_kind='global'"
            ).fetchone()[0]
            == 1
        )


def test_capacity_dimensions_release_bound_and_heartbeat_stale_race(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    scheduler.capacity("active_claim", "global", "claims", 1)
    _task(scheduler, "a", release_limit=1)
    _task(scheduler, "b")
    first = scheduler.claim_next("controller", "owner", requested_limit=8)
    assert len(first) == 1
    claim = first[0]
    scheduler.release(claim.claim_id, "owner", "controller")
    with pytest.raises(LostLeaseError):
        scheduler.release(claim.claim_id, "owner", "controller")
    new_claim = scheduler.claim_next("controller", "owner")[0]
    assert new_claim.generation == 1
    scheduler.release(new_claim.claim_id, "owner", "controller")
    reclaimed = scheduler.claim_next("controller", "owner")[0]
    assert reclaimed.task_id == "task-a-r1"
    assert reclaimed.generation == 2
    with pytest.raises(ConflictError, match="release limit"):
        scheduler.release(reclaimed.claim_id, "owner", "controller", reclaimed.generation)
    scheduler.heartbeat(reclaimed.claim_id, "owner", "controller", reclaimed.generation)
    assert scheduler.reconcile_stale(now="2000-01-01T00:00:00+00:00") == 0


def test_operation_retry_never_returns_to_authoring_and_completion_guards(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler)
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    receipt = scheduler.begin_operation(task_id, "integration", "integration-key")
    scheduler.fail_operation(receipt, "infrastructure", "network reset")
    assert scheduler.claim_next("controller", "owner") == []
    with scheduler.connect() as db:
        assert (
            db.execute("SELECT state FROM tasks WHERE task_id=?", (task_id,)).fetchone()[0]
            == "integration_retry"
        )
    with pytest.raises(sqlite3.IntegrityError, match="pushed integration required"):
        scheduler.transition(task_id, "complete", reason="not yet")


def test_archive_cleanup_are_receipt_fenced_and_completion_chain(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "chain")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    integration = scheduler.begin_operation(task_id, "integration", "chain-integration")
    with pytest.raises(ConflictError, match="pushed integration"):
        scheduler.begin_operation(task_id, "archive", "chain-archive")
    scheduler.update_receipt(integration, "pushed", commit_sha="c" * 40)
    archive = scheduler.begin_operation(task_id, "archive", "chain-archive")
    with pytest.raises(ConflictError, match="verified archive"):
        scheduler.begin_operation(task_id, "cleanup", "chain-cleanup")
    scheduler.update_receipt(
        archive, "verified", manifest_key="m", manifest_sha256="a" * 64,
        source_snapshot_sha256="b" * 64, object_count=1, byte_count=1, evidence_sha256="d" * 64,
    )
    cleanup = scheduler.begin_operation(task_id, "cleanup", "chain-cleanup")
    scheduler.update_receipt(cleanup, "applied", evidence_path="cleanup.json", evidence_sha256="e" * 64)
    scheduler.transition(task_id, "complete", reason="published")
    with scheduler.connect() as db:
        assert db.execute("SELECT state FROM tasks WHERE task_id=?", (task_id,)).fetchone()[0] == "complete"


def test_receipt_idempotency_checks_context_and_failure_is_conditional(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "receipt")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    receipt = scheduler.begin_operation(task_id, "integration", "same-key", operation_attempt=1, retry_no=0)
    assert scheduler.begin_operation(task_id, "integration", "same-key", operation_attempt=1, retry_no=0) == receipt
    with pytest.raises(ConflictError, match="context mismatch"):
        scheduler.begin_operation(task_id, "archive", "same-key", operation_attempt=1, retry_no=0)
    scheduler.fail_operation(receipt, "infrastructure", "temporary")
    with scheduler.connect() as db:
        before = tuple(db.execute("SELECT status,integration_retry_count FROM operation_receipts JOIN tasks USING(task_id) WHERE receipt_id=?", (receipt,)).fetchone())
    scheduler.fail_operation(receipt, "infrastructure", "replayed")
    with scheduler.connect() as db:
        after = tuple(db.execute("SELECT status,integration_retry_count FROM operation_receipts JOIN tasks USING(task_id) WHERE receipt_id=?", (receipt,)).fetchone())
    assert before == after


def test_controller_registration_requires_reservation_and_stop_releases_usage(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    with pytest.raises(ConflictError, match="requires a reservation"):
        scheduler.register_controller("bypass", "bypass-owner", "lane", "python", 1)
    scheduler.stop_controller("controller", "owner", pid=1, process_starttime_ticks=0, boot_id="test")
    with scheduler.connect() as db:
        assert db.execute("SELECT state FROM controllers WHERE controller_id='controller'").fetchone()[0] == "stopped"
        assert db.execute("SELECT used_count FROM capacity_rows WHERE capacity_unit='controller_slot' AND capacity_kind='global'").fetchone()[0] == 0


def test_reserved_slots_count_against_controller_configuration(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    scheduler.configure(enabled=True, max_total_controllers=1, controller_concurrency=1)
    with pytest.raises(ConflictError, match="configuration capacity"):
        scheduler.reserve_controller("lane", "another-owner", 1)


def test_reconcile_separates_unstarted_and_running_trials(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    first = _task(scheduler, "unstarted")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    with scheduler.connect() as db:
        db.execute("UPDATE claims SET lease_expires_at='2000-01-01T00:00:00+00:00' WHERE claim_id=?", (claim.claim_id,))
    assert scheduler.reconcile_stale(now="2001-01-01T00:00:00+00:00") == 1
    with scheduler.connect() as db:
        trial = db.execute("SELECT state,started_at,finished_at FROM trials WHERE trial_id=?", (claim.trial_id,)).fetchone()
        assert tuple(trial) == ("stale", None, None)
    second = _task(scheduler, "running")
    claim2 = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim2.claim_id, "owner", "controller", claim2.generation)
    scheduler.start(claim2.claim_id, "owner", "controller", claim2.generation, child_pid=2, child_starttime_ticks=2)
    with scheduler.connect() as db:
        db.execute("UPDATE claims SET lease_expires_at='2000-01-01T00:00:00+00:00' WHERE claim_id=?", (claim2.claim_id,))
    assert scheduler.reconcile_stale(now="2001-01-01T00:00:00+00:00") == 1
    with scheduler.connect() as db:
        trial = db.execute("SELECT state,started_at,finished_at FROM trials WHERE trial_id=?", (claim2.trial_id,)).fetchone()
        assert trial[0] == "stale" and trial[1] is not None and trial[2] is not None
    assert first != second


def test_full_claim_and_singleton_identity_fences(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "fenced")
    claim = scheduler.claim_next("controller", "owner")[0]
    with pytest.raises(LostLeaseError):
        scheduler.prepare(claim.claim_id, "owner", "controller", claim.generation, pid=99)
    with pytest.raises(LostLeaseError):
        scheduler.transition(task_id, "blocked", reason="operator", owner_uuid="owner", controller_id="controller", generation=claim.generation, pid=99, process_starttime_ticks=0, boot_id="test")
    scheduler.transition(task_id, "blocked", reason="operator", owner_uuid="owner", controller_id="controller", generation=claim.generation, pid=1, process_starttime_ticks=0, boot_id="test")
    scheduler.register_actor("supervisor", "supervisor-owner", "supervisor", pid=3, process_starttime_ticks=7, boot_id="boot")
    lease, generation = scheduler.acquire_singleton("supervisor", "supervisor", "supervisor-owner", pid=3, process_starttime_ticks=7, boot_id="boot")
    with pytest.raises(LostLeaseError):
        scheduler.heartbeat_singleton(lease, "supervisor", "supervisor", "supervisor-owner", generation, pid=3, process_starttime_ticks=8, boot_id="boot")
    scheduler.heartbeat_singleton(lease, "supervisor", "supervisor", "supervisor-owner", generation, pid=3, process_starttime_ticks=7, boot_id="boot")
    scheduler.release_singleton(lease, "supervisor", "supervisor", "supervisor-owner", generation, pid=3, process_starttime_ticks=7, boot_id="boot")
    assert task_id.startswith("task-fenced")


def test_launch_intent_reconciliation_does_not_invent_a_running_trial(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "launch")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    with scheduler.connect() as db:
        db.execute("UPDATE trials SET launch_intent_at='2000-01-01T00:00:00+00:00' WHERE trial_id=?", (claim.trial_id,))
    assert scheduler.reconcile_launch_intents(now="2001-01-01T00:00:00+00:00") == 1
    with scheduler.connect() as db:
        trial = db.execute("SELECT state,started_at,finished_at FROM trials WHERE trial_id=?", (claim.trial_id,)).fetchone()
        task = db.execute("SELECT state FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    assert tuple(trial) == ("cancelled", None, None)
    assert task[0] == "pending"


def test_busy_writer_is_mapped_with_bounded_wait(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    held = scheduler.connect()
    held.execute("BEGIN IMMEDIATE")
    started = time.monotonic()
    try:
        with pytest.raises(BusyError):
            scheduler.configure(enabled=True)
    finally:
        held.rollback()
        held.close()
    assert time.monotonic() - started < 5.5


def test_validation_refuses_production_outside_explicit_root(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        Scheduler("/tmp/elsewhere.sqlite3", supplied_root=tmp_path)
