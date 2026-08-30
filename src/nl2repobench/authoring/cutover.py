"""Explicit, auditable legacy-to-SQLite cutover orchestration."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import signal
import subprocess
import tempfile
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Any

from .migration import MigrationError, generate_manifest, import_manifest, validate_manifest
from .runtime import scheduler_for


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
    return original


def _authoring_processes(repository: Path, live_root: Path) -> list[int]:
    found: list[int] = []
    needles = ("run_authoring_loop.py", "authoring_supervisor.py", "archive_authoring_live.py")
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            cwd = os.path.realpath(entry / "cwd")
        except OSError:
            continue
        if any(needle in command for needle in needles) or cwd.startswith(str(live_root)):
            found.append(int(entry.name))
    return found


def _wait_for_controllers(repository: Path, live_root: Path, timeout: int) -> None:
    deadline = time.monotonic() + timeout
    while True:
        pids = _authoring_processes(repository, live_root)
        controllers = [
            pid
            for pid in pids
            if "run_authoring_loop.py"
            in Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="ignore")
        ]
        if not controllers:
            return
        if time.monotonic() >= deadline:
            raise MigrationError(f"controller drain timed out with pids {controllers}")
        time.sleep(1)


def _stop_service(unit: str) -> None:
    completed = subprocess.run(
        ["systemctl", "stop", unit], capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise MigrationError(
            f"systemd stop failed: {(completed.stderr or completed.stdout)[-1000:]}"
        )


def _stop_watcher(repository: Path, live_root: Path, timeout: int) -> None:
    for pid in _authoring_processes(repository, live_root):
        try:
            command = Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="ignore")
        except OSError:
            continue
        if "archive_authoring_live.py" in command:
            os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + timeout
    while any(
        "archive_authoring_live.py"
        in Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="ignore")
        for pid in _authoring_processes(repository, live_root)
        if Path(f"/proc/{pid}/cmdline").exists()
    ):
        if time.monotonic() >= deadline:
            raise MigrationError("archive watcher did not stop")
        time.sleep(0.2)


def _acquire_lock(stack: ExitStack, path: Path) -> None:
    stream = stack.enter_context(path.open("a+", encoding="utf-8"))
    try:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise MigrationError(f"legacy lock is still held: {path}") from exc


def _verify_docker(live_root: Path) -> None:
    listed = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True, check=False)
    if listed.returncode != 0:
        raise MigrationError("Docker inspection unavailable during cutover")
    ids = listed.stdout.split()
    if not ids:
        return
    inspected = subprocess.run(
        ["docker", "inspect", *ids], capture_output=True, text=True, check=False
    )
    if inspected.returncode != 0 or str(live_root) in inspected.stdout:
        raise MigrationError("Docker mount ambiguity remains under authoring-live")


def _initialize_capacity(database: Path) -> None:
    scheduler = scheduler_for(database)
    scheduler.configure(enabled=True, changed_by="cutover", reason="Phase 3 activation")
    scheduler.capacity("controller_slot", "global", "controllers", 6)
    scheduler.capacity("active_claim", "global", "claims", 6)
    scheduler.capacity("active_claim", "agent", "authoring", 6)
    for language in ("python", "node", "go"):
        scheduler.capacity("controller_slot", "language", language, 4)
        scheduler.capacity("active_claim", "language", language, 4)


def execute_cutover(
    *,
    repository: Path,
    live_root: Path,
    manifest_path: Path,
    database: Path,
    journal_path: Path,
    barrier_path: Path,
    cutover_id: str,
    service_unit: str,
    drain_timeout: int,
) -> dict[str, Any]:
    if barrier_path.exists():
        raise MigrationError("external-side-effect barrier already exists")
    runtime_config = live_root / "supervisor/runtime-config.json"
    original = json.loads(runtime_config.read_text(encoding="utf-8"))
    audit = {"pre_drain_inventory_sha256": inventory_digest(live_root), "cutover_id": cutover_id}
    _atomic_json(journal_path, {**audit, "phase": "pre-drain", "legacy_runtime_config": original})
    try:
        disable_legacy_config(runtime_config)
        _wait_for_controllers(repository, live_root, drain_timeout)
        _stop_service(service_unit)
        _stop_watcher(repository, live_root, drain_timeout)
        with ExitStack() as stack:
            _acquire_lock(stack, live_root / "archive.lock")
            _acquire_lock(stack, live_root / "supervisor.lock")
            remaining = _authoring_processes(repository, live_root)
            if remaining:
                raise MigrationError(f"authoring processes remain after stop: {remaining}")
            _verify_docker(live_root)
            manifest = generate_manifest(live_root, cutover_id=cutover_id)
            validate_manifest(manifest, live_root)
            _atomic_json(manifest_path, manifest)
            result = import_manifest(
                manifest,
                live_root,
                db_path=database,
                dry_run=False,
                barrier=lambda: {"barrier": "quiesced", "stopped": False},
            )
            _initialize_capacity(database)
            barrier = {
                "schema_version": "authoring-cutover-barrier/v1",
                "cutover_id": cutover_id,
                "manifest_sha256": manifest["manifest_sha256"],
                "database_sha256": hashlib.sha256(database.read_bytes()).hexdigest(),
                "rollback_allowed": False,
            }
            _atomic_json(barrier_path, barrier)
            _atomic_json(
                journal_path, {**audit, "phase": "activated", "barrier": str(barrier_path)}
            )
            return {
                "manifest": str(manifest_path),
                "database": str(database),
                "import": result,
                "barrier": barrier,
            }
    except Exception:
        if not barrier_path.exists():
            _atomic_json(runtime_config, original)
            for suffix in ("", "-wal", "-shm"):
                Path(str(database) + suffix).unlink(missing_ok=True)
            _atomic_json(
                journal_path, {**audit, "phase": "rolled-back", "legacy_runtime_config": original}
            )
        raise


def rollback_cutover(*, journal_path: Path, barrier_path: Path, runtime_config: Path) -> None:
    if barrier_path.exists():
        raise MigrationError("rollback is forbidden after external-side-effect barrier")
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    original = journal.get("legacy_runtime_config")
    if not isinstance(original, dict):
        raise MigrationError("cutover journal has no rollback configuration")
    _atomic_json(runtime_config, original)
