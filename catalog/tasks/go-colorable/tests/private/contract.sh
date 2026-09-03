#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"
responses="$(mktemp)"
trap 'rm -f "$responses"' EXIT

printf '%s\n' \
  '{"operation":"strip","args":["plain text"]}' \
  '{"operation":"strip","args":["\u001b[31mred\u001b[0m"]}' \
  '{"operation":"strip","args":["\u001b[2Jclear\u001b[H"]}' \
  '{"operation":"strip","args":["é\u001b[1m彩\u001b[0m"]}' \
  '{"operation":"strip","args":["\u001b"]}' \
  '{"operation":"strip","args":["\u001b\u001b"]}' \
  '{"operation":"strip","args":["\u001b[abc"]}' \
  '{"operation":"strip_chunks","args":[["a\u001b[31m","b\u001b[0mc"]]}' \
  '{"operation":"colorable","args":["\u001b[35mviolet\u001b[0m"]}' \
  '{"operation":"stdio_types","args":[]}' \
  '{"operation":"enable_colors","args":[]}' \
  '{"operation":"nil_colorable","args":[]}' \
  '{"operation":"unknown","args":[]}' \
  | "$proxy" "$bridge" > "$responses"

python3 - "$responses" <<'PY'
import json
import sys

rows = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8")]
if len(rows) != 13:
    raise SystemExit(f"expected 13 bridge responses, got {len(rows)}")

def value(index):
    row = rows[index]
    if "value" not in row:
        raise SystemExit(f"case {index + 1} returned error: {row}")
    return row["value"]

assert value(0) == {"text": "plain text", "n": 10, "error": ""}
assert value(1) == {"text": "red", "n": 12, "error": ""}
assert value(2) == {"text": "clear", "n": 12, "error": ""}
assert value(3) == {"text": "é彩", "n": len("é\x1b[1m彩\x1b[0m".encode()), "error": ""}
assert value(4) == {"text": "", "n": 1, "error": ""}
assert value(5) == {"text": "", "n": 2, "error": ""}
assert value(6) == {"text": "bc", "n": 5, "error": ""}
assert value(7) == {"text": "abc", "counts": [6, 6]}
assert value(8) == {"text": "\x1b[35mviolet\x1b[0m", "n": 15, "error": ""}
assert value(9) == {"stdout_file": True, "stderr_file": True}
assert value(10) == {"enabled": True, "unchanged_after_cleanup": True}
assert value(11) == {"panicked": True}
assert rows[12]["error_type"] == "InvalidInput"
print("13 bridge cases passed")
PY
