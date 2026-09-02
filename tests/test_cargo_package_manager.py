from __future__ import annotations

import hashlib
import inspect
import io
import json
import tarfile
from pathlib import Path

import pytest

import nl2repobench.package_managers.cargo as cargo_module
from nl2repobench.domain.canonical_contract import (
    PackageManager,
    RuntimeLanguage,
    RuntimeProfile,
)
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.package_managers import (
    CargoPackageManager,
    PackageManagerAdapter,
    PackageManagerError,
    PackageManagerErrorCode,
    PackageManagerRegistry,
)
from nl2repobench.storage.canonical_ustar import encode_tree, tree_digest, tree_entries
from nl2repobench.verification.rust_profile import load_rust_profile

CARGO_LOCK = '''version = 4

[[package]]
name = "demo"
version = "1.0.0"
dependencies = [
 "itoa",
]

[[package]]
name = "itoa"
version = "1.0.15"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "4a5f13b858c8d314ee3e8f639011f7ccefe71f97f96e50151fb991f267928e2c"
'''
CRATES_IO_SOURCE_LINE = 'source = "registry+https://github.com/rust-lang/crates.io-index"'
CHECKSUM_LINE = 'checksum = "4a5f13b858c8d314ee3e8f639011f7ccefe71f97f96e50151fb991f267928e2c"'
ROOT_PACKAGE_BLOCK = 'name = "demo"\nversion = "1.0.0"\ndependencies = ['

PROFILE = '''schema_version = "1.0"
[package]
name = "demo"
version = "1.0.0"
edition = "2021"
library_path = "src/lib.rs"
binaries = ["demo", "zeta"]
[target]
triple = "x86_64-unknown-linux-gnu"
[features]
default_features = false
enabled = ["std"]
[features.declarations]
std = []
[[candidate_dependencies]]
name = "itoa"
version = "1.0.15"
default_features = false
features = []
[bridge]
api_plan_digest = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
max_operations_per_request = 64
max_state_handles = 32
max_state_bytes = 8388608
unsafe_api_ids = []
[[cli]]
profile_id = "demo-cli"
binary_name = "demo"
argv_max_items = 64
stdin_max_bytes = 1048576
max_output_bytes = 8388608
tempdir_policy = "none"
tempdir_max_entries = 0
tempdir_max_bytes = 0
tempdir_max_file_bytes = 0
cli_timeout_sec = 120.0
expected_exit_codes = [0]
[limits]
build_timeout_sec = 600
leaf_timeout_sec = 120
cpu_sec = 120
max_stdin_bytes = 1048576
max_output_bytes = 8388608
max_file_bytes = 536870912
max_open_files = 256
max_processes = 64
'''


def _crate_archive(root: str, files: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        directory = tarfile.TarInfo(f"{root}/")
        directory.type = tarfile.DIRTYPE
        directory.mode = 0o755
        archive.addfile(directory)
        for relative, content in sorted(files.items()):
            info = tarfile.TarInfo(f"{root}/{relative}")
            info.size = len(content)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(content))
    return output.getvalue()


def _identity() -> RuntimeDiscriminator:
    return RuntimeDiscriminator(
        language=RuntimeLanguage.RUST,
        package_manager=PackageManager.CARGO,
    )


def _root_package_with(*extra_lines: str) -> str:
    """Return the root package block with extra lock keys inserted in order."""
    head, tail = ROOT_PACKAGE_BLOCK.split("dependencies = [")
    return head + "".join(f"{line}\n" for line in extra_lines) + "dependencies = [" + tail


def _inventory_section(name: str, root: Path, digest: str) -> dict[str, object]:
    entries = tree_entries(root)
    return {
        "archive_kind": name,
        "archive_digest": digest,
        "tree_digest": tree_digest(entries),
        "entries": [
            {"path": item.path, "type": item.type, "mode": item.mode,
             "size": item.size, "sha256": item.sha256}
            for item in entries
        ],
        "file_count": sum(item.type == "file" for item in entries),
        "directory_count": sum(item.type == "directory" for item in entries),
        "total_bytes": sum(item.size for item in entries),
    }


