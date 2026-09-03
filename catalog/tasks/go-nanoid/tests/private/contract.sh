#!/usr/bin/env bash
set -euo pipefail
bridge="${1:?bridge executable is required}"
proxy="${2:?bridge proxy is required}"
python3 - "$bridge" "$proxy" <<'PY'
import json
import subprocess
import sys
import unicodedata

bridge, proxy = sys.argv[1:]


def call(operation, args=()):
    payload = json.dumps(
        {"operation": operation, "args": list(args)}, separators=(",", ":")
    ) + "\n"
    result = subprocess.run(
        [proxy, bridge], input=payload, text=True,
        capture_output=True, check=False, timeout=12,
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert len(lines) == 1, result.stdout
    return json.loads(lines[0])


def value(operation, args=()):
    response = call(operation, args)
    assert "error_type" not in response, response
    return response["value"]


def expect_error(operation, args, error_type="CallFailed"):
    response = call(operation, args)
    assert response.get("error_type") == error_type, response
    assert response.get("message"), response


def assert_runes(value, size, alphabet):
    assert len(value) == size, (value, len(value), size)
    assert all(char in alphabet for char in value), (value, alphabet)


constants = value("constants")
assert constants == {
    "AlphaNum": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "Alpha": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "AlphaLowerNum": "abcdefghijklmnopqrstuvwxyz0123456789",
    "AlphaUpperNum": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "AlphaLower": "abcdefghijklmnopqrstuvwxyz",
    "AlphaUpper": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "Numeric": "0123456789",
    "CrockfordBase32Upper": "0123456789ABCDEFGHJKMNPQRSTVWXYZ",
    "CrockfordBase32Lower": "0123456789abcdefghjkmnpqrstvwxyz",
}

ascii_id = value("generate", ["abcdef", 64])
assert_runes(ascii_id, 64, "abcdef")
unicode_alphabet = "🚀💩🦄🤖"
unicode_id = value("generate", [unicode_alphabet, 40])
assert_runes(unicode_id, 40, unicode_alphabet)
assert all(unicodedata.category(char) == "So" for char in unicode_id)
assert_runes(value("must_generate", ["01", 17]), 17, "01")

expect_error("generate", ["", 4])
expect_error("generate", ["a" * 256, 4])
expect_error("generate", ["abc", -1])
expect_error("must_generate", ["", 4], "CallPanicked")

default_id = value("new")
default_alphabet = "_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
assert_runes(default_id, 21, default_alphabet)
assert_runes(value("new", [0]), 0, default_alphabet)
assert_runes(value("new", [9]), 9, default_alphabet)
expect_error("new", [-1])
expect_error("new", [1, 2])
expect_error("must", [-1], "CallPanicked")
assert value("must", [0]) == ""

invalid = call("unknown", [])
assert invalid == {"error_type": "InvalidInput", "message": "unknown operation"}
expect_error("generate", ["abc"], "InvalidInput")
print(json.dumps({"operation": "public-api", "status": "passed"}, separators=(",", ":")) )
PY
