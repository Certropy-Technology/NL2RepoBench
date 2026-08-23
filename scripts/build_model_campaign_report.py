#!/usr/bin/env python3
"""Build a redacted, structured report from a dual-model run plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import polars as pl

from nl2repobench.analysis.results import load_results, summarize_results


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid model plan {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"model plan root must be an object: {path}")
    return value


def _failure_class(rows: list[dict[str, Any]]) -> str | None:
    classes = {
        str(row["failure_class"])
        for row in rows
        if row.get("failure_class") is not None
    }
    if not classes:
        return None
    if len(classes) > 1:
        return "mixed"
    return classes.pop()


def _model_matches(actual: object, expected: str) -> bool:
    if not isinstance(actual, str):
        return False
    normalized = actual.removeprefix("openai/").removeprefix("anthropic/")
    return normalized == expected


def build_report(plan_path: Path, *, require_all: bool = True) -> dict[str, Any]:
    plan = _json(plan_path)
    tasks = plan.get("tasks")
    models = plan.get("models")
    if not isinstance(tasks, list) or not isinstance(models, list) or not models:
        raise ValueError("model plan requires tasks and models")
    normalized_by_model: dict[str, list[dict[str, Any]]] = {}
    all_rows: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    for model_plan in models:
        if not isinstance(model_plan, dict):
            raise ValueError("model plan model entries must be objects")
        model_id = model_plan.get("model_id")
        run_root = model_plan.get("run_root")
        if not isinstance(model_id, str) or not isinstance(run_root, str):
            raise ValueError("model plan model requires model_id and run_root")
        root = Path(run_root)
        frame, errors = load_results([root])
        if errors:
            raise ValueError(f"result parse errors for {model_id}: {errors[:3]}")
        rows = frame.to_dicts()
        mismatched = [
            row
            for row in rows
            if not _model_matches(row.get("model"), str(model_id))
        ]
        if mismatched:
            raise ValueError(f"result model mismatch for {model_id}: {mismatched[:2]}")
        normalized_by_model[model_id] = rows
        all_rows.extend(rows)
        seen = {str(row.get("task_id")) for row in rows}
        extras = seen - {str(task_id) for task_id in tasks}
        if extras:
            raise ValueError(f"unexpected task results for {model_id}: {sorted(extras)}")
        for task_id in tasks:
            if task_id not in seen:
                missing.append({"model": model_id, "task_id": str(task_id)})
    if require_all and missing:
        raise ValueError(f"missing model results: {missing[:10]}")

    records: list[dict[str, Any]] = []
    for task_id in tasks:
        task_record = {"task_id": task_id, "model_runs": []}
        for model_plan in models:
            model_id = model_plan["model_id"]
            rows = [row for row in normalized_by_model[model_id] if row.get("task_id") == task_id]
            valid_rows = [row for row in rows if row.get("valid") is True]
            rewards = [row["reward"] for row in valid_rows if row.get("reward") is not None]
            task_record["model_runs"].append(
                {
                    "model": model_id,
                    "attempts": len(rows),
                    "status": "completed" if valid_rows else "failed",
                    "failure_class": _failure_class(rows),
                    "valid": bool(valid_rows),
                    "rewards": rewards,
                }
            )
        records.append(task_record)
    summary_frame = pl.DataFrame(all_rows)
    return {
        "schema_version": "1.0",
        "campaign_id": plan.get("campaign_id"),
        "plan_sha256": "sha256:" + hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        "task_count": len(tasks),
        "models": [model["model_id"] for model in models],
        "tasks": records,
        "missing": missing,
        "summary": summarize_results(summary_frame),
        "retry_policy": "infrastructure-only",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()
    try:
        report = build_report(args.plan, require_all=not args.allow_missing)
    except (OSError, ValueError) as exc:
        print(f"model campaign report failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"output": str(args.output), "task_count": report["task_count"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
