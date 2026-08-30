from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCENARIOS = {
    "package-identity": ["17.1", True],
    "root-exports": [True, True],
    "headers-init": [[["Connection", "Upgrade"], ["Server", "websockets"]], True],
    "headers-lookup": ["websockets", True, ["websockets"], 1],
    "headers-duplicates": ["websockets.datastructures.MultipleValuesError", ["one", "two"]],
    "headers-mutation": [[["B", "2"]], [], 1],
    "headers-serialize": [
        "connection: Upgrade\r\nserver: websockets\r\n\r\n",
        "connection: Upgrade\r\nserver: websockets\r\n\r\n",
        "Headers([('connection', 'Upgrade'), ('server', 'websockets')])",
    ],
    "headers-invalid": "websockets.exceptions.InvalidHeaderValue",
    "headers-copy": [[["X", "one"]], [["X", "one"], ["Y", "two"]], False],
    "uri-basic": [False, "example.com", 80, "/chat", "room=1", "/chat?room=1", None],
    "uri-secure-userinfo": [True, 8443, ["alice", "secret"], "/x"],
    "uri-idna": ["xn--r8jz45g.xn--zckzah", "/%E8%B7%AF%E5%BE%84", "q=%E5%80%BC"],
    "uri-invalid-scheme": [
        "websockets.exceptions.InvalidURI",
        "http://example.com isn't a valid URI: scheme isn't ws or wss",
    ],
    "uri-invalid-fragment": "websockets.exceptions.InvalidURI",
    "frame-text": ["TEXT 'hi' [2 bytes]", "81026869", None],
    "frame-masked": "818261626364090b",
    "frame-long": ["827e007e", 130],
    "frame-parse": ["TEXT", "hi", True, False],
    "frame-invalid": "websockets.exceptions.ProtocolError",
    "close-roundtrip": [1000, "bye", "1000 (OK) bye", "03e8627965"],
    "close-invalid": "websockets.exceptions.ProtocolError",
    "exception-contract": [True, True, True, True],
    "protocol-receive": ["TEXT", "hi", True, "OPEN"],
    "protocol-send": ["82020001"],
    "protocol-close": ["880503e8627965", "CLOSING", True],
    "assembler-fragments": "hello",
    "assembler-binary-decode": "42",
    "assembler-concurrency": "websockets.exceptions.ConcurrencyError",
}

PROBE = Path(__file__).with_name("adapter.py").read_text(encoding="utf-8")


def invoke(name: str) -> dict[str, object]:
    command = [
        "runuser",
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
        "-c",
        PROBE,
        "--candidate-site",
        "/tmp/candidate-site",
        "--scenario",
        name,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {
            "ok": False,
            "exception_type": "CandidateProcessError",
            "exception_message": (completed.stderr or completed.stdout)[-1000:],
        }
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "exception_type": "CandidateProtocolError",
            "exception_message": str(exc),
        }
    return (
        result
        if isinstance(result, dict)
        else {"ok": False, "exception_type": "CandidateProtocolError"}
    )


def main() -> int:
    leaves = []
    for name, expected in SCENARIOS.items():
        result = invoke(name)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        passed = actual == expected
        leaves.append(
            {
                "id": f"websockets/{name}",
                "status": "passed" if passed else "failed",
                "message": ""
                if passed
                else json.dumps(
                    {
                        "actual": actual,
                        "detail": result.get("exception_message"),
                        "expected": expected,
                    },
                    sort_keys=True,
                )[:1000],
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
