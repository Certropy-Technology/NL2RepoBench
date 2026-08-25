"""Go runtime identity and typed bridge composition boundary."""

from __future__ import annotations

from dataclasses import dataclass

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.package_managers.go_modules import GoModulesPackageManager


@dataclass(frozen=True)
class GoRuntimeAdapter:
    identity = RuntimeDiscriminator(
        language=RuntimeLanguage.GO,
        package_manager=PackageManager.GO_MODULES,
    )
    package_manager = GoModulesPackageManager()
    runtime = "go"
