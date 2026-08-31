"""Cargo lock, vendor store, and offline command policy for Rust R0."""

from __future__ import annotations

import hashlib
import json
import re
import tarfile
import tomllib
import unicodedata
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import IO

from nl2repobench.domain.canonical_contract import PackageManager, RuntimeLanguage
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.runtimes.rust import SELECTED_TARGET, cargo_feature_args
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

CARGO_IDENTITY = RuntimeDiscriminator(
    language=RuntimeLanguage.RUST,
    package_manager=PackageManager.CARGO,
)
CARGO_ADAPTER_VERSION = "cargo-package-manager-v1"
CARGO_TOOLCHAIN_VERSION = "1.100.0-nightly"
CARGO_OFFLINE_SMOKE_COMMAND_ID = "cargo-metadata-frozen-offline-v1"
CRATES_IO_SOURCE = "registry+https://github.com/rust-lang/crates.io-index"
MAX_LOCK_BYTES = 16 * 1024 * 1024
_SEMVER = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
_CHECKSUM = re.compile(r"^[0-9a-f]{64}$")
_PACKAGE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_DEPENDENCY_REFERENCE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9_-]*)"
    r"(?: (?P<version>[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?))?"
    r"(?: \((?P<source>[^()]+)\))?$"
)

_OFFLINE_ENVIRONMENT = (
    ("PATH", "/opt/rust/bin:/usr/local/bin:/usr/bin:/bin"),
    ("HOME", "/tmp/nl2repo-cargo-home"),
    ("CARGO_HOME", "/tmp/nl2repo-cargo-home"),
    ("CARGO_NET_OFFLINE", "true"),
    ("CARGO_INCREMENTAL", "0"),
    ("CARGO_TERM_COLOR", "never"),
    ("LC_ALL", "C.UTF-8"),
    ("TZ", "UTC"),
    ("TMPDIR", "/tmp/nl2repo-cargo-tmp"),
    ("RUST_BACKTRACE", "0"),
)
_OFFLINE_ARGS = (
    "--locked",
    "--offline",
    "--frozen",
    "--target",
    SELECTED_TARGET,
    "--config",
    "net.offline=true",
    "--config",
    'source.crates-io.replace-with="vendored-sources"',
    "--config",
    'source.vendored-sources.directory="/opt/nl2repobench-cargo/vendor"',
)


def _error(
    message: str,
    code: PackageManagerErrorCode = PackageManagerErrorCode.LOCK_MALFORMED,
    *,
    stage: str = "lock",
) -> PackageManagerError:
    return PackageManagerError(code, CARGO_IDENTITY, stage, message)


def _lock_bytes(lock_root: Path) -> bytes:
    lock_path = lock_root / "Cargo.lock"
    if (
        lock_root.is_symlink()
        or not lock_root.is_dir()
        or lock_path.is_symlink()
        or not lock_path.is_file()
    ):
        raise _error("Cargo.lock is missing", PackageManagerErrorCode.LOCK_MISSING)
    files = tuple(path.name for path in lock_root.iterdir())
    if files != ("Cargo.lock",):
        extras = ", ".join(sorted(set(files) - {"Cargo.lock"}))
        raise _error(f"Cargo lock root contains unexpected entries: {extras}")
    if lock_path.stat().st_size > MAX_LOCK_BYTES:
        raise _error("Cargo.lock exceeds the size limit")
    try:
        return lock_path.read_bytes()
    except OSError as exc:
        raise _error(f"cannot read Cargo.lock: {exc}") from exc


