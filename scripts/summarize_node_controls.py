#!/usr/bin/env python3
"""Summarize and validate Node production controls from Harbor grading files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXPECTED = (
    "empty",
    "stub",
    "forgery",
    "install-script",
    "loader-hook",
    "hang",
    "offline",
)


def _grading(root: Path, kind: str) -> dict[str, Any]:
    paths = sorted(
        path
        for path in (root / kind).rglob("grading.json")
        if path.parent.name == "verifier"
    )
    if len(paths) != 1:
        raise ValueError(f"{kind}: expected exactly one grading.json, found {len(paths)}")
    value = json.loads(paths[0].read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{kind}: grading.json must be an object")
    return value


def _passed(kind: str, grading: dict[str, Any]) -> tuple[bool, str]:
    reward = grading.get("reward")
    valid = grading.get("valid")
    reason = grading.get("failure_reason")
    failure_class = grading.get("failure_class")
    if kind == "empty":
        return valid is True and failure_class == "model" and reward == 0, "near-zero model score"
    if kind == "stub":
        return (
            valid is True and isinstance(reward, (int, float)) and reward <= 0.2,
            "stub low score",
        )
    if kind == "forgery":
        return (
            valid is True and isinstance(reward, (int, float)) and reward < 1,
            "forged report cannot produce full score",
        )
    if kind == "install-script":
        return (
            valid is True and reason == "candidate-installation-failed",
            "lifecycle script rejected",
        )
    if kind == "loader-hook":
        return (
            valid is True and isinstance(reward, (int, float)) and reward < 1,
            "loader injection cannot produce full score",
        )
    if kind == "hang":
        return (
            valid is True
            and reward == 0
            and reason == "candidate-call-failed"
            and failure_class == "model",
            "hang terminated by the candidate-call supervisor",
        )
    if kind == "offline":
        return (
            valid is True and isinstance(reward, (int, float)) and reward < 1,
            "network behavior cannot produce full score",
        )
    return False, "unknown control"


def summarize(root: Path) -> dict[str, Any]:
    controls: dict[str, dict[str, Any]] = {}
    for kind in EXPECTED:
        grading = _grading(root, kind)
        passed, result = _passed(kind, grading)
        controls[kind] = {
            "passed": passed,
            "completed": True,
            "result": result,
            "reward": grading.get("reward"),
            "valid": grading.get("valid"),
            "failure_class": grading.get("failure_class"),
            "failure_reason": grading.get("failure_reason"),
            "evidence": [str(path) for path in sorted((root / kind).rglob("grading.json"))],
        }
    return {"schema_version": "1.0", "task_id": root.name, "controls": controls}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = summarize(args.root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Node control summary failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    passed = all(item["passed"] for item in report["controls"].values())
    print(json.dumps({"output": str(args.output), "passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
