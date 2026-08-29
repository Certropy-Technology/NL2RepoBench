from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

ADAPTER = Path(__file__).with_name("run_scenarios.py")
STAGE_DIR = Path("/tmp/google-api-core-verifier")
STAGED_ADAPTER = STAGE_DIR / "run_scenarios.py"
MARKER = "NL2REPO_REPORT="
SCENARIOS = (
    ("pkg", "package-identity-and-import-boundary"),
    ("client_info", "client-info-user-agent-order"),
    ("options", "client-options-storage-and-repr"),
    ("option_errors", "client-options-validation"),
    ("datetime", "datetime-epoch-conversions"),
    ("rfc3339", "rfc3339-offset-and-format"),
    ("nanoseconds", "nanosecond-preservation"),
    ("path", "path-template-expansion-and-validation"),
    ("path_mutation", "path-field-read-and-delete"),
    ("rest_flatten", "rest-query-flattening"),
    ("exceptions", "http-and-grpc-exception-mapping"),
    ("universe", "universe-domain-and-endpoint-selection"),
    ("timeout", "constant-and-exponential-timeouts"),
    ("deadline_timeout", "injected-clock-deadline-timeout"),
    ("retry", "retry-predicates-and-backoff"),
    ("retry_call", "retry-wrapper-repeats-transient-failure"),
    ("protobuf", "protobuf-field-access"),
    ("field_mask", "protobuf-field-mask"),
    ("page", "page-iteration-state"),
    ("version_header", "api-version-header"),
    ("optional_boundary", "optional-grpc-import-boundary"),
)


def invoke(operation, nonce):
    if os.geteuid() == 0:
        shutil.rmtree(STAGE_DIR, ignore_errors=True)
        STAGE_DIR.mkdir(mode=0o555)
        shutil.copyfile(ADAPTER, STAGED_ADAPTER)
        os.chown(STAGE_DIR, 0, 0)
        os.chown(STAGED_ADAPTER, 0, 0)
        os.chmod(STAGE_DIR, 0o555)
        os.chmod(STAGED_ADAPTER, 0o444)
        adapter = STAGED_ADAPTER
    else:
        adapter = ADAPTER
    command = [
        "runuser", "-u", "candidate", "--", "env",
        "HOME=/home/candidate", "PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0",
        "PYTHONNOUSERSITE=1", "LC_ALL=C.UTF-8", sys.executable, "-I", "-B", str(adapter),
        "--candidate-site", os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--dependency-site", os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"),
        "--operation", operation, "--nonce", nonce,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    except Exception as exc:
        return {"ok": False, "exception": type(exc).__name__, "message": str(exc)}
    reports = [line for line in result.stdout.splitlines() if line.startswith(MARKER)]
    if len(reports) != 1:
        return {"ok": False, "exception": "ProtocolError", "message": result.stderr[-1000:] or result.stdout[-1000:]}
    try:
        value = json.loads(reports[0][len(MARKER):])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception": "ProtocolError", "message": str(exc)}
    if value.get("nonce") != nonce:
        return {"ok": False, "exception": "NonceMismatch", "message": "adapter nonce mismatch"}
    return value


EXPECTED = {
    "package-identity-and-import-boundary": {"modules": True, "origin_under_site": True, "typed": True, "version": "2.35.0"},
    "client-info-user-agent-order": "tool/3 gl-python/3.12.0 grpc/grpc/1 rest/rest/4 gax/2.35.0 gapic/gapic/1 gccl/client/2 pb/pb/5",
    "client-options-storage-and-repr": {"attrs": ["api.example", ["a", "b"], "key"], "repr": "ClientOptions: {'api_endpoint': 'x', 'client_cert_source': None, 'client_encrypted_cert_source': None, 'quota_project_id': None, 'credentials_file': None, 'scopes': None, 'api_key': None, 'api_audience': None, 'universe_domain': None}"},
    "client-options-validation": ["ValueError", "ValueError", "ValueError"],
    "datetime-epoch-conversions": {"milliseconds": 1704164645123, "microseconds": 1704164645123456, "roundtrip": "2024-01-02T03:04:05.123456+00:00"},
    "rfc3339-offset-and-format": {"iso": "2020-01-02T03:04:05.123456+00:00", "formatted": "2020-01-02T03:04:05.123456Z", "date": "2020-01-02"},
    "nanosecond-preservation": {"nanosecond": 123456789, "rfc3339": "2020-01-02T03:04:05.123456789Z"},
    "path-template-expansion-and-validation": {"expanded": "v1/projects/p1/locations/l1", "positional": "books/book 1/chapters/a/b", "encoded": "a/b%20c", "valid": True, "invalid": False},
    "path-field-read-and-delete": {"request": {"a": {"keep": 4}}, "missing": "ValueError"},
    "rest-query-flattening": {"strict": [["a.b", "x"], ["a.b", "y"], ["flag", "true"]], "loose": [["n", 3], ["flag", False]], "bad": "TypeError"},
    "http-and-grpc-exception-mapping": {"http_class": "NotFound", "http_message": "404 missing", "grpc_class": "GoogleAPICallError", "status_class": "TooManyRequests", "unknown": "Cancelled"},
    "universe-domain-and-endpoint-selection": {"chosen": "custom.example", "determined": "alt.example", "mtls": "https://foo.mtls.googleapis.com:443", "endpoint": "api.alt.example", "empty": "EmptyUniverseError"},
    "constant-and-exponential-timeouts": {"seen": [7, 1, 2, 4], "constant": "<ConstantTimeout timeout=7.0>", "sequence": [1, 2, 4]},
    "injected-clock-deadline-timeout": [4.0],
    "retry-predicates-and-backoff": {"predicate": [True, False, True], "sleep": [0.8444218515250481, 1.515908805880605, 1.68228632332338, 1.2945837514648169, 2.5563736068430427], "transient": [True, False]},
    "retry-wrapper-repeats-transient-failure": {"result": "done", "attempts": 2},
    "protobuf-field-access": {"before": 1, "after": 4, "count": 7, "messages": 1},
    "protobuf-field-mask": ["seconds", "nanos"],
    "page-iteration-state": {"first": 10, "remaining": 2, "count": 3, "rest": [20, 30], "raw": {"token": "x"}},
    "api-version-header": {"key": "x-goog-api-version", "header": ["x-goog-api-version", "v1"]},
    "optional-grpc-import-boundary": {"module": "google.api_core.grpc_helpers", "missing": "ImportError"},
}


def main():
    nonce = secrets.token_hex(16)
    leaves = []
    for operation, name in SCENARIOS:
        actual = invoke(operation, nonce)
        passed = actual.get("ok") is True and actual.get("value") == EXPECTED[name]
        leaf = {"id": "google-api-core/" + name, "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = json.dumps({"actual": actual, "expected": EXPECTED[name]}, sort_keys=True)[:1800]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
