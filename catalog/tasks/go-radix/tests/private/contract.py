import json
import subprocess
import sys


bridge, proxy = sys.argv[1:]


def invoke(operation, args):
    request = json.dumps({"operation": operation, "args": args}, separators=(",", ":"))
    completed = subprocess.run(
        [proxy, bridge],
        input=request + "\n",
        text=True,
        capture_output=True,
        check=False,
        timeout=8,
    )
    assert completed.returncode == 0, completed.stderr
    lines = completed.stdout.splitlines()
    assert len(lines) == 1, completed.stdout
    response = json.loads(lines[0])
    assert "error_type" not in response, response
    return response["value"]


def expect_error(operation, args):
    request = json.dumps({"operation": operation, "args": args}, separators=(",", ":"))
    completed = subprocess.run(
        [proxy, bridge],
        input=request + "\n",
        text=True,
        capture_output=True,
        check=False,
        timeout=8,
    )
    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response.get("error_type") == "InvalidInput", response


def check_snapshot():
    entries = [
        {"key": "", "value": "root"},
        {"key": "app", "value": 1},
        {"key": "apple", "value": 2},
        {"key": "app/api", "value": 3},
        {"key": "app/web", "value": {"ok": True}},
        {"key": "banana", "value": 5},
        {"key": "band", "value": 6},
    ]
    result = invoke(
        "snapshot",
        [
            {
                "entries": entries,
                "lookups": ["app", "missing", "", "app/web"],
                "longest": ["applepie", "app/api/v1", "cat", ""],
                "prefixes": ["app", "app/", "ban", "x"],
                "paths": ["app/api/v1", "applepie", ""],
            }
        ],
    )
    assert result["len"] == 7
    assert result["lookups"] == [
        {"value": 1, "found": True},
        {"value": None, "found": False},
        {"value": "root", "found": True},
        {"value": {"ok": True}, "found": True},
    ]
    assert result["longest"] == [
        {"key": "apple", "value": 2, "found": True},
        {"key": "app/api", "value": 3, "found": True},
        {"key": "", "value": "root", "found": True},
        {"key": "", "value": "root", "found": True},
    ]
    assert result["minimum"] == {"key": "", "value": "root", "found": True}
    assert result["maximum"] == {"key": "band", "value": 6, "found": True}
    assert result["walk"] == {
        "keys": ["", "app", "app/api", "app/web", "apple", "banana", "band"],
        "values": ["root", 1, 3, {"ok": True}, 2, 5, 6],
    }
    assert result["prefixes"] == [
        {"keys": ["app", "app/api", "app/web", "apple"], "values": [1, 3, {"ok": True}, 2]},
        {"keys": ["app/api", "app/web"], "values": [3, {"ok": True}]},
        {"keys": ["banana", "band"], "values": [5, 6]},
        {"keys": [], "values": []},
    ]
    assert result["paths"] == [
        {"keys": ["", "app", "app/api"], "values": ["root", 1, 3]},
        {"keys": ["", "app", "apple"], "values": ["root", 1, 2]},
        {"keys": [""], "values": ["root"]},
    ]
    assert result["map"] == {
        "": "root", "app": 1, "apple": 2, "app/api": 3,
        "app/web": {"ok": True}, "banana": 5, "band": 6,
    }


def check_mutation():
    result = invoke(
        "mutate",
        [
            {
                "entries": [
                    {"key": "", "value": 0},
                    {"key": "app", "value": 1},
                    {"key": "app/api", "value": 2},
                    {"key": "app/web", "value": 3},
                    {"key": "banana", "value": 4},
                    {"key": "band", "value": 5},
                ],
                "inserts": [
                    {"key": "app", "value": 10},
                    {"key": "app/new", "value": 6},
                    {"key": "z", "value": 7},
                ],
                "deletes": ["missing", "app/api", ""],
                "delete_prefixes": ["app/", "ban"],
            }
        ],
    )
    assert result["inserts"] == [
        {"old": 1, "updated": True},
        {"old": None, "updated": False},
        {"old": None, "updated": False},
    ]
    assert result["deletes"] == [
        {"value": None, "found": False},
        {"value": 2, "found": True},
        {"value": 0, "found": True},
    ]
    assert result["prefix_deletes"] == [2, 2]
    assert result["len"] == 2
    assert result["walk"] == {"keys": ["app", "z"], "values": [10, 7]}
    assert result["map"] == {"app": 10, "z": 7}


def check_callbacks_and_errors():
    entries = [
        {"key": "d", "value": 4}, {"key": "b", "value": 2},
        {"key": "a", "value": 1}, {"key": "c", "value": 3},
    ]
    assert invoke("callbacks", [{"entries": entries, "stop_after": 2}]) == {
        "seen": ["a", "b"], "len": 4
    }
    assert invoke("callbacks", [{"entries": entries, "stop_after": 0}]) == {
        "seen": ["a", "b", "c", "d"], "len": 4
    }
    expect_error("unknown", [])
    expect_error("snapshot", [])
    expect_error("callbacks", [{"entries": [], "stop_after": -1}])


check_snapshot()
check_mutation()
check_callbacks_and_errors()
print(json.dumps({"operation": "public-api", "status": "passed"}, separators=(",", ":")))
