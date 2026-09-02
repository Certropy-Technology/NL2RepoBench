#!/usr/bin/env python3
"""Import one validated discovery queue into an existing SQLite scheduler.

The command is intentionally an ingestion boundary, not a discovery runner.
It reads only caller-supplied JSON files, records their byte digests, and adds
one generated lane with fresh pending tasks.  Existing tasks, claims, actors,
and attempts are never updated or reset.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from nl2repobench.authoring.scheduler import Scheduler, ValidationError

MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_CANDIDATES = 256
MAX_RECORD_BYTES = 256 * 1024
MAX_MARKER_BYTES = 512
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
SAFE_PACKAGE = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*|@[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)$"
)
LANGUAGES = frozenset({"python", "node", "go"})
PLACEHOLDER = re.compile(r"(?:todo|tbd|dummy|placeholder|replace[-_ ]?me)", re.IGNORECASE)


class DiscoveryImportError(ValueError):
    """Raised when a discovery import cannot be proven safe and complete."""


def _bounded_marker(value: object, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value.encode("utf-8")) > MAX_MARKER_BYTES
        or SAFE_ID.fullmatch(value) is None
        or PLACEHOLDER.search(value) is not None
    ):
        raise DiscoveryImportError(f"{field} must be a bounded non-placeholder marker")
    return value


def _safe_input_path(root: Path, path: Path, field: str) -> tuple[Path, str]:
    root = root.resolve()
    if root.is_symlink() or not root.is_dir():
        raise DiscoveryImportError("--root must be an existing real directory")
    if path.is_absolute():
        candidate = path
    else:
        candidate = root / path
    candidate = candidate.absolute()
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise DiscoveryImportError(f"{field} must be inside --root") from exc
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise DiscoveryImportError(f"{field} has an unsafe relative path")
    cursor = candidate.parent
    while cursor != cursor.parent:
        if cursor.is_symlink():
            raise DiscoveryImportError(f"{field} parent contains a symlink")
        cursor = cursor.parent
    if candidate.is_symlink() or not candidate.is_file():
        raise DiscoveryImportError(f"{field} must be a regular non-symlink file")
    return candidate, relative.as_posix()


def _read_json(root: Path, path: Path, field: str) -> tuple[dict[str, Any], str, str]:
    candidate, relative = _safe_input_path(root, path, field)
    descriptor = -1
    try:
        descriptor = os.open(candidate, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise DiscoveryImportError(f"{field} must be a regular file")
        data = os.read(descriptor, MAX_INPUT_BYTES + 1)
    except DiscoveryImportError:
        raise
    except OSError as exc:
        raise DiscoveryImportError(f"cannot read {field}") from exc
    finally:
        if descriptor != -1:
            os.close(descriptor)
    if len(data) > MAX_INPUT_BYTES:
        raise DiscoveryImportError(f"{field} exceeds the input size limit")
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DiscoveryImportError(f"{field} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise DiscoveryImportError(f"{field} root must be an object")
    return value, relative, hashlib.sha256(data).hexdigest()


def _https_url(value: object) -> str:
    if not isinstance(value, str) or len(value.encode("utf-8")) > 2048:
        raise DiscoveryImportError("upstream_url must be a bounded HTTPS URL")
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or "\\" in value
    ):
        raise DiscoveryImportError(
            "upstream_url must be an HTTPS URL without credentials/query/fragment"
        )
    return value.rstrip("/")


def _identity_digest(package: str, upstream_url: str, revision: str) -> str:
    payload = json.dumps(
        {"package": package, "revision": revision, "upstream": upstream_url},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _candidate(raw: object, language: str, index: int) -> dict[str, str]:
    if not isinstance(raw, dict):
        raise DiscoveryImportError(f"queue[{index}] must be an object")
    encoded = json.dumps(raw, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    if len(encoded) > MAX_RECORD_BYTES:
        raise DiscoveryImportError(f"queue[{index}] exceeds the record size limit")
    required = ("candidate_id", "package", "language", "upstream_url", "revision")
    missing = [key for key in required if key not in raw]
    if missing:
        raise DiscoveryImportError(f"queue[{index}] is missing fields: {', '.join(missing)}")
    candidate_id = raw["candidate_id"]
    package = raw["package"]
    record_language = raw["language"]
    if not isinstance(candidate_id, str) or SAFE_ID.fullmatch(candidate_id) is None:
        raise DiscoveryImportError(f"queue[{index}].candidate_id is unsafe")
    if not isinstance(package, str) or SAFE_PACKAGE.fullmatch(package) is None:
        raise DiscoveryImportError(f"queue[{index}].package is unsafe")
    if record_language != language:
        raise DiscoveryImportError(f"queue[{index}].language does not match --language")
    upstream_url = _https_url(raw["upstream_url"])
    revision = raw["revision"]
    if not isinstance(revision, str) or HEX40.fullmatch(revision) is None:
        raise DiscoveryImportError(
            f"queue[{index}].revision must be a complete lowercase 40-char SHA"
        )
    status = raw.get("status", "candidate")
    if status != "candidate":
        raise DiscoveryImportError(f"queue[{index}].status must be candidate")
    source_kind = raw.get("source_kind", "discovery")
    if not isinstance(source_kind, str) or SAFE_ID.fullmatch(source_kind) is None:
        raise DiscoveryImportError(f"queue[{index}].source_kind is unsafe")
    return {
        "candidate_id": candidate_id,
        "package": package,
        "language": language,
        "upstream_url": upstream_url,
        "revision": revision,
        "source_kind": source_kind,
        "identity_digest": _identity_digest(package, upstream_url, revision),
    }


def _validate_plan(plan: dict[str, Any], batch_id: str, language: str) -> None:
    if plan.get("batch_id") != batch_id:
        raise DiscoveryImportError("plan.batch_id must match --batch-id")
    if plan.get("language") != language:
        raise DiscoveryImportError("plan.language must match --language")


def import_discovery(
    *,
    root: Path,
    db: Path,
    queue: Path,
    plan: Path,
    batch_id: str,
    language: str,
    authorization: str,
    owner: str,
    attempt_limit: int = 3,
    retry_limit: int = 3,
    release_limit: int = 3,
) -> dict[str, object]:
    """Validate and atomically add one generated discovery lane."""

    if language not in LANGUAGES:
        raise DiscoveryImportError("language must be exactly python, node, or go")
    if SAFE_ID.fullmatch(batch_id) is None:
        raise DiscoveryImportError("batch_id is unsafe")
    _bounded_marker(authorization, "authorization")
    _bounded_marker(owner, "owner")
    for value, field, upper in (
        (attempt_limit, "attempt_limit", 100),
        (retry_limit, "retry_limit", 100),
        (release_limit, "release_limit", 100),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= upper:
            raise DiscoveryImportError(f"{field} is out of bounds")
    if attempt_limit < 1:
        raise DiscoveryImportError("attempt_limit must be positive")
    root = root.resolve()
    database = db if db.is_absolute() else root / db
    database = database.absolute()
    if database.is_symlink() or not database.is_file() or database.stat().st_size == 0:
        raise DiscoveryImportError("--db must point to an existing initialized scheduler database")
    try:
        queue_data, queue_path, queue_sha256 = _read_json(root, queue, "queue")
        plan_data, plan_path, plan_sha256 = _read_json(root, plan, "plan")
    except DiscoveryImportError:
        raise
    _validate_plan(plan_data, batch_id, language)
    values = queue_data.get("queue")
    if not isinstance(values, list) or not values:
        raise DiscoveryImportError("queue.queue must be a non-empty array")
    if len(values) > MAX_CANDIDATES:
        raise DiscoveryImportError("queue contains too many candidates")
    candidates = [_candidate(value, language, index) for index, value in enumerate(values)]
    candidate_ids = [candidate["candidate_id"] for candidate in candidates]
    identity_digests = [candidate["identity_digest"] for candidate in candidates]
    if len(set(candidate_ids)) != len(candidate_ids):
        raise DiscoveryImportError("queue contains duplicate candidate_id values")
    if len(set(identity_digests)) != len(identity_digests):
        raise DiscoveryImportError("queue contains duplicate identity values")

    lane_id = f"generated-{language}-{batch_id}"
    if SAFE_ID.fullmatch(lane_id) is None:
        raise DiscoveryImportError("generated lane_id is unsafe or too long")
    source_reports = [
        f"queue:{queue_path}",
        f"plan:{plan_path}",
        f"queue_sha256:{queue_sha256}",
        f"plan_sha256:{plan_sha256}",
        f"authorization_sha256:{hashlib.sha256(authorization.encode()).hexdigest()}",
        f"owner_sha256:{hashlib.sha256(owner.encode()).hexdigest()}",
    ]
    scheduler = Scheduler(database, supplied_root=root)
    # init validates the stored schema but does not create a new DB here: the
    # existence check above prevents accidental creation of an unbound stage.
    scheduler.init()
    with scheduler.connect() as connection:
        barrier = connection.execute(
            "SELECT state,cutover_id FROM cutover_barrier WHERE barrier_id=1"
        ).fetchone()
        if barrier is None or barrier["state"] not in {"prepared", "sealed"}:
            raise DiscoveryImportError(
                "scheduler database requires a prepared or sealed cutover barrier"
            )
        if connection.execute(
            "SELECT 1 FROM lanes WHERE lane_id=? OR batch_id=?", (lane_id, batch_id)
        ).fetchone():
            raise DiscoveryImportError("batch_id or generated lane already exists")
        placeholders = ",".join("?" for _ in candidate_ids)
        if connection.execute(
            f"SELECT candidate_id FROM candidates WHERE candidate_id IN ({placeholders}) LIMIT 1",
            candidate_ids,
        ).fetchone():
            raise DiscoveryImportError("candidate_id already exists in scheduler")
        if connection.execute(
            "SELECT identity_digest FROM candidate_identities "
            f"WHERE identity_digest IN ({placeholders}) LIMIT 1",
            identity_digests,
        ).fetchone():
            raise DiscoveryImportError("candidate identity already exists in scheduler")
        if any(
            connection.execute(
                "SELECT 1 FROM tasks WHERE task_id=?",
                (f"{lane_id}:{candidate['candidate_id']}:discovery",),
            ).fetchone()
            for candidate in candidates
        ):
            raise DiscoveryImportError("discovery task already exists in scheduler")
        now = (
            __import__("datetime")
            .datetime.now(__import__("datetime").UTC)
            .isoformat(timespec="microseconds")
        )
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT INTO lanes("
                "lane_id,batch_id,language,kind,status,queue_path,queue_sha256,"
                "plan_path,plan_sha256,state_path,state_sha256,source_reports_json,"
                "fairness_rank,last_dispatch_seq,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    lane_id,
                    batch_id,
                    language,
                    "generated",
                    "active",
                    queue_path,
                    queue_sha256,
                    plan_path,
                    plan_sha256,
                    None,
                    None,
                    json.dumps(
                        source_reports, ensure_ascii=True, sort_keys=True, separators=(",", ":")
                    ),
                    0,
                    0,
                    now,
                    now,
                ),
            )
            for ordinal, candidate in enumerate(candidates):
                selection = {
                    "candidate_id": candidate["candidate_id"],
                    "package": candidate["package"],
                    "language": language,
                    "source_kind": candidate["source_kind"],
                    "upstream_url": candidate["upstream_url"],
                    "revision": candidate["revision"],
                    "status": "candidate",
                }
                connection.execute(
                    "INSERT INTO candidate_identities("
                    "identity_digest,language,package,upstream_url,source_kind,"
                    "revision,canonical_json,created_at) VALUES(?,?,?,?,?,?,?,?)",
                    (
                        candidate["identity_digest"],
                        language,
                        candidate["package"],
                        candidate["upstream_url"],
                        candidate["source_kind"],
                        candidate["revision"],
                        json.dumps(
                            selection, ensure_ascii=True, sort_keys=True, separators=(",", ":")
                        ),
                        now,
                    ),
                )
                connection.execute(
                    "INSERT INTO candidates("
                    "candidate_id,lane_id,identity_digest,input_ordinal,"
                    "discovered_status,selection_json,created_at,updated_at) "
                    "VALUES(?,?,?,?,?,?,?,?)",
                    (
                        candidate["candidate_id"],
                        lane_id,
                        candidate["identity_digest"],
                        ordinal,
                        "candidate",
                        json.dumps(
                            selection, ensure_ascii=True, sort_keys=True, separators=(",", ":")
                        ),
                        now,
                        now,
                    ),
                )
                task_id = f"{lane_id}:{candidate['candidate_id']}:discovery"
                connection.execute(
                    "INSERT INTO tasks("
                    "task_id,candidate_id,lane_id,task_release,state,attempt_limit,"
                    "authoring_attempts,retry_limit,retry_count,release_count,"
                    "release_limit,input_ordinal,created_at,updated_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        task_id,
                        candidate["candidate_id"],
                        lane_id,
                        "discovery",
                        "pending",
                        attempt_limit,
                        0,
                        retry_limit,
                        0,
                        0,
                        release_limit,
                        ordinal,
                        now,
                        now,
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return {
        "schema_version": "1.0",
        "status": "imported",
        "database": str(database),
        "cutover_id": str(barrier["cutover_id"]),
        "lane_id": lane_id,
        "batch_id": batch_id,
        "language": language,
        "candidate_count": len(candidates),
        "queue_path": queue_path,
        "queue_sha256": queue_sha256,
        "plan_path": plan_path,
        "plan_sha256": plan_sha256,
        "task_release": "discovery",
        "attempts_initialized": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--language", choices=sorted(LANGUAGES), required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--attempt-limit", type=int, default=3)
    parser.add_argument("--retry-limit", type=int, default=3)
    parser.add_argument("--release-limit", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        result = import_discovery(
            root=args.root,
            db=args.db,
            queue=args.queue,
            plan=args.plan,
            batch_id=args.batch_id,
            language=args.language,
            authorization=args.authorization,
            owner=args.owner,
            attempt_limit=args.attempt_limit,
            retry_limit=args.retry_limit,
            release_limit=args.release_limit,
        )
    except (DiscoveryImportError, ValidationError, OSError, ValueError) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["DiscoveryImportError", "import_discovery", "main"]
