"""Pinned pnpm v9 lockfile and offline store validation.

The adapter validates the closure and returns an install command. It never
falls back to npm and never executes a package-manager command itself.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .base import PackageManagerError

MAX_LOCK_BYTES = 16 * 1024 * 1024
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_STORE_FILES = 100_000
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
FORBIDDEN_MARKERS = ("git+", "git://", "github:", "file:", "workspace:", "link:")


@dataclass(frozen=True)
class PnpmLockSummary:
    lockfile_version: str
    importer_count: int
    package_count: int
    snapshot_count: int
    digest: str


def _bounded_json(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_MANIFEST_BYTES:
        raise PackageManagerError(f"invalid bounded pnpm manifest: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageManagerError(f"invalid pnpm manifest JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise PackageManagerError("pnpm bundle manifest must be an object")
    return value


def _scan(value: object, path: str = "lockfile") -> None:
    if isinstance(value, str):
        lowered = value.casefold()
        if any(marker in lowered for marker in FORBIDDEN_MARKERS):
            raise PackageManagerError(f"forbidden dependency source at {path}")
        return
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).casefold()
            if key_text in {"registry", "registries", "npmregistry", "npmregistryserver"}:
                raise PackageManagerError(f"registry override at {path}.{key}")
            _scan(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _scan(nested, f"{path}[{index}]")


def _yaml_documents(path: Path) -> list[dict[str, Any]]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_LOCK_BYTES:
        raise PackageManagerError("pnpm lockfile must be a bounded regular file")
    try:
        import yaml
    except ImportError as exc:
        raise PackageManagerError("pnpm validation requires PyYAML") from exc
    try:
        documents = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
        raise PackageManagerError(f"cannot parse pnpm lockfile: {exc}") from exc
    result = [document for document in documents if document is not None]
    if not result or any(not isinstance(document, dict) for document in result):
        raise PackageManagerError("pnpm lockfile documents must be objects")
    return result


class PnpmPackageManager:
    identity = "pnpm"
    lockfile_name = "pnpm-lock.yaml"

    def validate_lock(self, lockfile: Path, *, expected_version: str) -> PnpmLockSummary:
        if not SEMVER.fullmatch(expected_version):
            raise PackageManagerError("pnpm version must be exact semver")
        documents = _yaml_documents(lockfile)
        root = documents[0]
        version = str(root.get("lockfileVersion", ""))
        if not version.startswith("9"):
            raise PackageManagerError("pnpm lockfile must use lockfile version 9")
        _scan(documents)
        importers = root.get("importers", {})
        packages = root.get("packages", {})
        snapshots = root.get("snapshots", {})
        for name, entry in packages.items() if isinstance(packages, Mapping) else ():
            if not isinstance(name, str) or not isinstance(entry, Mapping):
                raise PackageManagerError("pnpm packages entries are malformed")
            resolution = entry.get("resolution")
            if name == "":
                continue
            if not isinstance(resolution, Mapping):
                raise PackageManagerError(f"package resolution is missing: {name}")
            integrity = resolution.get("integrity")
            if not isinstance(integrity, str) or not integrity.startswith("sha512-"):
                raise PackageManagerError(f"package integrity is missing: {name}")
            if entry.get("hasInstallScript") or entry.get("requiresBuild"):
                raise PackageManagerError(f"lifecycle/native package is forbidden: {name}")
        if (
            not isinstance(importers, Mapping)
            or not isinstance(packages, Mapping)
            or not isinstance(snapshots, Mapping)
        ):
            raise PackageManagerError("pnpm lockfile requires importer, package, and snapshot maps")
        return PnpmLockSummary(
            lockfile_version=version,
            importer_count=len(importers),
            package_count=len(packages),
            snapshot_count=len(snapshots),
            digest=hashlib.sha256(lockfile.read_bytes()).hexdigest(),
        )

    def validate_offline_store(
        self,
        bundle_root: Path,
        *,
        lockfile: Path,
        manifest: Path,
        expected_version: str,
    ) -> None:
        summary = self.validate_lock(lockfile, expected_version=expected_version)
        payload = _bounded_json(manifest)
        if payload.get("schema_version") != "1.0":
            raise PackageManagerError("pnpm bundle manifest schema must be 1.0")
        if payload.get("ecosystem") != "npm" or payload.get("package_manager") != "pnpm":
            raise PackageManagerError("pnpm bundle manifest identity is invalid")
        if str(payload.get("lockfile_version")) != "9":
            raise PackageManagerError("pnpm bundle manifest lockfile version must be 9")
        if payload.get("package_manager_version") != expected_version:
            raise PackageManagerError("pnpm bundle version does not match the toolchain")
        if (
            payload.get("install_mode") != "offline"
            or payload.get("lifecycle_scripts") != "ignore-scripts"
        ):
            raise PackageManagerError("pnpm bundle must be offline and ignore lifecycle scripts")
        if payload.get("lockfile_sha256") != summary.digest:
            raise PackageManagerError("pnpm lockfile digest does not match the bundle manifest")
        store = bundle_root / "pnpm-store"
        if store.is_symlink() or not store.is_dir():
            raise PackageManagerError("pnpm bundle requires a regular pnpm-store directory")
        files = [path for path in store.rglob("*") if path.is_file()]
        if len(files) > MAX_STORE_FILES:
            raise PackageManagerError("pnpm store contains too many files")
        for path in store.rglob("*"):
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise PackageManagerError(f"pnpm store contains unsafe path: {path}")
        entries = payload.get("files")
        if not isinstance(entries, list):
            raise PackageManagerError("pnpm bundle manifest files must be an array")
        expected = {
            PurePosixPath(str(item.get("path"))): item.get("sha256")
            for item in entries
            if isinstance(item, Mapping)
        }
        actual = {
            PurePosixPath(path.relative_to(bundle_root).as_posix()): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in bundle_root.rglob("*")
            if path.is_file() and path != manifest
        }
        if expected != actual:
            raise PackageManagerError("pnpm bundle file inventory or digest does not match")

    def install_command(self, *, store_dir: str) -> tuple[str, ...]:
        return (
            "/usr/local/bin/pnpm",
            "install",
            "--offline",
            "--frozen-lockfile",
            "--ignore-scripts",
            "--store-dir",
            store_dir,
        )


__all__ = ["PnpmLockSummary", "PnpmPackageManager"]
