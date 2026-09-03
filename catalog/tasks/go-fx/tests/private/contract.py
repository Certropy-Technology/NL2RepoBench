import json
import subprocess
import sys


bridge, proxy = sys.argv[1:]


def call(operation, value):
    request = json.dumps(
        {"operation": operation, "args": [value]},
        ensure_ascii=False,
        separators=(",", ":"),
    )
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
    return json.loads(lines[0])


def value(operation, input_value):
    response = call(operation, input_value)
    assert "error_type" not in response, response
    return response["value"]


def test_shell_parser():
    cases = {
        "": "",
        "one two": "onetwo",
        'one "two three" four': "onetwo threefour",
        'a\\ b "c\\"d" \'e f\'': 'a bc"de f',
        "alpha # ignored\nbeta": "alphabeta",
        'one "two three': "onetwo three",
        "one 'two three'": "onetwo three",
        "seven#eight": "seven#eight",
    }
    for source, expected in cases.items():
        assert value("shell_parse", source) == expected, source


def test_width():
    cases = {
        "": 0,
        "hello": 5,
        "a\nb": 3,
        "a\rb": 3,
        "你好": 4,
        "ab你好cd": 8,
        "e\u0301": 1,
        "🚀": 2,
    }
    for source, expected in cases.items():
        assert value("string_width", source) == expected, source


test_shell_parser()
test_width()
print(json.dumps({"operation": "public-api", "status": "passed"}, separators=(",", ":")))
