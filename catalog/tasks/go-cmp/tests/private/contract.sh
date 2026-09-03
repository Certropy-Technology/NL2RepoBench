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

assert_case profile-default \
    '{"operation":"equal_profiles","args":[{"name":"api","labels":{"env":"prod"},"scores":[1,2]},{"name":"api","labels":{"env":"prod"},"scores":[1,2]},"default"]}' \
    '{"value":true}'
assert_case profile-empty \
    '{"operation":"equal_profiles","args":[{"name":"api","labels":{},"scores":[]},{"name":"api","labels":null,"scores":null},"empty"]}' \
    '{"value":true}'
assert_case profile-different \
    '{"operation":"equal_profiles","args":[{"name":"api","labels":{"env":"prod"},"scores":[1,2]},{"name":"api","labels":{"env":"stage"},"scores":[1,2]},"default"]}' \
    '{"value":false}'
assert_case approx-within \
    '{"operation":"equal_floats","args":[[100,1],[101,1.0005],0.01,0]}' \
    '{"value":true}'
assert_case approx-outside \
    '{"operation":"equal_floats","args":[[100],[102],0.01,0]}' \
    '{"value":false}'
assert_case nan-equality \
    '{"operation":"equal_floats","args":[[null],[null],0,0]}' \
    '{"value":true}'
assert_case sorted-slices \
    '{"operation":"equal_strings_sorted","args":[["beta","alpha"],["alpha","beta"]]}' \
    '{"value":true}'
assert_case sorted-maps \
    '{"operation":"equal_maps_sorted","args":[{"b":2,"a":1},{"a":1,"b":2}]}' \
    '{"value":true}'
assert_case diff-values \
    '{"operation":"diff_values","args":[{"name":"old","count":1},{"name":"new","count":2}]}' \
    '{"value":{"nonempty":true,"has_removed":true,"has_inserted":true}}'
assert_case exported-struct \
    '{"operation":"equal_exported","args":[{"visible":"same"},{"visible":"same"}]}' \
    '{"value":true}'
assert_case invalid-operation \
    '{"operation":"not-supported","args":[]}' \
    '{"error_type":"InvalidInput","message":"unknown operation"}'
printf '%s\n' 'contract::public-api: 10 cases passed'
