#!/usr/bin/env bash
set -euo pipefail
bridge=${1:?bridge executable is required}
proxy=${2:?bridge proxy is required}
python3 - "$bridge" "$proxy" <<'PY'
import json
import subprocess
import sys

bridge, proxy = sys.argv[1:]

def call(operation, args=()):
    payload = json.dumps({"operation": operation, "args": list(args)}) + "\n"
    result = subprocess.run([proxy, bridge], input=payload, text=True,
                            capture_output=True, timeout=12, check=False)
    if result.returncode:
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

assert value("sequence", [[
    {"operation":"set", "key":"b", "value":"two"},
    {"operation":"set", "key":"a", "value":"one"},
    {"operation":"set_if_absent", "key":"a", "value":"ignored"},
    {"operation":"upsert", "key":"a", "value":"+"},
    {"operation":"remove_if_value", "key":"b", "value":"wrong"},
]]) == {"count": 2, "empty": False,
       "items": [{"key":"a", "value":"one+"}, {"key":"b", "value":"two"}]}
assert value("lookup", [{"a":"one", "b":"two"}, "missing"]) == {
    "value":"", "found":False, "has":False, "count":2}
assert value("callbacks") == {"upserted":7, "removed":True, "empty":True}
assert value("json", [{"b":2, "a":1}]) == {
    "json":"{\"a\":1,\"b\":2}", "count":2, "items":{"a":1,"b":2}}
assert value("concurrent") == {"count":128, "empty":False}
assert value("custom_sharding") == {
    "one":"one", "one_found":True, "other":"thirty-three",
    "other_found":True, "count":2}
assert call("not-supported") == {"error_type":"InvalidInput", "message":"unknown operation"}
print('{"operation":"go-concurrent-map-contract","status":"passed"}')
PY
