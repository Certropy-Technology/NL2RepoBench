#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


BRIDGE = sys.argv[1]
PROXY = sys.argv[2]
CHECKS = 0


def invoke(operation: str, args: list[Any]) -> dict[str, Any]:
    request = json.dumps({"operation": operation, "args": args}, separators=(",", ":"))
    result = subprocess.run(
        [PROXY, BRIDGE],
        input=request + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{operation} bridge call failed with {result.returncode}: {result.stderr[:500]}"
        )
    lines = result.stdout.splitlines()
    if len(lines) != 1:
        raise AssertionError(f"{operation} returned {len(lines)} response lines")
    try:
        response = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{operation} returned invalid JSON") from exc
    if not isinstance(response, dict):
        raise AssertionError(f"{operation} response is not an object")
    return response


def expect_value(operation: str, args: list[Any], expected: Any) -> None:
    global CHECKS
    response = invoke(operation, args)
    if response.get("error_type"):
        raise AssertionError(f"{operation} unexpectedly failed: {response}")
    if response.get("value") != expected:
        raise AssertionError(
            f"{operation} value mismatch: got {response.get('value')!r}, want {expected!r}"
        )
    CHECKS += 1


def expect_error(operation: str, args: list[Any]) -> None:
    global CHECKS
    response = invoke(operation, args)
    if response.get("error_type") != "CallFailed" or not response.get("message"):
        raise AssertionError(f"{operation} did not return a package error: {response}")
    CHECKS += 1


def version(
    normalized: str,
    original: str,
    major: int,
    minor: int,
    patch: int,
    prerelease: str = "",
    metadata: str = "",
) -> dict[str, Any]:
    return {
        "string": normalized,
        "original": original,
        "major": major,
        "minor": minor,
        "patch": patch,
        "prerelease": prerelease,
        "metadata": metadata,
    }


def main() -> None:
    expect_value("parse", ["1.2.3", False], version("1.2.3", "1.2.3", 1, 2, 3))
    expect_value("parse", ["1.2", False], version("1.2.0", "1.2", 1, 2, 0))
    expect_value("parse", ["v7", False], version("7.0.0", "v7", 7, 0, 0))
    expect_value(
        "parse",
        ["v1.2.3-alpha.1+linux-amd64", False],
        version(
            "1.2.3-alpha.1+linux-amd64",
            "v1.2.3-alpha.1+linux-amd64",
            1,
            2,
            3,
            "alpha.1",
            "linux-amd64",
        ),
    )
    expect_value(
        "parse",
        ["1.2.3-rc.1+build.9", True],
        version(
            "1.2.3-rc.1+build.9",
            "1.2.3-rc.1+build.9",
            1,
            2,
            3,
            "rc.1",
            "build.9",
        ),
    )
    expect_error("parse", ["1.2", True])
    expect_error("parse", ["1.02.3", True])
    expect_error("parse", ["1.2.3-01", True])
    expect_error("parse", ["1.2.3+bad metadata", False])

    expect_value("compare", ["1.0.0-alpha", "1.0.0-alpha.1"], -1)
    expect_value("compare", ["1.0.0-beta.11", "1.0.0-rc.1"], -1)
    expect_value("compare", ["2.0.0", "1.99.99"], 1)
    expect_value("compare", ["1.0.0+build.1", "1.0.0+build.9"], 0)

    expect_value(
        "increment",
        ["1.2.3", "patch"],
        version("1.2.4", "1.2.4", 1, 2, 4),
    )
    expect_value(
        "increment",
        ["1.2.3-alpha+build", "patch"],
        version("1.2.3", "1.2.3", 1, 2, 3),
    )
    expect_value(
        "increment",
        ["1.2.3-alpha+build", "minor"],
        version("1.3.0", "1.3.0", 1, 3, 0),
    )
    expect_value(
        "increment",
        ["1.2.3-alpha+build", "major"],
        version("2.0.0", "2.0.0", 2, 0, 0),
    )
    expect_error("increment", ["18446744073709551615.0.0", "major"])

    expect_value(
        "set_prerelease",
        ["1.2.3+build.1", "beta.2"],
        version("1.2.3-beta.2+build.1", "1.2.3-beta.2+build.1", 1, 2, 3, "beta.2", "build.1"),
    )
    expect_value(
        "set_prerelease",
        ["1.2.3-alpha", ""],
        version("1.2.3", "1.2.3", 1, 2, 3),
    )
    expect_error("set_prerelease", ["1.2.3", "01"])
    expect_value(
        "set_metadata",
        ["1.2.3-alpha", "build.42"],
        version("1.2.3-alpha+build.42", "1.2.3-alpha+build.42", 1, 2, 3, "alpha", "build.42"),
    )
    expect_value(
        "set_metadata",
        ["1.2.3+build.1", ""],
        version("1.2.3", "1.2.3", 1, 2, 3),
    )
    expect_error("set_metadata", ["1.2.3", "bad metadata"])

    constraint_cases = [
        (">=1.2.0, <2.0.0", "1.8.4", True),
        (">=1.2.0, <2.0.0", "2.0.0", False),
        ("^1.2.3", "1.9.9", True),
        ("^1.2.3", "2.0.0", False),
        ("~1.2.3", "1.2.99", True),
        ("~1.2.3", "1.3.0", False),
        ("1.2.x", "1.2.99", True),
        ("1.2.x", "1.3.0", False),
        ("1.2.3 - 2.3.4", "2.3.4", True),
        ("1.2.3 - 2.3.4", "2.3.5", False),
        (">=2.0.0 || <1.0.0", "0.9.9", True),
        (">=2.0.0 || <1.0.0", "1.5.0", False),
        (">=1.2.3", "1.3.0-beta.1", False),
    ]
    for constraint, candidate, expected in constraint_cases:
        expect_value("constraint_check", [constraint, candidate], expected)
    expect_error("constraint_check", [">= nope", "1.2.3"])

    expect_value(
        "sort",
        [["2.0.0", "1.0.0", "1.0.0-alpha.1", "1.0.0-alpha"]],
        ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0", "2.0.0"],
    )
    expect_value("sort", [[]], [])
    expect_error("sort", [["1.2.3", "not-a-version"]])

    print(json.dumps({"contract": "go-semver", "checks": CHECKS, "status": "passed"}))


if __name__ == "__main__":
    main()

