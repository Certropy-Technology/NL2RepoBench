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

assert_field() {
    local name=$1 request=$2 field=$3 expected=$4 actual
    actual="$(printf '%s\n' "$request" | "$PROXY" "$BRIDGE")"
    python3 - "$name" "$actual" "$field" "$expected" <<'PY'
import json
import sys

name, actual_text, field, expected_text = sys.argv[1:]
actual = json.loads(actual_text)
expected = json.loads(expected_text)
if actual.get("value", {}).get(field) != expected:
    raise SystemExit(f"{name}: field mismatch: actual={actual!r}, field={field!r}, expected={expected!r}")
PY
}

assert_case \
    query-regexp-rows \
    '{"operation":"query","args":[{"query":"SELECT (.+) FROM users WHERE id = ?","columns":["id","name"],"rows":[[7,"alice"],[8,"bob"]],"args":[7],"close_rows":true}]}' \
    '{"value":{"columns":["id","name"],"rows":[[7,"alice"],[8,"bob"]]}}'

assert_case \
    query-equal-whitespace \
    '{"operation":"query","args":[{"query":"SELECT id FROM users WHERE id = ?","actual":"  SELECT   id FROM users WHERE id = ?  ","matcher":"equal","columns":["id"],"rows":[[9]],"args":[9]}]}' \
    '{"value":{"columns":["id"],"rows":[[9]]}}'

assert_case \
    query-csv \
    '{"operation":"query","args":[{"query":"SELECT id, name FROM users","columns":["id","name"],"csv":"1,Alice\n2,Bob"}]}' \
    '{"value":{"columns":["id","name"],"rows":[["1","Alice"],["2","Bob"]]}}'

assert_case \
    exec-result \
    '{"operation":"exec","args":[{"query":"UPDATE users SET active = ? WHERE id = ?","matcher":"equal","args":[true,7]}]}' \
    '{"value":{"last_insert_id":17,"rows_affected":3}}'

assert_case \
    transaction \
    '{"operation":"transaction","args":[{"query":"UPDATE ledger SET settled = true WHERE id = ?","matcher":"equal"}]}' \
    '{"value":{"committed":true}}'

assert_case \
    prepared-query \
    '{"operation":"prepare","args":[{"query":"SELECT id, name FROM users WHERE id = ?","matcher":"equal","columns":["id","name"],"rows":[[11,"carol"]]}]}' \
    '{"value":{"columns":["id","name"],"first_row":[11,"carol"]}}'

assert_case \
    regexp-matcher \
    '{"operation":"matcher","args":[{"query":"SELECT (.+) FROM users","actual":"SELECT id FROM users","matcher":"regexp"}]}' \
    '{"value":{"matched":true}}'

assert_field \
    matcher-rejects \
    '{"operation":"matcher","args":[{"query":"SELECT id FROM users","actual":"UPDATE users SET id = 1","matcher":"equal"}]}' \
    matched false

assert_case \
    result-builders \
    '{"operation":"result","args":[{"last_insert_id":42,"rows_affected":5}]}' \
    '{"value":{"error_result":true,"last_insert_id":42,"rows_affected":5}}'

assert_case \
    column-metadata \
    '{"operation":"column","args":["amount"]}' \
    '{"value":{"db_type":"DECIMAL","length":32,"length_ok":true,"name":"amount","nullable":true,"nullable_ok":true,"precision":10,"precision_ok":true,"scale":2,"scan_type":"float64"}}'

assert_case \
    any-argument \
    '{"operation":"any_arg","args":[[null,3,"value",true]]}' \
    '{"value":[true,true,true,true]}'

assert_case \
    invalid-operation \
    '{"operation":"not-supported","args":[]}' \
    '{"error_type":"CallFailed","message":"unknown operation"}'
