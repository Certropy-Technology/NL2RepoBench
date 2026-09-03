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
    result = subprocess.run([PROXY, BRIDGE], input=request + "\n", text=True,
                            capture_output=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"{operation} bridge exited {result.returncode}: {result.stderr[:400]}")
    lines = result.stdout.splitlines()
    if len(lines) != 1:
        raise AssertionError(f"{operation} returned {len(lines)} lines")
    value = json.loads(lines[0])
    if not isinstance(value, dict):
        raise AssertionError(f"{operation} response is not an object")
    return value


def expect_value(operation: str, args: list[Any], expected: Any) -> None:
    global CHECKS
    response = invoke(operation, args)
    if response.get("error_type"):
        raise AssertionError(f"{operation} unexpectedly failed: {response}")
    if response.get("value") != expected:
        raise AssertionError(f"{operation}: got {response.get('value')!r}, want {expected!r}")
    CHECKS += 1


def expect_error(operation: str, args: list[Any], error_type: str = "CallFailed") -> None:
    global CHECKS
    response = invoke(operation, args)
    if response.get("error_type") != error_type or not response.get("message"):
        raise AssertionError(f"{operation} did not return {error_type}: {response}")
    CHECKS += 1


def snap(text: str, original: str, prefix: str, segments: list[int],
         prerelease: str = "", metadata: str = "") -> dict[str, Any]:
    return {"string": text, "original": original, "prefix": prefix,
            "metadata": metadata, "prerelease": prerelease,
            "segments": segments}


def main() -> None:
    expect_value("parse", ["1.2.3", False, ""], snap("1.2.3", "1.2.3", "", [1, 2, 3]))
    expect_value("parse", ["1.2", False, ""], snap("1.2.0", "1.2", "", [1, 2, 0]))
    expect_value("parse", ["v7", False, ""], snap("7.0.0", "v7", "", [7, 0, 0]))
    expect_value("parse", ["1.04.0+build.2", False, ""],
                 snap("1.4.0+build.2", "1.04.0+build.2", "", [1, 4, 0], metadata="build.2"))
    expect_value("parse", ["1.2.3-alpha.1+linux-amd64", False, ""],
                 snap("1.2.3-alpha.1+linux-amd64", "1.2.3-alpha.1+linux-amd64", "",
                      [1, 2, 3], "alpha.1", "linux-amd64"))
    expect_value("parse", ["release-v1.2.3-beta", False, "release-"],
                 snap("1.2.3-beta", "release-v1.2.3-beta", "release-", [1, 2, 3], "beta"))
    expect_error("parse", ["1.2.3", False, "deploy-"])
    expect_value("parse", ["1.2", True, ""], snap("1.2.0", "1.2", "", [1, 2, 0]))
    expect_error("parse", ["1.2.3-", True, ""])
    expect_error("parse", ["1..2", False, ""])
    expect_error("parse", ["18446744073709551616", False, ""])

    expect_value("compare", ["1.0.0-alpha", "1.0.0-alpha.1"], -1)
    expect_value("compare", ["1.0.0-beta.11", "1.0.0-rc.1"], -1)
    expect_value("compare", ["1.0.0", "1.0.0-rc.1"], 1)
    expect_value("compare", ["1.0", "1.0.0"], 0)
    expect_value("compare", ["1.0.0+build.1", "1.0.0+build.9"], 0)
    expect_value("compare", ["2.0.0", "1.99.99"], 1)

    expect_value("core", ["1.2.3-alpha+meta"], snap("1.2.3", "1.2.3", "", [1, 2, 3]))
    expect_value("core", ["7"], snap("7.0.0", "7.0.0", "", [7, 0, 0]))

    expect_value("constraint_check", [">= 1.2, < 2.0", "1.5.0"], True)
    expect_value("constraint_check", [">= 1.2, < 2.0", "2.0.0"], False)
    expect_value("constraint_check", ["~> 1.2", "1.9.9"], True)
    expect_value("constraint_check", ["~> 1.2", "2.0.0"], False)
    expect_value("constraint_check", ["~> 1.2.3", "1.2.99"], True)
    expect_value("constraint_check", ["~> 1.2.3", "1.3.0"], False)
    expect_value("constraint_check", ["!= 1.2.3", "1.2.4"], True)
    expect_value("constraint_check", ["!= 1.2.3", "1.2.3"], False)
    expect_value("constraint_check", ["1.2.3", "1.2.3"], True)
    expect_value("constraint_check", ["1.2.3", "1.2.4"], False)
    expect_value("constraint_check", ["> 1.0, <= 2.0", "2.0"], True)
    expect_value("constraint_check", ["> 1.0, <= 2.0", "1.0.0"], False)
    expect_value("constraint_check", [">= 1.2.3", "1.2.3-beta"], False)
    expect_value("constraint_check", [">= 1.2.3-beta", "1.2.3-beta.1"], True)
    expect_value("constraint_check", ["~> 1.2-beta", "1.2.5"], False)
    expect_error("constraint_check", [">= nope", "1.2.3"])

    expect_value("constraint_string", [" >= 1.0, < 2.0 "], " >= 1.0, < 2.0 ")

    expect_value("sort", [["2.0.0", "1.0.0", "1.0.0-alpha", "1.0.0-alpha.1"]],
                 ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0", "2.0.0"])
    expect_value("sort", [["1.2", "1.0.0", "1.0.0+build", "2"]],
                 ["1.0.0", "1.0.0+build", "1.2.0", "2.0.0"])
    expect_value("sort", [[]], [])
    expect_error("sort", [["1.2.3", "not-a-version"]])
    expect_error("sort", [["1.2.3"]] * 65, "InvalidInput")

    expect_error("unknown", [], "InvalidInput")
    expect_error("parse", ["1.2.3", False], "InvalidInput")

    print(json.dumps({"contract": "go-version", "checks": CHECKS, "status": "passed"}))


if __name__ == "__main__":
    main()
