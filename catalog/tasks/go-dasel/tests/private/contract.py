import json
import subprocess
import sys


bridge, proxy = sys.argv[1:]


def raw_request(operation, args):
    request = json.dumps({"operation": operation, "args": args}, separators=(",", ":"))
    completed = subprocess.run(
        [proxy, bridge], input=request + "\n", text=True,
        capture_output=True, check=False, timeout=8,
    )
    if completed.returncode != 0:
        raise AssertionError(f"bridge exit {completed.returncode}: {completed.stderr}")
    lines = completed.stdout.splitlines()
    if len(lines) != 1:
        raise AssertionError(f"expected one response, got {completed.stdout!r}")
    return json.loads(lines[0])


def call(operation, args):
    response = raw_request(operation, args)
    if "error_type" in response:
        raise AssertionError(f"bridge error: {response}")
    return response["value"]


def check_selection_basics():
    document = {
        "users": [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False},
            {"name": "Cara", "age": 41, "active": True},
        ]
    }
    selected = call("select", [document, "users.map(name)..."])
    assert selected == {"values": ["Alice", "Bob", "Cara"], "count": 3}
    queried = call("query", [document, "users.map(age)..."])
    assert queried == {"values": [30, 25, 41], "count": 3}
    filtered = call("select", [document, "users.filter(active).map(name)..."])
    assert filtered == {"values": ["Alice", "Cara"], "count": 2}


def check_selector_evaluation():
    document = {
        "users": [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False},
            {"name": "Cara", "age": 41, "active": True},
        ]
    }
    conditional = call("select", [document, 'users.map(age >= 30 ? name : "junior")...'])
    assert conditional == {"values": ["Alice", "junior", "Cara"], "count": 3}
    arithmetic = call("select", [[1, 2, 3], "$this.map($this * 2)..."])
    assert arithmetic == {"values": [2, 4, 6], "count": 3}
    indexed = call("select", [["zero", "one", "two"], "$this[1]"])
    assert indexed == {"values": ["one"], "count": 1}


def check_mutation():
    document = {
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ],
        "untouched": {"ok": True},
    }
    changed = call("modify", [document, "users[1].name", "Robert"])
    assert changed == {
        "count": 1,
        "data": {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Robert", "age": 25},
            ],
            "untouched": {"ok": True},
        },
    }
    root = call("modify", [[1, 2, 3], "$this[1]", 99])
    assert root == {"count": 1, "data": [1, 99, 3]}


def check_errors_and_bounds():
    response = raw_request("select", [{"x": 1}, "x.no_such_call("])
    assert response.get("error_type") == "CallFailed"
    bad = raw_request("unknown", [])
    assert bad.get("error_type") == "InvalidInput"
    too_long = "x" * 513
    bounded = raw_request("select", [{"x": 1}, too_long])
    assert bounded.get("error_type") == "InvalidInput"


check_selection_basics()
check_selector_evaluation()
check_mutation()
check_errors_and_bounds()
print(json.dumps({"operation": "public-api", "status": "passed"}, separators=(",", ":")))
