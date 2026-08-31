"""Typed, verifier-owned command plan for the Java/Maven adapter."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.command_plan import MAX_COMMAND_PLAN_BYTES, CommandPlan
from nl2repobench.package_managers.base import CommandSpec
from nl2repobench.verification.command_plan import CommandPlanValidationError

JAVA_MAVEN_IDENTITY: str = "java+maven"
JAVA_RUNNER: str = "junit-open-test-subprocess-boundary-v1"
JAVA_CANDIDATE_INSTALL: str = "maven-source-compile-offline-v1"
JAVA_REPORT_FORMAT: Literal["junit-open-test-report-xml-v1"] = (
    "junit-open-test-report-xml-v1"
)
JAVA_TEST_ROOT: str = "/tests/private"
MAVEN_EXECUTABLE = "/opt/maven/bin/mvn"
MAVEN_REPOSITORY = "/opt/maven/repository"
MAVEN_HARNESS_POM = "/tests/private/harness/pom.xml"
JAVA_MAVEN_TIMEOUT_SECONDS = 600
_JDK_VERSION = re.compile(
    r"^[A-Za-z][A-Za-z0-9._-]*-21\.0\.[0-9]+\+[0-9]+(?:\.[0-9]+)?$"
)
_MAVEN_VERSION = re.compile(r"^3\.9\.[0-9]+$")


@dataclass(frozen=True, slots=True)
class JavaMavenBuildProfile:
    """The fixed inputs needed to render a Java verifier build command."""

    jdk_version: str
    maven_version: str
    release: Literal[8, 11, 17, 21] = 21

    def __post_init__(self) -> None:
        if not _JDK_VERSION.fullmatch(self.jdk_version):
            raise ValueError("Java build profile requires an exact JDK 21 identity")
        if not _MAVEN_VERSION.fullmatch(self.maven_version):
            raise ValueError("Java build profile requires an exact Maven 3.9.x version")


EXPECTED_JAVA_PLAN: dict[str, Any] = CommandPlan(
    identity=JAVA_MAVEN_IDENTITY,
    runner=JAVA_RUNNER,
    candidate_install=JAVA_CANDIDATE_INSTALL,
    report_format=JAVA_REPORT_FORMAT,
).model_dump(mode="json")


def expected_java_command_plan() -> CommandPlan:
    return CommandPlan.model_validate(EXPECTED_JAVA_PLAN)


def _validate_java_plan_semantics(payload: object) -> CommandPlan:
    if not isinstance(payload, dict):
        raise ValueError("Java command plan does not match the allowlisted verifier protocol")
    try:
        plan = CommandPlan.model_validate(payload)
    except ValueError as exc:
        raise ValueError(
            "Java command plan does not match the allowlisted verifier protocol; "
            f"canonical validation failed: {exc}"
        ) from exc
    expected = expected_java_command_plan()
    for field in (
        "schema_version",
        "identity",
        "runner",
        "candidate_install",
        "report_format",
        "test_root",
    ):
        if getattr(plan, field) != getattr(expected, field):
            raise ValueError("Java command plan does not match the allowlisted verifier protocol")
    if plan.steps:
        raise CommandPlanValidationError(
            "Java command plan setup steps are not supported without the candidate supervisor",
            stage="setup-not-supported",
        )
    return plan


def load_java_command_plan(data: bytes) -> CommandPlan:
    """Validate bounded canonical bytes from a private Java command artifact."""

    if len(data) > MAX_COMMAND_PLAN_BYTES:
        raise ValueError("Java command plan exceeds the size limit")
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Java command plan JSON: {exc}") from exc
    plan = _validate_java_plan_semantics(payload)
    if data != canonical_json(plan) + b"\n":
        raise ValueError("Java command plan JSON is not canonical")
    return plan


def validate_java_command_plan(path: Path) -> None:
    """Validate a bounded regular file against the exact Java allowlist."""

    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_COMMAND_PLAN_BYTES:
            raise ValueError("Java command plan must be a bounded regular file")
        data = os.read(descriptor, MAX_COMMAND_PLAN_BYTES + 1)
    finally:
        os.close(descriptor)
    load_java_command_plan(data)


def java_maven_environment() -> tuple[tuple[str, str], ...]:
    """Return the exact environment owned by the Java verifier command."""

    return (
        (
            "MAVEN_ARGS",
            "--offline --batch-mode --no-transfer-progress --strict-checksums",
        ),
        ("MAVEN_OPTS", "-Djava.awt.headless=true"),
    )


def java_maven_command(profile: JavaMavenBuildProfile) -> CommandSpec:
    """Render the fixed offline harness command without candidate interpolation."""

    if not isinstance(profile, JavaMavenBuildProfile):
        raise TypeError("Java Maven build commands require JavaMavenBuildProfile")
    return CommandSpec(
        argv=(
            MAVEN_EXECUTABLE,
            "--offline",
            "--batch-mode",
            "--no-transfer-progress",
            "--strict-checksums",
            f"-Dmaven.repo.local={MAVEN_REPOSITORY}",
            f"-Dmaven.compiler.release={profile.release}",
            "--file",
            MAVEN_HARNESS_POM,
            "test",
        ),
        cwd=".",
        environment=java_maven_environment(),
        timeout_sec=JAVA_MAVEN_TIMEOUT_SECONDS,
    )


def validate_java_maven_command(command: CommandSpec) -> CommandSpec:
    """Reject any command that is not the verifier-owned Maven invocation."""

    if not isinstance(command, CommandSpec):
        raise ValueError("Java Maven command must be a CommandSpec")
    if command.cwd != "." or command.timeout_sec != JAVA_MAVEN_TIMEOUT_SECONDS:
        raise ValueError("Java Maven command has an invalid cwd or timeout")
    if command.environment != java_maven_environment():
        raise ValueError("Java Maven command environment is not verifier-owned")
    prefix = (
        MAVEN_EXECUTABLE,
        "--offline",
        "--batch-mode",
        "--no-transfer-progress",
        "--strict-checksums",
    )
    if len(command.argv) != 10 or command.argv[:5] != prefix:
        raise ValueError("Java Maven command argv is not verifier-owned")
    if command.argv[5] != f"-Dmaven.repo.local={MAVEN_REPOSITORY}":
        raise ValueError("Java Maven command repository is not verifier-owned")
    if not re.fullmatch(r"-Dmaven\.compiler\.release=(?:8|11|17|21)", command.argv[6]):
        raise ValueError("Java Maven command release is invalid")
    if command.argv[7:] != ("--file", MAVEN_HARNESS_POM, "test"):
        raise ValueError("Java Maven command harness is not verifier-owned")
    return command


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()
    validate_java_command_plan(args.path)


if __name__ == "__main__":
    main()


__all__ = [
    "EXPECTED_JAVA_PLAN",
    "JAVA_CANDIDATE_INSTALL",
    "JAVA_MAVEN_IDENTITY",
    "JAVA_REPORT_FORMAT",
    "JAVA_RUNNER",
    "JAVA_TEST_ROOT",
    "JavaMavenBuildProfile",
    "expected_java_command_plan",
    "java_maven_command",
    "java_maven_environment",
    "load_java_command_plan",
    "validate_java_command_plan",
    "validate_java_maven_command",
]
