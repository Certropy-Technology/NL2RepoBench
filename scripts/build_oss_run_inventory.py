#!/usr/bin/env python3
"""Build a model/task inventory from the authoritative OSS run prefix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

BUCKET = "dingshang-sg"
ENDPOINT = "https://oss-ap-southeast-1.aliyuncs.com"
ROOT_PREFIX = "nl2repobench/runs/"
RUN_KINDS = frozenset({"gpt-5.6-sol", "claude-fable-5", "oracle"})


def _build_bucket() -> Any:
    try:
        import oss2
    except ImportError as exc:
        raise RuntimeError("install oss2 before querying OSS") from exc
    key_id = os.environ.get("OSS_ACCESS_KEY_ID")
    key_secret = os.environ.get("OSS_ACCESS_KEY_SECRET")
    if not key_id or not key_secret:
        raise RuntimeError("set OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET")
    return oss2.Bucket(oss2.Auth(key_id, key_secret), ENDPOINT, BUCKET)


def _objects(bucket: Any, prefix: str) -> Iterable[Any]:
    import oss2

    return oss2.ObjectIterator(bucket, prefix=prefix)


def canonical_task_id(raw: str, known_tasks: set[str]) -> str | None:
    if raw in known_tasks:
        return raw
    matches = [
        task
        for task in known_tasks
        if raw.startswith(f"{task}-") or raw.endswith(f"-{task}")
    ]
    return max(matches, key=len) if matches else None


def inventory(
    bucket: Any,
    *,
    prefix: str = ROOT_PREFIX,
    known_tasks: set[str] | None = None,
) -> dict[str, Any]:
    if known_tasks is None:
        catalog = Path("catalog/tasks")
        known_tasks = {
            path.name
            for path in catalog.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        } if catalog.is_dir() else set()
    runs: dict[tuple[str, str, str], dict[str, Any]] = {}
    object_count = 0
    for obj in _objects(bucket, prefix):
        key = str(getattr(obj, "key", ""))
        object_count += 1
        parts = key.split("/")
        if len(parts) < 5 or parts[:2] != ["nl2repobench", "runs"]:
            continue
        model, raw_task, trial = parts[2:5]
        if model not in RUN_KINDS or not raw_task or not trial or trial.endswith(".log"):
            continue
        task = canonical_task_id(raw_task, known_tasks)
        if task is None:
            continue
        identity = (model, task, trial)
        record = runs.setdefault(
            identity,
            {
                "model": model,
                "task_id": task,
                "trial": trial,
                "source": "oss",
                "prefix": "/".join(parts[:5]) + "/",
                "object_keys": [],
            },
        )
        record["object_keys"].append(key)
    verified: list[dict[str, Any]] = []
    for record in runs.values():
        object_keys = set(record.pop("object_keys", []))
        prefix_key = record["prefix"]
        result_key = prefix_key + "result.json"
        if result_key not in object_keys:
            continue
        try:
            payload = json.loads(bucket.get_object(result_key).read())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
            continue
        if not isinstance(payload, dict) or payload.get("finished_at") is None:
            continue
        stats = payload.get("stats")
        stats = stats if isinstance(stats, dict) else {}
        completed = stats.get("n_completed_trials", 0)
        errored = stats.get("n_errored_trials", 0)
        if not isinstance(completed, int) or not isinstance(errored, int):
            continue
        if completed < 1 and errored < 1:
            continue
        grading_keys = sorted(key for key in object_keys if key.endswith("/grading.json"))
        record.update(
            {
                "status": "completed" if completed > 0 else "errored",
                "result_key": result_key,
                "grading_keys": grading_keys,
                "evidence_keys": [result_key, *grading_keys],
                "finished_at": payload.get("finished_at"),
                "n_completed_trials": completed,
                "n_errored_trials": errored,
                "revision_binding": "unbound-legacy",
            }
        )
        verified.append(record)
    rows = sorted(verified, key=lambda row: (row["model"], row["task_id"], row["trial"]))
    return {
        "schema_version": "1.0",
        "source": "oss",
        "bucket": BUCKET,
        "prefix": prefix,
        "object_count_scanned": object_count,
        "run_count": len(rows),
        "runs": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefix", default=ROOT_PREFIX)
    args = parser.parse_args()
    try:
        bucket = _build_bucket()
        report = inventory(bucket, prefix=args.prefix)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"OSS run inventory failed: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.output.write_text(encoded, encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": "sha256:" + hashlib.sha256(encoded.encode()).hexdigest(),
                "run_count": report["run_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
