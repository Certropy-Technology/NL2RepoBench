#!/usr/bin/env python3
"""Validate the frozen source set and exact production Harbor task projection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harbor_production_validation import validate_catalog, write_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-sources", type=int, required=True)
    parser.add_argument("--artifact-root", type=Path, default=Path(".nl2repo/artifacts"))
    parser.add_argument("--python-toolchain", type=Path, default=Path("toolchain.lock.toml"))
    parser.add_argument("--node-toolchain", type=Path, default=Path("toolchain.node.lock.toml"))
    parser.add_argument("--go-toolchain", type=Path, default=Path("toolchain.go.lock.toml"))
    parser.add_argument("--java-toolchain", type=Path, default=Path("toolchain.java.lock.toml"))
    parser.add_argument("--no-compile", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    repository_root = Path.cwd().resolve()
    try:
        report = validate_catalog(
            sources_root=args.sources.resolve(),
            tasks_root=args.tasks.resolve(),
            input_path=args.input.resolve(),
            expected_sources=args.expected_sources,
            repository_root=repository_root,
            artifact_root=args.artifact_root.resolve(),
            python_toolchain=args.python_toolchain.resolve(),
            node_toolchain=args.node_toolchain.resolve(),
            go_toolchain=args.go_toolchain.resolve(),
            java_toolchain=args.java_toolchain.resolve(),
            compile_tasks=not args.no_compile,
        )
        write_report(args.report, report)
    except (OSError, ValueError) as exc:
        print(f"Harbor production catalog gate failed: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "report": str(args.report),
                "ok": report["ok"],
                "counts": report["counts"],
                "error_count": len(report["errors"]),
            },
            sort_keys=True,
        )
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
