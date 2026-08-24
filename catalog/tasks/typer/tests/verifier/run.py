"""Private trusted report writer for the typer deterministic CLI slice.

Trusted code never imports candidate modules. Each leaf runs the private
adapter in a fresh unprivileged child and compares a bounded JSON observation
against expectations frozen from revision
9a7b2e83f6b62c750d6026b0de9ebf2026a8b8fa.

Rich renders errors inside a box whose width depends on terminal settings, so
error leaves assert exit code, stream placement and message fragments rather
than frozen box bytes. Ordinary command output is asserted byte for byte.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

EXPECTED = 23
FIXTURE_SCHEMA = "typer-fixture-v1"
ADAPTER = Path(__file__).with_name("adapter.py")
CHILD_TIMEOUT_SEC = 30.0


def invocation(fixture, argv, **extra):
    request = {
        "fixture_schema": FIXTURE_SCHEMA,
        "operation": "invoke",
        "fixture": fixture,
        "argv": argv,
    }
    request.update(extra)
    return request


def ok(stdout, stderr="", exit_code=0, exception=None):
    return {
        "exception": exception,
        "exit_code": exit_code,
        "stderr": stderr,
        "stdout": stdout,
    }


CASES = [
    {
        "id": "api-surface",
        "request": {"fixture_schema": FIXTURE_SCHEMA, "operation": "api"},
        "expected": {
            "exports": {
                "Abort": True,
                "Argument": True,
                "Context": True,
                "Exit": True,
                "Option": True,
                "Typer": True,
                "echo": True,
                "run": True,
                "secho": True,
                "style": True,
            },
            "has_cli_main": True,
            "runner": True,
            "version": "0.27.1",
        },
    },
    {
        "id": "scalars-defaults",
        "request": invocation("scalars", ["alice"]),
        "expected": ok(
            "name=alice type=str\ncount=1 type=int\nratio=0.5 type=float\nflag=False type=bool\n"
        ),
    },
    {
        "id": "scalars-explicit",
        "request": invocation("scalars", ["bob", "--count", "3", "--ratio", "1.5", "--flag"]),
        "expected": ok(
            "name=bob type=str\ncount=3 type=int\nratio=1.5 type=float\nflag=True type=bool\n"
        ),
    },
    {
        "id": "scalars-invalid-int",
        "request": invocation("scalars", ["bob", "--count", "abc"]),
        "expected_shape": {
            "exit_code": 2,
            "exception": "SystemExit",
            "stdout": "",
            "stderr_fragments": [
                "Usage: main [OPTIONS]",
                "Try 'main --help' for help.",
                "Invalid value for '--count': 'abc' is not a valid int",
            ],
        },
    },
    {
        "id": "required-option-missing",
        "request": invocation("required", []),
        "expected_shape": {
            "exit_code": 2,
            "exception": "SystemExit",
            "stdout": "",
            "stderr_fragments": [
                "Usage: main [OPTIONS]",
                "Try 'main --help' for help.",
                "Missing option '--token'",
            ],
        },
    },
    {
        "id": "required-option-present",
        "request": invocation("required", ["--token", "t1"]),
        "expected": ok("token=t1 region=local\n"),
    },
    {
        "id": "required-option-envvar",
        "request": invocation("required", ["--token", "t1"], env={"SLICE_REGION": "eu"}),
        "expected": ok("token=t1 region=eu\n"),
    },
    {
        "id": "enum-default",
        "request": invocation("enum", []),
        "expected": ok("level=low member=low type=Level\n"),
    },
    {
        "id": "enum-explicit",
        "request": invocation("enum", ["--level", "high"]),
        "expected": ok("level=high member=high type=Level\n"),
    },
    {
        "id": "enum-invalid-choice",
        "request": invocation("enum", ["--level", "mid"]),
        "expected_shape": {
            "exit_code": 2,
            "exception": "SystemExit",
            "stdout": "",
            "stderr_fragments": [
                "Usage: main [OPTIONS]",
                "Invalid value for '--level': 'mid' is not one of 'low', 'high'",
            ],
        },
    },
    {
        "id": "containers-defaults",
        "request": invocation("containers", []),
        "expected": ok(
            "tag=[] type=list\npair=['none', 0] types=['str', 'int']\nnote=None type=NoneType\n"
        ),
    },
    {
        "id": "containers-multiple",
        "request": invocation(
            "containers",
            ["--tag", "a", "--tag", "b", "--pair", "x", "7", "--note", "hi"],
        ),
        "expected": ok(
            "tag=['a', 'b'] type=list\npair=['x', 7] types=['str', 'int']\nnote=hi type=str\n"
        ),
    },
    {
        "id": "richtypes-conversion",
        "request": invocation(
            "richtypes",
            [
                "--id",
                "12345678-1234-5678-1234-567812345678",
                "--when",
                "2020-01-02T03:04:05",
                "--target",
                "some/dir/file.txt",
            ],
        ),
        "expected": ok(
            "id=12345678-1234-5678-1234-567812345678 type=UUID\n"
            "when=2020-01-02T03:04:05 type=datetime\n"
            "target=some/dir/file.txt type=PosixPath\n"
        ),
    },
    {
        "id": "richtypes-invalid-uuid",
        "request": invocation(
            "richtypes",
            ["--id", "not-a-uuid", "--when", "2020-01-02T03:04:05", "--target", "f.txt"],
        ),
        "expected_shape": {
            "exit_code": 2,
            "exception": "SystemExit",
            "stdout": "",
            "stderr_fragments": [
                "Usage: main [OPTIONS]",
                "Invalid value for '--id': 'not-a-uuid' is not a valid UUID",
            ],
        },
    },
    {
        "id": "group-command-add",
        "request": invocation("group", ["add", "4"]),
        "expected": ok("sum=6 verbose=False\n"),
    },
    {
        "id": "group-callback-option",
        "request": invocation("group", ["--verbose", "add", "4", "--beta", "5"]),
        "expected": ok("sum=9 verbose=True\n"),
    },
    {
        "id": "group-renamed-command",
        "request": invocation("group", ["join-words", "a", "b", "--separator", "+"]),
        "expected": ok("a+b\n"),
    },
    {
        "id": "group-unknown-command",
        "request": invocation("group", ["missing"]),
        "expected_shape": {
            "exit_code": 2,
            "exception": "SystemExit",
            "stdout": "",
            "stderr_fragments": ["No such command 'missing'"],
        },
    },
    {
        "id": "nested-subcommand",
        "request": invocation("nested", ["items", "show", "21"]),
        "expected": ok("doubled=42\n"),
    },
    {
        "id": "nested-sibling-command",
        "request": invocation("nested", ["version"]),
        "expected": ok("slice-1\n"),
    },
    {
        "id": "streams-prompt-and-stderr",
        "request": invocation("streams", [], input="typed\n"),
        "expected": ok("Label: typed\nlabel=typed\nstyled\n", stderr="warned\n"),
    },
    {
        "id": "streams-explicit-exit-code",
        "request": invocation("streams", ["--label", "L", "--fail"]),
        "expected": ok(
            "label=L\nstyled\n", stderr="warned\n", exit_code=3, exception="SystemExit"
        ),
    },
    {
        "id": "callback-exception",
        "request": invocation("failing", ["--reason", "nope"]),
        "expected": ok("", exit_code=1, exception="ValueError"),
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
            "COLUMNS=80",
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
        return {
            "ok": False,
            "exception_type": "VerifierProcessError",
            "exception_message": str(error),
        }
    lines = [
        line for line in completed.stdout.decode("utf-8", "replace").splitlines() if line.strip()
    ]
    if completed.returncode != 0 or not lines:
        detail = completed.stderr.decode("utf-8", "replace") or completed.stdout.decode(
            "utf-8", "replace"
        )
        return {
            "ok": False,
            "exception_type": "CandidateProcessError",
            "exception_message": detail[-2000:],
        }
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError as error:
        return {
            "ok": False,
            "exception_type": "CandidateProtocolError",
            "exception_message": str(error),
        }


def matches_shape(value, shape):
    if not isinstance(value, dict):
        return False
    if value.get("exit_code") != shape["exit_code"]:
        return False
    if value.get("exception") != shape["exception"]:
        return False
    if value.get("stdout") != shape["stdout"]:
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
            passed = result.get("ok") is True and matches_shape(
                result.get("value"), case["expected_shape"]
            )
            expected = case["expected_shape"]
        else:
            passed = result.get("ok") is True and result.get("value") == case["expected"]
            expected = case["expected"]
        leaf = {"id": "typer/" + case["id"], "status": "passed" if passed else "failed"}
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
