#!/usr/bin/env python3
"""Trusted parent for the fixed sortedcontainers scenario slice."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

EXPECTED_TOTAL = 30
ADAPTER = Path(__file__).with_name("adapter.py")
CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
CASE_TIMEOUT_SEC = 12.0
SCENARIOS = (
    "api-surface",
    "sorted-list-init-order",
    "sorted-list-mutations",
    "sorted-list-sequence",
    "sorted-list-delete-pop",
    "sorted-list-bisect-count-index",
    "sorted-list-islice",
    "sorted-list-irange",
    "sorted-list-operators-copy",
    "sorted-key-list-init-stability",
    "sorted-key-list-mutations",
    "sorted-key-list-key-range",
    "sorted-key-list-value-queries",
    "sorted-set-init-sequence",
    "sorted-set-mutations",
    "sorted-set-delete-pop",
    "sorted-set-range-bisect",
    "sorted-set-algebra",
    "sorted-set-inplace-operations",
    "sorted-set-key-order",
    "sorted-dict-init-order",
    "sorted-dict-mutations",
    "sorted-dict-pop-peek",
    "sorted-dict-range-bisect",
    "sorted-dict-key-order",
    "sorted-dict-live-views",
    "sorted-dict-view-set-operations",
    "sorted-dict-union",
    "copy-independence",
    "error-contracts",
)


def run_case(scenario: str) -> dict[str, str]:
    command = [
        sys.executable,
        "-I",
        "-B",
        "-",
        "--candidate-site",
        CANDIDATE_SITE,
        "--scenario",
        scenario,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") != "1":
        command = [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "HOME=/home/candidate",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            *command,
        ]
    try:
        completed = subprocess.run(
            command,
            input=ADAPTER.read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=CASE_TIMEOUT_SEC,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"id": scenario, "status": "failed", "message": "child timeout"}
    except OSError as exc:
        return {"id": scenario, "status": "failed", "message": f"child error: {exc}"}

    lines = [
        line
        for line in completed.stdout.decode("utf-8", "replace").splitlines()
        if line.strip()
    ]
    if completed.returncode != 0 or len(lines) != 1:
        detail = (
            completed.stderr.decode("utf-8", "replace")
            or completed.stdout.decode("utf-8", "replace")
        )[-1200:]
        return {
            "id": scenario,
            "status": "failed",
            "message": f"invalid child process (exit {completed.returncode}): {detail}",
        }
    try:
        verdict = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {
            "id": scenario,
            "status": "failed",
            "message": f"invalid child verdict: {exc}",
        }
    if verdict.get("scenario") != scenario or verdict.get("status") != "passed":
        return {
            "id": scenario,
            "status": "failed",
            "message": str(verdict.get("message", "scenario failed"))[-1200:],
        }
    return {"id": scenario, "status": "passed"}


def main() -> int:
    leaves = [run_case(scenario) for scenario in SCENARIOS]
    if len(leaves) != EXPECTED_TOTAL or {leaf["id"] for leaf in leaves} != set(SCENARIOS):
        leaves = [
            {"id": scenario, "status": "failed", "message": "leaf set mismatch"}
            for scenario in SCENARIOS
        ]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
