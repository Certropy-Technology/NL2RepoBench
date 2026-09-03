#!/usr/bin/env python3
"""Repair a missing production-evidence file from an authored handoff.

This is an explicit repair for older authoring lanes. It copies only evidence
already recorded by a worker that completed the production gate. It refuses to
turn an ``awaiting-agent-run`` or ``packaged`` handoff into production evidence
and never creates Oracle or model-run results.
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


REQUIRED_CONTROLS = (
    "empty",
    "stub",
    "forgery",
    "install-failure",
    "panic",
    "hang",
    "oversized-output",
    "background-process",
    "offline",
)


def _local_file(worktree: Path, value: Any) -> bool:
    if not isinstance(value, str) or not value or "<" in value or ">" in value:
        return False
    path = Path(value)
    candidate = path if path.is_absolute() else worktree / path
    try:
        candidate.resolve().relative_to(worktree.resolve())
    except (OSError, ValueError):
        return False
    return candidate.is_file() and not candidate.is_symlink()


def _require_agent_production_gate(worktree: Path, package: str) -> dict[str, Any]:
    path = worktree / ".nl2repo/authoring-production-gates.json"
    try:
        payload = _json(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"agent production gate receipt is missing or invalid: {exc}") from exc
    if payload.get("schema_version") != "1.0" or payload.get("task_id") != package:
        raise ValueError("agent production gate receipt identity is invalid")
    if payload.get("status") != "controls-passed":
        raise ValueError("agent production gate status is not controls-passed")
    compile_record = payload.get("compile")
    if not isinstance(compile_record, dict) or compile_record.get("status") != "passed":
        raise ValueError("agent production compile receipt is missing")
    if not _local_file(worktree, compile_record.get("bundle_manifest")):
        raise ValueError("agent production bundle manifest is missing")
    oracle = payload.get("oracle")
    if not isinstance(oracle, dict):
        raise ValueError("agent Oracle receipt is missing")
    if oracle.get("valid") is not True:
        raise ValueError("agent Oracle receipt is not valid")
    passed = oracle.get("passed")
    collected = oracle.get("collected")
    frozen_total = oracle.get("frozen_total")
    reward = oracle.get("reward")
    if (
        not isinstance(passed, int)
        or isinstance(passed, bool)
        or not isinstance(collected, int)
        or isinstance(collected, bool)
        or not isinstance(frozen_total, int)
        or isinstance(frozen_total, bool)
        or collected != frozen_total
        or not 0 <= passed <= collected
        or frozen_total < 1
        or not isinstance(reward, (int, float))
        or isinstance(reward, bool)
        or reward < 0.8
    ):
        raise ValueError("agent Oracle counts or reward are invalid")
    for key in ("result", "grading", "network"):
        if not _local_file(worktree, oracle.get(key)):
            raise ValueError(f"agent Oracle {key} evidence is missing")
    controls = payload.get("controls")
    if not isinstance(controls, dict):
        raise ValueError("agent controls receipt is missing")
    for kind in REQUIRED_CONTROLS:
        record = controls.get(kind)
        if not isinstance(record, dict) or record.get("valid") is not True:
            raise ValueError(f"agent control {kind} is missing or invalid")
        control_reward = record.get("reward")
        if not isinstance(control_reward, (int, float)) or isinstance(control_reward, bool):
            raise ValueError(f"agent control {kind} reward is invalid")
        if kind != "offline" and control_reward != 0:
            raise ValueError(f"agent control {kind} reward is not zero")
        for key in ("result", "grading", "network"):
            if not _local_file(worktree, record.get(key)):
                raise ValueError(f"agent control {kind} {key} evidence is missing")
    if controls["offline"].get("public_network_available") is not False:
        raise ValueError("agent offline control does not prove no public network")
    return payload


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
    if handoff.get("status") != "controls-passed":
        raise ValueError("handoff must be controls-passed before evidence repair")
    production_gate = _require_agent_production_gate(worktree, package)
    environment = task.get("environment")
    dependencies = task.get("dependencies")
    tests = task.get("tests")
    lifecycle = task.get("lifecycle")
    return {
        "schema_version": "1.0",
        "task_id": task_id,
        "task_version": task.get("version"),
        "status": "controls-passed",
        "terminal_kind": "controls-passed",
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
        "oracle": production_gate["oracle"],
        "controls": production_gate["controls"],
        "lifecycle": lifecycle if isinstance(lifecycle, dict) else {},
        "residual_risks": handoff.get("residual_risks", []),
        "integrator_repair": {
            "kind": "production-evidence-from-authored-handoff",
            "recorded_at": datetime.now(UTC).isoformat(),
            "input_handoff": str(handoff_path),
            "official_oracle_created": False,
            "official_controls_created": False,
            "source": "agent-production-gate-receipt",
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
