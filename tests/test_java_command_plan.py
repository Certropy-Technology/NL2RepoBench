from __future__ import annotations

import json
from pathlib import Path

import pytest

from nl2repobench.package_managers.base import CommandSpec
from nl2repobench.verification.java_command_plan import (
    JavaMavenBuildProfile,
    expected_java_command_plan,
    java_maven_command,
    load_java_command_plan,
    validate_java_command_plan,
    validate_java_maven_command,
)


def test_java_command_plan_is_exact_and_canonical(tmp_path: Path) -> None:
    plan = expected_java_command_plan()
    data = (
        json.dumps(plan.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        .encode()
        + b"\n"
    )
    assert load_java_command_plan(data) == plan
    path = tmp_path / "command-plan.json"
    path.write_bytes(data)
    validate_java_command_plan(path)

    modified = dict(plan.model_dump(mode="json"))
    modified["runner"] = "candidate-controlled"
    with pytest.raises(ValueError, match="allowlisted"):
        load_java_command_plan(
            json.dumps(modified, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        )


def test_java_maven_command_has_fixed_verifier_argv() -> None:
    profile = JavaMavenBuildProfile(
        jdk_version="temurin-21.0.5+11",
        maven_version="3.9.9",
        release=21,
    )
    command = java_maven_command(profile)
    assert validate_java_maven_command(command) == command
    assert command.environment == (
        (
            "MAVEN_ARGS",
            "--offline --batch-mode --no-transfer-progress --strict-checksums",
        ),
        ("MAVEN_OPTS", "-Djava.awt.headless=true"),
    )
    with pytest.raises(ValueError, match="harness"):
        validate_java_maven_command(
            CommandSpec(
                argv=command.argv[:-1] + ("compile",),
                cwd=command.cwd,
                environment=command.environment,
                timeout_sec=command.timeout_sec,
            )
        )


def test_java_command_plan_rejects_setup_steps() -> None:
    payload = expected_java_command_plan().model_dump(mode="json")
    payload["steps"] = [
        {
            "step_id": "candidate",
            "argv": ["sh", "-c", "echo unsafe"],
            "cwd": ".",
            "environment": {},
            "timeout_sec": 1,
        }
    ]
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    with pytest.raises(ValueError, match="setup steps"):
        load_java_command_plan(data)
