from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from nl2repobench.domain.canonical_contract import PackageManager, RuntimeLanguage
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.package_managers import (
    CargoPackageManager,
    PackageManagerError,
    PackageManagerErrorCode,
    PackageManagerRegistry,
)

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


def test_cargo_lock_and_build_commands_are_strict_and_offline(tmp_path: Path) -> None:
    (tmp_path / "Cargo.lock").write_text(CARGO_LOCK, encoding="utf-8")
    adapter = CargoPackageManager()

    summary = adapter.validate_lock(tmp_path, "1.100.0-nightly")

    assert summary.identity == _identity()
    assert [(item.name, item.version) for item in summary.resolved] == [
        ("demo", "1.0.0"),
        ("itoa", "1.0.15"),
    ]
    command = adapter.build_commands(
        {"default_features": False, "enabled": ("std",)}
    )[0]
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

    from nl2repobench.storage.canonical_ustar import tree_digest, tree_entries

    entries = tree_entries(store)
    inventory = {
        "schema_version": "1.0",
        "identity": "rust+cargo",
        "adapter_version": "cargo-package-manager-v1",
        "toolchain_digest": "sha256:" + "1" * 64,
        "lock": {"digest": summary.lock_digest},
        "store": {
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
            "archive_digest": "sha256:" + "2" * 64,
            "file_count": sum(item.type == "file" for item in entries),
            "directory_count": sum(item.type == "directory" for item in entries),
            "total_bytes": sum(item.size for item in entries),
        },
        "offline_smoke": {
            "status": "passed",
            "command_id": "cargo-metadata-frozen-offline-v1",
        },
    }

    result = adapter.validate_offline_store(
        store, summary, inventory, "1.100.0-nightly"
    )
    assert result.offline_smoke is True

    crate.write_bytes(b"tampered")
    entries = tree_entries(store)
    inventory["store"].update(
        {
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
            "file_count": sum(item.type == "file" for item in entries),
            "directory_count": sum(item.type == "directory" for item in entries),
            "total_bytes": sum(item.size for item in entries),
        }
    )
    with pytest.raises(PackageManagerError, match="crate archive checksum") as raised:
        adapter.validate_offline_store(store, summary, inventory, "1.100.0-nightly")
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
    inventory = {
        "schema_version": "1.0",
        "identity": "rust+cargo",
        "adapter_version": "cargo-package-manager-v1",
        "toolchain_digest": "sha256:" + "1" * 64,
        "lock": {"digest": summary.lock_digest},
        "store": {
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
            "archive_digest": "sha256:" + "2" * 64,
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
        adapter.validate_offline_store(store, summary, inventory, "1.100.0-nightly")
