"""Node Harbor toolchain lock records for the canonical runtime."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from nl2repobench.domain.canonical_models import CanonicalRecord as RecordModel

from .models import PINNED_IMAGE, AgentRuntimeImageLock, HarborVersionLock

SEMVER_PATTERN = r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$"


class NodeImageLock(RecordModel):
    agent_base: str
    verifier_base: str
    verifier_python_base: str = (
        "python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a"
    )
    platform: Literal["linux/amd64"] = "linux/amd64"
    status: Literal["locked", "development-only"] = "development-only"

    @model_validator(mode="after")
    def validate_image_provenance(self) -> NodeImageLock:
        for name, value in {
            "agent_base": self.agent_base,
            "verifier_base": self.verifier_base,
            "verifier_python_base": self.verifier_python_base,
        }.items():
            if self.status == "locked":
                if not re.fullmatch(PINNED_IMAGE, value):
                    raise ValueError(f"{name} must be pinned by sha256 digest")
            elif "@sha256:" in value and not re.fullmatch(PINNED_IMAGE, value):
                raise ValueError(f"{name} has an invalid image digest")
        return self


class NodeRuntimeLock(RecordModel):
    runtime_version: str = Field(pattern=r"^(?:22|24)\.[0-9]+\.[0-9]+$")
    npm_version: str = Field(pattern=SEMVER_PATTERN)
    pnpm_version: str | None = Field(default=None, pattern=SEMVER_PATTERN)
    libc: Literal["glibc", "musl"]
    executable: str = "/usr/local/bin/node"
    npm_executable: str = "/usr/local/bin/npm"


class NodeHarborToolchainLock(RecordModel):
    status: Literal["locked", "development-only"] = "development-only"
    harbor: HarborVersionLock
    images: NodeImageLock
    agent_runtime: AgentRuntimeImageLock
    runtime: NodeRuntimeLock
    node_grader: Literal["absent", "locked"] = "absent"
    node_runtime_sha256: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    verifier_requirements_lock: str = "verifier/requirements.lock.txt"
    verifier_requirements_sha256: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    node_report_schema: Literal["node-test-json-v1"] = "node-test-json-v1"

    @model_validator(mode="after")
    def validate_toolchain_scope(self) -> NodeHarborToolchainLock:
        if self.harbor.task_schema != "1.4":
            raise ValueError("Node Harbor compiler requires task schema 1.4")
        if self.status == "locked" and self.images.status != "locked":
            raise ValueError("locked Node toolchain requires locked images")
        if self.status == "locked" and self.node_grader != "locked":
            raise ValueError("production Node toolchain requires a locked Node grader")
        if self.status == "locked" and self.node_runtime_sha256 is None:
            raise ValueError("production Node toolchain requires a Node runtime hash")
        if self.status == "locked" and self.verifier_requirements_sha256 is None:
            raise ValueError("production Node toolchain requires verifier requirements hash")
        return self


def load_node_toolchain_lock(path: Path) -> NodeHarborToolchainLock:
    """Load and validate the standalone canonical Node toolchain lock."""

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return NodeHarborToolchainLock.model_validate(data)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        raise ValueError(f"invalid Node toolchain lock {path}: {exc}") from exc


__all__ = ["NodeHarborToolchainLock", "load_node_toolchain_lock"]
