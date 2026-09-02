import json
import subprocess
import sys

bridge, proxy = sys.argv[1:]


def call(operation, payload):
    request = json.dumps(
        {"operation": operation, "args": [payload]}, separators=(",", ":")
    )
    completed = subprocess.run(
        [proxy, bridge], input=request + "\n", text=True,
        capture_output=True, check=False, timeout=8,
    )
    assert completed.returncode == 0, completed.stderr
    lines = completed.stdout.splitlines()
    assert len(lines) == 1, completed.stdout
    response = json.loads(lines[0])
    assert "error_type" not in response, response
    return response["value"]


def expect_invalid(operation, args):
    request = json.dumps(
        {"operation": operation, "args": args}, separators=(",", ":")
    )
    completed = subprocess.run(
        [proxy, bridge], input=request + "\n", text=True,
        capture_output=True, check=False, timeout=8,
    )
    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response.get("error_type") == "InvalidInput", response


assert call("aggregate", {"messages": [["foo", "bar"]]})["errors"] == ["foo", "bar"]
single = call("aggregate", {"messages": [["foo"]]})
assert single["text"] == "1 error occurred:\n\t* foo\n\n"
assert single["len"] == 1 and single["or_nil"] is True
assert call("format", {"messages": [["foo", "bar"]]}) == (
    "2 errors occurred:\n\t* foo\n\t* bar\n\n"
)
assert call("custom_format", {"messages": [["foo", "bar"]]}) == "custom:foo|bar"
assert call("append_nested", {"messages": [["one"], ["two", "three"]]}) == {
    "errors": ["one", "two", "three"], "len": 3
}
assert call("flatten", {"messages": [["one"], ["two", "three"]]})["errors"] == [
    "one", "two", "three"
]
assert call("prefix", {"messages": [["foo", "bar"]], "prefix": "scope"}) == {
    "errors": ["scope foo", "scope bar"],
    "text": "2 errors occurred:\n\t* scope foo\n\t* scope bar\n\n",
}
assert call("unwrap", {"messages": [["one", "two", "three"]]}) == [
    "3 errors occurred:\n\t* one\n\t* two\n\t* three\n\n", "one", "two", "three"
]
assert call("is_as", {"messages": [["sentinel", "typed"]]}) == {
    "is": True, "as": True, "as_text": "typed"
}
assert call("sort", {"messages": [["foo", "bar", "baz"]]}) == ["bar", "baz", "foo"]
grouped = call("group", {"messages": [["", "z", "a"]]})
assert grouped["nil"] is False and grouped["errors"] == ["a", "z"]
assert call("group", {"messages": [["", ""]]}) == {"errors": [], "nil": True}
expect_invalid("invalid", [])
print(json.dumps({"operation": "public-api", "status": "passed"}, separators=(",", ":")))
