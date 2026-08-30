from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCENARIOS = [
    "multidict", "multidict_convert", "immutable", "type_conversion", "headers",
    "accept", "mime_accept", "etags", "authorization", "http_headers", "options",
    "etag", "date", "cookie", "urls", "safe_join", "password", "wsgi_host",
    "limited_stream", "limited_stream_disconnect", "sansio_request", "sansio_response",
    "response", "request_values", "client", "client_cookie", "routing_match",
    "routing_build", "environ", "filestorage", "repr_headers", "header_delete",
    "routing_missing", "bad_password", "cookie_empty",
]

EXPECTED: dict[str, Any] = {
    "multidict": ["1", ["1", "2"], {"a": ["1", "2"], "b": ["x"]}, [["a", "1"], ["a", "2"], ["b", "x"]]],
    "multidict_convert": [[2, 3], "d", None, ["4", "5"]],
    "immutable": [["1", "2"], "builtins.TypeError", "MultiDict"],
    "type_conversion": [4, 9, 7],
    "headers": ["text/html", ["a", "b"], [["CONTENT-TYPE", "text/html"], ["X-Test", "a"], ["x-test", "b"]]],
    "accept": ["text/plain", 1, ["text/html", "text/plain", "*/*"]],
    "mime_accept": ["application/json", True, True],
    "etags": [True, True, True, '"abc", W/"weak"', ["abc", "weak"]],
    "authorization": ["basic", "alice", "secret", "Basic YWxpY2U6c2VjcmV0"],
    "http_headers": [["a", "b,c", "d"], 'a, "b,c"', {"a": "1; b=two"}, 'text/plain; charset=utf-8; x="a b"'],
    "options": ["form-data", {"filename": "a.txt", "name": "field"}],
    "etag": ['"abc"', 'W/"abc"', ["abc", True], "Ophdp0/iJbIEXBcta9OQvYVfCG4+nVJbRr/iRRFDFTI"],
    "date": ["Thu, 02 Jan 2020 03:04:05 GMT", "2020-01-02T03:04:05+00:00"],
    "cookie": ["session=abc; HttpOnly; Path=/; SameSite=Lax", "abc"],
    "urls": ["https://xn--r8jz45g.xn--zckzah/%E8%B7%AF%E5%BE%84?q=%E9%9B%AA", "https://例え.テスト/路"],
    "safe_join": ["/srv/files/a/b.txt", None, None],
    "password": [True, True, False],
    "wsgi_host": ["example.test", "https://example.test/x?a=1"],
    "limited_stream": ["ab", "cd", 4, "b''"],
    "limited_stream_disconnect": None,
    "sansio_request": ["https://example.test/a?x=1", "https://example.test/a", "example.test", True, True],
    "sansio_response": [201, "201 Created", "application/json", True, True],
    "response": [201, "hello", "yes"],
    "request_values": ["/search", "hello", "Alice"],
    "client": [200, "GET:1", "GET:1"],
    "client_cookie": ["set", "seen"],
    "routing_match": ["user", {"id": 42}],
    "routing_build": ["/user/42", "http://example.test/user/42"],
    "environ": ["POST", "/hello", "x=1", "yes"],
    "filestorage": ["data.txt", "text/plain", "payload"],
    "repr_headers": "Headers([('X-Test', 'yes')])",
    "header_delete": [None, [["Other", "ok"]]],
    "routing_missing": "werkzeug.exceptions.NotFound",
    "bad_password": False,
    "cookie_empty": "empty=; Path=/",
}

ADAPTER_PATH = Path("/tmp/werkzeug-verifier-adapter.py")


def materialize_adapter() -> None:
    data = (Path(__file__).resolve().parent / "adapter.py").read_bytes()
    ADAPTER_PATH.write_bytes(data)
    ADAPTER_PATH.chmod(0o555)


def invoke(name: str) -> dict[str, Any]:
    materialize_adapter()
    command = [
        "/usr/sbin/runuser", "-u", "candidate", "--", "env",
        "HOME=/tmp", "TMPDIR=/tmp", "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1", sys.executable,
        "-I", "-B", str(ADAPTER_PATH), "--candidate-site",
        "/tmp/candidate-site", "--scenario", name,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": completed.stderr[-1000:]}
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return result if isinstance(result, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def main() -> int:
    leaves = []
    for name in SCENARIOS:
        result = invoke(name)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        expected = EXPECTED.get(name)
        passed = name in EXPECTED and actual == expected
        leaves.append({"id": f"werkzeug/{name}", "status": "passed" if passed else "failed", "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1000]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
