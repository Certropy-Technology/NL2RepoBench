from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"

SCENARIOS: dict[str, Any] = {
    "metadata": {"version": "1.5.4", "failure_base": "shellingham._core.OSError"},
    "exports": ["ShellDetectionFailure", "detect_shell"],
    "exception-identity": True,
    "shell-names": {"bash": ["bash", "bash"], "ZSH": ["zsh", "ZSH"], "fish": ["fish", "fish"]},
    "login-env": ["login-shell", "/custom/login-shell"],
    "login-fallback": ["bash", "/bin/bash"],
    "qemu-forwarding": ["bash", "/usr/bin/bash"],
    "xonsh-script": ["xonsh", "/tmp/candidate-site/xonsh"],
    "parent-order": ["zsh", "/usr/bin/zsh"],
    "depth-bound": {"one": None, "two": ["bash", "bash"]},
    "no-shell": None,
    "dispatch-success": ["bash", "bash"],
    "proc-stat": "stat",
    "proc-status": "status",
    "proc-invalid": "shellingham.posix.proc.ProcFormatError",
    "proc-parents": [["prog"], ["bash"]],
    "proc-cmdline": ["python", "-m", "demo"],
    "proc-string-pid": ["7", "8"],
    "ps-bytes": [["python", "-m", "demo"], ["bash"]],
    "ps-malformed": [["python"]],
    "ps-depth": [["python"]],
    "ps-empty": [],
    "ps-missing": "shellingham.posix.ps.PsNotAvailable",
    "dispatch-fallback": ["bash", "bash"],
}


def invoke(scenario: str) -> dict[str, Any]:
    if scenario == "xonsh-script":
        try:
            Path("/tmp/candidate-site/xonsh").unlink()
        except FileNotFoundError:
            pass
    adapter_path = Path(__file__).resolve().parent / "adapter.py"
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
        "-",
        "--candidate-site",
        "/tmp/candidate-site",
        "--scenario",
        scenario,
    ]
    try:
        completed = subprocess.run(
            command,
            input=adapter_path.read_text(encoding="utf-8"),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__module__ + "." + type(exc).__name__}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": completed.stderr[-1000:]}
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return result if isinstance(result, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def main() -> int:
    leaves = []
    for scenario, expected in SCENARIOS.items():
        result = invoke(scenario)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        passed = actual == expected
        leaves.append({
            "id": f"shellingham/{scenario}",
            "status": "passed" if passed else "failed",
            "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1000],
        })
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
