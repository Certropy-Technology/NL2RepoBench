from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CASE_TIMEOUT = 20.0
ADDRESS_SPACE = 768 * 1024 * 1024


def _run_case(adapter: bytes, case: str) -> tuple[bool, str]:
    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        "PYTHONDONTWRITEBYTECODE=1",
        "prlimit",
        f"--as={ADDRESS_SPACE}",
        "--cpu=30",
        "--fsize=67108864",
        "--nofile=96",
        "--nproc=24",
        "--",
        sys.executable,
        "-I",
        "-B",
        "-",
        case,
    ]
    try:
        completed = subprocess.run(
            command,
            input=adapter,
            cwd="/workspace",
            capture_output=True,
            timeout=CASE_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, type(exc).__name__
    if completed.returncode != 0:
        return False, f"child-exit-{completed.returncode}"
    try:
        report = json.loads(completed.stdout.decode("utf-8").splitlines()[-1])
    except (IndexError, UnicodeDecodeError, json.JSONDecodeError):
        return False, "child-report-invalid"
    if report.get("case") != case:
        return False, "child-case-mismatch"
    return True, json.dumps(report.get("value"), ensure_ascii=False, sort_keys=True, default=str)


def main() -> None:
    private = Path(__file__).resolve().parent
    expected = json.loads((private / "expected.json").read_text(encoding="utf-8"))
    adapter = (private / "adapter.py").read_bytes()
    leaves = []
    for case in sorted(expected):
        ok, actual = _run_case(adapter, case)
        expected_value = json.dumps(expected[case], ensure_ascii=False, sort_keys=True, default=str)
        passed = ok and actual == expected_value
        leaf = {"id": f"markdown-it-py::{case}", "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = "observation mismatch" if ok else actual
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
