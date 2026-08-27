"""Trusted custom-json-v1 verifier for the offline PyMongo behavior slice."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

EXPECTED_TOTAL = 51
CANDIDATE_SITE = "/tmp/candidate-site"
CANDIDATE_USER = "candidate"
CASE_TIMEOUT_SEC = 2.0
ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / "adapter.py"
CASES_PATH = ROOT / "cases.json"
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"


def _load_cases() -> list[dict[str, Any]]:
    document = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = document.get("cases")
    if document.get("schema_version") != "1.0" or not isinstance(cases, list):
        raise ValueError("invalid scenario document")
    identifiers: list[str] = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"id", "request", "expected"}:
            raise ValueError("invalid scenario record")
        identifier = case["id"]
        request = case["request"]
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("invalid scenario identifier")
        if request != {"schema_version": "1.0", "scenario": identifier}:
            raise ValueError("scenario request is not allowlisted")
        identifiers.append(identifier)
    if len(cases) != EXPECTED_TOTAL or len(set(identifiers)) != EXPECTED_TOTAL:
        raise ValueError("scenario denominator does not match the frozen total")
    return cases


def _invoke(adapter: Path, request: dict[str, str], workspace: Path) -> dict[str, Any]:
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
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=CASE_TIMEOUT_SEC,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "exception_type": "VerifierTimeout"}
    except OSError as exc:
        return {"ok": False, "exception_type": "VerifierProcessError", "message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        detail = (completed.stderr or completed.stdout)[-1200:]
        return {
            "ok": False,
            "exception_type": "CandidateProcessError",
            "message": f"exit={completed.returncode}: {detail}",
        }
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "message": str(exc)}
    if not isinstance(result, dict):
        return {"ok": False, "exception_type": "CandidateProtocolError"}
    return result


def main() -> int:
    try:
        cases = _load_cases()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 70

    leaves: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="pymongo-verifier-") as temporary:
        workspace = Path(temporary)
        shutil.chown(workspace, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(workspace, 0o700)
        adapter = workspace / "adapter.py"
        adapter.write_bytes(ADAPTER.read_bytes())
        shutil.chown(adapter, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(adapter, 0o500)

        for case in cases:
            result = _invoke(adapter, case["request"], workspace)
            passed = result == case["expected"]
            leaf: dict[str, str] = {
                "id": f"pymongo/{case['id']}",
                "status": "passed" if passed else "failed",
            }
            if not passed:
                leaf["message"] = json.dumps(
                    {"actual": result, "expected": case["expected"]},
                    ensure_ascii=True,
                    sort_keys=True,
                )[:1000]
            leaves.append(leaf)

    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
