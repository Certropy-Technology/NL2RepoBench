"""Fail-closed allowlist for the Node/pnpm verifier protocol."""

from __future__ import annotations

EXPECTED_PNPM_PLAN = {
    "identity": "node+pnpm",
    "candidate_install": "pnpm-pack-offline-v1",
    "report_format": "node-test-json-v1",
    "runner": "node-test-subprocess-boundary-v1",
    "schema_version": "1.0",
    "test_root": "/tests/private",
    "steps": [],
}
