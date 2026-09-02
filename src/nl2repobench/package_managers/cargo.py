"""Cargo lock, vendor store, and offline command policy for Rust R0."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import tomllib
import unicodedata
from pathlib import Path, PurePosixPath
from typing import IO

from nl2repobench.domain.canonical_contract import (
    PackageManager,
    RuntimeLanguage,
    RuntimeProfile,
)
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.runtimes.rust import SELECTED_TARGET, cargo_feature_args
from nl2repobench.storage.canonical_ustar import encode_tree, tree_digest, tree_entries
from nl2repobench.verification.rust_profile import RustProfile

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
CARGO_TOOLCHAIN_VERSIONS = frozenset({"1.100.0-nightly", "1.97.1"})
CARGO_OFFLINE_SMOKE_COMMAND_ID = "cargo-metadata-frozen-offline-v1"
CRATES_IO_SOURCE = "registry+https://github.com/rust-lang/crates.io-index"
MAX_LOCK_BYTES = 16 * 1024 * 1024
MAX_CRATE_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_CRATE_MEMBERS = 10_000
MAX_CRATE_MEMBER_BYTES = 64 * 1024 * 1024
MAX_CRATE_TOTAL_BYTES = 512 * 1024 * 1024
MAX_CRATE_PATH_BYTES = 255
MAX_CRATE_READ_BYTES = 1024 * 1024
MAX_CRATE_TRAILING_BYTES = 1024 * 1024
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
        # Only an omitted `source` key marks the workspace root. A present value must
        # be a string so a malformed source can never be conflated with the root.
        if "source" in package:
            source = package["source"]
            if not isinstance(source, str):
                raise _error(
                    f"Cargo.lock package {name} has a malformed source: expected a string"
                )
        else:
            source = None
        if "checksum" in package:
            checksum = package["checksum"]
            if not isinstance(checksum, str):
                raise _error(
                    f"Cargo.lock package {name} has a malformed checksum: expected a string"
                )
        else:
            checksum = None
        identity = (name, version, source)
        if identity in identities:
            raise _error(f"Cargo.lock contains duplicate package {name} {version}")
        identities.add(identity)
        package_order.append(
            (
                name.encode("utf-8"),
                version.encode("utf-8"),
                (source or "").encode("utf-8"),
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
        if checksum is None or not _CHECKSUM.fullmatch(checksum):
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


def _profile_features(profile: object) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    if not isinstance(profile, RustProfile):
        raise _error(
            "Cargo build profile must be a validated RustProfile",
            PackageManagerErrorCode.UNSUPPORTED_PROFILE,
            stage="build",
        )
    try:
        return (
            profile.target.triple,
            profile.package.binaries,
            cargo_feature_args(profile.features.default_features, profile.features.enabled),
        )
    except ValueError as exc:
        raise _error(
            str(exc), PackageManagerErrorCode.UNSUPPORTED_PROFILE, stage="build"
        ) from exc


def _validate_runtime_profile(runtime_profile: RuntimeProfile | None, *, stage: str) -> None:
    """Accept only the pinned rust+cargo profile the canonical materializer passes."""

    if runtime_profile is None:
        return
    if (
        not isinstance(runtime_profile, RuntimeProfile)
        or runtime_profile.language is not RuntimeLanguage.RUST
        or runtime_profile.runtime != "rust"
        or runtime_profile.package_manager is not PackageManager.CARGO
        or runtime_profile.version not in CARGO_TOOLCHAIN_VERSIONS
        or runtime_profile.package_manager_version != runtime_profile.version
    ):
        raise _error(
            "Cargo validation requires a rust+cargo runtime profile pinned to "
            f"{CARGO_TOOLCHAIN_VERSION}",
            PackageManagerErrorCode.TOOLCHAIN_MISMATCH,
            stage=stage,
        )


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


def _validate_canonical_inventory_section(
    inventory: object, name: str, root: Path, archive_digest: str
) -> None:
    """Check one section against the canonical dependency contract."""

    if not isinstance(inventory, dict) or set(inventory) != {
        "archive_kind",
        "archive_digest",
        "tree_digest",
        "entries",
        "file_count",
        "directory_count",
        "total_bytes",
    }:
        raise _error(
            f"Cargo {name} inventory section is malformed",
            PackageManagerErrorCode.INVENTORY_MISMATCH,
            stage="store",
        )
    entries = tree_entries(root)
    expected = [
        {
            "path": entry.path,
            "type": entry.type,
            "mode": entry.mode,
            "size": entry.size,
            "sha256": entry.sha256,
        }
        for entry in entries
    ]
    if (
        inventory["archive_kind"] != name
        or inventory["archive_digest"] != archive_digest
        or inventory["entries"] != expected
        or inventory["tree_digest"] != tree_digest(entries)
        or inventory["file_count"] != sum(entry.type == "file" for entry in entries)
        or inventory["directory_count"] != sum(entry.type == "directory" for entry in entries)
        or inventory["total_bytes"] != sum(entry.size for entry in entries)
    ):
        raise _error(
            f"Cargo {name} inventory does not match canonical dependency contract",
            PackageManagerErrorCode.INVENTORY_MISMATCH,
            stage="store",
        )


def _read_exact(stream: gzip.GzipFile, size: int, description: str) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = stream.read(min(remaining, MAX_CRATE_READ_BYTES))
        if not chunk:
            raise ValueError(f"crate archive is truncated while reading {description}")
        if len(chunk) > MAX_CRATE_READ_BYTES:
            raise ValueError("crate archive read exceeds the read ceiling")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _tar_octal(field: bytes, description: str) -> int:
    value = field.rstrip(b"\0 ").lstrip(b" ")
    if not value:
        return 0
    if any(byte not in b"01234567" for byte in value):
        raise ValueError(f"crate archive has invalid {description}")
    return int(value, 8)


def _tar_member_path(header: bytes) -> str:
    name = header[:100].split(b"\0", 1)[0]
    prefix = header[345:500].split(b"\0", 1)[0]
    raw = prefix + (b"/" if prefix and name else b"") + name
    if len(raw) > MAX_CRATE_PATH_BYTES:
        raise ValueError("crate archive member path exceeds size limit")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("crate archive member path is not UTF-8") from exc


def _read_crate_archive(path: Path, *, expected_root: str) -> dict[str, str]:
    """Read a bounded ustar-compatible .crate without tar metadata expansion."""

    try:
        if path.is_symlink() or not path.is_file():
            raise ValueError("crate archive is not a regular file")
        if path.stat().st_size > MAX_CRATE_ARCHIVE_BYTES:
            raise ValueError("crate archive exceeds compressed size limit")
        files: dict[str, str] = {}
        seen: set[str] = set()
        member_count = 0
        expanded_total = 0
        with path.open("rb") as compressed, gzip.GzipFile(fileobj=compressed) as archive:
            while True:
                header = _read_exact(archive, 512, "member header")
                if header == bytes(512):
                    if _read_exact(archive, 512, "end marker") != bytes(512):
                        raise ValueError("crate archive has an invalid end marker")
                    trailing_total = 0
                    while chunk := archive.read(MAX_CRATE_READ_BYTES):
                        if len(chunk) > MAX_CRATE_READ_BYTES:
                            raise ValueError("crate archive read exceeds the read ceiling")
                        trailing_total += len(chunk)
                        if (
                            trailing_total > MAX_CRATE_TRAILING_BYTES
                            or any(byte != 0 for byte in chunk)
                        ):
                            raise ValueError("crate archive has excessive or nonzero trailing data")
                    break
                recorded_checksum = _tar_octal(header[148:156], "header checksum")
                checksum_header = header[:148] + b" " * 8 + header[156:]
                if recorded_checksum != sum(checksum_header):
                    raise ValueError("crate archive member checksum is invalid")
                member_count += 1
                if member_count > MAX_CRATE_MEMBERS:
                    raise ValueError("crate archive contains too many members")
                type_flag = header[156:157]
                if type_flag in {b"g", b"x", b"L", b"K"}:
                    raise ValueError(
                        "crate archive extension metadata is forbidden before expansion"
                    )
                if type_flag not in {b"\0", b"0", b"5"}:
                    raise ValueError("crate archive member is not regular or a directory")
                member_size = _tar_octal(header[124:136], "member size")
                is_directory = type_flag == b"5"
                if is_directory and member_size != 0:
                    raise ValueError("crate archive directory has a nonzero size")
                if member_size > MAX_CRATE_MEMBER_BYTES:
                    raise ValueError("crate archive member exceeds size limit")
                if expanded_total + member_size > MAX_CRATE_TOTAL_BYTES:
                    raise ValueError("crate archive expanded size exceeds total limit")
                raw = _tar_member_path(header).removesuffix("/")
                raw_parts = raw.split("/")
                if any(part in {"", ".", ".."} for part in raw_parts):
                    raise ValueError(f"unsafe archive member: {raw}")
                member_path = PurePosixPath(raw)
                if (
                    not raw
                    or member_path.is_absolute()
                    or not member_path.parts
                    or member_path.parts[0] != expected_root
                    or unicodedata.normalize("NFC", raw) != raw
                ):
                    raise ValueError(f"unsafe archive member: {raw}")
                relative = PurePosixPath(*member_path.parts[1:]).as_posix()
                if not relative:
                    if not is_directory or relative in seen:
                        raise ValueError("duplicate or invalid crate archive root")
                    seen.add(relative)
                elif relative in seen:
                    raise ValueError(f"duplicate archive member: {relative}")
                else:
                    seen.add(relative)

                digest = hashlib.sha256()
                remaining = member_size
                while remaining:
                    chunk = archive.read(min(remaining, MAX_CRATE_READ_BYTES))
                    if not chunk:
                        raise ValueError(f"crate archive member is truncated: {relative}")
                    if len(chunk) > MAX_CRATE_READ_BYTES or len(chunk) > remaining:
                        raise ValueError(
                            f"crate archive member read exceeds size limit: {relative}"
                        )
                    digest.update(chunk)
                    remaining -= len(chunk)
                padding_size = (-member_size) % 512
                if padding_size and any(
                    _read_exact(archive, padding_size, "member padding")
                ):
                    raise ValueError("crate archive member padding is nonzero")
                expanded_total += member_size
                if relative and not is_directory:
                    files[relative] = digest.hexdigest()
    except (EOFError, OSError, ValueError) as exc:
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

    def validate_lock(
        self,
        lock_root: Path,
        expected_toolchain: str,
        *,
        runtime_profile: RuntimeProfile | None = None,
    ) -> LockSummary:
        _validate_runtime_profile(runtime_profile, stage="lock")
        if expected_toolchain not in CARGO_TOOLCHAIN_VERSIONS:
            raise _error(
                "Cargo toolchain must use a supported exact release profile",
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
        *,
        runtime_profile: RuntimeProfile | None = None,
    ) -> StoreSummary:
        _validate_runtime_profile(runtime_profile, stage="store")
        # The generic dependency contract materializes sibling ``lock`` and
        # ``store`` roots and supplies the inventory, so route it through the
        # same strict Cargo validator used by the compiler-specific path.
        if not isinstance(inventory, dict):
            raise _error(
                "Cargo external inventory must be an object",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        toolchain_digest = inventory.get("toolchain_digest")
        if not isinstance(toolchain_digest, str) or not re.fullmatch(
            r"sha256:[0-9a-f]{64}", toolchain_digest
        ):
            raise _error(
                "Cargo inventory toolchain digest is malformed",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        lock_root = store_root.parent / "lock"
        if lock_root.resolve() == store_root.resolve():
            raise _error(
                "Cargo lock and store roots must be separate",
                PackageManagerErrorCode.STORE_MALFORMED,
                stage="store",
            )
        return self.validate_frozen_offline_store(
            store_root,
            lock_summary,
            inventory,
            expected_toolchain,
            expected_toolchain_digest=toolchain_digest,
            lock_root=lock_root,
        )

    def validate_frozen_offline_store(
        self,
        store_root: Path,
        lock_summary: LockSummary,
        inventory: object,
        expected_toolchain: str,
        *,
        expected_toolchain_digest: str,
        lock_root: Path,
    ) -> StoreSummary:
        if (
            lock_summary.identity != self.identity
            or lock_summary.toolchain_version != expected_toolchain
            or expected_toolchain not in CARGO_TOOLCHAIN_VERSIONS
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
            inventory.get("schema_version") != "1.0"
            or inventory.get("identity") != "rust+cargo"
            or inventory.get("adapter_version") != CARGO_ADAPTER_VERSION
            or inventory.get("offline_smoke")
            != {"status": "passed", "command_id": CARGO_OFFLINE_SMOKE_COMMAND_ID}
            or not isinstance(toolchain_digest, str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", toolchain_digest)
            or toolchain_digest != expected_toolchain_digest
        ):
            raise _error(
                "Cargo inventory identity or locked toolchain digest does not match",
                PackageManagerErrorCode.INVENTORY_MISMATCH,
                stage="store",
            )
        try:
            lock_inventory = inventory.get("lock")
            _validate_canonical_inventory_section(
                lock_inventory,
                "dependency-lock",
                lock_root,
                f"sha256:{hashlib.sha256(encode_tree(lock_root)).hexdigest()}",
            )
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
            _validate_canonical_inventory_section(
                inventory.get("store"),
                "offline-store",
                store_root,
                f"sha256:{hashlib.sha256(encode_tree(store_root)).hexdigest()}",
            )
            expected_store_digest = (
                f"sha256:{hashlib.sha256(encode_tree(store_root)).hexdigest()}"
            )
            if result.store_digest != expected_store_digest:
                raise _error(
                    "Cargo store archive digest does not match canonical archive bytes",
                    PackageManagerErrorCode.INVENTORY_MISMATCH,
                    stage="store",
                )
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
        target, binaries, feature_args = _profile_features(profile)
        selectors = ("--lib",) + tuple(
            item for name in binaries for item in ("--bin", name)
        )
        return (
            CommandSpec(
                (
                    "/opt/rust/bin/cargo",
                    "build",
                    *_OFFLINE_ARGS[:3],
                    "--target",
                    target,
                    *_OFFLINE_ARGS[5:],
                    *selectors,
                    *feature_args,
                ),
                ".",
                _OFFLINE_ENVIRONMENT,
                600,
            ),
        )

    def offline_environment(self, profile: object) -> dict[str, str]:
        _profile_features(profile)
        return dict(_OFFLINE_ENVIRONMENT)


__all__ = ["CARGO_OFFLINE_SMOKE_COMMAND_ID", "CargoPackageManager"]
