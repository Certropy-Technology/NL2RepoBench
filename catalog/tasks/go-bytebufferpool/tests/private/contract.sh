#!/usr/bin/env bash
set -euo pipefail

BRIDGE=$1
PROXY=$2

call() {
    OP=$1 ARGS=$2 BRIDGE_PATH=$BRIDGE PROXY_PATH=$PROXY python3 - <<'PY'
import json
import os
import subprocess

request = {"operation": os.environ["OP"], "args": json.loads(os.environ["ARGS"])}
result = subprocess.run(
    [os.environ["PROXY_PATH"], os.environ["BRIDGE_PATH"]],
    input=(json.dumps(request, ensure_ascii=False) + "\n").encode(),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=False,
    timeout=20,
)
if result.returncode != 0:
    raise SystemExit(f"bridge exit={result.returncode}: {result.stderr.decode(errors='replace')}")
lines = result.stdout.decode().splitlines()
if len(lines) != 1:
    raise SystemExit(f"expected one bridge response, got {len(lines)}")
print(lines[0])
PY
}

expect_value() {
    operation=$1
    args=$2
    expected=$3
    response=$(call "$operation" "$args")
    ACTUAL=$response EXPECTED=$expected python3 - <<'PY'
import json
import os

response = json.loads(os.environ["ACTUAL"])
if response.get("error_type"):
    raise SystemExit(f"unexpected bridge error: {response}")
expected = json.loads(os.environ["EXPECTED"])
actual = response["value"]
if not isinstance(expected, str) and isinstance(actual, str):
    actual = json.loads(actual)
if actual != expected:
    raise SystemExit(f"value mismatch: actual={actual!r} expected={expected!r}")
PY
}

expect_error() {
    operation=$1
    args=$2
    response=$(call "$operation" "$args")
    ACTUAL=$response python3 - <<'PY'
import json
import os

response = json.loads(os.environ["ACTUAL"])
if response.get("error_type") != "InvalidInput":
    raise SystemExit(f"expected InvalidInput, got {response}")
PY
}

expect_value buffer_sequence \
    '[[{"operation":"write_string","text":"hello"},{"operation":"write","text":" "},{"operation":"write_byte","byte":33}]]' \
    '{"bytes":"hello !","len":7,"string":"hello !"}'
expect_value buffer_sequence \
    '[[{"operation":"write_string","text":"discard"},{"operation":"reset"},{"operation":"set_string","text":"世界"},{"operation":"write_string","text":"!"}]]' \
    '{"bytes":"世界!","len":7,"string":"世界!"}'
expect_value buffer_sequence \
    '[[{"operation":"set","text":"abc"},{"operation":"write_byte","byte":0},{"operation":"write_string","text":"z"}]]' \
    '{"bytes":"abc\u0000z","len":5,"string":"abc\u0000z"}'
expect_value set_copy '["copy"]' '"copy"'
expect_value read_from '["read me 世界"]' \
    '{"error":"","len":14,"n":14,"string":"read me 世界"}'
expect_value read_from '[""]' \
    '{"error":"","len":0,"n":0,"string":""}'
expect_value read_from_error '["partial"]' \
    '{"error":"reader error","len":7,"n":7,"string":"partial"}'
expect_value write_to '["write me"]' \
    '{"error":"","n":8,"output":"write me"}'
expect_value write_to_error '["abcdef",3]' \
    '{"error":"writer error","n":3,"output":"abc"}'
expect_value pool_roundtrip '["temporary contents"]' \
    '{"len":0,"string":""}'
expect_value custom_pool_roundtrip '["custom pool contents"]' \
    '{"len":0,"string":""}'
expect_value buffer_sequence '[[{"operation":"set_string","text":"one"},{"operation":"set_string","text":"two"}]]' \
    '{"bytes":"two","len":3,"string":"two"}'
expect_error invalid '[]'
expect_error unknown_operation '[]'

