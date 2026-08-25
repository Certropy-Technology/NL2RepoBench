#!/usr/bin/env python3
"""Process-safe claim/record loop for independent Package authoring items."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import sys
import tempfile
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

TERMINAL = frozenset({"complete", "blocked", "excluded"})
ACTIVE = frozenset({"pending", "running"})


def now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_queue(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid package queue {path}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("queue"), list):
        raise ValueError("package queue must contain a queue list")
    return payload


def _default_record(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": candidate["candidate_id"],
        "package": candidate["package"],
        "language": candidate["language"],
        "status": "pending",
        "owner": None,
        "lease_expires_at": None,
        "attempts": 0,
        "reason": None,
        "failure_class": None,
        "artifacts": [],
        "updated_at": now(),
    }


@contextlib.contextmanager
def locked_state(path: Path) -> Iterator[dict[str, Any]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state: dict[str, Any]
        if path.is_file():
            state = json.loads(path.read_text(encoding="utf-8"))
        else:
            state = {"schema_version": "1.0", "queue_sha256": None, "items": {}}
        yield state
        state["updated_at"] = now()
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, sort_keys=True, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        fcntl.flock(lock, fcntl.LOCK_UN)


def sync_queue(state: dict[str, Any], queue_path: Path) -> dict[str, Any]:
    queue = _load_queue(queue_path)
    queue_digest = _sha256(queue_path)
    previous_digest = state.get("queue_sha256")
    if previous_digest and previous_digest != queue_digest:
        raise ValueError(
            f"queue changed from {previous_digest} to {queue_digest}; "
            "start a new state file or explicitly reconcile the queue"
        )
    state["queue_sha256"] = queue_digest
    items = state.setdefault("items", {})
    if not isinstance(items, dict):
        raise ValueError("state.items must be an object")
    for candidate in queue["queue"]:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("candidate_id"), str):
            raise ValueError("every queue item requires candidate_id")
        candidate_id = candidate["candidate_id"]
        record = items.setdefault(candidate_id, _default_record(candidate))
        if record.get("package") != candidate.get("package"):
            raise ValueError(f"candidate identity changed: {candidate_id}")
        record["selection"] = {
            "upstream_url": candidate.get("upstream_url"),
            "source_kind": candidate.get("source_kind"),
            "revision": candidate.get("revision"),
        }
    return items


def lease_expired(record: dict[str, Any]) -> bool:
    expires = record.get("lease_expires_at")
    if not isinstance(expires, str):
        return True
    return datetime.fromisoformat(expires) <= datetime.now(UTC)


def command_init(args: argparse.Namespace) -> int:
    with locked_state(args.state) as state:
        sync_queue(state, args.queue)
    print(json.dumps({"state": str(args.state), "queue_sha256": state["queue_sha256"]}))
    return 0


def command_status(args: argparse.Namespace) -> int:
    with locked_state(args.state) as state:
        items = sync_queue(state, args.queue)
        counts: dict[str, int] = {}
        for record in items.values():
            status = str(record.get("status"))
            counts[status] = counts.get(status, 0) + 1
        output = {
            "state": str(args.state),
            "queue_sha256": state["queue_sha256"],
            "total": len(items),
            "counts": dict(sorted(counts.items())),
            "remaining": sorted(
                candidate_id
                for candidate_id, record in items.items()
                if record.get("status") not in TERMINAL
            ),
        }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def _authorized_reclaim_statuses(
    plan_path: Path | None,
    *,
    queue_path: Path,
    candidate_id: str,
) -> set[str]:
    if plan_path is None:
        return set()
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid remediation plan {plan_path}: {exc}") from exc
    if not isinstance(plan, dict) or plan.get("remediation_mode") is not True:
        raise ValueError("terminal reclaim requires a remediation plan")
    if plan.get("candidate_input_sha256") != _sha256(queue_path):
        raise ValueError("remediation plan is not bound to this queue")
    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("remediation plan tasks must be an array")
    matches = [
        task
        for task in tasks
        if isinstance(task, dict) and task.get("candidate_id") == candidate_id
    ]
    if len(matches) != 1:
        raise ValueError(f"remediation plan does not authorize {candidate_id}")
    raw_statuses = matches[0].get("queue_reclaim_statuses")
    if not isinstance(raw_statuses, list):
        raise ValueError("remediation task must declare queue_reclaim_statuses")
    statuses = set(raw_statuses)
    if statuses - {"blocked", "complete"}:
        raise ValueError("remediation plan may reclaim only blocked or complete")
    return statuses


def command_claim(args: argparse.Namespace) -> int:
    if args.limit < 1 or args.lease_seconds < 1 or args.max_attempts < 1:
        raise ValueError("claim limits, lease-seconds, and max-attempts must be positive")
    candidate_filter = getattr(args, "candidate_id", None)
    plan_path = getattr(args, "remediation_plan", None)
    reclaim_statuses: set[str] = set()
    if plan_path is not None:
        if not isinstance(candidate_filter, list) or len(candidate_filter) != 1 or args.limit != 1:
            raise ValueError("remediation claim requires exactly one candidate-id and limit=1")
        reclaim_statuses = _authorized_reclaim_statuses(
            Path(plan_path),
            queue_path=args.queue,
            candidate_id=candidate_filter[0],
        )
    with locked_state(args.state) as state:
        items = sync_queue(state, args.queue)
        selected: list[dict[str, Any]] = []
        for candidate_id in sorted(items):
            if len(selected) >= args.limit:
                break
            record = items[candidate_id]
            if candidate_filter and candidate_id not in candidate_filter:
                continue
            if args.language and record.get("language") != args.language:
                continue
            current_status = str(record.get("status"))
            if current_status in reclaim_statuses:
                record["reopen_history"] = [
                    *record.get("reopen_history", []),
                    {
                        "status": current_status,
                        "reason": record.get("reason"),
                        "failure_class": record.get("failure_class"),
                        "artifacts": list(record.get("artifacts", [])),
                        "attempts": int(record.get("attempts", 0)),
                        "recorded_at": record.get("updated_at"),
                        "reopened_at": now(),
                        "reopened_by": args.owner,
                    },
                ]
                record.update(
                    {
                        "status": "pending",
                        "owner": None,
                        "lease_expires_at": None,
                        "attempts": 0,
                        "reason": None,
                        "failure_class": None,
                        "artifacts": [],
                        "release_reason": None,
                        "updated_at": now(),
                    }
                )
            if record.get("status") == "running":
                if not lease_expired(record):
                    continue
                if int(record.get("attempts", 0)) >= args.max_attempts:
                    record.update(
                        {
                            "status": "blocked",
                            "owner": None,
                            "lease_expires_at": None,
                            "reason": "lease expired at retry limit",
                            "failure_class": "infrastructure",
                            "updated_at": now(),
                        }
                    )
                    continue
                record["status"] = "pending"
                record["retry_history"] = [
                    *record.get("retry_history", []),
                    {
                        "failure_class": "infrastructure",
                        "reason": "lease expired before handoff",
                        "recorded_at": now(),
                    },
                ]
            if int(record.get("attempts", 0)) >= args.max_attempts:
                continue
            if record.get("status") not in ACTIVE:
                continue
            record.update(
                {
                    "status": "running",
                    "owner": args.owner,
                    "lease_expires_at": (
                        datetime.now(UTC) + timedelta(seconds=args.lease_seconds)
                    ).isoformat(),
                    "attempts": int(record.get("attempts", 0)) + 1,
                    "updated_at": now(),
                }
            )
            selected.append(dict(record))
    print(json.dumps({"claimed": selected}, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if selected else 2


def command_record(args: argparse.Namespace) -> int:
    if args.status not in TERMINAL:
        raise ValueError("record status must be complete, blocked, or excluded")
    if args.status != "complete" and not args.reason:
        raise ValueError("blocked/excluded records require a reason")
    if args.failure_class and args.failure_class not in {
        "source",
        "spec",
        "environment",
        "verifier",
        "model",
        "infrastructure",
    }:
        raise ValueError(f"invalid failure class: {args.failure_class}")
    with locked_state(args.state) as state:
        items = sync_queue(state, args.queue)
        record = items.get(args.candidate_id)
        if record is None:
            raise ValueError(f"unknown candidate: {args.candidate_id}")
        if record.get("owner") != args.owner or record.get("status") != "running":
            raise ValueError(f"{args.candidate_id} is not claimed by {args.owner}")
        if lease_expired(record):
            raise ValueError(f"claim lease expired for {args.candidate_id}")
        record.update(
            {
                "status": args.status,
                "owner": None,
                "lease_expires_at": None,
                "reason": args.reason,
                "failure_class": args.failure_class,
                "artifacts": args.artifact,
                "updated_at": now(),
            }
        )
        output = dict(record)
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def command_release(args: argparse.Namespace) -> int:
    """Return a claim to pending without consuming an attempt."""

    with locked_state(args.state) as state:
        items = sync_queue(state, args.queue)
        record = items.get(args.candidate_id)
        if record is None:
            raise ValueError(f"unknown candidate: {args.candidate_id}")
        if record.get("owner") != args.owner or record.get("status") != "running":
            raise ValueError(f"{args.candidate_id} is not claimed by {args.owner}")
        if lease_expired(record):
            raise ValueError(f"claim lease expired for {args.candidate_id}")
        record.update(
            {
                "status": "pending",
                "owner": None,
                "lease_expires_at": None,
                "release_reason": args.reason,
                "updated_at": now(),
            }
        )
    print(json.dumps({"released": args.candidate_id, "reason": args.reason}, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("init", "status", "claim", "record", "release"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--queue", type=Path, required=True)
        sub.add_argument("--state", type=Path, default=Path(".nl2repo/package-queue/state.json"))
        if name == "claim":
            sub.add_argument("--owner", required=True)
            sub.add_argument("--limit", type=int, default=1)
            sub.add_argument("--lease-seconds", type=int, default=7200)
            sub.add_argument("--max-attempts", type=int, default=3)
            sub.add_argument("--language", choices=("python", "node", "go"))
            sub.add_argument(
                "--candidate-id",
                action="append",
                help="Claim only the named candidate; repeatable.",
            )
        elif name in {"record", "release"}:
            sub.add_argument("candidate_id")
            sub.add_argument("--owner", required=True)
        if name == "release":
            sub.add_argument("--reason", required=True)
            continue
        if name == "record":
            sub.add_argument("--status", required=True, choices=sorted(TERMINAL))
            sub.add_argument("--reason")
            sub.add_argument("--failure-class")
            sub.add_argument("--artifact", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return {
            "init": command_init,
            "status": command_status,
            "claim": command_claim,
            "record": command_record,
            "release": command_release,
        }[args.command](args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"package queue failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
