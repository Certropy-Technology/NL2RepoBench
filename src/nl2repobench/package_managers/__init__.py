"""Explicit package-manager adapters with lazy optional imports."""

from typing import Any

from .base import (
    CommandSpec,
    LockSummary,
    PackageManagerAdapter,
    PackageManagerError,
    PackageManagerErrorCode,
    ResolvedPackage,
    StoreSummary,
)

__all__ = [
    "CommandSpec",
    "LockSummary",
    "PackageManagerAdapter",
    "PackageManagerError",
    "PackageManagerErrorCode",
    "PackageManagerRegistry",
    "GoModulesPackageManager",
    "PnpmPackageManager",
    "MavenPackageManager",
    "ResolvedPackage",
    "StoreSummary",
    "UnknownPackageManagerError",
]


def __getattr__(name: str) -> Any:
    if name == "GoModulesPackageManager":
        from .go_modules import GoModulesPackageManager

        return GoModulesPackageManager
    if name == "PnpmPackageManager":
        from .pnpm import PnpmPackageManager

        return PnpmPackageManager
    if name == "MavenPackageManager":
        from .maven import MavenPackageManager

        return MavenPackageManager
    if name in {"PackageManagerRegistry", "UnknownPackageManagerError"}:
        from .registry import PackageManagerRegistry, UnknownPackageManagerError

        return {
            "PackageManagerRegistry": PackageManagerRegistry,
            "UnknownPackageManagerError": UnknownPackageManagerError,
        }[name]
    raise AttributeError(name)
