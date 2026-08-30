"""Fail-closed package-manager adapter registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nl2repobench.domain.runtime import RuntimeDiscriminator

from .base import CommandSpec, LockSummary, StoreSummary
from .go_modules import GoModulesPackageManager
from .pnpm import PnpmPackageManager


class UnknownPackageManagerError(ValueError):
    """Raised when a package manager has no registered adapter."""


@dataclass(frozen=True)
class _CanonicalAdapter:
    """Small typed registry adapter used until a lane supplies stricter parsing."""

    identity: Any
    lockfile_names: tuple[str, ...]

    def validate_lock(self, lock_root: Any, expected_toolchain: str) -> LockSummary:
        from nl2repobench.domain.canonical import bytes_digest

        files = tuple(sorted(path.name for path in lock_root.iterdir() if path.is_file()))
        required = set(self.lockfile_names)
        if not required.issubset(files):
            raise ValueError(
                f"lock files missing for {self.identity}: {sorted(required - set(files))}"
            )
        data = b"".join((lock_root / name).read_bytes() for name in self.lockfile_names)
        language, manager = self.identity.split("+", 1)
        return LockSummary(
            RuntimeDiscriminator(language=language, package_manager=manager),
            expected_toolchain,
            self.lockfile_names,
            bytes_digest(data),
        )

    def validate_offline_store(
        self, store_root: Any, lock_summary: LockSummary, inventory: Any, expected_toolchain: str
    ) -> StoreSummary:
        del inventory, expected_toolchain
        files = [p for p in store_root.rglob("*") if p.is_file()]
        from nl2repobench.domain.canonical import bytes_digest

        digest = bytes_digest(b"".join(p.read_bytes() for p in sorted(files)))
        return StoreSummary(
            lock_summary.identity,
            digest,
            digest,
            len(files),
            sum(p.stat().st_size for p in files),
            True,
        )

    def build_commands(self, profile: Any) -> tuple[CommandSpec, ...]:
        del profile
        return (CommandSpec((self.identity,), ".", (), 1),)

    def offline_environment(self, profile: Any) -> dict[str, str]:
        del profile
        return {"NO_NETWORK": "1"}


@dataclass(frozen=True)
class PackageManagerRegistry:
    adapters: dict[str, Any]

    @classmethod
    def default(cls) -> PackageManagerRegistry:
        return cls(
            adapters={
                "go-modules": GoModulesPackageManager(),
                "pnpm": PnpmPackageManager(),
                "uv": _CanonicalAdapter("python+uv", ("requirements.lock.txt",)),
                "pip": _CanonicalAdapter("python+pip", ("requirements.lock.txt",)),
                "npm": _CanonicalAdapter("node+npm", ("package-lock.json",)),
                "none": _CanonicalAdapter("python+none", ()),
            }
        )

    def resolve(self, identity: str) -> Any:
        if "+" in identity:
            language, manager = identity.split("+", 1)
            if manager == "none" and language == "node":
                return _CanonicalAdapter("node+none", ())
            identity = manager
        try:
            return self.adapters[identity]
        except KeyError as exc:
            available = ", ".join(sorted(self.adapters))
            raise UnknownPackageManagerError(
                f"no package-manager adapter for {identity}; registered: {available}"
            ) from exc
