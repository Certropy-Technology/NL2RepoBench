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

assert_case \
    probe-pty \
    '{"operation":"probe_pty","args":[]}' \
    '{"value":{"name":"pty-slave","terminal":true,"cygwin":false}}'

assert_case \
    probe-fds \
    '{"operation":"probe_fds","args":[]}' \
    '{"value":[{"name":"stdin","terminal":false,"cygwin":false},{"name":"dev_null","terminal":false,"cygwin":false},{"name":"pipe","terminal":false,"cygwin":false},{"name":"invalid","terminal":false,"cygwin":false}]}'

assert_case \
    invalid-fd \
    '{"operation":"probe_fd","args":[18446744073709551615]}' \
    '{"value":{"name":"custom","terminal":false,"cygwin":false}}'

assert_case \
    invalid-operation \
    '{"operation":"not-supported","args":[]}' \
    '{"error_type":"InvalidInput","message":"unknown operation"}'

assert_case \
    malformed-arguments \
    '{"operation":"probe_fds","args":[1]}' \
    '{"error_type":"InvalidInput","message":"probe_fds expects no arguments"}'
