from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from nl2repobench.authoring import cutover
from nl2repobench.authoring.migration import MigrationError
from nl2repobench.authoring.runtime import SingletonActor, process_identity
from nl2repobench.authoring.scheduler import Identity, Scheduler


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
    import hashlib

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
    assert scheduler.status()["task_counts"] == {"complete": 1}


def test_cutover_freezes_only_after_disable_and_refuses_post_barrier_rollback(
    tmp_path: Path, monkeypatch
) -> None:
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
    monkeypatch.setattr(cutover, "_stop_service", lambda *args: events.append("service-stopped"))
    monkeypatch.setattr(cutover, "_stop_watcher", lambda *args: events.append("watcher-stopped"))
    monkeypatch.setattr(cutover, "_authoring_processes", lambda *args: [])
    monkeypatch.setattr(cutover, "_verify_docker", lambda *args: events.append("docker-verified"))

    def manifest(root, *, cutover_id):
        assert json.loads(config.read_text())["enabled"] is False
        events.append("manifest-frozen")
        return {"cutover_id": cutover_id, "manifest_sha256": "a" * 64}

    monkeypatch.setattr(cutover, "generate_manifest", manifest)
    monkeypatch.setattr(
        cutover, "validate_manifest", lambda *args: events.append("manifest-validated")
    )

    def imported(*args, **kwargs):
        Path(kwargs["db_path"]).write_bytes(b"sqlite")
        events.append("imported")
        return {"counts": {}}

    monkeypatch.setattr(cutover, "import_manifest", imported)
    monkeypatch.setattr(cutover, "_initialize_capacity", lambda *args: events.append("activated"))
    barrier = tmp_path / "barrier.json"
    cutover.execute_cutover(
        repository=tmp_path,
        live_root=live,
        manifest_path=tmp_path / "manifest.json",
        database=tmp_path / "scheduler.sqlite3",
        journal_path=tmp_path / "journal.json",
        barrier_path=barrier,
        cutover_id="cutover-3",
        service_unit="fake.service",
        drain_timeout=1,
    )

    assert events.index("manifest-frozen") > events.index("docker-verified")
    assert barrier.is_file()
    with pytest.raises(MigrationError, match="forbidden"):
        cutover.rollback_cutover(
            journal_path=tmp_path / "journal.json",
            barrier_path=barrier,
            runtime_config=config,
        )


def test_sqlite_service_template_has_singleton_failure_contract() -> None:
    root = Path(__file__).parents[1]
    service = (root / "ops/nl2repobench-authoring-supervisor-sqlite@.service").read_text()
    marker = (root / "ops/nl2repobench-authoring-failure-marker@.service").read_text()
    assert "--scheduler-db ${SCHEDULER_DB}" in service
    assert "RestartPreventExitStatus=2 64 78" in service
    assert "OnFailure=nl2repobench-authoring-failure-marker@%i.service" in service
    assert "StateDirectory=nl2repobench-authoring-failures" in marker
