from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


RUNUSER = "/usr/sbin/runuser"
ADAPTER = Path(__file__).with_name("adapter.py")
EXPECTED = Path(__file__).with_name("expected.json")
CANDIDATE_ADAPTER = Path("/tmp/python-multipart-adapter.py")


def invoke() -> dict[str, Any]:
    shutil.copyfile(ADAPTER, CANDIDATE_ADAPTER)
    os.chown(CANDIDATE_ADAPTER, 10001, 10001)
    os.chmod(CANDIDATE_ADAPTER, 0o500)
    command = [
        RUNUSER,
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/tmp",
        "TMPDIR=/tmp",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        sys.executable,
        "-I",
        "-B",
        str(CANDIDATE_ADAPTER),
        "--candidate-site",
        "/tmp/candidate-site",
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=240, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "results": {}, "diagnostic": type(exc).__name__ + ": " + str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {
            "ok": False,
            "results": {},
            "diagnostic": f"returncode={completed.returncode} lines={len(lines)} stderr={completed.stderr[-1000:]}",
        }
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "results": {}, "diagnostic": "json=" + str(exc)}
    return value if isinstance(value, dict) else {"ok": False, "results": {}}


def main() -> int:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    report = invoke()
    actual = report.get("results", {}) if report.get("ok") is True else {}
    leaves = []
    for name in sorted(expected):
        wanted = expected[name]
        observed = actual.get(name)
        passed = observed == wanted
        leaves.append(
            {
                "id": "python-multipart/" + name,
                "status": "passed" if passed else "failed",
                "message": "" if passed else json.dumps({"actual": observed, "expected": wanted}, sort_keys=True)[:1500],
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
