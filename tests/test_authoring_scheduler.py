# ruff: noqa: E501
from __future__ import annotations

import importlib.util
import json
import multiprocessing
import os
import sqlite3
import time
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path

import pytest

from nl2repobench.authoring.scheduler import (
    STATUS_SCHEMA_VERSION,
    ActorFence,
    BusyError,
    ConflictError,
    Identity,
    LostLeaseError,
    Scheduler,
    ValidationError,
    readonly_status,
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
    scheduler.register_actor("integration", "integration-owner", "integration", pid=3, process_starttime_ticks=3, boot_id="boot")
    scheduler.register_actor("archive", "archive-owner", "archive", pid=4, process_starttime_ticks=4, boot_id="boot")
    scheduler.register_actor("supervisor", "supervisor-owner", "supervisor", pid=5, process_starttime_ticks=5, boot_id="boot")
    scheduler.acquire_singleton("integration", "integration", "integration-owner", pid=3, process_starttime_ticks=3, boot_id="boot")
    scheduler.acquire_singleton("archive", "archive", "archive-owner", pid=4, process_starttime_ticks=4, boot_id="boot")
    scheduler.acquire_singleton("supervisor", "supervisor", "supervisor-owner", pid=5, process_starttime_ticks=5, boot_id="boot")
    return scheduler


def _actor(scheduler: Scheduler, scope: str) -> ActorFence:
    with scheduler.connect() as db:
        row = db.execute("SELECT * FROM scheduler_leases WHERE scope=? AND active=1", (scope,)).fetchone()
    pid = {"integration": 3, "archive": 4, "supervisor": 5}[scope]
    return ActorFence(scope, row["lease_id"], row["generation"], scope, f"{scope}-owner", pid, pid, "boot")


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


def _prepared_cutover_scheduler(tmp_path: Path) -> Scheduler:
    scheduler = Scheduler(tmp_path / "state/scheduler.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
        reason="prepared disabled configuration",
    )
    scheduler.prepare_cutover_barrier("cutover", "a" * 64)
    return scheduler


def test_prepared_cutover_first_enable_uses_exact_bounded_configuration(
    tmp_path: Path,
) -> None:
    scheduler = _prepared_cutover_scheduler(tmp_path)

    version = scheduler.first_enable()

    config = scheduler.runtime_config()
    assert version == config["config_version"]
    assert (
        config["enabled"],
        config["max_total_controllers"],
        config["controller_concurrency"],
        config["max_integrations"],
        config["agent_limit"],
    ) == (1, 1, 1, 0, 1)
    with scheduler.connect() as db:
        barrier = db.execute("SELECT state,first_effect_kind FROM cutover_barrier").fetchone()
    assert tuple(barrier) == ("sealed", "first-enable")


def test_sealed_enabled_configuration_can_change_bounded_limits(tmp_path: Path) -> None:
    scheduler = _prepared_cutover_scheduler(tmp_path)
    scheduler.first_enable()

    version = scheduler.configure(
        enabled=True,
        max_total_controllers=2,
        controller_concurrency=2,
        max_integrations=0,
        agent_limit=2,
        reason="bounded expansion",
    )

    config = scheduler.runtime_config()
    assert config["config_version"] == version
    assert (
        config["enabled"],
        config["max_total_controllers"],
        config["controller_concurrency"],
        config["max_integrations"],
        config["agent_limit"],
    ) == (1, 2, 2, 0, 2)


def test_sealed_disabled_configuration_rejects_reenable_without_file_mutation(
    tmp_path: Path,
) -> None:
    scheduler = _prepared_cutover_scheduler(tmp_path)
    scheduler.first_enable()
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
        reason="bounded shutdown",
    )
    before_bytes = scheduler.path.read_bytes()
    before_config = scheduler.runtime_config()

    with pytest.raises(
        ConflictError,
        match="sealed cutover cannot be re-enabled; a fresh cutover is required",
    ):
        scheduler.configure(enabled=True)

    assert scheduler.path.read_bytes() == before_bytes
    assert scheduler.runtime_config() == before_config


