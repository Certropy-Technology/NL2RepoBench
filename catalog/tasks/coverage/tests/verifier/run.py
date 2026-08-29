"""Trusted scenario driver for the coverage.py task."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_TOTAL = 12
CANDIDATE_SITE = "/tmp/candidate-site"
CANDIDATE_USER = "candidate"
CASE_TIMEOUT_SEC = 15.0
ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / "adapter.py"
CASES_PATH = ROOT / "cases.json"
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"


def _load_cases() -> list[dict[str, Any]]:
    document = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = document.get("cases")
    if document.get("schema_version") != "1.0" or not isinstance(cases, list):
        raise ValueError("invalid scenario document")
    ids: list[str] = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"id", "request", "expected"}:
            raise ValueError("invalid scenario record")
        identifier = case["id"]
        request = case["request"]
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("invalid scenario identifier")
        if request != {"schema_version": "1.0", "scenario": identifier}:
            raise ValueError("scenario request is not allowlisted")
        ids.append(identifier)
    if len(cases) != EXPECTED_TOTAL or len(set(ids)) != EXPECTED_TOTAL:
        raise ValueError("scenario denominator does not match frozen total")
    return cases


def _kill_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, 9)
    except ProcessLookupError:
        pass


def _invoke(request: dict[str, str], workspace: Path, adapter: Path) -> dict[str, Any]:
    payload = json.dumps(request, sort_keys=True, separators=(",", ":"))
    command = [
        RUNUSER,
        "-u",
        CANDIDATE_USER,
        "--",
        "env",
        f"HOME={workspace}",
        f"TMPDIR={workspace}",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "LANG=C.UTF-8",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        sys.executable,
        "-I",
        "-B",
        str(adapter),
        "--candidate-site",
        CANDIDATE_SITE,
        "--request",
        payload,
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=CASE_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        _kill_group(process)
        process.wait(timeout=5)
        return {"ok": False, "exception_type": "VerifierTimeout", "exception_message": "scenario timed out"}
    if process.returncode != 0:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": f"exit={process.returncode}: {stderr[-1200:]}"}
    lines = [line for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": f"output lines={len(lines)}"}
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    if not isinstance(result, dict):
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": "response is not an object"}
    return result


def main() -> int:
    cases = _load_cases()
    leaves: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="coverage-verifier-") as raw:
        workspace = Path(raw)
        shutil.chown(workspace, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(workspace, 0o700)
        adapter = workspace / "adapter.py"
        adapter.write_bytes(ADAPTER.read_bytes())
        shutil.chown(adapter, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(adapter, 0o500)
        for case in cases:
            result = _invoke(case["request"], workspace, adapter)
            passed = result.get("ok") is True and result.get("value") == case["expected"]
            leaf: dict[str, str] = {"id": f"coverage/{case['id']}", "status": "passed" if passed else "failed"}
            if not passed:
                leaf["message"] = json.dumps({"actual": result, "expected": case["expected"]}, sort_keys=True)[:1000]
            leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
