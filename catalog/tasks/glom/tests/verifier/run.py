"""Trusted parent for deterministic glom child scenarios."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ADAPTER = Path(__file__).with_name("adapter.py")
EXPECTED = json.loads(Path(__file__).with_name("expected.json").read_text(encoding="utf-8"))
SCHEMA_VERSION = "glom-scenarios-v1"
CHILD_TIMEOUT_SEC = 15.0


CASE_IDS = (
    "api-surface",
    "basic-access",
    "explicit-path",
    "construction-and-t",
    "call-and-invoke",
    "coalesce-contract",
    "val-fill-pipe",
    "ref-recursive",
    "spec-scope",
    "match-mapping",
    "match-logic",
    "check-and-switch",
    "match-error",
    "path-error",
    "assign-existing",
    "assign-missing",
    "assign-spec",
    "delete-contract",
    "iter-map-filter",
    "iter-chunk-window",
    "iter-unique-slice",
    "iter-flatten-split",
    "iter-terminal",
    "reductions",
    "fold-custom",
    "grouping",
    "glommer-registry",
    "cli-json",
)


def invoke(case_id: str) -> dict:
    request = {"case_id": case_id, "schema_version": SCHEMA_VERSION}
    payload = json.dumps(request, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    command = [
        "runuser", "-u", "candidate", "--", "env",
        "HOME=/home/candidate", "PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0",
        "PYTHONNOUSERSITE=1", "LC_ALL=C.UTF-8", "TZ=UTC",
        "NL2REPO_CANDIDATE_DEPENDENCIES="
        + os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"),
        sys.executable, "-I", "-B", "-",
        "--candidate-site", os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--request", payload,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") == "1":
        command = [
            sys.executable, "-I", "-B", "-",
            "--candidate-site", os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
            "--request", payload,
        ]
    try:
        completed = subprocess.run(
            command,
            input=ADAPTER.read_bytes(),
            capture_output=True,
            timeout=CHILD_TIMEOUT_SEC,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"exception_message": str(error), "exception_type": "VerifierProcessError", "ok": False}
    lines = [line for line in completed.stdout.decode("utf-8", "replace").splitlines() if line]
    if completed.returncode != 0 or len(lines) != 1:
        detail = completed.stderr.decode("utf-8", "replace") or completed.stdout.decode("utf-8", "replace")
        return {"exception_message": detail[-2000:], "exception_type": "CandidateProcessError", "ok": False}
    try:
        response = json.loads(lines[0])
    except json.JSONDecodeError as error:
        return {"exception_message": str(error), "exception_type": "CandidateProtocolError", "ok": False}
    return response if isinstance(response, dict) else {"ok": False}


def main() -> None:
    if set(EXPECTED) != set(CASE_IDS):
        raise RuntimeError("expected scenario IDs do not match requests")
    leaves = []
    for case_id in CASE_IDS:
        response = invoke(case_id)
        expected = EXPECTED[case_id]
        passed = response.get("ok") is True and response.get("value") == expected
        leaf = {"id": f"glom/{case_id}", "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = json.dumps(
                {"actual": response, "expected": expected},
                ensure_ascii=False,
                sort_keys=True,
            )[:1200]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
