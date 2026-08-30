from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from nl2repobench.domain.runtime import (
    PackageManager,
    RuntimeDiscriminator,
    RuntimeLanguage,
)
from nl2repobench.package_managers import (
    PackageManagerError,
    PackageManagerErrorCode,
    PackageManagerRegistry,
    PnpmPackageManager,
    UnknownPackageManagerError,
)

MINIMAL_LOCK = """lockfileVersion: '9.0'
settings:
  autoInstallPeers: false
  excludeLinksFromLockfile: false
importers:
  .: {}
packages: {}
snapshots: {}
"""


def _identity(language: RuntimeLanguage, manager: PackageManager) -> RuntimeDiscriminator:
    return RuntimeDiscriminator(language=language, package_manager=manager)


def test_pnpm_implements_typed_lock_and_command_protocol(tmp_path: Path) -> None:
    (tmp_path / "pnpm-lock.yaml").write_text(MINIMAL_LOCK, encoding="utf-8")
    adapter = PnpmPackageManager()
    summary = adapter.validate_lock(tmp_path, "9.15.0")
    assert summary.identity == _identity(RuntimeLanguage.NODE, PackageManager.PNPM)
    assert summary.lockfile_names == ("pnpm-lock.yaml",)
    command = adapter.build_commands({})[0]
    assert command.argv[:3] == ("/usr/local/bin/pnpm", "install", "--offline")
    assert adapter.offline_environment({}) == {"PNPM_HOME": "/opt/pnpm"}


@pytest.mark.parametrize(
    "marker",
    ["git+https://example.invalid/pkg.git", "workspace:*", "file:../pkg"],
)
def test_pnpm_rejects_non_registry_sources(tmp_path: Path, marker: str) -> None:
    lock = MINIMAL_LOCK.replace(
        "packages: {}", f"packages:\n  /demo@1.0.0:\n    resolution: {marker}"
    )
    (tmp_path / "pnpm-lock.yaml").write_text(lock, encoding="utf-8")
    with pytest.raises(PackageManagerError, match="forbidden dependency source") as raised:
        PnpmPackageManager().validate_lock(tmp_path, "9.15.0")
    assert raised.value.code is PackageManagerErrorCode.LOCK_MALFORMED


def test_registry_resolves_all_f0_identities_exactly() -> None:
    registry = PackageManagerRegistry.default()
    identities = {
        _identity(RuntimeLanguage.PYTHON, PackageManager.UV),
        _identity(RuntimeLanguage.PYTHON, PackageManager.PIP),
        _identity(RuntimeLanguage.PYTHON, PackageManager.NONE),
        _identity(RuntimeLanguage.NODE, PackageManager.NPM),
        _identity(RuntimeLanguage.NODE, PackageManager.PNPM),
        _identity(RuntimeLanguage.NODE, PackageManager.NONE),
        _identity(RuntimeLanguage.GO, PackageManager.GO_MODULES),
    }
    assert set(registry.adapters) == identities
    assert isinstance(
        registry.resolve(_identity(RuntimeLanguage.NODE, PackageManager.PNPM)),
        PnpmPackageManager,
    )
    with pytest.raises(UnknownPackageManagerError, match="validated RuntimeDiscriminator"):
        registry.resolve("pnpm")  # type: ignore[arg-type]
    with pytest.raises(ValidationError, match="go runtime cannot use uv"):
        _identity(RuntimeLanguage.GO, PackageManager.UV)


def test_node_none_adapter_rejects_builds() -> None:
    adapter = PackageManagerRegistry.default().resolve(
        _identity(RuntimeLanguage.NODE, PackageManager.NONE)
    )
    with pytest.raises(PackageManagerError, match="cannot build") as raised:
        adapter.build_commands({})
    assert raised.value.code is PackageManagerErrorCode.UNSUPPORTED_PROFILE


def test_package_manager_error_rejects_unknown_codes() -> None:
    with pytest.raises(ValueError, match="invalid package-manager error code"):
        PackageManagerError(
            "anything",
            _identity(RuntimeLanguage.PYTHON, PackageManager.UV),
            "lock",
            "invalid",
        )
