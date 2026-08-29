from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ADAPTER_PATH = Path("/tmp/httpx-sse-child-adapter.py")

SCENARIOS: dict[str, Any] = {
    "exports": {"version": "0.4.3", "all": ["__version__", "EventSource", "connect_sse", "aconnect_sse", "ServerSentEvent", "SSEError"], "symbols": True},
    "sse-default": {"event": "message", "data": "", "id": "", "retry": None},
    "sse-fields": {"event": "update", "data": "payload", "id": "evt-7", "retry": 2500},
    "sse-json": {"items": [1, 2], "ok": True},
    "sse-repr": "ServerSentEvent(event='update', data='payload', id='evt-7', retry=2500)",
    "multiline": [["message", "one\ntwo", "", None]],
    "line-endings": [["x", "y"], ["message", "z"]],
    "chunk-boundary": [["message", "hello"]],
    "flush": [],
    "comment-unknown": 0,
    "id-retry": [["one", "first", 1500], ["two", "first", None]],
    "nul-id": [["ok", ""]],
    "invalid-retry": 0,
    "data-spacing": "no-space\none-space\n two-spaces",
    "empty-dispatch": [["empty", ""]],
    "unicode-separator": {"text": "Hello\u2028World"},
    "response-identity": True,
    "content-type-parameter": "x",
    "wrong-content-type": ["httpx_sse._exceptions.SSEError", True, True],
    "connect-headers": {"seen": {"method": "POST", "path": "/events", "accept": "text/event-stream", "cache": "no-store"}, "data": ["connected"]},
    "connect-method-forwarding": {"seen": {"method": "PUT", "url": "http://testserver/a?x=1"}, "data": ["ok"]},
    "connect-custom-header-overrides": {"accept": "text/event-stream", "cache": "no-store"},
    "async-iteration": [["message", "async\nvalue"]],
    "async-connect": {"seen": {"accept": "text/event-stream", "cache": "no-store"}, "data": ["async-connected"]},
    "async-flush": [],
    "async-error": "httpx_sse._exceptions.SSEError",
}


def invoke(scenario: str) -> dict[str, Any]:
    command = [
        shutil.which("runuser") or "/usr/bin/runuser", "-u", "candidate", "--", "env",
        "HOME=/tmp", "TMPDIR=/tmp", "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1", "python",
        "-I", "-B", str(ADAPTER_PATH),
        "--candidate-site", "/tmp/candidate-site", "--scenario", scenario,
    ]
    try:
        # Keep a hung candidate probe bounded while still allowing normal HTTPX
        # mock-stream scenarios to complete inside the verifier budget.
        completed = subprocess.run(command, capture_output=True, text=True, timeout=2, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": completed.stderr[-1000:]}
    try:
        report = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return report if isinstance(report, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def main() -> int:
    adapter_source = Path(__file__).with_name("adapter.py")
    ADAPTER_PATH.write_bytes(adapter_source.read_bytes())
    os.chmod(ADAPTER_PATH, 0o444)
    leaves = []
    for scenario, expected in SCENARIOS.items():
        result = invoke(scenario)
        actual = result.get("value") if result.get("ok") is True else {
            "exception_type": result.get("exception_type"),
            "exception_message": result.get("exception_message"),
        }
        passed = actual == expected
        if scenario == "sse-repr" and isinstance(actual, str):
            passed = actual == expected
        leaves.append({
            "id": f"httpx-sse/{scenario}",
            "status": "passed" if passed else "failed",
            "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1200],
        })
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
