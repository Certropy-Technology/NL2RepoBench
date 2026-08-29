#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


def request(operation: str, *args: Any) -> dict[str, Any]:
    return {"operation": operation, "args": list(args)}


def run(requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payload = "".join(
        json.dumps(item, separators=(",", ":")) + "\n" for item in requests
    )
    result = subprocess.run(
        [sys.argv[2], sys.argv[1]],
        input=payload,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"bridge proxy exited {result.returncode}: {result.stderr[:1000]}"
        )
    if result.stderr:
        raise AssertionError(f"bridge wrote stderr: {result.stderr[:1000]}")
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    if len(rows) != len(requests):
        raise AssertionError(
            f"got {len(rows)} responses for {len(requests)} requests"
        )
    return rows


def value(row: dict[str, Any]) -> Any:
    if row.get("error_type"):
        raise AssertionError(f"unexpected bridge error: {row}")
    if "value" not in row:
        raise AssertionError(f"missing value: {row}")
    return row["value"]


def fixtures() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    build = {
        "kind": "object",
        "object": [
            {"key": "name", "value": {"kind": "string", "string": "A\nB"}},
            {
                "key": "items",
                "value": {
                    "kind": "array",
                    "array": [
                        {"kind": "number", "number": "12.50"},
                        {"kind": "bool", "bool": True},
                        {"kind": "null"},
                    ],
                },
            },
        ],
    }
    reset_first = {
        "kind": "object",
        "object": [
            {"key": "stale", "value": {"kind": "string", "string": "discard"}},
            {"key": "other", "value": {"kind": "number", "number": "9"}},
        ],
    }
    reset_second = {
        "kind": "array",
        "array": [
            {"kind": "string", "string": "fresh"},
            {"kind": "number", "number": "2"},
        ],
    }
    return build, reset_first, reset_second


def requests() -> list[dict[str, Any]]:
    build, reset_first, reset_second = fixtures()
    lookup_json = '{"a":{"s":"hi","n":-7,"f":1.25,"b":true}}'
    return [
        request(
            "parse",
            '{"name":"A\\nB","n":42,"f":-1.25e2,"ok":true,'
            '"nil":null,"arr":[1,"x"],"dup":1,"dup":2}',
        ),
        request("parse", '"snowman \\u2603"'),
        request("parse", "42"),
        request("parse", "-1.25e2"),
        request("parse", "{"),
        request("validate", " \n [1,true,null] \t"),
        request("validate", "[1,]"),
        request("validate", "true false"),
        request(
            "get",
            '{"a":{"items":[3,{"x":"hit"}]}}',
            ["a", "items", "1", "x"],
        ),
        request("get", '{"a":1}', ["missing"]),
        request("handy", lookup_json, ["a", "s"]),
        request("handy", lookup_json, ["a", "n"]),
        request("handy", lookup_json, ["a", "f"]),
        request("handy", lookup_json, ["a", "b"]),
        request("scan", ' {"x":1}\n[2,3]  "end" true '),
        request("scan", "1 {"),
        request(
            "mutate",
            '{"keep":1,"drop":2}',
            [
                {"operation": "set", "key": "keep", "value": "9"},
                {"operation": "set", "key": "added", "value": '"yes"'},
                {"operation": "del", "key": "drop"},
            ],
        ),
        request(
            "mutate",
            "[1]",
            [
                {"operation": "set_array_item", "index": 3, "value": "4"},
                {"operation": "del", "key": "1"},
            ],
        ),
        request("arena_build", [build]),
        request("arena_reset", [reset_first, reset_second]),
        request(
            "pool_parse",
            ['{"wide":[1,2,3],"tail":true}', '["short"]', '{"new":7}'],
        ),
        request("unknown"),
        request("parse", "NaN"),
        request("parse", "+Inf"),
        request("validate", "NaN"),
        request(
            "mutate",
            "[]",
            [{"operation": "set_array_item", "index": -1, "value": "1"}],
        ),
        request("arena_build", [{"kind": "number", "number": "NaN"}]),
    ]


def check(rows: list[dict[str, Any]]) -> None:
    parsed = value(rows[0])
    assert parsed["type"] == "object"
    assert parsed["marshaled"] == (
        '{"name":"A\\nB","n":42,"f":-1.25e2,"ok":true,'
        '"nil":null,"arr":[1,"x"],"dup":1,"dup":2}'
    )
    assert [entry["key"] for entry in parsed["object"]] == [
        "name",
        "n",
        "f",
        "ok",
        "nil",
        "arr",
        "dup",
        "dup",
    ]
    assert parsed["object"][0]["value"]["string"] == "A\nB"
    assert parsed["object"][1]["value"]["int64"] == 42
    assert parsed["object"][2]["value"]["float64"] == -125.0
    assert parsed["object"][3]["value"]["bool"] is True
    assert parsed["object"][5]["value"]["array"][1]["string"] == "x"

    assert value(rows[1])["string"] == "snowman \u2603"
    assert value(rows[2])["int64"] == 42
    assert value(rows[2])["uint64"] == 42
    assert value(rows[3])["float64"] == -125.0
    assert rows[4]["error_type"] == "CallFailed"
    assert value(rows[5]) is True
    assert value(rows[6]) is False
    assert value(rows[7]) is False

    selected = value(rows[8])
    assert selected["exists"] is True
    assert selected["value"]["string"] == "hit"
    assert value(rows[9]) == {"exists": False}

    assert value(rows[10]) == {
        "exists": True,
        "string": "hi",
        "bytes": "hi",
        "int": 0,
        "float": 0,
        "bool": False,
    }
    assert value(rows[11])["int"] == -7
    assert value(rows[12])["float"] == 1.25
    assert value(rows[13])["bool"] is True

    scanned = value(rows[14])
    assert [item["type"] for item in scanned] == [
        "object",
        "array",
        "string",
        "true",
    ]
    assert scanned[0]["object"][0]["key"] == "x"
    assert scanned[1]["array"][1]["int64"] == 3
    assert rows[15]["error_type"] == "CallFailed"

    assert value(rows[16]) == '{"keep":9,"added":"yes"}'
    assert value(rows[17]) == "[1,null,4]"
    assert value(rows[18]) == '{"name":"A\\nB","items":[12.50,true,null]}'
    assert value(rows[19]) == '["fresh",2]'

    pooled = value(rows[20])
    assert [item["marshaled"] for item in pooled] == [
        '{"wide":[1,2,3],"tail":true}',
        '["short"]',
        '{"new":7}',
    ]
    assert rows[21]["error_type"] == "InvalidInput"
    assert value(rows[22]) == {"type": "number", "marshaled": "NaN"}
    assert value(rows[23]) == {"type": "number", "marshaled": "+Inf"}
    assert value(rows[24]) is False
    assert rows[25]["error_type"] == "InvalidInput"
    assert rows[26]["error_type"] == "InvalidInput"


def main() -> None:
    check(run(requests()))
    print(json.dumps({"operation": "fastjson-contract", "status": "passed"}))


if __name__ == "__main__":
    main()
