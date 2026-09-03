#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"

python3 - "$proxy" "$bridge" <<'PY'
import json
import subprocess
import sys

proxy = sys.argv[1]
bridge = sys.argv[2]

def call(operation, args):
    request = json.dumps({"operation": operation, "args": args}) + "\n"
    result = subprocess.run([proxy, bridge], input=request, text=True, capture_output=True, timeout=30)
    if result.returncode != 0:
        raise AssertionError(f"bridge process failed: {result.returncode}: {result.stderr}")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise AssertionError(f"expected one JSON response, got {result.stdout!r}")
    value = json.loads(lines[0])
    if "error_type" in value:
        raise AssertionError(f"unexpected candidate error: {value}")
    return value.get("value")

for text, level in [("", 0), ("hello brotli " * 80, 6), ("unicode: cafe\N{COMBINING ACUTE ACCENT}", 11)]:
    value = call("brotli_roundtrip", [text, level])
    assert value["decoded"] == text and value["encoded_len"] > 0

value = call("brotli_v2_roundtrip", ["v2 stream " * 20, 11])
assert value["decoded"] == "v2 stream " * 20 and value["v2"] is True

value = call("stream_roundtrip", [["first", "", "second", " third"], 4])
assert value["decoded"] == "firstsecond third" and value["chunks"] == 4

value = call("writer_reset", ["writer one", "writer two"])
assert value == {"first": "writer one", "second": "writer two"}
value = call("reader_reset", ["reader one", "reader two"])
assert value == {"first": "reader one", "second": "reader two"}

for operation in ("flate_roundtrip", "gzip_roundtrip"):
    value = call(operation, ["deflate and gzip " * 4, 6])
    assert value["decoded"] == "deflate and gzip " * 4
    assert value["gzip"] is (operation == "gzip_roundtrip")

value = call("matchfinder_output", ["none", "abcabc"])
assert value["text"] == "abcabc"
assert value["matches"] == [{"Unmatched": 6, "Length": 0, "Distance": 0}]
value = call("matchfinder_output", ["m4", "abcabcabcabc"])
assert value["text"] == "abc<9,3>"
assert value["matches"][0]["Distance"] == 3

request = json.dumps({"operation": "not-a-real-operation", "args": []}) + "\n"
result = subprocess.run([proxy, bridge], input=request, text=True, capture_output=True, timeout=30)
assert result.returncode == 0
assert json.loads(result.stdout)["error_type"] == "InvalidInput"
print("contract::compression-api passed")
PY

