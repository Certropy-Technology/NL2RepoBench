#!/usr/bin/env bash
set -euo pipefail
bridge="$1"
proxy="$2"
python3 - "$bridge" "$proxy" <<'PY'
import json
import subprocess
import sys

bridge, proxy = sys.argv[1:]

def call(operation, args=()):
    payload = json.dumps({"operation": operation, "args": list(args)}) + "\n"
    result = subprocess.run([proxy, bridge], input=payload, text=True,
                            capture_output=True, timeout=12, check=False)
    if result.returncode != 0:
        raise AssertionError(f"bridge exit {result.returncode}: {result.stderr}")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise AssertionError(f"expected one response, got {lines!r}")
    return json.loads(lines[0])

def value(operation, args=()):
    response = call(operation, args)
    if response.get("error_type"):
        raise AssertionError(response)
    return response.get("value")

assert value("zero_wait") == {"nil": True}
assert value("single_error", ["unicode: café"]) == {
    "message": "unicode: café", "same_result": True
}
assert value("with_context", ["stop now"]) == {
    "wait_error": "stop now", "done": True, "cause": "stop now"
}
assert value("with_context_success") == {
    "wait_nil": True, "done": True, "cause": "context canceled"
}
assert value("trygo_limit") == {"second_started": False, "third_started": True}
assert value("go_limit") == {"blocked": True}
assert value("trygo_zero") == {"started": False, "wait_nil": True}
assert value("negative_limit") == {"all_started": True}
assert value("timed_call") is True

invalid = call("invalid")
assert invalid == {"error_type": "InvalidInput", "message": "unknown operation"}
unknown = call("not-a-real-operation")
assert unknown == {"error_type": "InvalidInput", "message": "unknown operation"}
PY
