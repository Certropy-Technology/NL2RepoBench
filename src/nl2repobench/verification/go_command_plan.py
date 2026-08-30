"""Fail-closed command-plan validation for the Go/modules verifier adapter."""

from __future__ import annotations

import argparse
import json
import os
import stat
from pathlib import Path
from typing import Any

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.command_plan import MAX_COMMAND_PLAN_BYTES, CommandPlan

EXPECTED_GO_PLAN: dict[str, Any] = CommandPlan(
    identity="go+go-modules",
    runner="go-test-subprocess-boundary-v1",
    candidate_install="go-modules-offline-v1",
    report_format="go-test-json-v1",
).model_dump(mode="json")


def expected_go_command_plan() -> CommandPlan:
    return CommandPlan.model_validate(EXPECTED_GO_PLAN)


def _validate_go_plan_semantics(payload: object) -> CommandPlan:
    if not isinstance(payload, dict):
        raise ValueError("Go command plan does not match the allowlisted verifier protocol")
    try:
        plan = CommandPlan.model_validate(payload)
    except ValueError as exc:
        raise ValueError(
            "Go command plan does not match the allowlisted verifier protocol; "
            f"canonical validation failed: {exc}"
        ) from exc
    expected = expected_go_command_plan()
    for field in (
        "schema_version",
        "identity",
        "runner",
        "candidate_install",
        "report_format",
        "test_root",
    ):
        if getattr(plan, field) != getattr(expected, field):
            raise ValueError("Go command plan does not match the allowlisted verifier protocol")
    return plan


def load_go_command_plan(data: bytes) -> CommandPlan:
    """Validate bounded canonical bytes from an authorized private artifact."""

    if len(data) > MAX_COMMAND_PLAN_BYTES:
        raise ValueError("Go command plan exceeds the size limit")
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Go command plan JSON: {exc}") from exc
    plan = _validate_go_plan_semantics(payload)
    if data != canonical_json(plan) + b"\n":
        raise ValueError("Go command plan JSON is not canonical")
    return plan


def validate_go_command_plan(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_COMMAND_PLAN_BYTES:
            raise ValueError("Go command plan must be a bounded regular file")
        data = os.read(descriptor, MAX_COMMAND_PLAN_BYTES + 1)
    finally:
        os.close(descriptor)
    load_go_command_plan(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()
    validate_go_command_plan(args.path)


if __name__ == "__main__":
    main()
