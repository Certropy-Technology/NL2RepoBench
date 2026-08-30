"""Fail-closed allowlist for the Node/npm verifier protocol."""

from __future__ import annotations

import argparse
import json
import os
import stat
from pathlib import Path
from typing import Any, Literal

from nl2repobench.domain.command_plan import CommandPlan

MAX_NODE_PLAN_BYTES = 4 * 1024 * 1024
EXPECTED_NODE_PLAN: dict[str, Any] = {
    "identity": "node+npm",
    "candidate_install": "npm-pack-offline-v1",
    "report_format": "node-test-json-v1",
    "runner": "node-test-subprocess-boundary-v1",
    "schema_version": "1.0",
    "test_root": "/tests/private",
    "steps": [],
}


NodeVerifierCommandPlan = CommandPlan


def expected_node_command_plan(
    candidate_install: str = "npm-pack-offline-v1",
) -> NodeVerifierCommandPlan:
    manager = "pnpm" if candidate_install.startswith("pnpm-") else "npm"
    return NodeVerifierCommandPlan.model_validate(
        {
            **EXPECTED_NODE_PLAN,
            "identity": f"node+{manager}",
            "candidate_install": candidate_install,
        }
    )


def _validate_node_plan_semantics(
    payload: object, *, candidate_install: str
) -> NodeVerifierCommandPlan:
    if not isinstance(payload, dict):
        raise ValueError("Node command plan does not match the allowlisted verifier protocol")
    plan = NodeVerifierCommandPlan.model_validate(payload)
    expected = expected_node_command_plan(candidate_install)
    expected_values = expected.model_dump(mode="json")
    actual_values = plan.model_dump(mode="json")
    for field in (
        "schema_version",
        "identity",
        "runner",
        "candidate_install",
        "report_format",
        "test_root",
    ):
        if actual_values[field] != expected_values[field]:
            raise ValueError("Node command plan does not match the allowlisted verifier protocol")
    return plan


def validate_node_command_plan(path: Path) -> None:
    """Validate a bounded regular file against the exact Node allowlist."""

    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_NODE_PLAN_BYTES:
            raise ValueError("Node command plan must be a bounded regular file")
        data = os.read(descriptor, MAX_NODE_PLAN_BYTES + 1)
    finally:
        os.close(descriptor)
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Node command plan JSON: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("candidate_install") not in {
        "npm-pack-offline-v1",
        "pnpm-pack-offline-v1",
    }:
        raise ValueError("Node command plan does not match the allowlisted verifier protocol")
    _validate_node_plan_semantics(payload, candidate_install=str(payload["candidate_install"]))


def load_node_command_plan(
    data: bytes,
    *,
    candidate_install: Literal["npm-pack-offline-v1", "pnpm-pack-offline-v1"],
) -> NodeVerifierCommandPlan:
    """Validate bounded canonical JSON from a task-scoped private artifact."""

    if len(data) > MAX_NODE_PLAN_BYTES:
        raise ValueError("Node command plan exceeds the size limit")
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Node command plan JSON: {exc}") from exc
    plan = _validate_node_plan_semantics(payload, candidate_install=candidate_install)
    if data != json.dumps(
        plan.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    ).encode() + b"\n":
        raise ValueError("Node command plan JSON is not canonical")
    return plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()
    validate_node_command_plan(args.path)


if __name__ == "__main__":
    main()
