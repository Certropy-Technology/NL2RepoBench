from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
PREFIX = "NL2REPO_S3FS_RESULT="
SCENARIOS = [
    "exports-and-metadata", "constructor-options", "constructor-validation", "split-paths",
    "chunking-and-version-helper", "utils-serialization", "error-translation",
    "retry-configuration", "root-and-cache", "cached-listing", "fake-info", "fake-exists",
    "pipe-file", "buffered-read", "buffered-write", "async-stream", "open-validation",
    "mapping-factory", "requester-pays", "cache-invalidation",
]
EXPECTED: dict[str, Any] = {
    "exports-and-metadata": {"distribution": "0+unknown", "exports": ["S3File", "S3FileSystem", "S3Map", "add_retryable_error", "set_custom_error_handler"], "module": "s3fs.core", "version": "0+unknown"},
    "constructor-options": {"anon": True, "block": 123, "cache": "none", "concurrency": 3, "endpoint": "http://example.invalid", "expiry": True, "fixed": True, "protocol": ["s3", "s3a"], "req_kw": {"RequestPayer": "requester"}, "requester_pays": True, "version_aware": True},
    "constructor-validation": {"aliases": ["u", "p"], "bad_concurrency": {"message": "max_concurrency must be >= 1", "type": "builtins.ValueError"}, "key_conflict": {"message": "'Supply either key or username, not both'", "type": "builtins.KeyError"}, "secret_conflict": {"message": "'Supply secret or password, not both'", "type": "builtins.KeyError"}},
    "split-paths": {"access_point": ["arn:aws:s3:us-east-1:123456789012:accesspoint/ap", "key", None], "aware_version": ["bucket", "key", "v1"], "plain": [["bucket", "key", None], ["bucket", "key/", None], ["bucket", "", None]], "plain_version": ["bucket", "key", None]},
    "chunking-and-version-helper": {"chunks": [52428800, 52428800, 52428800, 52428800], "large": 549755814, "version_ids": [{}, {}, {"VersionId": "v1"}]},
    "utils-serialization": {"empty_sse": {}, "sse": {"SSEKMSKeyId": "kid", "ServerSideEncryption": "AES256"}, "title": ["ContentType", "Etag", "XAmzMetaFoo", ""]},
    "error-translation": {"known": {"cause": True, "message": "missing", "type": "FileNotFoundError"}, "unknown": {"errno": 5, "type": "OSError"}},
    "retry-configuration": {"grew": True, "handler": True, "registered": True},
    "root-and-cache": {"after": [None, []], "before": [""], "root": True},
    "cached-listing": {"cached": ["bucket/a", "bucket/z"], "detail": [{"name": "bucket/z", "size": 2, "type": "file"}, {"name": "bucket/a", "size": 1, "type": "file"}], "names": ["bucket/a", "bucket/z"]},
    "fake-info": {"call": [{"kwargs": {"Bucket": "bucket", "Key": "key"}, "method": "head_object"}], "info": {"ContentType": "text/plain", "ETag": '"abc"', "LastModified": "", "StorageClass": "STANDARD", "VersionId": None, "name": "bucket/key", "size": 7, "type": "file"}},
    "fake-exists": {"bucket": True, "calls": ["head_object", "head_bucket"], "object": True},
    "pipe-file": {"body": "abc", "bucket": "bucket", "key": "key.txt", "method": "put_object", "result": {"ETag": "etag"}},
    "buffered-read": {"closed": True, "range": None, "value": "abcdef"},
    "buffered-write": {"body": "hello", "bucket": "bucket", "key": "key", "method": "put_object", "written": 5},
    "async-stream": {"first": "stream", "loc": 11, "second": "-data", "size": 11},
    "open-validation": {"compression": {"message": "", "type": "builtins.ValueError"}, "text": {"message": "", "type": "builtins.ValueError"}},
    "mapping-factory": {"check": False, "class": "FSMap", "create": False, "fs_class": "S3FileSystem", "root": "bucket/prefix"},
    "requester-pays": {"file": {"RequestPayer": "requester"}, "fs": {"RequestPayer": "requester"}, "requester": {"RequestPayer": "requester"}},
    "cache-invalidation": {"remaining": [""]},
}


def invoke(adapter: Path, site: str, scenario: str) -> dict[str, Any]:
    command = [RUNUSER, "-u", "candidate", "--", "env", "HOME=/tmp", "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1", "NL2REPO_CANDIDATE_DEPENDENCIES=/opt/candidate-dependencies/site", sys.executable, "-I", "-B", str(adapter), "--candidate-site", site, "--scenario", scenario]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=8, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.startswith(PREFIX)]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": completed.stderr[-1000:]}
    try:
        value = json.loads(lines[0][len(PREFIX):])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return value if isinstance(value, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", default="/tmp/candidate-site")
    args = parser.parse_args()
    adapter_source = Path(__file__).with_name("adapter.py")
    adapter = Path(tempfile.mktemp(prefix="s3fs-adapter-", suffix=".py"))
    adapter.write_bytes(adapter_source.read_bytes())
    os.chown(adapter, 10001, 10001)
    os.chmod(adapter, 0o500)
    leaves = []
    try:
        for scenario in SCENARIOS:
            result = invoke(adapter, args.candidate_site, scenario)
            actual = result.get("value") if result.get("ok") else result
            passed = result.get("ok") is True and actual == EXPECTED[scenario]
            message = "" if passed else json.dumps({"actual": actual, "expected": EXPECTED[scenario]}, sort_keys=True)[:2000]
            leaves.append({"id": f"s3fs/{scenario}", "status": "passed" if passed else "failed", "message": message})
    finally:
        adapter.unlink(missing_ok=True)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    # A valid report may contain failed leaves; the wrapper grades those
    # statuses. Reserve non-zero exits for failures to produce a report.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
