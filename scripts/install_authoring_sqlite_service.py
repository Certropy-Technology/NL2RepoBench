#!/usr/bin/env python3
"""Validate or install the exact SQLite scheduler environment binding."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nl2repobench.authoring.cutover import install_service_binding
from nl2repobench.authoring.migration import MigrationError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--barrier", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--sqlite-service-unit", required=True)
    parser.add_argument("--sqlite-env-file", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = install_service_binding(
            journal_path=args.journal.resolve(),
            barrier_path=args.barrier.resolve(),
            database=args.db.resolve(),
            sqlite_service_unit=args.sqlite_service_unit,
            sqlite_env_file=args.sqlite_env_file,
            write=args.write,
        )
    except (MigrationError, OSError, ValueError) as exc:
        print(f"SQLite service binding failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
