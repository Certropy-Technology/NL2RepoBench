from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED = Path(__file__).with_name("expected.json")
ADAPTER = Path(__file__).with_name("adapter.py")
MAX_OUTPUT_BYTES = 4 * 1024 * 1024
PREFIX = "NL2REPO_PYASN1_RESULT="


def invoke(scenario: str) -> dict[str, object]:
    command = [
        sys.executable,
        "-I",
        "-B",
        str(ADAPTER),
        "--candidate-site",
        "/tmp/candidate-site",
        "--scenario",
        scenario,
    ]
    environment = {
        "HOME": "/tmp/candidate-build/home",
        "TMPDIR": "/tmp/candidate-build/tmp",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            process = subprocess.run(command, env=environment, stdout=stdout, stderr=stderr, timeout=30, check=False, preexec_fn=_drop_candidate_privileges)
        except (OSError, subprocess.SubprocessError) as exc:
            return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
        stdout.seek(0)
        stderr.seek(0)
        out = stdout.read(MAX_OUTPUT_BYTES + 1)
        err = stderr.read(MAX_OUTPUT_BYTES + 1)
    if process.returncode != 0 or len(out) > MAX_OUTPUT_BYTES or len(err) > MAX_OUTPUT_BYTES:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": err[-2000:].decode("utf-8", "replace")}
    lines = [line for line in out.decode("utf-8", "replace").splitlines() if line.startswith(PREFIX)]
    if len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": "expected one result line"}
    try:
        value = json.loads(lines[0][len(PREFIX):])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return value if isinstance(value, dict) else {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": "result is not an object"}


def _drop_candidate_privileges() -> None:
    os.setgroups([])
    os.setgid(10001)
    os.setuid(10001)


def main() -> int:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    leaves = []
    for scenario, wanted in expected.items():
        result = invoke(scenario)
        actual = result.get("value") if result.get("ok") is True else {
            "exception_type": result.get("exception_type"),
            "exception_message": result.get("exception_message"),
        }
        passed = actual == wanted
        leaves.append({
            "id": f"pyasn1/{scenario}",
            "status": "passed" if passed else "failed",
            "message": "" if passed else json.dumps({"actual": actual, "expected": wanted}, sort_keys=True)[:2000],
        })
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
