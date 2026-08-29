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
CASE_TIMEOUT_SEC = 4.0
TOTAL_TIMEOUT_SEC = 90.0
MAX_OUTPUT_BYTES = 1024 * 1024
PROBE = Path(__file__).with_name("probe.py").read_text(encoding="utf-8")


def success(identifier: str, operation: str, value: Any, **kwargs: Any) -> dict[str, Any]:
    request = {"operation": operation, **kwargs}
    return {"id": identifier, "request": request, "expected": value}


V4 = 2
V6 = 10
STREAM = 1
TCP = 6

CASES = [
    success("root-exports", "exports", {"all": ["AddrInfoType", "SocketFactoryType", "addr_to_addr_infos", "pop_addr_infos_interleave", "remove_addr_infos", "start_connection"], "version": "2.7.1", "typed": True}),
    success("distribution-metadata", "metadata", {"name": "aiohappyeyeballs", "version": "2.7.1", "requires": []}),
    success("addr-none", "addr-to", None, addr=None),
    success("addr-ipv4", "addr-to", [[V4, STREAM, TCP, "", ["127.0.0.1", 8080]]], addr=["127.0.0.1", 8080]),
    success("addr-ipv6-defaults", "addr-to", [[V6, STREAM, TCP, "", ["2001:db8::1", 443, 0, 0]]], addr=["2001:db8::1", 443]),
    success("addr-ipv6-flow-scope", "addr-to", [[V6, STREAM, TCP, "", ["2001:db8::1", 443, 5, 7]]], addr=["2001:db8::1", 443, 5, 7]),
    success("pop-default", "pop", [[V6, STREAM, TCP, "", ["::2", 2, 0, 0]], [V4, STREAM, TCP, "", ["127.0.0.2", 4]]], records=[[V6, "::1", 1], [V6, "::2", 2], [V4, "127.0.0.1", 3], [V4, "127.0.0.2", 4]]),
    success("pop-interleave-two", "pop", [[V6, STREAM, TCP, "", ["::3", 3, 0, 0]], [V4, STREAM, TCP, "", ["127.0.0.3", 6]]], records=[[V6, "::1", 1], [V6, "::2", 2], [V6, "::3", 3], [V4, "127.0.0.1", 4], [V4, "127.0.0.2", 5], [V4, "127.0.0.3", 6]], interleave=2),
    success("remove-exact", "remove", [[V6, STREAM, TCP, "", ["::1", 80, 0, 0]]], records=[[V4, "127.0.0.1", 80], [V6, "::1", 80]], addr=["127.0.0.1", 80]),
    success("remove-normalized-ipv6", "remove", [[V4, STREAM, TCP, "", ["127.0.0.1", 80]]], records=[[V6, "0:0:0:0:0:0:0:1", 80], [V4, "127.0.0.1", 80]], addr=["::1", 80, 0, 0]),
    success("remove-missing", "remove", {"error": "ValueError", "contains": True}, records=[[V4, "127.0.0.1", 80]], addr=["127.0.0.2", 80]),
    success("start-empty", "start-empty", {"error": "ValueError", "contains": True}),
    success("start-loopback", "start-loopback", {"peer": ["127.0.0.1", "__port__"], "bound_host": "127.0.0.1", "bound_port_positive": True, "factory_families": []}),
    success("start-sequential-fallback", "start-fallback", {"peer": ["127.0.0.1", "__port__"], "bound_host": "127.0.0.1", "bound_port_positive": True, "factory_families": []}),
    success("start-happy-fallback", "start-happy", {"peer": ["127.0.0.1", "__port__"], "bound_host": "127.0.0.1", "bound_port_positive": True, "factory_families": []}),
    success("start-local-bind", "start-local", {"peer": ["127.0.0.1", "__port__"], "bound_host": "127.0.0.1", "bound_port_positive": True, "factory_families": []}),
    success("start-socket-factory", "start-factory", {"peer": ["127.0.0.1", "__port__"], "bound_host": "127.0.0.1", "bound_port_positive": True, "factory_families": [V4]}),
]


def _run_case(request: dict[str, Any], deadline: float) -> dict[str, Any]:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("candidate cumulative execution budget exhausted")
    dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    environment = ["HOME=/home/candidate", "PYTHONDONTWRITEBYTECODE=1"]
    if dependency_root:
        environment.append(f"NL2REPO_CANDIDATE_DEPENDENCIES={dependency_root}")
    process = subprocess.Popen(
        ["runuser", "-u", "candidate", "--", "env", *environment, "prlimit", "--as=536870912", "--cpu=8", "--fsize=1048576", "--nofile=64", "--nproc=32", "--", sys.executable, "-I", "-B", "-c", PROBE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(json.dumps(request, separators=(",", ":")), timeout=min(CASE_TIMEOUT_SEC, remaining))
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        raise TimeoutError("candidate case timed out") from None
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
    return response["value"]


def _matches(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(_matches(actual.get(key), value) for key, value in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(_matches(a, e) for a, e in zip(actual, expected))
    if expected == "__port__":
        return isinstance(actual, int) and 0 < actual < 65536
    return actual == expected


deadline = time.monotonic() + TOTAL_TIMEOUT_SEC
leaves: list[dict[str, str]] = []
for case in CASES:
    try:
        actual = _run_case(case["request"], deadline)
        passed = _matches(actual, case["expected"])
        message = "" if passed else f"expected {case['expected']!r}, got {actual!r}"
    except BaseException as error:
        passed = False
        message = f"{type(error).__name__}: {error}"
    leaf = {"id": case["id"], "status": "passed" if passed else "failed"}
    if message:
        leaf["message"] = message[:2000]
    leaves.append(leaf)

print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
