"""Fail-closed runtime validation for the compiler-selected verifier plan."""

from __future__ import annotations

import argparse
import json
import os
import stat
from pathlib import Path
from typing import Any

from nl2repobench.domain.command_plan import CommandPlan

MAX_PLAN_BYTES = 4 * 1024 * 1024
EXPECTED_PLAN: dict[str, Any] = CommandPlan(
    identity="python+uv",
    runner="pytest-subprocess-boundary-v1",
    candidate_install="pip-target-no-deps-v1",
    report_format="pytest-junit-xml-v1",
).model_dump(mode="json")


def validate_command_plan(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_PLAN_BYTES:
            raise ValueError("command plan must be a bounded regular file")
        data = os.read(descriptor, MAX_PLAN_BYTES + 1)
    finally:
        os.close(descriptor)
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid command plan JSON: {exc}") from exc
    try:
        CommandPlan.model_validate(payload)
    except ValueError as exc:
        raise ValueError(
            "command plan does not match the allowlisted verifier protocol; "
            f"canonical validation failed: {exc}"
        ) from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()
    validate_command_plan(args.path)


if __name__ == "__main__":
    main()
