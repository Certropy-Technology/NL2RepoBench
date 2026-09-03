#!/usr/bin/env bash
set -euo pipefail
bridge="$1"
proxy="$2"

/usr/bin/python3 - "$proxy" "$bridge" <<'PY'
import json
import subprocess
import sys

proxy, bridge = sys.argv[1:]
requests = [
    {"operation": "format", "args": ["sprint", "", ["hello", " world"]]},
    {"operation": "format", "args": ["sprintln", "", ["hello", 2]]},
    {"operation": "format", "args": ["sprintf", "%s=%d", ["n", 2]]},
    {"operation": "format", "args": ["sprintfln", "%s=%d", ["n", 2]]},
    {"operation": "format", "args": ["sprinto", "", ["replace"]]},
    {"operation": "color", "args": [31, "sprint", "x", True]},
    {"operation": "color", "args": [31, "sprintln", "x", True]},
    {"operation": "color", "args": [97, "string", "", True]},
    {"operation": "color", "args": [36, "to_style", "", True]},
    {"operation": "color", "args": [31, "sprint", "\u001b[32mgreen\u001b[0m text", False]},
    {"operation": "style", "args": [[31, 44, 1], "code", "", True, []]},
    {"operation": "style", "args": [[31, 1], "sprint", "one\ntwo", True, []]},
    {"operation": "style", "args": [[31], "add", "", True, [44, 1]]},
    {"operation": "style", "args": [[1, 31, 1, 44], "remove", "", True, [1]]},
    {"operation": "style", "args": [[31, 1], "sprint", "a\u001b[32mmid\u001b[0mb", True, []]},
    {"operation": "style", "args": [[31, 1], "sprint", "\u001b[32mgreen\u001b[0m", False, []]},
    {"operation": "basic_text", "args": [None, "sprint", "plain", True]},
    {"operation": "basic_text", "args": [[31, 1], "sprintln", "styled", True]},
    {"operation": "strip", "args": ["\u001b[31mred\u001b[0m plain"]},
    {"operation": "strip", "args": ["\u001b]8;;https://example.com\u001b\\link\u001b]8;;\u001b\\"]},
    {"operation": "bar", "args": ["cpu", 42, [31], [36, 1]]},
    {"operation": "center_text", "args": ["a\nabc\nabcde"]},
    {"operation": "center_text", "args": ["\u001b[31mab\u001b[0m\nabcdef"]},
    {"operation": "rgb_from_hex", "args": ["#1a2B3c"]},
    {"operation": "rgb_from_hex", "args": ["0xf0a"]},
    {"operation": "rgb_from_hex", "args": ["12"]},
    {"operation": "rgb_from_hex", "args": ["xyzxyz"]},
    {"operation": "letters", "args": ["default", "G\u00f6\u65e5", [], {}]},
    {"operation": "letters", "args": ["style", "hi", [31, 1], {}]},
    {"operation": "letters", "args": ["rgb", "ok", [], {"R": 1, "G": 2, "B": 3, "Background": True}]},
    {"operation": "letters", "args": ["default", "", [], {}]},
    {"operation": "missing", "args": []},
    {"operation": "color", "args": [31]},
]

payload = "\n".join(json.dumps(item, separators=(",", ":")) for item in requests) + "\n"
result = subprocess.run(
    [proxy, bridge], input=payload, text=True, capture_output=True, timeout=25, check=False
)
if result.returncode != 0:
    raise AssertionError(f"bridge failed: {result.returncode}: {result.stderr}")
responses = [json.loads(line) for line in result.stdout.splitlines()]
assert len(responses) == len(requests), (len(responses), result.stdout, result.stderr)
values = [item.get("value") for item in responses]

assert values[0] == "hello world"
assert values[1] == "hello 2\n"
assert values[2] == "n=2"
assert values[3] == "n=2\n"
assert values[4] == "\rreplace"
assert values[5] == "\u001b[31mx\u001b[0m"
assert values[6] == "\u001b[31mx\u001b[0m\n"
assert values[7] == "97"
assert values[8] == "36"
assert values[9] == "green text"
assert values[10] == {"code": "31;44;1"}
assert values[11] == {
    "code": "31;1",
    "output": "\u001b[31;1mone\u001b[0m\n\u001b[31;1mtwo\u001b[0m",
}
assert values[12] == {"code": "31;44;1"}
assert values[13] == {"code": "31;44"}
assert values[14] == {
    "code": "31;1",
    "output": "\u001b[31;1ma\u001b[32mmid\u001b[0m\u001b[31;1mb\u001b[0m",
}
assert values[15] == {"code": "31;1", "output": "green"}
assert values[16] == "plain"
assert values[17] == "\u001b[31;1mstyled\u001b[0m\n"
assert values[18] == "red plain"
assert values[19] == "link"
assert values[20] == {
    "original": {"label": "", "value": 0, "style_code": "", "label_style_code": ""},
    "modified": {"label": "cpu", "value": 42, "style_code": "31", "label_style_code": "36;1"},
}
assert values[21] == "  a  \n abc \nabcde"
assert values[22] == "  \u001b[31mab\u001b[0m  \nabcdef"
assert values[23] == {"R": 26, "G": 43, "B": 60, "Background": False}
assert values[24] == {"R": 255, "G": 0, "B": 170, "Background": False}
assert responses[25]["error_type"] == "CallFailed"
assert responses[26]["error_type"] == "CallFailed"
assert [item["string"] for item in values[27]] == ["G", "\u00f6", "\u65e5"]
assert [item["style_code"] for item in values[28]] == ["31;1", "31;1"]
assert values[29] == [
    {"string": "o", "style_code": "", "r": 1, "g": 2, "b": 3, "background": True},
    {"string": "k", "style_code": "", "r": 1, "g": 2, "b": 3, "background": True},
]
assert values[30] == []
assert responses[31]["error_type"] == "InvalidInput"
assert responses[32]["error_type"] == "InvalidInput"
PY

printf '%s\n' '{"operation":"pterm-contract","status":"passed"}'
