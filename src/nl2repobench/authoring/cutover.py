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
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .backup import (
    activate_database,
    backup_database,
    database_content_digest,
    issue_quiescence_receipt,
    restore_database,
    verify_backup,
)
from .migration import MigrationError, generate_manifest, import_manifest, validate_manifest
from .runtime import command_digest, executable_digest, scheduler_for

LEGACY_SERVICE_UNIT = "nl2repobench-authoring-supervisor.service"
SQLITE_SERVICE_UNIT = re.compile(
    r"^nl2repobench-authoring-supervisor-sqlite@([A-Za-z0-9._-]+)\.service$"
)


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


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(value)
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


def _read_parent_pid(pid: int) -> int:
    try:
        stat_fields = (
            Path(f"/proc/{pid}/stat")
            .read_text(encoding="utf-8")
            .rsplit(")", 1)[1]
            .split()
        )
        parent_pid = int(stat_fields[1])
    except (OSError, ValueError, IndexError) as exc:
        raise MigrationError(f"cannot inspect process ancestry: {pid}") from exc
    if parent_pid < 0:
        raise MigrationError(f"invalid process ancestry: {pid}")
    return parent_pid


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
            if entry.exists():
                raise MigrationError(f"cannot inspect live process identity: {entry.name}")
            continue
        scoped = _scope_process(record, repository, live_root)
        if scoped is not None:
            records.append(scoped)
    return records


def _scope_process(
    record: ProcessRecord, repository: Path, live_root: Path
) -> ProcessRecord | None:
    command_scoped = str(repository.resolve()) in record.command or str(
        live_root.resolve()
    ) in record.command
    cwd_scoped = _under(record.cwd, repository)
    cgroup_scoped = "nl2repobench-authoring" in record.cgroup
    if not (command_scoped or cwd_scoped or cgroup_scoped):
        return None
    return replace(record, role="generic") if record.role == "other" else record


def _same_process(record: ProcessRecord) -> bool:
    current = _read_process(record.pid)
    return current == record


def _capture_operator_ancestors() -> tuple[ProcessRecord, ...]:
    ancestors: list[ProcessRecord] = []
    child_pid = os.getpid()
    visited = {child_pid}
    while True:
        parent_pid = _read_parent_pid(child_pid)
        if parent_pid == 0:
            break
        if parent_pid in visited:
            raise MigrationError("process ancestry contains a cycle")
        visited.add(parent_pid)
        record = _read_process(parent_pid)
        if record is None:
            raise MigrationError(f"cannot capture operator ancestor identity: {parent_pid}")
        ancestors.append(record)
        child_pid = parent_pid
    return tuple(ancestors)


def _revalidate_operator_ancestors(
    snapshot: tuple[ProcessRecord, ...],
) -> None:
    if _capture_operator_ancestors() != snapshot:
        raise MigrationError("trusted operator ancestor identity changed")


def _operator_ancestor_audit(
    snapshot: tuple[ProcessRecord, ...],
    repository: Path,
    live_root: Path,
) -> list[dict[str, Any]]:
    return [
        {
            "pid": record.pid,
            "starttime_ticks": record.starttime_ticks,
            "boot_id": record.boot_id,
            "role": record.role,
            "executable_digest": record.executable_digest,
            "argv_digest": record.argv_digest,
        }
        for ancestor in snapshot
        if (record := _scope_process(ancestor, repository, live_root)) is not None
        and record.role in {"pi", "generic"}
    ]


def _quiescence_processes(
    repository: Path,
    live_root: Path,
    operator_ancestors: tuple[ProcessRecord, ...],
) -> list[ProcessRecord]:
    _revalidate_operator_ancestors(operator_ancestors)
    trusted = tuple(
        scoped
        for ancestor in operator_ancestors
        if (scoped := _scope_process(ancestor, repository, live_root)) is not None
        and scoped.role in {"pi", "generic"}
    )
    return [
        record
        for record in _authoring_processes(repository, live_root)
        if not (
            record.role in {"pi", "generic"}
            and any(
                record.pid == ancestor.pid and record == ancestor
                for ancestor in trusted
            )
        )
    ]


