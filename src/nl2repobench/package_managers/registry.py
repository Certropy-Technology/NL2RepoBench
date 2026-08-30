"""Fail-closed registry for the F0 package-manager protocol."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nl2repobench.domain.runtime import (
    PackageManager,
    RuntimeDiscriminator,
    RuntimeLanguage,
)
from nl2repobench.storage.canonical_ustar import encode_tree

from .base import (
    CommandSpec,
    LockSummary,
    PackageManagerError,
    PackageManagerErrorCode,
    StoreSummary,
    inventory_store_summary,
)
from .go_modules import GoModulesPackageManager
from .pnpm import PnpmPackageManager


class UnknownPackageManagerError(ValueError):
    """Raised when an exact runtime identity has no registered adapter."""


@dataclass(frozen=True, slots=True)
class CanonicalPackageManager:
    identity: RuntimeDiscriminator
    lockfile_names: tuple[str, ...]
    executable: tuple[str, ...]
    environment: tuple[tuple[str, str], ...]
    build_supported: bool = True

    def _error(
        self, code: PackageManagerErrorCode, stage: str, message: str
    ) -> PackageManagerError:
        return PackageManagerError(code, self.identity, stage, message)

    def validate_lock(self, lock_root: Path, expected_toolchain: str) -> LockSummary:
        if lock_root.is_symlink() or not lock_root.is_dir():
            raise self._error(
                PackageManagerErrorCode.LOCK_MISSING,
                "lock",
                "dependency lock root is missing",
            )
        actual = tuple(
            sorted(
                path.name
                for path in lock_root.iterdir()
                if path.is_file() and not path.is_symlink()
            )
        )
        missing = sorted(set(self.lockfile_names) - set(actual))
        if missing:
            raise self._error(
                PackageManagerErrorCode.LOCK_MISSING,
                "lock",
                "dependency lock files are missing: " + ", ".join(missing),
            )
        extras = sorted(set(actual) - set(self.lockfile_names))
        if extras:
            raise self._error(
                PackageManagerErrorCode.LOCK_MALFORMED,
                "lock",
                "dependency lock root contains unexpected files: " + ", ".join(extras),
            )
        if not expected_toolchain.strip():
            raise self._error(
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                "lock",
                "expected package-manager toolchain is empty",
            )
        archive = encode_tree(lock_root)
        return LockSummary(
            identity=self.identity,
            toolchain_version=expected_toolchain,
            lockfile_names=self.lockfile_names,
            lock_digest=f"sha256:{hashlib.sha256(archive).hexdigest()}",
        )

    def validate_offline_store(
        self,
        store_root: Path,
        lock_summary: LockSummary,
        inventory: object,
        expected_toolchain: str,
    ) -> StoreSummary:
        if lock_summary.identity != self.identity:
            raise self._error(
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                "store",
                "lock summary belongs to a different runtime identity",
            )
        if lock_summary.toolchain_version != expected_toolchain:
            raise self._error(
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                "store",
                "lock summary toolchain does not match store toolchain",
            )
        return inventory_store_summary(
            identity=self.identity,
            store_root=store_root,
            inventory=inventory,
        )

    def build_commands(self, profile: object) -> tuple[CommandSpec, ...]:
        del profile
        if not self.build_supported:
            raise self._error(
                PackageManagerErrorCode.UNSUPPORTED_PROFILE,
                "build",
                f"{self.identity.language.value}+"
                f"{self.identity.package_manager.value} cannot build",
            )
        return (CommandSpec(self.executable, ".", self.environment, 600),)

    def offline_environment(self, profile: object) -> dict[str, str]:
        del profile
        return dict(self.environment)


def _identity(language: RuntimeLanguage, manager: PackageManager) -> RuntimeDiscriminator:
    return RuntimeDiscriminator(language=language, package_manager=manager)


@dataclass(frozen=True, slots=True)
class PackageManagerRegistry:
    adapters: dict[RuntimeDiscriminator, Any]

    @classmethod
    def default(cls) -> PackageManagerRegistry:
        python_uv = _identity(RuntimeLanguage.PYTHON, PackageManager.UV)
        python_pip = _identity(RuntimeLanguage.PYTHON, PackageManager.PIP)
        python_none = _identity(RuntimeLanguage.PYTHON, PackageManager.NONE)
        node_npm = _identity(RuntimeLanguage.NODE, PackageManager.NPM)
        node_none = _identity(RuntimeLanguage.NODE, PackageManager.NONE)
        adapters: tuple[Any, ...] = (
            CanonicalPackageManager(
                python_uv,
                ("requirements.lock.txt",),
                ("/usr/local/bin/uv", "pip", "install", "--offline", "--require-hashes"),
                (("UV_OFFLINE", "1"),),
            ),
            CanonicalPackageManager(
                python_pip,
                ("requirements.lock.txt",),
                ("/usr/local/bin/python", "-m", "pip", "install", "--require-hashes"),
                (("PIP_NO_INDEX", "1"),),
            ),
            CanonicalPackageManager(python_none, (), ("/usr/bin/true",), (), True),
            CanonicalPackageManager(
                node_npm,
                ("package-lock.json",),
                ("/usr/local/bin/npm", "ci", "--offline", "--ignore-scripts"),
                (("npm_config_offline", "true"), ("npm_config_ignore_scripts", "true")),
            ),
            PnpmPackageManager(),
            CanonicalPackageManager(node_none, (), (), (), False),
            GoModulesPackageManager(),
        )
        return cls({adapter.identity: adapter for adapter in adapters})

    def resolve(self, identity: RuntimeDiscriminator) -> Any:
        if not isinstance(identity, RuntimeDiscriminator):
            raise UnknownPackageManagerError(
                "package-manager resolution requires a validated RuntimeDiscriminator"
            )
        try:
            return self.adapters[identity]
        except KeyError as exc:
            available = ", ".join(
                sorted(
                    f"{item.language.value}+{item.package_manager.value}"
                    for item in self.adapters
                )
            )
            requested = f"{identity.language.value}+{identity.package_manager.value}"
            raise UnknownPackageManagerError(
                f"no package-manager adapter for {requested}; registered: {available}"
            ) from exc


__all__ = [
    "CanonicalPackageManager",
    "PackageManagerRegistry",
    "UnknownPackageManagerError",
]