def test_cargo_lock_and_build_commands_are_strict_and_offline(tmp_path: Path) -> None:
    (tmp_path / "Cargo.lock").write_text(CARGO_LOCK, encoding="utf-8")
    adapter = CargoPackageManager()

    summary = adapter.validate_lock(tmp_path, "1.100.0-nightly")

    assert summary.identity == _identity()
    assert [(item.name, item.version) for item in summary.resolved] == [
        ("demo", "1.0.0"),
        ("itoa", "1.0.15"),
    ]
    profile_path = tmp_path / "rust-profile.toml"
    profile_path.write_text(PROFILE, encoding="utf-8")
    command = adapter.build_commands(load_rust_profile(profile_path))[0]
    assert command.argv == (
        "/opt/rust/bin/cargo",
        "build",
        "--locked",
        "--offline",
        "--frozen",
        "--target",
        "x86_64-unknown-linux-gnu",
        "--config",
        "net.offline=true",
        "--config",
        'source.crates-io.replace-with="vendored-sources"',
        "--config",
        'source.vendored-sources.directory="/opt/nl2repobench-cargo/vendor"',
        "--lib",
        "--bin",
        "demo",
        "--bin",
        "zeta",
        "--no-default-features",
        "--features",
        "std",
    )
    assert isinstance(PackageManagerRegistry.default().resolve(_identity()), CargoPackageManager)


@pytest.mark.parametrize(
    ("old", "new", "message", "code"),
    [
        ("version = 4", "version = 3", "version 4", PackageManagerErrorCode.LOCK_MALFORMED),
        (
            "registry+https://github.com/rust-lang/crates.io-index",
            "git+https://example.invalid/itoa",
            "registry source",
            PackageManagerErrorCode.LOCK_MALFORMED,
        ),
        (
            'checksum = "4a5f13b858c8d314ee3e8f639011f7ccefe71f97f96e50151fb991f267928e2c"',
            "",
            "checksum",
            PackageManagerErrorCode.LOCK_MALFORMED,
        ),
    ],
)
def test_cargo_lock_rejects_unfrozen_sources(
    tmp_path: Path,
    old: str,
    new: str,
    message: str,
    code: PackageManagerErrorCode,
) -> None:
    (tmp_path / "Cargo.lock").write_text(CARGO_LOCK.replace(old, new), encoding="utf-8")

    with pytest.raises(PackageManagerError, match=message) as raised:
        CargoPackageManager().validate_lock(tmp_path, "1.100.0-nightly")
    assert raised.value.code is code


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (CRATES_IO_SOURCE_LINE, "source = 123", "malformed source"),
        (CRATES_IO_SOURCE_LINE, "source = true", "malformed source"),
        (CRATES_IO_SOURCE_LINE, "source = 1.5", "malformed source"),
        (CRATES_IO_SOURCE_LINE, 'source = ["registry"]', "malformed source"),
        (CHECKSUM_LINE, "checksum = 123", "malformed checksum"),
        (CHECKSUM_LINE, "checksum = true", "malformed checksum"),
        (CHECKSUM_LINE, 'checksum = ["4a5f"]', "malformed checksum"),
        (ROOT_PACKAGE_BLOCK, _root_package_with("source = 123"), "malformed source"),
        (ROOT_PACKAGE_BLOCK, _root_package_with(CHECKSUM_LINE), "cannot have a checksum"),
        (ROOT_PACKAGE_BLOCK, _root_package_with("checksum = 123"), "malformed checksum"),
    ],
)
def test_cargo_lock_rejects_non_string_source_or_checksum(
    tmp_path: Path, old: str, new: str, message: str
) -> None:
    """A present malformed `source`/`checksum` is never read as an absent key."""
    (tmp_path / "Cargo.lock").write_text(CARGO_LOCK.replace(old, new), encoding="utf-8")

    with pytest.raises(PackageManagerError, match=message) as raised:
        CargoPackageManager().validate_lock(tmp_path, "1.100.0-nightly")
    assert raised.value.code is PackageManagerErrorCode.LOCK_MALFORMED


