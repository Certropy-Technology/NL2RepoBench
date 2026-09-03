from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from nl2repobench.harbor.pnpm_compiler import PnpmHarborCompiler
from nl2repobench.package_managers import (
    PackageManagerError,
    PackageManagerRegistry,
    PnpmPackageManager,
    UnknownPackageManagerError,
)


def _write_bundle(root, lock_text: str) -> None:
    lock = root / "pnpm-lock.yaml"
    store = root / "pnpm-store"
    store.mkdir()
    lock.write_text(lock_text, encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "ecosystem": "npm",
        "lockfile_version": "9",
        "package_manager": "pnpm",
        "package_manager_version": "9.15.0",
        "install_mode": "offline",
        "lifecycle_scripts": "ignore-scripts",
        "lockfile_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "files": [
            {
                "path": "pnpm-lock.yaml",
                "sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
            }
        ],
    }
    (root / "bundle.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


MINIMAL_LOCK = """lockfileVersion: '9.0'
settings:
  autoInstallPeers: false
  excludeLinksFromLockfile: false
importers:
  .: {}
packages: {}
snapshots: {}
"""


def test_pnpm_validates_v9_lock_store_and_command(tmp_path) -> None:
    _write_bundle(tmp_path, MINIMAL_LOCK)
    adapter = PnpmPackageManager()
    summary = adapter.validate_lock(tmp_path / "pnpm-lock.yaml", expected_version="9.15.0")
    assert summary.lockfile_version == "9.0"
    adapter.validate_offline_store(
        tmp_path,
        lockfile=tmp_path / "pnpm-lock.yaml",
        manifest=tmp_path / "bundle.manifest.json",
        expected_version="9.15.0",
    )
    assert adapter.install_command(store_dir="/opt/pnpm-store") == (
        "/usr/local/bin/pnpm",
        "install",
        "--offline",
        "--frozen-lockfile",
        "--ignore-scripts",
        "--store-dir",
        "/opt/pnpm-store",
    )


@pytest.mark.parametrize(
    "marker",
    ["git+https://example.invalid/pkg.git", "workspace:*", "file:../pkg"],
)
def test_pnpm_rejects_non_registry_sources(tmp_path, marker: str) -> None:
    lock = MINIMAL_LOCK.replace(
        "packages: {}", f"packages:\n  /demo@1.0.0:\n    resolution: {marker}"
    )
    lock_path = tmp_path / "pnpm-lock.yaml"
    lock_path.write_text(lock, encoding="utf-8")
    with pytest.raises(PackageManagerError, match="forbidden dependency source"):
        PnpmPackageManager().validate_lock(
            lock_path,
            expected_version="9.15.0",
        )


def test_package_manager_registry_fails_closed() -> None:
    registry = PackageManagerRegistry.default()
    assert isinstance(registry.resolve("pnpm"), PnpmPackageManager)
    with pytest.raises(UnknownPackageManagerError, match="registered: go-modules, maven, pnpm"):
        registry.resolve("npm")


def test_pnpm_compiler_writes_pnpm_runtime_bundle(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    output = PnpmHarborCompiler(root / "toolchain.node.dev.lock.toml").compile_task(
        root / "catalog/sources/node-pnpm-synthetic",
        tmp_path,
        allow_incomplete=True,
    )
    task = (output / "task.toml").read_text(encoding="utf-8")
    assert 'package_manager = "pnpm"' in task
    assert 'metric_contract = "fixed-test-pass-rate-v1"' in task
    assert (output / "tests/dependencies/pnpm-lock.yaml").is_file()
    assert "pnpm-pack-offline-v1" in (output / "tests/command-plan.json").read_text()
