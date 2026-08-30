"""Pinned pnpm v9 lockfile and offline store validation.

The adapter validates the closure and returns an install command. It never
falls back to npm and never executes a package-manager command itself.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.storage.canonical_ustar import encode_tree

from .base import (
    CommandSpec,
    LockSummary,
    PackageManagerError,
    PackageManagerErrorCode,
    StoreSummary,
    inventory_store_summary,
)

MAX_LOCK_BYTES = 16 * 1024 * 1024
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_STORE_FILES = 100_000
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
FORBIDDEN_MARKERS = ("git+", "git://", "github:", "file:", "workspace:", "link:")


PNPM_IDENTITY = RuntimeDiscriminator(
    language=RuntimeLanguage.NODE,
    package_manager=PackageManager.PNPM,
)


def _error(
    message: str,
    code: PackageManagerErrorCode = PackageManagerErrorCode.LOCK_MALFORMED,
) -> PackageManagerError:
    return PackageManagerError(code, PNPM_IDENTITY, "lock", message)


def _scan(value: object, path: str = "lockfile") -> None:
    if isinstance(value, str):
        lowered = value.casefold()
        if any(marker in lowered for marker in FORBIDDEN_MARKERS):
            raise _error(f"forbidden dependency source at {path}")
        return
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).casefold()
            if key_text in {"registry", "registries", "npmregistry", "npmregistryserver"}:
                raise _error(f"registry override at {path}.{key}")
            _scan(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _scan(nested, f"{path}[{index}]")


def _yaml_documents(path: Path) -> list[dict[str, Any]]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_LOCK_BYTES:
        raise _error("pnpm lockfile must be a bounded regular file")
    try:
        import yaml
    except ImportError as exc:
        raise _error("pnpm validation requires PyYAML") from exc
    try:
        documents = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
        raise _error(f"cannot parse pnpm lockfile: {exc}") from exc
    result = [document for document in documents if document is not None]
    if not result or any(not isinstance(document, dict) for document in result):
        raise _error("pnpm lockfile documents must be objects")
    return result


class PnpmPackageManager:
    identity = PNPM_IDENTITY
    lockfile_names = ("pnpm-lock.yaml",)

    def validate_lock(self, lock_root: Path, expected_toolchain: str) -> LockSummary:
        if not SEMVER.fullmatch(expected_toolchain):
            raise PackageManagerError(
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                self.identity,
                "lock",
                "pnpm version must be exact semver",
            )
        lockfile = lock_root / "pnpm-lock.yaml"
        if lock_root.is_symlink() or not lockfile.is_file():
            raise PackageManagerError(
                PackageManagerErrorCode.LOCK_MISSING,
                self.identity,
                "lock",
                "pnpm-lock.yaml is missing",
            )
        documents = _yaml_documents(lockfile)
        root = documents[0]
        version = str(root.get("lockfileVersion", ""))
        if not version.startswith("9"):
            raise _error("pnpm lockfile must use lockfile version 9")
        _scan(documents)
        importers = root.get("importers", {})
        packages = root.get("packages", {})
        snapshots = root.get("snapshots", {})
        for name, entry in packages.items() if isinstance(packages, Mapping) else ():
            if not isinstance(name, str) or not isinstance(entry, Mapping):
                raise _error("pnpm packages entries are malformed")
            resolution = entry.get("resolution")
            if name == "":
                continue
            if not isinstance(resolution, Mapping):
                raise _error(f"package resolution is missing: {name}")
            integrity = resolution.get("integrity")
            if not isinstance(integrity, str) or not integrity.startswith("sha512-"):
                raise _error(f"package integrity is missing: {name}")
            if entry.get("hasInstallScript") or entry.get("requiresBuild"):
                raise _error(f"lifecycle/native package is forbidden: {name}")
        if (
            not isinstance(importers, Mapping)
            or not isinstance(packages, Mapping)
            or not isinstance(snapshots, Mapping)
        ):
            raise _error("pnpm lockfile requires importer, package, and snapshot maps")
        return LockSummary(
            identity=self.identity,
            toolchain_version=expected_toolchain,
            lockfile_names=self.lockfile_names,
            lock_digest=f"sha256:{hashlib.sha256(encode_tree(lock_root)).hexdigest()}",
        )

    def validate_offline_store(
        self,
        store_root: Path,
        lock_summary: LockSummary,
        inventory: object,
        expected_toolchain: str,
    ) -> StoreSummary:
        if (
            lock_summary.identity != self.identity
            or lock_summary.toolchain_version != expected_toolchain
        ):
            raise PackageManagerError(
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                self.identity,
                "store",
                "pnpm lock and store toolchains do not match",
            )
        return inventory_store_summary(
            identity=self.identity,
            store_root=store_root,
            inventory=inventory,
        )

    def build_commands(self, profile: object) -> tuple[CommandSpec, ...]:
        del profile
        return (
            CommandSpec(
                (
                    "/usr/local/bin/pnpm",
                    "install",
                    "--offline",
                    "--frozen-lockfile",
                    "--ignore-scripts",
                ),
                ".",
                (("PNPM_HOME", "/opt/pnpm"),),
                600,
            ),
        )

    def offline_environment(self, profile: object) -> dict[str, str]:
        del profile
        return {"PNPM_HOME": "/opt/pnpm"}


__all__ = ["PnpmPackageManager"]
