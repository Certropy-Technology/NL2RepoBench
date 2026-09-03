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

assert_case merge-default \
    '{"operation":"merge_record","args":[{"name":"keep","count":0,"enabled":false,"tags":[],"meta":{"keep":"old"},"child":null},{"name":"source","count":5,"enabled":true,"tags":[1,2],"meta":{"keep":"new","add":"x"},"child":{"label":"child","value":8}},[]]}' \
    '{"value":{"child":{"label":"child","value":8},"count":5,"enabled":true,"hidden":"destination-private","meta":{"add":"x","keep":"old"},"name":"keep","tags":[1,2]}}'

assert_case merge-override \
    '{"operation":"merge_record","args":[{"name":"keep","count":7,"enabled":true,"tags":[9],"meta":{"keep":"old"},"child":{"label":"old","value":3}},{"name":"source","count":5,"enabled":false,"tags":[1,2],"meta":{"keep":"new","add":"x"},"child":{"label":"new","value":8}},["override"]]}' \
    '{"value":{"child":{"label":"new","value":8},"count":5,"enabled":true,"hidden":"destination-private","meta":{"add":"x","keep":"new"},"name":"source","tags":[1,2]}}'

assert_case merge-overwrite-empty \
    '{"operation":"merge_record","args":[{"name":"keep","count":7,"enabled":true,"tags":[1],"meta":{"keep":"old","drop":"x"},"child":{"label":"old","value":3}},{"name":"","count":0,"enabled":false,"tags":[],"meta":{"keep":"new"},"child":null},["overwrite_empty"]]}' \
    '{"value":{"child":null,"count":0,"enabled":false,"hidden":"destination-private","meta":{"keep":"new"},"name":"","tags":[]}}'

assert_case merge-append-slice \
    '{"operation":"merge_record","args":[{"name":"keep","count":7,"enabled":true,"tags":[1],"meta":{},"child":null},{"name":"source","count":5,"enabled":true,"tags":[2,3],"meta":{},"child":null},["append_slice"]]}' \
    '{"value":{"child":null,"count":7,"enabled":true,"hidden":"destination-private","meta":{},"name":"keep","tags":[1,2,3]}}'

assert_case map-default \
    '{"operation":"merge_map","args":[{"a":1,"nested":{"a":1},"keep":"x"},{"a":2,"b":3,"nested":{"b":4},"keep":""},[]]}' \
    '{"value":{"a":1,"b":3,"keep":"x","nested":{"a":1,"b":4}}}'

assert_case map-override \
    '{"operation":"merge_map","args":[{"a":1,"nested":{"a":1},"keep":"x"},{"a":2,"b":3,"nested":{"b":4},"keep":"new"},["override"]]}' \
    '{"value":{"a":2,"b":3,"keep":"new","nested":{"a":1,"b":4}}}'

assert_case map-overwrite-empty \
    '{"operation":"merge_map","args":[{"a":1,"drop":2,"nested":{"a":1}},{"a":0,"nested":{}},["overwrite_empty"]]}' \
    '{"value":{"a":0,"nested":{}}}'

assert_case map-to-record \
    '{"operation":"map_to_record","args":[{"name":"dst","count":3,"enabled":false,"tags":[9],"meta":{"keep":"old"},"child":null},{"name":"src","count":8,"enabled":true,"tags":[1,2],"meta":{"add":"yes"},"child":{"label":"new","value":4}},[]]}' \
    '{"value":{"child":{"label":"new","value":4},"count":3,"enabled":true,"hidden":"destination-private","meta":{"add":"yes"},"name":"dst","tags":[9]}}'

assert_case record-to-map \
    '{"operation":"record_to_map","args":[{"name":"existing","count":99},{"name":"src","count":8,"enabled":true,"tags":[1,2],"meta":{"add":"yes"},"child":{"label":"new","value":4}},[]]}' \
    '{"value":{"child":{"label":"new","value":4},"count":99,"enabled":true,"meta":{"add":"yes"},"name":"existing","tags":[1,2]}}'

for error_case in nil non_pointer different_types unsupported expected_map expected_struct; do
    case "$error_case" in
        nil) expected='{"value":"src and dst must not be nil"}' ;;
        non_pointer) expected='{"value":"dst must be a pointer"}' ;;
        different_types) expected='{"value":"src and dst must be of same type"}' ;;
        unsupported) expected='{"value":"only structs, maps, and slices are supported"}' ;;
        expected_map) expected='{"value":"dst was expected to be a map"}' ;;
        expected_struct) expected='{"value":"dst was expected to be a struct"}' ;;
    esac
    assert_case "error-$error_case" "{\"operation\":\"error\",\"args\":[\"$error_case\"]}" "$expected"
done

assert_case invalid-operation \
    '{"operation":"not-supported","args":[]}' \
    '{"error_type":"InvalidInput","message":"unknown operation"}'

assert_case malformed-json \
    '{not json' \
    '{"error_type":"InvalidInput","message":"invalid character '\''n'\'' looking for beginning of object key string"}'