def test_sealed_missing_configuration_rejects_reenable_without_inserting_config(
    tmp_path: Path,
) -> None:
    scheduler = _prepared_cutover_scheduler(tmp_path)
    scheduler.first_enable()
    with scheduler.connect() as db:
        db.execute("DELETE FROM runtime_config")

    before_bytes = scheduler.path.read_bytes()
    with scheduler.connect() as db:
        before_count = db.execute("SELECT count(*) FROM runtime_config").fetchone()[0]
    assert before_count == 0

    with pytest.raises(
        ConflictError,
        match="sealed cutover cannot be re-enabled; a fresh cutover is required",
    ):
        scheduler.configure(enabled=True)

    assert scheduler.path.read_bytes() == before_bytes
    with scheduler.connect() as db:
        assert db.execute("SELECT count(*) FROM runtime_config").fetchone()[0] == 0


def test_release_identity_allows_new_terminal_release(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    first = _task(scheduler, "same", "r1")
    scheduler.transition(first, "blocked", reason="operator decision", operator_actor=_actor(scheduler, "supervisor"))
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
    scheduler.register_actor("watcher-test", "watcher-owner", "watcher", pid=6, process_starttime_ticks=6, boot_id="boot")
    first, generation = scheduler.acquire_singleton("watcher", "watcher-test", "watcher-owner", pid=6, process_starttime_ticks=6, boot_id="boot")
    assert generation == 1
    with pytest.raises(ConflictError):
        scheduler.acquire_singleton("watcher", "watcher-test", "watcher-owner", pid=6, process_starttime_ticks=6, boot_id="boot")
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
    integration_actor = _actor(scheduler, "integration")
    receipt = scheduler.begin_operation(task_id, "integration", "integration-key", actor=integration_actor)
    scheduler.fail_operation(receipt, "infrastructure", "network reset", actor=integration_actor)
    assert scheduler.claim_next("controller", "owner") == []
    with scheduler.connect() as db:
        assert (
            db.execute("SELECT state FROM tasks WHERE task_id=?", (task_id,)).fetchone()[0]
            == "integration_retry"
        )
    with pytest.raises(ConflictError, match="not ready"):
        scheduler.complete(task_id, "not yet")


def test_archive_cleanup_are_receipt_fenced_and_completion_chain(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "chain")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    integration_actor = _actor(scheduler, "integration")
    archive_actor = _actor(scheduler, "archive")
    integration = scheduler.begin_operation(task_id, "integration", "chain-integration", actor=integration_actor)
    with pytest.raises(ConflictError, match="pushed integration"):
        scheduler.begin_operation(task_id, "archive", "chain-archive", actor=archive_actor)
    scheduler.update_receipt(integration, "pushed", actor=integration_actor, commit_sha="c" * 40, external_ref="refs/heads/main")
    archive = scheduler.begin_operation(task_id, "archive", "chain-archive", actor=archive_actor)
    with pytest.raises(ConflictError, match="verified archive"):
        scheduler.begin_operation(task_id, "cleanup", "chain-cleanup", actor=archive_actor)
    scheduler.update_receipt(
        archive, "verified", actor=archive_actor, manifest_key="m", manifest_sha256="a" * 64,
        source_snapshot_sha256="b" * 64, object_count=1, byte_count=1, evidence_sha256="d" * 64,
    )
    cleanup = scheduler.begin_operation(task_id, "cleanup", "chain-cleanup", actor=archive_actor)
    scheduler.update_receipt(cleanup, "applied", actor=archive_actor, evidence_path="cleanup.json", evidence_sha256="e" * 64)
    scheduler.complete(task_id, "published")
    with scheduler.connect() as db:
        assert db.execute("SELECT state FROM tasks WHERE task_id=?", (task_id,)).fetchone()[0] == "complete"


def test_authoring_infrastructure_finish_retries_and_noninfra_blocks(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    retry_task = _task(scheduler, "authoring-infra", retry_limit=2)
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=False,
                     failure_class="infrastructure", reason="worker crashed")
    with scheduler.connect() as db:
        row = db.execute("SELECT state,retry_count,next_retry_at FROM tasks WHERE task_id=?", (retry_task,)).fetchone()
    assert row[0] == "pending" and row[1] == 1 and row[2] is not None
    blocked_task = _task(scheduler, "authoring-source", retry_limit=2)
    claim2 = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim2.claim_id, "owner", "controller")
    scheduler.start(claim2.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim2.claim_id, "owner", "controller", success=False,
                     failure_class="source", reason="invalid source")
    with scheduler.connect() as db:
        assert db.execute("SELECT state FROM tasks WHERE task_id=?", (blocked_task,)).fetchone()[0] == "blocked"


