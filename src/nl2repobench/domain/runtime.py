"""Neutral runtime selection for the canonical task contract."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

if TYPE_CHECKING:
    from .canonical_contract import TaskSource


class RuntimeContractError(ValueError):
    """Raised when a catalog source cannot provide an explicit runtime choice."""


class RuntimeLanguage(StrEnum):
    """Languages supported by the current runtime adapter boundary."""

    PYTHON = "python"
    NODE = "node"
    GO = "go"


class PackageManager(StrEnum):
    """Package managers understood by the current runtime discriminator."""

    UV = "uv"
    PIP = "pip"
    NPM = "npm"
    PNPM = "pnpm"
    GO_MODULES = "go-modules"
    NONE = "none"


class RuntimeProfile(BaseModel):
    """Exact runtime identity shared by source and generated manifests."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    language: RuntimeLanguage
    runtime: str
    version: str
    package_manager: PackageManager
    package_manager_version: str | None = None

    @model_validator(mode="after")
    def validate_profile(self) -> Self:
        expected = {
            RuntimeLanguage.PYTHON: "cpython",
            RuntimeLanguage.NODE: "node",
            RuntimeLanguage.GO: "go",
        }[self.language]
        if self.runtime != expected:
            raise ValueError(f"{self.language.value} requires runtime {expected}")
        if not self.version.strip():
            raise ValueError("runtime version must be exact and non-empty")
        if self.package_manager is PackageManager.NONE and self.package_manager_version is not None:
            raise ValueError("none package manager cannot have a version")
        if (
            self.package_manager is not PackageManager.NONE
            and not (self.package_manager_version or "").strip()
        ):
            raise ValueError("package manager version is required")
        return self


class RuntimeDiscriminator(BaseModel):
    """Explicit language and package-manager identity for one task.

    ``schema_version`` is deliberately absent: record shape and runtime
    selection are independent concerns. Python accepts ``uv``, ``pip`` or
    ``none``; Node accepts ``npm``, ``pnpm`` or ``none``. Any other pairing is
    rejected so a caller cannot silently route a task to the wrong adapter.

    Runtime selection is derived only from the typed canonical runtime profile.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    language: RuntimeLanguage
    package_manager: PackageManager

    @model_validator(mode="after")
    def validate_package_manager(self) -> Self:
        allowed: dict[RuntimeLanguage, frozenset[PackageManager]] = {
            RuntimeLanguage.PYTHON: frozenset(
                {PackageManager.UV, PackageManager.PIP, PackageManager.NONE}
            ),
            RuntimeLanguage.NODE: frozenset(
                {PackageManager.NPM, PackageManager.PNPM, PackageManager.NONE}
            ),
            RuntimeLanguage.GO: frozenset({PackageManager.GO_MODULES}),
        }
        if self.package_manager not in allowed[self.language]:
            accepted = ", ".join(
                manager.value
                for manager in sorted(allowed[self.language], key=lambda item: item.value)
            )
            raise ValueError(
                f"{self.language.value} runtime cannot use {self.package_manager.value}; "
                f"accepted package managers: {accepted}"
            )
        return self

    @classmethod
    def from_task_source(cls, source: TaskSource) -> Self:
        """Build a discriminator from one validated canonical source."""

        runtime = source.environment.runtime
        if runtime is None:
            raise RuntimeContractError(
                "environment.runtime is required for runtime dispatch"
            )
        try:
            return cls(
                language=RuntimeLanguage(runtime.language.value),
                package_manager=PackageManager(runtime.package_manager.value),
            )
        except (ValidationError, ValueError) as exc:
            raise RuntimeContractError(f"invalid runtime discriminator: {exc}") from exc
