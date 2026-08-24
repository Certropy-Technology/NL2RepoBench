#!/usr/bin/env python3
"""Freeze the source set for one Harbor production campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def freeze(base: str, source_path: str) -> dict[str, object]:
    commit = _git("rev-parse", base)
    lines = _git("ls-tree", f"{commit}:{source_path}").splitlines()
    sources = []
    for line in lines:
        metadata, task_id = line.split("\t", 1)
        _mode, kind, object_id = metadata.split()
        if kind == "tree":
            sources.append({"task_id": task_id, "source_tree_sha1": object_id})
    sources.sort(key=lambda item: str(item["task_id"]))
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "campaign_id": "harbor-production-input-v1",
        "base_commit": commit,
        "source_root": source_path,
        "source_count": len(sources),
        "sources": sources,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["content_sha256"] = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Commit/ref whose source tree is frozen.")
    parser.add_argument("--sources", default="catalog/sources")
    parser.add_argument("--expected-sources", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = freeze(args.base, args.sources)
    if payload["source_count"] != args.expected_sources:
        raise SystemExit(
            f"expected {args.expected_sources} sources, found {payload['source_count']}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "source_count": payload["source_count"],
                "content_sha256": payload["content_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
