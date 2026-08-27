"""Machine-readable toolchain lock used by the Harbor compiler."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from nl2repobench.domain.models import RecordModel

PINNED_IMAGE = r"^[A-Za-z0-9._/-]+@sha256:[0-9a-f]{64}$"
LOCAL_IMAGE_TAG = r"^[a-z0-9][a-z0-9._/-]*:[A-Za-z0-9._-]+$"


class HarborVersionLock(RecordModel):
    version: str
    task_schema: str
    runner: str
    lock_file: str
    lock_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class ImageLock(RecordModel):
    agent_base: str
    verifier_base: str
    platform: Literal["linux/amd64"] = "linux/amd64"

    @model_validator(mode="after")
    def validate_pinned_images(self) -> ImageLock:
        for name, value in {
            "agent_base": self.agent_base,
            "verifier_base": self.verifier_base,
        }.items():
            if not re.fullmatch(PINNED_IMAGE, value):
                raise ValueError(f"{name} must be pinned by sha256 digest")
        return self


class AgentRuntimeImageLock(RecordModel):
    """Prebuilt OpenHands runtime shared by every Agent environment."""

    image: str
    image_id: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    fork_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    python_executable: Literal["/opt/openhands-sdk-venv/bin/python"] = (
        "/opt/openhands-sdk-venv/bin/python"
    )
    sdk_version: str
    tools_version: str
    litellm_version: str

    @model_validator(mode="after")
    def validate_image_identity(self) -> AgentRuntimeImageLock:
        if not (
            re.fullmatch(PINNED_IMAGE, self.image)
            or re.fullmatch(LOCAL_IMAGE_TAG, self.image)
        ):
            raise ValueError("image must be an immutable digest reference or local tag")
        if re.fullmatch(PINNED_IMAGE, self.image):
            image_digest = self.image.rsplit("@", 1)[1]
            if image_digest != self.image_id:
                raise ValueError("image digest must match image_id")
        return self


class VerifierRuntimeLock(RecordModel):
    requirements_lock: str
    requirements_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    pytest_version: str
    pydantic_version: str
    defusedxml_version: str


class AuthoringRuntimeLock(RecordModel):
    uv_version: str
    python: str


class HarborToolchainLock(RecordModel):
    harbor: HarborVersionLock
    images: ImageLock
    agent_runtime: AgentRuntimeImageLock
    verifier: VerifierRuntimeLock
    authoring: AuthoringRuntimeLock


class VerifierCommandPlan(RecordModel):
    """Allowlisted verifier behavior; arbitrary shell commands are not executed."""

    runner: Literal["pytest-subprocess-boundary-v1"]
    candidate_install: Literal["pip-target-no-deps-v1"]
    test_root: Literal["/tests/private"] = "/tests/private"


def load_command_plan(data: bytes) -> VerifierCommandPlan:
    try:
        return VerifierCommandPlan.model_validate(json.loads(data))
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"invalid verifier command plan: {exc}") from exc


def load_toolchain_lock(path: Path) -> HarborToolchainLock:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return HarborToolchainLock.model_validate(data)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        raise ValueError(f"invalid toolchain lock {path}: {exc}") from exc