def test_cargo_lock_root_exemption_requires_an_omitted_source(tmp_path: Path) -> None:
    """Presence of `source`, even empty or crates.io-valued, is never the root."""
    registry_only = tmp_path / "registry-only"
    registry_only.mkdir()
    (registry_only / "Cargo.lock").write_text(
        CARGO_LOCK.replace(
            ROOT_PACKAGE_BLOCK,
            _root_package_with(CRATES_IO_SOURCE_LINE, CHECKSUM_LINE),
        ),
        encoding="utf-8",
    )
    with pytest.raises(PackageManagerError, match="exactly one source-less root"):
        CargoPackageManager().validate_lock(registry_only, "1.100.0-nightly")

    empty_source = tmp_path / "empty-source"
    empty_source.mkdir()
    (empty_source / "Cargo.lock").write_text(
        CARGO_LOCK.replace(CRATES_IO_SOURCE_LINE, 'source = ""'), encoding="utf-8"
    )
    with pytest.raises(PackageManagerError, match="forbidden registry source"):
        CargoPackageManager().validate_lock(empty_source, "1.100.0-nightly")


@pytest.mark.parametrize(
    "dependency",
    [
        "itoa 9.9.9",
        "itoa 1.0.15 (registry+https://example.invalid/index)",
        "itoa not-a-version",
    ],
)
def test_cargo_lock_resolves_dependency_edges_by_exact_identity(
    tmp_path: Path, dependency: str
) -> None:
    (tmp_path / "Cargo.lock").write_text(
        CARGO_LOCK.replace(' "itoa",', f' "{dependency}",'), encoding="utf-8"
    )

    with pytest.raises(PackageManagerError, match="resolve"):
        CargoPackageManager().validate_lock(tmp_path, "1.100.0-nightly")


def test_cargo_store_binds_vendor_and_crate_bytes_to_lock(tmp_path: Path) -> None:
    lock_root = tmp_path / "lock"
    lock_root.mkdir()
    (lock_root / "Cargo.lock").write_text(CARGO_LOCK, encoding="utf-8")
    adapter = CargoPackageManager()
    store = tmp_path / "store"
    vendor = store / "vendor" / "itoa-1.0.15"
    cache = store / "registry" / "cache"
    index = store / "registry" / "index"
    vendor.mkdir(parents=True)
    cache.mkdir(parents=True)
    index.mkdir(parents=True)
    crate = cache / "itoa-1.0.15.crate"
    vendor_files = {"Cargo.toml": b"[package]\nname = \"itoa\"\nversion = \"1.0.15\"\n"}
    crate.write_bytes(_crate_archive("itoa-1.0.15", vendor_files))
    checksum = hashlib.sha256(crate.read_bytes()).hexdigest()
    lock_text = CARGO_LOCK.replace(
        "4a5f13b858c8d314ee3e8f639011f7ccefe71f97f96e50151fb991f267928e2c",
        checksum,
    )
    (lock_root / "Cargo.lock").write_text(lock_text, encoding="utf-8")
    summary = adapter.validate_lock(lock_root, "1.100.0-nightly")
    for relative, content in vendor_files.items():
        (vendor / relative).write_bytes(content)
    file_checksums = {
        relative: hashlib.sha256(content).hexdigest()
        for relative, content in vendor_files.items()
    }
    (vendor / ".cargo-checksum.json").write_text(
        json.dumps(
            {"files": file_checksums, "package": checksum}, separators=(",", ":")
        ),
        encoding="utf-8",
    )
    (index / "snapshot").write_text("frozen\n", encoding="utf-8")

    entries = tree_entries(store)
    def section(name: str, root: Path, digest: str) -> dict[str, object]:
        entries = tree_entries(root)
        return {
            "archive_kind": name,
            "archive_digest": digest,
            "tree_digest": tree_digest(entries),
            "entries": [
                {"path": item.path, "type": item.type, "mode": item.mode,
                 "size": item.size, "sha256": item.sha256}
                for item in entries
            ],
            "file_count": sum(item.type == "file" for item in entries),
            "directory_count": sum(item.type == "directory" for item in entries),
            "total_bytes": sum(item.size for item in entries),
        }

    toolchain_digest = "sha256:" + "1" * 64
    inventory = {
        "schema_version": "1.0",
        "identity": "rust+cargo",
        "adapter_version": "cargo-package-manager-v1",
        "toolchain_digest": toolchain_digest,
        "lock": section("dependency-lock", lock_root, summary.lock_digest),
        "store": section(
            "offline-store",
            store,
            f"sha256:{hashlib.sha256(encode_tree(store)).hexdigest()}",
        ),
        "offline_smoke": {
            "status": "passed",
            "command_id": "cargo-metadata-frozen-offline-v1",
        },
    }

    result = adapter.validate_frozen_offline_store(
        store, summary, inventory, "1.100.0-nightly",
        expected_toolchain_digest=toolchain_digest,
        lock_root=lock_root,
    )
    assert result.offline_smoke is True
    generic_result = adapter.validate_offline_store(
        store, summary, inventory, "1.100.0-nightly"
    )
    assert generic_result == result

    crate.write_bytes(b"tampered")
    entries = tree_entries(store)
    inventory["store"].update(
        {
            "entries": [
                {"path": item.path, "type": item.type, "mode": item.mode,
                 "size": item.size, "sha256": item.sha256}
                for item in entries
            ],
            "archive_kind": "offline-store",
            "tree_digest": tree_digest(entries),
            "file_count": sum(item.type == "file" for item in entries),
            "directory_count": sum(item.type == "directory" for item in entries),
            "total_bytes": sum(item.size for item in entries),
        }
    )
    with pytest.raises(PackageManagerError, match="crate archive checksum") as raised:
        adapter.validate_frozen_offline_store(
            store,
            summary,
            inventory,
            "1.100.0-nightly",
            expected_toolchain_digest=toolchain_digest,
            lock_root=lock_root,
        )
    assert raised.value.code is PackageManagerErrorCode.INVENTORY_MISMATCH


