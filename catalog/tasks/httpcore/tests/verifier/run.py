#!/usr/bin/env python3
"""Trusted parent for the fixed httpcore child-side behavior suite."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EXPECTED_TOTAL = 24
SCENARIOS = (
    "api-surface",
    "url-origin-proxy",
    "request-model",
    "response-buffered",
    "response-sync-stream",
    "response-async-stream",
    "mock-stream",
    "http11-basic",
    "http11-post-body",
    "http11-interim",
    "http11-upgrade",
    "http11-errors",
    "http11-lifecycle",
    "pool-keepalive",
    "pool-close-header",
    "pool-trace",
    "async-http11-basic",
    "async-http11-interim",
    "async-pool-keepalive",
    "async-trace",
    "http2-basic",
    "interfaces",
    "exception-contracts",
    "deterministic-projection",
)
CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
ADAPTER = Path(__file__).with_name("adapter.py")


def run_case(scenario: str, adapter: Path, workspace: Path) -> dict[str, str]:
    output = workspace / f"{scenario}.json"
    command = [
        RUNUSER,
        "-u",
        "candidate",
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
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=20, check=False
        )
    except subprocess.TimeoutExpired:
        return {"id": scenario, "status": "failed", "message": "child timeout"}
    except OSError as exc:
        return {"id": scenario, "status": "failed", "message": f"child error: {exc}"}
    if not output.is_file():
        detail = (completed.stderr or completed.stdout)[-1600:]
        return {
            "id": scenario,
            "status": "failed",
            "message": f"no child verdict (exit {completed.returncode}): {detail}",
        }
    try:
        verdict = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"id": scenario, "status": "failed", "message": f"invalid verdict: {exc}"}
    if verdict.get("status") != "passed":
        return {
            "id": scenario,
            "status": "failed",
            "message": str(verdict.get("message", "scenario failed"))[-1600:],
        }
    return {"id": scenario, "status": "passed"}


def main() -> int:
    leaves: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="httpcore-verifier-") as temporary:
        workspace = Path(temporary)
        shutil.chown(workspace, "candidate", "candidate")
        os.chmod(workspace, 0o700)
        adapter = workspace / "adapter.py"
        adapter.write_bytes(ADAPTER.read_bytes())
        shutil.chown(adapter, "candidate", "candidate")
        os.chmod(adapter, 0o500)
        for scenario in SCENARIOS:
            leaves.append(run_case(scenario, adapter, workspace))
    if len(leaves) != EXPECTED_TOTAL or {leaf["id"] for leaf in leaves} != set(SCENARIOS):
        leaves = [
            {"id": scenario, "status": "failed", "message": "leaf set mismatch"}
            for scenario in SCENARIOS
        ]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
