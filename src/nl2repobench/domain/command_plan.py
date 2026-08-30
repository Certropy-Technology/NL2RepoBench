"""Canonical verifier command plans shared by every runtime adapter."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import Field, field_validator

from .canonical_models import CanonicalRecord


class CommandStep(CanonicalRecord):
    """One bounded, argv-based verifier step."""

    step_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    argv: tuple[str, ...] = Field(min_length=1)
    cwd: str = "."
    environment: dict[str, str] = Field(default_factory=dict)
    timeout_sec: int = Field(gt=0, le=600)

    @field_validator("cwd")
    @classmethod
    def validate_cwd(cls, value: str) -> str:
        parts = value.split("/")
        if not value or value.startswith("/") or ".." in parts or "" in parts:
            raise ValueError("command step cwd must be a safe relative path")
        return value

    @field_validator("argv")
    @classmethod
    def validate_argv(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item or "\x00" in item for item in value):
            raise ValueError("command step argv entries must be non-empty")
        return value

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: dict[str, str]) -> dict[str, str]:
        forbidden = {"PATH", "LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH", "NODE_PATH"}
        if any(
            name in forbidden or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name)
            for name in value
        ):
            raise ValueError("command step environment contains a forbidden name")
        return value


class CommandPlan(CanonicalRecord):
    """The single command-plan shape consumed by Python, Node, and Go."""

    identity: str = Field(pattern=r"^[a-z][a-z0-9-]*\+[a-z][a-z0-9-]*$")
    runner: str = Field(min_length=1)
    candidate_install: str = Field(min_length=1)
    report_format: Literal[
        "pytest-junit-xml-v1", "node-test-json-v1", "go-test-json-v1", "custom-json-v1"
    ]
    test_root: Literal["/tests/private"] = "/tests/private"
    steps: tuple[CommandStep, ...] = ()


__all__ = ["CommandPlan", "CommandStep"]