def test_cargo_store_rejects_rehashed_vendor_tampering(tmp_path: Path) -> None:
    lock_root = tmp_path / "lock"
    lock_root.mkdir()
    store = tmp_path / "store"
    vendor = store / "vendor" / "itoa-1.0.15"
    cache = store / "registry" / "cache"
    index = store / "registry" / "index"
    vendor.mkdir(parents=True)
    cache.mkdir(parents=True)
    index.mkdir(parents=True)
    original = b"original\n"
    archive = _crate_archive("itoa-1.0.15", {"src/lib.rs": original})
    crate = cache / "itoa-1.0.15.crate"
    crate.write_bytes(archive)
    checksum = hashlib.sha256(archive).hexdigest()
    (lock_root / "Cargo.lock").write_text(
        CARGO_LOCK.replace(
            "4a5f13b858c8d314ee3e8f639011f7ccefe71f97f96e50151fb991f267928e2c",
            checksum,
        ),
        encoding="utf-8",
    )
    (vendor / "src").mkdir()
    tampered = b"tampered\n"
    (vendor / "src/lib.rs").write_bytes(tampered)
    (vendor / ".cargo-checksum.json").write_text(
        json.dumps(
            {
                "files": {"src/lib.rs": hashlib.sha256(tampered).hexdigest()},
                "package": checksum,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    (index / "snapshot").write_text("frozen\n", encoding="utf-8")
    adapter = CargoPackageManager()
    summary = adapter.validate_lock(lock_root, "1.100.0-nightly")

    from nl2repobench.storage.canonical_ustar import tree_digest, tree_entries

    entries = tree_entries(store)
    toolchain_digest = "sha256:" + "1" * 64
    inventory = {
        "schema_version": "1.0",
        "identity": "rust+cargo",
        "adapter_version": "cargo-package-manager-v1",
        "toolchain_digest": toolchain_digest,
        "lock": _inventory_section("dependency-lock", lock_root, summary.lock_digest),
        "store": {
            "archive_kind": "offline-store",
            "entries": [
                {
                    "path": item.path,
                    "type": item.type,
                    "mode": item.mode,
                    "size": item.size,
                    "sha256": item.sha256,
                }
                for item in entries
            ],
            "tree_digest": tree_digest(entries),
            "archive_digest": f"sha256:{hashlib.sha256(encode_tree(store)).hexdigest()}",
            "file_count": sum(item.type == "file" for item in entries),
            "directory_count": sum(item.type == "directory" for item in entries),
            "total_bytes": sum(item.size for item in entries),
        },
        "offline_smoke": {
            "status": "passed",
            "command_id": "cargo-metadata-frozen-offline-v1",
        },
    }

    with pytest.raises(PackageManagerError, match="differs from crate archive"):
        adapter.validate_frozen_offline_store(
            store,
            summary,
            inventory,
            "1.100.0-nightly",
            expected_toolchain_digest=toolchain_digest,
            lock_root=lock_root,
        )


@pytest.mark.parametrize(
    ("limit", "files", "message"),
    [
        ("members", {"a": b"a", "b": b"b"}, "too many members"),
        ("member_bytes", {"a": b"oversized"}, "member exceeds size limit"),
    ],
)
def test_crate_archive_expansion_limits_are_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    limit: str,
    files: dict[str, bytes],
    message: str,
) -> None:
    archive = tmp_path / "demo-1.0.0.crate"
    archive.write_bytes(_crate_archive("demo-1.0.0", files))
    if limit == "members":
        monkeypatch.setattr(cargo_module, "MAX_CRATE_MEMBERS", 2)
    else:
        monkeypatch.setattr(cargo_module, "MAX_CRATE_MEMBER_BYTES", 1)

    with pytest.raises(PackageManagerError, match=message):
        cargo_module._read_crate_archive(archive, expected_root="demo-1.0.0")


@pytest.mark.parametrize("archive_format", [tarfile.GNU_FORMAT, tarfile.PAX_FORMAT])
def test_crate_archive_rejects_extension_metadata_before_expansion(
    tmp_path: Path, archive_format: int
) -> None:
    archive_path = tmp_path / "demo-1.0.0.crate"
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz", format=archive_format) as archive:
        info = tarfile.TarInfo("demo-1.0.0/" + "a" * 101)
        info.size = 1
        if archive_format == tarfile.PAX_FORMAT:
            info.pax_headers = {"comment": "x" * 4096}
        archive.addfile(info, io.BytesIO(b"x"))
    archive_path.write_bytes(output.getvalue())

    with pytest.raises(PackageManagerError, match="extension metadata is forbidden"):
        cargo_module._read_crate_archive(archive_path, expected_root="demo-1.0.0")


@pytest.mark.parametrize(
    ("limit", "message"),
    [
        ("compressed", "compressed size limit"),
        ("path", "path exceeds size limit"),
        ("total", "expanded size exceeds total limit"),
    ],
)
def test_crate_archive_direct_size_ceilings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    limit: str,
    message: str,
) -> None:
    archive = tmp_path / "demo-1.0.0.crate"
    archive.write_bytes(_crate_archive("demo-1.0.0", {"a": b"ab"}))
    if limit == "compressed":
        monkeypatch.setattr(cargo_module, "MAX_CRATE_ARCHIVE_BYTES", archive.stat().st_size - 1)
    elif limit == "path":
        monkeypatch.setattr(cargo_module, "MAX_CRATE_PATH_BYTES", len("demo-1.0.0/a") - 1)
    else:
        monkeypatch.setattr(cargo_module, "MAX_CRATE_TOTAL_BYTES", 1)

    with pytest.raises(PackageManagerError, match=message):
        cargo_module._read_crate_archive(archive, expected_root="demo-1.0.0")


def test_crate_archive_reads_members_in_bounded_chunks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive = tmp_path / "demo-1.0.0.crate"
    archive.write_bytes(_crate_archive("demo-1.0.0", {"a": b"abc"}))
    monkeypatch.setattr(cargo_module, "MAX_CRATE_READ_BYTES", 1)

    assert cargo_module._read_crate_archive(
        archive, expected_root="demo-1.0.0"
    ) == {"a": hashlib.sha256(b"abc").hexdigest()}


def test_crate_archive_rejects_truncated_compressed_stream(tmp_path: Path) -> None:
    archive = tmp_path / "demo-1.0.0.crate"
    raw = _crate_archive("demo-1.0.0", {"a": b"abc"})
    archive.write_bytes(raw[:-8])

    with pytest.raises(PackageManagerError, match="malformed"):
        cargo_module._read_crate_archive(archive, expected_root="demo-1.0.0")


@pytest.mark.parametrize("relative", ["./src/lib.rs", "/src/lib.rs"])
def test_crate_archive_rejects_noncanonical_raw_path_components(
    tmp_path: Path, relative: str
) -> None:
    archive = tmp_path / "demo-1.0.0.crate"
    archive.write_bytes(_crate_archive("demo-1.0.0", {relative: b"content"}))

    with pytest.raises(PackageManagerError, match="unsafe archive member"):
        cargo_module._read_crate_archive(archive, expected_root="demo-1.0.0")


def test_generic_cargo_store_staging_requires_canonical_inventory(tmp_path: Path) -> None:
    adapter = CargoPackageManager()
    lock_root = tmp_path / "lock"
    lock_root.mkdir()
    (lock_root / "Cargo.lock").write_text(CARGO_LOCK, encoding="utf-8")
    summary = adapter.validate_lock(lock_root, "1.100.0-nightly")

    with pytest.raises(PackageManagerError, match="toolchain digest is malformed") as raised:
        adapter.validate_offline_store(
            tmp_path / "store", summary, {}, "1.100.0-nightly"
        )
    assert raised.value.code is PackageManagerErrorCode.INVENTORY_MISMATCH


def _rust_profile() -> RuntimeProfile:
    return RuntimeProfile(
        language="rust",
        runtime="rust",
        version="1.100.0-nightly",
        package_manager="cargo",
        package_manager_version="1.100.0-nightly",
    )


@pytest.mark.parametrize("method", ["validate_lock", "validate_offline_store"])
def test_cargo_adapter_declares_the_shared_runtime_profile_keyword(method: str) -> None:
    """The canonical materializer always passes `runtime_profile` as a keyword."""

    protocol = inspect.signature(getattr(PackageManagerAdapter, method)).parameters
    implementation = inspect.signature(getattr(CargoPackageManager, method)).parameters
    assert "runtime_profile" in protocol
    assert implementation["runtime_profile"].kind is inspect.Parameter.KEYWORD_ONLY
    assert implementation["runtime_profile"].default is None


def test_canonical_cargo_adapter_call_reports_typed_errors(tmp_path: Path) -> None:
    """Registry-resolved Cargo validation must never surface a raw TypeError."""

    adapter = PackageManagerRegistry.default().resolve(_identity())
    lock_root = tmp_path / "lock"
    lock_root.mkdir()
    (lock_root / "Cargo.lock").write_text(CARGO_LOCK, encoding="utf-8")
    profile = _rust_profile()

    summary = adapter.validate_lock(lock_root, "1.100.0-nightly", runtime_profile=profile)
    assert [item.name for item in summary.resolved] == ["demo", "itoa"]

    with pytest.raises(PackageManagerError, match="toolchain digest is malformed") as raised:
        adapter.validate_offline_store(
            tmp_path / "store",
            summary,
            {},
            "1.100.0-nightly",
            runtime_profile=profile,
        )
    assert raised.value.code is PackageManagerErrorCode.INVENTORY_MISMATCH
    assert raised.value.stage == "store"

    mismatched = RuntimeProfile(
        language="node",
        runtime="node",
        version="22.11.0",
        package_manager="pnpm",
        package_manager_version="9.15.0",
    )
    with pytest.raises(PackageManagerError, match=r"rust\+cargo runtime profile") as wrong:
        adapter.validate_offline_store(
            tmp_path / "store",
            summary,
            {},
            "1.100.0-nightly",
            runtime_profile=mismatched,
        )
    assert wrong.value.code is PackageManagerErrorCode.TOOLCHAIN_MISMATCH
    with pytest.raises(PackageManagerError, match=r"rust\+cargo runtime profile") as wrong_lock:
        adapter.validate_lock(lock_root, "1.100.0-nightly", runtime_profile=mismatched)
    assert wrong_lock.value.code is PackageManagerErrorCode.TOOLCHAIN_MISMATCH
    assert wrong_lock.value.stage == "lock"

    # model_construct skips validation to simulate an unpinned profile reaching the adapter.
    unpinned = RuntimeProfile.model_construct(
        language="rust",
        runtime="rust",
        version="1.99.0",
        package_manager="cargo",
        package_manager_version="1.100.0-nightly",
    )
    with pytest.raises(PackageManagerError, match=r"rust\+cargo runtime profile"):
        adapter.validate_lock(lock_root, "1.100.0-nightly", runtime_profile=unpinned)
