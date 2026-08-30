from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from nl2repobench.verification.process_cleanup import terminate_uid_processes


CANDIDATE_UID = 10001
BATCH_SIZE = 8
BATCH_TIMEOUT_SEC = 25.0
TOTAL_TIMEOUT_SEC = 180.0
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
ROOT = Path(__file__).resolve().parent
PROBE = (ROOT / "probe.py").read_text(encoding="utf-8")
CASES = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))


def _run_batch(requests: list[dict[str, Any]], deadline: float) -> list[Any]:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("candidate cumulative execution budget exhausted")
    dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    environment = [
        "HOME=/home/candidate",
        "PYTHONDONTWRITEBYTECODE=1",
        "NL2REPO_CANDIDATE_SITE=/tmp/candidate-site",
    ]
    if dependency_root:
        environment.append(f"NL2REPO_CANDIDATE_DEPENDENCIES={dependency_root}")
    process = subprocess.Popen(
        [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            *environment,
            "prlimit",
            "--as=1073741824",
            "--cpu=20",
            "--fsize=2097152",
            "--nofile=96",
            "--nproc=48",
            "--",
            sys.executable,
            "-I",
            "-B",
            "-c",
            PROBE,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(
            json.dumps({"batch": requests}, separators=(",", ":")),
            timeout=min(BATCH_TIMEOUT_SEC, remaining),
        )
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        raise TimeoutError("candidate batch timed out") from None
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        terminate_uid_processes(CANDIDATE_UID)
    if len(stdout.encode()) > MAX_OUTPUT_BYTES or len(stderr.encode()) > MAX_OUTPUT_BYTES:
        raise RuntimeError("candidate output exceeds limit")
    if process.returncode != 0:
        raise RuntimeError((stderr or stdout or "candidate probe failed")[-2000:])
    lines = [line for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("candidate probe returned invalid response count")
    response = json.loads(lines[0])
    if not isinstance(response, dict) or response.get("ok") is not True:
        raise RuntimeError(f"candidate error: {response!r}")
    values = response.get("value")
    if not isinstance(values, list) or len(values) != len(requests):
        raise RuntimeError("candidate probe returned invalid batch length")
    return values


def _matches(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and set(actual) == set(expected) and all(
            _matches(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(_matches(left, right) for left, right in zip(actual, expected))
        )
    if isinstance(expected, float):
        return isinstance(actual, (int, float)) and abs(float(actual) - expected) <= 1e-12
    return actual == expected


deadline = time.monotonic() + TOTAL_TIMEOUT_SEC
leaves: list[dict[str, str]] = []
for start in range(0, len(CASES), BATCH_SIZE):
    batch = CASES[start : start + BATCH_SIZE]
    try:
        actual_values = _run_batch([item["request"] for item in batch], deadline)
        batch_error = None
    except BaseException as error:
        actual_values = [None] * len(batch)
        batch_error = f"{type(error).__name__}: {error}"
    for case, actual in zip(batch, actual_values):
        passed = batch_error is None and _matches(actual, case["expected"])
        leaf = {"id": case["id"], "status": "passed" if passed else "failed"}
        if not passed:
            message = batch_error or f"expected {case['expected']!r}, got {actual!r}"
            leaf["message"] = message[:2000]
        leaves.append(leaf)

print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
