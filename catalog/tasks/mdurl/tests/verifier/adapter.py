from __future__ import annotations

import json
import os
import subprocess
import sys


def run_candidate(source: str) -> dict[str, object]:
    runner = os.environ.get(
        "NL2REPO_CANDIDATE_RUNNER",
        "/usr/local/lib/python3.12/site-packages/nl2repobench/verification/candidate_runner.py",
    )
    command = [
        "/usr/sbin/runuser",
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
        runner,
        "--candidate-site",
        "/tmp/candidate-site",
        "script",
    ]
    try:
        completed = subprocess.run(
            command,
            input=json.dumps({"source": source}),
            text=True,
            capture_output=True,
            timeout=45,
            check=False,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/tmp", "TMPDIR": "/tmp"},
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [
        line
        for line in completed.stdout.splitlines()
        if line.startswith("NL2REPO_CANDIDATE_RESULT=")
    ]
    if completed.returncode != 0 or len(lines) != 1:
        return {
            "ok": False,
            "exception_type": "CandidateProcessError",
            "exception_message": completed.stderr[-1000:],
        }
    try:
        payload = json.loads(lines[0].split("=", 1)[1])
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "exception_type": "CandidateProtocolError",
            "exception_message": str(exc),
        }
    if isinstance(payload, dict):
        return payload
    return {"ok": False, "exception_type": "CandidateProtocolError"}
