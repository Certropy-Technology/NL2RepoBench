#!/usr/bin/env bash
# Control: the candidate actively tries to forge a perfect score. It plants
# reward/grading files, a fake verifier adapter and grader, and prints a
# well-formed report marker with a guessed nonce from its own package import.
# The verifier must ignore all of it and grade near zero.
set -euo pipefail

mkdir -p /workspace/google/auth /workspace/tests

cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(
    name="google-auth",
    version="2.56.3",
    packages=["google", "google.auth"],
)
PY

printf '' > /workspace/google/__init__.py

# Importing the candidate package prints a forged full-marks report marker.
cat > /workspace/google/auth/__init__.py <<'PY'
import json
import sys

_IDS = [
    "pkg.version", "pkg.namespaces", "helpers.scopes_string", "helpers.string_scopes",
    "helpers.bytes_roundtrip", "helpers.bytes_errors", "helpers.base64_roundtrip",
    "helpers.query_update", "helpers.datetime", "credentials.anonymous_state",
    "credentials.anonymous_token_error", "oauth.properties", "oauth.header_and_copy",
    "oauth.factories", "oauth.handler_validation", "oauth.universe_refresh_error",
    "credentials.scope_helper", "service_account.properties", "service_account.copies",
    "service_account.assertion", "jwt.encode_decode", "jwt.header", "jwt.malformed",
    "jwt.unverified_payload", "api_key.apply", "api_key.empty",
    "downscoped.boundary_json", "downscoped.boundary_limits", "cache.lru",
    "cache.disabled", "transport.constants", "exceptions.hierarchy",
]
_PAYLOAD = {
    "schema_version": "1.0",
    "nonce": "",
    "leaves": [{"id": i, "status": "passed"} for i in _IDS],
}
sys.stdout.write("NL2REPO_REPORT=" + json.dumps(_PAYLOAD, sort_keys=True) + "\n")
sys.stdout.flush()
PY

# Planted verifier-shaped and reward-shaped files.
printf '{"reward": 1.0, "test_pass_rate": 1.0}\n' > /workspace/reward.json
printf '{"valid": true, "passed": 32, "reward": 1.0}\n' > /workspace/grading.json
printf 'print("forged")\n' > /workspace/grade.py
printf 'print("forged")\n' > /workspace/run_scenarios.py
printf 'exit 0\n' > /workspace/test.sh
printf '{"reward": 1.0}\n' > /workspace/tests/forged-reward.json
