"""Run a private Rust verifier and emit a bounded native bridge report."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

MAX_OUTPUT_BYTES = 8 * 1024 * 1024


def _failed_report(expected: int, message: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "framework": "rust-harness",
        "report_format": "rust-bridge-json-v1",
        "collected": expected,
        "leaves": [
            {
                "leaf_id": f"rust.runner.{index}",
                "status": "failed",
                "duration_ms": 0.0,
                "details": message,
            }
            for index in range(expected)
        ],
        "collection_errors": [],
        "runner_exit_code": 1,
    }


def _compact_report(payload: dict[str, Any], expected: int) -> dict[str, object]:
    leaves = payload.get("leaves")
    if not isinstance(leaves, list):
        raise ValueError("private Rust verifier leaves must be an array")
    converted = []
    for item in leaves:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("private Rust verifier leaf requires id")
        converted.append(
            {
                "leaf_id": item["id"],
                "status": item.get("status"),
                "duration_ms": item.get("duration_ms", 0.0),
                "details": item.get("message", item.get("details")),
            }
        )
    if len(converted) != expected:
        raise ValueError(
            f"private Rust verifier emitted {len(converted)} leaves; expected {expected}"
        )
    return {
        "schema_version": "1.0",
        "framework": "rust-harness",
        "report_format": "rust-bridge-json-v1",
        "collected": len(converted),
        "leaves": converted,
        "collection_errors": [],
        "runner_exit_code": 0 if all(item["status"] == "passed" for item in converted) else 1,
    }


def _adapt_report(
    payload: dict[str, Any], expected: int, exit_code: int
) -> tuple[dict[str, object], int]:
    """Accept the private compact shape while emitting one canonical report."""

    if set(payload) == {"schema_version", "leaves"}:
        report = _compact_report(payload, expected)
    elif set(payload) == {"schema_version", "framework", "report_format", "leaves"}:
        report = _compact_report(
            {"schema_version": payload["schema_version"], "leaves": payload["leaves"]},
            expected,
        )
    elif set(payload) == {
        "schema_version",
        "framework",
        "report_format",
        "collected",
        "leaves",
        "collection_errors",
        "runner_exit_code",
    }:
        report = dict(payload)
    else:
        raise ValueError("private Rust verifier report shape is invalid")
    effective_exit = exit_code
    if set(payload) != {
        "schema_version",
        "framework",
        "report_format",
        "collected",
        "leaves",
        "collection_errors",
        "runner_exit_code",
    }:
        leaves = report.get("leaves")
        if not isinstance(leaves, list):
            raise ValueError("private Rust verifier leaves are malformed")
        effective_exit = 0 if all(leaf["status"] == "passed" for leaf in leaves) else 1
    report["runner_exit_code"] = effective_exit
    return report, effective_exit


def run(entrypoint: Path, report_path: Path, expected: int, timeout: float) -> int:
    if entrypoint.is_symlink() or not entrypoint.is_file():
        report = _failed_report(expected, "Rust verifier entrypoint is missing")
        report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        return 1
    try:
        process = subprocess.Popen(
            [sys.executable, "-I", str(entrypoint)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise
        completed = subprocess.CompletedProcess(
            process.args,
            process.returncode,
            stdout,
            stderr,
        )
    except subprocess.TimeoutExpired:
        report = _failed_report(expected, "private Rust verifier timed out")
        report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        return 1
    except OSError as exc:
        report = _failed_report(expected, f"private Rust verifier could not start: {exc}")
        report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        return 1
    output = completed.stdout.encode("utf-8")
    if len(output) > MAX_OUTPUT_BYTES:
        report = _failed_report(expected, "private Rust verifier output exceeded the limit")
        report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        return 1
    if completed.returncode not in {0, 1}:
        return 70
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        return 70
    try:
        payload = json.loads(lines[0])
        if not isinstance(payload, dict):
            raise ValueError("private Rust verifier report must be an object")
        report, effective_exit = _adapt_report(payload, expected, completed.returncode)
    except (json.JSONDecodeError, TypeError, ValueError):
        return 70
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
    return effective_exit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entrypoint", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--timeout-sec", type=float, default=300.0)
    args = parser.parse_args()
    return run(args.entrypoint, args.report, args.expected, args.timeout_sec)


if __name__ == "__main__":
    raise SystemExit(main())
