"""Process-facing adapters for the SQLite authoring scheduler."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .scheduler import ActorFence, LostLeaseError, Scheduler


def process_identity(pid: int | None = None) -> tuple[int, int, str]:
    process_id = pid or os.getpid()
    fields = Path(f"/proc/{process_id}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()
    starttime = int(fields[19])
    boot_id = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="utf-8").strip()
    return process_id, starttime, boot_id


def command_digest(command: list[str]) -> str:
    raw = json.dumps(command, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def executable_digest(path: str) -> str:
    executable = Path(path).resolve()
    try:
        return hashlib.sha256(executable.read_bytes()).hexdigest()
    except OSError:
        return hashlib.sha256(str(executable).encode()).hexdigest()


@dataclass
class SingletonActor:
    scheduler: Scheduler
    scope: str
    controller_id: str
    owner_uuid: str
    fence: ActorFence

    @classmethod
    def acquire(
        cls,
        scheduler: Scheduler,
        scope: str,
        *,
        owner_uuid: str | None = None,
        lease_seconds: int = 7200,
    ) -> SingletonActor:
        owner = owner_uuid or str(uuid.uuid4())
        controller = f"{scope}-{uuid.uuid4()}"
        pid, starttime, boot_id = process_identity()
        scheduler.register_actor(
            controller,
            owner,
            scope,
            pid=pid,
            process_starttime_ticks=starttime,
            boot_id=boot_id,
        )
        try:
            lease_id, generation = scheduler.acquire_singleton(
                scope,
                controller,
                owner,
                lease_seconds=lease_seconds,
                pid=pid,
                process_starttime_ticks=starttime,
                boot_id=boot_id,
            )
        except Exception:
            scheduler.stop_controller(
                controller,
                owner,
                pid=pid,
                process_starttime_ticks=starttime,
                boot_id=boot_id,
            )
            raise
        return cls(
            scheduler,
            scope,
            controller,
            owner,
            ActorFence(scope, lease_id, generation, controller, owner, pid, starttime, boot_id),
        )

    def heartbeat(self, *, lease_seconds: int = 7200) -> None:
        fence = self.fence
        self.scheduler.heartbeat_singleton(
            fence.lease_id,
            fence.scope,
            fence.controller_id,
            fence.owner_uuid,
            fence.generation,
            lease_seconds=lease_seconds,
            pid=fence.pid,
            process_starttime_ticks=fence.process_starttime_ticks,
            boot_id=fence.boot_id,
        )

    def __enter__(self) -> SingletonActor:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.release()

    def release(self) -> None:
        fence = self.fence
        try:
            self.scheduler.release_singleton(
                fence.lease_id,
                fence.scope,
                fence.controller_id,
                fence.owner_uuid,
                fence.generation,
                pid=fence.pid,
                process_starttime_ticks=fence.process_starttime_ticks,
                boot_id=fence.boot_id,
            )
        finally:
            try:
                self.scheduler.stop_controller(
                    fence.controller_id,
                    fence.owner_uuid,
                    pid=fence.pid,
                    process_starttime_ticks=fence.process_starttime_ticks,
                    boot_id=fence.boot_id,
                )
            except LostLeaseError:
                pass


def db_root(database: Path) -> Path:
    return database.expanduser().resolve().parent


def scheduler_for(database: Path) -> Scheduler:
    return Scheduler(database, supplied_root=db_root(database))


def idempotency_key(task: dict[str, Any], kind: str) -> str:
    attempt = int(task[f"{kind}_attempts"]) + 1
    retry = int(task[f"{kind}_retry_count"])
    return f"{kind}:{task['task_id']}:{attempt}:{retry}"
