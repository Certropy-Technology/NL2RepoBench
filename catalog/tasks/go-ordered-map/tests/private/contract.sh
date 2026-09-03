#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"
result_file="$(mktemp)"
trap 'rm -f "$result_file"' EXIT

"$proxy" "$bridge" >"$result_file" <<'REQUESTS'
{"operation":"basic_mutation"}
{"operation":"marshal_default"}
{"operation":"marshal_no_escape"}
{"operation":"unmarshal_nested"}
{"operation":"unmarshal_duplicates"}
{"operation":"unmarshal_special_keys"}
{"operation":"sort_keys"}
{"operation":"sort_pairs"}
{"operation":"pair_access"}
{"operation":"struct_unmarshal"}
{"operation":"invalid"}
{"operation":"unknown_operation"}
REQUESTS

python3 - "$result_file" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    actual = [json.loads(line) for line in handle if line.strip()]

if len(actual) != 12:
    raise SystemExit(f"expected 12 bridge responses, got {len(actual)}")

nested = {"keys": ["b", "a"], "values": {"b": "value", "a": {"keys": ["deep"], "values": {"deep": True}}}}
expected = [
    {"value": {"keys": ["number", "string"], "missing": False, "values": {"number": 4, "string": "x"}}},
    {"value": {"compact": '{"number":4,"special":"\\\\.\\u003c\\u003e[]{}_-","z":1,"a":2,"empty_array":[],"empty_map":{},"nested":{"e":1,"a":2}}', "indented": '{\n  "number": 4,\n  "special": "\\\\.\\u003c\\u003e[]{}_-",\n  "z": 1,\n  "a": 2,\n  "empty_array": [],\n  "empty_map": {},\n  "nested": {\n    "e": 1,\n    "a": 2\n  }\n}'}},
    {"value": {"encoded": '{"x":"<>","y":[{"z":["<>"]}]}'}},
    {"value": {"keys": ["root", "nested", "list"], "values": {"root": 1, "nested": nested, "list": [{"keys": ["x"], "values": {"x": 2}}, [{"keys": ["y"], "values": {"y": "z"}}]]}}},
    {"value": {"keys": ["c", "d", "e", "a", "b"], "values": {"a": {"keys": [], "values": {}}, "b": [[1]], "c": 1, "d": {"keys": ["y"], "values": {"y": 2}}, "e": [{"keys": ["z"], "values": {"z": 2}}]}}},
    None,
    {"value": ["a", "b", "c"]},
    {"value": ["high", "middle", "low"]},
    {"value": {"keys": ["first", "second"], "observed": [{"left_key": "second", "left_value": 2, "right_key": "first", "right_value": "value"}]}},
    {"value": {"keys": ["x"], "ok": True, "value": 1}},
    {"error_type": "InvalidInput", "message": "known bridge operation has invalid request"},
    {"error_type": "InvalidInput", "message": "unknown operation"},
]

special = actual[5].get("value")
if not isinstance(special, list) or len(special) != 3:
    raise SystemExit(f"special-key result has wrong shape: {special!r}")
if not (special[0].startswith(" A") and special[1] == "\\" and special[2] == "\n"):
    raise SystemExit(f"special-key result has wrong decoded keys: {special!r}")
actual[5] = {"value": "special-key-boundary-passed"}
expected[5] = {"value": "special-key-boundary-passed"}

if actual != expected:
    raise SystemExit(f"bridge contract mismatch\nactual={actual!r}\nexpected={expected!r}")
PY
