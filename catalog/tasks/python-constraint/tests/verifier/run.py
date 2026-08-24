#!/usr/bin/env python3
"""Trusted parent for python-constraint scenario leaves.

The parent never imports the candidate. It launches the fixed adapter as the
unprivileged candidate user and sends only one allowlisted scenario token.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED_TOTAL = 16
CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
CANDIDATE_USER = "candidate"
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
ADAPTER = Path(__file__).with_name("adapter.py")
SCENARIOS = (
    "domain-nested-state",
    "problem-domain-copy",
    "callable-order-and-generator",
    "custom-constraint-forward-check",
    "backtracking-family-equivalence",
    "string-constraint-solve",
    "numeric-and-set-constraints",
    "parser-specialization",
    "parser-operator-helpers",
    "lazy-solution-iterator",
    "min-conflicts-seeded",
    "parallel-thread-solutions",
    "parallel-process-string-solutions",
    "parallel-process-callable-rejection",
    "unsatisfiable-and-empty-problems",
    "repeated-solves-stable",
)
CASE_TIMEOUT_SEC = 20.0


def run_case(scenario: str, adapter: Path, workspace: Path) -> dict[str, str]:
    output = workspace / (scenario.replace("/", "_") + ".json")
    command = [
        RUNUSER,
        "-u",
        CANDIDATE_USER,
        "--",
        "env",
        "HOME=/home/candidate",
        "TMPDIR=/tmp",
        "PYTHONDONTWRITEBYTECODE=1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
        sys.executable,
        "-I",
        "-B",
        str(adapter),
        "--scenario",
        scenario,
        "--candidate-site",
        CANDIDATE_SITE,
        "--output",
        str(output),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=CASE_TIMEOUT_SEC, check=False)
    except subprocess.TimeoutExpired:
        return {"id": scenario, "status": "failed", "message": "child timeout"}
    except OSError as exc:
        return {"id": scenario, "status": "failed", "message": f"child error: {exc}"}
    if not output.is_file():
        detail = (completed.stderr or completed.stdout)[-1200:]
        return {"id": scenario, "status": "failed", "message": f"no child verdict (exit {completed.returncode}): {detail}"}
    try:
        verdict = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"id": scenario, "status": "failed", "message": f"invalid child verdict: {exc}"}
    if verdict.get("status") != "passed":
        return {"id": scenario, "status": "failed", "message": str(verdict.get("message", "scenario failed"))[-1200:]}
    return {"id": scenario, "status": "passed"}


def main() -> int:
    leaves = []
    with tempfile.TemporaryDirectory(prefix="python-constraint-verifier-") as temporary:
        workspace = Path(temporary)
        shutil.chown(workspace, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(workspace, 0o700)
        adapter = workspace / "adapter.py"
        adapter.write_bytes(ADAPTER.read_bytes())
        shutil.chown(adapter, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(adapter, 0o500)
        for scenario in SCENARIOS:
            leaves.append(run_case(scenario, adapter, workspace))
    if len(leaves) != EXPECTED_TOTAL or {leaf["id"] for leaf in leaves} != set(SCENARIOS):
        leaves = [{"id": scenario, "status": "failed", "message": "leaf set mismatch"} for scenario in SCENARIOS]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
