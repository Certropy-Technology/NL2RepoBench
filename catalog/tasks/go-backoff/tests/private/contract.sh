#!/usr/bin/env bash
set -euo pipefail

BRIDGE=${1:?bridge executable is required}
PROXY=${2:?bridge proxy is required}

assert_case() {
    local name=$1 request=$2 expected=$3 actual
    actual="$(printf '%s\n' "$request" | "$PROXY" "$BRIDGE")"
    python3 - "$name" "$actual" "$expected" <<'PY'
import json
import sys

name, actual_text, expected_text = sys.argv[1:]
try:
    actual = json.loads(actual_text)
    expected = json.loads(expected_text)
except json.JSONDecodeError as exc:
    raise SystemExit(f"{name}: invalid JSON response: {exc}: {actual_text!r}")
if actual != expected:
    raise SystemExit(f"{name}: response mismatch\nactual={actual!r}\nexpected={expected!r}")
PY
}

assert_case constant-sequence \
    '{"operation":"constant_sequence","args":[25,4]}' \
    '{"value":[25,25,25,25]}'
assert_case zero-stop \
    '{"operation":"zero_and_stop","args":[3]}' \
    '{"value":{"zero":[0,0,0],"stop":-1}}'
assert_case exponential-sequence \
    '{"operation":"exponential_sequence","args":[100,0,2,350,5]}' \
    '{"value":[100,200,350,350,350]}'
assert_case retry-success \
    '{"operation":"retry_failures","args":[2,0,-1]}' \
    '{"value":{"attempts":3,"error":{"is_error":false},"result":"success"}}'
assert_case retry-exhausted \
    '{"operation":"retry_failures","args":[5,3,-1]}' \
    '{"value":{"attempts":3,"error":{"cause":"backoff: retries exhausted","error":"backoff: retries exhausted (last error: failure-3)","is_error":true,"is_exhausted":true,"is_permanent":false,"last_error":"failure-3"},"result":""}}'
assert_case retry-permanent \
    '{"operation":"retry_failures","args":[5,0,2]}' \
    '{"value":{"attempts":2,"error":{"cause":"backoff: permanent error","error":"backoff: permanent error (last error: failure-2)","is_error":true,"is_exhausted":false,"is_permanent":true,"last_error":"failure-2"},"result":""}}'
assert_case retry-after-notify \
    '{"operation":"retry_after_and_notify","args":[]}' \
    '{"value":{"attempts":2,"delays_ms":[0],"error":{"is_error":false},"notify_count":1,"result":"ready"}}'
assert_case error-wrappers \
    '{"operation":"error_wrappers","args":[]}' \
    '{"value":{"after":"temporary (retry after 7ms)","after_duration_ms":7,"after_unwrap":true,"permanent":"temporary","permanent_is_marker":true}}'
assert_case invalid-operation \
    '{"operation":"not-supported","args":[]}' \
    '{"error_type":"InvalidInput","message":"unknown operation"}'
printf '%s\n' 'contract::public-api: 9 cases passed'
