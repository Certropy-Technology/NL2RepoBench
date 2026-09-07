"""Rust/Cargo runtime identity for the authoring and Harbor adapters."""

from __future__ import annotations

from dataclasses import dataclass

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.package_managers.cargo import CargoPackageManager


@dataclass(frozen=True)
class RustRuntimeAdapter:
    """Compose the Rust runtime identity with the Cargo package manager."""

    identity = RuntimeDiscriminator(
        language=RuntimeLanguage.RUST,
        package_manager=PackageManager.CARGO,
    )
    package_manager = CargoPackageManager()
    runtime = "rust"


__all__ = ["RustRuntimeAdapter"]
