from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

RUNUSER = "/usr/sbin/runuser"
SCENARIOS: dict[str, Any] = {
    "api/components": ["http", "user:pass@example.com:8080", "/a/b", "x=1", "frag", {"userinfo": "user:pass", "host": "example.com", "port": "8080"}],
    "api/unsplit": "http://example.com/a%2fb?x=%3a#f",
    "api/normalize": "http://example.com/b/%7E?q=%3A",
    "api/valid": [True, True], "uri/absolute": [True, False],
    "uri/resolve": "http://example.com/x?y=1", "uri/copy": "http://example.com/b#f",
    "uri/userinfo": ["user:pass", "example.com", "8080"],
    "iri/parts": ["例え.テスト", "/%E3%83%91%E3%82%B9", "q=%E5%80%A4", "%E9%83%A8%E5%88%86"],
    "iri/encode": "https://xn--r8jz45g.xn--zckzah/%E3%83%91%E3%82%B9?q=%E5%80%A4#%E9%83%A8%E5%88%86",
    "parse/urlparse": ["http", "user:pass", "example.com", 8080, "/a", "x=1", "f"],
    "parse/shims": ["example.com", "example.com", "x=1", "http://example.com/a?x=1"],
    "parse/copy": "http://example.com/b?y=2", "parse/encode": ["ParseResultBytes", "http://example.com/a?x=1"],
    "parse/from-parts": "https://u@example.com:443/x?a=1#f",
    "builder/chain": "https://example.com/b?q=a+b#Top", "builder/credentials": "//u:p%40ss@example.com", "builder/extend": "/a/b?x=1",
    "normalizers/percent": "%3A%AF%zz", "normalizers/host": "example.com", "normalizers/ipv6-zone": "[fe80::1%25eth0]", "normalizers/path": "/a/c", "normalizers/encoding": "caf%C3%A9%20path", "misc/merge": "/a/c",
    "validator/ok": None, "validator/missing": "rfc3986.exceptions.MissingComponentError", "validator/unpermitted": "rfc3986.exceptions.UnpermittedComponentError", "validator/password": "rfc3986.exceptions.PasswordForbidden", "validator/ipv4": [True, False],
    "exceptions/messages": ['The port ("abc") is not valid.', "The authority (bad) is not valid."],
    "bytes/reference": ["str", "http://example.com/a", "bytes", "http://example.com"],
    "uri/query-empty": "http://example.com/a?", "uri/fragment-empty": "http://example.com/a#", "uri/normalized-equality": True, "uri/authority-invalid": "rfc3986.exceptions.InvalidAuthority",
    "validator/component": [True, True, True], "builder/port-boundary": ["0", "65535"], "api/reexports": ["2.0.0", "URIReference", "IRIReference", True, True],
}


def invoke(scenario: str) -> dict[str, Any]:
    command = [RUNUSER, "-u", "candidate", "--", "env", "HOME=/tmp", "TMPDIR=/tmp", "PATH=/usr/local/bin:/usr/bin:/bin", "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1", sys.executable, "-I", "-B", "-", "--candidate-site", "/tmp/candidate-site", "--dependency-site", "/opt/candidate-dependencies/site", "--scenario", scenario]
    adapter_source = Path(__file__).with_name("adapter.py").read_text(encoding="utf-8")
    try:
        completed = subprocess.run(command, input=adapter_source, capture_output=True, text=True, timeout=2, check=False)
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
    for scenario, expected in SCENARIOS.items():
        result = invoke(scenario)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        passed = actual == expected
        leaves.append({"id": f"rfc3986/{scenario}", "status": "passed" if passed else "failed", "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, ensure_ascii=False, sort_keys=True)[:1000]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
