"""Explicit package-manager adapters with lazy optional imports."""

from typing import Any

from .base import PackageManagerAdapter, PackageManagerError

__all__ = [
    "PackageManagerAdapter",
    "PackageManagerError",
    "PackageManagerRegistry",
    "GoModulesPackageManager",
    "PnpmLockSummary",
    "PnpmPackageManager",
    "UnknownPackageManagerError",
]


def __getattr__(name: str) -> Any:
    if name == "GoModulesPackageManager":
        from .go_modules import GoModulesPackageManager

        return GoModulesPackageManager
    if name == "PnpmPackageManager":
        from .pnpm import PnpmPackageManager

        return PnpmPackageManager
    if name == "PnpmLockSummary":
        from .pnpm import PnpmLockSummary

        return PnpmLockSummary
    if name in {"PackageManagerRegistry", "UnknownPackageManagerError"}:
        from .registry import PackageManagerRegistry, UnknownPackageManagerError

        return {
            "PackageManagerRegistry": PackageManagerRegistry,
            "UnknownPackageManagerError": UnknownPackageManagerError,
        }[name]
    raise AttributeError(name)
