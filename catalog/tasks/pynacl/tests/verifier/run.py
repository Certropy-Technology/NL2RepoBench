from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
RESULT_PREFIX = "NL2REPO_PYNACL_RESULT="
MAX_OUTPUT_BYTES = 1024 * 1024
PER_CALL_TIMEOUT_SEC = 5.0
TOTAL_CALL_BUDGET_SEC = 60.0


def _load_expected() -> dict[str, Any]:
    path = Path(__file__).resolve().parent / "expected.json"
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or len(value) != 49:
        raise ValueError("expected vector set is invalid")
    return value


def _stage_adapter() -> Path:
    source = Path(__file__).resolve().parent / "adapter.py"
    target = Path("/tmp/pynacl-candidate-adapter.py")
    target.write_bytes(source.read_bytes())
    os.chown(target, 10001, 10001)
    os.chmod(target, 0o500)
    return target


def _cleanup_candidate() -> None:
    for _ in range(5):
        pids: list[int] = []
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue
            try:
                status = (entry / "status").read_text(errors="replace")
                uid_line = next(
                    line for line in status.splitlines() if line.startswith("Uid:")
                )
                if int(uid_line.split()[1]) == 10001:
                    pids.append(int(entry.name))
            except (FileNotFoundError, PermissionError, StopIteration, ValueError):
                continue
        if not pids:
            return
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.05)


def invoke(adapter: Path, scenario: str, timeout: float) -> dict[str, Any]:
    environment = [
        "HOME=/tmp/candidate-build/home",
        "TMPDIR=/tmp/candidate-build/tmp",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
    ]
    command = [
        RUNUSER,
        "-u",
        "candidate",
        "--",
        "env",
        *environment,
        sys.executable,
        "-I",
        "-B",
        str(adapter),
        "--candidate-site",
        "/tmp/candidate-site",
        "--scenario",
        scenario,
    ]
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        process = subprocess.Popen(
            command,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return {
                "ok": False,
                "exception_type": "CandidateTimeout",
                "exception_message": f"scenario exceeded {timeout:.3f}s",
            }
        finally:
            _cleanup_candidate()
        stdout.seek(0)
        stderr.seek(0)
        output = stdout.read(MAX_OUTPUT_BYTES + 1)
        error = stderr.read(MAX_OUTPUT_BYTES + 1)
    if len(output) > MAX_OUTPUT_BYTES or len(error) > MAX_OUTPUT_BYTES:
        return {
            "ok": False,
            "exception_type": "CandidateOutputLimit",
            "exception_message": "candidate output exceeded limit",
        }
    if process.returncode != 0:
        return {
            "ok": False,
            "exception_type": "CandidateProcessError",
            "exception_message": error[-1000:].decode("utf-8", "replace"),
        }
    lines = [
        line
        for line in output.decode("utf-8", "replace").splitlines()
        if line.startswith(RESULT_PREFIX)
    ]
    if len(lines) != 1:
        return {
            "ok": False,
            "exception_type": "CandidateProtocolError",
            "exception_message": "expected exactly one result line",
        }
    try:
        result = json.loads(lines[0][len(RESULT_PREFIX) :])
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "exception_type": "CandidateProtocolError",
            "exception_message": str(exc),
        }
    if not isinstance(result, dict):
        return {
            "ok": False,
            "exception_type": "CandidateProtocolError",
            "exception_message": "result must be an object",
        }
    return result


def main() -> int:
    expected = _load_expected()
    adapter = _stage_adapter()
    leaves: list[dict[str, str]] = []
    deadline = time.monotonic() + TOTAL_CALL_BUDGET_SEC
    try:
        for scenario, expected_value in expected.items():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                result = {
                    "ok": False,
                    "exception_type": "CandidateBudgetExhausted",
                    "exception_message": "cumulative call budget exhausted",
                }
            else:
                result = invoke(
                    adapter,
                    scenario,
                    min(PER_CALL_TIMEOUT_SEC, remaining),
                )
            actual = (
                result.get("value")
                if result.get("ok") is True
                else {
                    "exception_message": result.get("exception_message"),
                    "exception_type": result.get("exception_type"),
                }
            )
            passed = actual == expected_value
            message = ""
            if not passed:
                message = json.dumps(
                    {"actual": actual, "expected": expected_value},
                    sort_keys=True,
                )[:2000]
            leaves.append(
                {
                    "id": f"pynacl/{scenario}",
                    "message": message,
                    "status": "passed" if passed else "failed",
                }
            )
    finally:
        adapter.unlink(missing_ok=True)
        _cleanup_candidate()
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
