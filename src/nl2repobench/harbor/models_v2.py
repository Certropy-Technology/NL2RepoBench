"""Node/npm Harbor toolchain lock records.

This lock is separate from ``toolchain.lock.toml``. The current development
fixture records a verified Node image digest, but remains development-only until
its private dependency and production-grader artifacts are locked.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from nl2repobench.domain.models_v2 import SEMVER_PATTERN, V2RecordModel

from .models import PINNED_IMAGE, HarborVersionLock


class NodeImageLockV2(V2RecordModel):
    agent_base: str
    verifier_base: str
    platform: Literal["linux/amd64"] = "linux/amd64"
    status: Literal["locked", "development-only"] = "development-only"

    @model_validator(mode="after")
    def validate_image_provenance(self) -> NodeImageLockV2:
        for name, value in {
            "agent_base": self.agent_base,
            "verifier_base": self.verifier_base,
        }.items():
            if self.status == "locked":
                if not re.fullmatch(PINNED_IMAGE, value):
                    raise ValueError(f"{name} must be pinned by sha256 digest")
            elif "@sha256:" in value and not re.fullmatch(PINNED_IMAGE, value):
                raise ValueError(f"{name} has an invalid image digest")
        return self


class NodeRuntimeLockV2(V2RecordModel):
    runtime_version: str = Field(pattern=r"^22\.[0-9]+\.[0-9]+$")
    npm_version: str = Field(pattern=SEMVER_PATTERN)
    libc: Literal["glibc", "musl"]
    executable: str = "/usr/local/bin/node"
    npm_executable: str = "/usr/local/bin/npm"


class NodeHarborToolchainLockV2(V2RecordModel):
    status: Literal["locked", "development-only"] = "development-only"
    harbor: HarborVersionLock
    images: NodeImageLockV2
    runtime: NodeRuntimeLockV2
    python_grader: Literal["absent", "locked"] = "absent"
    node_report_schema: Literal["node-test-json-v1"] = "node-test-json-v1"

    @model_validator(mode="after")
    def validate_toolchain_scope(self) -> NodeHarborToolchainLockV2:
        if self.harbor.task_schema != "1.4":
            raise ValueError("Node Harbor compiler requires task schema 1.4")
        if self.status == "locked" and self.images.status != "locked":
            raise ValueError("locked Node toolchain requires locked images")
        if self.status == "locked" and self.python_grader != "locked":
            raise ValueError("production Node toolchain requires a locked grader")
        return self


def load_node_toolchain_lock(path: Path) -> NodeHarborToolchainLockV2:
    """Load and validate a standalone Node/npm toolchain lock."""

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return NodeHarborToolchainLockV2.model_validate(data)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        raise ValueError(f"invalid Node toolchain lock {path}: {exc}") from exc
