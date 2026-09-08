"""Strict Cargo lock and offline-closure checks for the Rust authoring lane."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
import tomllib
from collections import Counter
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import cast

from .base import PackageManagerError

MAX_LOCK_BYTES = 16 * 1024 * 1024
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_CLOSURE_FILES = 100_000
MAX_CRATE_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_CRATE_EXPANDED_BYTES = 512 * 1024 * 1024
MAX_CRATE_MEMBERS = 10_000
CRATES_IO_SOURCE = "registry+https://github.com/rust-lang/crates.io-index"
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
PACKAGE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def _read_regular(path: Path, limit: int, description: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise PackageManagerError(f"{description} must be a regular file")
    try:
        if path.stat().st_size > limit:
            raise PackageManagerError(f"{description} exceeds the size limit")
        return path.read_bytes()
    except OSError as exc:
        raise PackageManagerError(f"cannot read {description}: {exc}") from exc


def _parse_lock(data: bytes) -> dict[str, object]:
    try:
        payload = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise PackageManagerError(f"Cargo.lock is invalid TOML: {exc}") from exc
    if set(payload) != {"version", "package"}:
        raise PackageManagerError("Cargo.lock may contain only version and package")
    version = payload.get("version")
    if version not in {3, 4}:
        raise PackageManagerError("Cargo.lock must use lockfile version 3 or 4")
    packages = payload.get("package")
    if not isinstance(packages, list) or not packages:
        raise PackageManagerError("Cargo.lock must contain at least one package")
    identities: set[tuple[str, str, str | None]] = set()
    package_names: list[str] = []
    sort_keys: list[tuple[str, str, str]] = []
    source_less = 0
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise PackageManagerError(f"Cargo.lock package {index} is not a table")
        if not set(package).issubset({"name", "version", "source", "checksum", "dependencies"}):
            raise PackageManagerError(f"Cargo.lock package {index} has unknown fields")
        name = package.get("name")
        package_version = package.get("version")
        if not isinstance(name, str) or not PACKAGE_NAME.fullmatch(name):
            raise PackageManagerError(f"Cargo.lock package {index} has an invalid name")
        if not isinstance(package_version, str) or not SEMVER.fullmatch(package_version):
            raise PackageManagerError(f"Cargo.lock package {name} has an invalid version")
        dependencies = package.get("dependencies", [])
        if not isinstance(dependencies, list) or any(
            not isinstance(item, str) or not item for item in dependencies
        ):
            raise PackageManagerError(f"Cargo.lock package {name} has invalid dependencies")
        source = package.get("source")
        if source is not None and not isinstance(source, str):
            raise PackageManagerError(f"Cargo.lock package {name} has an invalid source")
        if source is not None and source != CRATES_IO_SOURCE:
            raise PackageManagerError(f"Cargo.lock package {name} uses a non-crates.io source")
        checksum = package.get("checksum")
        if source is None:
            source_less += 1
            if checksum is not None:
                raise PackageManagerError(f"workspace package {name} cannot have a checksum")
        elif not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            raise PackageManagerError(f"Cargo package {name} requires a SHA-256 checksum")
        identity = (name, package_version, source)
        if identity in identities:
            raise PackageManagerError(f"Cargo.lock contains duplicate package {name}")
        identities.add(identity)
        package_names.append(name)
        sort_keys.append((name, package_version, source or ""))
    if source_less != 1:
        raise PackageManagerError("Cargo.lock must contain exactly one workspace package")
    if sort_keys != sorted(sort_keys):
        raise PackageManagerError("Cargo.lock packages must be sorted")
    return {
        "lockfile_version": version,
        "package_count": len(packages),
        "package_names": tuple(sorted(package_names)),
        "lockfile_sha256": hashlib.sha256(data).hexdigest(),
    }


def _lock_packages(lockfile: Path) -> tuple[tuple[str, str, str | None], ...]:
    """Return lock identities for vendor directory validation."""

    try:
        payload = tomllib.loads(
            _read_regular(lockfile, MAX_LOCK_BYTES, "Cargo.lock").decode("utf-8")
        )
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise PackageManagerError(f"Cargo.lock is invalid TOML: {exc}") from exc
    packages = payload.get("package")
    if not isinstance(packages, list):
        raise PackageManagerError("Cargo.lock package list is malformed")
    result: list[tuple[str, str, str | None]] = []
    for package in packages:
        if not isinstance(package, Mapping):
            raise PackageManagerError("Cargo.lock package is malformed")
        name = package.get("name")
        version = package.get("version")
        source = package.get("source")
        if (
            not isinstance(name, str)
            or not isinstance(version, str)
            or source is not None
            and not isinstance(source, str)
        ):
            raise PackageManagerError("Cargo.lock package identity is malformed")
        result.append((name, version, source))
    return tuple(result)


def _crate_files(path: Path, *, expected_root: str) -> dict[str, str]:
    """Hash one bounded crates.io archive without extracting it."""

    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_CRATE_ARCHIVE_BYTES:
        raise PackageManagerError(f"Cargo crate archive is unsafe: {path}")
    result: dict[str, str] = {}
    expanded = 0
    try:
        with tarfile.open(path, mode="r:gz") as archive:
            for index, member in enumerate(archive, start=1):
                if index > MAX_CRATE_MEMBERS:
                    raise PackageManagerError("Cargo crate archive contains too many members")
                relative = PurePosixPath(member.name)
                if (
                    relative.is_absolute()
                    or ".." in relative.parts
                    or not relative.parts
                    or relative.parts[0] != expected_root
                ):
                    raise PackageManagerError(
                        f"Cargo crate archive path is unsafe: {member.name}"
                    )
                if member.isdir():
                    continue
                if not member.isfile() or member.issym() or member.islnk():
                    raise PackageManagerError(
                        f"Cargo crate archive member type is unsafe: {member.name}"
                    )
                expanded += member.size
                if expanded > MAX_CRATE_EXPANDED_BYTES:
                    raise PackageManagerError("Cargo crate archive expands beyond the limit")
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise PackageManagerError(
                        f"Cargo crate archive member cannot be read: {member.name}"
                    )
                name = PurePosixPath(*relative.parts[1:]).as_posix()
                if not name or name in result:
                    raise PackageManagerError(
                        f"Cargo crate archive contains duplicate path: {member.name}"
                    )
                digest = hashlib.sha256()
                observed = 0
                while chunk := extracted.read(1024 * 1024):
                    observed += len(chunk)
                    digest.update(chunk)
                if observed != member.size:
                    raise PackageManagerError(
                        f"Cargo crate archive member size is inconsistent: {member.name}"
                    )
                result[name] = digest.hexdigest()
    except (OSError, tarfile.TarError) as exc:
        raise PackageManagerError(f"Cargo crate archive is malformed: {exc}") from exc
    return result


class CargoPackageManager:
    """Cargo adapter used by Rust sources and the Rust Harbor compiler."""

    identity = "cargo"
    lockfile_name = "Cargo.lock"

    def validate_lock(self, lockfile: Path, *, expected_version: str) -> dict[str, object]:
        if lockfile.name != self.lockfile_name:
            raise PackageManagerError("Cargo lockfile must be named Cargo.lock")
        data = _read_regular(lockfile, MAX_LOCK_BYTES, "Cargo.lock")
        summary = _parse_lock(data)
        if not isinstance(expected_version, str) or not expected_version.strip():
            raise PackageManagerError("Cargo toolchain version must be explicit")
        return {"toolchain_version": expected_version, **summary}

    def validate_offline_store(
        self,
        bundle_root: Path,
        *,
        lockfile: Path,
        manifest: Path,
        expected_version: str,
    ) -> None:
        summary = self.validate_lock(lockfile, expected_version=expected_version)
        if bundle_root.is_symlink() or not bundle_root.is_dir():
            raise PackageManagerError("Cargo bundle root must be a regular directory")
        if manifest.resolve().parent != bundle_root.resolve():
            raise PackageManagerError("Cargo manifest must be directly inside the bundle root")
        cargo_toml = bundle_root / "Cargo.toml"
        _read_regular(cargo_toml, MAX_MANIFEST_BYTES, "Cargo.toml")
        manifest_data = _read_regular(manifest, MAX_MANIFEST_BYTES, "Cargo manifest")
        try:
            payload = json.loads(manifest_data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PackageManagerError(f"Cargo manifest is invalid JSON: {exc}") from exc
        if not isinstance(payload, Mapping):
            raise PackageManagerError("Cargo manifest must be an object")
        if payload.get("schema_version") != "1.0":
            raise PackageManagerError("Cargo manifest schema must be 1.0")
        for key, value in summary.items():
            if key == "package_names":
                continue
            if payload.get(key) != value:
                raise PackageManagerError(f"Cargo manifest {key} does not match Cargo.lock")
        if payload.get("offline") is not True:
            raise PackageManagerError("Cargo manifest must declare offline=true")
        closure = bundle_root / "vendor"
        if closure.is_symlink() or not closure.is_dir():
            raise PackageManagerError("Cargo offline closure requires a vendor directory")
        expected_vendor_packages = {
            (name, version)
            for name, version, source in _lock_packages(lockfile)
            if source is not None
        }
        lock_checksums: dict[tuple[str, str], str] = {}
        lock_data = tomllib.loads(lockfile.read_text(encoding="utf-8"))
        for package in lock_data.get("package", []):
            if not isinstance(package, Mapping) or package.get("source") is None:
                continue
            name = package.get("name")
            version = package.get("version")
            checksum = package.get("checksum")
            if not all(isinstance(value, str) for value in (name, version, checksum)):
                raise PackageManagerError("Cargo.lock registry checksum is malformed")
            lock_checksums[(cast(str, name), cast(str, version))] = cast(str, checksum)
        archive_root = bundle_root / "registry" / "cache"
        if expected_vendor_packages:
            if archive_root.is_symlink() or not archive_root.is_dir():
                raise PackageManagerError(
                    "Cargo closure with registry dependencies requires registry/cache"
                )
            crate_archives = {
                path.name: path
                for path in archive_root.rglob("*.crate")
                if path.is_file() and not path.is_symlink()
            }
            if any(path.is_symlink() for path in archive_root.rglob("*.crate")):
                raise PackageManagerError("Cargo crate archive inventory contains a symlink")
            expected_archives = {
                f"{name}-{version}.crate" for name, version in expected_vendor_packages
            }
            if set(crate_archives) != expected_archives:
                raise PackageManagerError(
                    "Cargo crate archive inventory does not match Cargo.lock"
                )
        else:
            crate_archives = {}
        actual_vendor_packages: dict[tuple[str, str], Path] = {}
        for vendor in sorted(closure.iterdir()):
            if not vendor.is_dir() or vendor.is_symlink():
                continue
            package_manifest = tomllib.loads(
                _read_regular(
                    vendor / "Cargo.toml", MAX_MANIFEST_BYTES, "vendored Cargo.toml"
                ).decode("utf-8")
            )
            package = package_manifest.get("package")
            if not isinstance(package, Mapping):
                raise PackageManagerError(f"Cargo vendor package is malformed: {vendor}")
            name = package.get("name")
            version = package.get("version")
            if not isinstance(name, str) or not isinstance(version, str):
                raise PackageManagerError(f"Cargo vendor identity is malformed: {vendor}")
            identity = (name, version)
            if identity in actual_vendor_packages:
                raise PackageManagerError(f"Cargo vendor package is duplicated: {identity}")
            actual_vendor_packages[identity] = vendor
            checksum_path = vendor / ".cargo-checksum.json"
            checksum_data = json.loads(
                _read_regular(checksum_path, MAX_MANIFEST_BYTES, "Cargo checksum").decode(
                    "utf-8"
                )
            )
            if not isinstance(checksum_data, Mapping) or set(checksum_data) != {
                "files",
                "package",
            }:
                raise PackageManagerError(
                    f"Cargo checksum file is malformed: {checksum_path}"
                )
            if checksum_data.get("package") != lock_checksums.get(identity):
                raise PackageManagerError(
                    f"Cargo vendor package checksum does not match lock: {vendor}"
                )
            files = checksum_data.get("files")
            if not isinstance(files, Mapping):
                raise PackageManagerError(f"Cargo checksum inventory is malformed: {vendor}")
            actual_files = {
                path.relative_to(vendor).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in vendor.rglob("*")
                if path.is_file() and path.name != ".cargo-checksum.json"
            }
            if dict(files) != actual_files:
                raise PackageManagerError(f"Cargo vendor file checksums do not match: {vendor}")
            archive_name = f"{name}-{version}.crate"
            archive = crate_archives[archive_name]
            if hashlib.sha256(archive.read_bytes()).hexdigest() != lock_checksums[identity]:
                raise PackageManagerError(
                    f"Cargo crate archive checksum does not match lock: {archive}"
                )
            if _crate_files(archive, expected_root=f"{name}-{version}") != actual_files:
                raise PackageManagerError(
                    f"Cargo vendor bytes differ from crate archive: {vendor}"
                )
        if set(actual_vendor_packages) != expected_vendor_packages:
            raise PackageManagerError(
                "Cargo vendor package identities do not match Cargo.lock"
            )
        files = [path for path in bundle_root.rglob("*") if path.is_file()]
        if len(files) > MAX_CLOSURE_FILES:
            raise PackageManagerError("Cargo closure contains too many files")
        for path in bundle_root.rglob("*"):
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise PackageManagerError(f"Cargo closure contains unsafe path: {path}")
        expected_files = payload.get("files")
        if not isinstance(expected_files, list):
            raise PackageManagerError("Cargo manifest files must be an array")
        actual = {
            path.relative_to(bundle_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files
            if path != manifest
        }
        declared: dict[str, object] = {}
        for item in expected_files:
            if not isinstance(item, Mapping):
                raise PackageManagerError("Cargo manifest file entry must be an object")
            relative = item.get("path")
            if not isinstance(relative, str):
                raise PackageManagerError("Cargo manifest file path must be a string")
            parsed = PurePosixPath(relative)
            if parsed.is_absolute() or ".." in parsed.parts or relative in {"", "."}:
                raise PackageManagerError("Cargo manifest contains an unsafe file path")
            if relative in declared:
                raise PackageManagerError("Cargo manifest contains duplicate file paths")
            declared[relative] = item.get("sha256")
        if declared != actual:
            raise PackageManagerError("Cargo closure inventory or digest does not match")
        package_names = summary["package_names"]
        package_count = summary["package_count"]
        if not isinstance(package_names, tuple) or not isinstance(package_count, int):
            raise PackageManagerError("Cargo lock package names are malformed")
        self._validate_metadata(
            bundle_root,
            expected_version=expected_version,
            expected_package_count=package_count,
            expected_package_names=package_names,
            expected_packages=set(_lock_packages(lockfile)),
        )

    @staticmethod
    def _validate_metadata(
        bundle_root: Path,
        *,
        expected_version: str,
        expected_package_count: int,
        expected_package_names: tuple[str, ...],
        expected_packages: set[tuple[str, str, str | None]],
    ) -> None:
        """Ask Cargo to resolve the exact locked graph without contacting a registry."""

        cargo = shutil.which("cargo") or "/usr/local/cargo/bin/cargo"
        if not Path(cargo).is_file():
            raise PackageManagerError("Cargo executable is unavailable for metadata validation")
        version_process = subprocess.run(
            [cargo, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if version_process.returncode != 0 or not version_process.stdout.startswith(
            f"cargo {expected_version} "
        ):
            raise PackageManagerError(
                f"Cargo metadata executable does not match locked version {expected_version}"
            )
        with tempfile.TemporaryDirectory(prefix="nl2repo-cargo-home-") as cargo_home:
            with tempfile.TemporaryDirectory(prefix="nl2repo-cargo-metadata-") as metadata_root:
                metadata_root_path = Path(metadata_root)
                manifest_path = bundle_root / "Cargo.toml"
                if not (bundle_root / "src").is_dir() and not (
                    bundle_root / "src/lib.rs"
                ).is_file():
                    # Dependency bundles describe a package graph, not the candidate
                    # implementation. Supply a throwaway target so Cargo can parse
                    # and resolve the graph without changing the checked artifact.
                    shutil.copy2(manifest_path, metadata_root_path / "Cargo.toml")
                    shutil.copy2(bundle_root / "Cargo.lock", metadata_root_path / "Cargo.lock")
                    (metadata_root_path / "src").mkdir()
                    (metadata_root_path / "src/lib.rs").write_text(
                        "#![allow(dead_code)]\n", encoding="utf-8"
                    )
                    manifest_path = metadata_root_path / "Cargo.toml"
                command = [
                    cargo,
                    "metadata",
                    "--format-version",
                    "1",
                    "--locked",
                    "--offline",
                    "--manifest-path",
                    str(manifest_path),
                    "--config",
                    'source.crates-io.replace-with="vendored-sources"',
                    "--config",
                    f'source.vendored-sources.directory="{bundle_root / "vendor"}"',
                ]
                try:
                    completed = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        check=False,
                        env={
                            "CARGO_HOME": cargo_home,
                            "CARGO_NET_OFFLINE": "true",
                            "CARGO_TERM_COLOR": "never",
                            "HOME": cargo_home,
                            "PATH": str(Path(cargo).parent),
                        },
                    )
                except (OSError, subprocess.SubprocessError) as exc:
                    raise PackageManagerError(
                        f"Cargo metadata validation failed: {exc}"
                    ) from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()[-2000:]
            raise PackageManagerError(f"Cargo metadata validation failed: {detail}")
        try:
            metadata = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise PackageManagerError(f"Cargo metadata output is invalid JSON: {exc}") from exc
        packages = metadata.get("packages") if isinstance(metadata, Mapping) else None
        if not isinstance(packages, list) or len(packages) != expected_package_count:
            count = len(packages) if isinstance(packages, list) else "invalid"
            raise PackageManagerError(
                f"Cargo metadata package count {count} does not match lock {expected_package_count}"
            )
        metadata_names: list[str] = []
        metadata_packages: set[tuple[str, str, str | None]] = set()
        for package in packages:
            if not isinstance(package, Mapping):
                raise PackageManagerError("Cargo metadata package entry is malformed")
            name = package.get("name")
            if not isinstance(name, str):
                raise PackageManagerError("Cargo metadata package names are malformed")
            metadata_names.append(name)
            source = package.get("source")
            if source is not None and source != CRATES_IO_SOURCE:
                raise PackageManagerError("Cargo metadata contains a non-crates.io source")
            package_version = package.get("version")
            manifest_path_value = package.get("manifest_path")
            targets = package.get("targets")
            if (
                not isinstance(package_version, str)
                or not isinstance(manifest_path_value, str)
                or not isinstance(targets, list)
            ):
                raise PackageManagerError("Cargo metadata package fields are malformed")
            identity = (name, package_version, source)
            if identity in metadata_packages:
                raise PackageManagerError("Cargo metadata package identity is duplicated")
            metadata_packages.add(identity)
            package_root = Path(manifest_path_value).resolve().parent
            for target in targets:
                if not isinstance(target, Mapping):
                    raise PackageManagerError("Cargo metadata target is malformed")
                kinds = target.get("kind")
                source_path = target.get("src_path")
                if not isinstance(kinds, list) or not isinstance(source_path, str):
                    raise PackageManagerError("Cargo metadata target fields are malformed")
                if "custom-build" in kinds and not Path(source_path).resolve().is_relative_to(
                    package_root
                ):
                    raise PackageManagerError("Cargo build script target escapes its package")
        if Counter(metadata_names) != Counter(expected_package_names):
            raise PackageManagerError(
                "Cargo metadata package names do not match Cargo.lock"
            )
        if metadata_packages != expected_packages:
            raise PackageManagerError(
                "Cargo metadata package identities do not match Cargo.lock"
            )

    def install_command(self, *, store_dir: str) -> tuple[str, ...]:
        return (
            "/usr/local/cargo/bin/cargo",
            "test",
            "--locked",
            "--offline",
            "--manifest-path",
            f"{store_dir}/Cargo.toml",
        )


__all__ = ["CargoPackageManager"]
