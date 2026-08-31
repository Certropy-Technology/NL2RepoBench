#!/usr/bin/env python3
"""Phase 1 command adapter for the typed SQLite authoring scheduler.

It refuses production-like implicit paths: callers must pass both ``--root``
and a database path contained by that root.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nl2repobench.authoring.backup import backup_database, restore_database, verify_backup
from nl2repobench.authoring.migration import validate_manifest
from nl2repobench.authoring.scheduler import (
    BusyError,
    ConflictError,
    CorruptionError,
    Scheduler,
    SchedulerError,
    ValidationError,
    readonly_status,
)


def _output(command: str, data: dict[str, Any], error: str | None = None) -> None:
    print(
        json.dumps(
            {
                "schema_version": "authoring-scheduler/v3",
                "command": command,
                "observed_at": datetime.now(UTC).isoformat(),
                "data": data,
                "error": error,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )


def _process_identity(
    pid: int | None, starttime: int | None, boot_id: str | None
) -> tuple[int, int, str]:
    actual_pid = pid if pid is not None else os.getpid()
    if starttime is None:
        stat = Path(f"/proc/{actual_pid}/stat").read_text(encoding="utf-8")
        starttime = int(stat.rsplit(")", 1)[1].split()[19])
    actual_boot = boot_id or Path("/proc/sys/kernel/random/boot_id").read_text(
        encoding="utf-8"
    ).strip()
    if not actual_boot:
        raise ValidationError("boot id is empty")
    return actual_pid, starttime, actual_boot


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, required=True, help="explicit scheduler root")
    result.add_argument("--db", type=Path, required=True, help="database contained by --root")
    result.add_argument("--pid", type=int)
    result.add_argument("--starttime-ticks", type=int)
    result.add_argument("--boot-id")
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    config = sub.add_parser("config-set")
    config.add_argument("--enabled", choices=("true", "false"), required=True)
    config.add_argument("--lease-seconds", type=int, default=7200)
    config.add_argument("--heartbeat-seconds", type=int, default=600)
    config.add_argument("--max-total-controllers", type=int, required=True)
    config.add_argument("--controller-concurrency", type=int, required=True)
    config.add_argument("--max-integrations", type=int, required=True)
    config.add_argument("--agent-limit", type=int, required=True)
    sub.add_parser("first-enable")
    resource = sub.add_parser("resource-set")
    resource.add_argument("--repository-min-free-bytes", type=int, required=True)
    resource.add_argument("--docker-min-free-bytes", type=int, required=True)
    resource.add_argument("--watcher-min-free-bytes", type=int, required=True)
    sub.add_parser("status")
    verify = sub.add_parser("verify")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--live-root", type=Path, required=True)
    backup = sub.add_parser("backup")
    backup.add_argument("--destination", type=Path, required=True)
    vb = sub.add_parser("verify-backup")
    vb.add_argument("--directory", type=Path, required=True)
    restore = sub.add_parser("restore")
    restore.add_argument("--directory", type=Path, required=True)
    restore.add_argument("--target", type=Path, required=True)
    restore.add_argument("--quiescence-marker", type=Path, required=True)
    restore.add_argument("--activate", action="store_true")
    claim = sub.add_parser("claim")
    claim.add_argument("--controller", required=True)
    claim.add_argument("--owner", required=True)
    claim.add_argument("--limit", type=int, default=1)
    heartbeat = sub.add_parser("heartbeat")
    heartbeat.add_argument("--claim", required=True)
    heartbeat.add_argument("--controller", required=True)
    heartbeat.add_argument("--owner", required=True)
    heartbeat.add_argument("--generation", type=int, default=1)
    release = sub.add_parser("release")
    release.add_argument("--claim", required=True)
    release.add_argument("--controller", required=True)
    release.add_argument("--owner", required=True)
    release.add_argument("--generation", type=int, default=1)
    release.add_argument("--reason", default="released")
    finish = sub.add_parser("finish")
    finish.add_argument("--claim", required=True)
    finish.add_argument("--controller", required=True)
    finish.add_argument("--owner", required=True)
    finish.add_argument("--generation", type=int, default=1)
    finish.add_argument("--success", choices=("true", "false"), required=True)
    finish.add_argument("--reason", default="finished")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "status":
            _output("status", readonly_status(args.db))
            return 0
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
                max_total_controllers=args.max_total_controllers,
                controller_concurrency=args.controller_concurrency,
                max_integrations=args.max_integrations,
                agent_limit=args.agent_limit,
            )
            _output("config-set", {"config_version": version})
            return 0
        if args.command == "first-enable":
            version = scheduler.first_enable()
            _output("first-enable", {"config_version": version})
            return 0
        if args.command == "resource-set":
            version = scheduler.configure_resource_policy(
                repository_min_free_bytes=args.repository_min_free_bytes,
                docker_min_free_bytes=args.docker_min_free_bytes,
                watcher_min_free_bytes=args.watcher_min_free_bytes,
            )
            _output("resource-set", {"policy_version": version})
            return 0
        if args.command == "claim":
            pid, starttime, boot_id = _process_identity(
                args.pid, args.starttime_ticks, args.boot_id
            )
            claims = scheduler.claim_next(
                args.controller, args.owner, requested_limit=args.limit,
                pid=pid, process_starttime_ticks=starttime, boot_id=boot_id
            )
            _output("claim", {"claims": [claim.__dict__ for claim in claims]})
            return 0 if claims else 2
        if args.command == "heartbeat":
            pid, starttime, boot_id = _process_identity(
                args.pid, args.starttime_ticks, args.boot_id
            )
            scheduler.heartbeat(args.claim, args.owner, args.controller, args.generation,
                                pid=pid, process_starttime_ticks=starttime, boot_id=boot_id)
            _output("heartbeat", {"claim_id": args.claim})
            return 0
        if args.command == "release":
            pid, starttime, boot_id = _process_identity(
                args.pid, args.starttime_ticks, args.boot_id
            )
            scheduler.release(args.claim, args.owner, args.controller, args.generation,
                              reason=args.reason, pid=pid, process_starttime_ticks=starttime,
                              boot_id=boot_id)
            _output("release", {"claim_id": args.claim})
            return 0
        if args.command == "finish":
            pid, starttime, boot_id = _process_identity(
                args.pid, args.starttime_ticks, args.boot_id
            )
            scheduler.finish(args.claim, args.owner, args.controller, args.generation,
                             success=args.success == "true", reason=args.reason, pid=pid,
                             process_starttime_ticks=starttime, boot_id=boot_id)
            _output("finish", {"claim_id": args.claim})
            return 0
        if args.command == "verify":
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            validate_manifest(manifest, args.live_root)
            _output("verify", {"valid": True, "manifest": str(args.manifest)})
            return 0
        if args.command == "backup":
            _output("backup", backup_database(args.db, args.destination))
            return 0
        if args.command == "verify-backup":
            _output("verify-backup", verify_backup(args.directory))
            return 0
        if args.command == "restore":
            _output("restore", restore_database(args.directory, args.target, activate=args.activate,
                                                  quiescence_marker=args.quiescence_marker))
            return 0
        with scheduler.connect() as db:
            counts = {
                str(row["state"]): int(row["count"])
                for row in db.execute("SELECT state,count(*) count FROM tasks GROUP BY state")
            }
            _output("status", {"task_counts": counts, "last_event_id": int(
                db.execute("SELECT COALESCE(MAX(event_id),0) FROM events").fetchone()[0]
            )})
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