def _wait_for_controllers(
    repository: Path,
    live_root: Path,
    timeout: int,
    operator_ancestors: tuple[ProcessRecord, ...],
) -> None:
    deadline = time.monotonic() + timeout
    while True:
        controllers = [
            record
            for record in _quiescence_processes(
                repository, live_root, operator_ancestors
            )
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


def _verify_mountinfo(
    worktree_root: Path, *, proc_root: Path = Path("/proc")
) -> None:
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        lines = _read_mountinfo(entry)
        if _mountinfo_conflicts(lines, worktree_root):
            raise MigrationError(f"process mount remains under worktrees: pid={entry.name}")


def _read_mountinfo(entry: Path) -> list[str]:
    mountinfo = entry / "mountinfo"
    try:
        return mountinfo.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        if entry.exists():
            raise MigrationError(
                f"cannot inspect mountinfo for live pid: {entry.name}"
            ) from exc
        return []


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
        invalid_chronology = int(
            db.execute(
                "SELECT count(*) FROM operation_receipts WHERE finished_at IS NOT NULL "
                "AND finished_at<started_at"
            ).fetchone()[0]
        )
        duplicate_terminal = db.execute(
            "SELECT task_id,operation_kind,count(*) count FROM operation_receipts "
            "WHERE (operation_kind='integration' AND status='pushed') "
            "OR (operation_kind='archive' AND status='verified') "
            "OR (operation_kind='cleanup' AND status='applied') "
            "GROUP BY task_id,operation_kind HAVING count(*)<>1"
        ).fetchall()
        if invalid_chronology or duplicate_terminal:
            raise MigrationError("receipt chronology or terminal receipt uniqueness is invalid")
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
                "SELECT operation_kind,status,started_at,finished_at FROM operation_receipts "
                "WHERE task_id=? AND status IN ('pushed','verified','applied') "
                "ORDER BY finished_at,operation_kind,receipt_id",
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
            _validate_stage_chronology(terminal)
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


def _validate_stage_chronology(terminal: dict[str, Any]) -> None:
    if not (
        terminal["integration"]["finished_at"]
        <= terminal["archive"]["started_at"]
        and terminal["archive"]["finished_at"]
        <= terminal["cleanup"]["started_at"]
    ):
        raise MigrationError("receipt operation stages overlap or are reversed")


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


@contextmanager
def _activation_authority(database: Path) -> Iterator[None]:
    independent = database.parent / f".{database.name}.activation.lock"
    scheduler_lock = database.parent / f".{database.name}.lock"
    with ExitStack() as stack:
        for path in (independent, scheduler_lock):
            if path.is_symlink():
                raise MigrationError("activation authority lock is a symlink")
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            stream = stack.enter_context(os.fdopen(fd, "a+"))
            fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def _prepare_staged_activation(staging: Path) -> None:
    if staging.is_symlink() or not staging.is_file():
        raise MigrationError("activation staging main file is missing or unsafe")
    with sqlite3.connect(staging) as db:
        checkpoint = db.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        db.commit()
    if checkpoint is None or int(checkpoint[0]) != 0:
        raise MigrationError("activation staging WAL checkpoint did not quiesce")
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(staging) + suffix)
        if sidecar.is_symlink() or (sidecar.exists() and not sidecar.is_file()):
            raise MigrationError("activation staging sidecar is unsafe")
        sidecar.unlink(missing_ok=True)


