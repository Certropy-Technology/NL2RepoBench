#!/usr/bin/env python3
"""Run fixed distro scenarios in UID-isolated candidate subprocesses."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCENARIOS = (
    "api-surface",
    "os-release-instance",
    "normalization-and-versions",
    "release-file-fallback",
    "root-isolation",
    "global-accessors",
    "deprecated-compatibility",
    "cli-text",
    "cli-json",
    "source-accessors",
    "constructor-contract",
    "metadata-and-determinism",
    "missing-data",
    "version-best",
    "local-only-behavior",
)
EXPECTED_TOTAL = len(SCENARIOS)
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
ADAPTER = Path(__file__).with_name("adapter.py")


def run_scenario(scenario: str, adapter: Path, root: Path) -> dict[str, str]:
    output = root / f"{scenario}.json"
    command = [
        RUNUSER,
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/home/candidate",
        "TMPDIR=/tmp",
        "PYTHONDONTWRITEBYTECODE=1",
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
        completed = subprocess.run(command, capture_output=True, text=True, timeout=2, check=False)
    except subprocess.TimeoutExpired:
        return {"id": scenario, "status": "failed", "message": "child timeout"}
    except OSError as exc:
        return {"id": scenario, "status": "failed", "message": f"child error: {exc}"}
    if not output.is_file():
        detail = (completed.stderr or completed.stdout)[-1200:]
        return {"id": scenario, "status": "failed", "message": f"no verdict (exit {completed.returncode}): {detail}"}
    try:
        verdict = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"id": scenario, "status": "failed", "message": f"invalid verdict: {exc}"}
    if verdict.get("status") != "passed":
        return {"id": scenario, "status": "failed", "message": str(verdict.get("message", "scenario failed"))[-1200:]}
    return {"id": scenario, "status": "passed"}


def main() -> int:
    leaves: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="distro-verifier-") as temporary:
        root = Path(temporary)
        shutil.chown(root, "candidate", "candidate")
        os.chmod(root, 0o700)
        child_adapter = root / "adapter.py"
        child_adapter.write_bytes(ADAPTER.read_bytes())
        shutil.chown(child_adapter, "candidate", "candidate")
        os.chmod(child_adapter, 0o500)
        for scenario in SCENARIOS:
            leaves.append(run_scenario(scenario, child_adapter, root))
    if len(leaves) != EXPECTED_TOTAL or {leaf["id"] for leaf in leaves} != set(SCENARIOS):
        leaves = [{"id": scenario, "status": "failed", "message": "leaf set mismatch"} for scenario in SCENARIOS]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
