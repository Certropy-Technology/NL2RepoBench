#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"

request() {
    printf '%s\n' "$1" | "$proxy" "$bridge"
}

check_value() {
    local actual
    actual="$(request "$1")"
    ACTUAL="$actual" EXPECTED="$2" /usr/bin/python3 - <<'PY'
import json
import os

payload = json.loads(os.environ["ACTUAL"])
expected = os.environ["EXPECTED"]
assert payload.get("error_type") is None, payload
assert payload.get("value") == expected, payload
PY
}

check_error() {
    local actual
    actual="$(request "$1")"
    ACTUAL="$actual" /usr/bin/python3 - <<'PY'
import json
import os

payload = json.loads(os.environ["ACTUAL"])
assert payload.get("error_type") == "CallFailed", payload
PY
}

check_value \
    '{"operation":"parse","args":["550e8400-e29b-41d4-a716-446655440000"]}' \
    '550e8400-e29b-41d4-a716-446655440000'
check_value \
    '{"operation":"parse","args":["550e8400e29b41d4a716446655440000"]}' \
    '550e8400-e29b-41d4-a716-446655440000'
check_value \
    '{"operation":"parse","args":["URN:UUID:550E8400-E29B-41D4-A716-446655440000"]}' \
    '550e8400-e29b-41d4-a716-446655440000'
check_value \
    '{"operation":"parse","args":["{550E8400-e29b-41d4-a716-446655440000}"]}' \
    '550e8400-e29b-41d4-a716-446655440000'
check_value \
    '{"operation":"parse","args":["00000000000000000000000000000000"]}' \
    '00000000-0000-0000-0000-000000000000'

check_error '{"operation":"parse","args":[""]}'
check_error '{"operation":"parse","args":["550e8400-e29b-41d4-a716-44665544000"]}'
check_error '{"operation":"parse","args":["550e8400-e29b-41d4-a716-44665544000z"]}'
check_error '{"operation":"parse","args":["550e8400_e29b-41d4-a716-446655440000"]}'
check_error '{"operation":"parse","args":["urnxuuid:550e8400-e29b-41d4-a716-446655440000"]}'
check_error '{"operation":"parse","args":["{550e8400-e29b-41d4-a716-446655440000"]}'

printf '%s\n' 'contract passed'
