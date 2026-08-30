"""Go Modules lock and offline-closure validator."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.storage.canonical_ustar import encode_tree

from .base import (
    CommandSpec,
    LockSummary,
    PackageManagerError,
    PackageManagerErrorCode,
    ResolvedPackage,
    StoreSummary,
    inventory_store_summary,
)

MAX_GO_MOD_BYTES = 4 * 1024 * 1024
MAX_GO_SUM_BYTES = 16 * 1024 * 1024
MAX_CLOSURE_FILES = 100_000
GO_VERSION = re.compile(r"^1\.[0-9]+(?:\.[0-9]+)?$")
MODULE_PATH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9./_-]*$")
GO_IDENTITY = RuntimeDiscriminator(
    language=RuntimeLanguage.GO,
    package_manager=PackageManager.GO_MODULES,
)


def _error(
    message: str,
    code: PackageManagerErrorCode = PackageManagerErrorCode.LOCK_MALFORMED,
) -> PackageManagerError:
    return PackageManagerError(code, GO_IDENTITY, "lock", message)


def _regular(path: Path, limit: int, description: str) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise _error(
            f"{description} must be a bounded regular file",
            PackageManagerErrorCode.LOCK_MISSING,
        )
    try:
        return path.read_bytes()
    except OSError as exc:
        raise _error(f"cannot read {description}: {exc}") from exc


def _module_directives(data: str) -> tuple[str, str]:
    module_path: str | None = None
    go_version: str | None = None
    for raw in data.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        fields = line.split()
        if fields[0] == "module" and len(fields) == 2:
            if module_path is not None:
                raise _error("go.mod contains multiple module directives")
            module_path = fields[1]
        elif fields[0] == "go" and len(fields) == 2:
            if go_version is not None:
                raise _error("go.mod contains multiple go directives")
            go_version = fields[1]
        elif fields[0] == "replace":
            raise _error(
                "go.mod replace directives are not allowed in the first Go lane"
            )
        elif fields[0] in {"toolchain", "godebug", "require", "exclude", "retract"}:
            continue
        elif fields[0] in {"module", "go"}:
            raise _error(f"malformed go.mod directive: {line}")
    if module_path is None or not MODULE_PATH.fullmatch(module_path):
        raise _error("go.mod must declare one valid module path")
    if go_version is None or not GO_VERSION.fullmatch(go_version):
        raise _error("go.mod must declare an exact Go 1.x version")
    return module_path, go_version


def _validate_sum(data: str) -> None:
    for index, raw in enumerate(data.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 3 or fields[0].startswith("../") or not fields[2].startswith("h1:"):
            raise _error(f"malformed go.sum entry at line {index}")


class GoModulesPackageManager:
    identity = GO_IDENTITY
    lockfile_names = ("go.mod", "go.sum")

    def validate_lock(self, lock_root: Path, expected_toolchain: str) -> LockSummary:
        lockfile = lock_root / "go.mod"
        data = _regular(lockfile, MAX_GO_MOD_BYTES, "go.mod")
        module_path, go_version = _module_directives(data.decode("utf-8"))
        if go_version != expected_toolchain:
            raise PackageManagerError(
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                self.identity,
                "lock",
                f"go.mod toolchain {go_version} does not match locked Go {expected_toolchain}",
            )
        sum_path = lockfile.with_name("go.sum")
        sum_data = _regular(sum_path, MAX_GO_SUM_BYTES, "go.sum")
        _validate_sum(sum_data.decode("utf-8"))
        return LockSummary(
            identity=self.identity,
            toolchain_version=expected_toolchain,
            lockfile_names=self.lockfile_names,
            lock_digest=f"sha256:{hashlib.sha256(encode_tree(lock_root)).hexdigest()}",
            resolved=(ResolvedPackage(module_path, go_version, "go-module"),),
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
                "Go lock and store toolchains do not match",
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
                ("/usr/local/go/bin/go", "test", "-mod=vendor", "./..."),
                ".",
                (("GOPROXY", "off"), ("GOSUMDB", "off"), ("GOWORK", "off")),
                600,
            ),
        )

    def offline_environment(self, profile: object) -> dict[str, str]:
        del profile
        return {"GOPROXY": "off", "GOSUMDB": "off", "GOWORK": "off"}


__all__ = ["GoModulesPackageManager"]