def test_malformed_receipt_metadata_is_rejected(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "metadata")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    actor = _actor(scheduler, "integration")
    receipt = scheduler.begin_operation(task_id, "integration", "metadata-integration", actor=actor)
    with pytest.raises(ValidationError, match="commit_sha"):
        scheduler.update_receipt(receipt, "pushed", actor=actor, commit_sha="bad", external_ref="refs/heads/main")
    with scheduler.connect() as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "UPDATE operation_receipts SET status='pushed',commit_sha='x',external_ref='refs/main' WHERE receipt_id=?",
                (receipt,),
            )


def test_generic_transition_cannot_bypass_claim_lifecycle(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "transition")
    with pytest.raises(ValidationError, match="invalid task state"):
        scheduler.transition(task_id, "claimed")
    claim = scheduler.claim_next("controller", "owner")[0]
    with pytest.raises(ValidationError, match="invalid task state"):
        scheduler.transition(task_id, "handoff_ready")
    scheduler.transition(task_id, "blocked", reason="operator", operator_actor=_actor(scheduler, "supervisor"), owner_uuid="owner", controller_id="controller", generation=claim.generation, pid=1, process_starttime_ticks=0, boot_id="test")


def test_operator_can_exclude_post_authoring_and_post_operation(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    post_authoring = _task(scheduler, "exclude-authored")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    scheduler.transition(
        post_authoring, "excluded", reason="operator exclusion",
        operator_actor=_actor(scheduler, "supervisor"),
    )
    post_operation = _task(scheduler, "exclude-operation")
    claim2 = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim2.claim_id, "owner", "controller")
    scheduler.start(claim2.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim2.claim_id, "owner", "controller", success=True)
    scheduler.begin_operation(
        post_operation, "integration", "exclude-integration",
        actor=_actor(scheduler, "integration"),
    )
    scheduler.transition(
        post_operation, "excluded", reason="operator exclusion",
        operator_actor=_actor(scheduler, "supervisor"),
    )
    with scheduler.connect() as db:
        states = dict(db.execute(
            "SELECT task_id,state FROM tasks WHERE task_id IN (?,?)",
            (post_authoring, post_operation),
        ).fetchall())
    assert states == {post_authoring: "excluded", post_operation: "excluded"}


