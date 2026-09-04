from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    child = Path(__file__).with_name("child.py")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [sys.executable, "-I", str(child)],
        cwd="/workspace",
        env=env,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    if completed.returncode != 0:
        print(json.dumps({"error": "child-exit", "detail": completed.stderr[-2000:]}))
        return 1
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        print(json.dumps({"error": "child-empty-output"}))
        return 1
    try:
        report = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": "child-invalid-json", "detail": str(exc)}))
        return 1
    if report.get("schema_version") != "1.0" or not isinstance(report.get("leaves"), list):
        print(json.dumps({"error": "child-invalid-report"}))
        return 1
    print(json.dumps(report, sort_keys=True))
    # The generic custom verifier wrapper owns the pytest-style exit code after
    # converting leaf statuses into JUnit and collection reports.  Returning
    # success here is therefore required even when behavioral leaves fail.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
