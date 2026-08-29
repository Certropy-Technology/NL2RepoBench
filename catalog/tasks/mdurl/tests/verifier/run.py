# ruff: noqa: E501, I001

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from adapter import run_candidate


FIXTURE_PATH = Path(__file__).with_name("fixture_url.py")
namespace: dict[str, Any] = {}
exec(compile(FIXTURE_PATH.read_text(encoding="utf-8"), str(FIXTURE_PATH), "exec"), namespace)
FIXTURES: dict[str, dict[str, Any]] = namespace["PARSED"]


def script() -> str:
    fixture = repr(FIXTURES)
    return f'''\
import json
from mdurl import DECODE_COMPONENT_CHARS, DECODE_DEFAULT_CHARS
from mdurl import ENCODE_COMPONENT_CHARS, ENCODE_DEFAULT_CHARS
from mdurl import URL, __all__, __version__, decode, encode, format, parse

FIXTURES = {fixture}
results = []

def leaf(leaf_id, thunk):
    try:
        value = thunk()
    except BaseException as exc:
        results.append({{"id": leaf_id, "ok": False, "error": f"{{type(exc).__module__}}.{{type(exc).__qualname__}}", "message": str(exc)}})
    else:
        results.append({{"id": leaf_id, "ok": True, "value": value}})

leaf("api/version-and-exports", lambda: [__version__, list(__all__)])
leaf("api/url-shape", lambda: [URL._fields, URL(None, False, None, None, None, None, None, None)])
leaf("api/url-input-identity", lambda: (lambda value: parse(value) is value)(URL("x:", False, None, None, None, None, None, None)))
leaf("api/constants", lambda: [DECODE_DEFAULT_CHARS, DECODE_COMPONENT_CHARS, ENCODE_DEFAULT_CHARS, ENCODE_COMPONENT_CHARS])
leaf("api/slashes-denote-host", lambda: parse("//example.com/path", slashes_denote_host=True)._asdict())
leaf("api/trim-whitespace", lambda: parse("  http://example.com/path  ")._asdict())
leaf("api/ipv6-format", lambda: format(parse("http://[::1]:8080/p")))
leaf("api/encode-escaped-toggle", lambda: [encode("%2f", keep_escaped=True), encode("%2f", keep_escaped=False)])
leaf("api/decode-exclude", lambda: decode("%20%2F", exclude=" /"))
leaf("api/roundtrip-custom", lambda: format(parse("dash-test:foo/bar")))

leaf("decode/multi-byte", lambda: decode("https://host.invalid/%F0%9F%91%A9"))
leaf("decode/invalid-utf8", lambda: [decode("https://host.invalid/%CF"), decode("https://host.invalid/%C0%bf"), decode("https://host.invalid/%F1%81%d1%45")])

for index, (value, expected) in enumerate([
    ("%%%", "%25%25%25"), ("\\r\\n", "%0D%0A"), ("?#", "?#"),
    ("[]^", "%5B%5D%5E"), ("my url", "my%20url"), ("φου", "%CF%86%CE%BF%CF%85"),
    ("%FG", "%25FG"), ("%00%FF", "%00%FF"), ("\\x00\\x7f\\x80", "%00%7F%C2%80"),
]):
    leaf(f"encode/param-{{index}}", lambda value=value: encode(value))
leaf("encode/arguments", lambda: [encode("!@#$", exclude="@$"), encode("%20%2G", keep_escaped=True), encode("%20%2G", keep_escaped=False), encode("!@%25", exclude="@", keep_escaped=False)])
leaf("encode/surrogates", lambda: [encode("\\ud800foo"), encode("foo\\ud800"), encode("\\udd00foo"), encode("foo\\udd00"), encode("𐄀")])

for index, (url, expected) in enumerate(FIXTURES.items()):
    def parse_case(url=url, expected=expected):
        value = parse(url)
        return [value.protocol, value.slashes, value.auth, value.port, value.hostname, value.hash, value.search, value.pathname] == [expected.get("protocol"), expected.get("slashes", False), expected.get("auth"), expected.get("port"), expected.get("hostname"), expected.get("hash"), expected.get("search"), expected.get("pathname")]
    leaf(f"parse/fixture-{{index}}", parse_case)
    leaf(f"format/fixture-{{index}}", lambda url=url: format(parse(url)))

result = {{"results": results}}
'''


