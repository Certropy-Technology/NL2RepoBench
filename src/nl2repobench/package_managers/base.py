"""Typed package-manager boundary for the canonical dependency bundle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from nl2repobench.domain.runtime import RuntimeDiscriminator


class PackageManagerError(ValueError):
    """A package-manager input violates the canonical dependency contract."""

    def __init__(
        self,
        code: str = "store-malformed",
        identity: RuntimeDiscriminator | None = None,
        stage: str = "validate",
        message: str = "",
        details: str = "",
    ) -> None:
        self.code = code
        self.identity = identity
        self.stage = stage
        self.details = details
        super().__init__(message or code)


@dataclass(frozen=True, slots=True)
class ResolvedPackage:
    name: str
    version: str
    kind: str
    artifact_digest: str | None = None


@dataclass(frozen=True, slots=True)
class LockSummary:
    identity: RuntimeDiscriminator
    toolchain_version: str
    lockfile_names: tuple[str, ...]
    lock_digest: str
    resolved: tuple[ResolvedPackage, ...] = ()


@dataclass(frozen=True, slots=True)
class StoreSummary:
    identity: RuntimeDiscriminator
    store_digest: str
    inventory_digest: str
    file_count: int
    total_bytes: int
    offline_smoke: bool


@dataclass(frozen=True, slots=True)
class CommandSpec:
    argv: tuple[str, ...]
    cwd: str
    environment: tuple[tuple[str, str], ...]
    timeout_sec: int

    def __post_init__(self) -> None:
        if not self.argv or any(not item for item in self.argv):
            raise ValueError("command argv must be non-empty")
        if not self.cwd or self.cwd.startswith("/") or ".." in Path(self.cwd).parts:
            raise ValueError("command cwd must be a safe relative path")
        if self.timeout_sec <= 0:
            raise ValueError("command timeout must be positive")


class PackageManagerAdapter(Protocol):
    """Package-manager responsibilities below the runtime adapter."""

    identity: RuntimeDiscriminator
    lockfile_names: tuple[str, ...]

    def validate_lock(self, lock_root: Path, expected_toolchain: str) -> LockSummary: ...

    def validate_offline_store(
        self,
        store_root: Path,
        lock_summary: LockSummary,
        inventory: object,
        expected_toolchain: str,
    ) -> StoreSummary: ...

    def build_commands(self, profile: object) -> tuple[CommandSpec, ...]: ...

    def offline_environment(self, profile: object) -> dict[str, str]: ...


__all__ = [
    "CommandSpec",
    "LockSummary",
    "PackageManagerAdapter",
    "PackageManagerError",
    "ResolvedPackage",
    "StoreSummary",
]
