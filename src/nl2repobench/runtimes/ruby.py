"""Ruby runtime identity and Bundler composition boundary."""

from __future__ import annotations

from dataclasses import dataclass

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.package_managers.bundler import BundlerPackageManager


@dataclass(frozen=True)
class RubyRuntimeAdapter:
    """The first Ruby profile: MRI plus an offline Bundler cache."""

    identity = RuntimeDiscriminator(
        language=RuntimeLanguage.RUBY,
        package_manager=PackageManager.BUNDLER,
    )
    package_manager = BundlerPackageManager()
    runtime = "ruby"