def main() -> int:
    observed = run_candidate(script())
    raw_results = observed.get("value", {}).get("results") if observed.get("ok") else None
    results_valid = isinstance(raw_results, list)
    leaves = []
    results = raw_results if results_valid else []
    expected: dict[str, object] = {
        "api/version-and-exports": ["0.1.2", ["decode", "DECODE_DEFAULT_CHARS", "DECODE_COMPONENT_CHARS", "encode", "ENCODE_DEFAULT_CHARS", "ENCODE_COMPONENT_CHARS", "format", "parse", "URL"]],
        "api/url-shape": [["protocol", "slashes", "auth", "port", "hostname", "hash", "search", "pathname"], [None, False, None, None, None, None, None, None]],
        "api/url-input-identity": True,
        "api/constants": [";/?:@&=+$,#", "", ";/?:@&=+$,-_.!~*'()#", "-_.!~*'()"],
        "api/slashes-denote-host": {"protocol": None, "slashes": True, "auth": None, "port": None, "hostname": "example.com", "hash": None, "search": None, "pathname": "/path"},
        "api/trim-whitespace": {"protocol": "http:", "slashes": True, "auth": None, "port": None, "hostname": "example.com", "hash": None, "search": None, "pathname": "/path"},
        "api/ipv6-format": "http://[::1]:8080/p",
        "api/encode-escaped-toggle": ["%2f", "%252f"],
        "api/decode-exclude": "%20%2F",
        "api/roundtrip-custom": "dash-test:foo/bar",
        "decode/multi-byte": "https://host.invalid/👩",
        "decode/invalid-utf8": ["https://host.invalid/�", "https://host.invalid/��", "https://host.invalid/���E"],
    }
    expected.update({
        f"encode/param-{i}": value for i, value in enumerate(["%25%25%25", "%0D%0A", "?#", "%5B%5D%5E", "my%20url", "%CF%86%CE%BF%CF%85", "%25FG", "%00%FF", "%00%7F%C2%80"])
    })
    expected["encode/arguments"] = ["%21@%23$", "%20%252G", "%2520%252G", "%21@%2525"]
    expected["encode/surrogates"] = ["%EF%BF%BDfoo", "foo%EF%BF%BD", "%EF%BF%BDfoo", "foo%EF%BF%BD", "%F0%90%84%80"]
    for index, (url, fixture) in enumerate(FIXTURES.items()):
        expected[f"parse/fixture-{index}"] = [fixture.get("protocol"), fixture.get("slashes", False), fixture.get("auth"), fixture.get("port"), fixture.get("hostname"), fixture.get("hash"), fixture.get("search"), fixture.get("pathname")]  # compared specially below
        expected[f"format/fixture-{index}"] = url
    observed_by_id = {item.get("id"): item for item in results if isinstance(item, dict)}
    for leaf_id, want in expected.items():
        item = observed_by_id.get(leaf_id, {})
        actual = item.get("value") if item.get("ok") is True else item.get("error")
        if leaf_id.startswith("parse/"):
            fixture = list(FIXTURES.values())[int(leaf_id.rsplit("-", 1)[1])]
            passed = actual is True
        else:
            passed = item.get("ok") is True and actual == want
        diagnostic = {
            "actual": actual,
            "expected": want,
            "candidate_message": item.get("message"),
            "candidate_response": observed if not results_valid else None,
        }
        leaves.append({"id": f"mdurl/{leaf_id}", "status": "passed" if passed else "failed", "message": "" if passed else json.dumps(diagnostic, ensure_ascii=False, sort_keys=True)[:1000]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
