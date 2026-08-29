#!/usr/bin/env python3
"""Private GitPython contract runner.

The trusted verifier only launches ``child.py``. Candidate code is imported in
that unprivileged child, never in this process.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CASES = tuple(f"gitpython-{index:02d}" for index in range(1, 21))
CHILD = Path(__file__).with_name("child.py")


def run_case(case: str) -> tuple[str, str]:
    environment = os.environ.copy()
    candidate = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
    dependencies = environment.get("NL2REPO_CANDIDATE_DEPENDENCIES", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (candidate, dependencies) if part
    )
    environment["GIT_TERMINAL_PROMPT"] = "0"
    try:
        completed = subprocess.run(
            [sys.executable, str(CHILD), case],
            cwd="/tmp",
            env=environment,
            capture_output=True,
            text=True,
            timeout=12.0,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return "failed", f"child launch failed: {exc}"
    if completed.returncode == 0:
        return "passed", ""
    detail = (completed.stderr or completed.stdout).strip().replace("\n", " ")
    return "failed", detail[-1200:] or f"child exit {completed.returncode}"


def main() -> None:
    leaves = []
    for case in CASES:
        status, message = run_case(case)
        leaf = {"id": case, "status": status}
        if message:
            leaf["message"] = message
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
