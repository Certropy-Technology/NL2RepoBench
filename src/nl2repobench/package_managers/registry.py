"""Fail-closed package-manager adapter registry."""

from __future__ import annotations

from dataclasses import dataclass

from .base import PackageManagerAdapter
from .go_modules import GoModulesPackageManager
from .pnpm import PnpmPackageManager


class UnknownPackageManagerError(ValueError):
    """Raised when a package manager has no registered adapter."""


@dataclass(frozen=True)
class PackageManagerRegistry:
    adapters: dict[str, PackageManagerAdapter]

    @classmethod
    def default(cls) -> PackageManagerRegistry:
        return cls(
            adapters={
                "go-modules": GoModulesPackageManager(),
                "pnpm": PnpmPackageManager(),
            }
        )

    def resolve(self, identity: str) -> PackageManagerAdapter:
        try:
            return self.adapters[identity]
        except KeyError as exc:
            available = ", ".join(sorted(self.adapters))
            raise UnknownPackageManagerError(
                f"no package-manager adapter for {identity}; registered: {available}"
            ) from exc
