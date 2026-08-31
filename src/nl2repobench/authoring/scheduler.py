# ruff: noqa: E501
"""Typed, process-safe SQLite primitives for authoring scheduling.

This module is intentionally a library boundary.  External effects belong to
the Phase 2 workers; all methods here are short ``BEGIN IMMEDIATE`` changes.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import sqlite3
import time
import uuid
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import TracebackType
from typing import Any, Literal, cast

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
LANGUAGES = ("python", "node", "go")
# Schema v4 adds ``legacy_archive_evidence``.  No pre-v4 database is deployed, so
# v4 is the only accepted version and there is no in-place upgrade path.
SCHEMA_VERSION = "4"
STATUS_SCHEMA_VERSION = "authoring-scheduler/v4"


class SchedulerError(Exception):
    """Base for errors that are safe to expose through the CLI."""


class ValidationError(SchedulerError):
    pass


class ConflictError(SchedulerError):
    pass


class LostLeaseError(ConflictError):
    pass


class BusyError(SchedulerError):
    pass


class CorruptionError(SchedulerError):
    pass


class _LockedConnection(sqlite3.Connection):
    """Hold the scheduler lock for exactly the lifetime of a DB connection."""

    def __init__(self, *args: Any, lock_fd: int, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._scheduler_lock_fd = lock_fd

    def close(self) -> None:
        try:
            super().close()
        finally:
            os.close(self._scheduler_lock_fd)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        try:
            super().__exit__(exc_type, exc, traceback)
        finally:
            self.close()
        return False


@dataclass(frozen=True)
class Identity:
    digest: str
    language: str
    package: str
    upstream_url: str
    source_kind: str
    revision: str


@dataclass(frozen=True)
class Claim:
    task_id: str
    trial_id: str
    claim_id: str
    lane_id: str
    owner_uuid: str
    controller_id: str
    attempt_no: int
    retry_no: int
    generation: int


@dataclass(frozen=True)
class ActorFence:
    scope: str
    lease_id: str
    generation: int
    controller_id: str
    owner_uuid: str
    pid: int
    process_starttime_ticks: int
    boot_id: str


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


def _future(seconds: int) -> str:
    return (datetime.now(UTC) + timedelta(seconds=seconds)).isoformat(timespec="microseconds")


def _id(value: str, label: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise ValidationError(f"invalid {label}")
    return value


def _json(value: Mapping[str, Any] | list[Any] | None, label: str = "payload") -> str:
    if value is None:
        value = {}
    try:
        return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"invalid {label}") from exc


def _digest(value: str, label: str = "digest") -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value.removeprefix("sha256:")):
        raise ValidationError(f"invalid {label}")
    return value.removeprefix("sha256:")


@contextmanager
def _transaction(db: sqlite3.Connection, *, immediate: bool = True) -> Iterator[sqlite3.Connection]:
    deadline = time.monotonic() + 5.0
    try:
        while True:
            try:
                db.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
                break
            except sqlite3.OperationalError as exc:
                if "busy" not in str(exc).lower() and "locked" not in str(exc).lower():
                    raise
                if time.monotonic() >= deadline:
                    db.rollback()
                    raise BusyError("sqlite write transaction is busy") from exc
                time.sleep(0.02)
        yield db
    except sqlite3.OperationalError as exc:
        if "busy" in str(exc).lower() or "locked" in str(exc).lower():
            db.rollback()
            raise BusyError("sqlite operation is busy") from exc
        raise
    except Exception:
        db.rollback()
        raise
    else:
        while True:
            try:
                db.commit()
                break
            except sqlite3.OperationalError as exc:
                if "busy" not in str(exc).lower() and "locked" not in str(exc).lower():
                    raise
                if time.monotonic() >= deadline:
                    db.rollback()
                    raise BusyError("sqlite commit is busy") from exc
                time.sleep(min(0.02, max(0.001, deadline - time.monotonic())))


class Scheduler:
    """A narrowly typed facade over one local scheduler database."""

    def __init__(self, path: Path | str, *, supplied_root: Path | str | None = None) -> None:
        self.path = Path(path).expanduser()
        if supplied_root is None:
            raise ValidationError("supplied_root is required")
        root = Path(supplied_root).expanduser().resolve()
        if not root.is_absolute() or root.is_symlink():
            raise ValidationError("supplied_root must be an absolute non-symlink path")
        resolved = self.path.resolve()
        if root != resolved and root not in resolved.parents:
            raise ValidationError("database must be under supplied root")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        deadline = time.monotonic() + 5.0
        try:
            lock_path = self.path.parent / f".{self.path.name}.lock"
            lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            while True:
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError as exc:
                    if time.monotonic() >= deadline:
                        os.close(lock_fd)
                        raise BusyError("scheduler lock is busy") from exc
                    time.sleep(0.02)
            rollback_marker = self.path.parent / f".{self.path.name}.rolled-back.json"
            if rollback_marker.exists():
                os.close(lock_fd)
                raise ConflictError("scheduler database was rolled back")
            db = sqlite3.connect(
                self.path,
                timeout=0.0,
                isolation_level=None,
                factory=cast(Any, lambda *a, **kw: _LockedConnection(*a, lock_fd=lock_fd, **kw)),
            )
        except sqlite3.OperationalError as exc:
            if "busy" in str(exc).lower() or "locked" in str(exc).lower():
                raise BusyError("sqlite connection is busy") from exc
            raise
        db.row_factory = sqlite3.Row
        pragmas = (
            "PRAGMA journal_mode=WAL",
            "PRAGMA synchronous=FULL",
            "PRAGMA busy_timeout=0",
            "PRAGMA foreign_keys=ON",
            "PRAGMA temp_store=MEMORY",
            "PRAGMA wal_autocheckpoint=1000",
            "PRAGMA journal_size_limit=67108864",
            "PRAGMA trusted_schema=OFF",
        )
        try:
            for pragma in pragmas:
                while True:
                    try:
                        db.execute(pragma)
                        break
                    except sqlite3.OperationalError as exc:
                        if "busy" not in str(exc).lower() and "locked" not in str(exc).lower():
                            raise
                        if time.monotonic() >= deadline:
                            raise BusyError("sqlite connection setup is busy") from exc
                        time.sleep(min(0.02, max(0.001, deadline - time.monotonic())))
        except Exception:
            db.close()
            raise
        return cast(sqlite3.Connection, db)

    def connect(self) -> sqlite3.Connection:
        return self._connect()

    def runtime_config(self) -> dict[str, Any]:
        """Return the current operator configuration from the DB authority."""
        with self._db() as db:
            row = db.execute("SELECT * FROM current_runtime_config").fetchone()
            if row is None:
                raise ConflictError("scheduler runtime configuration is missing")
            return dict(row)

    def resource_policy(self) -> dict[str, Any]:
        with self._db() as db:
            row = db.execute("SELECT * FROM current_resource_policy").fetchone()
            if row is None:
                raise ConflictError("scheduler resource policy is missing")
            return dict(row)

    def configure_resource_policy(
        self,
        *,
        repository_min_free_bytes: int,
        docker_min_free_bytes: int,
        watcher_min_free_bytes: int,
        changed_by: str = "operator",
        reason: str = "resource policy configuration",
    ) -> int:
        values = (repository_min_free_bytes, docker_min_free_bytes, watcher_min_free_bytes)
        if any(not isinstance(value, int) or value <= 0 for value in values):
            raise ValidationError("resource policy limits must be positive integers")
        _id(changed_by, "changed_by")
        if not reason or len(reason) > 500:
            raise ValidationError("reason is required and bounded")
        with self._db() as db, _transaction(db):
            cur = db.execute(
                "INSERT INTO resource_policy(repository_min_free_bytes,docker_min_free_bytes,"
                "watcher_min_free_bytes,changed_by,changed_at,reason) VALUES(?,?,?,?,?,?)",
                (*values, changed_by, _now(), reason),
            )
            if cur.lastrowid is None:
                raise CorruptionError("resource policy insert did not return an id")
            return int(cur.lastrowid)

    def task_context(self, task_id: str) -> dict[str, Any]:
        """Return the immutable candidate and mutable task context for one worker."""
        _id(task_id, "task_id")
        with self._db() as db:
            row = db.execute(
                "SELECT t.*,l.batch_id,l.language,i.package,i.upstream_url,i.revision,"
                "c.selection_json FROM tasks t JOIN lanes l ON l.lane_id=t.lane_id "
                "JOIN candidates c ON c.candidate_id=t.candidate_id AND c.lane_id=t.lane_id "
                "JOIN candidate_identities i ON i.identity_digest=c.identity_digest "
                "WHERE t.task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise ConflictError("unknown task")
            result = dict(row)
            result["selection"] = json.loads(str(result.pop("selection_json")))
            return result

    def operation_candidates(self, kind: str, *, limit: int = 8) -> list[dict[str, Any]]:
        """Return DB-owned work awaiting a fenced external operation."""
        states = {
            "integration": ("handoff_ready", "integration_retry"),
            "archive": ("integrating", "archive_retry"),
            "cleanup": ("archiving", "cleanup_retry"),
        }
        if kind not in states or not 1 <= limit <= 64:
            raise ValidationError("invalid operation candidate request")
        placeholders = ",".join("?" for _ in states[kind])
        with self._db() as db:
            rows = db.execute(
                f"SELECT t.*,l.batch_id,l.language,i.package FROM tasks t "
                "JOIN lanes l ON l.lane_id=t.lane_id "
                "JOIN candidates c ON c.candidate_id=t.candidate_id AND c.lane_id=t.lane_id "
                "JOIN candidate_identities i ON i.identity_digest=c.identity_digest "
                f"WHERE t.state IN ({placeholders}) ORDER BY t.updated_at,t.task_id LIMIT ?",
                (*states[kind], limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def controller_active(
        self,
        controller_id: str,
        owner_uuid: str,
        *,
        pid: int,
        process_starttime_ticks: int,
        boot_id: str,
    ) -> bool:
        with self._db() as db:
            row = db.execute(
                "SELECT 1 FROM controllers WHERE controller_id=? AND owner_uuid=? "
                "AND pid=? AND process_starttime_ticks=? AND boot_id=? "
                "AND state='running' AND desired=1",
                (controller_id, owner_uuid, pid, process_starttime_ticks, boot_id),
            ).fetchone()
            return row is not None

    def next_available_slot(self, lane_id: str) -> int:
        """Return the first lane slot not occupied by a controller or reservation."""
        _id(lane_id, "lane_id")
        config = self.runtime_config()
        with self._db() as db:
            for slot in range(int(config["controller_concurrency"])):
                occupied = db.execute(
                    "SELECT 1 FROM controllers WHERE lane_id=? AND slot=? "
                    "AND state IN ('running','draining') UNION ALL "
                    "SELECT 1 FROM controller_slot_reservations WHERE lane_id=? AND slot=? "
                    "AND state='reserved' LIMIT 1",
                    (lane_id, slot, lane_id, slot),
                ).fetchone()
                if occupied is None:
                    return slot
        raise ConflictError("lane controller slots are exhausted")

    def record_handoff(
        self,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        generation: int,
        *,
        worktree_path: str,
        worktree_git_head: str,
        handoff_path: str,
        handoff_sha256: str,
        pid: int,
        process_starttime_ticks: int,
        boot_id: str,
    ) -> None:
        """Bind a successful worker handoff to its still-live claim fence."""
        _digest(handoff_sha256, "handoff_sha256")
        if not worktree_path or not handoff_path or not HEX40_RE.fullmatch(worktree_git_head):
            raise ValidationError("invalid handoff metadata")
        with self._db() as db, _transaction(db):
            row = self._fenced_claim(
                db,
                claim_id,
                owner_uuid,
                controller_id,
                generation,
                pid,
                process_starttime_ticks,
                boot_id,
                _now(),
            )
            db.execute(
                "UPDATE tasks SET worktree_path=?,worktree_git_head=?,handoff_path=?,"
                "handoff_sha256=?,updated_at=? WHERE task_id=? AND state='authoring'",
                (
                    worktree_path,
                    worktree_git_head,
                    handoff_path,
                    handoff_sha256,
                    _now(),
                    row["task_id"],
                ),
            )

    def init(self) -> None:
        schema = Path(__file__).with_name("scheduler_schema.sql").read_text(encoding="utf-8")
        if self.path.exists() and self.path.stat().st_size:
            try:
                with self.connect() as existing:
                    row = existing.execute(
                        "SELECT value FROM schema_meta WHERE key='schema_version'"
                    ).fetchone()
                    if row is None or row[0] != SCHEMA_VERSION:
                        raise ValidationError("incompatible scheduler schema version")
                    required = {
                        "lanes",
                        "tasks",
                        "controllers",
                        "events",
                        "runtime_config",
                        "resource_policy",
                        "cutover_barrier",
                        "legacy_archive_evidence",
                    }
                    actual = {
                        str(r[0])
                        for r in existing.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                    }
                    if not required <= actual:
                        raise ValidationError("incomplete scheduler schema")
                    return
            except sqlite3.DatabaseError as exc:
                raise ValidationError("incompatible scheduler database") from exc
        with self.connect() as db:
            db.executescript(schema)
            with _transaction(db):
                now = _now()
                db.execute("INSERT OR IGNORE INTO fairness_state VALUES (1,0,0,?)", (now,))
                db.execute(
                    "INSERT OR IGNORE INTO schema_meta VALUES ('schema_version',?)",
                    (SCHEMA_VERSION,),
                )
                db.execute(
                    "INSERT OR IGNORE INTO resource_policy(policy_version,repository_min_free_bytes,"
                    "docker_min_free_bytes,watcher_min_free_bytes,changed_by,changed_at,reason) "
                    "VALUES(1,?,?,?,?,?,?)",
                    (12 * 1024**3, 20 * 1024**3, 2 * 1024**3, "schema", now, "Phase 3 defaults"),
                )

    def _db(self) -> sqlite3.Connection:
        return self.connect()

    @staticmethod
    def _fenced_claim(
        db: sqlite3.Connection,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        generation: int,
        pid: int,
        starttime: int,
        boot_id: str,
        moment: str,
        *,
        by_task: bool = False,
    ) -> sqlite3.Row:
        selector = "cl.task_id=?" if by_task else "cl.claim_id=?"
        row = db.execute(
            f"SELECT cl.*,c.pid,c.process_starttime_ticks,c.boot_id,c.state controller_state "
            "FROM claims cl JOIN controllers c ON c.controller_id=cl.controller_id "
            f"AND c.owner_uuid=cl.owner_uuid WHERE {selector} AND cl.owner_uuid=? "
            "AND cl.controller_id=? AND cl.generation=? AND cl.active=1 "
            "AND cl.lease_expires_at>? AND c.state='running' AND c.desired=1 "
            "AND c.pid=? AND c.process_starttime_ticks=? AND c.boot_id=?",
            (claim_id, owner_uuid, controller_id, generation, moment, pid, starttime, boot_id),
        ).fetchone()
        if row is None:
            raise LostLeaseError("claim or controller identity fence failed")
        return cast(sqlite3.Row, row)

    @staticmethod
    def _close_claim(db: sqlite3.Connection, row: sqlite3.Row, now: str, reason: str) -> None:
        cur = db.execute(
            "UPDATE claims SET active=0,released_at=?,release_reason=?,updated_at=? "
            "WHERE claim_id=? AND generation=? AND active=1",
            (now, reason, now, row["claim_id"], row["generation"]),
        )
        if cur.rowcount != 1:
            raise LostLeaseError("claim was concurrently closed")
        db.execute(
            "UPDATE trials SET state='cancelled',updated_at=? WHERE trial_id=? AND state='created'",
            (now, row["trial_id"]),
        )
        db.execute(
            "UPDATE trials SET state='failed',finished_at=?,updated_at=? WHERE trial_id=? AND state='running'",
            (now, now, row["trial_id"]),
        )
        Scheduler._decrement(db, row["controller_id"], row["task_id"], now)

    @staticmethod
    def _controller_capacity_delta(
        db: sqlite3.Connection, controller_id: str, language: str, delta: int, now: str
    ) -> None:
        for kind, key in (("global", "controllers"), ("language", language)):
            row = db.execute(
                "SELECT used_count,remaining_count FROM capacity_rows WHERE capacity_unit='controller_slot' "
                "AND capacity_kind=? AND capacity_key=?",
                (kind, key),
            ).fetchone()
            if row is None or row["used_count"] + delta < 0 or row["remaining_count"] - delta < 0:
                raise CorruptionError("controller capacity invariant failed")
            db.execute(
                "UPDATE capacity_rows SET used_count=used_count+?,remaining_count=remaining_count-?,updated_at=? "
                "WHERE capacity_unit='controller_slot' AND capacity_kind=? AND capacity_key=?",
                (delta, delta, now, kind, key),
            )

    @staticmethod
    def _fenced_actor(
        db: sqlite3.Connection, actor: ActorFence, operation_kind: str, moment: str
    ) -> sqlite3.Row:
        expected_scope = "integration" if operation_kind == "integration" else "archive"
        if actor.scope != expected_scope:
            raise LostLeaseError("actor scope does not own operation")
        row = db.execute(
            "SELECT l.* FROM scheduler_leases l JOIN controllers c ON c.controller_id=l.controller_id "
            "AND c.owner_uuid=l.owner_uuid WHERE l.lease_id=? AND l.scope=? AND l.generation=? "
            "AND l.controller_id=? AND l.owner_uuid=? AND l.active=1 AND l.lease_expires_at>? "
            "AND c.state='running' AND c.desired=1 AND c.pid=? AND c.process_starttime_ticks=? AND c.boot_id=?",
            (
                actor.lease_id,
                actor.scope,
                actor.generation,
                actor.controller_id,
                actor.owner_uuid,
                moment,
                actor.pid,
                actor.process_starttime_ticks,
                actor.boot_id,
            ),
        ).fetchone()
        if row is None:
            raise LostLeaseError("operation actor fence failed")
        return cast(sqlite3.Row, row)

    @staticmethod
    def _fenced_operator(db: sqlite3.Connection, actor: ActorFence, moment: str) -> None:
        if actor.scope != "supervisor":
            raise LostLeaseError("operator transition requires supervisor actor")
        row = db.execute(
            "SELECT 1 FROM scheduler_leases l JOIN controllers c ON c.controller_id=l.controller_id "
            "AND c.owner_uuid=l.owner_uuid WHERE l.lease_id=? AND l.scope='supervisor' "
            "AND l.generation=? AND l.controller_id=? AND l.owner_uuid=? AND l.active=1 "
            "AND l.lease_expires_at>? AND c.state='running' AND c.desired=1 AND c.pid=? "
            "AND c.process_starttime_ticks=? AND c.boot_id=?",
            (
                actor.lease_id,
                actor.generation,
                actor.controller_id,
                actor.owner_uuid,
                moment,
                actor.pid,
                actor.process_starttime_ticks,
                actor.boot_id,
            ),
        ).fetchone()
        if row is None:
            raise LostLeaseError("operator actor fence failed")

    def configure(
        self,
        *,
        enabled: bool,
        lease_seconds: int = 7200,
        heartbeat_interval_seconds: int = 600,
        max_total_controllers: int = 6,
        controller_concurrency: int = 4,
        max_integrations: int = 3,
        agent_limit: int | None = 6,
        changed_by: str = "operator",
        reason: str = "configuration",
    ) -> int:
        if not isinstance(lease_seconds, int) or not 5 <= lease_seconds <= 86400:
            raise ValidationError("lease_seconds out of bounds")
        if (
            not isinstance(heartbeat_interval_seconds, int)
            or not 5 <= heartbeat_interval_seconds < lease_seconds
        ):
            raise ValidationError("heartbeat interval must be 5..lease-1")
        _id(changed_by, "changed_by")
        if not reason or len(reason) > 500:
            raise ValidationError("reason is required and bounded")
        if not 0 <= max_total_controllers <= 6 or not 0 <= controller_concurrency <= 4:
            raise ValidationError("controller limits out of bounds")
        if not 0 <= max_integrations <= 3 or (
            agent_limit is not None and not 0 <= agent_limit <= 6
        ):
            raise ValidationError("operation limits out of bounds")
        with self._db() as db, _transaction(db):
            barrier = db.execute(
                "SELECT state FROM cutover_barrier WHERE barrier_id=1"
            ).fetchone()
            current = db.execute("SELECT * FROM current_runtime_config").fetchone()
            if (
                enabled
                and barrier is not None
                and barrier["state"] == "prepared"
                and current is not None
                and not bool(current["enabled"])
                and (
                    max_total_controllers,
                    controller_concurrency,
                    max_integrations,
                    agent_limit,
                )
                != (1, 1, 0, 1)
            ):
                raise ConflictError("prepared cutover requires bounded first enable")
            bounded_first_enable = (
                enabled
                and barrier is not None
                and barrier["state"] == "prepared"
                and current is not None
                and not bool(current["enabled"])
                and (
                    max_total_controllers,
                    controller_concurrency,
                    max_integrations,
                    agent_limit,
                )
                == (1, 1, 0, 1)
            )
            now = _now()
            if bounded_first_enable:
                self._seal_cutover_barrier(db, "first-enable", None, now)
            cur = db.execute(
                "INSERT INTO runtime_config(enabled,max_total_controllers,controller_concurrency,max_integrations,agent_limit,lease_seconds,heartbeat_interval_seconds,changed_by,changed_at,reason) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    int(enabled),
                    max_total_controllers,
                    controller_concurrency,
                    max_integrations,
                    agent_limit,
                    lease_seconds,
                    heartbeat_interval_seconds,
                    changed_by,
                    now,
                    reason,
                ),
            )
            if cur.lastrowid is None:
                raise CorruptionError("configuration insert did not return an id")
            version = int(cur.lastrowid)
            effective_agent_limit = max_total_controllers if agent_limit is None else agent_limit
            limits = [
                ("controller_slot", "global", "controllers", max_total_controllers),
                ("active_claim", "global", "claims", effective_agent_limit),
                ("active_claim", "agent", "authoring", effective_agent_limit),
            ]
            limits.extend(
                (unit, "language", language, controller_concurrency)
                for language in LANGUAGES
                for unit in ("controller_slot", "active_claim")
            )
            for unit, kind, key, limit in limits:
                current = db.execute(
                    "SELECT used_count FROM capacity_rows WHERE capacity_unit=? "
                    "AND capacity_kind=? AND capacity_key=?",
                    (unit, kind, key),
                ).fetchone()
                used = int(current[0]) if current is not None else 0
                if used > limit:
                    raise ConflictError("runtime limit is below live capacity usage")
                db.execute(
                    "INSERT INTO capacity_rows VALUES(?,?,?,?,?,?,?,?) "
                    "ON CONFLICT(capacity_unit,capacity_kind,capacity_key) DO UPDATE SET "
                    "limit_count=excluded.limit_count,remaining_count=excluded.limit_count-"
                    "capacity_rows.used_count,config_version=excluded.config_version,"
                    "updated_at=excluded.updated_at",
                    (unit, kind, key, limit, used, limit - used, version, now),
                )
            return version

    def prepare_cutover_barrier(self, cutover_id: str, manifest_sha256: str) -> None:
        _id(cutover_id, "cutover_id")
        digest = _digest(manifest_sha256, "manifest_sha256")
        with self._db() as db, _transaction(db):
            if db.execute("SELECT 1 FROM cutover_barrier").fetchone() is not None:
                raise ConflictError("cutover barrier already exists")
            db.execute(
                "INSERT INTO cutover_barrier VALUES(1,?,?,'prepared',1,?,NULL,NULL,NULL)",
                (cutover_id, digest, _now()),
            )

    def first_enable(self, *, changed_by: str = "operator") -> int:
        """Perform the bounded one-controller activation after cutover preparation."""
        with self._db() as db:
            config = db.execute("SELECT * FROM current_runtime_config").fetchone()
            barrier = db.execute("SELECT * FROM cutover_barrier WHERE barrier_id=1").fetchone()
            if (
                config is None
                or bool(config["enabled"])
                or any(
                    int(config[key]) != 0
                    for key in ("max_total_controllers", "controller_concurrency", "max_integrations")
                )
                or config["agent_limit"] != 0
                or barrier is None
                or barrier["state"] != "prepared"
            ):
                raise ConflictError("database is not ready for first enable")
            lease = int(config["lease_seconds"])
            heartbeat = int(config["heartbeat_interval_seconds"])
        return self.configure(
            enabled=True,
            lease_seconds=lease,
            heartbeat_interval_seconds=heartbeat,
            max_total_controllers=1,
            controller_concurrency=1,
            max_integrations=0,
            agent_limit=1,
            changed_by=changed_by,
            reason="bounded first enable",
        )

    @staticmethod
    def _seal_cutover_barrier(
        db: sqlite3.Connection, effect_kind: str, task_id: str | None, moment: str
    ) -> None:
        barrier = db.execute("SELECT * FROM cutover_barrier WHERE barrier_id=1").fetchone()
        if barrier is None or barrier["state"] == "sealed":
            return
        cur = db.execute(
            "UPDATE cutover_barrier SET state='sealed',rollback_allowed=0,sealed_at=?,"
            "first_effect_kind=?,first_effect_task_id=? WHERE barrier_id=1 AND state='prepared'",
            (moment, effect_kind, task_id),
        )
        if cur.rowcount != 1:
            raise ConflictError("cutover barrier seal raced")

    def add_lane(
        self,
        lane_id: str,
        batch_id: str,
        language: str,
        kind: str = "base",
        *,
        status: str = "active",
        queue_path: str = "queue.json",
        plan_path: str = "plan.json",
        state_path: str | None = None,
        queue_sha256: str = "0" * 64,
        plan_sha256: str = "0" * 64,
        source_reports: list[str] | None = None,
        fairness_rank: int = 0,
    ) -> None:
        _id(lane_id, "lane_id")
        _id(batch_id, "batch_id")
        if (
            language not in LANGUAGES
            or kind not in {"base", "generated"}
            or status not in {"planned", "active", "draining", "closed", "blocked"}
        ):
            raise ValidationError("invalid lane fields")
        for value, label in ((queue_path, "queue_path"), (plan_path, "plan_path")):
            if not value or Path(value).is_absolute() or ".." in Path(value).parts:
                raise ValidationError(f"invalid {label}")
        _digest(queue_sha256, "queue_sha256")
        _digest(plan_sha256, "plan_sha256")
        if fairness_rank < 0:
            raise ValidationError("fairness_rank must be non-negative")
        with self._db() as db, _transaction(db):
            db.execute(
                "INSERT INTO lanes VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    lane_id,
                    batch_id,
                    language,
                    kind,
                    status,
                    queue_path,
                    queue_sha256,
                    plan_path,
                    plan_sha256,
                    state_path,
                    None,
                    _json(source_reports or []),
                    fairness_rank,
                    0,
                    _now(),
                    _now(),
                ),
            )

    def add_identity(self, identity: Identity, canonical: Mapping[str, Any] | None = None) -> None:
        _digest(identity.digest, "identity_digest")
        if (
            identity.language not in LANGUAGES
            or not identity.package
            or not identity.upstream_url
            or len(identity.revision) != 40
        ):
            raise ValidationError("invalid identity")
        with self._db() as db, _transaction(db):
            db.execute(
                "INSERT INTO candidate_identities VALUES(?,?,?,?,?,?,?,?)",
                (
                    identity.digest.removeprefix("sha256:"),
                    identity.language,
                    identity.package,
                    identity.upstream_url,
                    identity.source_kind,
                    identity.revision,
                    _json(canonical or {"package": identity.package}),
                    _now(),
                ),
            )

    def add_candidate(
        self,
        candidate_id: str,
        lane_id: str,
        identity_digest: str,
        ordinal: int = 0,
        selection: Mapping[str, Any] | None = None,
    ) -> None:
        _id(candidate_id, "candidate_id")
        _id(lane_id, "lane_id")
        _digest(identity_digest, "identity_digest")
        if ordinal < 0:
            raise ValidationError("ordinal must be non-negative")
        with self._db() as db, _transaction(db):
            now = _now()
            db.execute(
                "INSERT INTO candidates VALUES(?,?,?,?,?,?,?,?)",
                (
                    candidate_id,
                    lane_id,
                    identity_digest.removeprefix("sha256:"),
                    ordinal,
                    "candidate",
                    _json(selection),
                    now,
                    now,
                ),
            )

    def add_task(
        self,
        task_id: str,
        candidate_id: str,
        lane_id: str,
        task_release: str,
        *,
        attempt_limit: int = 3,
        retry_limit: int = 3,
        release_limit: int = 3,
        input_ordinal: int = 0,
    ) -> None:
        for value, label in (
            (task_id, "task_id"),
            (candidate_id, "candidate_id"),
            (lane_id, "lane_id"),
            (task_release, "task_release"),
        ):
            _id(value, label)
        if (
            not 1 <= attempt_limit <= 100
            or not 0 <= retry_limit <= 100
            or not 0 <= release_limit <= 100
        ):
            raise ValidationError("task limits out of bounds")
        with self._db() as db, _transaction(db):
            now = _now()
            db.execute(
                "INSERT INTO tasks(task_id,candidate_id,lane_id,task_release,state,attempt_limit,retry_limit,release_limit,input_ordinal,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    task_id,
                    candidate_id,
                    lane_id,
                    task_release,
                    "pending",
                    attempt_limit,
                    retry_limit,
                    release_limit,
                    input_ordinal,
                    now,
                    now,
                ),
            )

    def capacity(self, unit: str, kind: str, key: str, limit: int, *, used: int = 0) -> None:
        if (
            unit not in {"controller_slot", "active_claim"}
            or kind not in {"global", "controller", "language", "agent"}
            or limit < 0
            or not 0 <= used <= limit
        ):
            raise ValidationError("invalid capacity row")
        with self._db() as db, _transaction(db):
            current = db.execute(
                "SELECT used_count FROM capacity_rows WHERE capacity_unit=? AND capacity_kind=? AND capacity_key=?",
                (unit, kind, key),
            ).fetchone()
            actual_used = int(current[0]) if current is not None else used
            if actual_used > limit:
                raise ConflictError("capacity limit is below live usage")
            db.execute(
                "INSERT INTO capacity_rows VALUES(?,?,?,?,?,?,?,?) "
                "ON CONFLICT(capacity_unit,capacity_kind,capacity_key) DO UPDATE SET "
                "limit_count=excluded.limit_count,remaining_count=excluded.limit_count-capacity_rows.used_count,updated_at=excluded.updated_at",
                (unit, kind, key, limit, actual_used, limit - actual_used, None, _now()),
            )

    def register_controller(
        self,
        controller_id: str,
        owner_uuid: str,
        lane_id: str,
        language: str,
        slot: int,
        *,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
        executable_digest: str = "0" * 64,
        argv_digest: str = "0" * 64,
        reservation_token: str | None = None,
    ) -> None:
        _id(controller_id, "controller_id")
        _id(owner_uuid, "owner_uuid")
        _id(lane_id, "lane_id")
        if language not in LANGUAGES or slot < 0 or pid <= 0 or process_starttime_ticks < 0:
            raise ValidationError("invalid controller identity")
        _digest(executable_digest)
        _digest(argv_digest)
        if reservation_token is None:
            raise ConflictError("controller registration requires a reservation")
        with self._db() as db, _transaction(db):
            now = _now()
            reservation = db.execute(
                "SELECT 1 FROM controller_slot_reservations WHERE reservation_token=? "
                "AND owner_uuid=? AND lane_id=? AND language=? AND slot=? "
                "AND state='reserved' AND expires_at>?",
                (reservation_token, owner_uuid, lane_id, language, slot, now),
            ).fetchone()
            if reservation is None:
                raise ConflictError("controller reservation is unavailable")
            cfg = db.execute("SELECT enabled FROM current_runtime_config").fetchone()
            if cfg is None or not cfg["enabled"]:
                raise ConflictError("scheduler is disabled")
            db.execute(
                "INSERT INTO controllers VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    controller_id,
                    owner_uuid,
                    "authoring_controller",
                    lane_id,
                    language,
                    slot,
                    pid,
                    process_starttime_ticks,
                    boot_id,
                    executable_digest,
                    argv_digest,
                    "running",
                    1,
                    now,
                    None,
                    now,
                    now,
                ),
            )
            db.execute(
                "UPDATE controller_slot_reservations SET state='activated',controller_id=?,updated_at=? "
                "WHERE reservation_token=? AND state='reserved'",
                (controller_id, now, reservation_token),
            )

    def stop_controller(
        self,
        controller_id: str,
        owner_uuid: str,
        *,
        pid: int,
        process_starttime_ticks: int,
        boot_id: str,
        state: str = "stopped",
    ) -> None:
        if state not in {"stopped", "lost", "reconciled"}:
            raise ValidationError("invalid controller stop state")
        with self._db() as db, _transaction(db):
            row = db.execute(
                "SELECT * FROM controllers WHERE controller_id=? AND owner_uuid=? AND pid=? "
                "AND process_starttime_ticks=? AND boot_id=? AND state IN ('running','draining')",
                (controller_id, owner_uuid, pid, process_starttime_ticks, boot_id),
            ).fetchone()
            if row is None:
                raise LostLeaseError("controller identity fence failed")
            active_claims = db.execute(
                "SELECT 1 FROM claims WHERE controller_id=? AND owner_uuid=? AND active=1 LIMIT 1",
                (controller_id, owner_uuid),
            ).fetchone()
            if active_claims is not None:
                raise ConflictError("controller has active claims")
            now = _now()
            db.execute(
                "UPDATE controllers SET state=?,desired=0,stopped_at=?,updated_at=? WHERE controller_id=? AND state IN ('running','draining')",
                (state, now, now, controller_id),
            )
            if row["role"] == "authoring_controller":
                db.execute(
                    "UPDATE controller_slot_reservations SET state='released',updated_at=? WHERE controller_id=? AND state='activated'",
                    (now, controller_id),
                )
                self._controller_capacity_delta(db, controller_id, row["language"], -1, now)

    def register_actor(
        self,
        controller_id: str,
        owner_uuid: str,
        role: str,
        *,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> None:
        """Register an observed non-authoring actor for a singleton lease."""
        _id(controller_id, "controller_id")
        _id(owner_uuid, "owner_uuid")
        if role not in {"supervisor", "watcher", "integration", "archive"} or pid <= 0:
            raise ValidationError("invalid actor")
        now = _now()
        with self._db() as db, _transaction(db):
            db.execute(
                "INSERT INTO controllers VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    controller_id,
                    owner_uuid,
                    role,
                    None,
                    None,
                    None,
                    pid,
                    process_starttime_ticks,
                    boot_id,
                    "0" * 64,
                    "0" * 64,
                    "running",
                    1,
                    now,
                    None,
                    now,
                    now,
                ),
            )

    def reserve_controller(
        self, lane_id: str, owner_uuid: str, slot: int, *, ttl_seconds: int = 60
    ) -> str:
        """Reserve a spawn slot; this is intentionally distinct from a controller row."""
        _id(lane_id, "lane_id")
        _id(owner_uuid, "owner_uuid")
        if slot < 0 or not 5 <= ttl_seconds <= 86400:
            raise ValidationError("invalid slot reservation")
        with self._db() as db, _transaction(db):
            lane = db.execute(
                "SELECT language,status FROM lanes WHERE lane_id=?", (lane_id,)
            ).fetchone()
            if lane is None or lane["status"] != "active":
                raise ConflictError("lane is not active")
            cfg = db.execute("SELECT * FROM current_runtime_config").fetchone()
            if cfg is None or not cfg["enabled"]:
                raise ConflictError("scheduler is disabled")
            controller_count = db.execute(
                "SELECT (SELECT count(*) FROM controllers WHERE role='authoring_controller' "
                "AND state IN ('running','draining')) + (SELECT count(*) FROM "
                "controller_slot_reservations WHERE state='reserved')"
            ).fetchone()[0]
            language_count = db.execute(
                "SELECT (SELECT count(*) FROM controllers WHERE role='authoring_controller' "
                "AND language=? AND state IN ('running','draining')) + (SELECT count(*) "
                "FROM controller_slot_reservations WHERE language=? AND state='reserved')",
                (lane["language"], lane["language"]),
            ).fetchone()[0]
            if (
                controller_count >= cfg["max_total_controllers"]
                or language_count >= cfg["controller_concurrency"]
            ):
                raise ConflictError("controller configuration capacity exhausted")
            occupied = db.execute(
                "SELECT 1 FROM controllers WHERE lane_id=? AND slot=? "
                "AND role='authoring_controller' AND state IN ('running','draining')",
                (lane_id, slot),
            ).fetchone()
            if occupied is not None:
                raise ConflictError("controller slot is occupied")
            capacities = []
            for kind, key in (("global", "controllers"), ("language", lane["language"])):
                row = db.execute(
                    "SELECT * FROM capacity_rows WHERE capacity_unit='controller_slot' AND capacity_kind=? AND capacity_key=?",
                    (kind, key),
                ).fetchone()
                if row is None:
                    raise CorruptionError("missing controller_slot capacity row")
                capacities.append(row)
            if any(row["remaining_count"] < 1 for row in capacities):
                raise ConflictError("controller slot capacity exhausted")
            now, token = _now(), str(uuid.uuid4())
            db.execute(
                "INSERT INTO controller_slot_reservations VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    token,
                    lane_id,
                    lane["language"],
                    slot,
                    owner_uuid,
                    "reserved",
                    now,
                    _future(ttl_seconds),
                    None,
                    now,
                    now,
                ),
            )
            for row in capacities:
                db.execute(
                    "UPDATE capacity_rows SET used_count=used_count+1,remaining_count=remaining_count-1,updated_at=? WHERE capacity_unit=? AND capacity_kind=? AND capacity_key=? AND remaining_count>0",
                    (now, row["capacity_unit"], row["capacity_kind"], row["capacity_key"]),
                )
            db.execute(
                "INSERT INTO events(event_type,occurred_at,actor_type,actor_id,lane_id,payload_json) VALUES('controller_slot_reserved',?,?,?,?,?)",
                (now, "supervisor", owner_uuid, lane_id, "{}"),
            )
            return token

    def activate_controller(
        self,
        token: str,
        controller_id: str,
        owner_uuid: str,
        *,
        pid: int,
        process_starttime_ticks: int,
        boot_id: str,
        executable_digest: str,
        argv_digest: str,
    ) -> None:
        _id(controller_id, "controller_id")
        _id(owner_uuid, "owner_uuid")
        _digest(executable_digest)
        _digest(argv_digest)
        if pid <= 0 or process_starttime_ticks < 0:
            raise ValidationError("invalid process identity")
        with self._db() as db, _transaction(db):
            now = _now()
            row = db.execute(
                "SELECT * FROM controller_slot_reservations WHERE reservation_token=? "
                "AND owner_uuid=? AND state='reserved' AND expires_at>?",
                (token, owner_uuid, now),
            ).fetchone()
            if row is None:
                raise ConflictError("reservation is unavailable")
            cfg = db.execute("SELECT enabled FROM current_runtime_config").fetchone()
            if cfg is None or not cfg["enabled"]:
                raise ConflictError("scheduler is disabled")
            db.execute(
                "INSERT INTO controllers VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    controller_id,
                    row["owner_uuid"],
                    "authoring_controller",
                    row["lane_id"],
                    row["language"],
                    row["slot"],
                    pid,
                    process_starttime_ticks,
                    boot_id,
                    executable_digest,
                    argv_digest,
                    "running",
                    1,
                    now,
                    None,
                    now,
                    now,
                ),
            )
            db.execute(
                "UPDATE controller_slot_reservations SET state='activated',controller_id=?,updated_at=? WHERE reservation_token=? AND state='reserved'",
                (controller_id, now, token),
            )
            db.execute(
                "INSERT INTO events(event_type,occurred_at,actor_type,actor_id,lane_id,payload_json) VALUES('controller_activated',?,?,?,?,?)",
                (now, "supervisor", row["owner_uuid"], row["lane_id"], "{}"),
            )

    def reconcile_reservations(self, *, now: str | None = None) -> int:
        moment = now or _now()
        with self._db() as db, _transaction(db):
            rows = db.execute(
                "SELECT * FROM controller_slot_reservations WHERE state='reserved' AND expires_at<=?",
                (moment,),
            ).fetchall()
            changed = 0
            for row in rows:
                cur = db.execute(
                    "UPDATE controller_slot_reservations SET state='expired',updated_at=? WHERE reservation_id=? AND state='reserved'",
                    (moment, row["reservation_id"]),
                )
                if cur.rowcount != 1:
                    continue
                changed += 1
                for kind, key in (("global", "controllers"), ("language", row["language"])):
                    db.execute(
                        "UPDATE capacity_rows SET used_count=used_count-1,remaining_count=remaining_count+1,updated_at=? WHERE capacity_unit='controller_slot' AND capacity_kind=? AND capacity_key=? AND used_count>0",
                        (moment, kind, key),
                    )
            return changed

    def release_controller_reservation(
        self, token: str, owner_uuid: str, *, reason: str = "spawn failed"
    ) -> None:
        _id(owner_uuid, "owner_uuid")
        if not reason:
            raise ValidationError("reservation release reason is required")
        with self._db() as db, _transaction(db):
            now = _now()
            row = db.execute(
                "SELECT * FROM controller_slot_reservations WHERE reservation_token=? "
                "AND owner_uuid=? AND state='reserved'",
                (token, owner_uuid),
            ).fetchone()
            if row is None:
                raise ConflictError("reservation is not releasable")
            cur = db.execute(
                "UPDATE controller_slot_reservations SET state='released',updated_at=? "
                "WHERE reservation_id=? AND owner_uuid=? AND state='reserved'",
                (now, row["reservation_id"], owner_uuid),
            )
            if cur.rowcount != 1:
                raise ConflictError("reservation was concurrently released")
            for kind, key in (("global", "controllers"), ("language", row["language"])):
                cur = db.execute(
                    "UPDATE capacity_rows SET used_count=used_count-1,remaining_count=remaining_count+1,updated_at=? "
                    "WHERE capacity_unit='controller_slot' AND capacity_kind=? AND capacity_key=? AND used_count>0",
                    (now, kind, key),
                )
                if cur.rowcount != 1:
                    raise CorruptionError("controller capacity invariant failed")

    def acquire_singleton(
        self,
        scope: str,
        controller_id: str,
        owner_uuid: str,
        *,
        lease_seconds: int = 7200,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> tuple[str, int]:
        if (
            scope not in {"supervisor", "watcher", "integration", "archive"}
            or not 5 <= lease_seconds <= 86400
        ):
            raise ValidationError("invalid singleton lease")
        with self._db() as db, _transaction(db):
            now = _now()
            actor = db.execute(
                "SELECT 1 FROM controllers WHERE controller_id=? AND owner_uuid=? AND role=? "
                "AND state='running' AND desired=1 AND pid=? AND process_starttime_ticks=? AND boot_id=?",
                (controller_id, owner_uuid, scope, pid, process_starttime_ticks, boot_id),
            ).fetchone()
            if actor is None:
                raise LostLeaseError("actor identity fence failed")
            current = db.execute(
                "SELECT * FROM scheduler_leases WHERE scope=? AND active=1", (scope,)
            ).fetchone()
            if current is not None and current["lease_expires_at"] > now:
                raise ConflictError("singleton lease is held")
            if current is not None:
                db.execute(
                    "UPDATE scheduler_leases SET active=0,released_at=?,updated_at=? WHERE lease_id=? AND active=1",
                    (now, now, current["lease_id"]),
                )
            generation = int(
                db.execute(
                    "SELECT COALESCE(MAX(generation),0)+1 FROM scheduler_leases WHERE scope=?",
                    (scope,),
                ).fetchone()[0]
            )
            lease_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO scheduler_leases VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    lease_id,
                    scope,
                    owner_uuid,
                    controller_id,
                    generation,
                    now,
                    now,
                    _future(lease_seconds),
                    1,
                    None,
                    now,
                    now,
                ),
            )
            return lease_id, generation

    def heartbeat_singleton(
        self,
        lease_id: str,
        scope: str,
        controller_id: str,
        owner_uuid: str,
        generation: int,
        *,
        lease_seconds: int = 7200,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> None:
        if scope not in {"supervisor", "watcher", "integration", "archive"}:
            raise ValidationError("invalid singleton scope")
        with self._db() as db, _transaction(db):
            now = _now()
            cur = db.execute(
                "UPDATE scheduler_leases SET heartbeat_at=?,lease_expires_at=?,updated_at=? "
                "WHERE lease_id=? AND scope=? AND controller_id=? AND owner_uuid=? "
                "AND generation=? AND active=1 AND lease_expires_at>? AND EXISTS "
                "(SELECT 1 FROM controllers c WHERE c.controller_id=? AND c.owner_uuid=? "
                "AND c.role=? AND c.state='running' AND c.desired=1 AND c.pid=? "
                "AND c.process_starttime_ticks=? AND c.boot_id=?)",
                (
                    now,
                    _future(lease_seconds),
                    now,
                    lease_id,
                    scope,
                    controller_id,
                    owner_uuid,
                    generation,
                    now,
                    controller_id,
                    owner_uuid,
                    scope,
                    pid,
                    process_starttime_ticks,
                    boot_id,
                ),
            )
            if cur.rowcount != 1:
                raise LostLeaseError("singleton lease is lost or expired")

    def release_singleton(
        self,
        lease_id: str,
        scope: str,
        controller_id: str,
        owner_uuid: str,
        generation: int,
        *,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> None:
        with self._db() as db, _transaction(db):
            now = _now()
            cur = db.execute(
                "UPDATE scheduler_leases SET active=0,released_at=?,updated_at=? WHERE lease_id=? "
                "AND scope=? AND controller_id=? AND owner_uuid=? AND generation=? AND active=1 "
                "AND EXISTS (SELECT 1 FROM controllers c WHERE c.controller_id=? AND c.owner_uuid=? "
                "AND c.role=? AND c.state='running' AND c.pid=? AND c.process_starttime_ticks=? AND c.boot_id=?)",
                (
                    now,
                    now,
                    lease_id,
                    scope,
                    controller_id,
                    owner_uuid,
                    generation,
                    controller_id,
                    owner_uuid,
                    scope,
                    pid,
                    process_starttime_ticks,
                    boot_id,
                ),
            )
            if cur.rowcount != 1:
                raise LostLeaseError("singleton release fence failed")

    def claim_next(
        self,
        controller_id: str,
        owner_uuid: str,
        *,
        requested_limit: int = 1,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> list[Claim]:
        if not isinstance(requested_limit, int) or not 1 <= requested_limit <= 8:
            raise ValidationError("requested_limit must be an integer from 1 to 8")
        with self._db() as db, _transaction(db):
            now = _now()
            controller = db.execute(
                "SELECT c.*,l.language lane_language,l.status lane_status FROM controllers c JOIN lanes l ON l.lane_id=c.lane_id WHERE c.controller_id=? AND c.owner_uuid=? AND c.role='authoring_controller' AND c.state='running' AND c.desired=1 AND c.pid=? AND c.process_starttime_ticks=? AND c.boot_id=?",
                (controller_id, owner_uuid, pid, process_starttime_ticks, boot_id),
            ).fetchone()
            if controller is None:
                raise LostLeaseError("controller identity fence failed")
            cfg = db.execute("SELECT * FROM current_runtime_config").fetchone()
            if cfg is None or not cfg["enabled"] or controller["lane_status"] != "active":
                return []
            rows = []
            for unit, kind, key in (
                ("active_claim", "controller", controller_id),
                ("active_claim", "language", controller["language"]),
                ("active_claim", "global", "claims"),
                ("active_claim", "agent", "authoring"),
            ):
                row = db.execute(
                    "SELECT * FROM capacity_rows WHERE capacity_unit=? AND capacity_kind=? AND capacity_key=?",
                    (unit, kind, key),
                ).fetchone()
                if row is None:
                    raise CorruptionError("missing active_claim capacity row")
                rows.append(row)
            limit = min([requested_limit, *(int(row["remaining_count"]) for row in rows)])
            if limit <= 0:
                return []
            selected = db.execute(
                "SELECT t.* FROM tasks t JOIN candidates c ON c.candidate_id=t.candidate_id AND c.lane_id=t.lane_id JOIN candidate_identities i ON i.identity_digest=c.identity_digest WHERE t.state='pending' AND t.lane_id=? AND i.language=? AND (t.next_retry_at IS NULL OR t.next_retry_at<=?) AND t.authoring_attempts<t.attempt_limit ORDER BY CASE WHEN t.priority_until IS NOT NULL AND t.priority_until>? THEN 0 ELSE 1 END,t.priority_until DESC,t.input_ordinal,t.updated_at,t.task_id LIMIT ?",
                (controller["lane_id"], controller["language"], now, now, limit),
            ).fetchall()
            result: list[Claim] = []
            for task in selected:
                self._seal_cutover_barrier(db, "claim", str(task["task_id"]), now)
                db.execute(
                    "UPDATE tasks SET state='claimed',authoring_attempts=authoring_attempts+1,updated_at=? WHERE task_id=? AND state='pending'",
                    (now, task["task_id"]),
                )
                generation = int(
                    db.execute(
                        "SELECT COALESCE(MAX(generation),0)+1 FROM claims WHERE task_id=?",
                        (task["task_id"],),
                    ).fetchone()[0]
                )
                seq = int(
                    db.execute("SELECT COALESCE(MAX(trial_sequence),0)+1 FROM trials").fetchone()[0]
                )
                trial_id, claim_id = str(uuid.uuid4()), str(uuid.uuid4())
                attempt = int(task["authoring_attempts"]) + 1
                db.execute(
                    "INSERT INTO trials(trial_id,trial_sequence,task_id,attempt_no,retry_no,kind,state,owner_uuid,controller_id,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        trial_id,
                        seq,
                        task["task_id"],
                        attempt,
                        task["retry_count"],
                        "authoring",
                        "created",
                        owner_uuid,
                        controller_id,
                        now,
                        now,
                    ),
                )
                interval = max(
                    5, min(int(cfg["heartbeat_interval_seconds"]), int(cfg["lease_seconds"]) - 1)
                )
                db.execute(
                    "INSERT INTO claims VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        claim_id,
                        task["task_id"],
                        trial_id,
                        owner_uuid,
                        controller_id,
                        cfg["lease_seconds"],
                        interval,
                        now,
                        now,
                        _future(cfg["lease_seconds"]),
                        None,
                        None,
                        generation,
                        1,
                        now,
                        now,
                    ),
                )
                for row in rows:
                    cur = db.execute(
                        "UPDATE capacity_rows SET used_count=used_count+1,remaining_count=remaining_count-1,updated_at=? WHERE capacity_unit=? AND capacity_kind=? AND capacity_key=? AND remaining_count>0",
                        (now, row["capacity_unit"], row["capacity_kind"], row["capacity_key"]),
                    )
                    if cur.rowcount != 1:
                        raise CorruptionError("active claim capacity exhausted during claim")
                db.execute(
                    "INSERT INTO events(event_type,occurred_at,actor_type,actor_id,task_id,trial_id,claim_id,lane_id,payload_json) VALUES('task_claimed',?,?,?,?,?,?,?,?)",
                    (
                        now,
                        "controller",
                        controller_id,
                        task["task_id"],
                        trial_id,
                        claim_id,
                        controller["lane_id"],
                        "{}",
                    ),
                )
                result.append(
                    Claim(
                        task["task_id"],
                        trial_id,
                        claim_id,
                        controller["lane_id"],
                        owner_uuid,
                        controller_id,
                        attempt,
                        task["retry_count"],
                        generation,
                    )
                )
            return result

    def dispatch_next_lane(self, *, now: str | None = None) -> str | None:
        """Advance the durable Python/Node/Go lane rotation for controller binding."""
        moment = now or _now()
        with self._db() as db, _transaction(db):
            fairness = db.execute("SELECT * FROM fairness_state WHERE fairness_id=1").fetchone()
            if fairness is None:
                raise CorruptionError("fairness state is missing")
            for offset in range(3):
                index = (int(fairness["next_language_index"]) + offset) % 3
                language = LANGUAGES[index]
                lane = db.execute(
                    "SELECT l.lane_id FROM lanes l WHERE l.language=? AND l.status='active' "
                    "AND EXISTS (SELECT 1 FROM tasks t WHERE t.lane_id=l.lane_id AND t.state='pending' "
                    "AND (t.next_retry_at IS NULL OR t.next_retry_at<=?) "
                    "AND t.authoring_attempts<t.attempt_limit) "
                    "ORDER BY l.last_dispatch_seq,l.fairness_rank,l.lane_id LIMIT 1",
                    (language, moment),
                ).fetchone()
                if lane is None:
                    continue
                sequence = int(fairness["dispatch_sequence"]) + 1
                db.execute(
                    "UPDATE fairness_state SET next_language_index=?,dispatch_sequence=?,updated_at=? WHERE fairness_id=1",
                    ((index + 1) % 3, sequence, moment),
                )
                db.execute(
                    "UPDATE lanes SET last_dispatch_seq=?,updated_at=? WHERE lane_id=?",
                    (sequence, moment, lane["lane_id"]),
                )
                return str(lane["lane_id"])
            return None

    def transition(
        self,
        task_id: str,
        state: str,
        *,
        reason: str | None = None,
        owner_uuid: str | None = None,
        controller_id: str | None = None,
        generation: int | None = None,
        pid: int | None = None,
        process_starttime_ticks: int | None = None,
        boot_id: str | None = None,
        operator_actor: ActorFence | None = None,
    ) -> None:
        _id(task_id, "task_id")
        if state not in {"blocked", "excluded", "cancelled"}:
            raise ValidationError("invalid task state")
        with self._db() as db, _transaction(db):
            if state in {"blocked", "excluded", "cancelled"} and not reason:
                raise ValidationError("terminal reason required")
            task = db.execute("SELECT state FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if task is None:
                raise ConflictError("unknown task")
            if task["state"] in {"claimed", "preparing", "authoring"}:
                if operator_actor is None:
                    raise LostLeaseError("terminal transition requires operator fence")
                self._fenced_operator(db, operator_actor, _now())
                if None in (
                    owner_uuid,
                    controller_id,
                    generation,
                    pid,
                    process_starttime_ticks,
                    boot_id,
                ):
                    raise LostLeaseError("terminal task transition requires full claim fence")
                assert controller_id is not None
                assert owner_uuid is not None
                assert generation is not None
                assert pid is not None
                assert process_starttime_ticks is not None
                assert boot_id is not None
                claim = self._fenced_claim(
                    db,
                    task_id,
                    owner_uuid,
                    controller_id,
                    generation,
                    pid,
                    process_starttime_ticks,
                    boot_id,
                    _now(),
                    by_task=True,
                )
                if state in {"blocked", "excluded", "cancelled"}:
                    self._close_claim(db, claim, _now(), "operator terminal transition")
            elif operator_actor is None:
                raise LostLeaseError("terminal transition requires operator fence")
            else:
                self._fenced_operator(db, operator_actor, _now())
            cur = db.execute(
                "UPDATE tasks SET state=?,terminal_reason=COALESCE(?,terminal_reason),updated_at=? WHERE task_id=?",
                (state, reason, _now(), task_id),
            )
            if cur.rowcount != 1:
                raise ConflictError("unknown task or invalid transition")

    def complete(self, task_id: str, reason: str) -> None:
        """Fenced-by-schema terminal completion after cleanup evidence exists."""
        _id(task_id, "task_id")
        if not reason or not reason.strip():
            raise ValidationError("completion reason is required")
        with self._db() as db, _transaction(db):
            cur = db.execute(
                "UPDATE tasks SET state='complete',terminal_reason=?,updated_at=? "
                "WHERE task_id=? AND state='cleaning'",
                (reason, _now(), task_id),
            )
            if cur.rowcount != 1:
                raise ConflictError("task is not ready for completion")

    def prepare(
        self,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        generation: int = 1,
        *,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> None:
        with self._db() as db, _transaction(db):
            now = _now()
            row = self._fenced_claim(
                db,
                claim_id,
                owner_uuid,
                controller_id,
                generation,
                pid,
                process_starttime_ticks,
                boot_id,
                now,
            )
            cur = db.execute(
                "UPDATE tasks SET state='preparing',updated_at=? WHERE task_id=? AND state='claimed'",
                (now, row["task_id"]),
            )
            if cur.rowcount != 1:
                raise ConflictError("task is not claimable for preparation")
            db.execute(
                "UPDATE trials SET launch_intent_at=?,updated_at=? WHERE trial_id=? AND state='created'",
                (now, now, row["trial_id"]),
            )

    def start(
        self,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        generation: int = 1,
        *,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
        child_pid: int | None = None,
        child_starttime_ticks: int | None = None,
    ) -> None:
        """Confirm a launch intent after Popen succeeded; never before it."""
        if (
            child_pid is None
            or child_starttime_ticks is None
            or child_pid <= 0
            or child_starttime_ticks < 0
        ):
            raise ValidationError("invalid child pid")
        with self._db() as db, _transaction(db):
            now = _now()
            row = self._fenced_claim(
                db,
                claim_id,
                owner_uuid,
                controller_id,
                generation,
                pid,
                process_starttime_ticks,
                boot_id,
                now,
            )
            cur = db.execute(
                "UPDATE tasks SET state='authoring',updated_at=? WHERE task_id=? AND state='preparing'",
                (now, row["task_id"]),
            )
            if cur.rowcount != 1:
                raise ConflictError("task is not prepared")
            cur = db.execute(
                "UPDATE trials SET state='running',child_pid=?,child_starttime_ticks=?,child_boot_id=?,started_at=?,updated_at=? WHERE trial_id=? "
                "AND state='created' AND launch_intent_at IS NOT NULL",
                (
                    child_pid,
                    child_starttime_ticks,
                    boot_id if child_pid is not None else None,
                    now,
                    now,
                    row["trial_id"],
                ),
            )
            if cur.rowcount != 1:
                raise ConflictError("trial lacks launch intent")

    def heartbeat(
        self,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        generation: int = 1,
        *,
        now: str | None = None,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> None:
        moment = now or _now()
        with self._db() as db, _transaction(db):
            row = self._fenced_claim(
                db,
                claim_id,
                owner_uuid,
                controller_id,
                generation,
                pid,
                process_starttime_ticks,
                boot_id,
                moment,
            )
            db.execute(
                "UPDATE claims SET heartbeat_at=?,lease_expires_at=?,updated_at=? WHERE claim_id=?",
                (
                    moment,
                    (
                        datetime.fromisoformat(moment) + timedelta(seconds=row["lease_seconds"])
                    ).isoformat(timespec="microseconds"),
                    moment,
                    claim_id,
                ),
            )

    def release(
        self,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        generation: int = 1,
        *,
        reason: str = "released",
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> None:
        with self._db() as db, _transaction(db):
            row = self._fenced_claim(
                db,
                claim_id,
                owner_uuid,
                controller_id,
                generation,
                pid,
                process_starttime_ticks,
                boot_id,
                _now(),
            )
            task = db.execute(
                "SELECT release_count,release_limit FROM tasks WHERE task_id=?", (row["task_id"],)
            ).fetchone()
            if task["release_count"] >= task["release_limit"]:
                raise ConflictError("release limit exhausted")
            now = _now()
            db.execute(
                "UPDATE claims SET active=0,released_at=?,release_reason=?,updated_at=? WHERE claim_id=? AND active=1",
                (now, reason, now, claim_id),
            )
            db.execute(
                "UPDATE trials SET state='released',finished_at=?,updated_at=? WHERE trial_id=? AND state='running'",
                (now, now, row["trial_id"]),
            )
            db.execute(
                "UPDATE trials SET state='released',updated_at=? WHERE trial_id=? AND state='created'",
                (now, row["trial_id"]),
            )
            db.execute(
                "UPDATE tasks SET state='pending',release_count=release_count+1,updated_at=? WHERE task_id=?",
                (now, row["task_id"]),
            )
            self._decrement(db, row["controller_id"], row["task_id"], now)

    def abort_claim(
        self,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        generation: int = 1,
        *,
        reason: str,
        failure_class: str = "infrastructure",
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> None:
        """Close a claim that failed before a child reached running state."""
        if failure_class not in {
            "source",
            "spec",
            "environment",
            "verifier",
            "model",
            "infrastructure",
        } or not reason:
            raise ValidationError("abort requires a classified reason")
        with self._db() as db, _transaction(db):
            row = self._fenced_claim(
                db,
                claim_id,
                owner_uuid,
                controller_id,
                generation,
                pid,
                process_starttime_ticks,
                boot_id,
                _now(),
            )
            trial = db.execute(
                "SELECT state FROM trials WHERE trial_id=?", (row["trial_id"],)
            ).fetchone()
            if trial is None or trial["state"] != "created":
                raise ConflictError("abort accepts only a pre-start claim")
            now = _now()
            self._close_claim(db, row, now, reason)
            task = db.execute(
                "SELECT retry_count,retry_limit FROM tasks WHERE task_id=?", (row["task_id"],)
            ).fetchone()
            retryable = failure_class == "infrastructure" and task["retry_count"] < task["retry_limit"]
            if retryable:
                db.execute(
                    "UPDATE tasks SET state='pending',retry_count=retry_count+1,"
                    "last_failure_class=?,last_failure_reason=?,updated_at=? WHERE task_id=?",
                    (failure_class, reason, now, row["task_id"]),
                )
            else:
                db.execute(
                    "UPDATE tasks SET state='blocked',terminal_reason=?,last_failure_class=?,"
                    "last_failure_reason=?,updated_at=? WHERE task_id=?",
                    (reason, failure_class, reason, now, row["task_id"]),
                )

    @staticmethod
    def _decrement(db: sqlite3.Connection, controller_id: str, task_id: str, now: str) -> None:
        language = db.execute(
            "SELECT language FROM controllers WHERE controller_id=?", (controller_id,)
        ).fetchone()[0]
        for kind, key in (
            ("controller", controller_id),
            ("language", language),
            ("global", "claims"),
            ("agent", "authoring"),
        ):
            cur = db.execute(
                "UPDATE capacity_rows SET used_count=used_count-1,remaining_count=remaining_count+1,updated_at=? WHERE capacity_unit='active_claim' AND capacity_kind=? AND capacity_key=? AND used_count>0",
                (now, kind, key),
            )
            if cur.rowcount != 1:
                raise CorruptionError("active claim capacity invariant failed")

    def finish(
        self,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        generation: int = 1,
        *,
        success: bool,
        reason: str = "finished",
        failure_class: str | None = None,
        pid: int = 1,
        process_starttime_ticks: int = 0,
        boot_id: str = "test",
    ) -> None:
        if not success and failure_class not in {
            "source",
            "spec",
            "environment",
            "verifier",
            "model",
            "infrastructure",
        }:
            raise ValidationError("failed finish requires a failure class")
        with self._db() as db, _transaction(db):
            row = self._fenced_claim(
                db,
                claim_id,
                owner_uuid,
                controller_id,
                generation,
                pid,
                process_starttime_ticks,
                boot_id,
                _now(),
            )
            trial = db.execute(
                "SELECT state FROM trials WHERE trial_id=?", (row["trial_id"],)
            ).fetchone()
            if trial is None or trial["state"] != "running":
                raise ConflictError("trial has not started")
            now = _now()
            db.execute(
                "UPDATE claims SET active=0,released_at=?,release_reason=?,updated_at=? WHERE claim_id=? AND active=1",
                (now, reason, now, claim_id),
            )
            db.execute(
                "UPDATE trials SET state=?,finished_at=?,updated_at=? WHERE trial_id=? AND state='running'",
                ("succeeded" if success else "failed", now, now, row["trial_id"]),
            )
            task = db.execute(
                "SELECT retry_count,retry_limit FROM tasks WHERE task_id=?", (row["task_id"],)
            ).fetchone()
            retryable = (
                not success
                and failure_class == "infrastructure"
                and task["retry_count"] < task["retry_limit"]
            )
            if retryable:
                new_retry = int(task["retry_count"]) + 1
                delay = min(1800, 30 * (2**new_retry)) + (
                    int(hashlib.sha256(row["task_id"].encode()).hexdigest()[:4], 16) % 30
                )
                next_retry = (datetime.fromisoformat(now) + timedelta(seconds=delay)).isoformat(
                    timespec="microseconds"
                )
                db.execute(
                    "UPDATE tasks SET state='pending',terminal_reason=NULL,retry_count=?,next_retry_at=?,last_failure_class=?,last_failure_reason=?,updated_at=? WHERE task_id=?",
                    (new_retry, next_retry, failure_class, reason, now, row["task_id"]),
                )
            else:
                db.execute(
                    "UPDATE tasks SET state=?,terminal_reason=?,last_failure_class=?,last_failure_reason=?,updated_at=? WHERE task_id=?",
                    (
                        "handoff_ready" if success else "blocked",
                        None if success else reason,
                        None if success else failure_class,
                        None if success else reason,
                        now,
                        row["task_id"],
                    ),
                )
            self._decrement(db, controller_id, row["task_id"], now)

    def begin_receipt(
        self,
        task_id: str,
        kind: str,
        attempt: int,
        retry_no: int,
        idempotency_key: str,
        *,
        actor: ActorFence | None = None,
    ) -> str:
        if attempt < 1 or retry_no < 0:
            raise ValidationError("invalid operation receipt counters")
        return self.begin_operation(
            task_id,
            kind,
            idempotency_key,
            operation_attempt=attempt,
            retry_no=retry_no,
            actor=actor,
        )

    def begin_operation(
        self,
        task_id: str,
        kind: str,
        idempotency_key: str,
        *,
        operation_attempt: int | None = None,
        retry_no: int | None = None,
        actor: ActorFence | None = None,
    ) -> str:
        """Persist an operation intent and move only its matching stage forward.

        Authoring claims select only ``pending`` tasks, therefore all operation
        retry states are structurally excluded from reauthoring.
        """
        _id(task_id, "task_id")
        _id(idempotency_key, "idempotency_key")
        if actor is None:
            raise LostLeaseError("operation requires a live singleton actor")
        states = {
            "integration": (
                ("handoff_ready", "integration_retry"),
                "integrating",
                "integration_attempts",
                "integration_retry_count",
            ),
            "archive": (
                ("integrating", "archive_retry"),
                "archiving",
                "archive_attempts",
                "archive_retry_count",
            ),
            "cleanup": (
                ("archiving", "cleanup_retry"),
                "cleaning",
                "cleanup_attempts",
                "cleanup_retry_count",
            ),
        }
        if kind not in states:
            raise ValidationError("invalid operation kind")
        accepted, next_state, attempt_col, retry_col = states[kind]
        with self._db() as db, _transaction(db):
            self._fenced_actor(db, actor, kind, _now())
            existing = db.execute(
                "SELECT * FROM operation_receipts WHERE idempotency_key=?",
                (idempotency_key,),
            ).fetchone()
            if existing is not None:
                if existing["task_id"] != task_id or existing["operation_kind"] != kind:
                    raise ConflictError("idempotency key context mismatch")
                if (
                    operation_attempt is not None
                    and existing["operation_attempt"] != operation_attempt
                ):
                    raise ConflictError("idempotency attempt mismatch")
                if retry_no is not None and existing["retry_no"] != retry_no:
                    raise ConflictError("idempotency retry mismatch")
                if (
                    existing["actor_lease_id"],
                    existing["actor_generation"],
                    existing["actor_id"],
                    existing["actor_owner_uuid"],
                ) != (actor.lease_id, actor.generation, actor.controller_id, actor.owner_uuid):
                    raise LostLeaseError("receipt actor context mismatch")
                return str(existing[0])
            task = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if task is None or task["state"] not in accepted:
                raise ConflictError("task is not ready for this operation")
            if (
                kind == "archive"
                and db.execute(
                    "SELECT 1 FROM operation_receipts WHERE task_id=? AND operation_kind='integration' AND status='pushed'",
                    (task_id,),
                ).fetchone()
                is None
            ):
                raise ConflictError("pushed integration receipt required")
            if (
                kind == "cleanup"
                and db.execute(
                    "SELECT 1 FROM operation_receipts WHERE task_id=? AND operation_kind='archive' AND status='verified'",
                    (task_id,),
                ).fetchone()
                is None
            ):
                raise ConflictError("verified archive receipt required")
            now = _now()
            attempt = int(task[attempt_col]) + 1
            retry = int(task[retry_col])
            if operation_attempt is not None and operation_attempt != attempt:
                raise ConflictError("operation attempt does not match task")
            if retry_no is not None and retry_no != retry:
                raise ConflictError("operation retry does not match task")
            self._seal_cutover_barrier(db, kind, task_id, now)
            db.execute(
                f"UPDATE tasks SET state=?,{attempt_col}=?,updated_at=? WHERE task_id=?",
                (next_state, attempt, now, task_id),
            )
            receipt = str(uuid.uuid4())
            db.execute(
                "INSERT INTO operation_receipts(receipt_id,task_id,operation_kind,operation_attempt,retry_no,idempotency_key,status,actor_scope,actor_lease_id,actor_generation,actor_id,actor_owner_uuid,actor_pid,actor_starttime_ticks,actor_boot_id,started_at,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    receipt,
                    task_id,
                    kind,
                    attempt,
                    retry,
                    idempotency_key,
                    "started",
                    actor.scope,
                    actor.lease_id,
                    actor.generation,
                    actor.controller_id,
                    actor.owner_uuid,
                    actor.pid,
                    actor.process_starttime_ticks,
                    actor.boot_id,
                    now,
                    now,
                    now,
                ),
            )
            return receipt

    def fail_operation(
        self,
        receipt_id: str,
        failure_class: str,
        reason: str,
        *,
        actor: ActorFence | None = None,
        evidence_path: str | None = None,
        evidence_sha256: str | None = None,
    ) -> None:
        """Record a failure; only infrastructure failures enter the same-stage retry state."""
        if (
            failure_class
            not in {"source", "spec", "environment", "verifier", "model", "infrastructure"}
            or not reason
        ):
            raise ValidationError("invalid operation failure")
        evidence_digest: str | None = None
        if (evidence_path is None) != (evidence_sha256 is None):
            raise ValidationError("operation failure evidence must be complete")
        if evidence_path is not None and evidence_sha256 is not None:
            path = Path(evidence_path)
            if path.is_absolute() or ".." in path.parts:
                raise ValidationError("operation failure evidence_path must be relative")
            evidence_digest = _digest(evidence_sha256, "evidence_sha256")
        with self._db() as db, _transaction(db):
            receipt = db.execute(
                "SELECT * FROM operation_receipts WHERE receipt_id=?", (receipt_id,)
            ).fetchone()
            if receipt is None:
                raise ConflictError("unknown receipt")
            task = db.execute(
                "SELECT * FROM tasks WHERE task_id=?", (receipt["task_id"],)
            ).fetchone()
            kind = str(receipt["operation_kind"])
            if actor is None:
                raise LostLeaseError("operation requires a live singleton actor")
            self._fenced_actor(db, actor, kind, _now())
            if (
                receipt["actor_lease_id"],
                receipt["actor_generation"],
                receipt["actor_id"],
                receipt["actor_owner_uuid"],
            ) != (actor.lease_id, actor.generation, actor.controller_id, actor.owner_uuid):
                raise LostLeaseError("receipt actor context mismatch")
            retry_col, limit_col, retry_state = {
                "integration": (
                    "integration_retry_count",
                    "integration_retry_limit",
                    "integration_retry",
                ),
                "archive": ("archive_retry_count", "archive_retry_limit", "archive_retry"),
                "cleanup": ("cleanup_retry_count", "cleanup_retry_limit", "cleanup_retry"),
            }[kind]
            now = _now()
            if receipt["status"] == "failed":
                return
            if receipt["status"] not in {"started", "committed"}:
                raise ConflictError("receipt is no longer fail-able")
            cur = db.execute(
                "UPDATE operation_receipts SET status='failed',failure_class=?,failure_reason=?,"
                "evidence_path=?,evidence_sha256=?,finished_at=?,updated_at=? "
                "WHERE receipt_id=? AND status IN ('started','committed')",
                (
                    failure_class,
                    reason,
                    evidence_path,
                    evidence_digest,
                    now,
                    now,
                    receipt_id,
                ),
            )
            if cur.rowcount != 1:
                return
            if failure_class == "infrastructure" and task[retry_col] < task[limit_col]:
                db.execute(
                    f"UPDATE tasks SET state=?,{retry_col}={retry_col}+1,last_failure_class=?,last_failure_reason=?,updated_at=? WHERE task_id=?",
                    (retry_state, failure_class, reason, now, task["task_id"]),
                )
            else:
                db.execute(
                    "UPDATE tasks SET state='blocked',terminal_reason=?,last_failure_class=?,last_failure_reason=?,updated_at=? WHERE task_id=?",
                    (reason, failure_class, reason, now, task["task_id"]),
                )

    def collide_operation(
        self,
        receipt_id: str,
        failure_class: str,
        reason: str,
        *,
        evidence_path: str,
        evidence_sha256: str,
        actor: ActorFence | None = None,
    ) -> None:
        """Record a classified remote collision and block cleanup atomically."""
        if failure_class not in {"source", "environment", "infrastructure"} or not reason:
            raise ValidationError("collision requires a classified failure")
        path = Path(evidence_path)
        if not evidence_path or path.is_absolute() or ".." in path.parts:
            raise ValidationError("collision evidence_path must be relative")
        digest = _digest(evidence_sha256, "evidence_sha256")
        with self._db() as db, _transaction(db):
            receipt = db.execute(
                "SELECT * FROM operation_receipts WHERE receipt_id=?", (receipt_id,)
            ).fetchone()
            if receipt is None or receipt["operation_kind"] != "archive":
                raise ConflictError("collision requires an archive receipt")
            if actor is None:
                raise LostLeaseError("collision requires a live archive actor")
            self._fenced_actor(db, actor, "archive", _now())
            if (
                receipt["actor_lease_id"],
                receipt["actor_generation"],
                receipt["actor_id"],
                receipt["actor_owner_uuid"],
            ) != (actor.lease_id, actor.generation, actor.controller_id, actor.owner_uuid):
                raise LostLeaseError("receipt actor context mismatch")
            task = db.execute(
                "SELECT state FROM tasks WHERE task_id=?", (receipt["task_id"],)
            ).fetchone()
            if task is None or task["state"] != "archiving":
                raise ConflictError("collision task-state fence failed")
            now = _now()
            cur = db.execute(
                "UPDATE operation_receipts SET status='collision',failure_class=?,failure_reason=?,"
                "evidence_path=?,evidence_sha256=?,finished_at=?,updated_at=? "
                "WHERE receipt_id=? AND status='started'",
                (failure_class, reason, evidence_path, digest, now, now, receipt_id),
            )
            if cur.rowcount != 1:
                raise ConflictError("receipt is no longer collision-reportable")
            db.execute(
                "UPDATE tasks SET state='blocked',terminal_reason=?,last_failure_class=?,"
                "last_failure_reason=?,updated_at=? WHERE task_id=? AND state='archiving'",
                (reason, failure_class, reason, now, receipt["task_id"]),
            )

    def reconcile_stale(self, *, now: str | None = None) -> int:
        """Close expired claims atomically; heartbeat wins any TOCTOU race."""
        moment = now or _now()
        with self._db() as db, _transaction(db):
            rows = db.execute(
                "SELECT * FROM claims WHERE active=1 AND lease_expires_at<=?", (moment,)
            ).fetchall()
            changed = 0
            for row in rows:
                cur = db.execute(
                    "UPDATE claims SET active=0,released_at=?,release_reason='expired',updated_at=? WHERE claim_id=? AND active=1 AND lease_expires_at<=?",
                    (moment, moment, row["claim_id"], moment),
                )
                if cur.rowcount != 1:
                    continue
                task = db.execute(
                    "SELECT * FROM tasks WHERE task_id=?", (row["task_id"],)
                ).fetchone()
                db.execute(
                    "UPDATE trials SET state='stale',updated_at=? WHERE trial_id=? AND state='created'",
                    (moment, row["trial_id"]),
                )
                db.execute(
                    "UPDATE trials SET state='stale',finished_at=?,failure_class='infrastructure',failure_reason='lease expired',updated_at=? WHERE trial_id=? AND state='running'",
                    (moment, moment, row["trial_id"]),
                )
                db.execute(
                    "UPDATE tasks SET state='stale',last_failure_class='infrastructure',last_failure_reason='lease expired',updated_at=? WHERE task_id=?",
                    (moment, row["task_id"]),
                )
                self._decrement(db, row["controller_id"], row["task_id"], moment)
                if task["retry_count"] < task["retry_limit"]:
                    new_count = int(task["retry_count"]) + 1
                    delay = min(1800, 30 * (2**new_count)) + (
                        int(hashlib.sha256(task["task_id"].encode()).hexdigest()[:4], 16) % 30
                    )
                    later = (datetime.fromisoformat(moment) + timedelta(seconds=delay)).isoformat(
                        timespec="microseconds"
                    )
                    db.execute(
                        "UPDATE tasks SET state='pending',retry_count=?,next_retry_at=?,updated_at=? WHERE task_id=?",
                        (new_count, later, moment, row["task_id"]),
                    )
                else:
                    db.execute(
                        "UPDATE tasks SET state='blocked',terminal_reason='infrastructure retry limit exhausted',updated_at=? WHERE task_id=?",
                        (moment, row["task_id"]),
                    )
                changed += 1
            return changed

    def reconcile_launch_intents(self, *, now: str | None = None) -> int:
        """Close claims whose durable launch intent never became a running trial."""
        moment = now or _now()
        with self._db() as db, _transaction(db):
            rows = db.execute(
                "SELECT cl.*,t.state task_state FROM claims cl JOIN trials tr ON tr.trial_id=cl.trial_id "
                "JOIN tasks t ON t.task_id=cl.task_id WHERE cl.active=1 AND tr.state='created' "
                "AND tr.launch_intent_at IS NOT NULL AND tr.launch_intent_at<=?",
                (moment,),
            ).fetchall()
            for row in rows:
                self._close_claim(db, row, moment, "launch intent expired before process start")
                db.execute(
                    "UPDATE tasks SET state='stale',last_failure_class='infrastructure',last_failure_reason='launch intent expired',updated_at=? WHERE task_id=?",
                    (moment, row["task_id"]),
                )
                task = db.execute(
                    "SELECT retry_count,retry_limit FROM tasks WHERE task_id=?", (row["task_id"],)
                ).fetchone()
                if task["retry_count"] < task["retry_limit"]:
                    db.execute(
                        "UPDATE tasks SET state='pending',retry_count=retry_count+1,updated_at=? WHERE task_id=?",
                        (moment, row["task_id"]),
                    )
                else:
                    db.execute(
                        "UPDATE tasks SET state='blocked',terminal_reason='launch retry limit exhausted',updated_at=? WHERE task_id=?",
                        (moment, row["task_id"]),
                    )
            return len(rows)

    def reconcile_controllers(self, *, now: str | None = None) -> int:
        """Fence dead/reused local processes and release their scheduler usage."""
        moment = now or _now()

        def alive(pid: int, starttime: int, boot_id: str) -> bool:
            try:
                current_boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
                fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
                return current_boot == boot_id and int(fields[19]) == starttime
            except (OSError, ValueError, IndexError):
                return False

        with self._db() as db, _transaction(db):
            rows = db.execute(
                "SELECT * FROM controllers WHERE state IN ('running','draining')"
            ).fetchall()
            changed = 0
            for controller in rows:
                if alive(
                    int(controller["pid"]),
                    int(controller["process_starttime_ticks"]),
                    str(controller["boot_id"]),
                ):
                    continue
                claims = db.execute(
                    "SELECT * FROM claims WHERE controller_id=? AND owner_uuid=? AND active=1",
                    (controller["controller_id"], controller["owner_uuid"]),
                ).fetchall()
                for claim in claims:
                    self._close_claim(db, claim, moment, "controller process disappeared")
                    task = db.execute(
                        "SELECT retry_count,retry_limit FROM tasks WHERE task_id=?",
                        (claim["task_id"],),
                    ).fetchone()
                    if task["retry_count"] < task["retry_limit"]:
                        db.execute(
                            "UPDATE tasks SET state='pending',retry_count=retry_count+1,"
                            "last_failure_class='infrastructure',last_failure_reason=?,updated_at=? "
                            "WHERE task_id=?",
                            ("controller process disappeared", moment, claim["task_id"]),
                        )
                    else:
                        db.execute(
                            "UPDATE tasks SET state='blocked',terminal_reason=?,"
                            "last_failure_class='infrastructure',last_failure_reason=?,updated_at=? "
                            "WHERE task_id=?",
                            (
                                "controller reconciliation retry limit exhausted",
                                "controller process disappeared",
                                moment,
                                claim["task_id"],
                            ),
                        )
                db.execute(
                    "UPDATE scheduler_leases SET active=0,released_at=?,updated_at=? "
                    "WHERE controller_id=? AND active=1",
                    (moment, moment, controller["controller_id"]),
                )
                db.execute(
                    "UPDATE controllers SET state='reconciled',desired=0,stopped_at=?,updated_at=? "
                    "WHERE controller_id=? AND state IN ('running','draining')",
                    (moment, moment, controller["controller_id"]),
                )
                if controller["role"] == "authoring_controller":
                    db.execute(
                        "UPDATE controller_slot_reservations SET state='released',updated_at=? "
                        "WHERE controller_id=? AND state='activated'",
                        (moment, controller["controller_id"]),
                    )
                    self._controller_capacity_delta(
                        db,
                        str(controller["controller_id"]),
                        str(controller["language"]),
                        -1,
                        moment,
                    )
                changed += 1
            return changed

    def recover_controller(
        self,
        claim_id: str,
        generation: int,
        controller_id: str,
        owner_uuid: str,
        *,
        pid: int,
        process_starttime_ticks: int,
        boot_id: str,
        reason: str,
    ) -> int:
        """Atomically close running claims after their child has been reaped."""
        if not reason:
            raise ValidationError("controller recovery reason is required")
        with self._db() as db, _transaction(db):
            controller = db.execute(
                "SELECT * FROM controllers WHERE controller_id=? AND owner_uuid=? "
                "AND pid=? AND process_starttime_ticks=? AND boot_id=?",
                (controller_id, owner_uuid, pid, process_starttime_ticks, boot_id),
            ).fetchone()
            if controller is None:
                raise LostLeaseError("controller recovery identity fence failed")
            if controller["state"] in {"stopped", "lost", "reconciled"}:
                return 0
            now = _now()
            claim = db.execute(
                "SELECT * FROM claims WHERE claim_id=? AND generation=? AND controller_id=? "
                "AND owner_uuid=? AND active=1",
                (claim_id, generation, controller_id, owner_uuid),
            ).fetchone()
            if claim is None:
                raise LostLeaseError("claim recovery generation fence failed")
            self._close_claim(db, claim, now, reason)
            task = db.execute(
                "SELECT retry_count,retry_limit FROM tasks WHERE task_id=?",
                (claim["task_id"],),
            ).fetchone()
            if int(task["retry_count"]) < int(task["retry_limit"]):
                db.execute(
                    "UPDATE tasks SET state='pending',retry_count=retry_count+1,"
                    "last_failure_class='infrastructure',last_failure_reason=?,updated_at=? "
                    "WHERE task_id=?",
                    (reason, now, claim["task_id"]),
                )
            else:
                db.execute(
                    "UPDATE tasks SET state='blocked',terminal_reason=?,"
                    "last_failure_class='infrastructure',last_failure_reason=?,updated_at=? "
                    "WHERE task_id=?",
                    (reason, reason, now, claim["task_id"]),
                )
            remaining = db.execute(
                "SELECT 1 FROM claims WHERE controller_id=? AND owner_uuid=? AND active=1 LIMIT 1",
                (controller_id, owner_uuid),
            ).fetchone()
            if remaining is not None:
                return 1
            db.execute(
                "UPDATE scheduler_leases SET active=0,released_at=?,updated_at=? "
                "WHERE controller_id=? AND active=1",
                (now, now, controller_id),
            )
            db.execute(
                "UPDATE controllers SET state='stopped',desired=0,stopped_at=?,updated_at=? "
                "WHERE controller_id=? AND state IN ('running','draining')",
                (now, now, controller_id),
            )
            if controller["role"] == "authoring_controller":
                db.execute(
                    "UPDATE controller_slot_reservations SET state='released',updated_at=? "
                    "WHERE controller_id=? AND state='activated'",
                    (now, controller_id),
                )
                self._controller_capacity_delta(
                    db, controller_id, str(controller["language"]), -1, now
                )
            return 1

    def reconcile_singletons(self, *, now: str | None = None) -> int:
        """Expire singleton leases even when a wedged process still exists."""
        moment = now or _now()
        with self._db() as db, _transaction(db):
            rows = db.execute(
                "SELECT * FROM scheduler_leases WHERE active=1 AND lease_expires_at<=?",
                (moment,),
            ).fetchall()
            for row in rows:
                db.execute(
                    "UPDATE scheduler_leases SET active=0,released_at=?,updated_at=? "
                    "WHERE lease_id=? AND active=1 AND lease_expires_at<=?",
                    (moment, moment, row["lease_id"], moment),
                )
                db.execute(
                    "UPDATE controllers SET state='reconciled',desired=0,stopped_at=?,updated_at=? "
                    "WHERE controller_id=? AND role<>'authoring_controller' "
                    "AND state IN ('running','draining')",
                    (moment, moment, row["controller_id"]),
                )
            return len(rows)

    def reconcile_operations(self, actor: ActorFence, *, now: str | None = None) -> int:
        """Retry or block abandoned external-operation intents under a new actor fence."""
        moment = now or _now()
        operation_kinds = ("integration",) if actor.scope == "integration" else ("archive", "cleanup")
        if actor.scope not in {"integration", "archive"}:
            raise ValidationError("operation reconciliation requires integration or archive actor")
        with self._db() as db, _transaction(db):
            self._fenced_actor(db, actor, operation_kinds[0], moment)
            placeholders = ",".join("?" for _ in operation_kinds)
            rows = db.execute(
                f"SELECT r.*,t.state task_state FROM operation_receipts r "
                "JOIN tasks t ON t.task_id=r.task_id "
                f"WHERE r.operation_kind IN ({placeholders}) AND r.status IN ('started','committed') "
                "AND NOT EXISTS (SELECT 1 FROM scheduler_leases l JOIN controllers c "
                "ON c.controller_id=l.controller_id AND c.owner_uuid=l.owner_uuid "
                "WHERE l.lease_id=r.actor_lease_id AND l.generation=r.actor_generation "
                "AND l.active=1 AND l.lease_expires_at>? AND c.state='running' AND c.desired=1)",
                (*operation_kinds, moment),
            ).fetchall()
            changed = 0
            for receipt in rows:
                kind = str(receipt["operation_kind"])
                retry_col, limit_col, retry_state, expected_state = {
                    "integration": (
                        "integration_retry_count",
                        "integration_retry_limit",
                        "integration_retry",
                        "integrating",
                    ),
                    "archive": (
                        "archive_retry_count",
                        "archive_retry_limit",
                        "archive_retry",
                        "archiving",
                    ),
                    "cleanup": (
                        "cleanup_retry_count",
                        "cleanup_retry_limit",
                        "cleanup_retry",
                        "cleaning",
                    ),
                }[kind]
                task = db.execute("SELECT * FROM tasks WHERE task_id=?", (receipt["task_id"],)).fetchone()
                if task is None or task["state"] != expected_state:
                    raise CorruptionError("abandoned receipt task-state mismatch")
                reason = "operation actor lease expired before terminal receipt"
                cur = db.execute(
                    "UPDATE operation_receipts SET status='failed',failure_class='infrastructure',"
                    "failure_reason=?,finished_at=?,updated_at=? WHERE receipt_id=? "
                    "AND status IN ('started','committed')",
                    (reason, moment, moment, receipt["receipt_id"]),
                )
                if cur.rowcount != 1:
                    continue
                if int(task[retry_col]) < int(task[limit_col]):
                    db.execute(
                        f"UPDATE tasks SET state=?,{retry_col}={retry_col}+1,"
                        "last_failure_class='infrastructure',last_failure_reason=?,updated_at=? "
                        "WHERE task_id=?",
                        (retry_state, reason, moment, task["task_id"]),
                    )
                else:
                    db.execute(
                        "UPDATE tasks SET state='blocked',terminal_reason=?,"
                        "last_failure_class='infrastructure',last_failure_reason=?,updated_at=? "
                        "WHERE task_id=?",
                        (reason, reason, moment, task["task_id"]),
                    )
                changed += 1
            return changed

    def update_receipt(
        self, receipt_id: str, status: str, *, actor: ActorFence | None = None, **fields: Any
    ) -> None:
        _id(receipt_id, "receipt_id")
        if status not in {"committed", "pushed", "verified", "applied"}:
            raise ValidationError("invalid receipt status")
        allowed = {
            "source_digest",
            "generated_digest",
            "commit_sha",
            "external_ref",
            "manifest_key",
            "manifest_sha256",
            "source_snapshot_sha256",
            "object_count",
            "byte_count",
            "evidence_path",
            "evidence_sha256",
            "receipt_json",
        }
        if set(fields) - allowed:
            raise ValidationError("unknown receipt field")
        for key in (
            "source_digest",
            "generated_digest",
            "manifest_sha256",
            "source_snapshot_sha256",
            "evidence_sha256",
        ):
            if key in fields:
                fields[key] = _digest(fields[key], key)
        if status == "pushed":
            commit_sha = fields.get("commit_sha")
            if not isinstance(commit_sha, str) or not HEX40_RE.fullmatch(commit_sha):
                raise ValidationError("pushed receipt requires a 40-hex commit_sha")
            if not isinstance(fields.get("external_ref"), str) or not fields[
                "external_ref"
            ].startswith("refs/"):
                raise ValidationError("pushed receipt requires external_ref")
        if status == "verified":
            if not isinstance(fields.get("manifest_key"), str) or not fields["manifest_key"]:
                raise ValidationError("verified receipt requires manifest_key")
            if not isinstance(fields.get("object_count"), int) or fields["object_count"] <= 0:
                raise ValidationError("verified receipt requires positive object_count")
            if not isinstance(fields.get("byte_count"), int) or fields["byte_count"] <= 0:
                raise ValidationError("verified receipt requires positive byte_count")
            for key in ("manifest_sha256", "source_snapshot_sha256", "evidence_sha256"):
                if key not in fields:
                    raise ValidationError(f"verified receipt requires {key}")
        if status == "applied":
            if not isinstance(fields.get("evidence_path"), str) or not fields["evidence_path"]:
                raise ValidationError("applied receipt requires evidence_path")
            evidence_path = Path(fields["evidence_path"])
            if evidence_path.is_absolute() or ".." in evidence_path.parts:
                raise ValidationError("evidence_path must be relative")
            if "evidence_sha256" not in fields:
                raise ValidationError("applied receipt requires evidence_sha256")
        with self._db() as db, _transaction(db):
            receipt = db.execute(
                "SELECT * FROM operation_receipts WHERE receipt_id=?", (receipt_id,)
            ).fetchone()
            if receipt is None:
                raise ConflictError("unknown receipt")
            if actor is None:
                raise LostLeaseError("receipt update requires a live singleton actor")
            self._fenced_actor(db, actor, receipt["operation_kind"], _now())
            task = db.execute(
                "SELECT state FROM tasks WHERE task_id=?", (receipt["task_id"],)
            ).fetchone()
            if task is None:
                raise CorruptionError("receipt task is missing")
            expected_state = {
                "integration": "integrating",
                "archive": "archiving",
                "cleanup": "cleaning",
            }[receipt["operation_kind"]]
            if task["state"] != expected_state:
                raise ConflictError("receipt task-state fence failed")
            current = receipt["status"]
            transitions = {
                "started": {"committed", "pushed", "verified", "applied"},
                "committed": {"pushed"},
            }
            if status not in transitions.get(current, set()):
                raise ConflictError("invalid receipt status transition")
            allowed_statuses = {
                "integration": {"committed", "pushed"},
                "archive": {"verified"},
                "cleanup": {"applied"},
            }
            if status not in allowed_statuses[receipt["operation_kind"]]:
                raise ConflictError("status does not match operation kind")
            if (
                receipt["actor_lease_id"],
                receipt["actor_generation"],
                receipt["actor_id"],
                receipt["actor_owner_uuid"],
            ) != (actor.lease_id, actor.generation, actor.controller_id, actor.owner_uuid):
                raise LostLeaseError("receipt actor context mismatch")
            values = {
                key: (
                    _json(value) if key == "receipt_json" and not isinstance(value, str) else value
                )
                for key, value in fields.items()
            }
            values["status"], values["finished_at"], values["updated_at"] = status, _now(), _now()
            assignments = ",".join(f"{key}=?" for key in values)
            cur = db.execute(
                f"UPDATE operation_receipts SET {assignments} WHERE receipt_id=?",
                (*values.values(), receipt_id),
            )
            if cur.rowcount != 1:
                raise ConflictError("unknown receipt")

    def apply_cleanup_and_complete(
        self,
        receipt_id: str,
        *,
        actor: ActorFence,
        evidence_path: str,
        evidence_sha256: str,
        receipt_json: Mapping[str, Any],
        reason: str,
    ) -> None:
        """Atomically apply cleanup evidence and complete its task."""
        _id(receipt_id, "receipt_id")
        path = Path(evidence_path)
        if not evidence_path or path.is_absolute() or ".." in path.parts:
            raise ValidationError("cleanup evidence_path must be relative")
        digest = _digest(evidence_sha256, "evidence_sha256")
        if not reason.strip():
            raise ValidationError("completion reason is required")
        with self._db() as db, _transaction(db):
            receipt = db.execute(
                "SELECT * FROM operation_receipts WHERE receipt_id=?", (receipt_id,)
            ).fetchone()
            if receipt is None or receipt["operation_kind"] != "cleanup":
                raise ConflictError("unknown cleanup receipt")
            task = db.execute(
                "SELECT state FROM tasks WHERE task_id=?", (receipt["task_id"],)
            ).fetchone()
            if receipt["status"] == "applied" and task is not None and task["state"] == "complete":
                return
            self._fenced_actor(db, actor, "cleanup", _now())
            if (
                receipt["status"] != "started"
                or task is None
                or task["state"] != "cleaning"
                or (
                    receipt["actor_lease_id"],
                    receipt["actor_generation"],
                    receipt["actor_id"],
                    receipt["actor_owner_uuid"],
                )
                != (actor.lease_id, actor.generation, actor.controller_id, actor.owner_uuid)
            ):
                raise ConflictError("cleanup receipt task or actor fence failed")
            now = _now()
            cur = db.execute(
                "UPDATE operation_receipts SET status='applied',evidence_path=?,"
                "evidence_sha256=?,receipt_json=?,finished_at=?,updated_at=? "
                "WHERE receipt_id=? AND status='started'",
                (evidence_path, digest, _json(receipt_json), now, now, receipt_id),
            )
            if cur.rowcount != 1:
                raise ConflictError("cleanup receipt was concurrently changed")
            cur = db.execute(
                "UPDATE tasks SET state='complete',terminal_reason=?,updated_at=? "
                "WHERE task_id=? AND state='cleaning'",
                (reason, now, receipt["task_id"]),
            )
            if cur.rowcount != 1:
                raise ConflictError("cleanup task was concurrently changed")

    def snapshot(
        self,
        supervisor_id: str,
        lease_id: str,
        generation: int,
        payload: Mapping[str, Any],
        config_version: int,
    ) -> int:
        raw = _json(payload)
        with self._db() as db, _transaction(db):
            now = _now()
            digest = hashlib.sha256(raw.encode()).hexdigest()
            cur = db.execute(
                "INSERT INTO status_snapshots(observed_at,supervisor_id,supervisor_lease_id,supervisor_generation,config_version,payload_json,payload_sha256) VALUES(?,?,?,?,?,?,?)",
                (now, supervisor_id, lease_id, generation, config_version, raw, digest),
            )
            if cur.lastrowid is None:
                raise CorruptionError("snapshot insert did not return an id")
            return int(cur.lastrowid)

    def status(self) -> dict[str, Any]:
        """Return a redacted, scheduler-owned observability snapshot."""
        return readonly_status(self.path)

    @staticmethod
    def _status_from(db: sqlite3.Connection, path: Path) -> dict[str, Any]:
        config = db.execute("SELECT * FROM current_runtime_config").fetchone()
        resource_policy = db.execute("SELECT * FROM current_resource_policy").fetchone()
        cutover = db.execute("SELECT * FROM cutover_barrier WHERE barrier_id=1").fetchone()
        counts = {
            str(row["state"]): int(row["count"])
            for row in db.execute("SELECT state,count(*) count FROM tasks GROUP BY state")
        }
        leases = [
            {
                "scope": row["scope"],
                "generation": row["generation"],
                "active": bool(row["active"]),
                "expires_at": row["lease_expires_at"],
            }
            for row in db.execute(
                "SELECT scope,generation,active,lease_expires_at FROM scheduler_leases ORDER BY scope,generation"
            )
        ]
        capacities = [
            dict(row)
            for row in db.execute(
                "SELECT * FROM capacity_rows ORDER BY capacity_unit,capacity_kind,capacity_key"
            )
        ]
        safe_config = dict(config) if config is not None else None
        if safe_config is not None:
            safe_config.pop("changed_by", None)
            safe_config.pop("reason", None)
        safe_policy = dict(resource_policy) if resource_policy is not None else None
        if safe_policy is not None:
            safe_policy.pop("changed_by", None)
            safe_policy.pop("reason", None)
        return {
            "schema_version": STATUS_SCHEMA_VERSION,
            "database": str(path.name),
            "event_id": int(
                db.execute("SELECT COALESCE(MAX(event_id),0) FROM events").fetchone()[0]
            ),
            "task_counts": counts,
            "wal": {
                "present": Path(str(path) + "-wal").is_file(),
                "size_bytes": Path(str(path) + "-wal").stat().st_size
                if Path(str(path) + "-wal").is_file()
                else 0,
            },
            "config": safe_config,
            "resource_policy": safe_policy,
            "cutover_barrier": dict(cutover) if cutover is not None else None,
            "leases": leases,
            "capacities": capacities,
        }


def readonly_status(path: Path | str) -> dict[str, Any]:
    """Observe one scheduler DB without constructing a write-capable facade."""
    database = Path(path)
    lock_path = database.parent / f".{database.name}.lock"
    lock_fd = os.open(lock_path, os.O_RDONLY | os.O_NOFOLLOW) if lock_path.exists() else None
    if lock_fd is not None:
        fcntl.flock(lock_fd, fcntl.LOCK_SH)
    uri = f"file:{database.resolve().as_posix()}?mode=ro"
    try:
        with sqlite3.connect(uri, uri=True, isolation_level=None) as db:
            db.row_factory = sqlite3.Row
            return Scheduler._status_from(db, database)
    finally:
        if lock_fd is not None:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