def _activate_cutover_database(staging: Path, database: Path) -> None:
    _prepare_staged_activation(staging)
    with _activation_authority(database):
        if not staging.is_file() or any(
            Path(str(staging) + suffix).exists() for suffix in ("-wal", "-shm")
        ):
            raise MigrationError("activation staging file set changed before rename")
        if any(
            Path(str(database) + suffix).exists() for suffix in ("", "-wal", "-shm")
        ):
            raise MigrationError("activation target file set changed before rename")
        activate_database(staging, database, activate=True)


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
    sqlite_service_unit: str,
    sqlite_env_file: Path,
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
        or service_unit != LEGACY_SERVICE_UNIT
    ):
        raise MigrationError("cutover identifiers, timeout, or resource limits are invalid")
    unit_match = SQLITE_SERVICE_UNIT.fullmatch(sqlite_service_unit)
    if unit_match is None:
        raise MigrationError("SQLite service unit is not the tracked template instance")
    expected_env = Path(
        f"/etc/nl2repobench/authoring-scheduler-{unit_match.group(1)}.env"
    )
    if sqlite_env_file != expected_env or not database.is_absolute():
        raise MigrationError("SQLite service environment or database path is not exact")
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
    ) or (database.parent / f".{database.name}.rolled-back.json").exists():
        raise MigrationError("cutover target or preclaim record already exists")
    runtime_config = live_root / "supervisor/runtime-config.json"
    operator_ancestors = _capture_operator_ancestors()
    audit = {
        "pre_drain_inventory_sha256": inventory_digest(live_root),
        "cutover_id": cutover_id,
        "trusted_operator_ancestors": _operator_ancestor_audit(
            operator_ancestors, repository, live_root
        ),
    }
    disabled = disable_legacy_config(runtime_config)
    _atomic_json(
        journal_path,
        {**audit, "phase": "draining", "legacy_runtime_config": disabled, "rollback_allowed": True},
    )
    staging = database.with_name(f".{database.name}.{cutover_id}.staging")
    try:
        _wait_for_controllers(
            repository, live_root, drain_timeout, operator_ancestors
        )
        _disable_and_mask_service(service_unit)
        with ExitStack() as stack:
            _acquire_lock(stack, live_root / "archive.lock")
            watcher_snapshot = _quiescence_processes(
                repository, live_root, operator_ancestors
            )
            _stop_watcher(watcher_snapshot, drain_timeout)
            _acquire_lock(stack, live_root / "supervisor.lock")
            remaining = _quiescence_processes(
                repository, live_root, operator_ancestors
            )
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
            _activate_cutover_database(staging, database)
            activated = _database_validation(database, validation["task_count"])
            database_digest = hashlib.sha256(database.read_bytes()).hexdigest()
            preclaim = {
                "schema_version": "authoring-cutover-barrier/v2",
                "cutover_id": cutover_id,
                "manifest_sha256": manifest["manifest_sha256"],
                "database": str(database.resolve()),
                "database_sha256": database_digest,
                "rollback_allowed": True,
                "state_at_activation": "prepared",
                "authority": "database.cutover_barrier",
                "sqlite_service_unit": sqlite_service_unit,
                "sqlite_env_file": str(sqlite_env_file),
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
                    "manifest_sha256": manifest["manifest_sha256"],
                    "database": str(database.resolve()),
                    "database_sha256": database_digest,
                    "repository": str(repository.resolve()),
                    "live_root": str(live_root.resolve()),
                    "legacy_service_unit": service_unit,
                    "sqlite_service_unit": sqlite_service_unit,
                    "sqlite_env_file": str(sqlite_env_file),
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


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError(f"{label} is missing or invalid") from exc
    if not isinstance(value, dict):
        raise MigrationError(f"{label} must be an object")
    return value


def _rollback_identity(
    journal_path: Path, barrier_path: Path, database: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    journal = _read_json_object(journal_path, "cutover journal")
    record = _read_json_object(barrier_path, "cutover barrier record")
    database_name = str(database.resolve())
    required = {
        "phase": "activated-preclaim",
        "rollback_allowed": True,
        "database": database_name,
    }
    if any(journal.get(key) != value for key, value in required.items()):
        raise MigrationError("cutover journal is not rollback-eligible")
    cutover_id = journal.get("cutover_id")
    manifest_digest = journal.get("manifest_sha256")
    database_digest = journal.get("database_sha256")
    if (
        not isinstance(cutover_id, str)
        or not re.fullmatch(r"[A-Za-z0-9._:-]{1,200}", cutover_id)
        or not isinstance(manifest_digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", manifest_digest)
        or not isinstance(database_digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", database_digest)
    ):
        raise MigrationError("cutover journal identity is incomplete")
    sqlite_unit = journal.get("sqlite_service_unit")
    sqlite_env = journal.get("sqlite_env_file")
    unit_match = SQLITE_SERVICE_UNIT.fullmatch(str(sqlite_unit))
    if (
        unit_match is None
        or sqlite_env
        != f"/etc/nl2repobench/authoring-scheduler-{unit_match.group(1)}.env"
    ):
        raise MigrationError("cutover deployment binding is incomplete")
    record_required = {
        "schema_version": "authoring-cutover-barrier/v2",
        "cutover_id": cutover_id,
        "manifest_sha256": manifest_digest,
        "database": database_name,
        "database_sha256": database_digest,
        "rollback_allowed": True,
        "state_at_activation": "prepared",
        "authority": "database.cutover_barrier",
        "sqlite_service_unit": journal.get("sqlite_service_unit"),
        "sqlite_env_file": journal.get("sqlite_env_file"),
    }
    if any(record.get(key) != value for key, value in record_required.items()):
        raise MigrationError("cutover barrier identity does not match journal")
    return journal, record


@contextmanager
def _rollback_authority(database: Path, journal_path: Path) -> Iterator[None]:
    independent = journal_path.parent / f".{journal_path.name}.rollback.lock"
    scheduler_lock = database.parent / f".{database.name}.lock"
    with ExitStack() as stack:
        for path in (independent, scheduler_lock):
            if path.is_symlink():
                raise MigrationError("rollback authority lock is a symlink")
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            stream = stack.enter_context(os.fdopen(fd, "a+"))
            fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def _validate_rollback_database(
    database: Path, journal: dict[str, Any]
) -> None:
    if hashlib.sha256(database.read_bytes()).hexdigest() != journal["database_sha256"]:
        raise MigrationError("rollback database digest does not match cutover journal")
    uri = f"file:{database.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.row_factory = sqlite3.Row
        barrier = db.execute("SELECT * FROM cutover_barrier WHERE barrier_id=1").fetchone()
        config = db.execute("SELECT * FROM current_runtime_config").fetchone()
        if (
            barrier is None
            or barrier["cutover_id"] != journal["cutover_id"]
            or barrier["manifest_sha256"] != journal["manifest_sha256"]
            or barrier["state"] != "prepared"
            or int(barrier["rollback_allowed"]) != 1
            or config is None
            or bool(config["enabled"])
            or any(
                int(config[key]) != 0
                for key in (
                    "max_total_controllers",
                    "controller_concurrency",
                    "max_integrations",
                    "agent_limit",
                )
            )
        ):
            raise MigrationError("rollback database is not disabled preclaim state")
        nonzero = db.execute(
            "SELECT count(*) FROM capacity_rows WHERE limit_count<>0 OR used_count<>0 "
            "OR remaining_count<>0"
        ).fetchone()[0]
        live = db.execute(
            "SELECT (SELECT count(*) FROM controllers WHERE state IN ('running','draining')) + "
            "(SELECT count(*) FROM claims WHERE active=1) + "
            "(SELECT count(*) FROM scheduler_leases WHERE active=1) + "
            "(SELECT count(*) FROM controller_slot_reservations "
            "WHERE state IN ('reserved','activated'))"
        ).fetchone()[0]
        if int(nonzero) or int(live):
            raise MigrationError("rollback database still has capacity or live actors")


def _verify_sqlite_service_stopped(unit: str) -> None:
    if SQLITE_SERVICE_UNIT.fullmatch(unit) is None:
        raise MigrationError("rollback SQLite service unit is invalid")
    control_group = _systemctl("show", "--property=ControlGroup", "--value", unit)
    _verify_empty_cgroup(control_group)


def install_service_binding(
    *,
    journal_path: Path,
    barrier_path: Path,
    database: Path,
    sqlite_service_unit: str,
    sqlite_env_file: Path,
    write: bool = False,
) -> dict[str, str]:
    """Validate and optionally install the exact cutover DB environment binding."""
    with _rollback_authority(database, journal_path):
        journal, _record = _rollback_identity(journal_path, barrier_path, database)
        if (
            journal.get("sqlite_service_unit") != sqlite_service_unit
            or journal.get("sqlite_env_file") != str(sqlite_env_file)
        ):
            raise MigrationError("installer arguments do not match cutover deployment binding")
        _validate_service_database(database, journal)
        content = (
            f"SCHEDULER_DB={database.resolve()}\n"
            f"CUTOVER_ID={journal['cutover_id']}\n"
            f"CUTOVER_JOURNAL={journal_path.resolve()}\n"
            f"CUTOVER_BARRIER={barrier_path.resolve()}\n"
        )
        if write:
            _atomic_text(sqlite_env_file, content)
        return {
            "sqlite_service_unit": sqlite_service_unit,
            "sqlite_env_file": str(sqlite_env_file),
            "scheduler_db": str(database.resolve()),
            "cutover_id": str(journal["cutover_id"]),
            "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "installed": str(write).lower(),
        }


def _validate_service_database(database: Path, journal: dict[str, Any]) -> None:
    uri = f"file:{database.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.row_factory = sqlite3.Row
        barrier = db.execute("SELECT * FROM cutover_barrier WHERE barrier_id=1").fetchone()
        if (
            barrier is None
            or barrier["cutover_id"] != journal["cutover_id"]
            or barrier["manifest_sha256"] != journal["manifest_sha256"]
            or barrier["state"] not in {"prepared", "sealed"}
        ):
            raise MigrationError("installed service database does not match cutover identity")
        if barrier["state"] == "prepared" and (
            hashlib.sha256(database.read_bytes()).hexdigest()
            != journal["database_sha256"]
        ):
            raise MigrationError("prepared service database digest changed before first enable")


@contextmanager
def _restore_authority(database: Path) -> Iterator[None]:
    independent = database.parent / f".{database.name}.restore-authority.lock"
    scheduler_lock = database.parent / f".{database.name}.lock"
    with ExitStack() as stack:
        for path in (independent, scheduler_lock):
            if path.is_symlink():
                raise MigrationError("restore authority lock is a symlink")
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            stream = stack.enter_context(os.fdopen(fd, "a+"))
            fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def _validate_restore_quiescence(
    database: Path, journal: dict[str, Any]
) -> dict[str, Any]:
    uri = f"file:{database.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.row_factory = sqlite3.Row
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise MigrationError("restore target database integrity check failed")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise MigrationError("restore target database foreign keys are invalid")
        config = db.execute("SELECT * FROM current_runtime_config").fetchone()
        barrier = db.execute("SELECT * FROM cutover_barrier WHERE barrier_id=1").fetchone()
        if (
            config is None
            or bool(config["enabled"])
            or any(
                int(config[key]) != 0
                for key in (
                    "max_total_controllers",
                    "controller_concurrency",
                    "max_integrations",
                    "agent_limit",
                )
            )
            or barrier is None
            or barrier["cutover_id"] != journal["cutover_id"]
            or barrier["manifest_sha256"] != journal["manifest_sha256"]
        ):
            raise MigrationError("restore target is not disabled cutover state")
        nonzero = int(
            db.execute(
                "SELECT count(*) FROM capacity_rows WHERE limit_count<>0 OR used_count<>0 "
                "OR remaining_count<>0"
            ).fetchone()[0]
        )
        active = int(
            db.execute(
                "SELECT (SELECT count(*) FROM claims WHERE active=1) + "
                "(SELECT count(*) FROM controllers WHERE state IN ('running','draining')) + "
                "(SELECT count(*) FROM scheduler_leases WHERE active=1) + "
                "(SELECT count(*) FROM controller_slot_reservations "
                "WHERE state IN ('reserved','activated'))"
            ).fetchone()[0]
        )
        generation = int(
            db.execute("SELECT COALESCE(MAX(generation),0) FROM scheduler_leases").fetchone()[0]
        )
        if nonzero or active:
            raise MigrationError("restore target has capacity or active scheduler actors")
    return {
        "generation": generation,
        "target_file_sha256": hashlib.sha256(database.read_bytes()).hexdigest(),
        "target_content_digest": database_content_digest(database),
    }


def restore_cutover_database(
    *,
    backup_directory: Path,
    database: Path,
    journal_path: Path,
    barrier_path: Path,
    runtime_config: Path,
    receipt_authority: Path,
) -> dict[str, Any]:
    """Issue and consume a cutover-grade restore receipt under held authorities."""
    with _restore_authority(database):
        journal, _record = _rollback_identity(journal_path, barrier_path, database)
        repository = Path(str(journal.get("repository", "")))
        live_root = Path(str(journal.get("live_root", "")))
        operator_ancestors = _capture_operator_ancestors()
        operator_audit = _operator_ancestor_audit(
            operator_ancestors, repository, live_root
        )
        disabled = _read_json_object(runtime_config, "legacy runtime config")
        if (
            runtime_config.resolve()
            != (live_root / "supervisor/runtime-config.json").resolve()
            or disabled.get("enabled") is not False
            or any(
                int(disabled.get(key, -1)) != 0
                for key in (
                    "max_total_controllers",
                    "controller_concurrency",
                    "max_integrations",
                    "agent_limit",
                )
            )
        ):
            raise MigrationError("legacy admissions are not disabled for restore")
        _atomic_json(
            journal_path,
            {**journal, "restore_trusted_operator_ancestors": operator_audit},
        )
        if _quiescence_processes(repository, live_root, operator_ancestors):
            raise MigrationError("repository actors remain during restore")
        _verify_sqlite_service_stopped(str(journal["sqlite_service_unit"]))
        _verify_docker(live_root / "worktrees")
        verify_backup(backup_directory)
        _validate_restore_quiescence(backup_directory / "database.sqlite3", journal)
        observed = _validate_restore_quiescence(database, journal)
        evidence = {
            "schema_version": "cutover-restore-quiescence/v1",
            "cutover_id": journal["cutover_id"],
            "database": str(database.resolve()),
            "target_file_sha256": observed["target_file_sha256"],
            "target_content_digest": observed["target_content_digest"],
            "generation": observed["generation"],
            "observed_at": datetime.now(UTC).isoformat(),
            "quiesced": True,
        }
        receipt = issue_quiescence_receipt(
            backup_directory,
            database,
            receipt_authority,
            cutover_evidence=evidence,
            generation=int(observed["generation"]),
        )
        if _quiescence_processes(repository, live_root, operator_ancestors):
            raise MigrationError("repository actors appeared before restore activation")
        _verify_sqlite_service_stopped(str(journal["sqlite_service_unit"]))
        _verify_docker(live_root / "worktrees")
        if _validate_restore_quiescence(database, journal) != observed:
            raise MigrationError("restore target changed after receipt issuance")
        result = restore_database(
            backup_directory,
            database,
            activate=True,
            quiescence_marker=receipt,
            _scheduler_lock_held=True,
        )
        return {"receipt": str(receipt), "restore": result, "evidence": evidence}


def rollback_cutover(
    *, journal_path: Path, barrier_path: Path, runtime_config: Path, database: Path
) -> None:
    with _rollback_authority(database, journal_path):
        journal, _record = _rollback_identity(journal_path, barrier_path, database)
        disabled = journal.get("legacy_runtime_config")
        if not isinstance(disabled, dict) or disabled.get("enabled") is not False:
            raise MigrationError("cutover journal lacks a disabled legacy configuration")
        repository = Path(str(journal.get("repository", "")))
        live_root = Path(str(journal.get("live_root", "")))
        if (
            not repository.is_absolute()
            or not live_root.is_absolute()
            or runtime_config.resolve()
            != (live_root / "supervisor/runtime-config.json").resolve()
        ):
            raise MigrationError("rollback repository or runtime config identity is invalid")
        actors = _authoring_processes(repository, live_root)
        if actors:
            raise MigrationError(
                f"rollback found live SQLite/repository actors: {[actor.pid for actor in actors]}"
            )
        _verify_sqlite_service_stopped(str(journal.get("sqlite_service_unit", "")))
        _validate_rollback_database(database, journal)
        # Re-read every authority under both locks immediately before deletion.
        current_journal, _current_record = _rollback_identity(
            journal_path, barrier_path, database
        )
        _validate_rollback_database(database, current_journal)
        _atomic_json(runtime_config, disabled)
        rollback_marker = database.parent / f".{database.name}.rolled-back.json"
        _atomic_json(
            rollback_marker,
            {
                "schema_version": "authoring-rollback-tombstone/v1",
                "cutover_id": current_journal["cutover_id"],
                "manifest_sha256": current_journal["manifest_sha256"],
                "database_sha256": current_journal["database_sha256"],
            },
        )
        for suffix in ("", "-wal", "-shm"):
            Path(str(database) + suffix).unlink(missing_ok=True)
        _atomic_json(
            journal_path,
            {**current_journal, "phase": "rolled-back-preclaim", "rollback_allowed": False},
        )
