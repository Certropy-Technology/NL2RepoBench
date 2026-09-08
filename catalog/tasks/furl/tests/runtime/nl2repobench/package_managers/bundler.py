"""Bundler lock and offline gem-cache validation."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from .base import PackageManagerError

MAX_LOCK_BYTES = 4 * 1024 * 1024
MAX_CACHE_FILES = 100_000
MAX_CACHE_FILE_BYTES = 512 * 1024 * 1024
MAX_CACHE_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
RUBYGEMS_REMOTE = "https://rubygems.org/"


def _regular(path: Path, limit: int, description: str) -> bytes:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise PackageManagerError(f"cannot stat {description}: {exc}") from exc
    if (
        stat.S_ISLNK(metadata.st_mode)
        or not stat.S_ISREG(metadata.st_mode)
        or metadata.st_size > limit
    ):
        raise PackageManagerError(f"{description} must be a bounded regular file")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PackageManagerError(f"cannot read {description}: {exc}") from exc


def _bundler_version(data: str) -> str:
    matches = re.findall(r"^BUNDLED WITH\n\s+([^\s]+)\s*$", data, re.MULTILINE)
    if len(matches) != 1 or not VERSION_PATTERN.fullmatch(matches[0]):
        raise PackageManagerError("Gemfile.lock must contain one exact BUNDLED WITH version")
    return str(matches[0])


def _validate_lock_text(data: str, *, expected_version: str) -> str:
    if not VERSION_PATTERN.fullmatch(expected_version):
        raise PackageManagerError("Bundler version must be exact semver")
    if "GIT\n" in data or "PATH\n" in data or "PLUGIN\n" in data:
        raise PackageManagerError("Gemfile.lock GIT, PATH, and PLUGIN sources are not allowed")
    if "GEM\n" not in data:
        raise PackageManagerError("Gemfile.lock must contain a GEM source section")
    remotes = re.findall(r"^\s{2}remote:\s*(\S+)\s*$", data, re.MULTILINE)
    if not remotes or any(remote != RUBYGEMS_REMOTE for remote in remotes):
        raise PackageManagerError("Gemfile.lock must use only https://rubygems.org/ remotes")
    version = _bundler_version(data)
    if version != expected_version:
        raise PackageManagerError(
            f"Gemfile.lock Bundler {version} does not match locked Bundler {expected_version}"
        )
    if not re.search(r"^PLATFORMS\n(?:\s+\S+\n)+", data, re.MULTILINE):
        raise PackageManagerError("Gemfile.lock must declare at least one platform")
    if not re.search(r"^DEPENDENCIES\n", data, re.MULTILINE):
        raise PackageManagerError("Gemfile.lock must contain a DEPENDENCIES section")
    return version


class BundlerPackageManager:
    """Validate a RubyGems lock and a fully inventoried offline cache.

    The bundle contains the task's ``Gemfile`` and ``Gemfile.lock`` plus a
    ``vendor/cache`` directory. The candidate package itself is built by the
    verifier and is never treated as a dependency artifact.
    """

    identity = "bundler"
    lockfile_name = "Gemfile.lock"

    def validate_lock(self, lockfile: Path, *, expected_version: str) -> dict[str, str]:
        data = _regular(lockfile, MAX_LOCK_BYTES, "Gemfile.lock")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PackageManagerError(f"Gemfile.lock must be UTF-8: {exc}") from exc
        version = _validate_lock_text(text, expected_version=expected_version)
        gemfile = lockfile.with_name("Gemfile")
        _regular(gemfile, MAX_LOCK_BYTES, "Gemfile")
        return {
            "bundler_version": version,
            "gemfile_sha256": hashlib.sha256(gemfile.read_bytes()).hexdigest(),
            "gemfile_lock_sha256": hashlib.sha256(data).hexdigest(),
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
        try:
            manifest_metadata = manifest.lstat()
        except OSError as exc:
            raise PackageManagerError(f"cannot stat gem bundle manifest: {exc}") from exc
        if (
            stat.S_ISLNK(manifest_metadata.st_mode)
            or not stat.S_ISREG(manifest_metadata.st_mode)
            or manifest_metadata.st_size > MAX_LOCK_BYTES
        ):
            raise PackageManagerError("gem bundle manifest must be a bounded regular file")
        try:
            payload: Any = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PackageManagerError(f"invalid gem bundle manifest: {exc}") from exc
        if not isinstance(payload, Mapping) or payload.get("schema_version") != "1.0":
            raise PackageManagerError("gem bundle manifest schema must be 1.0")
        if payload.get("ecosystem") != "rubygems" or payload.get("package_manager") != "bundler":
            raise PackageManagerError("gem bundle manifest identity is invalid")
        if payload.get("offline") is not True:
            raise PackageManagerError("gem bundle must be explicitly offline")
        for key, value in summary.items():
            if payload.get(key) != value:
                raise PackageManagerError(f"gem bundle manifest {key} does not match lock")
        cache = bundle_root / "vendor/cache"
        if cache.is_symlink() or not cache.is_dir():
            raise PackageManagerError("gem bundle requires a regular vendor/cache directory")
        files: list[Path] = []
        total = 0
        for path in bundle_root.rglob("*"):
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise PackageManagerError(f"gem bundle contains unsafe path: {path}")
            if stat.S_ISREG(mode) and path != manifest:
                if path.stat().st_size > MAX_CACHE_FILE_BYTES:
                    raise PackageManagerError(f"gem bundle file exceeds limit: {path}")
                total += path.stat().st_size
                if total > MAX_CACHE_TOTAL_BYTES:
                    raise PackageManagerError("gem bundle exceeds total size limit")
                files.append(path)
        if len(files) > MAX_CACHE_FILES:
            raise PackageManagerError("gem bundle contains too many files")
        entries = payload.get("files")
        if not isinstance(entries, list):
            raise PackageManagerError("gem bundle manifest files must be an array")
        expected: dict[PurePosixPath, str] = {}
        for entry in entries:
            if not isinstance(entry, Mapping):
                raise PackageManagerError("gem bundle manifest file entry is malformed")
            raw_path = entry.get("path")
            digest = entry.get("sha256")
            if not isinstance(raw_path, str) or not isinstance(digest, str):
                raise PackageManagerError("gem bundle manifest file entry is malformed")
            relative = PurePosixPath(raw_path)
            if relative.is_absolute() or ".." in relative.parts or raw_path in {"", "."}:
                raise PackageManagerError("gem bundle manifest contains an unsafe path")
            if relative in expected:
                raise PackageManagerError("gem bundle manifest contains duplicate paths")
            expected[relative] = digest
        actual = {
            PurePosixPath(path.relative_to(bundle_root).as_posix()): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in files
        }
        if expected != actual:
            raise PackageManagerError("gem bundle file inventory or digest does not match")

    def install_command(self, *, store_dir: str) -> tuple[str, ...]:
        if not store_dir or not store_dir.startswith("/"):
            raise PackageManagerError("Bundler store directory must be absolute")
        return (
            "/usr/bin/env",
            f"BUNDLE_PATH={store_dir}",
            "/usr/local/bin/bundle",
            "install",
            "--local",
            "--jobs",
            "1",
            "--retry",
            "0",
        )


__all__ = ["BundlerPackageManager"]
