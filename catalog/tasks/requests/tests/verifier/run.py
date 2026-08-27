from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ADAPTER = Path(__file__).with_name("adapter.py")
SCHEMA = "requests-offline-slice-v1"

CASES = [
    ("packaging-version", "packaging", {"all_names": True, "version": "2.34.2"}),
    ("case-insensitive-headers", "case_insensitive", {"equal": True, "keys": ["content-type", "X-ID"], "lookup": "application/json", "lower": [["content-type", "application/json"], ["x-id", "1"]]}),
    ("lookup-dict", "lookup_dict", {"attribute": 200, "item": 200, "missing": None, "repr": "<lookup 'status'>"}),
    ("request-preparation", "request_prepare", {"fragment": True, "header": "yes", "method": "GET", "path_url": "/path?a=1&q=a+b", "url": "https://example.test/path?a=1&q=a+b#frag"}),
    ("json-body", "json_body", {"body": '{"n": 2, "ok": true}', "content_type": "application/json", "length": "20"}),
    ("form-body", "form_body", {"body": "a=1&a=2&q=a+b", "content_type": "application/x-www-form-urlencoded", "length": "13"}),
    ("response-decoding", "response_decode", {"content": '{"name":"Ada","n":2}', "json": {"n": 2, "name": "Ada"}, "ok": True, "text": '{"name":"Ada","n":2}'}),
    ("response-iteration", "response_iter", {"chunks": ["aa", "\nb", "b\n", "cc"], "lines": ["aa", "bb", "cc"]}),
    ("response-status", "response_status", {"ok": False, "raised": {"has_status": True, "request": True, "type": "HTTPError"}, "redirect": False}),
    ("basic-auth", "basic_auth", {"expected": "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==", "header": "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=="}),
    ("cookies", "cookies", {"dict": {"scoped": "yes", "sid": "abc", "theme": "dark"}, "domain": {"scoped": "yes"}, "header": "sid=abc; theme=dark; scoped=yes"}),
    ("session-preparation", "session_prepare", {"cookie": "sid=abc", "request_header": "one", "session_header": "yes", "url": "https://example.test/items"}),
    ("local-adapter-session", "adapter_session", {"body": "adapter", "closed_before": False, "request_method": "POST", "seen": [{"body": "x=1", "method": "POST", "url": "https://example.test/submit"}], "status": 200}),
    ("response-hooks", "hooks", {"content": "hook", "events": [[200, True]], "header": "yes"}),
    ("redirect-chain", "redirects", {"final": "https://example.test/next#fragment", "history": [302], "seen": [{"body": None, "method": "GET", "url": "https://example.test/start#fragment"}, {"body": None, "method": "GET", "url": "https://example.test/next#fragment"}], "status": 200}),
    ("redirect-methods", "redirect_methods", {"post302": {"seen": [["POST", "body", "4"], ["GET", None, None]], "status": 200}, "post307": {"seen": [["POST", "body", "4"], ["POST", "body", "4"]], "status": 200}}),
    ("utilities", "utilities", {"auth": ["u", "p"], "defrag": "https://example.test/path", "dict_header": {"a": "1", "b": "two"}, "links": [{"rel": "next", "url": "https://example.test/2"}], "list_header": ["one", "two words", "three"], "requote": "https://example.test/a%20b", "slices": ["ab", "cd", "ef"]}),
    ("status-codes", "status_codes", {"found": 302, "missing": 404, "ok": 200, "too_many": 429}),
    ("prepared-copy", "prepared_copy", {"independent_headers": True, "repr": True, "same_body": True, "same_url": True}),
    ("response-links", "response_links", {"next": {"rel": "next", "url": "https://example.test/2"}, "prev": {"rel": "prev", "url": "https://example.test/0"}}),
    ("session-close", "session_close", {"adapters": 2, "closed": True}),
]


def invoke(operation: str) -> dict[str, object]:
    request = json.dumps({"operation": operation, "schema_version": SCHEMA}, sort_keys=True, separators=(",", ":"))
    command = [
        "runuser", "-u", "candidate", "--", "env", "HOME=/home/candidate",
        "PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0", "PYTHONNOUSERSITE=1",
        sys.executable, "-I", "-B", "-", "--candidate-site",
        os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--dependency-site", os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"),
        "--request", request,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") == "1":
        command = [sys.executable, "-I", "-B", "-", "--candidate-site", os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"), "--dependency-site", os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", ""), "--request", request]
    try:
        completed = subprocess.run(command, input=ADAPTER.read_bytes(), capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError) as error:
        return {"ok": False, "exception_type": type(error).__name__, "exception_message": str(error)}
    lines = [line for line in completed.stdout.decode("utf-8", "replace").splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": (completed.stderr or completed.stdout).decode("utf-8", "replace")[-2000:]}
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as error:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(error)}
    return value if isinstance(value, dict) else {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": "adapter response is not an object"}


def main() -> None:
    leaves = []
    for case_id, operation, expected in CASES:
        actual = invoke(operation)
        passed = actual.get("ok") is True and actual.get("value") == expected
        leaf = {"id": "requests/" + case_id, "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1200]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
