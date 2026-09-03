#!/usr/bin/env python3
"""Repair a missing production-evidence file from an authored handoff.

This is an explicit integrator repair for older authoring lanes.  It copies
only evidence already recorded by the worker and marks the repair in the
result.  It never creates Oracle or model-run results.
"""

from __future__ import annotations

import argparse
import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _source_freeze(task: dict[str, Any], handoff: dict[str, Any]) -> dict[str, Any]:
    source = task.get("source") if isinstance(task.get("source"), dict) else {}
    handoff_source = handoff.get("source")
    if isinstance(handoff_source, dict):
        source = {**source, **handoff_source}
    return {
        key: source[key]
        for key in ("upstream_url", "revision", "license_spdx", "source_digest")
        if key in source
    }


def build_evidence(worktree: Path, package: str) -> dict[str, Any]:
    source_root = worktree / "catalog/sources" / package
    task_path = source_root / "task.toml"
    handoff_path = worktree / ".nl2repo/authoring-handoff.json"
    task = tomllib.loads(task_path.read_text(encoding="utf-8"))
    handoff = _json(handoff_path)
    task_id = task.get("task_id")
    if not isinstance(task_id, str) or task_id != package:
        raise ValueError(f"task_id does not match package: {task_id!r} != {package!r}")
    if handoff.get("task_id") not in {None, task_id}:
        raise ValueError("handoff task_id does not match task.toml")
    environment = task.get("environment")
    dependencies = task.get("dependencies")
    tests = task.get("tests")
    lifecycle = task.get("lifecycle")
    return {
        "schema_version": "1.0",
        "task_id": task_id,
        "task_version": task.get("version"),
        "status": "awaiting-agent-run",
        "terminal_kind": "awaiting-agent-run",
        "source_freeze": _source_freeze(task, handoff),
        "environment": environment if isinstance(environment, dict) else {},
        "dependency_closure": dependencies if isinstance(dependencies, dict) else {},
        "frozen_collection": {
            "tests": tests if isinstance(tests, dict) else {},
            "handoff_inventory": handoff.get("inventory"),
            "handoff_frozen_tests": handoff.get("frozen_tests"),
            "handoff_collection": handoff.get("collection"),
        },
        "bundle": {
            "handoff_artifacts": handoff.get("artifacts"),
            "handoff_compiled_bundle": handoff.get("compiled_bundle"),
        },
        "commands": handoff.get("commands", []),
        "oracle": handoff.get("oracle") or handoff.get("oracle_outcome") or {
            "status": "not-run",
            "reason": "No official Harbor Oracle was run in the authoring lane.",
        },
        "controls": handoff.get("controls") or handoff.get("control_outcomes") or {
            "status": "pending-integrator-runtime"
        },
        "lifecycle": lifecycle if isinstance(lifecycle, dict) else {},
        "residual_risks": handoff.get("residual_risks", []),
        "integrator_repair": {
            "kind": "production-evidence-from-authored-handoff",
            "recorded_at": datetime.now(UTC).isoformat(),
            "input_handoff": str(handoff_path),
            "official_oracle_created": False,
            "official_controls_created": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    output = args.worktree / "catalog/sources" / args.package / "production-evidence.json"
    if output.exists() and not args.force:
        raise SystemExit(f"production evidence already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            build_evidence(args.worktree, args.package),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(output), "task_id": args.package}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
