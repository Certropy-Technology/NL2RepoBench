import json
import subprocess
import sys


bridge, proxy = sys.argv[1:]


def call(operation, args):
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
    response = json.loads(lines[0])
    if "error_type" in response:
        raise AssertionError(f"bridge error: {response}")
    return response["value"]


def check_get():
    document = '{"name":{"first":"Janet","last":"Prichard"},"age":47,"active":true}'
    value = call("get", [document, "name.last"])
    assert value["type"] == "String" and value["raw"] == '"Prichard"'
    assert value["str"] == "Prichard" and value["string"] == "Prichard"
    assert value["exists"] and not value["is_array"] and not value["is_bool"]

    number = call("get", [document, "age"])
    assert number["type"] == "Number" and number["raw"] == "47"
    assert number["num"] == 47 and number["int"] == 47 and number["uint"] == 47
    assert number["float"] == 47 and number["string"] == "47" and number["bool"]


def check_parse_and_paths():
    parsed = call("parse", [' {"friends":[{"first":"Dale","last":"Murphy"},{"first":"Jane","last":"Murphy"}]} '])
    assert parsed["type"] == "JSON" and parsed["raw"].startswith("{")
    matches = call(
        "get", [
            '{"friends":[{"first":"Dale","last":"Murphy"},{"first":"Jane","last":"Murphy"},{"first":"Roger","last":"Craig"}]}',
            'friends.#(last=="Murphy")#.first',
        ],
    )
    assert matches["type"] == "JSON" and matches["raw"] == '["Dale","Jane"]'
    count = call("get", ['{"children":["Sara","Alex","Jack"]}', "children.#"])
    assert count["type"] == "Number" and count["string"] == "3"
    escaped = call("get", ['{"fav.movie":"Deer Hunter"}', r"fav\.movie"])
    assert escaped["string"] == "Deer Hunter"


def check_many_and_validation():
    values = call("get_many", ['{"a":1,"b":"two","missing":null}', ["a", "b", "missing", "none"]])
    assert len(values) == 4
    assert values[0]["string"] == "1" and values[1]["string"] == "two"
    assert values[2]["type"] == "Null" and not values[3]["exists"]
    assert call("valid", ['{"ok":[1,true,null]}']) is True
    assert call("valid", ['{"ok":']) is False
    assert call("escape", ["fav.movie*"]) == r"fav\.movie\*"


check_get()
check_parse_and_paths()
check_many_and_validation()
print(json.dumps({"operation": "public-api", "status": "passed"}, separators=(",", ":")))
