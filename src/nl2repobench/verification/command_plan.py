"""Fail-closed runtime validation for the compiler-selected verifier plan."""

from __future__ import annotations

import argparse
import json
import os
import stat
from pathlib import Path
from typing import Any

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.command_plan import MAX_COMMAND_PLAN_BYTES, CommandPlan

EXPECTED_PLAN: dict[str, Any] = CommandPlan(
    identity="python+uv",
    runner="pytest-subprocess-boundary-v1",
    candidate_install="pip-target-no-deps-v1",
    report_format="pytest-junit-xml-v1",
).model_dump(mode="json")


def expected_python_command_plan(
    *,
    identity: str = "python+uv",
    report_format: str = "pytest-junit-xml-v1",
) -> CommandPlan:
    if identity not in {"python+uv", "python+pip", "python+none"}:
        raise ValueError("Python command plan identity is not adapter-owned")
    return CommandPlan.model_validate(
        {
            **EXPECTED_PLAN,
            "identity": identity,
            "report_format": report_format,
        }
    )


def _validate_python_plan_semantics(
    payload: object,
    *,
    identity: str,
    report_format: str,
) -> CommandPlan:
    if not isinstance(payload, dict):
        raise ValueError("Python command plan does not match the allowlisted verifier protocol")
    try:
        plan = CommandPlan.model_validate(payload)
        expected = expected_python_command_plan(
            identity=identity,
            report_format=report_format,
        )
    except ValueError as exc:
        raise ValueError(
            "Python command plan does not match the allowlisted verifier protocol; "
            f"canonical validation failed: {exc}"
        ) from exc
    for field in (
        "schema_version",
        "identity",
        "runner",
        "candidate_install",
        "report_format",
        "test_root",
    ):
        if getattr(plan, field) != getattr(expected, field):
            raise ValueError(
                "Python command plan does not match the allowlisted verifier protocol"
            )
    return plan


def load_python_command_plan(
    data: bytes,
    *,
    identity: str = "python+uv",
    report_format: str = "pytest-junit-xml-v1",
) -> CommandPlan:
    """Validate canonical artifact bytes against the selected Python adapter."""

    if len(data) > MAX_COMMAND_PLAN_BYTES:
        raise ValueError("Python command plan exceeds the size limit")
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Python command plan JSON: {exc}") from exc
    plan = _validate_python_plan_semantics(
        payload,
        identity=identity,
        report_format=report_format,
    )
    if data != canonical_json(plan) + b"\n":
        raise ValueError("Python command plan JSON is not canonical")
    return plan


def validate_command_plan(
    path: Path,
    *,
    identity: str = "python+uv",
    report_format: str = "pytest-junit-xml-v1",
) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_COMMAND_PLAN_BYTES:
            raise ValueError("command plan must be a bounded regular file")
        data = os.read(descriptor, MAX_COMMAND_PLAN_BYTES + 1)
    finally:
        os.close(descriptor)
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid command plan JSON: {exc}") from exc
    _validate_python_plan_semantics(
        payload,
        identity=identity,
        report_format=report_format,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--identity", default="python+uv")
    parser.add_argument("--report-format", default="pytest-junit-xml-v1")
    args = parser.parse_args()
    validate_command_plan(
        args.path,
        identity=args.identity,
        report_format=args.report_format,
    )


if __name__ == "__main__":
    main()
