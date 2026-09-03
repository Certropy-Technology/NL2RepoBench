"""Neutral runtime selection for the unified task contract.

The catalog compiler must choose a runtime adapter from an explicit task
identity, not from the shape version of a record. This module owns the small
shared discriminator used for that decision. Runtime-specific models may
still carry additional lock, installer, and report fields while migration is
in progress, but they must not redefine this language/package-manager pair.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator


class RuntimeContractError(ValueError):
    """Raised when a catalog source cannot provide an explicit runtime choice."""


class RuntimeLanguage(StrEnum):
    """Languages supported by the current runtime adapter boundary."""

    PYTHON = "python"
    NODE = "node"
    GO = "go"
    JAVA = "java"


class PackageManager(StrEnum):
    """Package managers understood by the current runtime discriminator."""

    UV = "uv"
    PIP = "pip"
    NPM = "npm"
    PNPM = "pnpm"
    GO_MODULES = "go-modules"
    MAVEN = "maven"
    NONE = "none"


class RuntimeDiscriminator(BaseModel):
    """Explicit language and package-manager identity for one task.

    ``schema_version`` is deliberately absent: record shape and runtime
    selection are independent concerns. Python accepts ``uv``, ``pip`` or
    ``none``; Node accepts ``npm``, ``pnpm`` or ``none``. Any other pairing is
    rejected so a caller cannot silently route a task to the wrong adapter.

    ``from_catalog_source`` reads the current human-facing source locations:
    Python sources declare their installer in ``dependencies.installer``;
    Node sources declare their language and package manager in
    ``environment.runtime``. This is an explicit transitional mapping, not a
    fallback parser. The canonical ``environment_lock.runtime`` field remains
    a later migration step documented by the caller.
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
            RuntimeLanguage.JAVA: frozenset({PackageManager.MAVEN}),
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
    def from_catalog_source(cls, source: Mapping[str, object]) -> Self:
        """Build a discriminator from the current explicit catalog fields.

        The language field is required and determines which package-manager
        field is required. Missing objects, missing fields, unknown values,
        and contradictory Node language declarations all fail closed with
        :class:`RuntimeContractError`.
        """

        metadata = _required_mapping(source, "metadata")
        language = metadata.get("language")
        if language == RuntimeLanguage.PYTHON.value:
            dependencies = _required_mapping(source, "dependencies")
            package_manager = dependencies.get("installer")
        elif language == RuntimeLanguage.NODE.value:
            environment = _required_mapping(source, "environment")
            runtime = _required_mapping(environment, "runtime")
            if runtime.get("language") != language:
                raise RuntimeContractError(
                    "environment.runtime.language must explicitly match metadata.language"
                )
            package_manager = runtime.get("package_manager")
        elif language == RuntimeLanguage.GO.value:
            package_manager = PackageManager.GO_MODULES.value
        elif language == RuntimeLanguage.JAVA.value:
            dependencies = _required_mapping(source, "dependencies")
            package_manager = dependencies.get("installer")
        else:
            raise RuntimeContractError(
                "metadata.language must explicitly be one of: python, node, go, java"
            )

        if not isinstance(package_manager, str) or not package_manager:
            location = "dependencies.installer"
            raise RuntimeContractError(f"{location} is required for runtime dispatch")

        try:
            return cls(
                language=RuntimeLanguage(language),
                package_manager=PackageManager(package_manager),
            )
        except (ValidationError, ValueError) as exc:
            raise RuntimeContractError(f"invalid runtime discriminator: {exc}") from exc


def _required_mapping(source: Mapping[str, object], field_name: str) -> Mapping[str, object]:
    """Return a required object field without accepting alternate spellings."""

    value = source.get(field_name)
    if not isinstance(value, Mapping):
        raise RuntimeContractError(f"{field_name} must be an explicit object")
    return value
