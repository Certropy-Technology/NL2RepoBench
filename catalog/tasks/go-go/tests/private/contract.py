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
            f"{operation} bridge call failed with {result.returncode}: "
            f"{result.stderr[:500]}"
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
            f"{operation} value mismatch: "
            f"got {response.get('value')!r}, want {expected!r}"
        )
    CHECKS += 1


def expect_error(operation: str, args: list[Any]) -> None:
    global CHECKS
    response = invoke(operation, args)
    if response.get("error_type") != "CallFailed" or not response.get("message"):
        raise AssertionError(f"{operation} did not return a package error: {response}")
    CHECKS += 1


def main() -> None:
    base64_cases = [
        ("", ""),
        ("f", "Zg=="),
        ("fo", "Zm8="),
        ("foo", "Zm9v"),
        ("foob", "Zm9vYg=="),
        ("fooba", "Zm9vYmE="),
        ("foobar", "Zm9vYmFy"),
        ("Hello World!", "SGVsbG8gV29ybGQh"),
        ("Go, 世界", "R28sIOS4lueVjA=="),
    ]
    for raw, encoded in base64_cases:
        expect_value("base64_encode", [raw], encoded)
        expect_value("base64_decode", [encoded], raw)

    binary_cases = [
        ("0", 0),
        ("1", 1),
        ("00000101", 5),
        ("101010", 42),
        ("1111111111111111111111111111111", 2147483647),
    ]
    for binary, decimal in binary_cases:
        expect_value("binary_to_decimal", [binary], decimal)
    for invalid in ["", "10201", " 101", "1" * 33]:
        expect_error("binary_to_decimal", [invalid])

    reverse_cases = [
        ("", ""),
        ("algorithm", "mhtirogla"),
        ("A界🙂", "🙂界A"),
        ("mañana", "anañam"),
    ]
    for original, reversed_value in reverse_cases:
        expect_value("reverse", [original], reversed_value)

    decimal_cases = [
        (0, "0"),
        (1, "1"),
        (42, "101010"),
        (1024, "10000000000"),
        (2147483647, "1111111111111111111111111111111"),
    ]
    for decimal, binary in decimal_cases:
        expect_value("decimal_to_binary", [decimal], binary)
    expect_error("decimal_to_binary", [-1])

    roman_cases = [
        (1, "I"),
        (4, "IV"),
        (9, "IX"),
        (58, "LVIII"),
        (1994, "MCMXCIV"),
        (3999, "MMMCMXCIX"),
    ]
    for decimal, roman in roman_cases:
        expect_value("int_to_roman", [decimal], roman)
        expect_value("roman_to_int", [roman], decimal)
    expect_error("int_to_roman", [0])
    expect_error("int_to_roman", [4000])
    expect_value("roman_to_int", [""], 0)
    for invalid in ["abc", "iv", "IVCMXCIX"]:
        expect_error("roman_to_int", [invalid])

    rgb_cases = [
        (0x000000, [0, 0, 0]),
        (0xFFFFFF, [255, 255, 255]),
        (0x1ABC9C, [26, 188, 156]),
        (0x12345678, [52, 86, 120]),
    ]
    for packed, components in rgb_cases:
        expect_value("hex_to_rgb", [packed], components)
    for components, packed in [
        ([0, 0, 0], 0x000000),
        ([255, 255, 255], 0xFFFFFF),
        ([52, 152, 219], 0x3498DB),
        ([222, 173, 190], 0xDEADBE),
    ]:
        expect_value("rgb_to_hex", components, packed)

    print(json.dumps({"contract": "go-go", "checks": CHECKS, "status": "passed"}))


if __name__ == "__main__":
    main()
