#!/usr/bin/env python3
"""Trusted parent for the frozen Hatchling subprocess scenarios."""
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
CANDIDATE_DEPENDENCIES = os.environ.get(
    "NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"
)
CANDIDATE_UID = 10001
CANDIDATE_USER = "candidate"
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
ADAPTER_SOURCE = Path(__file__).with_name("adapter.py")
EXPECTED = json.loads(Path(__file__).with_name("expected.json").read_text(encoding="utf-8"))
CASE_TIMEOUT_SEC = 20.0


def candidate_pids() -> list[int]:
    result = []
    for status in Path("/proc").glob("[0-9]*/status"):
        try:
            uid_line = next(line for line in status.read_text().splitlines() if line.startswith("Uid:"))
            if int(uid_line.split()[1]) == CANDIDATE_UID:
                result.append(int(status.parent.name))
        except (OSError, StopIteration, ValueError):
            pass
    return result


def cleanup() -> None:
    for _ in range(10):
        pids = candidate_pids()
        if not pids:
            return
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.02)
    if candidate_pids():
        raise RuntimeError("candidate processes survived cleanup")


def run_case(scenario: str, workspace: Path) -> dict[str, str]:
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
        f"NL2REPO_CANDIDATE_DEPENDENCIES={CANDIDATE_DEPENDENCIES}",
        "prlimit",
        "--as=805306368",
        "--cpu=15",
        "--fsize=33554432",
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
            command, capture_output=True, text=True, timeout=CASE_TIMEOUT_SEC, check=False
        )
    except subprocess.TimeoutExpired:
        cleanup()
        return {"id": scenario, "status": "failed", "message": "child timeout"}
    except OSError as error:
        cleanup()
        return {"id": scenario, "status": "failed", "message": f"child error: {error}"}
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
        if report.get("value") != EXPECTED[scenario]:
            return {
                "id": scenario,
                "status": "failed",
                "message": "observation mismatch: "
                + json.dumps(report.get("value"), ensure_ascii=False, sort_keys=True)[-1000:],
            }
        return {"id": scenario, "status": "passed", "message": ""}
    except (OSError, json.JSONDecodeError) as error:
        return {"id": scenario, "status": "failed", "message": f"invalid observation: {error}"}
    finally:
        cleanup()


def main() -> int:
    leaves = []
    try:
        with tempfile.TemporaryDirectory(prefix="hatchling-verifier-") as temporary:
            workspace = Path(temporary)
            os.chown(workspace, CANDIDATE_UID, CANDIDATE_UID)
            os.chmod(workspace, 0o700)
            for scenario in EXPECTED:
                leaves.append(run_case(scenario, workspace))
    except BaseException as error:
        print(
            f"hatchling verifier infrastructure error: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return 70
    if len(leaves) != len(EXPECTED) or {leaf["id"] for leaf in leaves} != set(EXPECTED):
        return 70
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
