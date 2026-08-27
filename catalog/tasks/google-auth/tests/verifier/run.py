#!/usr/bin/env python3
"""Private ``custom-json-v1`` entrypoint for the google-auth task.

The generic Harbor wrapper runs this file with ``python -I`` after it has copied
and installed the candidate workspace, and it grades the last non-empty stdout
line as a bounded JSON report.

This module is root-owned and never imports candidate code. It runs the hidden
scenario adapter as the unprivileged ``candidate`` UID with the candidate site
on ``PYTHONPATH``, so only that child process imports the candidate package.
The child is given a per-run nonce and must echo it back, which stops a
candidate from fabricating a passing report on its own stdout. The adapter pops
that nonce out of its environment before importing any candidate module.
"""

from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

ADAPTER = Path(__file__).resolve().parent / "run_scenarios.py"
# The compiled verifier image installs /tests/verifier as root-only 0500, so the
# unprivileged candidate UID cannot read the adapter in place. Stage a
# root-owned, world-readable copy the candidate can execute but never modify.
STAGE_DIR = Path("/tmp/verifier-adapter")
STAGED_ADAPTER = STAGE_DIR / "run_scenarios.py"
CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
CANDIDATE_DEPENDENCIES = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "")
CANDIDATE_USER = "candidate"
MARKER = "NL2REPO_REPORT="
TIMEOUT_SEC = float(os.environ.get("NL2REPO_ADAPTER_TIMEOUT_SEC", "180"))

SCENARIO_IDS = (
    "pkg.version",
    "pkg.namespaces",
    "helpers.scopes_string",
    "helpers.string_scopes",
    "helpers.bytes_roundtrip",
    "helpers.bytes_errors",
    "helpers.base64_roundtrip",
    "helpers.query_update",
    "helpers.datetime",
    "credentials.anonymous_state",
    "credentials.anonymous_token_error",
    "oauth.properties",
    "oauth.header_and_copy",
    "oauth.factories",
    "oauth.handler_validation",
    "oauth.universe_refresh_error",
    "credentials.scope_helper",
    "service_account.properties",
    "service_account.copies",
    "service_account.assertion",
    "jwt.encode_decode",
    "jwt.header",
    "jwt.malformed",
    "jwt.unverified_payload",
    "api_key.apply",
    "api_key.empty",
    "downscoped.boundary_json",
    "downscoped.boundary_limits",
    "cache.lru",
    "cache.disabled",
    "transport.constants",
    "exceptions.hierarchy",
)


def _all_failed(message: str) -> list[dict[str, str]]:
    return [
        {"id": name, "status": "failed", "message": message[:2000]} for name in SCENARIO_IDS
    ]


def _path_entries() -> list[str]:
    entries = [CANDIDATE_SITE]
    if CANDIDATE_DEPENDENCIES:
        entries.append(CANDIDATE_DEPENDENCIES)
    return entries


def _stage_adapter() -> Path:
    """Publish the adapter read-only for the candidate UID.

    The staging directory is root-owned and not writable by the candidate, so a
    candidate process cannot substitute the adapter between stage and run.
    """
    if os.geteuid() != 0:
        return ADAPTER
    if STAGE_DIR.exists():
        shutil.rmtree(STAGE_DIR)
    STAGE_DIR.mkdir(parents=True)
    shutil.copyfile(ADAPTER, STAGED_ADAPTER)
    os.chown(STAGE_DIR, 0, 0)
    os.chown(STAGED_ADAPTER, 0, 0)
    os.chmod(STAGE_DIR, 0o555)
    os.chmod(STAGED_ADAPTER, 0o444)
    return STAGED_ADAPTER


def _command(nonce: str, adapter: Path) -> list[str]:
    # The adapter runs under `python -I`, which deliberately ignores PYTHONPATH,
    # so the candidate site and dependency site are passed as explicit argv and
    # the adapter inserts them into sys.path itself.
    child = [
        "env",
        "HOME=/home/candidate",
        "PYTHONDONTWRITEBYTECODE=1",
        "PYTHONHASHSEED=0",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
        f"NL2REPO_REPORT_NONCE={nonce}",
        sys.executable,
        "-I",
        "-B",
        str(adapter),
        *_path_entries(),
    ]
    # Drop privileges when the verifier image provides the candidate account.
    if os.geteuid() == 0:
        return ["runuser", "-u", CANDIDATE_USER, "--", *child]
    return child


def _run(nonce: str) -> list[dict[str, object]]:
    if ADAPTER.is_symlink() or not ADAPTER.is_file():
        return _all_failed("verifier-adapter-missing")
    try:
        adapter = _stage_adapter()
    except OSError as exc:
        return _all_failed(f"verifier-adapter-stage-failed: {exc}")
    try:
        completed = subprocess.run(
            _command(nonce, adapter),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SEC,
            check=False,
            start_new_session=True,
        )
    except subprocess.TimeoutExpired:
        return _all_failed("candidate-adapter-timeout")
    except OSError as exc:
        return _all_failed(f"verifier-adapter-spawn-failed: {exc}")

    sys.stderr.write(completed.stderr[-4000:])
    lines = [line for line in completed.stdout.splitlines() if line.startswith(MARKER)]
    if len(lines) != 1:
        return _all_failed(
            f"adapter-report-missing: found {len(lines)} markers, "
            f"exit {completed.returncode}"
        )
    try:
        payload = json.loads(lines[0][len(MARKER) :])
    except json.JSONDecodeError as exc:
        return _all_failed(f"adapter-report-unparsable: {exc}")
    if not isinstance(payload, dict) or payload.get("nonce") != nonce:
        return _all_failed("adapter-report-nonce-mismatch")
    leaves = payload.get("leaves")
    if not isinstance(leaves, list) or len(leaves) != len(SCENARIO_IDS):
        return _all_failed("adapter-report-collection-mismatch")
    return leaves


def main() -> int:
    nonce = secrets.token_hex(16)
    leaves = _run(nonce)
    # The generic wrapper grades the last non-empty stdout line and derives
    # pass/fail from the leaf statuses. It treats ANY non-zero exit from this
    # entrypoint as a verifier-internal error, so a report that was produced
    # successfully must always exit 0 even when leaves failed.
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
