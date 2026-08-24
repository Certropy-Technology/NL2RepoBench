#!/usr/bin/env python3
"""Build the immutable task set for a 300+ Harbor benchmark release.

This is a release gate, not a candidate discovery report. A task enters the
manifest only when its catalog source says ``lifecycle.status = published`` and
the generated Harbor tree contains the required execution files. The default
minimum is 300 tasks; a diagnostic ``--allow-below-target`` mode can inspect a
smaller local set but still labels the result non-releaseable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from pathlib import Path
from typing import Any

import polars as pl

REQUIRED_HARBOR_FILES = (
    "task.toml",
    "instruction.md",
    "solution",
    "tests",
    "environment",
)


def collect_published_tasks(
    catalog_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Collect published source/Harbor pairs and return rejection diagnostics."""

    tasks: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    for source_path in sorted(catalog_root.glob("*/task.toml")):
        task_dir = source_path.parent
        task_id = task_dir.name
        try:
            source = tomllib.loads(source_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            rejected.append({"task_id": task_id, "reason": f"invalid-source: {exc}"})
            continue
        lifecycle = source.get("lifecycle")
        status = lifecycle.get("status") if isinstance(lifecycle, dict) else None
        if status != "published":
            continue
        harbor_dir = task_dir / "harbor"
        missing = [name for name in REQUIRED_HARBOR_FILES if not (harbor_dir / name).exists()]
        if missing:
            rejected.append(
                {
                    "task_id": task_id,
                    "reason": f"published-source-missing-harbor: {','.join(missing)}",
                }
            )
            continue
        harbor_task = harbor_dir / "task.toml"
        try:
            harbor_data = tomllib.loads(harbor_task.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            rejected.append({"task_id": task_id, "reason": f"invalid-harbor-task: {exc}"})
            continue
        tasks.append(
            {
                "task_id": task_id,
                "task_release": str(
                    source.get("task_release") or source.get("version") or "unknown"
                ),
                "source_schema": str(source.get("schema_version") or "unknown"),
                "language": _language(source),
                "category": _metadata_value(source, "category"),
                "difficulty": _metadata_value(source, "difficulty"),
                "source_manifest_sha256": _sha256(source_path),
                "harbor_task_sha256": _sha256(harbor_task),
                "harbor_path": harbor_dir.as_posix(),
                "harbor_schema": str(harbor_data.get("schema_version") or "unknown"),
            }
        )
    tasks.sort(key=lambda item: (item["task_id"], item["task_release"]))
    return tasks, rejected


def build_manifest(
    catalog_root: Path,
    *,
    dataset_id: str,
    dataset_release: str,
    minimum_tasks: int,
    allow_below_target: bool,
) -> dict[str, Any]:
    """Build a deterministic release manifest or raise a fail-closed error."""

    tasks, rejected = collect_published_tasks(catalog_root)
    task_ids = [task["task_id"] for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("published benchmark manifest contains duplicate task IDs")
    status = "releaseable" if len(tasks) >= minimum_tasks else "below-target"
    if status == "below-target" and not allow_below_target:
        raise ValueError(
            f"published task count {len(tasks)} is below required minimum {minimum_tasks}; "
            "use --allow-below-target only for diagnostics"
        )
    return {
        "contract": "published-harbor-benchmark",
        "dataset_id": dataset_id,
        "dataset_release": dataset_release,
        "minimum_tasks": minimum_tasks,
        "task_count": len(tasks),
        "status": status,
        "tasks": tasks,
        "rejected_published_sources": rejected,
    }


def write_outputs(manifest: dict[str, Any], output: Path, parquet: Path | None) -> None:
    """Write JSON and optional Polars/Parquet task index."""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    if parquet is not None:
        parquet.parent.mkdir(parents=True, exist_ok=True)
        pl.DataFrame(manifest["tasks"]).write_parquet(parquet)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root", type=Path, default=Path("catalog/sources"))
    parser.add_argument("--dataset-id", default="nl2repobench-harbor-300")
    parser.add_argument("--dataset-release", required=True)
    parser.add_argument("--minimum-tasks", type=int, default=300)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--parquet", type=Path)
    parser.add_argument("--allow-below-target", action="store_true")
    args = parser.parse_args()
    if args.minimum_tasks < 300:
        parser.error("--minimum-tasks cannot be lower than 300")
    if not args.catalog_root.is_dir():
        parser.error(f"catalog root does not exist: {args.catalog_root}")
    try:
        manifest = build_manifest(
            args.catalog_root,
            dataset_id=args.dataset_id,
            dataset_release=args.dataset_release,
            minimum_tasks=args.minimum_tasks,
            allow_below_target=args.allow_below_target,
        )
    except ValueError as exc:
        print(f"published benchmark manifest rejected: {exc}")
        return 2
    write_outputs(manifest, args.output, args.parquet)
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _metadata_value(source: dict[str, Any], name: str) -> str:
    metadata = source.get("metadata")
    if not isinstance(metadata, dict):
        return "unknown"
    return str(metadata.get(name) or "unknown")


def _language(source: dict[str, Any]) -> str:
    metadata = source.get("metadata")
    if isinstance(metadata, dict) and metadata.get("language"):
        return str(metadata["language"])
    environment = source.get("environment")
    if isinstance(environment, dict):
        runtime = environment.get("runtime")
        if isinstance(runtime, dict) and runtime.get("language"):
            return str(runtime["language"])
    return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
