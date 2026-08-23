#!/usr/bin/env python3
"""Fail-closed gate for a real Node production vertical slice."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

EXPECTED = frozenset(
    {"empty", "stub", "forgery", "install-script", "loader-hook", "hang", "offline"}
)


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _oracle(root: Path) -> dict[str, Any]:
    paths = sorted(root.rglob("grading.json"))
    paths = [path for path in paths if path.parent.name == "verifier"]
    if len(paths) != 1:
        raise ValueError(
            "Oracle evidence requires exactly one verifier grading.json, "
            f"got {len(paths)}"
        )
    return _json(paths[0])


def validate(
    task: Path,
    bundle: Path,
    toolchain: Path,
    oracle_root: Path,
    controls: Path,
) -> dict[str, Any]:
    source = tomllib.loads((task / "task.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads(toolchain.read_text(encoding="utf-8"))
    if lock.get("status") != "locked" or lock.get("node_grader") != "locked":
        raise ValueError("Node toolchain is not production locked")
    runtime = lock.get("runtime", {})
    if runtime.get("runtime_version", "").split(".", 1)[0] != "24":
        raise ValueError("production Node vertical slice must use Node 24")
    if not bundle.is_dir() or not (bundle / "bundle.manifest.json").is_file():
        raise ValueError("compiled production bundle is missing")
    bundle_manifest = _json(bundle / "bundle.manifest.json")
    if bundle_manifest.get("mode") != "production":
        raise ValueError("compiled bundle is not production mode")
    expected = source.get("tests", {}).get("expected_total")
    grading = _oracle(oracle_root)
    if (
        grading.get("valid") is not True
        or grading.get("reward", 0) < 0.80
        or grading.get("expected_total") != expected
        or grading.get("counts", {}).get("collected") != expected
    ):
        raise ValueError("Node Oracle gate did not pass fixed denominator/reward")
    control_report = _json(controls)
    control_rows = control_report.get("controls")
    if not isinstance(control_rows, dict) or set(control_rows) != EXPECTED:
        raise ValueError("Node control matrix is incomplete")
    if not all(row.get("passed") is True for row in control_rows.values() if isinstance(row, dict)):
        raise ValueError("Node control matrix contains a failed control")
    return {
        "schema_version": "1.0",
        "task_id": source.get("task_id") or source.get("task", {}).get("task_id"),
        "runtime": runtime,
        "bundle_mode": bundle_manifest.get("mode"),
        "oracle": {
            "valid": grading["valid"],
            "reward": grading["reward"],
            "expected_total": grading["expected_total"],
            "collected": grading["counts"]["collected"],
        },
        "controls": {name: row["passed"] for name, row in control_rows.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--oracle-root", type=Path, required=True)
    parser.add_argument("--controls", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = validate(args.task, args.bundle, args.toolchain, args.oracle_root, args.controls)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"Node production gate failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "task_id": report["task_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