def _parse_lock(data: bytes) -> tuple[ResolvedPackage, ...]:
    try:
        parsed = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise _error(f"cannot parse Cargo.lock: {exc}") from exc
    if set(parsed) != {"version", "package"} or parsed.get("version") != 4:
        raise _error("Cargo.lock must contain only lock version 4 and packages")
    packages = parsed.get("package")
    if not isinstance(packages, list) or not packages:
        raise _error("Cargo.lock must contain at least one package")

    result: list[ResolvedPackage] = []
    identities: set[tuple[str, str, str | None]] = set()
    package_order: list[tuple[bytes, bytes, bytes]] = []
    source_less = 0
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise _error(f"Cargo.lock package {index} is not a table")
        allowed = {"name", "version", "source", "checksum", "dependencies"}
        if not set(package).issubset(allowed) or not {"name", "version"}.issubset(package):
            raise _error(f"Cargo.lock package {index} has invalid fields")
        name = package["name"]
        version = package["version"]
        source = package.get("source")
        checksum = package.get("checksum")
        dependencies = package.get("dependencies", [])
        if not isinstance(name, str) or not _PACKAGE_NAME.fullmatch(name):
            raise _error(f"Cargo.lock package {index} has an invalid name")
        if not isinstance(version, str) or not _SEMVER.fullmatch(version):
            raise _error(f"Cargo.lock package {name} has a non-exact version")
        if not isinstance(dependencies, list) or any(
            not isinstance(item, str) or not item for item in dependencies
        ):
            raise _error(f"Cargo.lock package {name} has malformed dependencies")
        dependency_order = [item.encode("utf-8") for item in dependencies]
        if dependency_order != sorted(dependency_order) or len(dependencies) != len(
            set(dependencies)
        ):
            raise _error(f"Cargo.lock package {name} dependencies must be sorted and unique")
        identity = (name, version, source if isinstance(source, str) else None)
        if identity in identities:
            raise _error(f"Cargo.lock contains duplicate package {name} {version}")
        identities.add(identity)
        package_order.append(
            (
                name.encode("utf-8"),
                version.encode("utf-8"),
                (source or "").encode("utf-8") if isinstance(source, str) else b"",
            )
        )
        if source is None:
            source_less += 1
            if checksum is not None:
                raise _error(f"source-less Cargo package {name} cannot have a checksum")
            result.append(ResolvedPackage(name, version, "cargo-root"))
            continue
        if source != CRATES_IO_SOURCE:
            raise _error(f"Cargo package {name} uses a forbidden registry source")
        if not isinstance(checksum, str) or not _CHECKSUM.fullmatch(checksum):
            raise _error(f"Cargo package {name} requires a lowercase SHA-256 checksum")
        result.append(
            ResolvedPackage(name, version, "cargo-registry", f"sha256:{checksum}")
        )
    if source_less != 1:
        raise _error("single-package Cargo.lock must contain exactly one source-less root")
    if package_order != sorted(package_order):
        raise _error("Cargo.lock packages must be sorted by name, version, and source")
    lock_identities = tuple(identities)
    for package in packages:
        for dependency in package.get("dependencies", []):
            match = _DEPENDENCY_REFERENCE.fullmatch(dependency)
            if match is None:
                raise _error(f"Cargo.lock dependency does not resolve: {dependency}")
            name = match.group("name")
            version = match.group("version")
            source = match.group("source")
            matches = tuple(
                identity
                for identity in lock_identities
                if identity[0] == name
                and (version is None or identity[1] == version)
                and (source is None or identity[2] == source)
            )
            if len(matches) != 1:
                raise _error(f"Cargo.lock dependency does not resolve exactly: {dependency}")
    return tuple(result)


def _profile_features(profile: object) -> tuple[bool, tuple[str, ...]]:
    if isinstance(profile, Mapping):
        if set(profile) != {"default_features", "enabled"}:
            raise _error(
                "Cargo build profile must contain default_features and enabled",
                PackageManagerErrorCode.UNSUPPORTED_PROFILE,
                stage="build",
            )
        default_features = profile["default_features"]
        enabled = profile["enabled"]
    else:
        default_features = getattr(profile, "default_features", None)
        enabled = getattr(profile, "enabled", None)
    if not isinstance(default_features, bool) or not isinstance(enabled, tuple):
        raise _error(
            "Cargo build profile has invalid feature fields",
            PackageManagerErrorCode.UNSUPPORTED_PROFILE,
            stage="build",
        )
    try:
        return default_features, cargo_feature_args(default_features, enabled)
    except ValueError as exc:
        raise _error(
            str(exc), PackageManagerErrorCode.UNSUPPORTED_PROFILE, stage="build"
        ) from exc


