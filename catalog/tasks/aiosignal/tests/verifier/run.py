from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
SCENARIOS: dict[str, Any] = {
    "empty-frozen": {"before": [0, False], "after": [0, True]},
    "positional-forwarding": {"seen": [[42, "ok"]], "result": None},
    "keyword-forwarding": [{"alpha": 1, "beta": "two"}],
    "order-and-mixed-forwarding": [
        ["first", ["a", "b"], {"flag": True}],
        ["second", ["a", "b"], {"flag": True}],
    ],
    "reject-non-callable": "builtins.TypeError",
    "reject-non-awaitable": "builtins.TypeError",
    "append-after-freeze": {"error": "builtins.RuntimeError", "length": 1},
    "set-after-freeze": {"error": "builtins.RuntimeError", "length": 1},
    "delete-after-freeze": {"error": "builtins.RuntimeError", "length": 1},
    "send-before-freeze": {"error": "builtins.RuntimeError", "called": False},
    "decorator-registration": {"same": True, "seen": ["called"]},
    "repr": "<Signal owner=<Owner>, frozen=False, [",
    "stop-on-error": {"error": "builtins.ValueError", "seen": ["before-error"]},
}


def invoke(scenario: str) -> dict[str, Any]:
    command = [
        RUNUSER,
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/tmp",
        "TMPDIR=/tmp",
        "NL2REPO_CANDIDATE_DEPENDENCIES=/opt/candidate-dependencies/site",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        sys.executable,
        "-I",
        "-B",
        str(Path(__file__).resolve().parent / "adapter.py"),
        "--candidate-site",
        "/tmp/candidate-site",
        "--scenario",
        scenario,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": completed.stderr[-1000:]}
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return result if isinstance(result, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def main() -> int:
    leaves = []
    for scenario, expected in SCENARIOS.items():
        result = invoke(scenario)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        if scenario == "repr" and isinstance(actual, str):
            passed = actual.startswith(expected)
        else:
            passed = actual == expected
        leaves.append({"id": f"aiosignal/{scenario}", "status": "passed" if passed else "failed", "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1000]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
