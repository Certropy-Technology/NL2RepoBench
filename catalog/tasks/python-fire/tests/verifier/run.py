"""Private trusted report writer for the python-fire deterministic slice.

Trusted code never imports candidate modules. Each leaf runs the private
adapter in a fresh unprivileged child and compares a bounded JSON observation
against expectations frozen from revision
716bbc23d7eca949fdb682172283c8d18f742cb6.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

EXPECTED = 20
FIXTURE_SCHEMA = "fire-fixture-v1"
ADAPTER = Path(__file__).with_name("adapter.py")
CHILD_TIMEOUT_SEC = 20.0


def invocation(fixture, argv):
    return {
        "fixture_schema": FIXTURE_SCHEMA,
        "operation": "invoke",
        "fixture": fixture,
        "argv": argv,
        "name": "tool",
    }


def ok(result, stdout, exit_code=0, stderr=""):
    return {
        "exception": None,
        "exit_code": exit_code,
        "result": result,
        "stderr": stderr,
        "stdout": stdout,
    }


def scalar(kind, value):
    return {"kind": kind, "value": value}


NONE = scalar("NoneType", None)

CASES = [
    {
        "id": "api-surface",
        "request": {"fixture_schema": FIXTURE_SCHEMA, "operation": "api"},
        "expected": {"all": ["Fire"], "callable_fire": True, "has_main": True, "version": "0.7.1"},
    },
    {
        "id": "positional-args",
        "request": invocation("add-function", ["1", "2"]),
        "expected": ok(scalar("int", 3), "3\n"),
    },
    {
        "id": "default-flag-value",
        "request": invocation("add-function", ["1"]),
        "expected": ok(scalar("int", 3), "3\n"),
    },
    {
        "id": "varargs-and-boolean-flag",
        "request": invocation("add-function", ["1", "2", "3", "4", "--gamma"]),
        "expected": ok(scalar("int", -10), "-10\n"),
    },
    {
        "id": "named-flags",
        "request": invocation("add-function", ["--alpha", "5", "--beta", "6"]),
        "expected": ok(scalar("int", 11), "11\n"),
    },
    {
        "id": "equals-flag-syntax",
        "request": invocation("add-function", ["1", "--beta=9"]),
        "expected": ok(scalar("int", 10), "10\n"),
    },
    {
        "id": "argument-parsing-int",
        "request": invocation("types-echo", ["10"]),
        "expected": ok(
            {"kind": "dict", "value": {"text": scalar("str", "10"), "type": scalar("str", "int")}},
            "type: int\ntext: 10\n",
        ),
    },
    {
        "id": "argument-parsing-list",
        "request": invocation("types-echo", ["--value", "[1, 2]"]),
        "expected": ok(
            {"kind": "dict", "value": {"text": scalar("str", "[1, 2]"), "type": scalar("str", "list")}},
            "type: list\ntext: [1, 2]\n",
        ),
    },
    {
        "id": "argument-parsing-unicode-string",
        "request": invocation("types-echo", ["café"]),
        "expected": ok(
            {"kind": "dict", "value": {"text": scalar("str", "'café'"), "type": scalar("str", "str")}},
            "type: str\ntext: 'café'\n",
        ),
    },
    {
        "id": "class-method-invocation",
        "request": invocation("calculator-class", ["double", "4"]),
        "expected": ok(scalar("int", 8), "8\n"),
    },
    {
        "id": "class-init-flags",
        "request": invocation("calculator-class", ["--offset", "3", "double", "4"]),
        "expected": ok(scalar("int", 11), "11\n"),
    },
    {
        "id": "class-varargs-separator",
        "request": invocation("calculator-class", ["join", "a", "b", "--separator", "+"]),
        "expected": ok(scalar("str", "a+b"), "a+b\n"),
    },
    {
        "id": "class-default-separator",
        "request": invocation("calculator-class", ["join", "x", "y"]),
        "expected": ok(scalar("str", "x-y"), "x-y\n"),
    },
    {
        "id": "dict-value-lookup",
        "request": invocation("mapping", ["value"]),
        "expected": ok(scalar("int", 7), "7\n"),
    },
    {
        "id": "dict-nested-unicode",
        "request": invocation("mapping", ["nested", "name"]),
        "expected": ok(scalar("str", "café"), "café\n"),
    },
    {
        "id": "list-index-lookup",
        "request": invocation("sequence", ["1"]),
        "expected": ok(scalar("int", 20), "20\n"),
    },
    {
        "id": "exception-exit-code",
        "request": invocation("failing-function", ["--reason", "nope"]),
        "expected": {
            "exception": "ValueError",
            "exit_code": 1,
            "result": NONE,
            "stderr": "",
            "stdout": "",
        },
    },
    {
        "id": "missing-required-argument",
        "request": invocation("add-function", []),
        "expected_shape": {
            "exit_code": 2,
            "result": NONE,
            "stdout": "",
            "stderr_fragments": [
                "ERROR: The function received no value for the required argument: alpha",
                "Usage: tool ALPHA <flags> [REST]...",
                "--beta",
                "--gamma",
                "For detailed information on this command, run:",
                "tool --help",
            ],
        },
    },
    {
        "id": "unknown-command-usage",
        "request": invocation("calculator-class", ["missing"]),
        "expected_shape": {
            "exit_code": 2,
            "result": NONE,
            "stdout": "",
            "stderr_fragments": [
                "ERROR: Could not consume arg: missing",
                "Usage: tool - <command|value>",
                "available commands:",
                "double",
                "join",
                "label",
                "available values:",
                "offset",
            ],
        },
    },
    {
        "id": "help-flag-sections",
        "request": invocation("add-function", ["--help"]),
        "expected_shape": {
            "exit_code": 0,
            "result": NONE,
            "stdout": "",
            "stderr_fragments": [
                "NAME\n    tool - Adds numbers.",
                "SYNOPSIS\n    tool ALPHA <flags> [REST]...",
                "DESCRIPTION\n    Adds numbers.",
                "POSITIONAL ARGUMENTS",
                "ALPHA\n        The first addend.",
                "FLAGS",
                "--beta=BETA",
                "Default: 2",
                "--gamma=GAMMA",
                "Default: False",
            ],
        },
    },
]


def invoke(request):
    payload = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    command = [
        sys.executable,
        "-I",
        "-B",
        "-",
        "--candidate-site",
        os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--request",
        payload,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") != "1":
        command = [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "HOME=/home/candidate",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTHONHASHSEED=0",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            "LC_ALL=C.UTF-8",
            "TZ=UTC",
            "TERM=dumb",
            "PAGER=cat",
            "ANSI_COLORS_DISABLED=1",
            "NO_COLOR=1",
            *command,
        ]
    try:
        completed = subprocess.run(
            command,
            input=ADAPTER.read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=None,
            timeout=CHILD_TIMEOUT_SEC,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"ok": False, "exception_type": "VerifierProcessError", "exception_message": str(error)}
    lines = [line for line in completed.stdout.decode("utf-8", "replace").splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        detail = completed.stderr.decode("utf-8", "replace") or completed.stdout.decode("utf-8", "replace")
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": detail[-2000:]}
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError as error:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(error)}


def matches_shape(value, shape):
    if not isinstance(value, dict):
        return False
    if value.get("exit_code") != shape["exit_code"]:
        return False
    if value.get("result") != shape["result"]:
        return False
    if value.get("stdout") != shape["stdout"]:
        return False
    if value.get("exception") is not None:
        return False
    stderr = value.get("stderr")
    if not isinstance(stderr, str):
        return False
    return all(fragment in stderr for fragment in shape["stderr_fragments"])


def main():
    leaves = []
    for case in CASES:
        result = invoke(case["request"])
        if "expected_shape" in case:
            passed = result.get("ok") is True and matches_shape(result.get("value"), case["expected_shape"])
            expected = case["expected_shape"]
        else:
            passed = result.get("ok") is True and result.get("value") == case["expected"]
            expected = case["expected"]
        leaf = {"id": "python-fire/" + case["id"], "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = json.dumps(
                {"expected": expected, "actual": result}, ensure_ascii=False, sort_keys=True
            )[:1000]
        leaves.append(leaf)
    assert len(leaves) == EXPECTED, len(leaves)
    print(
        json.dumps(
            {"schema_version": "1.0", "leaves": leaves},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