def _validate_cargo_store(store_root: Path, lock_summary: LockSummary) -> None:
    vendor_root = store_root / "vendor"
    cache_root = store_root / "registry" / "cache"
    index_root = store_root / "registry" / "index"
    for path, description in (
        (vendor_root, "vendor root"),
        (cache_root, "crate archive cache"),
        (index_root, "registry index snapshot"),
    ):
        if path.is_symlink() or not path.is_dir() or not any(path.iterdir()):
            raise _error(
                f"Cargo {description} is missing or empty",
                PackageManagerErrorCode.STORE_MALFORMED,
                stage="store",
            )

    if {path.name for path in store_root.iterdir()} != {"registry", "vendor"}:
        raise _error(
            "Cargo store must contain exactly registry and vendor roots",
            PackageManagerErrorCode.STORE_MALFORMED,
            stage="store",
        )
    registry_root = store_root / "registry"
    if {path.name for path in registry_root.iterdir()} != {"cache", "index"}:
        raise _error(
            "Cargo registry store must contain exactly cache and index roots",
            PackageManagerErrorCode.STORE_MALFORMED,
            stage="store",
        )

    for path in store_root.rglob("*"):
        relative = path.relative_to(store_root).as_posix()
        if unicodedata.normalize("NFC", relative) != relative:
            raise _error(
                f"Cargo store path is not NFC: {relative}",
                PackageManagerErrorCode.STORE_MALFORMED,
                stage="store",
            )

    registry_packages = tuple(
        package for package in lock_summary.resolved if package.kind == "cargo-registry"
    )
    expected_names = {f"{package.name}-{package.version}" for package in registry_packages}
    actual_vendor_names = {
        path.name for path in vendor_root.iterdir() if path.is_dir() and not path.is_symlink()
    }
    if actual_vendor_names != expected_names:
        raise _error(
            "Cargo vendor package inventory does not match Cargo.lock",
            PackageManagerErrorCode.INVENTORY_MISMATCH,
            stage="store",
        )
    actual_archives = {path.name for path in cache_root.rglob("*.crate") if path.is_file()}
    expected_archives = {
        f"{package.name}-{package.version}.crate" for package in registry_packages
    }
    if actual_archives != expected_archives:
        raise _error(
            "Cargo crate archive inventory does not match Cargo.lock",
            PackageManagerErrorCode.INVENTORY_MISMATCH,
            stage="store",
        )

    for package in registry_packages:
        if package.kind != "cargo-registry":
            continue
        checksum = (package.artifact_digest or "").removeprefix("sha256:")
        archive_name = f"{package.name}-{package.version}.crate"
        archives = tuple(cache_root.rglob(archive_name))
        if len(archives) != 1 or archives[0].is_symlink() or not archives[0].is_file():
            raise _error(
                f"Cargo crate archive is missing or duplicated: {archive_name}",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        actual = _sha256_file(archives[0])
        if actual != checksum:
            raise _error(
                f"Cargo crate archive checksum does not match lock: {archive_name}",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        archive_files = _read_crate_archive(
            archives[0], expected_root=f"{package.name}-{package.version}"
        )
        vendor = vendor_root / f"{package.name}-{package.version}"
        checksum_path = vendor / ".cargo-checksum.json"
        if checksum_path.is_symlink() or not checksum_path.is_file():
            raise _error(
                f"Cargo vendor checksum is missing: {package.name}-{package.version}",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        try:
            checksum_data = json.loads(checksum_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise _error(
                f"Cargo vendor checksum is malformed: {package.name}-{package.version}",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            ) from exc
        if (
            not isinstance(checksum_data, dict)
            or set(checksum_data) != {"files", "package"}
            or not isinstance(checksum_data["files"], dict)
            or checksum_data["package"] != checksum
        ):
            raise _error(
                f"Cargo vendor checksum does not match lock: {package.name}-{package.version}",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        expected_vendor_files = {
            path.relative_to(vendor).as_posix()
            for path in vendor.rglob("*")
            if path.is_file() and path.name != ".cargo-checksum.json"
        }
        if set(checksum_data["files"]) != expected_vendor_files:
            raise _error(
                f"Cargo vendor file inventory does not match: {package.name}-{package.version}",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        if set(archive_files) != expected_vendor_files:
            raise _error(
                f"Cargo vendor tree does not match crate archive: {package.name}-{package.version}",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        for relative, expected in checksum_data["files"].items():
            if not isinstance(relative, str) or not isinstance(expected, str):
                raise _error(
                    "Cargo vendor file inventory is malformed",
                    PackageManagerErrorCode.INVENTORY_MISMATCH,
                    stage="store",
                )
            path = vendor / relative
            if (
                path.is_symlink()
                or not path.is_file()
                or not path.resolve().is_relative_to(vendor.resolve())
                or _sha256_file(path) != expected
            ):
                raise _error(
                    f"Cargo vendor file checksum mismatch: {relative}",
                    PackageManagerErrorCode.INVENTORY_MISMATCH,
                    stage="store",
                )
            if archive_files[relative] != _sha256_file(path):
                raise _error(
                    f"Cargo vendor file differs from crate archive: {relative}",
                    PackageManagerErrorCode.INVENTORY_MISMATCH,
                    stage="store",
                )


def _read_crate_archive(path: Path, *, expected_root: str) -> dict[str, str]:
    """Read one checksum-verified .crate without extracting it to the host."""

    try:
        with tarfile.open(path, mode="r:gz") as archive:
            files: dict[str, str] = {}
            seen: set[str] = set()
            for member in archive.getmembers():
                raw = member.name.removesuffix("/")
                member_path = PurePosixPath(raw)
                if (
                    not raw
                    or member_path.is_absolute()
                    or ".." in member_path.parts
                    or not member_path.parts
                    or member_path.parts[0] != expected_root
                    or unicodedata.normalize("NFC", raw) != raw
                ):
                    raise ValueError(f"unsafe archive member: {member.name}")
                relative = PurePosixPath(*member_path.parts[1:]).as_posix()
                if not relative or relative in seen:
                    if relative in seen:
                        raise ValueError(f"duplicate archive member: {relative}")
                    if not member.isdir():
                        raise ValueError("crate archive root must be a directory")
                    continue
                seen.add(relative)
                if member.isdir():
                    continue
                if not member.isreg():
                    raise ValueError(f"crate archive member is not regular: {relative}")
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise ValueError(f"cannot read crate archive member: {relative}")
                files[relative] = _sha256_stream(extracted)
    except (OSError, tarfile.TarError, ValueError) as exc:
        raise _error(
            f"Cargo crate archive is malformed: {path.name}: {exc}",
            PackageManagerErrorCode.STORE_MALFORMED,
            stage="store",
        ) from exc
    return files


def _sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return _sha256_stream(stream)


def _sha256_stream(stream: IO[bytes]) -> str:
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


class CargoPackageManager:
    """Typed Cargo implementation of the existing package-manager protocol."""

    identity = CARGO_IDENTITY
    lockfile_names = ("Cargo.lock",)

    def validate_lock(self, lock_root: Path, expected_toolchain: str) -> LockSummary:
        if expected_toolchain != CARGO_TOOLCHAIN_VERSION:
            raise _error(
                f"Cargo toolchain must be exactly {CARGO_TOOLCHAIN_VERSION}",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
            )
        data = _lock_bytes(lock_root)
        resolved = _parse_lock(data)
        return LockSummary(
            identity=self.identity,
            toolchain_version=expected_toolchain,
            lockfile_names=self.lockfile_names,
            lock_digest=f"sha256:{hashlib.sha256(encode_tree(lock_root)).hexdigest()}",
            resolved=resolved,
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
            or expected_toolchain != CARGO_TOOLCHAIN_VERSION
        ):
            raise _error(
                "Cargo lock and store toolchains do not match",
                PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
                stage="store",
            )
        if not isinstance(inventory, dict):
            raise _error(
                "Cargo external inventory must be an object",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        toolchain_digest = inventory.get("toolchain_digest")
        if (
            inventory.get("adapter_version") != CARGO_ADAPTER_VERSION
            or inventory.get("lock") != {"digest": lock_summary.lock_digest}
            or inventory.get("offline_smoke")
            != {"status": "passed", "command_id": CARGO_OFFLINE_SMOKE_COMMAND_ID}
            or not isinstance(toolchain_digest, str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", toolchain_digest)
        ):
            raise _error(
                "Cargo inventory adapter or lock digest does not match",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        try:
            result = inventory_store_summary(
                identity=self.identity,
                store_root=store_root,
                inventory=inventory,
            )
            if result.file_count > 100_000:
                raise _error(
                    "Cargo store exceeds the file-count limit",
                    PackageManagerErrorCode.STORE_MALFORMED,
                    stage="store",
                )
            _validate_cargo_store(store_root, lock_summary)
        except PackageManagerError:
            raise
        except (OSError, ValueError) as exc:
            raise _error(
                f"Cargo store is malformed: {exc}",
                PackageManagerErrorCode.STORE_MALFORMED,
                stage="store",
            ) from exc
        return result

    def build_commands(self, profile: object) -> tuple[CommandSpec, ...]:
        _, feature_args = _profile_features(profile)
        return (
            CommandSpec(
                ("/opt/rust/bin/cargo", "build", *_OFFLINE_ARGS, *feature_args),
                ".",
                _OFFLINE_ENVIRONMENT,
                600,
            ),
        )

    def offline_environment(self, profile: object) -> dict[str, str]:
        _profile_features(profile)
        return dict(_OFFLINE_ENVIRONMENT)


__all__ = ["CARGO_OFFLINE_SMOKE_COMMAND_ID", "CargoPackageManager"]
