"""Go Modules lock and offline-closure validator."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from .base import PackageManagerError

MAX_GO_MOD_BYTES = 4 * 1024 * 1024
MAX_GO_SUM_BYTES = 16 * 1024 * 1024
MAX_CLOSURE_FILES = 100_000
GO_VERSION = re.compile(r"^1\.[0-9]+(?:\.[0-9]+)?$")
MODULE_PATH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9./_-]*$")


def _regular(path: Path, limit: int, description: str) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise PackageManagerError(f"{description} must be a bounded regular file")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PackageManagerError(f"cannot read {description}: {exc}") from exc


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
                raise PackageManagerError("go.mod contains multiple module directives")
            module_path = fields[1]
        elif fields[0] == "go" and len(fields) == 2:
            if go_version is not None:
                raise PackageManagerError("go.mod contains multiple go directives")
            go_version = fields[1]
        elif fields[0] == "replace":
            raise PackageManagerError(
                "go.mod replace directives are not allowed in the first Go lane"
            )
        elif fields[0] in {"toolchain", "godebug", "require", "exclude", "retract"}:
            continue
        elif fields[0] in {"module", "go"}:
            raise PackageManagerError(f"malformed go.mod directive: {line}")
    if module_path is None or not MODULE_PATH.fullmatch(module_path):
        raise PackageManagerError("go.mod must declare one valid module path")
    if go_version is None or not GO_VERSION.fullmatch(go_version):
        raise PackageManagerError("go.mod must declare an exact Go 1.x version")
    return module_path, go_version


def _validate_sum(data: str) -> None:
    for index, raw in enumerate(data.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 3 or fields[0].startswith("../") or not fields[2].startswith("h1:"):
            raise PackageManagerError(f"malformed go.sum entry at line {index}")


class GoModulesPackageManager:
    identity = "go-modules"
    lockfile_name = "go.mod"

    def validate_lock(self, lockfile: Path, *, expected_version: str) -> dict[str, str]:
        data = _regular(lockfile, MAX_GO_MOD_BYTES, "go.mod")
        module_path, go_version = _module_directives(data.decode("utf-8"))
        if go_version != expected_version:
            raise PackageManagerError(
                f"go.mod toolchain {go_version} does not match locked Go {expected_version}"
            )
        sum_path = lockfile.with_name("go.sum")
        sum_data = _regular(sum_path, MAX_GO_SUM_BYTES, "go.sum")
        _validate_sum(sum_data.decode("utf-8"))
        return {
            "module_path": module_path,
            "go_version": go_version,
            "go_mod_sha256": hashlib.sha256(data).hexdigest(),
            "go_sum_sha256": hashlib.sha256(sum_data).hexdigest(),
        }

    def validate_offline_store(
        self,
        bundle_root: Path,
        *,
        lockfile: Path,
        manifest: Path,
        expected_version: str,
    ) -> None:
        summary = self.validate_lock(lockfile, expected_version=expected_version)
        if (
            manifest.is_symlink()
            or not manifest.is_file()
            or manifest.stat().st_size > MAX_GO_MOD_BYTES
        ):
            raise PackageManagerError("Go module manifest must be a bounded regular file")
        try:
            payload: Any = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PackageManagerError(f"invalid Go module manifest: {exc}") from exc
        if not isinstance(payload, Mapping) or payload.get("schema_version") != "1.0":
            raise PackageManagerError("Go module manifest schema must be 1.0")
        for key, value in summary.items():
            if payload.get(key) != value:
                raise PackageManagerError(f"Go module manifest {key} does not match lock")
        if payload.get("offline") is not True:
            raise PackageManagerError("Go module closure must be explicitly offline")
        closure = bundle_root / ("vendor" if (bundle_root / "vendor").is_dir() else "module-cache")
        if closure.is_symlink() or not closure.is_dir():
            raise PackageManagerError("Go module closure requires vendor or module-cache")
        files = [path for path in bundle_root.rglob("*") if path.is_file() and path != manifest]
        if len(files) > MAX_CLOSURE_FILES:
            raise PackageManagerError("Go module closure contains too many files")
        for path in bundle_root.rglob("*"):
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise PackageManagerError(f"Go module closure contains unsafe path: {path}")
        entries = payload.get("files")
        if not isinstance(entries, list):
            raise PackageManagerError("Go module manifest files must be an array")
        expected = {
            PurePosixPath(str(entry.get("path"))): entry.get("sha256")
            for entry in entries
            if isinstance(entry, Mapping)
        }
        actual = {
            PurePosixPath(path.relative_to(bundle_root).as_posix()): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in files
        }
        if expected != actual:
            raise PackageManagerError("Go module closure inventory or digest does not match")

    def install_command(self, *, store_dir: str) -> tuple[str, ...]:
        del store_dir
        return ("/usr/local/go/bin/go", "test", "-mod=vendor", "./...")


__all__ = ["GoModulesPackageManager"]
