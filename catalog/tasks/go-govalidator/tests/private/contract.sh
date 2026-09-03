#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"

python3 - "$bridge" "$proxy" <<'PY'
import json
import subprocess
import sys

bridge, proxy = sys.argv[1:]
checks = []

def value(operation, args, expected):
    checks.append(({"operation": operation, "args": args}, expected, None))

def error(operation, args, error_type):
    checks.append(({"operation": operation, "args": args}, None, error_type))

for name, text, expected in [
    ("is_email", "foo+tag@example.com", True), ("is_email", "invalid@", False),
    ("is_url", "https://example.com/a?b=c", True), ("is_url", "http//example.com", False),
    ("is_request_url", "custom://example.com", True), ("is_request_uri", "/absolute/path", True),
    ("is_alpha", "abcXYZ", True), ("is_utf_letter", "Go语言", True),
    ("is_alphanumeric", "abc123", True), ("is_utf_letter_numeric", "Go语言123", True),
    ("is_numeric", "-12.5", False), ("is_utf_numeric", "１２３", True), ("is_utf_digit", "１２３", True),
    ("is_int", "-42", True), ("is_float", "+0.125", True), ("is_null", "", True),
    ("is_not_null", "value", True), ("is_ascii", "plain-text", True),
    ("is_printable_ascii", "line\n", False), ("is_base64", "SGVsbG8=", True),
    ("is_dns_name", "service.local", True), ("is_ip", "2001:db8::1", True),
    ("is_ipv4", "127.0.0.1", True), ("is_ipv6", "127.0.0.1", False),
    ("is_port", "65535", True), ("is_mac", "3D:F2:C9:A6:B3:4F", True), ("is_host", "::1", True),
    ("is_uuid", "a987fbc9-4bed-3078-cf07-9141ba07c9f3", True),
    ("is_uuid_v3", "a987fbc9-4bed-3078-cf07-9141ba07c9f3", True),
    ("is_uuid_v4", "57b73598-8764-4ad0-a76a-679bb6640eb1", True),
    ("is_uuid_v5", "987fbc97-4bed-5078-af07-9141ba07c9f3", True),
    ("is_json", '{"nested":[1,true]}', True), ("is_hexadecimal", "deadBEEF", True),
    ("is_hexcolor", "#f00", True), ("is_rgbcolor", "rgb(0, 31, 255)", True),
    ("is_latitude", "-90.000", True), ("is_longitude", "180.1", False),
]:
    value("validate", [name, text], expected)

for name, text, params, expected in [
    ("contains", "abacada", ["aca"], True), ("matches", "123456", ["[0-9]+"], True),
    ("trim", "  value \t", [""], "value"), ("left_trim", "010100201000", ["01"], "201000"),
    ("right_trim", "010100201000", ["01"], "0101002"), ("blacklist", "a1b2c3", ["abc"], "123"),
    ("whitelist", "a3a43a5", ["a-z"], "aaa"), ("strip_low", "foo\x00\n", [False], "foo"),
    ("strip_low", "foo\n\r", [True], "foo\n\r"),
    ("replace_pattern", "ab123ba", ["[0-9]+", "aca"], "abacaba"),
    ("camel_case_to_underscore", "FooV2Bar", [], "foo_v2_bar"),
    ("underscore_to_camel_case", "my_func", [], "MyFunc"), ("reverse", "Go语言", [], "言语oG"),
    ("safe_file_name", "../../../Hello World!.txt", [], "hello-world.txt"),
    ("normalize_email", "some.name+tag@googlemail.com", [], "somename@gmail.com"),
    ("get_lines", "a\nb\nc", [], ["a", "b", "c"]), ("get_line", "a\nb\nc", ["1"], "b"),
]:
    value("transform", [name, text, *params], expected)

for name, raw, expected in [
    ("to_string", 12.5, "12.5"), ("to_string", True, "true"),
    ("to_json", {"a": [1, 2]}, '{"a":[1,2]}'), ("to_float", "1.25e2", 125),
    ("to_int", "-123", -123), ("to_boolean", "True", True), ("to_boolean", "0", False),
]:
    value("convert", [name, raw], expected)

error("validate", ["unknown", "x"], "InvalidInput")
value("transform", ["matches", "x", "((123+]"], False)
error("transform", ["get_line", "x", "not-an-index"], "CallFailed")
error("convert", ["to_boolean", 1], "InvalidInput")
error("unknown", [], "InvalidInput")
error("validate", ["is_email", "x" * (64 * 1024 + 1)], "InvalidInput")

payload = b"".join(json.dumps(request, separators=(",", ":")).encode() + b"\n" for request, _, _ in checks)
result = subprocess.run([proxy, bridge], input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if result.returncode != 0:
    raise SystemExit(f"candidate bridge returned {result.returncode}: {result.stderr.decode(errors='replace')}")
lines = result.stdout.splitlines()
if len(lines) != len(checks):
    raise SystemExit(f"expected {len(checks)} bridge responses, received {len(lines)}")
for index, ((request, expected, expected_error), raw) in enumerate(zip(checks, lines), start=1):
    try:
        actual = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"response {index} is not JSON: {exc}") from exc
    if expected_error is not None:
        if actual.get("error_type") != expected_error:
            raise SystemExit(f"response {index} for {request} expected {expected_error}, got {actual}")
    elif actual.get("value") != expected:
        raise SystemExit(f"response {index} for {request} expected {expected!r}, got {actual}")
PY
