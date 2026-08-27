"""Offline npm bundle and package tar validation for the Node pilot."""

from __future__ import annotations

import hashlib
import json
import re
import stat
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

from nl2repobench.domain.models_v2 import SEMVER_PATTERN

MAX_NPM_MEMBERS = 10_000
MAX_NPM_MEMBER_BYTES = 512 * 1024 * 1024
MAX_NPM_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
MAX_NPM_LOCK_BYTES = 16 * 1024 * 1024
MAX_NPM_MANIFEST_BYTES = 4 * 1024 * 1024
FORBIDDEN_SPEC_MARKERS = ("git+", "git://", "github:", "file:", "workspace:", "link:")
FORBIDDEN_FILES = {".npmrc", "package-lock.json.tmp"}
NPM_PACKAGE_PATTERN = re.compile(
    r"^(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$",
    re.IGNORECASE,
)


class NodeDependencyError(ValueError):
    """Raised when a dependency bundle or npm package tar is unsafe."""


def _relative_member(name: str) -> PurePosixPath:
    relative = PurePosixPath(name)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise NodeDependencyError(f"archive path escapes bundle: {name}")
    return relative


def _reject_path(relative: PurePosixPath) -> None:
    if any(part == "node_modules" for part in relative.parts):
        raise NodeDependencyError(f"node_modules is forbidden in dependency bundle: {relative}")
    if relative.name in FORBIDDEN_FILES or relative.name.endswith((".sh", ".bash")):
        raise NodeDependencyError(f"forbidden npm bundle file: {relative}")


def _walk_regular_tree(root: Path) -> list[Path]:
    if not root.is_dir() or root.is_symlink():
        raise NodeDependencyError(f"npm dependency bundle root is not a directory: {root}")
    paths: list[Path] = []
    for path in sorted(root.rglob("*")):
        relative = PurePosixPath(path.relative_to(root).as_posix())
        _reject_path(relative)
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise NodeDependencyError(f"npm dependency bundle contains a link: {relative}")
        if stat.S_ISCHR(mode) or stat.S_ISBLK(mode) or stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode):
            raise NodeDependencyError(f"npm dependency bundle contains a special file: {relative}")
        if stat.S_ISREG(mode):
            paths.append(path)
    if len(paths) > MAX_NPM_MEMBERS:
        raise NodeDependencyError("npm dependency bundle contains too many members")
    return paths


