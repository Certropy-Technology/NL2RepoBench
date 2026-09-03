#!/usr/bin/env bash
set -euo pipefail
bridge=${1:?bridge path required}
proxy=${2:?proxy path required}
output=$(mktemp)
trap 'rm -f "$output"' EXIT

cat <<'JSON' | "$proxy" "$bridge" > "$output"
{"operation":"put_get","args":[[{"key":"alpha","value":"one","meta":1},{"key":"beta","value":"two\u0000bytes","meta":7}],"beta"]}
{"operation":"scan","args":[[{"key":"a/2","value":"second","meta":2},{"key":"b/1","value":"other","meta":3},{"key":"a/1","value":"first","meta":1}],"a/",false]}
{"operation":"scan","args":[[{"key":"c","value":"3","meta":3},{"key":"a","value":"1","meta":1},{"key":"b","value":"2","meta":2}],"",true]}
{"operation":"transaction","args":[]}
{"operation":"errors","args":[]}
{"operation":"unknown","args":[]}
JSON

python3 - "$output" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    rows = [json.loads(line) for line in handle if line.strip()]
assert len(rows) == 6, rows

item = rows[0]["value"]
assert item["key"] == "beta"
assert item["value"] == "two\x00bytes"
assert item["meta"] == 7
assert item["version"] > 0
assert item["key_size"] == 4
assert item["value_size"] == 9

forward = rows[1]["value"]
assert [(item["key"], item["value"], item["meta"]) for item in forward] == [
    ("a/1", "first", 1),
    ("a/2", "second", 2),
]
assert all(item["version"] > 0 for item in forward)

reverse = rows[2]["value"]
assert [item["key"] for item in reverse] == ["c", "b", "a"]
assert [item["value"] for item in reverse] == ["3", "2", "1"]

assert rows[3]["value"] == {
    "commit_visible": True,
    "delete_hides_write": True,
    "discard_hides_write": True,
    "read_your_write": True,
    "rollback_hides_write": True,
    "update_propagates_error": True,
}
assert rows[4]["value"] == {
    "discarded_txn": True,
    "empty_key": True,
    "missing_key": True,
    "read_only_write": True,
}
assert rows[5]["error_type"] == "InvalidInput"
PY
