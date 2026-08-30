#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate and validate the Phase 2 authoring-live manifest and dry-run import."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

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
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
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
        args.manifest.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    validate_manifest(manifest, args.live_root)
    result: dict[str, object] = {"manifest": str(args.manifest), "barrier": barrier_check(args.live_root, manifest=manifest)}
    if args.do_import:
        result["import"] = import_manifest(manifest, args.live_root, db_path=args.db, dry_run=True)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
