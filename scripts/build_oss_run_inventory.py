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
MODELS = frozenset({"gpt-5.6-sol", "claude-fable-5"})


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


def inventory(bucket: Any, *, prefix: str = ROOT_PREFIX) -> dict[str, Any]:
    runs: dict[tuple[str, str, str], dict[str, str]] = {}
    object_count = 0
    for obj in _objects(bucket, prefix):
        key = str(getattr(obj, "key", ""))
        object_count += 1
        parts = key.split("/")
        if len(parts) < 5 or parts[:2] != ["nl2repobench", "runs"]:
            continue
        model, task, trial = parts[2:5]
        if model not in MODELS or not task or not trial:
            continue
        identity = (model, task, trial)
        runs[identity] = {
            "model": model,
            "task_id": task,
            "trial": trial,
            "source": "oss",
            "prefix": "/".join(parts[:5]) + "/",
        }
    rows = sorted(runs.values(), key=lambda row: (row["model"], row["task_id"], row["trial"]))
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