def test_generic_receipt_update_rejects_failure_and_collision(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "collision")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    integration_actor = _actor(scheduler, "integration")
    archive_actor = _actor(scheduler, "archive")
    integration = scheduler.begin_operation(
        task_id, "integration", "collision-integration", actor=integration_actor
    )
    scheduler.update_receipt(
        integration, "pushed", actor=integration_actor,
        commit_sha="c" * 40, external_ref="refs/heads/main",
    )
    archive = scheduler.begin_operation(
        task_id, "archive", "collision-archive", actor=archive_actor
    )
    with pytest.raises(ValidationError, match="invalid receipt status"):
        scheduler.update_receipt(
            archive, "collision", actor=archive_actor,
            failure_class="infrastructure", failure_reason="remote exists",
        )
    scheduler.collide_operation(
        archive, "infrastructure", "remote object already exists",
        evidence_path="evidence/collision.json", evidence_sha256="a" * 64,
        actor=archive_actor,
    )
    with scheduler.connect() as db:
        receipt = db.execute(
            "SELECT status,failure_class,evidence_sha256 FROM operation_receipts WHERE receipt_id=?",
            (archive,),
        ).fetchone()
        task = db.execute("SELECT state FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    assert tuple(receipt) == ("collision", "infrastructure", "a" * 64)
    assert task[0] == "blocked"


def test_spawn_failure_releases_reservation_immediately(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    token = scheduler.reserve_controller("lane", "spawn-owner", 1)
    with pytest.raises(ConflictError, match="not releasable"):
        scheduler.release_controller_reservation(token, "other-owner")
    scheduler.release_controller_reservation(token, "spawn-owner", reason="Popen failed")
    with pytest.raises(ConflictError):
        scheduler.release_controller_reservation(token, "spawn-owner")
    with scheduler.connect() as db:
        assert db.execute("SELECT state FROM controller_slot_reservations WHERE reservation_token=?", (token,)).fetchone()[0] == "released"
        assert db.execute("SELECT used_count FROM capacity_rows WHERE capacity_unit='controller_slot' AND capacity_kind='global'").fetchone()[0] == 1


def test_fairness_dispatch_advances_language_and_lane_sequence(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    _task(scheduler, "python-task")
    scheduler.add_lane("node-lane", "node-batch", "node")
    identity = _identity("node-task", "node")
    scheduler.add_identity(identity)
    scheduler.add_candidate("node-task", "node-lane", identity.digest)
    scheduler.add_task("task-node-task-r1", "node-task", "node-lane", "r1")
    assert scheduler.dispatch_next_lane() == "lane"
    assert scheduler.dispatch_next_lane() == "node-lane"
    with scheduler.connect() as db:
        rows = db.execute("SELECT lane_id,last_dispatch_seq FROM lanes ORDER BY last_dispatch_seq").fetchall()
        fairness = db.execute("SELECT next_language_index,dispatch_sequence FROM fairness_state WHERE fairness_id=1").fetchone()
    assert [tuple(row) for row in rows] == [("lane", 1), ("node-lane", 2)]
    assert tuple(fairness) == (2, 2)


def test_fairness_dispatch_skips_tasks_outside_retry_and_attempt_budget(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "ineligible")
    with scheduler.connect() as db:
        db.execute(
            "UPDATE tasks SET next_retry_at='2999-01-01T00:00:00+00:00' WHERE task_id=?",
            (task_id,),
        )
    assert scheduler.dispatch_next_lane(now="2026-01-01T00:00:00+00:00") is None
    with scheduler.connect() as db:
        db.execute(
            "UPDATE tasks SET next_retry_at=NULL,authoring_attempts=attempt_limit WHERE task_id=?",
            (task_id,),
        )
    assert scheduler.dispatch_next_lane() is None


def test_cli_derives_current_process_identity_and_exposes_generation() -> None:
    path = Path(__file__).parents[1] / "scripts/authoring_scheduler.py"
    spec = importlib.util.spec_from_file_location("authoring_scheduler_cli", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pid, starttime, boot_id = module._process_identity(None, None, None)
    assert pid == os.getpid() and starttime > 0 and boot_id
    args = module.parser().parse_args(["--root", "/tmp", "--db", "/tmp/scheduler.sqlite3", "heartbeat", "--claim", "c", "--controller", "x", "--owner", "o", "--generation", "4"])
    assert args.generation == 4


def test_cli_success_and_error_envelopes_share_the_status_schema_version(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = Path(__file__).parents[1] / "scripts/authoring_scheduler.py"
    spec = importlib.util.spec_from_file_location("authoring_scheduler_cli", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    database = tmp_path / "state/scheduler.sqlite3"
    assert module.main(["--root", str(tmp_path), "--db", str(database), "init"]) == 0
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["schema_version"] == STATUS_SCHEMA_VERSION == "authoring-scheduler/v4"
    assert envelope["command"] == "init" and envelope["error"] is None
    assert module.main(["--root", str(tmp_path), "--db", str(database), "status"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["schema_version"] == "authoring-scheduler/v4"
    assert status["data"]["schema_version"] == "authoring-scheduler/v4"
    assert module.main(["--root", str(tmp_path), "--db", "/outside/scheduler.sqlite3", "init"]) == 2
    failure = json.loads(capsys.readouterr().out)
    assert failure["schema_version"] == "authoring-scheduler/v4"
    assert failure["error"] == "database must be under supplied root"


def _cli_module():
    path = Path(__file__).parents[1] / "scripts/authoring_scheduler.py"
    spec = importlib.util.spec_from_file_location("authoring_scheduler_cli_status", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_readonly_status_and_init_share_the_stored_schema_gate(tmp_path: Path) -> None:
    """A v4 envelope may only come from a DB that proves it is v4.

    ``init`` already fenced the stored version, but the read-only status path
    is a separate emitter: without the same gate a structurally readable v3
    file would be reported under ``authoring-scheduler/v4``.
    """
    database = tmp_path / "state/scheduler.sqlite3"
    scheduler = Scheduler(database, supplied_root=tmp_path)
    scheduler.init()
    with scheduler.connect() as db:
        db.execute("UPDATE schema_meta SET value='3' WHERE key='schema_version'")
    for observe in (readonly_status, lambda path: Scheduler(path, supplied_root=tmp_path).status()):
        with pytest.raises(ValidationError, match="incompatible scheduler schema version"):
            observe(database)
    with pytest.raises(ValidationError, match="incompatible scheduler schema version"):
        scheduler.init()
    with scheduler.connect() as db:
        db.execute("UPDATE schema_meta SET value='4' WHERE key='schema_version'")
        db.execute("DROP TABLE legacy_archive_evidence")
    with pytest.raises(ValidationError, match="incomplete scheduler schema"):
        readonly_status(database)
    with pytest.raises(ValidationError, match="incomplete scheduler schema"):
        scheduler.init()


def test_cli_status_reports_typed_error_for_a_v3_database(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI ``status`` bypasses ``init``, so its own rejection must be typed."""
    module = _cli_module()
    database = tmp_path / "state/scheduler.sqlite3"
    assert module.main(["--root", str(tmp_path), "--db", str(database), "init"]) == 0
    capsys.readouterr()
    with sqlite3.connect(database) as db:
        db.execute("UPDATE schema_meta SET value='3' WHERE key='schema_version'")
    assert module.main(["--root", str(tmp_path), "--db", str(database), "status"]) == 2
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["error"] == "incompatible scheduler schema version"
    assert envelope["schema_version"] == STATUS_SCHEMA_VERSION
    assert envelope["data"] == {}


def test_receipt_idempotency_checks_context_and_failure_is_conditional(tmp_path: Path) -> None:
    scheduler = _scheduler(tmp_path)
    task_id = _task(scheduler, "receipt")
    claim = scheduler.claim_next("controller", "owner")[0]
    scheduler.prepare(claim.claim_id, "owner", "controller")
    scheduler.start(claim.claim_id, "owner", "controller", child_pid=2, child_starttime_ticks=2)
    scheduler.finish(claim.claim_id, "owner", "controller", success=True)
    integration_actor = _actor(scheduler, "integration")
    receipt = scheduler.begin_operation(task_id, "integration", "same-key", operation_attempt=1, retry_no=0, actor=integration_actor)
    assert scheduler.begin_operation(task_id, "integration", "same-key", operation_attempt=1, retry_no=0, actor=integration_actor) == receipt
    with pytest.raises(ConflictError, match="context mismatch"):
        scheduler.begin_operation(task_id, "archive", "same-key", operation_attempt=1, retry_no=0, actor=_actor(scheduler, "archive"))
    with pytest.raises(LostLeaseError, match="scope"):
        scheduler.fail_operation(receipt, "infrastructure", "wrong actor", actor=_actor(scheduler, "archive"))
    scheduler.fail_operation(receipt, "infrastructure", "temporary", actor=integration_actor)
    with scheduler.connect() as db:
        before = tuple(db.execute("SELECT status,integration_retry_count FROM operation_receipts JOIN tasks USING(task_id) WHERE receipt_id=?", (receipt,)).fetchone())
    scheduler.fail_operation(receipt, "infrastructure", "replayed", actor=integration_actor)
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
    scheduler.transition(task_id, "blocked", reason="operator", operator_actor=_actor(scheduler, "supervisor"), owner_uuid="owner", controller_id="controller", generation=claim.generation, pid=1, process_starttime_ticks=0, boot_id="test")
    operator = _actor(scheduler, "supervisor")
    lease, generation = operator.lease_id, operator.generation
    with pytest.raises(LostLeaseError):
        scheduler.heartbeat_singleton(lease, "supervisor", "supervisor", "supervisor-owner", generation, pid=5, process_starttime_ticks=8, boot_id="boot")
    scheduler.heartbeat_singleton(lease, "supervisor", "supervisor", "supervisor-owner", generation, pid=5, process_starttime_ticks=5, boot_id="boot")
    scheduler.release_singleton(lease, "supervisor", "supervisor", "supervisor-owner", generation, pid=5, process_starttime_ticks=5, boot_id="boot")
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
