"""Fail-closed allowlist for the Node/npm verifier protocol."""

from __future__ import annotations

import argparse
import json
import os
import stat
from pathlib import Path
from typing import Any, Literal

from nl2repobench.domain.canonical_models import CanonicalRecord as RecordModel

MAX_NODE_PLAN_BYTES = 4096
EXPECTED_NODE_PLAN: dict[str, Any] = {
    "candidate_install": "npm-pack-offline-v1",
    "report_format": "node-test-json-v1",
    "runner": "node-test-subprocess-boundary-v1",
    "schema_version": "1.0",
    "test_root": "/tests/private",
}


class NodeVerifierCommandPlan(RecordModel):
    """Allowlisted Node verifier behavior; arbitrary shell is never accepted."""

    runner: Literal["node-test-subprocess-boundary-v1"] = "node-test-subprocess-boundary-v1"
    candidate_install: Literal["npm-pack-offline-v1", "pnpm-pack-offline-v1"]
    report_format: Literal["node-test-json-v1"] = "node-test-json-v1"
    test_root: Literal["/tests/private"] = "/tests/private"

    @classmethod
    def expected(cls, candidate_install: str = "npm-pack-offline-v1") -> NodeVerifierCommandPlan:
        return cls.model_validate({**EXPECTED_NODE_PLAN, "candidate_install": candidate_install})

    def as_allowlist(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


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
    if payload != EXPECTED_NODE_PLAN:
        raise ValueError("Node command plan does not match the allowlisted verifier protocol")


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
    plan = NodeVerifierCommandPlan.model_validate(payload)
    if plan.candidate_install != candidate_install:
        raise ValueError("Node command plan package manager does not match runtime")
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
