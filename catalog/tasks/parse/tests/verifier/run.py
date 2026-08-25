"""Trusted 96-leaf verifier for the bounded parse contract."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path("/tests/verifier")
PROBE = Path("/tmp/parse-candidate-probe.py")


def observed(fixed=(), named=None):
    return {"fixed": list(fixed), "named": {} if named is None else named}


def case(name, request, expected=None, exception=None):
    return {"name": name, "request": request, "expected": expected, "exception": exception}


def cases():
    values = []
    for index, literal in enumerate(["?", "|", "[", "]", "(", ")", "*", "+", "^", "$"]):
        values.append(case(f"parse_literal_meta_{index}", {"action": "parse", "args": [literal + "{}", literal + "value"]}, observed(["value"])))
    for index, text in enumerate(["t€st", "naïve", "東京", "line\none"]):
        values.append(case(f"parse_unicode_{index}", {"action": "parse", "args": ["{}", text]}, observed([text])))
    for index, text in enumerate(["0", "12", "-12", "+12", " 12", "0b1000", "0o1000", "0x1000", "0xabcdef", "999999"]):
        expected = int(text.strip(), 0) if text.strip().lower().startswith(("0b", "0o", "0x")) else int(text)
        values.append(case(f"parse_integer_{index}", {"action": "parse", "args": ["{:d}", text]}, observed([expected])))
    numeric = [
        ("binary", "{:b}", "101", 5), ("octal", "{:o}", "17", 15),
        ("hex", "{:x}", "0xff", 255), ("float", "{:f}", "3.25", 3.25),
        ("float_sign", "{:+.2f}", "-3.25", -3.25), ("exponent", "{:e}", "1.2e3", 1200.0),
        ("percent", "{:%}", "50%", 0.5), ("letters", "{:l}", "AbCd", "AbCd"),
    ]
    for name, fmt, text, expected in numeric:
        values.append(case(f"parse_numeric_{name}", {"action": "parse", "args": [fmt, text]}, observed([expected])))
    widths = [
        ("pair_plain", "{:2}{:2}", "look", ["lo", "ok"]),
        ("pair_precision", "{:.2}{:.2}", "look", ["lo", "ok"]),
        ("first_four", "{:4}{}", "look at that", ["look", " at that"]),
        ("exact_four", "{:4.4}", "look", ["look"]),
        ("min_width", "{:4}", "looky", ["looky"]),
        ("zero_pair", "{:02d}{:02d}", "0440", [4, 40]),
        ("zero_three", "{:03d}{:d}", "04404", [44, 4]),
        ("precision_tail", "{:4}{:.4}", "look at that", ["look at ", "that"]),
    ]
    for name, fmt, text, expected in widths:
        values.append(case(f"parse_width_{name}", {"action": "parse", "args": [fmt, text]}, observed(expected)))
    named = [
        ("single", "hello {name}", "hello world", [], {"name": "world"}),
        ("typed", "{name:w}:{age:d}", "Ada:42", [], {"name": "Ada", "age": 42}),
        ("mixed", "{} {name} {}", "one two three", ["one", "three"], {"name": "two"}),
        ("repeated", "{n} {n}", "x x", [], {"n": "x"}),
        ("dot", "{user.name}:{user.id:d}", "Ada:7", [], {"user.name": "Ada", "user.id": 7}),
        ("bracket", "{user[name]}:{user[id]:d}", "Ada:7", [], {"user": {"name": "Ada", "id": 7}}),
        ("numbered", "{0}:{1:d}", "Ada:7", ["Ada", 7], {}),
        ("escaped", "{{{name}}}", "{Ada}", [], {"name": "Ada"}),
    ]
    for name, fmt, text, fixed, mapping in named:
        values.append(case(f"parse_named_{name}", {"action": "parse", "args": [fmt, text]}, observed(fixed, mapping)))
    tail = [
        ("left", "{:<} world", "hello       world", observed(["hello"]), {}),
        ("right", "hello {:>}", "hello       world", observed(["world"]), {}),
        ("center", "hello {:^} world", "hello  there     world", observed(["there"]), {}),
        ("case_default", "HELLO {}", "hello world", observed(["world"]), {}),
        ("case_sensitive", "HELLO {}", "hello world", None, {"case_sensitive": True}),
        ("whole_input", "hello {}", "x hello world", None, {}),
        ("repeated_mismatch", "{n} {n}", "x y", None, {}),
        ("delayed", "hello {}", "hello world", observed(["world"]), {"evaluate_result": False}),
    ]
    for name, fmt, text, expected, kwargs in tail:
        values.append(case(f"parse_{name}", {"action": "parse", "args": [fmt, text], "kwargs": kwargs}, expected))

    searches = [
        ("basic", "a {} c", " a b c ", {}, observed(["b"])),
        ("multiline", "age: {:d}\n", "name: Ada\nage: 42\n", {}, observed([42])),
        ("pos_hit", "{} c", "a b c", {"pos": 2}, observed(["b"])),
        ("pos_miss", "a {} c", "a b c", {"pos": 2}, None),
        ("end_hit", "a {}", "a b tail", {"endpos": 3}, observed(["b"])),
        ("end_miss", "tail {}", "head tail x", {"endpos": 8}, None),
        ("named", "id={id:d}", "x id=17 y", {}, observed([], {"id": 17})),
        ("case_default", "TAG {}", "tag value", {}, observed(["v"])),
        ("case_sensitive", "TAG {}", "tag value", {"case_sensitive": True}, None),
        ("delayed", "id={:d}", "x id=17", {"evaluate_result": False}, observed([17])),
        ("first", "<{}>", "<one><two>", {}, observed(["one"])),
        ("none", "missing {}", "present value", {}, None),
    ]
    for name, fmt, text, kwargs, expected in searches:
        values.append(case(f"search_{name}", {"action": "search", "args": [fmt, text], "kwargs": kwargs}, expected))

    all_cases = [
        ("ordered", "<{}>", "<a><b><c>", {}, [observed(["a"]), observed(["b"]), observed(["c"])]),
        ("none", "<{}>", "plain", {}, []),
        ("typed", "{:d}", "1 2 3", {}, [observed([1]), observed([2]), observed([3])]),
        ("named", "id={id:d}", "id=1 id=2", {}, [observed([], {"id": 1}), observed([], {"id": 2})]),
        ("case_default", "x({})x", "X(a)X x(b)x", {}, [observed(["a"]), observed(["b"])]),
        ("case_sensitive", "x({})x", "X(a)X x(b)x", {"case_sensitive": True}, [observed(["b"])]),
        ("range", "<{}>", "<a><b><c>", {"pos": 3, "endpos": 6}, [observed(["b"])]),
        ("delayed", "<{}>", "<a><b>", {"evaluate_result": False}, [observed(["a"]), observed(["b"])]),
    ]
    for name, fmt, text, kwargs, expected in all_cases:
        values.append(case(f"findall_{name}", {"action": "findall", "args": [fmt, text], "kwargs": kwargs}, expected))

    parser_cases = [
        case("parser_parse", {"action": "parser", "format": "{name:w}:{age:d}", "operation": "parse", "args": ["Ada:42"]}, observed([], {"name": "Ada", "age": 42})),
        case("parser_parse_none", {"action": "parser", "format": "{:d}", "operation": "parse", "args": ["word"]}, None),
        case("parser_search", {"action": "parser", "format": "id={id:d}", "operation": "search", "args": ["x id=9"]}, observed([], {"id": 9})),
        case("parser_findall", {"action": "parser", "format": "<{}>", "operation": "findall", "args": ["<a><b>"]}, [observed(["a"]), observed(["b"])]),
        case("parser_fields_mixed", {"action": "parser", "format": "{} {name} {:d}", "operation": "fields"}, {"format": "{} {name} {:d}", "fixed_fields": [0, 2], "named_fields": ["name"]}),
        case("parser_fields_named", {"action": "parser", "format": "{left}:{right:d}", "operation": "fields"}, {"format": "{left}:{right:d}", "fixed_fields": [], "named_fields": ["left", "right"]}),
        case("parser_case_default", {"action": "parser", "format": "TAG {}", "operation": "parse", "args": ["tag x"]}, observed(["x"])),
        case("parser_case_sensitive", {"action": "parser", "format": "TAG {}", "case_sensitive": True, "operation": "parse", "args": ["tag x"]}, None),
        case("parser_delayed", {"action": "parser", "format": "{:d}", "operation": "parse", "args": ["7"], "kwargs": {"evaluate_result": False}}, observed([7])),
        case("parser_repeated_type_error", {"action": "parser", "format": "{n:d} {n:w}", "operation": "fields"}, exception="RepeatedNameError"),
    ]
    values.extend(parser_cases)

    result_cases = [
        case("result_get_zero", {"action": "result", "fixed": [1, 2], "named": {}, "operation": "get", "key": 0}, 1),
        case("result_get_negative", {"action": "result", "fixed": [1, 2], "named": {}, "operation": "get", "key": -1}, 2),
        case("result_get_named", {"action": "result", "fixed": [], "named": {"spam": "ham"}, "operation": "get", "key": "spam"}, "ham"),
        case("result_slice", {"action": "result", "fixed": [1, 2, 3, 4], "named": {}, "operation": "slice", "slice": [1, 3, None]}, [2, 3]),
        case("result_slice_reverse", {"action": "result", "fixed": [1, 2, 3, 4], "named": {}, "operation": "slice", "slice": [None, None, -2]}, [4, 2]),
        case("result_contains_name", {"action": "result", "fixed": ["cat"], "named": {"spam": "ham"}, "operation": "contains", "key": "spam"}, True),
        case("result_not_contains_value", {"action": "result", "fixed": ["cat"], "named": {"spam": "ham"}, "operation": "contains", "key": "ham"}, False),
        case("result_shape", {"action": "result", "fixed": [1], "named": {"a": 2}, "spans": {"a": [0, 1]}, "operation": "shape"}, {"fixed": [1], "named": {"a": 2}, "spans": {"a": [0, 1]}}),
        case("result_missing_index", {"action": "result", "fixed": [1], "named": {}, "operation": "get", "key": 2}, exception="IndexError"),
        case("result_missing_name", {"action": "result", "fixed": [], "named": {}, "operation": "get", "key": "missing"}, exception="KeyError"),
    ]
    values.extend(result_cases)
    assert len(values) == 96, len(values)
    return values


def run_probe(request):
    completed = subprocess.run(
        ["runuser", "-u", "candidate", "--", "env", "HOME=/home/candidate", "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1", "/usr/local/bin/python", "-I", "-B", str(PROBE)],
        input=json.dumps(request, ensure_ascii=False), capture_output=True, text=True,
        timeout=5, check=False,
    )
    if completed.returncode != 0:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": (completed.stderr or completed.stdout)[-512:]}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}


def main():
    shutil.copyfile(ROOT / "probe.py", PROBE)
    PROBE.chmod(0o555)
    leaves = []
    for item in cases():
        try:
            response = run_probe(item["request"])
        except subprocess.TimeoutExpired:
            response = {"ok": False, "exception_type": "CandidateTimeout"}
        if item["exception"] is not None:
            passed = not response.get("ok") and str(response.get("exception_type", "")).endswith(item["exception"])
        else:
            passed = response.get("ok") is True and response.get("value") == item["expected"]
        leaves.append({"id": item["name"], "status": "passed" if passed else "failed", "message": "" if passed else str(response)[:512]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
