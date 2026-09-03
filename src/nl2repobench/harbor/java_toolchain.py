"""Strict, probe-backed Java/Maven development toolchain identity."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

_MAVEN = re.compile(r"^3\.9\.[0-9]+$")
_JDK = re.compile(r"^temurin-21\.0\.[0-9]+\+[0-9]+$")


class JavaToolchainLock(BaseModel):
    """Observed Java runtime tuple; not a claim of production readiness."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal["1.0"]
    release_id: str
    status: Literal["observed-not-production", "locked"]
    jdk_version: str
    maven_version: str
    expected_platform: Literal["linux/amd64"]
    expected_jdk_base: str
    jdk_base_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    expected_maven_base: str
    maven_base_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    runtime_image: str
    runtime_image_id: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    runtime_build_ref: str
    java_executable: Literal["/opt/java/openjdk/bin/java"]
    javac_executable: Literal["/opt/java/openjdk/bin/javac"]
    maven_executable: Literal["/opt/maven/bin/mvn"]
    agent_runtime_image: str
    agent_runtime_image_id: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    agent_runtime_build_ref: str
    harbor_version: Literal["0.21.0"]
    task_schema: Literal["1.4"]
    harbor_lock: str
    harbor_lock_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    verifier_requirements_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    verifier_requirements_lock: str = "verifier/requirements.lock.txt"
    java_runtime_sha256: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    private_artifacts_status: Literal["unavailable", "available"]
    agent_image_status: Literal["not-java-bound", "java-bound"]

    @model_validator(mode="after")
    def validate_identity(self) -> JavaToolchainLock:
        if not _JDK.fullmatch(self.jdk_version):
            raise ValueError("Java toolchain requires the exact Temurin JDK 21 build")
        if not _MAVEN.fullmatch(self.maven_version):
            raise ValueError("Java toolchain requires an exact Maven 3.9.x version")
        if self.expected_jdk_base.rsplit("@", 1)[-1] != self.jdk_base_digest:
            raise ValueError("JDK base image digest does not match")
        if self.expected_maven_base.rsplit("@", 1)[-1] != self.maven_base_digest:
            raise ValueError("Maven base image digest does not match")
        for name, image in {
            "runtime_image": self.runtime_image,
            "agent_runtime_image": self.agent_runtime_image,
        }.items():
            if "@sha256:" not in image:
                raise ValueError(f"{name} must be digest pinned")
        if "@sha256:" in self.runtime_build_ref:
            if self.runtime_build_ref.rsplit("@", 1)[1] != self.runtime_image_id:
                raise ValueError("runtime build ref digest does not match runtime image id")
        elif not re.fullmatch(r"[a-z0-9][a-z0-9._/-]*:[A-Za-z0-9._-]+", self.runtime_build_ref):
            raise ValueError(
                "runtime_build_ref must be a valid local image tag or digest reference"
            )
        if "@sha256:" in self.agent_runtime_build_ref:
            if self.agent_runtime_build_ref.rsplit("@", 1)[1] != self.agent_runtime_image_id:
                raise ValueError("agent runtime build ref digest does not match image id")
        elif not re.fullmatch(
            r"[a-z0-9][a-z0-9._/-]*:[A-Za-z0-9._-]+", self.agent_runtime_build_ref
        ):
            raise ValueError(
                "agent_runtime_build_ref must be a valid local image tag or digest reference"
            )
        if self.status == "locked" and self.runtime_build_ref != self.runtime_image:
            raise ValueError("locked Java toolchain runtime_build_ref must be digest pinned")
        if self.status == "locked" and self.agent_runtime_build_ref != self.agent_runtime_image:
            raise ValueError("locked Java toolchain agent_runtime_build_ref must be digest pinned")
        return self

    @property
    def production_ready(self) -> bool:
        return (
            self.status == "locked"
            and self.private_artifacts_status == "available"
            and self.agent_image_status == "java-bound"
        )

    @property
    def runtime_base_ref(self) -> str:
        """Return the immutable production ref or the explicit dev ref."""

        return self.runtime_image if self.status == "locked" else self.runtime_build_ref

    @property
    def agent_runtime_base_ref(self) -> str:
        """Return the immutable production ref or the explicit dev ref."""

        return (
            self.agent_runtime_image
            if self.status == "locked"
            else self.agent_runtime_build_ref
        )


def load_java_toolchain_lock(path: Path) -> JavaToolchainLock:
    """Load one regular, bounded Java toolchain lock without external access."""

    if path.is_symlink() or not path.is_file():
        raise ValueError("Java toolchain lock must be a regular file")
    if path.stat().st_size > 64 * 1024:
        raise ValueError("Java toolchain lock exceeds the size limit")
    try:
        return JavaToolchainLock.model_validate(tomllib.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        raise ValueError(f"invalid Java toolchain lock: {exc}") from exc


__all__ = ["JavaToolchainLock", "load_java_toolchain_lock"]