def _validate_json_file(path: Path, *, max_bytes: int) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > max_bytes:
        raise NodeDependencyError(f"invalid bounded npm metadata file: {path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NodeDependencyError(f"invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise NodeDependencyError(f"{path.name} must contain a JSON object")
    return payload


def _scan_lock_value(value: object, path: str = "lockfile") -> None:
    if isinstance(value, str):
        lowered = value.casefold()
        if any(marker in lowered for marker in FORBIDDEN_SPEC_MARKERS):
            raise NodeDependencyError(f"forbidden dependency source at {path}")
        return
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered_key = str(key).casefold()
            if lowered_key in {"registry", "registries", "npmregistry", "npmregistryserver"}:
                raise NodeDependencyError(f"registry override at {path}.{key}")
            _scan_lock_value(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _scan_lock_value(nested, f"{path}[{index}]")


def _validate_native_packages(value: object) -> dict[str, dict[str, str]]:
    if value is None:
        return {}
    if not isinstance(value, list):
        raise NodeDependencyError("npm bundle native_packages must be an array")
    native_packages: dict[str, dict[str, str]] = {}
    expected_keys = {"package", "version", "integrity", "os", "cpu", "libc"}
    for item in value:
        if not isinstance(item, dict) or set(item) != expected_keys:
            raise NodeDependencyError("npm bundle native package declaration is malformed")
        package = item.get("package")
        version = item.get("version")
        integrity = item.get("integrity")
        if not isinstance(package, str) or not NPM_PACKAGE_PATTERN.fullmatch(package):
            raise NodeDependencyError("npm bundle native package name is invalid")
        if not isinstance(version, str) or not re.fullmatch(SEMVER_PATTERN, version):
            raise NodeDependencyError("npm bundle native package version must be exact")
        if not isinstance(integrity, str) or not integrity.startswith("sha512-"):
            raise NodeDependencyError("npm bundle native package integrity is invalid")
        if item.get("os") != "linux" or item.get("cpu") != "x64" or item.get("libc") != "glibc":
            raise NodeDependencyError(
                "npm bundle native packages are restricted to linux/x64/glibc"
            )
        package_path = f"node_modules/{package}"
        if package_path in native_packages:
            raise NodeDependencyError(f"duplicate npm native package declaration: {package}")
        native_packages[package_path] = {
            "version": version,
            "integrity": integrity,
            "os": "linux",
            "cpu": "x64",
            "libc": "glibc",
        }
    return native_packages


def _validate_lockfile(
    path: Path,
    expected_npm_version: str | None,
    native_packages: dict[str, dict[str, str]],
) -> dict[str, Any]:
    payload = _validate_json_file(path, max_bytes=MAX_NPM_LOCK_BYTES)
    if payload.get("lockfileVersion") != 3:
        raise NodeDependencyError("npm dependency lockfile must use lockfileVersion 3")
    packages = payload.get("packages")
    if not isinstance(packages, dict) or "" not in packages:
        raise NodeDependencyError("npm dependency lockfile must contain a packages root")
    _scan_lock_value(payload)
    matched_native_packages: set[str] = set()
    for package_path, package in packages.items():
        if not isinstance(package_path, str) or not (
            package_path == "" or package_path.startswith("node_modules/")
        ):
            raise NodeDependencyError(f"invalid package path in lockfile: {package_path}")
        if package_path == "":
            continue
        if not isinstance(package, dict):
            raise NodeDependencyError(f"invalid package entry in lockfile: {package_path}")
        if package.get("link") is True or package.get("resolved", "").startswith("file:"):
            raise NodeDependencyError(f"linked package is forbidden: {package_path}")
        native_markers = {"node-gyp", "node-pre-gyp", "nan", "node-addon-api"}
        package_name = package_path.removeprefix("node_modules/").casefold()
        if package.get("hasInstallScript") or package.get("gypfile") or package.get("binary"):
            raise NodeDependencyError(f"native or platform package is forbidden: {package_path}")
        platform_marked = any(package.get(field) for field in ("os", "cpu", "libc"))
        declaration = native_packages.get(package_path)
        if platform_marked or declaration is not None:
            if declaration is None:
                raise NodeDependencyError(
                    f"undeclared native or platform package is forbidden: {package_path}"
                )
            if (
                package.get("version") != declaration["version"]
                or package.get("integrity") != declaration["integrity"]
                or package.get("os") != [declaration["os"]]
                or package.get("cpu") != [declaration["cpu"]]
                or package.get("libc") not in (None, [declaration["libc"]])
            ):
                raise NodeDependencyError(
                    f"native package lock metadata mismatch: {package_path}"
                )
            matched_native_packages.add(package_path)
        if package_name in native_markers:
            raise NodeDependencyError(f"native build dependency is forbidden: {package_path}")
        if not isinstance(package.get("integrity"), str) or not package["integrity"].startswith(
            "sha512-"
        ):
            raise NodeDependencyError(f"package integrity is missing: {package_path}")
        if not isinstance(package.get("resolved"), str) or not package["resolved"].startswith(
            ("https://", "http://")
        ):
            raise NodeDependencyError(f"package resolution is missing: {package_path}")
    if expected_npm_version is not None and not re.fullmatch(SEMVER_PATTERN, expected_npm_version):
        raise NodeDependencyError("expected npm version is not an exact semantic version")
    missing_native_packages = set(native_packages) - matched_native_packages
    if missing_native_packages:
        raise NodeDependencyError(
            "declared npm native packages are missing from the lockfile: "
            + ", ".join(sorted(missing_native_packages))
        )
    return payload


def _validate_manifest(
    path: Path,
    root: Path,
    expected_npm_version: str | None,
) -> dict[str, dict[str, str]]:
    payload = _validate_json_file(path, max_bytes=MAX_NPM_MANIFEST_BYTES)
    if payload.get("schema_version") != "1.0":
        raise NodeDependencyError("npm bundle manifest must use schema version 1.0")
    if payload.get("ecosystem") != "npm":
        raise NodeDependencyError("npm bundle manifest ecosystem must be npm")
    if payload.get("lockfile_version") not in {"3", 3}:
        raise NodeDependencyError("npm bundle manifest lockfile version must be 3")
    if payload.get("package_manager") != "npm":
        raise NodeDependencyError("npm bundle manifest package manager must be npm")
    version = payload.get("package_manager_version")
    if not isinstance(version, str) or not re.fullmatch(SEMVER_PATTERN, version):
        raise NodeDependencyError("npm bundle manifest requires an exact npm version")
    if expected_npm_version is not None and version != expected_npm_version:
        raise NodeDependencyError("npm bundle npm version does not match the locked runtime")
    if (
        payload.get("install_mode") != "offline"
        or payload.get("lifecycle_scripts") != "ignore-scripts"
    ):
        raise NodeDependencyError("npm bundle must be offline and ignore lifecycle scripts")
    cache_entries = payload.get("cache_entries", [])
    if not isinstance(cache_entries, list) or any(
        not isinstance(item, str) for item in cache_entries
    ):
        raise NodeDependencyError("npm cache entries must be relative paths")
    cache_root = root / "npm-cache"
    for item in cache_entries:
        relative = _relative_member(item)
        target = cache_root.joinpath(*relative.parts)
        if not target.is_file() or target.is_symlink():
            raise NodeDependencyError(f"npm cache entry is missing: {item}")
    listed = {PurePosixPath(item) for item in cache_entries}
    actual = {
        PurePosixPath(path.relative_to(cache_root).as_posix())
        for path in cache_root.rglob("*")
        if path.is_file()
    }
    if listed != actual:
        raise NodeDependencyError("npm cache entries do not match the bundle")
    files = payload.get("files")
    if files is not None:
        if not isinstance(files, list):
            raise NodeDependencyError("npm bundle files must be an array")
        for entry in files:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise NodeDependencyError("npm bundle file entry is malformed")
            relative = _relative_member(entry["path"])
            target = root.joinpath(*relative.parts)
            if not target.is_file() or target.is_symlink():
                raise NodeDependencyError(f"npm bundle file is missing: {entry['path']}")
            digest = entry.get("sha256")
            if (
                not isinstance(digest, str)
                or digest != hashlib.sha256(target.read_bytes()).hexdigest()
            ):
                raise NodeDependencyError(f"npm bundle file digest mismatch: {entry['path']}")
    return _validate_native_packages(payload.get("native_packages"))


def validate_npm_dependency_bundle(
    root: Path,
    *,
    expected_npm_version: str | None = None,
) -> None:
    """Validate the extracted ``package-lock.json``/cache closure."""

    paths = _walk_regular_tree(root)
    required = {"package-lock.json", "bundle.manifest.json"}
    actual_root = {path.name for path in root.iterdir()}
    if not required.issubset(actual_root) or "npm-cache" not in actual_root:
        raise NodeDependencyError(
            "npm dependency bundle requires package-lock.json, npm-cache, and bundle.manifest.json"
        )
    unexpected = actual_root - required - {"npm-cache"}
    if unexpected:
        raise NodeDependencyError(f"unexpected npm dependency bundle entries: {sorted(unexpected)}")
    native_packages = _validate_manifest(
        root / "bundle.manifest.json", root, expected_npm_version
    )
    _validate_lockfile(root / "package-lock.json", expected_npm_version, native_packages)
    total = sum(path.stat().st_size for path in paths)
    if total > MAX_NPM_TOTAL_BYTES:
        raise NodeDependencyError("npm dependency bundle exceeds expanded size limit")


def validate_npm_package_tarball(archive: Path) -> None:
    """Reject traversal, links, scripts, native addons, and duplicate tar members."""

    if (
        archive.is_symlink()
        or not archive.is_file()
        or archive.stat().st_size > MAX_NPM_TOTAL_BYTES
    ):
        raise NodeDependencyError("candidate npm package tarball is not bounded and regular")
    try:
        handle = tarfile.open(archive, mode="r:*")
    except (OSError, tarfile.TarError) as exc:
        raise NodeDependencyError(f"cannot read candidate npm tarball: {exc}") from exc
    with handle:
        seen: set[PurePosixPath] = set()
        total = 0
        members = 0
        package_json: dict[str, Any] | None = None
        for member in handle:
            members += 1
            if members > MAX_NPM_MEMBERS:
                raise NodeDependencyError("candidate npm tarball has too many members")
            relative = _relative_member(member.name)
            if relative.parts[0] != "package":
                raise NodeDependencyError(
                    f"candidate npm tarball path is outside package/: {member.name}"
                )
            _reject_path(relative)
            if member.issym() or member.islnk() or member.isdev():
                raise NodeDependencyError(
                    f"candidate npm tarball contains a link/device: {member.name}"
                )
            if relative in seen:
                raise NodeDependencyError(
                    f"candidate npm tarball contains duplicate path: {member.name}"
                )
            seen.add(relative)
            if member.size < 0 or member.size > MAX_NPM_MEMBER_BYTES:
                raise NodeDependencyError(
                    f"candidate npm tarball member exceeds size limit: {member.name}"
                )
            if member.isfile():
                total += member.size
                if total > MAX_NPM_TOTAL_BYTES:
                    raise NodeDependencyError("candidate npm tarball expanded size exceeds limit")
                if relative.as_posix() == "package/package.json":
                    extracted = handle.extractfile(member)
                    if extracted is None:
                        raise NodeDependencyError("candidate package.json cannot be read")
                    try:
                        package_json = json.loads(extracted.read(MAX_NPM_MEMBER_BYTES))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise NodeDependencyError("candidate package.json is malformed") from exc
                if (
                    relative.suffix == ".node"
                    or relative.name in {"binding.gyp", "binding.gypi"}
                    or "prebuilds" in relative.parts
                ):
                    raise NodeDependencyError("native Node addons are not supported")
                if relative.name in FORBIDDEN_FILES or relative.name.endswith((".sh", ".bash")):
                    raise NodeDependencyError(
                        f"candidate npm tarball contains a script: {member.name}"
                    )
            elif not member.isdir():
                raise NodeDependencyError(f"unsupported npm tarball member: {member.name}")
        if package_json is None:
            raise NodeDependencyError("candidate npm tarball lacks package/package.json")
        if not isinstance(package_json, dict):
            raise NodeDependencyError("candidate package.json must be an object")
        lifecycle_hooks = {
            "preinstall",
            "install",
            "postinstall",
            "prepare",
            "prepublish",
            "prepublishonly",
            "publish",
            "postpublish",
        }
        scripts = package_json.get("scripts")
        if scripts is not None and (
            not isinstance(scripts, dict)
            or any(str(name).casefold() in lifecycle_hooks for name in scripts)
        ):
            raise NodeDependencyError("candidate lifecycle scripts are forbidden")
        if "workspaces" in package_json:
            raise NodeDependencyError("npm workspaces are forbidden")
        if package_json.get("gypfile") or package_json.get("binary"):
            raise NodeDependencyError("native Node addons are not supported")
