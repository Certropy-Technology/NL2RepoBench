from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import tempfile


CASES = (
    "package-metadata",
    "version",
    "help-check",
    "check-clean",
    "check-f401",
    "check-json",
    "check-stdin",
    "check-noqa",
    "check-ignore-config",
    "check-isolated-config",
    "check-e501-config",
    "check-missing-config",
    "fix-f401",
    "no-fix",
    "format-stdin",
    "format-check",
    "format-write",
    "format-diff",
    "format-function",
    "rule-f401",
)
ROOT = Path(__file__).resolve().parent
MAX_OUTPUT_BYTES = 1024 * 1024


def candidate_command(adapter: Path) -> list[str]:
    command = [
        "env",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        "NL2REPO_RUFF_CANDIDATE_SITE=/tmp/candidate-site",
        "prlimit",
        "--as=1073741824",
        "--cpu=12",
        f"--fsize={MAX_OUTPUT_BYTES}",
        "--nofile=64",
        "--nproc=24",
        "--",
        sys.executable,
        "-I",
        str(adapter),
    ]
    if os.geteuid() == 0:
        try:
            pwd.getpwnam("candidate")
        except KeyError:
            pass
        else:
            command = ["runuser", "-u", "candidate", "--", *command]
    return command


def run_case(adapter: Path, case_id: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="ruff-verifier-") as temporary:
        try:
            completed = subprocess.run(
                candidate_command(adapter),
                input=json.dumps({"id": case_id}),
                text=True,
                capture_output=True,
                timeout=3,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False, "candidate-timeout"
        except (OSError, subprocess.SubprocessError) as exc:
            return False, f"{type(exc).__name__}: {exc}"
    if len(completed.stdout) > MAX_OUTPUT_BYTES or len(completed.stderr) > MAX_OUTPUT_BYTES:
        return False, "candidate-output-limit"
    try:
        payload = json.loads(completed.stdout.splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        payload = None
    passed = completed.returncode == 0 and payload == {"id": case_id, "ok": True}
    diagnostic = (
        f"candidate-exit={completed.returncode}; stderr="
        f"{completed.stderr[-800:].replace(chr(10), ' ')}"
    )
    return passed, diagnostic


def main() -> None:
    adapter = Path("/tmp/ruff-contract-adapter.py")
    shutil.copyfile(ROOT / "adapter.py", adapter)
    adapter.chmod(0o444)
    leaves = []
    for case_id in CASES:
        passed, diagnostic = run_case(adapter, case_id)
        leaves.append(
            {
                "id": f"ruff-contract::{case_id}",
                "status": "passed" if passed else "failed",
                "message": "" if passed else diagnostic,
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
