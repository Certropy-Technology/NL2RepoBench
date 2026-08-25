#!/usr/bin/env python3
"""Trusted parent for the frozen schema 0.7.8 subprocess scenarios."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time


CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
CANDIDATE_UID = 10001
CANDIDATE_USER = "candidate"
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
ADAPTER_SOURCE = Path(__file__).with_name("adapter.py")
EXPECTED_SOURCE = Path(__file__).with_name("expected.json")
CASE_TIMEOUT_SEC = 15.0


def _candidate_pids() -> list[int]:
    result = []
    for status in Path("/proc").glob("[0-9]*/status"):
        try:
            uid_line = next(
                line
                for line in status.read_text(encoding="utf-8").splitlines()
                if line.startswith("Uid:")
            )
            if int(uid_line.split()[1]) == CANDIDATE_UID:
                result.append(int(status.parent.name))
        except (OSError, StopIteration, ValueError):
            pass
    return result


def _cleanup() -> None:
    for _ in range(10):
        pids = _candidate_pids()
        if not pids:
            return
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.02)
    if _candidate_pids():
        raise RuntimeError("candidate processes survived cleanup")


def run_case(scenario: str, expected: object, workspace: Path) -> dict[str, str]:
    case_root = workspace / scenario
    case_root.mkdir()
    os.chown(case_root, CANDIDATE_UID, CANDIDATE_UID)
    os.chmod(case_root, 0o700)
    adapter = case_root / "adapter.py"
    adapter.write_bytes(ADAPTER_SOURCE.read_bytes())
    os.chown(adapter, CANDIDATE_UID, CANDIDATE_UID)
    os.chmod(adapter, 0o500)
    output = case_root / "observation.json"
    command = [
        RUNUSER,
        "-u",
        CANDIDATE_USER,
        "--",
        "env",
        "HOME=/home/candidate",
        "TMPDIR=/tmp",
        "PYTHONDONTWRITEBYTECODE=1",
        "PYTHONNOUSERSITE=1",
        "PYTHONHASHSEED=0",
        "LC_ALL=C.UTF-8",
        "TZ=UTC",
        "prlimit",
        "--as=536870912",
        "--cpu=10",
        "--fsize=16777216",
        "--nofile=128",
        "--nproc=32",
        "--",
        sys.executable,
        "-I",
        "-B",
        str(adapter),
        "--scenario",
        scenario,
        "--candidate-site",
        CANDIDATE_SITE,
        "--output",
        str(output),
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
        _cleanup()
        return {"id": scenario, "status": "failed", "message": "child timeout"}
    except OSError as error:
        _cleanup()
        return {
            "id": scenario,
            "status": "failed",
            "message": f"child error: {error}",
        }
    try:
        if completed.returncode != 0 or not output.is_file():
            detail = (completed.stderr or completed.stdout)[-1200:]
            return {
                "id": scenario,
                "status": "failed",
                "message": f"no observation (exit {completed.returncode}): {detail}",
            }
        report = json.loads(output.read_text(encoding="utf-8"))
        if (
            report.get("schema_version") != "1.0"
            or report.get("scenario") != scenario
            or report.get("ok") is not True
        ):
            return {
                "id": scenario,
                "status": "failed",
                "message": json.dumps(report, sort_keys=True)[-1200:],
            }
        if report.get("value") != expected:
            detail = json.dumps(
                report.get("value"), ensure_ascii=False, sort_keys=True
            )[-1000:]
            return {
                "id": scenario,
                "status": "failed",
                "message": "observation mismatch: " + detail,
            }
        return {"id": scenario, "status": "passed", "message": ""}
    except (OSError, json.JSONDecodeError) as error:
        return {
            "id": scenario,
            "status": "failed",
            "message": f"invalid observation: {error}",
        }
    finally:
        _cleanup()


def main() -> int:
    leaves = []
    try:
        expected = json.loads(EXPECTED_SOURCE.read_text(encoding="utf-8"))
        if not isinstance(expected, dict) or len(expected) != 30:
            raise ValueError("expected scenario map must contain exactly 30 entries")
        # Candidate children run as UID 10001; hide trusted expectations before launch.
        EXPECTED_SOURCE.chmod(0o600)
        ADAPTER_SOURCE.chmod(0o600)
        with tempfile.TemporaryDirectory(prefix="schema-verifier-") as temporary:
            workspace = Path(temporary)
            os.chown(workspace, CANDIDATE_UID, CANDIDATE_UID)
            os.chmod(workspace, 0o700)
            for scenario, value in expected.items():
                leaves.append(run_case(scenario, value, workspace))
    except BaseException as error:
        print(
            f"schema verifier infrastructure error: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return 70
    if len(leaves) != len(expected) or {leaf["id"] for leaf in leaves} != set(expected):
        return 70
    print(
        json.dumps(
            {"schema_version": "1.0", "leaves": leaves},
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    # Leaf statuses carry candidate failures; a nonzero process status is
    # reserved for verifier infrastructure failures.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
