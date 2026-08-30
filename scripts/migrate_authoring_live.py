#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate and validate the Phase 2 authoring-live manifest and dry-run import."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nl2repobench.authoring.cutover import (
    execute_cutover,
    restore_cutover_database,
    rollback_cutover,
)
from nl2repobench.authoring.migration import (
    barrier_check,
    generate_manifest,
    import_manifest,
    validate_manifest,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--live-root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--cutover-id")
    p.add_argument("--db", type=Path)
    p.add_argument("--write", action="store_true", help="write the generated manifest")
    p.add_argument("--import", dest="do_import", action="store_true")
    p.add_argument("--execute-cutover", action="store_true")
    p.add_argument("--rollback-cutover", action="store_true")
    p.add_argument("--restore-cutover", action="store_true")
    p.add_argument("--repository-root", type=Path)
    p.add_argument("--journal", type=Path)
    p.add_argument("--external-side-effect-barrier", type=Path)
    p.add_argument("--legacy-runtime-config", type=Path)
    p.add_argument("--service-unit", default="nl2repobench-authoring-supervisor.service")
    p.add_argument("--sqlite-service-unit")
    p.add_argument("--sqlite-env-file", type=Path)
    p.add_argument("--drain-timeout", type=int, default=7200)
    p.add_argument("--backup-directory", type=Path)
    p.add_argument("--repository-min-free-bytes", type=int)
    p.add_argument("--docker-min-free-bytes", type=int)
    p.add_argument("--watcher-min-free-bytes", type=int)
    p.add_argument("--receipt-authority", type=Path)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.execute_cutover:
        required = (
            args.cutover_id,
            args.db,
            args.repository_root,
            args.journal,
            args.external_side_effect_barrier,
            args.backup_directory,
            args.repository_min_free_bytes,
            args.docker_min_free_bytes,
            args.watcher_min_free_bytes,
            args.sqlite_service_unit,
            args.sqlite_env_file,
        )
        if any(value is None for value in required):
            raise SystemExit(
                "cutover requires identifiers/paths plus explicit backup and resource limits"
            )
        assert args.sqlite_service_unit is not None
        assert args.sqlite_env_file is not None
        cutover_result = execute_cutover(
            repository=args.repository_root.resolve(),
            live_root=args.live_root.resolve(),
            manifest_path=args.manifest.resolve(),
            database=args.db.resolve(),
            backup_directory=args.backup_directory.resolve(),
            journal_path=args.journal.resolve(),
            barrier_path=args.external_side_effect_barrier.resolve(),
            cutover_id=args.cutover_id,
            service_unit=args.service_unit,
            sqlite_service_unit=args.sqlite_service_unit,
            sqlite_env_file=args.sqlite_env_file,
            drain_timeout=args.drain_timeout,
            repository_min_free_bytes=args.repository_min_free_bytes,
            docker_min_free_bytes=args.docker_min_free_bytes,
            watcher_min_free_bytes=args.watcher_min_free_bytes,
        )
        print(json.dumps(cutover_result, sort_keys=True))
        return 0
    if args.rollback_cutover:
        if (
            args.journal is None
            or args.external_side_effect_barrier is None
            or args.legacy_runtime_config is None
            or args.db is None
        ):
            raise SystemExit(
                "rollback requires --journal, --external-side-effect-barrier, and --legacy-runtime-config"
            )
        rollback_cutover(
            journal_path=args.journal.resolve(),
            barrier_path=args.external_side_effect_barrier.resolve(),
            runtime_config=args.legacy_runtime_config.resolve(),
            database=args.db.resolve(),
        )
        print(json.dumps({"status": "rolled-back"}, sort_keys=True))
        return 0
    if args.restore_cutover:
        restore_required = (
            args.db,
            args.journal,
            args.external_side_effect_barrier,
            args.legacy_runtime_config,
            args.backup_directory,
            args.receipt_authority,
        )
        if any(value is None for value in restore_required):
            raise SystemExit("restore requires DB, journal, barrier, runtime config, backup, and receipt authority")
        restore_result = restore_cutover_database(
            backup_directory=args.backup_directory.resolve(),
            database=args.db.resolve(),
            journal_path=args.journal.resolve(),
            barrier_path=args.external_side_effect_barrier.resolve(),
            runtime_config=args.legacy_runtime_config.resolve(),
            receipt_authority=args.receipt_authority.resolve(),
        )
        print(json.dumps(restore_result, sort_keys=True))
        return 0
    if args.do_import:
        try:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"cannot read frozen manifest: {exc}") from exc
    else:
        if not args.cutover_id:
            raise SystemExit("--cutover-id is required when generating a manifest")
        manifest = generate_manifest(args.live_root, cutover_id=args.cutover_id)
    if args.write and not args.do_import:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
    validate_manifest(manifest, args.live_root)
    result: dict[str, object] = {
        "manifest": str(args.manifest),
        "barrier": barrier_check(args.live_root, manifest=manifest),
    }
    if args.do_import:
        result["import"] = import_manifest(manifest, args.live_root, db_path=args.db, dry_run=True)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
