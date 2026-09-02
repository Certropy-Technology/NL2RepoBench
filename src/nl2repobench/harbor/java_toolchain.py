"""Strict, probe-backed Java/Maven development toolchain identity."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_MAVEN = re.compile(r"^3\.9\.[0-9]+$")
_JDK = re.compile(r"^temurin-21\.0\.[0-9]+\+[0-9]+$")


class JavaToolchainLock(BaseModel):
    """The host-independent Java runtime tuple established by the local probe.

    ``observed-not-production`` is intentional: this lock records exact runtime
    bytes without claiming that the Java agent image or private task artifacts
    have passed their production gates.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal["1.0"]
    release_id: Literal["java-temurin-21.0.12-maven-3.9.11-v1"]
    status: Literal["observed-not-production"]
    jdk_version: str
    maven_version: str
    expected_platform: Literal["linux/amd64"]
    expected_jdk_base: str
    jdk_base_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    expected_maven_base: str
    maven_base_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    runtime_image: str
    runtime_image_id: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    java_executable: Literal["/opt/java/openjdk/bin/java"] = "/opt/java/openjdk/bin/java"
    javac_executable: Literal["/opt/java/openjdk/bin/javac"] = "/opt/java/openjdk/bin/javac"
    maven_executable: Literal["/opt/maven/bin/mvn"] = "/opt/maven/bin/mvn"
    agent_runtime_image: str
    agent_runtime_image_id: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    harbor_version: Literal["0.21.0"]
    task_schema: Literal["1.4"]
    harbor_lock: Literal["harbor-runner/uv.lock"]
    harbor_lock_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    java_command_plan_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    java_bridge_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    junit_normalizer_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    verifier_requirements_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    private_artifacts_status: Literal["unavailable"]
    agent_image_status: Literal["not-java-bound"]

    @model_validator(mode="after")
    def validate_identity(self) -> JavaToolchainLock:
        if not _JDK.fullmatch(self.jdk_version):
            raise ValueError("Java toolchain requires the exact Temurin JDK 21 build")
        if not _MAVEN.fullmatch(self.maven_version):
            raise ValueError("Java toolchain requires an exact Maven 3.9.x version")
        if "@sha256:" not in self.expected_jdk_base:
            raise ValueError("JDK base image must be digest pinned")
        if self.expected_jdk_base.rsplit("@", 1)[1] != self.jdk_base_digest:
            raise ValueError("JDK base image digest does not match")
        if "@sha256:" not in self.expected_maven_base:
            raise ValueError("Maven base image must be digest pinned")
        if self.expected_maven_base.rsplit("@", 1)[1] != self.maven_base_digest:
            raise ValueError("Maven base image digest does not match")
        return self

    @property
    def production_ready(self) -> bool:
        return False


def load_java_toolchain_lock(path: Path) -> JavaToolchainLock:
    """Load a regular, bounded Java lock without network or Docker access."""

    if path.is_symlink() or not path.is_file():
        raise ValueError("Java toolchain lock must be a regular file")
    if path.stat().st_size > 64 * 1024:
        raise ValueError("Java toolchain lock exceeds the size limit")
    try:
        return JavaToolchainLock.model_validate(
            tomllib.loads(path.read_text(encoding="utf-8"))
        )
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        raise ValueError(f"invalid Java toolchain lock: {exc}") from exc


__all__ = ["JavaToolchainLock", "load_java_toolchain_lock"]
