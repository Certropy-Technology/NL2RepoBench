#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"

python3 - "$bridge" "$proxy" <<'PY'
import json
import subprocess
import sys

bridge, proxy = sys.argv[1:]
requests = [
    ({"operation": "transport_summary", "args": []}, {
        "default": {
            "disable_keep_alives": True,
            "max_idle_conns": 100,
            "max_idle_conns_per_host": -1,
            "idle_conn_timeout_ms": 90000,
            "tls_handshake_timeout_ms": 10000,
            "expect_continue_ms": 1000,
            "force_attempt_http2": True,
        },
        "pooled": {
            "disable_keep_alives": False,
            "max_idle_conns": 100,
            "max_idle_conns_per_host": 0,
            "idle_conn_timeout_ms": 90000,
            "tls_handshake_timeout_ms": 10000,
            "expect_continue_ms": 1000,
            "force_attempt_http2": True,
        },
        "fresh": True,
        "pooled_max_idle_matches_gomaxprocs": True,
    }),
    ({"operation": "client_summary", "args": []}, {
        "default": {
            "disable_keep_alives": True,
            "max_idle_conns": 100,
            "max_idle_conns_per_host": -1,
            "idle_conn_timeout_ms": 90000,
            "tls_handshake_timeout_ms": 10000,
            "expect_continue_ms": 1000,
            "force_attempt_http2": True,
        },
        "pooled": {
            "disable_keep_alives": False,
            "max_idle_conns": 100,
            "max_idle_conns_per_host": 0,
            "idle_conn_timeout_ms": 90000,
            "tls_handshake_timeout_ms": 10000,
            "expect_continue_ms": 1000,
            "force_attempt_http2": True,
        },
        "concrete": True,
        "fresh_transports": True,
        "pooled_max_idle_matches_gomaxprocs": True,
    }),
    ({"operation": "handler_status", "args": ["/valid", None]}, {"status": 204, "next_called": True}),
    ({"operation": "handler_status", "args": ["/bad\npath", None]}, {"status": 400, "next_called": False}),
    ({"operation": "handler_status", "args": ["/bad\x00path", {"ErrStatus": 451}]}, {"status": 451, "next_called": False}),
    ({"operation": "handler_status", "args": ["/valid", {"ErrStatus": 0}]}, {"status": 204, "next_called": True}),
    ({"operation": "handler_nil_request", "args": []}, {"status": 200, "next_called": False}),
]

payload = "".join(json.dumps(request, separators=(",", ":")) + "\n" for request, _ in requests).encode()
result = subprocess.run([proxy, bridge], input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if result.returncode:
    sys.stderr.buffer.write(result.stderr)
    raise SystemExit(result.returncode)
lines = result.stdout.splitlines()
if len(lines) != len(requests):
    raise SystemExit(f"expected {len(requests)} bridge responses, got {len(lines)}")
for index, (line, (_, expected)) in enumerate(zip(lines, requests), start=1):
    try:
        response = json.loads(line)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"response {index} is not JSON: {exc}") from exc
    if response.get("error_type"):
        raise SystemExit(f"response {index} returned {response}")
    actual = response.get("value")
    if isinstance(actual, dict) and "pooled_max_idle_matches_gomaxprocs" in expected:
        expected = dict(expected)
        expected["pooled"]["max_idle_conns_per_host"] = actual["pooled"]["max_idle_conns_per_host"]
    if actual != expected:
        raise SystemExit(f"response {index} mismatch: {actual!r} != {expected!r}")
print(json.dumps({"cases": len(requests), "status": "passed"}, sort_keys=True))
PY
