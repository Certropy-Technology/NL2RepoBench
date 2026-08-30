"""Explicit, auditable legacy-to-SQLite cutover orchestration."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import signal
import sqlite3
import subprocess
import tempfile
import time
from contextlib import ExitStack
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .backup import activate_database, backup_database, verify_backup
from .migration import MigrationError, generate_manifest, import_manifest, validate_manifest
from .runtime import command_digest, executable_digest, scheduler_for


@dataclass(frozen=True)
class ProcessRecord:
    pid: int
    starttime_ticks: int
    boot_id: str
    executable: str
    executable_digest: str
    argv_digest: str
    command: str
    cwd: str
    cgroup: str
    role: str


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inventory_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        item for item in root.rglob("*") if item.is_file() and not item.is_symlink()
    ):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(relative + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def disable_legacy_config(path: Path) -> dict[str, Any]:
    original = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(original, dict):
        raise MigrationError("legacy runtime config must be an object")
    disabled = {
        **original,
        "enabled": False,
        "max_total_controllers": 0,
        "controller_concurrency": 0,
        "max_integrations": 0,
        "agent_limit": 0,
    }
    _atomic_json(path, disabled)
    return disabled


def _read_process(pid: int) -> ProcessRecord | None:
    proc = Path(f"/proc/{pid}")
    try:
        stat_fields = (proc / "stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()
        starttime = int(stat_fields[19])
        boot_id = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="utf-8").strip()
        argv = (proc / "cmdline").read_bytes().split(b"\0")
        command = " ".join(value.decode(errors="replace") for value in argv if value)
        cwd = os.path.realpath(proc / "cwd")
        executable = os.path.realpath(proc / "exe")
        cgroup = (proc / "cgroup").read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError, IndexError):
        return None
    role = "other"
    if "run_authoring_loop.py" in command:
        role = "controller"
    elif "archive_authoring_live.py" in command:
        role = "watcher"
    elif "authoring_supervisor.py" in command:
        role = "supervisor"
    elif any(Path(value.decode(errors="replace")).name == "pi" for value in argv if value):
        role = "pi"
    return ProcessRecord(
        pid,
        starttime,
        boot_id,
        executable,
        executable_digest(executable),
        command_digest([value.decode(errors="replace") for value in argv if value]),
        command,
        cwd,
        cgroup,
        role,
    )


def _under(path: str, root: Path) -> bool:
    value = Path(path).resolve()
    expected = root.resolve()
    return value == expected or expected in value.parents


def _authoring_processes(repository: Path, live_root: Path) -> list[ProcessRecord]:
    records: list[ProcessRecord] = []
    repository = repository.resolve()
    live_root = live_root.resolve()
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        record = _read_process(int(entry.name))
        if record is None:
            continue
        cwd_worktree = _under(record.cwd, live_root / "worktrees")
        if record.role == "other" and cwd_worktree:
            record = replace(record, role="workspace")
        if record.role == "other":
            continue
        command_scoped = str(repository) in record.command or str(live_root) in record.command
        cwd_scoped = _under(record.cwd, repository)
        cgroup_scoped = "nl2repobench-authoring" in record.cgroup
        if command_scoped or cwd_scoped or cgroup_scoped:
            records.append(record)
    return records


def _same_process(record: ProcessRecord) -> bool:
    current = _read_process(record.pid)
    return current == record


def _wait_for_controllers(repository: Path, live_root: Path, timeout: int) -> None:
    deadline = time.monotonic() + timeout
    while True:
        controllers = [
            record
            for record in _authoring_processes(repository, live_root)
            if record.role in {"controller", "pi"}
        ]
        if not controllers:
            return
        if time.monotonic() >= deadline:
            raise MigrationError(
                f"controller/Pi drain timed out with pids {[record.pid for record in controllers]}"
            )
        time.sleep(1)


def _systemctl(*arguments: str) -> str:
    completed = subprocess.run(
        ["systemctl", *arguments], capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise MigrationError(
            f"systemctl {' '.join(arguments)} failed: "
            f"{(completed.stderr or completed.stdout)[-1000:]}"
        )
    return completed.stdout.strip()


def _disable_and_mask_service(unit: str) -> None:
    _systemctl("disable", "--now", unit)
    _systemctl("mask", "--runtime", unit)
    control_group = _systemctl("show", "--property=ControlGroup", "--value", unit)
    _verify_empty_cgroup(control_group)


def _verify_empty_cgroup(
    control_group: str, *, cgroup_root: Path = Path("/sys/fs/cgroup")
) -> None:
    if not control_group:
        return
    relative = Path(control_group.lstrip("/"))
    if ".." in relative.parts:
        raise MigrationError("systemd returned an unsafe control group")
    procs = cgroup_root / relative / "cgroup.procs"
    if procs.is_file() and procs.read_text(encoding="utf-8").strip():
        raise MigrationError("legacy systemd cgroup is not empty")


def _stop_watcher(records: list[ProcessRecord], timeout: int) -> None:
    watchers = [record for record in records if record.role == "watcher"]
    for record in watchers:
        if not _same_process(record):
            raise MigrationError(f"watcher identity changed before stop: {record.pid}")
        os.kill(record.pid, signal.SIGTERM)
    deadline = time.monotonic() + timeout
    while any(_same_process(record) for record in watchers):
        if time.monotonic() >= deadline:
            raise MigrationError("archive watcher did not stop")
        time.sleep(0.2)


def _acquire_lock(stack: ExitStack, path: Path) -> None:
    stream = stack.enter_context(path.open("a+", encoding="utf-8"))
    try:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise MigrationError(f"legacy lock is still held: {path}") from exc


def _mount_path(raw: str) -> Path:
    for escaped, value in (("\\040", " "), ("\\011", "\t"), ("\\134", "\\")):
        raw = raw.replace(escaped, value)
    return Path(raw).resolve()


def _verify_mountinfo(worktree_root: Path) -> None:
    for entry in Path("/proc").iterdir():
        mountinfo = entry / "mountinfo"
        if not entry.name.isdigit() or not mountinfo.is_file():
            continue
        try:
            lines = mountinfo.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        if _mountinfo_conflicts(lines, worktree_root):
            raise MigrationError(f"process mount remains under worktrees: pid={entry.name}")


def _mountinfo_conflicts(lines: list[str], worktree_root: Path) -> bool:
    for line in lines:
        fields = line.split()
        if "-" not in fields or len(fields) < 6:
            continue
        separator = fields.index("-")
        candidates = (fields[3], fields[4], fields[separator + 2])
        if any(
            value.startswith("/") and _under(str(_mount_path(value)), worktree_root)
            for value in candidates
        ):
            return True
    return False


def _verify_docker(worktree_root: Path) -> None:
    listed = subprocess.run(
        ["docker", "ps", "-aq"], capture_output=True, text=True, check=False
    )
    if listed.returncode != 0:
        raise MigrationError("Docker inspection unavailable during cutover")
    ids = listed.stdout.split()
    if ids:
        inspected = subprocess.run(
            ["docker", "inspect", *ids], capture_output=True, text=True, check=False
        )
        if inspected.returncode != 0:
            raise MigrationError("Docker structured inspection failed")
        try:
            records = json.loads(inspected.stdout)
        except json.JSONDecodeError as exc:
            raise MigrationError("Docker inspection returned invalid JSON") from exc
        for record in records:
            for mount in record.get("Mounts", []) if isinstance(record, dict) else []:
                if not isinstance(mount, dict):
                    continue
                source = mount.get("Source")
                if isinstance(source, str) and _under(source, worktree_root):
                    raise MigrationError(
                        f"Docker container mount remains under worktrees: {record.get('Id')}"
                    )
    _verify_mountinfo(worktree_root)


def _manifest_task_count(manifest: dict[str, Any], live_root: Path) -> int:
    count = 0
    for lane in manifest["lanes"]:
        source = Path(str(lane["queue_source"]))
        payload = json.loads(
            (source if source.is_absolute() else live_root / source).read_text(encoding="utf-8")
        )
        queue = payload.get("queue", []) if isinstance(payload, dict) else []
        count += len(
            {
                str(item["candidate_id"])
                for item in queue
                if isinstance(item, dict) and item.get("candidate_id")
            }
        )
    return count


def _database_validation(database: Path, expected_tasks: int) -> dict[str, Any]:
    with sqlite3.connect(database) as db:
        db.row_factory = sqlite3.Row
        integrity = str(db.execute("PRAGMA integrity_check").fetchone()[0])
        foreign_keys = db.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or foreign_keys:
            raise MigrationError("scheduler database integrity or foreign-key check failed")
        task_count = int(db.execute("SELECT count(*) FROM tasks").fetchone()[0])
        if task_count != expected_tasks:
            raise MigrationError(
                f"scheduler task count mismatch: expected {expected_tasks}, got {task_count}"
            )
        dangling = int(
            db.execute(
                "SELECT count(*) FROM operation_receipts WHERE status IN ('started','committed')"
            ).fetchone()[0]
        )
        if dangling:
            raise MigrationError("import contains abandoned operation receipts")
        config = db.execute("SELECT * FROM current_runtime_config").fetchone()
        if config is None or bool(config["enabled"]) or any(
            int(config[key]) != 0
            for key in (
                "max_total_controllers",
                "controller_concurrency",
                "max_integrations",
                "agent_limit",
            )
        ):
            raise MigrationError("activated scheduler is not disabled with zero limits")
        nonzero_capacity = int(
            db.execute(
                "SELECT count(*) FROM capacity_rows WHERE limit_count<>0 "
                "OR used_count<>0 OR remaining_count<>0"
            ).fetchone()[0]
        )
        live_runtime = int(
            db.execute(
                "SELECT (SELECT count(*) FROM controllers WHERE state IN ('running','draining')) + "
                "(SELECT count(*) FROM claims WHERE active=1) + "
                "(SELECT count(*) FROM scheduler_leases WHERE active=1)"
            ).fetchone()[0]
        )
        barrier = db.execute("SELECT state,rollback_allowed FROM cutover_barrier").fetchone()
        if nonzero_capacity or live_runtime or barrier is None or tuple(barrier) != ("prepared", 1):
            raise MigrationError("activated scheduler runtime is not preclaim-quiescent")
        completed = db.execute("SELECT task_id FROM tasks WHERE state='complete'").fetchall()
        for task in completed:
            receipts = db.execute(
                "SELECT operation_kind,status,finished_at FROM operation_receipts "
                "WHERE task_id=? AND status IN ('pushed','verified','applied')",
                (task["task_id"],),
            ).fetchall()
            terminal = {str(row["operation_kind"]): row for row in receipts}
            if set(terminal) != {"integration", "archive", "cleanup"}:
                raise MigrationError("complete task lacks a unique terminal receipt chain")
            times = [
                terminal[kind]["finished_at"]
                for kind in ("integration", "archive", "cleanup")
            ]
            if any(value is None for value in times) or times != sorted(times):
                raise MigrationError("receipt chronology is invalid")
        counts = {
            str(row["state"]): int(row["count"])
            for row in db.execute("SELECT state,count(*) count FROM tasks GROUP BY state")
        }
    return {
        "integrity": integrity,
        "foreign_key_errors": len(foreign_keys),
        "task_count": task_count,
        "task_counts": counts,
    }


def _initialize_staging(
    database: Path,
    *,
    cutover_id: str,
    manifest_sha256: str,
    repository_min_free_bytes: int,
    docker_min_free_bytes: int,
    watcher_min_free_bytes: int,
) -> None:
    scheduler = scheduler_for(database)
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
        changed_by="cutover",
        reason="disabled preclaim activation",
    )
    scheduler.configure_resource_policy(
        repository_min_free_bytes=repository_min_free_bytes,
        docker_min_free_bytes=docker_min_free_bytes,
        watcher_min_free_bytes=watcher_min_free_bytes,
        changed_by="cutover",
        reason="operator supplied cutover resource policy",
    )
    scheduler.prepare_cutover_barrier(cutover_id, manifest_sha256)


def execute_cutover(
    *,
    repository: Path,
    live_root: Path,
    manifest_path: Path,
    database: Path,
    backup_directory: Path,
    journal_path: Path,
    barrier_path: Path,
    cutover_id: str,
    service_unit: str,
    drain_timeout: int,
    repository_min_free_bytes: int,
    docker_min_free_bytes: int,
    watcher_min_free_bytes: int,
) -> dict[str, Any]:
    if (
        not re.fullmatch(r"[A-Za-z0-9._:-]{1,200}", cutover_id)
        or drain_timeout < 1
        or any(
            value <= 0
            for value in (
                repository_min_free_bytes,
                docker_min_free_bytes,
                watcher_min_free_bytes,
            )
        )
        or not service_unit.strip()
    ):
        raise MigrationError("cutover identifiers, timeout, or resource limits are invalid")
    live_resolved = live_root.resolve()
    for output in (
        manifest_path,
        database,
        backup_directory,
        journal_path,
        barrier_path,
    ):
        resolved = output.resolve()
        if resolved == live_resolved or live_resolved in resolved.parents:
            raise MigrationError("cutover outputs must remain outside the legacy live tree")
    if barrier_path.exists() or any(
        Path(str(database) + suffix).exists() for suffix in ("", "-wal", "-shm")
    ):
        raise MigrationError("cutover target or preclaim record already exists")
    runtime_config = live_root / "supervisor/runtime-config.json"
    audit = {"pre_drain_inventory_sha256": inventory_digest(live_root), "cutover_id": cutover_id}
    disabled = disable_legacy_config(runtime_config)
    _atomic_json(
        journal_path,
        {**audit, "phase": "draining", "legacy_runtime_config": disabled, "rollback_allowed": True},
    )
    staging = database.with_name(f".{database.name}.{cutover_id}.staging")
    try:
        _wait_for_controllers(repository, live_root, drain_timeout)
        _disable_and_mask_service(service_unit)
        with ExitStack() as stack:
            _acquire_lock(stack, live_root / "archive.lock")
            watcher_snapshot = _authoring_processes(repository, live_root)
            _stop_watcher(watcher_snapshot, drain_timeout)
            _acquire_lock(stack, live_root / "supervisor.lock")
            remaining = _authoring_processes(repository, live_root)
            if remaining:
                raise MigrationError(
                    "repository authoring actors remain after stop: "
                    f"{[item.pid for item in remaining]}"
                )
            _verify_docker(live_root / "worktrees")
            manifest = generate_manifest(live_root, cutover_id=cutover_id)
            validate_manifest(manifest, live_root)
            _atomic_json(manifest_path, manifest)
            imported = import_manifest(
                manifest,
                live_root,
                db_path=staging,
                dry_run=False,
                barrier=lambda: {"barrier": "quiesced", "stopped": False},
            )
            _initialize_staging(
                staging,
                cutover_id=cutover_id,
                manifest_sha256=str(manifest["manifest_sha256"]),
                repository_min_free_bytes=repository_min_free_bytes,
                docker_min_free_bytes=docker_min_free_bytes,
                watcher_min_free_bytes=watcher_min_free_bytes,
            )
            validation = _database_validation(
                staging, _manifest_task_count(manifest, live_root)
            )
            if imported.get("counts") != validation["task_counts"]:
                raise MigrationError("import summary does not match final database counts")
            backup_database(staging, backup_directory)
            backup = verify_backup(backup_directory)
            activate_database(staging, database, activate=True)
            activated = _database_validation(database, validation["task_count"])
            preclaim = {
                "schema_version": "authoring-cutover-barrier/v2",
                "cutover_id": cutover_id,
                "manifest_sha256": manifest["manifest_sha256"],
                "database": str(database),
                "state_at_activation": "prepared",
                "authority": "database.cutover_barrier",
            }
            _atomic_json(barrier_path, preclaim)
            _atomic_json(
                journal_path,
                {
                    **audit,
                    "phase": "activated-preclaim",
                    "barrier": str(barrier_path),
                    "legacy_runtime_config": disabled,
                    "rollback_allowed": True,
                },
            )
            return {
                "manifest": str(manifest_path),
                "database": str(database),
                "import": imported,
                "validation": activated,
                "backup": backup,
                "barrier": preclaim,
            }
    except Exception:
        for path in (staging, Path(str(staging) + "-wal"), Path(str(staging) + "-shm")):
            path.unlink(missing_ok=True)
        _atomic_json(
            journal_path,
            {
                **audit,
                "phase": "failed-preclaim",
                "legacy_runtime_config": disabled,
                "rollback_allowed": True,
            },
        )
        raise


def rollback_cutover(
    *, journal_path: Path, barrier_path: Path, runtime_config: Path, database: Path
) -> None:
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    disabled = journal.get("legacy_runtime_config")
    if not isinstance(disabled, dict) or disabled.get("enabled") is not False:
        raise MigrationError("cutover journal lacks a disabled legacy configuration")
    if database.is_file():
        scheduler = scheduler_for(database)
        barrier = scheduler.status().get("cutover_barrier")
        if not isinstance(barrier, dict) or barrier.get("state") != "prepared":
            raise MigrationError("rollback is forbidden after the first SQLite side effect")
    if barrier_path.is_file():
        record = json.loads(barrier_path.read_text(encoding="utf-8"))
        if record.get("database") not in {None, str(database)}:
            raise MigrationError("rollback record points to another database")
    _atomic_json(runtime_config, disabled)
    for suffix in ("", "-wal", "-shm"):
        Path(str(database) + suffix).unlink(missing_ok=True)
    _atomic_json(
        journal_path,
        {**journal, "phase": "rolled-back-preclaim", "rollback_allowed": True},
    )
