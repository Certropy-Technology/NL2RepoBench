#!/usr/bin/env python3
"""Phase 1 command adapter for the typed SQLite authoring scheduler.

It refuses production-like implicit paths: callers must pass both ``--root``
and a database path contained by that root.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nl2repobench.authoring.scheduler import (
    BusyError,
    ConflictError,
    CorruptionError,
    Scheduler,
    SchedulerError,
    ValidationError,
)


def _output(command: str, data: dict[str, Any], error: str | None = None) -> None:
    print(
        json.dumps(
            {
                "schema_version": "authoring-scheduler/v2",
                "command": command,
                "observed_at": datetime.now(UTC).isoformat(),
                "data": data,
                "error": error,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, required=True, help="explicit temporary Phase 1 root")
    result.add_argument("--db", type=Path, required=True, help="database contained by --root")
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    config = sub.add_parser("config-set")
    config.add_argument("--enabled", choices=("true", "false"), required=True)
    config.add_argument("--lease-seconds", type=int, default=7200)
    config.add_argument("--heartbeat-seconds", type=int, default=600)
    sub.add_parser("status")
    claim = sub.add_parser("claim")
    claim.add_argument("--controller", required=True)
    claim.add_argument("--owner", required=True)
    claim.add_argument("--limit", type=int, default=1)
    heartbeat = sub.add_parser("heartbeat")
    heartbeat.add_argument("--claim", required=True)
    heartbeat.add_argument("--controller", required=True)
    heartbeat.add_argument("--owner", required=True)
    release = sub.add_parser("release")
    release.add_argument("--claim", required=True)
    release.add_argument("--controller", required=True)
    release.add_argument("--owner", required=True)
    release.add_argument("--reason", default="released")
    finish = sub.add_parser("finish")
    finish.add_argument("--claim", required=True)
    finish.add_argument("--controller", required=True)
    finish.add_argument("--owner", required=True)
    finish.add_argument("--success", choices=("true", "false"), required=True)
    finish.add_argument("--reason", default="finished")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        scheduler = Scheduler(args.db, supplied_root=args.root)
        if args.command == "init":
            scheduler.init()
            _output("init", {"db": str(args.db)})
            return 0
        if args.command == "config-set":
            version = scheduler.configure(
                enabled=args.enabled == "true",
                lease_seconds=args.lease_seconds,
                heartbeat_interval_seconds=args.heartbeat_seconds,
            )
            _output("config-set", {"config_version": version})
            return 0
        if args.command == "claim":
            claims = scheduler.claim_next(args.controller, args.owner, requested_limit=args.limit)
            _output("claim", {"claims": [claim.__dict__ for claim in claims]})
            return 0 if claims else 2
        if args.command == "heartbeat":
            scheduler.heartbeat(args.claim, args.owner, args.controller)
            _output("heartbeat", {"claim_id": args.claim})
            return 0
        if args.command == "release":
            scheduler.release(args.claim, args.owner, args.controller, reason=args.reason)
            _output("release", {"claim_id": args.claim})
            return 0
        if args.command == "finish":
            scheduler.finish(args.claim, args.owner, args.controller,
                             success=args.success == "true", reason=args.reason)
            _output("finish", {"claim_id": args.claim})
            return 0
        with scheduler.connect() as db:
            counts = {
                str(row["state"]): int(row["count"])
                for row in db.execute("SELECT state,count(*) count FROM tasks GROUP BY state")
            }
            _output(
                "status",
                {
                    "task_counts": counts,
                    "last_event_id": int(
                        db.execute("SELECT COALESCE(MAX(event_id),0) FROM events").fetchone()[0]
                    ),
                },
            )
        return 0
    except ValidationError as exc:
        _output(args.command, {}, str(exc))
        return 2
    except ConflictError as exc:
        _output(args.command, {}, str(exc))
        return 3
    except BusyError as exc:
        _output(args.command, {}, str(exc))
        return 4
    except CorruptionError as exc:
        _output(args.command, {}, str(exc))
        return 5
    except SchedulerError as exc:
        _output(args.command, {}, str(exc))
        return 5
    except sqlite3.Error:
        _output(args.command, {}, "scheduler database error")
        return 5


if __name__ == "__main__":
    sys.exit(main())
