from __future__ import annotations

import errno
import fcntl
import hashlib
import importlib.util
import io
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from nl2repobench.authoring import cutover
from nl2repobench.authoring import migration as authoring_migration
from nl2repobench.authoring.migration import MigrationError
from nl2repobench.authoring.runtime import SingletonActor, process_identity
from nl2repobench.authoring.scheduler import Identity, LostLeaseError, Scheduler


def _script(name: str):
    path = Path(__file__).parents[1] / "scripts" / name
    spec = importlib.util.spec_from_file_location(f"phase3_{path.stem}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


loop = _script("run_authoring_loop.py")
supervisor = _script("authoring_supervisor.py")
archive = _script("archive_authoring_live.py")
installer = _script("install_authoring_sqlite_service.py")


def _scheduler(tmp_path: Path) -> tuple[Scheduler, str, str]:
    scheduler = Scheduler(tmp_path / "scheduler.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(enabled=True, lease_seconds=60, heartbeat_interval_seconds=5)
    scheduler.add_lane("lane", "batch", "python")
    identity = Identity("a" * 64, "python", "demo", "https://example.invalid/demo", "git", "b" * 40)
    scheduler.add_identity(identity)
    scheduler.add_candidate("candidate", "lane", identity.digest)
    scheduler.add_task("task", "candidate", "lane", "r1")
    scheduler.capacity("controller_slot", "global", "controllers", 6)
    scheduler.capacity("controller_slot", "language", "python", 4)
    scheduler.capacity("active_claim", "global", "claims", 6)
    scheduler.capacity("active_claim", "language", "python", 4)
    scheduler.capacity("active_claim", "agent", "authoring", 6)
    owner, controller = "owner", "controller"
    token = scheduler.reserve_controller("lane", owner, 0)
    pid, starttime, boot_id = process_identity()
    scheduler.capacity("active_claim", "controller", controller, 1)
    scheduler.activate_controller(
        token,
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
        executable_digest="c" * 64,
        argv_digest="d" * 64,
    )
    return scheduler, owner, controller


def _finish_authoring(
    scheduler: Scheduler,
    owner: str,
    controller: str,
    worktree: Path,
) -> None:
    pid, starttime, boot_id = process_identity()
    claim = scheduler.claim_next(
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )[0]
    scheduler.prepare(
        claim.claim_id,
        owner,
        controller,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    scheduler.start(
        claim.claim_id,
        owner,
        controller,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
        child_pid=pid,
        child_starttime_ticks=starttime,
    )
    source = worktree / "catalog/sources/demo"
    source.mkdir(parents=True)
    (source / "task.toml").write_text("task_id='demo'\n", encoding="utf-8")
    (worktree / ".nl2repo").mkdir(exist_ok=True)
    handoff = worktree / ".nl2repo/authoring-handoff.json"
    handoff.write_text('{"status":"ready"}\n', encoding="utf-8")
    scheduler.record_handoff(
        claim.claim_id,
        owner,
        controller,
        claim.generation,
        worktree_path=str(worktree),
        worktree_git_head="e" * 40,
        handoff_path=str(handoff),
        handoff_sha256=hashlib.sha256(handoff.read_bytes()).hexdigest(),
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    scheduler.finish(
        claim.claim_id,
        owner,
        controller,
        success=True,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )


def _write_rollback_authorities(
    *,
    database: Path,
    journal: Path,
    barrier: Path,
    repository: Path,
    live_root: Path,
    disabled: dict[str, object],
    cutover_id: str,
    manifest_sha256: str,
) -> None:
    database_digest = hashlib.sha256(database.read_bytes()).hexdigest()
    unit = "nl2repobench-authoring-supervisor-sqlite@phase3.service"
    env_file = "/etc/nl2repobench/authoring-scheduler-phase3.env"
    journal.write_text(
        json.dumps(
            {
                "phase": "activated-preclaim",
                "rollback_allowed": True,
                "cutover_id": cutover_id,
                "manifest_sha256": manifest_sha256,
                "database": str(database.resolve()),
                "database_sha256": database_digest,
                "repository": str(repository.resolve()),
                "live_root": str(live_root.resolve()),
                "legacy_runtime_config": disabled,
                "sqlite_service_unit": unit,
                "sqlite_env_file": env_file,
            }
        ),
        encoding="utf-8",
    )
    barrier.write_text(
        json.dumps(
            {
                "schema_version": "authoring-cutover-barrier/v2",
                "cutover_id": cutover_id,
                "manifest_sha256": manifest_sha256,
                "database": str(database.resolve()),
                "database_sha256": database_digest,
                "rollback_allowed": True,
                "state_at_activation": "prepared",
                "authority": "database.cutover_barrier",
                "sqlite_service_unit": unit,
                "sqlite_env_file": env_file,
            }
        ),
        encoding="utf-8",
    )


def test_db_loop_never_reads_legacy_json_authorities(tmp_path: Path, monkeypatch) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    monkeypatch.setattr(loop, "TMPFS_ROOTS", ())
    monkeypatch.setattr(loop, "_load_json", lambda _path: pytest.fail("legacy JSON read"))
    monkeypatch.setattr(loop, "_load_queue_loop", lambda: pytest.fail("legacy queue adapter"))
    monkeypatch.setattr(
        loop,
        "_prepare_db_claim",
        lambda _args, _scheduler, claim, **_kwargs: {"claim": claim},
    )

    def finish(_args, db, identity, context):
        claim = context["claim"]
        db.prepare(
            claim.claim_id,
            owner,
            controller,
            claim.generation,
            pid=identity[0],
            process_starttime_ticks=identity[1],
            boot_id=identity[2],
        )
        db.start(
            claim.claim_id,
            owner,
            controller,
            claim.generation,
            pid=identity[0],
            process_starttime_ticks=identity[1],
            boot_id=identity[2],
            child_pid=os.getpid(),
            child_starttime_ticks=identity[1],
        )
        db.finish(
            claim.claim_id,
            owner,
            controller,
            claim.generation,
            success=True,
            pid=identity[0],
            process_starttime_ticks=identity[1],
            boot_id=identity[2],
        )
        return {"task_id": claim.task_id, "status": "complete"}

    monkeypatch.setattr(loop, "_run_db_claim", finish)
    args = SimpleNamespace(
        scheduler_db=scheduler.path,
        controller_id=controller,
        owner=owner,
        state_root=tmp_path / "state",
        worktree_root=tmp_path / "worktrees",
    )
    result = loop.run_db(args)

    assert result["authority"] == "sqlite"
    assert result["results"] == [{"task_id": "task", "status": "complete"}]


def test_prestart_abort_is_classified_and_closes_claim(tmp_path: Path) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    pid, starttime, boot_id = process_identity()
    claim = scheduler.claim_next(
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )[0]
    scheduler.prepare(
        claim.claim_id,
        owner,
        controller,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    scheduler.abort_claim(
        claim.claim_id,
        owner,
        controller,
        reason="Popen failed",
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    with scheduler.connect() as db:
        task = db.execute(
            "SELECT state,retry_count,last_failure_class FROM tasks WHERE task_id='task'"
        ).fetchone()
        active = db.execute(
            "SELECT active FROM claims WHERE claim_id=?", (claim.claim_id,)
        ).fetchone()[0]
    assert tuple(task) == ("pending", 1, "infrastructure")
    assert active == 0


def test_controller_recovery_cannot_close_replacement_claim(tmp_path: Path) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    pid, starttime, boot_id = process_identity()
    first = scheduler.claim_next(
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )[0]
    scheduler.release(
        first.claim_id,
        owner,
        controller,
        first.generation,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    second = scheduler.claim_next(
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )[0]
    with pytest.raises(LostLeaseError, match="generation fence"):
        scheduler.recover_controller(
            first.claim_id,
            first.generation,
            controller,
            owner,
            pid=pid,
            process_starttime_ticks=starttime,
            boot_id=boot_id,
            reason="delayed recovery",
        )
    with scheduler.connect() as db:
        assert db.execute(
            "SELECT active FROM claims WHERE claim_id=?", (second.claim_id,)
        ).fetchone()[0] == 1


def test_db_supervisor_honors_dynamic_disable_and_records_snapshot(
    tmp_path: Path, monkeypatch
) -> None:
    scheduler, _owner, _controller = _scheduler(tmp_path)
    scheduler.configure(enabled=False, lease_seconds=60, heartbeat_interval_seconds=5)
    monkeypatch.setattr(supervisor, "_free_bytes", lambda _path: 100 * 1024**3)
    monkeypatch.setattr(
        supervisor,
        "_docker_storage_status",
        lambda: (tmp_path, 100 * 1024**3, None),
    )
    monkeypatch.setattr(supervisor, "_git_status", lambda _root: [])
    monkeypatch.setattr(
        supervisor,
        "_start_db_controller",
        lambda *args: pytest.fail("disabled scheduler started a controller"),
    )
    monkeypatch.setattr(
        supervisor,
        "_start_db_watcher",
        lambda *args: pytest.fail("disabled scheduler started a watcher"),
    )
    args = SimpleNamespace(
        repository_root=tmp_path,
        live_root=Path("live"),
        scheduler_db=scheduler.path,
        remote="fake",
        branch="main",
        interval_sec=1,
        command_timeout=10,
        dry_run=False,
    )

    assert supervisor.supervise_db(args) == 0
    with scheduler.connect() as db:
        assert db.execute("SELECT count(*) FROM status_snapshots").fetchone()[0] == 1
    assert scheduler.resource_policy()["docker_min_free_bytes"] == 20 * 1024**3


def test_db_supervisor_dry_run_is_table_content_read_only(tmp_path: Path, monkeypatch) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    _finish_authoring(scheduler, owner, controller, tmp_path / "worktree")
    actor = SingletonActor.acquire(scheduler, "integration")
    receipt = scheduler.begin_operation(
        "task", "integration", "dry-run-abandoned", actor=actor.fence
    )
    with scheduler.connect() as db:
        db.execute(
            "UPDATE scheduler_leases SET lease_expires_at='2000-01-01T00:00:00+00:00' "
            "WHERE lease_id=?",
            (actor.fence.lease_id,),
        )

    def content() -> dict[str, list[tuple[object, ...]]]:
        uri = f"file:{scheduler.path.resolve().as_posix()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as db:
            tables = [
                row[0]
                for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
            ]
            return {
                table: [tuple(row) for row in db.execute(f'SELECT * FROM "{table}"')]
                for table in tables
            }

    before = content()
    monkeypatch.setattr(supervisor, "_free_bytes", lambda _path: 100 * 1024**3)
    monkeypatch.setattr(
        supervisor,
        "_docker_storage_status",
        lambda: (tmp_path, 100 * 1024**3, None),
    )
    args = SimpleNamespace(
        repository_root=tmp_path,
        live_root=Path("live"),
        scheduler_db=scheduler.path,
        dry_run=True,
    )
    assert supervisor.supervise_db(args) == 0
    assert content() == before
    with scheduler.connect() as db:
        assert db.execute(
            "SELECT status FROM operation_receipts WHERE receipt_id=?", (receipt,)
        ).fetchone()[0] == "started"


def test_prepared_disabled_supervisor_cycle_is_read_only(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    database = tmp_path / "prepared.sqlite3"
    scheduler = Scheduler(database, supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
    )
    scheduler.prepare_cutover_barrier("prepared", "a" * 64)
    before_digest = hashlib.sha256(database.read_bytes()).hexdigest()
    monkeypatch.setattr(supervisor, "_free_bytes", lambda _path: 100 * 1024**3)
    monkeypatch.setattr(
        supervisor,
        "_docker_storage_status",
        lambda: (tmp_path, 100 * 1024**3, None),
    )
    result = supervisor.supervise_db(
        SimpleNamespace(
            repository_root=tmp_path,
            live_root=Path("live"),
            scheduler_db=database,
            dry_run=False,
        )
    )
    assert result == 0
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before_digest
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "awaiting-first-enable"
    assert report["dry_run"] is False
    with sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True) as db:
        assert db.execute("SELECT count(*) FROM controllers").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM scheduler_leases").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM status_snapshots").fetchone()[0] == 0


def test_zero_runtime_limits_skip_work_but_allow_maintenance(
    tmp_path: Path, monkeypatch
) -> None:
    scheduler = Scheduler(tmp_path / "zero.sqlite3", supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(
        enabled=True,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
    )
    monkeypatch.setattr(supervisor, "_free_bytes", lambda _path: 100 * 1024**3)
    monkeypatch.setattr(
        supervisor,
        "_docker_storage_status",
        lambda: (tmp_path, 0, "docker unavailable"),
    )
    monkeypatch.setattr(supervisor, "_git_status", lambda _root: [])
    monkeypatch.setattr(
        supervisor,
        "_integrate_db_task",
        lambda *args: pytest.fail("zero integration limit executed work"),
    )
    monkeypatch.setattr(
        supervisor,
        "_start_db_controller",
        lambda *args: pytest.fail("zero agent/controller limit spawned work"),
    )
    monkeypatch.setattr(supervisor, "_start_db_watcher", lambda *args: 4321)
    args = SimpleNamespace(
        repository_root=tmp_path,
        live_root=Path("live"),
        scheduler_db=scheduler.path,
        remote="fake",
        branch="main",
        interval_sec=1,
        command_timeout=10,
        dry_run=False,
    )
    assert supervisor.supervise_db(args) == 0
    with scheduler.connect() as db:
        payload = json.loads(
            db.execute(
                "SELECT payload_json FROM status_snapshots ORDER BY snapshot_id DESC"
            ).fetchone()[0]
        )
    assert {action["status"] for action in payload["actions"]} == {"watcher-started"}

    limited = Scheduler(tmp_path / "agent-zero.sqlite3", supplied_root=tmp_path)
    limited.init()
    limited.configure(
        enabled=True,
        max_total_controllers=1,
        controller_concurrency=1,
        max_integrations=0,
        agent_limit=0,
    )
    limited.add_lane("lane", "batch", "python")
    identity = Identity("1" * 64, "python", "demo", "https://example.invalid", "git", "2" * 40)
    limited.add_identity(identity)
    limited.add_candidate("candidate", "lane", identity.digest)
    limited.add_task("task", "candidate", "lane", "r1")
    token = limited.reserve_controller("lane", "owner", 0)
    pid, starttime, boot_id = process_identity()
    limited.capacity("active_claim", "controller", "controller", 1)
    limited.activate_controller(
        token,
        "controller",
        "owner",
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
        executable_digest="3" * 64,
        argv_digest="4" * 64,
    )
    assert limited.claim_next(
        "controller",
        "owner",
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    ) == []


def test_scheduler_operator_exposes_runtime_and_resource_limits() -> None:
    cli = _script("authoring_scheduler.py")
    configured = cli.parser().parse_args(
        [
            "--root",
            "/tmp",
            "--db",
            "/tmp/scheduler.sqlite3",
            "config-set",
            "--enabled",
            "true",
            "--max-total-controllers",
            "1",
            "--controller-concurrency",
            "1",
            "--max-integrations",
            "0",
            "--agent-limit",
            "1",
        ]
    )
    resource = cli.parser().parse_args(
        [
            "--root",
            "/tmp",
            "--db",
            "/tmp/scheduler.sqlite3",
            "resource-set",
            "--repository-min-free-bytes",
            "1",
            "--docker-min-free-bytes",
            "2",
            "--watcher-min-free-bytes",
            "3",
        ]
    )
    assert configured.agent_limit == 1 and configured.max_integrations == 0
    assert resource.docker_min_free_bytes == 2


@pytest.mark.parametrize("option", sorted(supervisor.DB_FORBIDDEN_OPTIONS))
def test_db_supervisor_rejects_every_legacy_only_option(option: str) -> None:
    assert supervisor._db_legacy_options([option]) == [option]


def test_db_supervisor_parser_errors_on_legacy_authority(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "authoring_supervisor.py",
            "--scheduler-db",
            str(tmp_path / "scheduler.sqlite3"),
            "--queue-root",
            str(tmp_path / "legacy-queue"),
            "--once",
        ],
    )
    with pytest.raises(SystemExit) as exc:
        supervisor.main()
    assert exc.value.code == 2


def test_malformed_scheduler_database_returns_restart_preventing_78(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    database = tmp_path / "malformed.sqlite3"
    database.write_bytes(b"not sqlite")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "authoring_supervisor.py",
            "--scheduler-db",
            str(database),
            "--repository-root",
            str(tmp_path),
            "--once",
        ],
    )
    assert supervisor.main() == 78
    assert "corruption marker" in capsys.readouterr().err


def test_binding_installer_maps_corruption_to_78(
    tmp_path: Path, capsys
) -> None:
    database = tmp_path / "malformed.sqlite3"
    database.write_bytes(b"not sqlite")
    journal = tmp_path / "journal.json"
    barrier = tmp_path / "barrier.json"
    _write_rollback_authorities(
        database=database,
        journal=journal,
        barrier=barrier,
        repository=tmp_path / "repository",
        live_root=tmp_path / "live",
        disabled={
            "enabled": False,
            "max_total_controllers": 0,
            "controller_concurrency": 0,
            "max_integrations": 0,
            "agent_limit": 0,
        },
        cutover_id="malformed",
        manifest_sha256="a" * 64,
    )
    result = installer.main(
        [
            "--journal",
            str(journal),
            "--barrier",
            str(barrier),
            "--db",
            str(database),
            "--sqlite-service-unit",
            "nl2repobench-authoring-supervisor-sqlite@phase3.service",
            "--sqlite-env-file",
            "/etc/nl2repobench/authoring-scheduler-phase3.env",
        ]
    )
    assert result == 78
    assert "corruption marker" in capsys.readouterr().err


class FakeBucket:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def object_exists(self, key: str) -> bool:
        return key in self.objects

    def put_object_from_file(self, key: str, path: str, headers=None) -> None:
        del headers
        self.objects[key] = Path(path).read_bytes()

    def get_object(self, key: str):
        return io.BytesIO(self.objects[key])


def test_shadow_e2e_receipt_chain_with_fake_external_adapters(tmp_path: Path, monkeypatch) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    pid, starttime, boot_id = process_identity()
    claim = scheduler.claim_next(
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )[0]
    scheduler.prepare(
        claim.claim_id,
        owner,
        controller,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    scheduler.start(
        claim.claim_id,
        owner,
        controller,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
        child_pid=pid,
        child_starttime_ticks=starttime,
    )
    worktree = tmp_path / "repo/.nl2repo/authoring-live/worktrees/batch/demo"
    source = worktree / "catalog/sources/demo"
    source.mkdir(parents=True)
    (source / "task.toml").write_text("task_id='demo'\n", encoding="utf-8")
    (worktree / ".nl2repo").mkdir(exist_ok=True)
    handoff = worktree / ".nl2repo/authoring-handoff.json"
    handoff.write_text('{"status":"ready"}\n', encoding="utf-8")
    scheduler.record_handoff(
        claim.claim_id,
        owner,
        controller,
        claim.generation,
        worktree_path=str(worktree),
        worktree_git_head="e" * 40,
        handoff_path=str(handoff),
        handoff_sha256=hashlib.sha256(handoff.read_bytes()).hexdigest(),
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    scheduler.finish(
        claim.claim_id,
        owner,
        controller,
        success=True,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    integration = SingletonActor.acquire(scheduler, "integration")
    monkeypatch.setattr(
        supervisor,
        "_integrate_task",
        lambda *args, **kwargs: {"status": "integrated", "package": "demo", "commit": "f" * 40},
    )
    monkeypatch.setattr(
        supervisor,
        "_run",
        lambda *args, **kwargs: {"exit_code": 0, "raw_output": "f" * 40, "output": "f" * 40},
    )
    task = scheduler.operation_candidates("integration")[0]
    action = supervisor._integrate_db_task(
        SimpleNamespace(remote="fake", branch="main", dry_run=False, command_timeout=10),
        scheduler,
        integration,
        tmp_path / "repo",
        task,
        [],
    )
    assert action["status"] == "integrated"
    integration.release()

    archive_actor = SingletonActor.acquire(scheduler, "archive")
    monkeypatch.setattr(archive, "task_is_idle", lambda _worktree: True)
    archived = archive._db_archive_one(
        scheduler,
        archive_actor,
        FakeBucket(),
        scheduler.operation_candidates("archive")[0],
        receipt_root=tmp_path / "receipts",
        workers=2,
    )
    assert archived["status"] == "archived"
    completed = archive._db_cleanup_one(
        scheduler,
        archive_actor,
        scheduler.operation_candidates("cleanup")[0],
        receipt_root=tmp_path / "receipts",
    )
    archive_actor.release()

    assert completed["status"] == "complete"
    assert not worktree.exists()
    assert scheduler.status()["task_counts"] == {"complete": 1}


def test_cleanup_apply_and_complete_is_atomic_on_completion_failure(tmp_path: Path) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    _finish_authoring(scheduler, owner, controller, tmp_path / "worktree")
    integration = SingletonActor.acquire(scheduler, "integration")
    integration_receipt = scheduler.begin_operation(
        "task", "integration", "atomic-integration", actor=integration.fence
    )
    scheduler.update_receipt(
        integration_receipt,
        "pushed",
        actor=integration.fence,
        commit_sha="f" * 40,
        external_ref="refs/heads/main",
    )
    integration.release()
    archive_actor = SingletonActor.acquire(scheduler, "archive")
    archive_receipt = scheduler.begin_operation(
        "task", "archive", "atomic-archive", actor=archive_actor.fence
    )
    scheduler.update_receipt(
        archive_receipt,
        "verified",
        actor=archive_actor.fence,
        manifest_key="archive/manifest.json",
        manifest_sha256="1" * 64,
        source_snapshot_sha256="2" * 64,
        object_count=1,
        byte_count=1,
        evidence_sha256="3" * 64,
    )
    cleanup_receipt = scheduler.begin_operation(
        "task", "cleanup", "atomic-cleanup", actor=archive_actor.fence
    )
    with scheduler.connect() as db:
        db.execute(
            "CREATE TRIGGER fail_atomic_complete BEFORE UPDATE OF state ON tasks "
            "WHEN NEW.state='complete' BEGIN SELECT RAISE(ABORT,'injected completion failure'); END"
        )
    with pytest.raises(sqlite3.IntegrityError, match="injected completion failure"):
        scheduler.apply_cleanup_and_complete(
            cleanup_receipt,
            actor=archive_actor.fence,
            evidence_path="cleanup/evidence.json",
            evidence_sha256="4" * 64,
            receipt_json={"removed": True},
            reason="complete",
        )
    with scheduler.connect() as db:
        assert tuple(
            db.execute(
                "SELECT r.status,t.state FROM operation_receipts r "
                "JOIN tasks t ON t.task_id=r.task_id WHERE r.receipt_id=?",
                (cleanup_receipt,),
            ).fetchone()
        ) == ("started", "cleaning")
        db.execute("DROP TRIGGER fail_atomic_complete")
    scheduler.apply_cleanup_and_complete(
        cleanup_receipt,
        actor=archive_actor.fence,
        evidence_path="cleanup/evidence.json",
        evidence_sha256="4" * 64,
        receipt_json={"removed": True},
        reason="complete",
    )
    assert scheduler.status()["task_counts"] == {"complete": 1}
    archive_actor.release()


def test_abandoned_operation_is_reconciled_under_new_actor(tmp_path: Path) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    _finish_authoring(scheduler, owner, controller, tmp_path / "worktree")
    abandoned = SingletonActor.acquire(scheduler, "integration")
    task = scheduler.operation_candidates("integration")[0]
    receipt = scheduler.begin_operation(
        "task", "integration", "abandoned-integration", actor=abandoned.fence
    )
    with scheduler.connect() as db:
        db.execute(
            "UPDATE scheduler_leases SET lease_expires_at='2000-01-01T00:00:00+00:00' "
            "WHERE lease_id=?",
            (abandoned.fence.lease_id,),
        )
    replacement = SingletonActor.acquire(scheduler, "integration")

    assert scheduler.reconcile_operations(replacement.fence) == 1
    with scheduler.connect() as db:
        assert db.execute(
            "SELECT status FROM operation_receipts WHERE receipt_id=?", (receipt,)
        ).fetchone()[0] == "failed"
        assert db.execute("SELECT state FROM tasks WHERE task_id='task'").fetchone()[0] == (
            "integration_retry"
        )
    replacement.release()
    assert task["task_id"] == "task"


def test_integration_dry_run_and_nonprogress_results_do_not_strand_receipts(
    tmp_path: Path, monkeypatch
) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    _finish_authoring(scheduler, owner, controller, tmp_path / "worktree")
    actor = SingletonActor.acquire(scheduler, "integration")
    task = scheduler.operation_candidates("integration")[0]
    with pytest.raises(ValueError, match="must not begin"):
        supervisor._integrate_db_task(
            SimpleNamespace(dry_run=True), scheduler, actor, tmp_path, task, []
        )
    with scheduler.connect() as db:
        assert db.execute("SELECT count(*) FROM operation_receipts").fetchone()[0] == 0

    monkeypatch.setattr(
        supervisor,
        "_integrate_task",
        lambda *args, **kwargs: {"status": "active", "package": "demo"},
    )
    result = supervisor._integrate_db_task(
        SimpleNamespace(
            dry_run=False, remote="fake", branch="main", command_timeout=10
        ),
        scheduler,
        actor,
        tmp_path,
        task,
        [],
    )
    assert result["receipt_disposition"] == "failed"
    with scheduler.connect() as db:
        assert db.execute("SELECT status FROM operation_receipts").fetchone()[0] == "failed"
        assert db.execute("SELECT state FROM tasks WHERE task_id='task'").fetchone()[0] == (
            "integration_retry"
        )
    actor.release()


def test_integration_source_error_is_classified_as_source(tmp_path: Path, monkeypatch) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    _finish_authoring(scheduler, owner, controller, tmp_path / "worktree")
    actor = SingletonActor.acquire(scheduler, "integration")
    task = scheduler.operation_candidates("integration")[0]
    monkeypatch.setattr(
        supervisor,
        "_integrate_task",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            supervisor.SourceIntegrationError("integration source collision")
        ),
    )
    with pytest.raises(supervisor.SourceIntegrationError):
        supervisor._integrate_db_task(
            SimpleNamespace(
                dry_run=False, remote="fake", branch="main", command_timeout=10
            ),
            scheduler,
            actor,
            tmp_path,
            task,
            [],
        )
    with scheduler.connect() as db:
        assert db.execute(
            "SELECT failure_class FROM operation_receipts"
        ).fetchone()[0] == "source"
        assert db.execute("SELECT state FROM tasks WHERE task_id='task'").fetchone()[0] == (
            "blocked"
        )
    actor.release()


def test_generated_task_collision_has_source_receipt_and_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    _finish_authoring(scheduler, owner, controller, tmp_path / "worktree")
    actor = SingletonActor.acquire(scheduler, "integration")
    task = scheduler.operation_candidates("integration")[0]
    collision = supervisor.GeneratedTaskCollision(
        tmp_path / "catalog/tasks/demo", "expected", "actual"
    )
    monkeypatch.setattr(
        supervisor,
        "_integrate_task",
        lambda *args, **kwargs: (_ for _ in ()).throw(collision),
    )
    with pytest.raises(supervisor.GeneratedTaskCollision):
        supervisor._integrate_db_task(
            SimpleNamespace(
                dry_run=False, remote="fake", branch="main", command_timeout=10
            ),
            scheduler,
            actor,
            tmp_path,
            task,
            [],
        )
    with scheduler.connect() as db:
        receipt = db.execute(
            "SELECT status,failure_class,evidence_path,evidence_sha256 "
            "FROM operation_receipts WHERE operation_kind='integration'"
        ).fetchone()
        state = db.execute("SELECT state FROM tasks WHERE task_id='task'").fetchone()[0]
    assert tuple(receipt[:2]) == ("failed", "source")
    evidence = tmp_path / receipt[2]
    assert evidence.is_file()
    assert hashlib.sha256(evidence.read_bytes()).hexdigest() == receipt[3]
    assert state == "blocked"
    actor.release()


def test_private_cas_collision_has_digest_bound_source_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    cas_root = tmp_path / "cas-root"
    cas_worktree = tmp_path / "cas-worktree"
    cas_source = cas_worktree / "catalog/sources/demo"
    cas_source.mkdir(parents=True)
    payload = b"expected private artifact"
    expected_digest = hashlib.sha256(payload).hexdigest()
    (cas_source / "task.toml").write_text(
        f"artifact = 'sha256:{expected_digest}'\n", encoding="utf-8"
    )
    source_artifact = supervisor._cas_file(cas_worktree, expected_digest)
    source_artifact.parent.mkdir(parents=True)
    source_artifact.write_bytes(payload)
    central_artifact = supervisor._cas_file(cas_root, expected_digest)
    central_artifact.parent.mkdir(parents=True)
    central_artifact.write_bytes(b"collision")
    with pytest.raises(supervisor.PrivateArtifactCollision) as direct_collision:
        supervisor._sync_private_cas(cas_root, cas_worktree, cas_source)
    assert direct_collision.value.expected_digest == expected_digest
    assert direct_collision.value.actual_digest == hashlib.sha256(b"collision").hexdigest()

    scheduler, owner, controller = _scheduler(tmp_path)
    _finish_authoring(scheduler, owner, controller, tmp_path / "worktree")
    actor = SingletonActor.acquire(scheduler, "integration")
    task = scheduler.operation_candidates("integration")[0]
    collision = supervisor.PrivateArtifactCollision(
        tmp_path / ".nl2repo/artifacts/private/object",
        "a" * 64,
        "b" * 64,
    )
    monkeypatch.setattr(
        supervisor,
        "_integrate_task",
        lambda *args, **kwargs: (_ for _ in ()).throw(collision),
    )
    with pytest.raises(supervisor.PrivateArtifactCollision):
        supervisor._integrate_db_task(
            SimpleNamespace(
                dry_run=False, remote="fake", branch="main", command_timeout=10
            ),
            scheduler,
            actor,
            tmp_path,
            task,
            [],
        )
    with scheduler.connect() as db:
        receipt = db.execute(
            "SELECT failure_class,evidence_path,evidence_sha256 FROM operation_receipts"
        ).fetchone()
        state = db.execute("SELECT state FROM tasks WHERE task_id='task'").fetchone()[0]
    evidence = tmp_path / receipt[1]
    payload = json.loads(evidence.read_text())
    assert receipt[0] == "source" and state == "blocked"
    assert payload["collision_kind"] == "PrivateArtifactCollision"
    assert payload["expected_digest"] == "a" * 64
    assert payload["actual_digest"] == "b" * 64
    assert hashlib.sha256(evidence.read_bytes()).hexdigest() == receipt[2]
    actor.release()


def test_private_cas_eexist_race_never_replaces_winner(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "root"
    worktree = tmp_path / "worktree"
    source = worktree / "catalog/sources/demo"
    source.mkdir(parents=True)
    payload = b"expected"
    digest = hashlib.sha256(payload).hexdigest()
    (source / "task.toml").write_text(
        f"artifact = 'sha256:{digest}'\n", encoding="utf-8"
    )
    source_artifact = supervisor._cas_file(worktree, digest)
    source_artifact.parent.mkdir(parents=True)
    source_artifact.write_bytes(payload)
    target = supervisor._cas_file(root, digest)
    winner = b"racing mismatch"

    def racing_link(_source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(winner)
        raise FileExistsError(destination)

    monkeypatch.setattr(supervisor.os, "link", racing_link)
    with pytest.raises(supervisor.PrivateArtifactCollision) as collision:
        supervisor._sync_private_cas(root, worktree, source)
    assert collision.value.actual_digest == hashlib.sha256(winner).hexdigest()
    assert target.read_bytes() == winner


def test_private_cas_fallback_preserves_bad_temp_digest(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "root"
    worktree = tmp_path / "worktree"
    source = worktree / "catalog/sources/demo"
    source.mkdir(parents=True)
    payload = b"expected"
    digest = hashlib.sha256(payload).hexdigest()
    (source / "task.toml").write_text(
        f"artifact = 'sha256:{digest}'\n", encoding="utf-8"
    )
    source_artifact = supervisor._cas_file(worktree, digest)
    source_artifact.parent.mkdir(parents=True)
    source_artifact.write_bytes(payload)
    monkeypatch.setattr(
        supervisor.os,
        "link",
        lambda *_args: (_ for _ in ()).throw(OSError(errno.EXDEV, "cross-device")),
    )
    bad = b"bad copied bytes"
    monkeypatch.setattr(
        supervisor.shutil,
        "copyfile",
        lambda _source, destination: Path(destination).write_bytes(bad),
    )
    with pytest.raises(supervisor.PrivateArtifactCollision) as collision:
        supervisor._sync_private_cas(root, worktree, source)
    assert collision.value.actual_digest == hashlib.sha256(bad).hexdigest()
    assert not supervisor._cas_file(root, digest).exists()


def test_archive_watcher_disable_and_partial_singleton_rollback(
    tmp_path: Path, monkeypatch
) -> None:
    scheduler, _owner, _controller = _scheduler(tmp_path)
    scheduler.configure(
        enabled=False,
        lease_seconds=60,
        heartbeat_interval_seconds=5,
        max_total_controllers=1,
        controller_concurrency=1,
        max_integrations=0,
        agent_limit=1,
    )
    watcher = SingletonActor.acquire(scheduler, "watcher")
    archive_actor = SingletonActor.acquire(scheduler, "archive")
    monkeypatch.setattr(
        scheduler,
        "operation_candidates",
        lambda *args, **kwargs: pytest.fail("disabled watcher selected work"),
    )
    result = archive._run_db_cycle(
        SimpleNamespace(workers=1, receipt_root=tmp_path / "receipts"),
        FakeBucket(),
        scheduler,
        watcher,
        archive_actor,
    )
    assert result == [{"status": "disabled", "authority": "sqlite"}]
    archive_actor.release()
    watcher.release()

    held = SingletonActor.acquire(scheduler, "archive")
    with pytest.raises(Exception, match="singleton lease is held"):
        archive.run_db_once(
            SimpleNamespace(
                scheduler_db=scheduler.path,
                workers=1,
                receipt_root=tmp_path / "receipts",
            ),
            FakeBucket(),
        )
    with scheduler.connect() as db:
        assert db.execute(
            "SELECT count(*) FROM scheduler_leases WHERE scope='watcher' AND active=1"
        ).fetchone()[0] == 0
    held.release()


def test_archive_remote_collision_uses_collision_receipt(tmp_path: Path, monkeypatch) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    worktree = tmp_path / "worktree"
    _finish_authoring(scheduler, owner, controller, worktree)
    integration = SingletonActor.acquire(scheduler, "integration")
    integration_receipt = scheduler.begin_operation(
        "task", "integration", "collision-integration", actor=integration.fence
    )
    scheduler.update_receipt(
        integration_receipt,
        "pushed",
        actor=integration.fence,
        commit_sha="f" * 40,
        external_ref="refs/heads/main",
    )
    integration.release()
    archive_actor = SingletonActor.acquire(scheduler, "archive")
    monkeypatch.setattr(archive, "task_is_idle", lambda _worktree: True)

    class CollisionBucket(FakeBucket):
        def object_exists(self, key: str) -> bool:
            return True

        def get_object(self, key: str):
            return io.BytesIO(b"different")

    with pytest.raises(archive.ArchiveCollisionError):
        archive._db_archive_one(
            scheduler,
            archive_actor,
            CollisionBucket(),
            scheduler.operation_candidates("archive")[0],
            receipt_root=tmp_path / "receipts",
            workers=1,
        )
    with scheduler.connect() as db:
        row = db.execute(
            "SELECT status,evidence_path FROM operation_receipts "
            "WHERE operation_kind='archive'"
        ).fetchone()
        assert row[0] == "collision"
        assert (tmp_path / "receipts" / row[1]).is_file()
        assert db.execute("SELECT state FROM tasks WHERE task_id='task'").fetchone()[0] == (
            "blocked"
        )
    archive_actor.release()


def test_archive_secret_failure_is_classified_as_source(tmp_path: Path, monkeypatch) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    worktree = tmp_path / "secret-worktree"
    _finish_authoring(scheduler, owner, controller, worktree)
    (worktree / "catalog/sources/demo/secret.txt").write_text(
        "AKIA" + "A" * 16, encoding="utf-8"
    )
    integration = SingletonActor.acquire(scheduler, "integration")
    receipt = scheduler.begin_operation(
        "task", "integration", "secret-integration", actor=integration.fence
    )
    scheduler.update_receipt(
        receipt,
        "pushed",
        actor=integration.fence,
        commit_sha="f" * 40,
        external_ref="refs/heads/main",
    )
    integration.release()
    archive_actor = SingletonActor.acquire(scheduler, "archive")
    monkeypatch.setattr(archive, "task_is_idle", lambda _worktree: True)
    with pytest.raises(archive.ArchiveSourceError):
        archive._db_archive_one(
            scheduler,
            archive_actor,
            FakeBucket(),
            scheduler.operation_candidates("archive")[0],
            receipt_root=tmp_path / "receipts",
            workers=1,
        )
    with scheduler.connect() as db:
        assert db.execute(
            "SELECT failure_class FROM operation_receipts WHERE operation_kind='archive'"
        ).fetchone()[0] == "source"
    archive_actor.release()


def test_controller_cancellation_after_popen_kills_child(tmp_path: Path, monkeypatch) -> None:
    events: list[str] = []

    class Process:
        pid = 12345

        def terminate(self):
            events.append("terminate")

        def kill(self):
            events.append("kill")

        def wait(self, timeout=None):
            events.append("wait")
            return 0

    class FailingScheduler:
        def reserve_controller(self, *args):
            return "token"

        def capacity(self, *args):
            raise KeyboardInterrupt("cancelled")

        def release_controller_reservation(self, *args, **kwargs):
            events.append("reservation-released")

    monkeypatch.setattr(supervisor.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(supervisor, "process_identity", lambda _pid: (_pid, 1, "boot"))
    monkeypatch.setattr(supervisor.os, "killpg", lambda *args: events.append("term-sent"))
    args = SimpleNamespace(
        scheduler_db=tmp_path / "scheduler.sqlite3",
        interval_sec=1,
    )
    with pytest.raises(KeyboardInterrupt, match="cancelled"):
        supervisor._start_db_controller(
            args, FailingScheduler(), tmp_path, tmp_path / "live", "lane", 0
        )
    assert "term-sent" in events
    assert "wait" in events
    assert "reservation-released" in events


def test_worker_start_failure_kills_child_and_releases_claim(tmp_path: Path, monkeypatch) -> None:
    events: list[str] = []

    class Process:
        pid = 12346

    class FailingScheduler:
        def prepare(self, *args, **kwargs):
            events.append("prepared")

        def start(self, *args, **kwargs):
            raise RuntimeError("start failed")

        def abort_claim(self, *args, **kwargs):
            events.append("released")

    monkeypatch.setattr(loop, "_agent_prompt", lambda **kwargs: "prompt")
    monkeypatch.setattr(loop, "_pi_command", lambda *args, **kwargs: ["pi"])
    monkeypatch.setattr(loop, "_agent_environment", lambda _args: {})
    monkeypatch.setattr(loop.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(loop, "process_identity", lambda _pid: (_pid, 2, "boot"))
    monkeypatch.setattr(loop, "_terminate_process", lambda _process: events.append("terminated"))
    claim = SimpleNamespace(
        claim_id="claim",
        owner_uuid="owner",
        controller_id="controller",
        generation=1,
        attempt_no=1,
    )
    with pytest.raises(RuntimeError, match="start failed"):
        loop._launch_agent_db(
            SimpleNamespace(agent_timeout_sec=10),
            FailingScheduler(),
            claim,
            (os.getpid(), 1, "boot"),
            plan={"batch_id": "batch"},
            task={"package": "demo"},
            brief_path=tmp_path / "brief",
            worktree=tmp_path,
            session_dir=tmp_path / "sessions",
            log_path=tmp_path / "child.log",
            handoff_path=tmp_path / "handoff",
        )
    assert events == ["prepared", "terminated", "released"]


def test_worker_heartbeat_failure_kills_running_child(tmp_path: Path, monkeypatch) -> None:
    events: list[str] = []

    class Process:
        pid = 12347

        def wait(self, timeout=None):
            raise loop.subprocess.TimeoutExpired(["pi"], timeout)

    class FailingScheduler:
        def prepare(self, *args, **kwargs):
            events.append("prepared")

        def start(self, *args, **kwargs):
            events.append("started")

        def runtime_config(self):
            return {"heartbeat_interval_seconds": 5}

        def heartbeat(self, *args, **kwargs):
            events.append("heartbeat-failed")
            raise RuntimeError("heartbeat failed")

    monkeypatch.setattr(loop, "_agent_prompt", lambda **kwargs: "prompt")
    monkeypatch.setattr(loop, "_pi_command", lambda *args, **kwargs: ["pi"])
    monkeypatch.setattr(loop, "_agent_environment", lambda _args: {})
    monkeypatch.setattr(loop.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(loop, "process_identity", lambda _pid: (_pid, 2, "boot"))
    monkeypatch.setattr(loop, "_terminate_process", lambda _process: events.append("terminated"))
    claim = SimpleNamespace(
        claim_id="claim",
        owner_uuid="owner",
        controller_id="controller",
        generation=1,
        attempt_no=1,
    )
    with pytest.raises(RuntimeError, match="heartbeat failed"):
        loop._launch_agent_db(
            SimpleNamespace(agent_timeout_sec=10),
            FailingScheduler(),
            claim,
            (os.getpid(), 1, "boot"),
            plan={"batch_id": "batch"},
            task={"package": "demo"},
            brief_path=tmp_path / "brief",
            worktree=tmp_path,
            session_dir=tmp_path / "sessions",
            log_path=tmp_path / "child.log",
            handoff_path=tmp_path / "handoff",
        )
    assert events == ["prepared", "started", "heartbeat-failed", "terminated"]


def test_heartbeat_and_finish_failure_recovers_claim_and_controller(
    tmp_path: Path, monkeypatch
) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    events: list[str] = []

    class Process:
        pid = 12348

        def wait(self, timeout=None):
            raise loop.subprocess.TimeoutExpired(["pi"], timeout)

    monkeypatch.setattr(loop, "TMPFS_ROOTS", ())
    monkeypatch.setattr(loop, "scheduler_for", lambda _path: scheduler)
    monkeypatch.setattr(loop, "_agent_prompt", lambda **kwargs: "prompt")
    monkeypatch.setattr(loop, "_pi_command", lambda *args, **kwargs: ["pi"])
    monkeypatch.setattr(loop, "_agent_environment", lambda _args: {})
    monkeypatch.setattr(loop.subprocess, "Popen", lambda *args, **kwargs: Process())
    monkeypatch.setattr(loop, "_terminate_process", lambda _process: events.append("terminated"))
    original_identity = process_identity()
    monkeypatch.setattr(
        loop,
        "process_identity",
        lambda pid=None: (
            (pid, 2, original_identity[2])
            if pid is not None
            else original_identity
        ),
    )
    monkeypatch.setattr(
        scheduler,
        "heartbeat",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("heartbeat failed")),
    )
    monkeypatch.setattr(
        scheduler,
        "finish",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("finish failed")),
    )

    def context(_args, _scheduler, claim, **_kwargs):
        return {
            "claim": claim,
            "plan": {"batch_id": "batch"},
            "task": {"package": "demo"},
            "brief": tmp_path / "brief.json",
            "worktree": tmp_path,
            "session_root": tmp_path / "sessions",
            "log": tmp_path / "child.log",
            "handoff": tmp_path / "handoff.json",
            "task_root": tmp_path / "catalog/sources/demo",
            "package": "demo",
        }

    monkeypatch.setattr(loop, "_prepare_db_claim", context)
    args = SimpleNamespace(
        scheduler_db=scheduler.path,
        controller_id=controller,
        owner=owner,
        state_root=tmp_path / "state",
        worktree_root=tmp_path / "worktrees",
        agent_timeout_sec=10,
    )
    with pytest.raises(RuntimeError, match="heartbeat failed"):
        loop.run_db(args)
    with scheduler.connect() as db:
        active_claims = db.execute("SELECT count(*) FROM claims WHERE active=1").fetchone()[0]
        controller_state = db.execute(
            "SELECT state FROM controllers WHERE controller_id=?", (controller,)
        ).fetchone()[0]
        task = db.execute(
            "SELECT state,retry_count,last_failure_class FROM tasks WHERE task_id='task'"
        ).fetchone()
    assert events == ["terminated"]
    assert active_claims == 0
    assert controller_state == "stopped"
    assert tuple(task) == ("pending", 1, "infrastructure")


def test_cutover_process_identity_lock_and_mount_guards(tmp_path: Path, monkeypatch) -> None:
    record = cutover.ProcessRecord(
        123,
        4,
        "boot",
        "/usr/bin/python",
        "a" * 64,
        "b" * 64,
        "python archive_authoring_live.py",
        str(tmp_path),
        "0::/service",
        "watcher",
    )
    monkeypatch.setattr(cutover, "_read_process", lambda _pid: None)
    with pytest.raises(MigrationError, match="identity changed"):
        cutover._stop_watcher([record], 1)
    generic = cutover.ProcessRecord(
        124,
        5,
        "boot",
        "/usr/bin/bash",
        "c" * 64,
        "d" * 64,
        "bash",
        str(tmp_path / "repository"),
        "0::/user.slice",
        "other",
    )
    scoped = cutover._scope_process(
        generic, tmp_path / "repository", tmp_path / "live"
    )
    assert scoped is not None and scoped.role == "generic"

    lock = tmp_path / "archive.lock"
    with lock.open("a+") as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        from contextlib import ExitStack

        with ExitStack() as stack, pytest.raises(MigrationError, match="still held"):
            cutover._acquire_lock(stack, lock)

    worktrees = tmp_path / "worktrees"
    worktrees.mkdir()

    def docker(command, **kwargs):
        if command[:3] == ["docker", "ps", "-aq"]:
            return SimpleNamespace(returncode=0, stdout="container\n", stderr="")
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps([{"Id": "container", "Mounts": [{"Source": str(worktrees)}]}]),
            stderr="",
        )

    monkeypatch.setattr(cutover.subprocess, "run", docker)
    with pytest.raises(MigrationError, match="container mount"):
        cutover._verify_docker(worktrees)
    mount_line = (
        f"36 25 0:32 / {worktrees} rw,relatime - bind {worktrees} rw"
    )
    assert cutover._mountinfo_conflicts([mount_line], worktrees)
    bind_root_line = (
        f"37 25 0:33 {worktrees / 'task'} /outside rw,relatime - ext4 /dev/sda1 rw"
    )
    assert cutover._mountinfo_conflicts([bind_root_line], worktrees)

    class UnreadableMount:
        def read_text(self, **kwargs):
            raise OSError("denied")

    class ExtantProcess:
        name = "123"

        def __truediv__(self, _name):
            return UnreadableMount()

        def exists(self):
            return True

    with pytest.raises(MigrationError, match="cannot inspect mountinfo"):
        cutover._read_mountinfo(ExtantProcess())

    proc_root = tmp_path / "proc"
    unreadable_process = proc_root / "456"
    unreadable_process.mkdir(parents=True)
    unreadable_mountinfo = unreadable_process / "mountinfo"
    unreadable_mountinfo.mkdir()
    with pytest.raises(MigrationError, match="live pid: 456"):
        cutover._verify_mountinfo(worktrees, proc_root=proc_root)

    calls: list[tuple[str, ...]] = []

    def systemctl(*arguments: str) -> str:
        calls.append(arguments)
        return ""

    monkeypatch.setattr(cutover, "_systemctl", systemctl)
    cutover._disable_and_mask_service("legacy.service")
    assert ("disable", "--now", "legacy.service") in calls
    assert ("mask", "--runtime", "legacy.service") in calls
    cgroup = tmp_path / "cgroup/service"
    cgroup.mkdir(parents=True)
    (cgroup / "cgroup.procs").write_text("123\n", encoding="utf-8")
    with pytest.raises(MigrationError, match="not empty"):
        cutover._verify_empty_cgroup("/service", cgroup_root=tmp_path / "cgroup")


def test_activation_rechecks_late_target_sidecars(tmp_path: Path) -> None:
    staging = tmp_path / "staging.sqlite3"
    target = tmp_path / "target.sqlite3"
    with sqlite3.connect(staging) as db:
        db.execute("CREATE TABLE proof(value TEXT)")
    Path(str(target) + "-wal").write_bytes(b"late collision")
    with pytest.raises(MigrationError, match="target file set changed"):
        cutover._activate_cutover_database(staging, target)
    assert staging.is_file()
    assert Path(str(target) + "-wal").is_file()


def test_cutover_stages_backup_activates_disabled_database(tmp_path: Path, monkeypatch) -> None:
    live = tmp_path / "live"
    config = live / "supervisor/runtime-config.json"
    config.parent.mkdir(parents=True)
    config.write_text(
        json.dumps(
            {
                "enabled": True,
                "max_total_controllers": 3,
                "controller_concurrency": 1,
                "max_integrations": 2,
            }
        ),
        encoding="utf-8",
    )
    events: list[str] = []
    monkeypatch.setattr(cutover, "_wait_for_controllers", lambda *args: events.append("drained"))
    monkeypatch.setattr(
        cutover, "_disable_and_mask_service", lambda *args: events.append("service-masked")
    )
    monkeypatch.setattr(cutover, "_stop_watcher", lambda *args: events.append("watcher-stopped"))
    monkeypatch.setattr(cutover, "_authoring_processes", lambda *args: [])
    monkeypatch.setattr(cutover, "_verify_docker", lambda *args: events.append("docker-verified"))

    def manifest(root, *, cutover_id):
        assert json.loads(config.read_text())["enabled"] is False
        events.append("manifest-frozen")
        return {"cutover_id": cutover_id, "manifest_sha256": "a" * 64, "lanes": []}

    monkeypatch.setattr(cutover, "generate_manifest", manifest)
    monkeypatch.setattr(
        cutover, "validate_manifest", lambda *args: events.append("manifest-validated")
    )

    def imported(*args, **kwargs):
        scheduler = Scheduler(kwargs["db_path"], supplied_root=Path(kwargs["db_path"]).parent)
        scheduler.init()
        events.append("imported")
        return {"counts": {}}

    monkeypatch.setattr(cutover, "import_manifest", imported)
    monkeypatch.setattr(cutover, "_manifest_task_count", lambda *args: 0)
    barrier = tmp_path / "barrier.json"
    result = cutover.execute_cutover(
        repository=tmp_path,
        live_root=live,
        manifest_path=tmp_path / "manifest.json",
        database=tmp_path / "scheduler.sqlite3",
        backup_directory=tmp_path / "backup",
        journal_path=tmp_path / "journal.json",
        barrier_path=barrier,
        cutover_id="cutover-3",
        service_unit=cutover.LEGACY_SERVICE_UNIT,
        sqlite_service_unit="nl2repobench-authoring-supervisor-sqlite@phase3.service",
        sqlite_env_file=Path("/etc/nl2repobench/authoring-scheduler-phase3.env"),
        drain_timeout=1,
        repository_min_free_bytes=1,
        docker_min_free_bytes=1,
        watcher_min_free_bytes=1,
    )

    assert events.index("manifest-frozen") > events.index("docker-verified")
    assert barrier.is_file()
    assert result["backup"]["verified"] is True
    activated = Scheduler(tmp_path / "scheduler.sqlite3", supplied_root=tmp_path)
    assert activated.runtime_config()["enabled"] == 0
    assert activated.status()["cutover_barrier"]["state"] == "prepared"
    assert json.loads(config.read_text())["enabled"] is False
    binding = cutover.install_service_binding(
        journal_path=tmp_path / "journal.json",
        barrier_path=barrier,
        database=tmp_path / "scheduler.sqlite3",
        sqlite_service_unit="nl2repobench-authoring-supervisor-sqlite@phase3.service",
        sqlite_env_file=Path("/etc/nl2repobench/authoring-scheduler-phase3.env"),
    )
    assert binding["scheduler_db"] == str((tmp_path / "scheduler.sqlite3").resolve())
    with pytest.raises(MigrationError, match="do not match"):
        cutover.install_service_binding(
            journal_path=tmp_path / "journal.json",
            barrier_path=barrier,
            database=tmp_path / "scheduler.sqlite3",
            sqlite_service_unit="nl2repobench-authoring-supervisor-sqlite@other.service",
            sqlite_env_file=Path("/etc/nl2repobench/authoring-scheduler-other.env"),
        )
    monkeypatch.setattr(cutover, "_verify_sqlite_service_stopped", lambda _unit: None)
    restored = cutover.restore_cutover_database(
        backup_directory=tmp_path / "backup",
        database=tmp_path / "scheduler.sqlite3",
        journal_path=tmp_path / "journal.json",
        barrier_path=barrier,
        runtime_config=config,
        receipt_authority=tmp_path / "restore-authority-success",
    )
    assert restored["restore"]["verified"] is True
    assert (tmp_path / ".scheduler.sqlite3.restore-consumed.json").is_file()
    activated.first_enable()
    activated.add_lane("restore-lane", "restore-batch", "python")
    restore_identity = Identity(
        "6" * 64,
        "python",
        "restore-demo",
        "https://example.invalid/restore",
        "git",
        "7" * 40,
    )
    activated.add_identity(restore_identity)
    activated.add_candidate("restore-candidate", "restore-lane", restore_identity.digest)
    activated.add_task("restore-task", "restore-candidate", "restore-lane", "r1")
    owner, controller = "restore-owner", "restore-controller"
    token = activated.reserve_controller("restore-lane", owner, 0)
    pid, starttime, boot_id = process_identity()
    activated.capacity("active_claim", "controller", controller, 1)
    activated.activate_controller(
        token,
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
        executable_digest="8" * 64,
        argv_digest="9" * 64,
    )
    assert activated.claim_next(
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    with pytest.raises(MigrationError, match="not disabled cutover|capacity or active"):
        cutover.restore_cutover_database(
            backup_directory=tmp_path / "backup",
            database=tmp_path / "scheduler.sqlite3",
            journal_path=tmp_path / "journal.json",
            barrier_path=barrier,
            runtime_config=config,
            receipt_authority=tmp_path / "restore-authority",
        )
    assert not (tmp_path / "restore-authority").exists()


def test_import_receipt_times_are_preserved_and_reverse_chronology_rejected() -> None:
    receipt = {
        "status": "pushed",
        "started_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:00:05+00:00",
    }
    assert authoring_migration._receipt_times(receipt, fallback="2027-01-01T00:00:00+00:00") == (
        "2026-01-01T00:00:00.000000+00:00",
        "2026-01-01T00:00:05.000000+00:00",
    )
    with pytest.raises(MigrationError, match="finishes before"):
        authoring_migration._receipt_times(
            {
                "status": "verified",
                "started_at": "2026-01-01T00:00:05+00:00",
                "finished_at": "2026-01-01T00:00:00+00:00",
            },
            fallback="2027-01-01T00:00:00+00:00",
        )
    with pytest.raises(MigrationError, match="overlap"):
        cutover._validate_stage_chronology(
            {
                "integration": {
                    "finished_at": "2026-01-01T00:00:05.000000+00:00"
                },
                "archive": {
                    "started_at": "2026-01-01T00:00:04.000000+00:00",
                    "finished_at": "2026-01-01T00:00:06.000000+00:00",
                },
                "cleanup": {
                    "started_at": "2026-01-01T00:00:06.000000+00:00"
                },
            }
        )


def test_cutover_validation_rejects_duplicate_terminal_receipts(tmp_path: Path) -> None:
    scheduler, owner, controller = _scheduler(tmp_path)
    _finish_authoring(scheduler, owner, controller, tmp_path / "worktree")
    integration = SingletonActor.acquire(scheduler, "integration")
    pushed = scheduler.begin_operation(
        "task", "integration", "duplicate-integration", actor=integration.fence
    )
    scheduler.update_receipt(
        pushed,
        "pushed",
        actor=integration.fence,
        commit_sha="a" * 40,
        external_ref="refs/heads/main",
    )
    integration.release()
    archive_actor = SingletonActor.acquire(scheduler, "archive")
    verified = scheduler.begin_operation(
        "task", "archive", "duplicate-archive", actor=archive_actor.fence
    )
    scheduler.update_receipt(
        verified,
        "verified",
        actor=archive_actor.fence,
        manifest_key="manifest.json",
        manifest_sha256="b" * 64,
        source_snapshot_sha256="c" * 64,
        object_count=1,
        byte_count=1,
        evidence_sha256="d" * 64,
    )
    cleanup = scheduler.begin_operation(
        "task", "cleanup", "duplicate-cleanup", actor=archive_actor.fence
    )
    scheduler.apply_cleanup_and_complete(
        cleanup,
        actor=archive_actor.fence,
        evidence_path="cleanup.json",
        evidence_sha256="e" * 64,
        receipt_json={"done": True},
        reason="done",
    )
    archive_actor.release()
    pid, starttime, boot_id = process_identity()
    scheduler.stop_controller(
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
    )
    scheduler.prepare_cutover_barrier("duplicate", "f" * 64)
    with scheduler.connect() as db:
        db.execute(
            "INSERT INTO operation_receipts(receipt_id,task_id,operation_kind,"
            "operation_attempt,retry_no,idempotency_key,status,commit_sha,external_ref,"
            "actor_lease_id,receipt_json,started_at,finished_at,created_at,updated_at) "
            "VALUES('duplicate-pushed','task','integration',2,1,'duplicate-terminal',"
            "'pushed',?,?,'legacy','{}',?,?,?,?)",
            (
                "f" * 40,
                "refs/heads/main",
                "2026-01-01T00:00:00.000000+00:00",
                "2026-01-01T00:00:01.000000+00:00",
                "2026-01-01T00:00:00.000000+00:00",
                "2026-01-01T00:00:01.000000+00:00",
            ),
        )
    with pytest.raises(MigrationError, match="terminal receipt uniqueness"):
        cutover._database_validation(scheduler.path, 1)


def test_preclaim_rollback_and_first_claim_seals_barrier(
    tmp_path: Path, monkeypatch
) -> None:
    disabled = {
        "enabled": False,
        "max_total_controllers": 0,
        "controller_concurrency": 0,
        "max_integrations": 0,
        "agent_limit": 0,
    }
    rollback_db = tmp_path / "rollback.sqlite3"
    rollback_scheduler = Scheduler(rollback_db, supplied_root=tmp_path)
    rollback_scheduler.init()
    rollback_scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
    )
    rollback_scheduler.prepare_cutover_barrier("rollback", "f" * 64)
    rollback_live = tmp_path / "rollback-live"
    rollback_config = rollback_live / "supervisor/runtime-config.json"
    rollback_config.parent.mkdir(parents=True)
    rollback_config.write_text(json.dumps(disabled), encoding="utf-8")
    rollback_journal = tmp_path / "rollback-journal.json"
    rollback_record = tmp_path / "rollback-record.json"
    _write_rollback_authorities(
        database=rollback_db,
        journal=rollback_journal,
        barrier=rollback_record,
        repository=tmp_path / "rollback-repository",
        live_root=rollback_live,
        disabled=disabled,
        cutover_id="rollback",
        manifest_sha256="f" * 64,
    )
    monkeypatch.setattr(cutover, "_verify_sqlite_service_stopped", lambda _unit: None)
    monkeypatch.setattr(cutover, "_authoring_processes", lambda *_args: [])
    cutover.rollback_cutover(
        journal_path=rollback_journal,
        barrier_path=rollback_record,
        runtime_config=rollback_config,
        database=rollback_db,
    )
    assert not rollback_db.exists()
    assert json.loads(rollback_config.read_text())["enabled"] is False

    database = tmp_path / "scheduler.sqlite3"
    scheduler = Scheduler(database, supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
    )
    scheduler.prepare_cutover_barrier("cutover", "a" * 64)
    assert scheduler.first_enable() > 0
    scheduler.add_lane("lane", "batch", "python")
    identity = Identity("b" * 64, "python", "demo", "https://example.invalid", "git", "c" * 40)
    scheduler.add_identity(identity)
    scheduler.add_candidate("candidate", "lane", identity.digest)
    scheduler.add_task("task", "candidate", "lane", "r1")
    owner, controller = "owner", "controller"
    token = scheduler.reserve_controller("lane", owner, 0)
    pid, starttime, boot_id = process_identity()
    scheduler.capacity("active_claim", "controller", controller, 1)
    scheduler.activate_controller(
        token,
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
        executable_digest="d" * 64,
        argv_digest="e" * 64,
    )
    live_supervisor = SingletonActor.acquire(scheduler, "supervisor")
    assert scheduler.status()["cutover_barrier"]["first_effect_kind"] == "first-enable"
    live = tmp_path / "live"
    config = live / "supervisor/runtime-config.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps(disabled), encoding="utf-8")
    journal = tmp_path / "journal.json"
    barrier = tmp_path / "barrier.json"
    _write_rollback_authorities(
        database=database,
        journal=journal,
        barrier=barrier,
        repository=tmp_path / "repository",
        live_root=live,
        disabled=disabled,
        cutover_id="cutover",
        manifest_sha256="a" * 64,
    )
    with pytest.raises(MigrationError, match="not disabled preclaim"):
        cutover.rollback_cutover(
            journal_path=journal,
            barrier_path=barrier,
            runtime_config=config,
            database=database,
        )
    live_supervisor.release()
    assert scheduler.claim_next(
        controller,
        owner,
        pid=pid,
        process_starttime_ticks=starttime,
        boot_id=boot_id,
    )
    assert scheduler.status()["cutover_barrier"]["state"] == "sealed"

    operation_scheduler, operation_owner, operation_controller = _scheduler(
        tmp_path / "operation-root"
    )
    _finish_authoring(
        operation_scheduler,
        operation_owner,
        operation_controller,
        tmp_path / "operation-worktree",
    )
    operation_scheduler.prepare_cutover_barrier("operation", "9" * 64)
    integration = SingletonActor.acquire(operation_scheduler, "integration")
    operation_scheduler.begin_operation(
        "task", "integration", "first-integration", actor=integration.fence
    )
    assert operation_scheduler.status()["cutover_barrier"]["first_effect_kind"] == (
        "integration"
    )
    integration.release()


def test_rollback_serializes_concurrent_first_enable(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "race.sqlite3"
    scheduler = Scheduler(database, supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
    )
    scheduler.prepare_cutover_barrier("race", "a" * 64)
    disabled: dict[str, object] = {
        "enabled": False,
        "max_total_controllers": 0,
        "controller_concurrency": 0,
        "max_integrations": 0,
        "agent_limit": 0,
    }
    live = tmp_path / "live"
    runtime_config = live / "supervisor/runtime-config.json"
    runtime_config.parent.mkdir(parents=True)
    runtime_config.write_text(json.dumps(disabled), encoding="utf-8")
    journal = tmp_path / "journal.json"
    barrier = tmp_path / "barrier.json"
    _write_rollback_authorities(
        database=database,
        journal=journal,
        barrier=barrier,
        repository=tmp_path / "repository",
        live_root=live,
        disabled=disabled,
        cutover_id="race",
        manifest_sha256="a" * 64,
    )
    monkeypatch.setattr(cutover, "_verify_sqlite_service_stopped", lambda _unit: None)
    monkeypatch.setattr(cutover, "_authoring_processes", lambda *_args: [])
    entered = threading.Event()
    proceed = threading.Event()
    original_validate = cutover._validate_rollback_database
    calls = 0

    def blocking_validate(path: Path, identity: dict[str, object]) -> None:
        nonlocal calls
        original_validate(path, identity)
        calls += 1
        if calls == 1:
            entered.set()
            assert proceed.wait(timeout=5)

    monkeypatch.setattr(cutover, "_validate_rollback_database", blocking_validate)
    rollback_errors: list[BaseException] = []
    enable_errors: list[BaseException] = []

    def rollback_worker() -> None:
        try:
            cutover.rollback_cutover(
                journal_path=journal,
                barrier_path=barrier,
                runtime_config=runtime_config,
                database=database,
            )
        except BaseException as exc:  # pragma: no cover - asserted below
            rollback_errors.append(exc)

    def enable_worker() -> None:
        try:
            scheduler.first_enable()
        except BaseException as exc:
            enable_errors.append(exc)

    rollback_thread = threading.Thread(target=rollback_worker)
    rollback_thread.start()
    assert entered.wait(timeout=5)
    enable_thread = threading.Thread(target=enable_worker)
    enable_thread.start()
    time.sleep(0.1)
    assert enable_thread.is_alive()
    proceed.set()
    rollback_thread.join(timeout=5)
    enable_thread.join(timeout=5)
    assert not rollback_errors
    assert enable_errors
    assert not database.exists()
    assert (tmp_path / ".race.sqlite3.rolled-back.json").is_file()
    assert json.loads(journal.read_text())["phase"] == "rolled-back-preclaim"


def test_sqlite_service_template_has_singleton_failure_contract() -> None:
    root = Path(__file__).parents[1]
    service = (root / "ops/nl2repobench-authoring-supervisor-sqlite@.service").read_text()
    marker = (root / "ops/nl2repobench-authoring-failure-marker@.service").read_text()
    assert "--scheduler-db ${SCHEDULER_DB}" in service
    assert "RestartPreventExitStatus=2 64 78" in service
    assert "KillMode=control-group" in service
    assert "ExecStartPre=" in service
    assert "install_authoring_sqlite_service.py" in service
    assert (
        "ExecStartPre=/data/NL2RepoBench-integration-20260827/.venv/bin/python3 "
        "/data/NL2RepoBench-integration-20260827/scripts/install_authoring_sqlite_service.py"
        in service
    )
    assert "OnFailure=nl2repobench-authoring-failure-marker@%i.service" in service
    assert "StateDirectory=nl2repobench-authoring-failures" in marker
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    completed = subprocess.run(
        [
            str(root / ".venv/bin/python3"),
            str(root / "scripts/install_authoring_sqlite_service.py"),
            "--help",
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
