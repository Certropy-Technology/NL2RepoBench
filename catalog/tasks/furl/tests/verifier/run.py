from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def main() -> int:
    command = [
        "/usr/bin/runuser",
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/tmp",
        "TMPDIR=/tmp",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE=1",
        sys.executable,
        "-I",
        "-B",
        str(Path(__file__).with_name("adapter.py")),
        "--candidate-site",
        "/tmp/candidate-site",
        "--dependency-site",
        "/opt/candidate-dependencies/site",
        "--tests",
        "/tests/verifier/private_tests",
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=300, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"schema_version": "1.0", "leaves": [], "error": str(exc)}))
        return 0
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        print(json.dumps({"schema_version": "1.0", "leaves": [], "error": completed.stderr[-1200:]}))
        return 0
    try:
        report: dict[str, Any] = json.loads(lines[-1])
    except json.JSONDecodeError:
        print(json.dumps({"schema_version": "1.0", "leaves": [], "error": completed.stderr[-1200:]}))
        return 0
    if completed.returncode not in {0, 1}:
        report["error"] = completed.stderr[-1200:]
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
