#!/usr/bin/env python3
"""Plan model runs for catalog Harbor tasks absent from the trusted OSS inventory."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

REQUIRED_HARBOR = (
    "task.toml",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/Dockerfile",
    "tests/test.sh",
    "tests/grade.py",
)


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _oss_tasks(path: Path) -> set[str]:
    payload = _json(path)
    runs = payload.get("runs")
    if not isinstance(runs, list):
        raise ValueError("OSS inventory requires runs list")
    return {
        str(run["task_id"])
        for run in runs
        if isinstance(run, dict) and run.get("source") == "oss" and run.get("task_id")
    }


def plan(catalog_root: Path, oss_inventory: Path, limit: int) -> dict[str, Any]:
    if limit < 1:
        raise ValueError("limit must be positive")
    oss_tasks = _oss_tasks(oss_inventory)
    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for task_dir in sorted(path for path in catalog_root.iterdir() if path.is_dir()):
        if task_dir.name.startswith("."):
            continue
        task_id = task_dir.name
        if task_id in oss_tasks:
            skipped.append({"task_id": task_id, "reason": "oss-run-exists"})
            continue
        source_path = task_dir / "task.toml"
        harbor_root = task_dir / "harbor"
        if not source_path.is_file() or not harbor_root.is_dir():
            skipped.append({"task_id": task_id, "reason": "missing-task-or-harbor"})
            continue
        source = tomllib.loads(source_path.read_text(encoding="utf-8"))
        lifecycle = source.get("lifecycle")
        lifecycle = lifecycle if isinstance(lifecycle, dict) else {}
        if lifecycle.get("status") in {"blocked", "excluded"}:
            skipped.append({"task_id": task_id, "reason": f"lifecycle-{lifecycle.get('status')}"})
            continue
        missing = [
            relative for relative in REQUIRED_HARBOR if not (harbor_root / relative).is_file()
        ]
        if missing:
            skipped.append(
                {"task_id": task_id, "reason": "missing-harbor-files:" + ",".join(missing)}
            )
            continue
        selected.append(
            {
                "task_id": task_id,
                "language": source.get("metadata", {}).get("language", "python"),
                "harbor_path": str(harbor_root),
                "lifecycle": lifecycle.get("status"),
            }
        )
        if len(selected) >= limit:
            break
    return {
        "schema_version": "1.0",
        "policy": "skip task when trusted OSS inventory contains any finished run",
        "catalog_root": str(catalog_root),
        "oss_inventory": str(oss_inventory),
        "oss_task_count": len(oss_tasks),
        "selected": selected,
        "skipped": skipped,
        "status": "planned",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root", type=Path, default=Path("catalog/tasks"))
    parser.add_argument("--oss-inventory", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = plan(args.catalog_root, args.oss_inventory, args.limit)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"missing OSS run plan failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "selected": len(report["selected"]),
                "skipped": len(report["skipped"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
