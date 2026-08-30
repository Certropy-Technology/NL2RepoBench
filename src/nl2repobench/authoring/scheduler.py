# ruff: noqa: E501
"""Typed, process-safe SQLite primitives for authoring scheduling.

This module is intentionally a library boundary.  External effects belong to
the Phase 2 workers; all methods here are short ``BEGIN IMMEDIATE`` changes.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import uuid
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
LANGUAGES = ("python", "node", "go")


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
                    raise BusyError("sqlite write transaction is busy") from exc
                time.sleep(0.02)
        yield db
    except sqlite3.OperationalError as exc:
        if "busy" in str(exc).lower() or "locked" in str(exc).lower():
            raise BusyError("sqlite operation is busy") from exc
        raise
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()


class Scheduler:
    """A narrowly typed facade over one local scheduler database."""

    def __init__(self, path: Path | str, *, supplied_root: Path | str | None = None) -> None:
        self.path = Path(path).expanduser()
        if supplied_root is None:
            raise ValidationError("supplied_root is required in Phase 1")
        root = Path(supplied_root).expanduser().resolve()
        resolved = self.path.resolve()
        if root != resolved and root not in resolved.parents:
            raise ValidationError("database must be under supplied root")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
        db.row_factory = sqlite3.Row
        for pragma in (
            "PRAGMA journal_mode=WAL",
            "PRAGMA synchronous=FULL",
            "PRAGMA busy_timeout=5000",
            "PRAGMA foreign_keys=ON",
            "PRAGMA temp_store=MEMORY",
            "PRAGMA wal_autocheckpoint=1000",
            "PRAGMA journal_size_limit=67108864",
            "PRAGMA trusted_schema=OFF",
        ):
            db.execute(pragma)
        return db

    def init(self) -> None:
        schema = Path(__file__).with_name("scheduler_schema.sql").read_text(encoding="utf-8")
        with self.connect() as db:
            db.executescript(schema)
            with _transaction(db):
                now = _now()
                db.execute("INSERT OR IGNORE INTO fairness_state VALUES (1,0,0,?)", (now,))
                db.execute("INSERT OR IGNORE INTO schema_meta VALUES ('schema_version','2')")

    def _db(self) -> sqlite3.Connection:
        return self.connect()

    def configure(
        self,
        *,
        enabled: bool,
        lease_seconds: int = 7200,
        heartbeat_interval_seconds: int = 600,
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
        with self._db() as db, _transaction(db):
            cur = db.execute(
                "INSERT INTO runtime_config(enabled,lease_seconds,heartbeat_interval_seconds,changed_by,changed_at,reason) VALUES(?,?,?,?,?,?)",
                (
                    int(enabled),
                    lease_seconds,
                    heartbeat_interval_seconds,
                    changed_by,
                    _now(),
                    reason,
                ),
            )
            if cur.lastrowid is None:
                raise CorruptionError("configuration insert did not return an id")
            return int(cur.lastrowid)

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
            db.execute(
                "INSERT OR REPLACE INTO capacity_rows VALUES(?,?,?,?,?,?,?,?)",
                (unit, kind, key, limit, used, limit - used, None, _now()),
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
    ) -> None:
        _id(controller_id, "controller_id")
        _id(owner_uuid, "owner_uuid")
        _id(lane_id, "lane_id")
        if language not in LANGUAGES or slot < 0 or pid <= 0 or process_starttime_ticks < 0:
            raise ValidationError("invalid controller identity")
        _digest(executable_digest)
        _digest(argv_digest)
        with self._db() as db, _transaction(db):
            now = _now()
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
            for row in rows:
                cur = db.execute(
                    "UPDATE controller_slot_reservations SET state='expired',updated_at=? WHERE reservation_id=? AND state='reserved'",
                    (moment, row["reservation_id"]),
                )
                if cur.rowcount != 1:
                    continue
                for kind, key in (("global", "controllers"), ("language", row["language"])):
                    db.execute(
                        "UPDATE capacity_rows SET used_count=used_count-1,remaining_count=remaining_count+1,updated_at=? WHERE capacity_unit='controller_slot' AND capacity_kind=? AND capacity_key=? AND used_count>0",
                        (moment, kind, key),
                    )
            return len(rows)

    def acquire_singleton(
        self, scope: str, controller_id: str, owner_uuid: str, *, lease_seconds: int = 7200
    ) -> tuple[str, int]:
        if (
            scope not in {"supervisor", "watcher", "integration", "archive"}
            or not 5 <= lease_seconds <= 86400
        ):
            raise ValidationError("invalid singleton lease")
        with self._db() as db, _transaction(db):
            now = _now()
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
            actor = db.execute(
                "SELECT 1 FROM controllers WHERE controller_id=? AND owner_uuid=? AND role=? AND state='running'",
                (controller_id, owner_uuid, scope),
            ).fetchone()
            if actor is None:
                raise LostLeaseError("actor identity fence failed")
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
        self, lease_id: str, scope: str, controller_id: str, owner_uuid: str,
        generation: int, *, lease_seconds: int = 7200,
    ) -> None:
        if scope not in {"supervisor", "watcher", "integration", "archive"}:
            raise ValidationError("invalid singleton scope")
        with self._db() as db, _transaction(db):
            now = _now()
            cur = db.execute(
                "UPDATE scheduler_leases SET heartbeat_at=?,lease_expires_at=?,updated_at=? "
                "WHERE lease_id=? AND scope=? AND controller_id=? AND owner_uuid=? "
                "AND generation=? AND active=1 AND lease_expires_at>?",
                (now, _future(lease_seconds), now, lease_id, scope, controller_id,
                 owner_uuid, generation, now),
            )
            if cur.rowcount != 1:
                raise LostLeaseError("singleton lease is lost or expired")

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
                "SELECT t.* FROM tasks t JOIN candidates c ON c.candidate_id=t.candidate_id AND c.lane_id=t.lane_id JOIN candidate_identities i ON i.identity_digest=c.identity_digest WHERE t.state='pending' AND t.lane_id=? AND i.language=? AND (t.next_retry_at IS NULL OR t.next_retry_at<=?) AND t.authoring_attempts<t.attempt_limit AND t.release_count<t.release_limit ORDER BY CASE WHEN t.priority_until IS NOT NULL AND t.priority_until>? THEN 0 ELSE 1 END,t.priority_until DESC,t.input_ordinal,t.updated_at,t.task_id LIMIT ?",
                (controller["lane_id"], controller["language"], now, now, limit),
            ).fetchall()
            result: list[Claim] = []
            for task in selected:
                db.execute(
                    "UPDATE tasks SET state='claimed',authoring_attempts=authoring_attempts+1,updated_at=? WHERE task_id=? AND state='pending'",
                    (now, task["task_id"]),
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
                        1,
                        1,
                        now,
                        now,
                    ),
                )
                for row in rows:
                    db.execute(
                        "UPDATE capacity_rows SET used_count=used_count+1,remaining_count=remaining_count-1,updated_at=? WHERE capacity_unit=? AND capacity_kind=? AND capacity_key=? AND remaining_count>0",
                        (now, row["capacity_unit"], row["capacity_kind"], row["capacity_key"]),
                    )
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
                    )
                )
            return result

    def transition(self, task_id: str, state: str, *, reason: str | None = None) -> None:
        _id(task_id, "task_id")
        valid_states = {
            "pending", "claimed", "preparing", "authoring", "handoff_ready", "stale",
            "integrating", "integration_retry", "archiving", "archive_retry", "cleaning",
            "cleanup_retry", "complete", "blocked", "excluded", "cancelled",
        }
        if state not in valid_states:
            raise ValidationError("invalid task state")
        with self._db() as db, _transaction(db):
            if state in {"blocked", "excluded", "cancelled"} and not reason:
                raise ValidationError("terminal reason required")
            cur = db.execute(
                "UPDATE tasks SET state=?,terminal_reason=COALESCE(?,terminal_reason),updated_at=? WHERE task_id=?",
                (state, reason, _now(), task_id),
            )
            if cur.rowcount != 1:
                raise ConflictError("unknown task or invalid transition")

    def prepare(self, claim_id: str, owner_uuid: str, controller_id: str) -> None:
        with self._db() as db, _transaction(db):
            row = db.execute(
                "SELECT * FROM claims WHERE claim_id=? AND owner_uuid=? AND controller_id=? AND active=1",
                (claim_id, owner_uuid, controller_id),
            ).fetchone()
            if row is None:
                raise LostLeaseError("claim is not active")
            now = _now()
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

    def start(self, claim_id: str, owner_uuid: str, controller_id: str) -> None:
        """Commit the Popen-adjacent launch state immediately before spawning."""
        with self._db() as db, _transaction(db):
            row = db.execute(
                "SELECT * FROM claims WHERE claim_id=? AND owner_uuid=? AND controller_id=? AND active=1",
                (claim_id, owner_uuid, controller_id),
            ).fetchone()
            if row is None:
                raise LostLeaseError("claim is not active")
            now = _now()
            cur = db.execute(
                "UPDATE tasks SET state='authoring',updated_at=? WHERE task_id=? AND state='preparing'",
                (now, row["task_id"]),
            )
            if cur.rowcount != 1:
                raise ConflictError("task is not prepared")
            cur = db.execute(
                "UPDATE trials SET state='running',started_at=?,updated_at=? WHERE trial_id=? AND state='created' AND launch_intent_at IS NOT NULL",
                (now, now, row["trial_id"]),
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
    ) -> None:
        moment = now or _now()
        with self._db() as db, _transaction(db):
            row = db.execute(
                "SELECT c.lease_seconds FROM claims c WHERE claim_id=? AND owner_uuid=? AND controller_id=? AND generation=? AND active=1 AND lease_expires_at>?",
                (claim_id, owner_uuid, controller_id, generation, moment),
            ).fetchone()
            if row is None:
                raise LostLeaseError("claim lease is lost or expired")
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
        self, claim_id: str, owner_uuid: str, controller_id: str, *, reason: str = "released"
    ) -> None:
        with self._db() as db, _transaction(db):
            row = db.execute(
                "SELECT * FROM claims WHERE claim_id=? AND owner_uuid=? AND controller_id=? AND active=1",
                (claim_id, owner_uuid, controller_id),
            ).fetchone()
            if row is None:
                raise LostLeaseError("claim is not active")
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
                "UPDATE tasks SET state='pending',release_count=release_count+1,updated_at=? WHERE task_id=?",
                (now, row["task_id"]),
            )
            self._decrement(db, row["controller_id"], row["task_id"], now)

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
            db.execute(
                "UPDATE capacity_rows SET used_count=used_count-1,remaining_count=remaining_count+1,updated_at=? WHERE capacity_unit='active_claim' AND capacity_kind=? AND capacity_key=? AND used_count>0",
                (now, kind, key),
            )

    def finish(
        self,
        claim_id: str,
        owner_uuid: str,
        controller_id: str,
        *,
        success: bool,
        reason: str = "finished",
    ) -> None:
        with self._db() as db, _transaction(db):
            row = db.execute(
                "SELECT * FROM claims WHERE claim_id=? AND owner_uuid=? AND controller_id=? AND active=1",
                (claim_id, owner_uuid, controller_id),
            ).fetchone()
            if row is None:
                raise LostLeaseError("claim is not active")
            now = _now()
            db.execute(
                "UPDATE claims SET active=0,released_at=?,release_reason=?,updated_at=? WHERE claim_id=? AND active=1",
                (now, now, reason, claim_id),
            )
            db.execute(
                "UPDATE trials SET state=?,finished_at=?,updated_at=? WHERE trial_id=? AND state='running'",
                ("succeeded" if success else "failed", now, now, row["trial_id"]),
            )
            db.execute(
                "UPDATE tasks SET state=?,terminal_reason=?,last_failure_reason=?,updated_at=? "
                "WHERE task_id=?",
                (
                    "handoff_ready" if success else "blocked",
                    None if success else reason,
                    None if success else reason,
                    now,
                    row["task_id"],
                ),
            )
            self._decrement(db, controller_id, row["task_id"], now)

    def begin_receipt(
        self, task_id: str, kind: str, attempt: int, retry_no: int, idempotency_key: str
    ) -> str:
        _id(task_id, "task_id")
        _id(idempotency_key, "idempotency_key")
        if kind not in {"integration", "archive", "cleanup"} or attempt < 1 or retry_no < 0:
            raise ValidationError("invalid operation receipt")
        with self._db() as db, _transaction(db):
            old = db.execute(
                "SELECT receipt_id FROM operation_receipts WHERE idempotency_key=?",
                (idempotency_key,),
            ).fetchone()
            if old:
                return str(old[0])
            receipt = str(uuid.uuid4())
            now = _now()
            db.execute(
                "INSERT INTO operation_receipts(receipt_id,task_id,operation_kind,operation_attempt,retry_no,idempotency_key,status,started_at,created_at,updated_at) VALUES(?,?,?,?,?,?,?, ?,?,?)",
                (
                    receipt,
                    task_id,
                    kind,
                    attempt,
                    retry_no,
                    idempotency_key,
                    "started",
                    now,
                    now,
                    now,
                ),
            )
            return receipt

    def begin_operation(self, task_id: str, kind: str, idempotency_key: str) -> str:
        """Persist an operation intent and move only its matching stage forward.

        Authoring claims select only ``pending`` tasks, therefore all operation
        retry states are structurally excluded from reauthoring.
        """
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
            existing = db.execute(
                "SELECT receipt_id FROM operation_receipts WHERE idempotency_key=?",
                (idempotency_key,),
            ).fetchone()
            if existing is not None:
                return str(existing[0])
            task = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if task is None or task["state"] not in accepted:
                raise ConflictError("task is not ready for this operation")
            now = _now()
            attempt = int(task[attempt_col]) + 1
            retry = int(task[retry_col])
            db.execute(
                f"UPDATE tasks SET state=?,{attempt_col}=?,updated_at=? WHERE task_id=?",
                (next_state, attempt, now, task_id),
            )
            receipt = str(uuid.uuid4())
            db.execute(
                "INSERT INTO operation_receipts(receipt_id,task_id,operation_kind,operation_attempt,retry_no,idempotency_key,status,started_at,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (receipt, task_id, kind, attempt, retry, idempotency_key, "started", now, now, now),
            )
            return receipt

    def fail_operation(self, receipt_id: str, failure_class: str, reason: str) -> None:
        """Record a failure; only infrastructure failures enter the same-stage retry state."""
        if (
            failure_class
            not in {"source", "spec", "environment", "verifier", "model", "infrastructure"}
            or not reason
        ):
            raise ValidationError("invalid operation failure")
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
            db.execute(
                "UPDATE operation_receipts SET status='failed',failure_class=?,failure_reason=?,finished_at=?,updated_at=? WHERE receipt_id=?",
                (failure_class, reason, now, now, receipt_id),
            )
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
                    "UPDATE trials SET state='stale',finished_at=?,failure_class='infrastructure',failure_reason='lease expired',updated_at=? WHERE trial_id=? AND state IN ('created','running')",
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

    def update_receipt(self, receipt_id: str, status: str, **fields: Any) -> None:
        _id(receipt_id, "receipt_id")
        if status not in {"committed", "pushed", "verified", "applied", "failed", "collision"}:
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
            "failure_class",
            "failure_reason",
            "receipt_json",
        }
        if set(fields) - allowed:
            raise ValidationError("unknown receipt field")
        with self._db() as db, _transaction(db):
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
