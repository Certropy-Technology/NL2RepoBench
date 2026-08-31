"""Runtime-specific source asset validation below the canonical task model."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from nl2repobench.domain.canonical_contract import (
    PackageManager,
    RuntimeLanguage,
    TaskSource,
)
from nl2repobench.domain.canonical_models import TaskStatus, Visibility
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.verification.rust_bridge import load_rust_api_plan
from nl2repobench.verification.rust_profile import (
    load_rust_profile,
    validate_rust_profile_api_plan,
)

RUST_VERSION = "1.100.0-nightly"
_PRODUCTION_STATUSES = {
    TaskStatus.PACKAGED,
    TaskStatus.ORACLE_PASSED,
    TaskStatus.CONTROLS_PASSED,
    TaskStatus.REVIEWED,
    TaskStatus.PILOTED,
    TaskStatus.PUBLISHED,
}
_PRIVATE_MEDIA_TYPES = {
    "dependencies.lock": "application/vnd.nl2repobench.package-lock.tar",
    "dependencies.offline_store": "application/vnd.nl2repobench.offline-store.tar",
    "dependencies.inventory": "application/vnd.nl2repobench.inventory+json",
    "tests.commands_artifact": "application/vnd.nl2repobench.command-plan+json",
    "tests.test_bundle": "application/vnd.nl2repobench.test-bundle.tar",
    "verifier.bundle": "application/vnd.nl2repobench.verifier-bundle.tar",
    "oracle_bundle": "application/vnd.nl2repobench.oracle-bundle.tar",
}


class RuntimeSourceAssetError(ValueError):
    """A runtime-specific authoring asset is missing or inconsistent."""


class UnknownRuntimeSourceAssetValidatorError(ValueError):
    """No source validator is registered for an explicitly requested identity."""


class RuntimeSourceAssetValidator(Protocol):
    identity: RuntimeDiscriminator

    def validate_source_assets(self, source_dir: Path, source: TaskSource) -> None: ...


@dataclass(frozen=True, slots=True)
class RustSourceAssetValidator:
    identity = RuntimeDiscriminator(
        language=RuntimeLanguage.RUST,
        package_manager=PackageManager.CARGO,
    )

    def validate_source_assets(self, source_dir: Path, source: TaskSource) -> None:
        runtime = source.environment.runtime
        production = source.lifecycle.status in _PRODUCTION_STATUSES
        if runtime is None and production:
            raise RuntimeSourceAssetError(
                "production Rust sources require an explicit rust+cargo runtime profile"
            )
        if runtime is not None and (
            runtime.runtime,
            runtime.version,
            runtime.package_manager_version,
        ) != ("rust", RUST_VERSION, RUST_VERSION):
            raise RuntimeSourceAssetError(
                "Rust sources require the exact rust+cargo 1.100.0-nightly profile"
            )

        profile_assets = tuple(
            sorted(
                path.relative_to(source_dir).as_posix()
                for path in source_dir.rglob("rust-profile*")
            )
        )
        if "rust-profile.json" in profile_assets:
            raise RuntimeSourceAssetError(
                "Rust authoring sources must not contain rust-profile.json"
            )
        api_plan_path = source_dir / "rust-api-plan.json"
        if not profile_assets and not api_plan_path.exists() and not production:
            return
        if profile_assets != ("rust-profile.toml",):
            raise RuntimeSourceAssetError(
                "Rust authoring sources require exactly one root rust-profile.toml"
            )
        try:
            profile = load_rust_profile(source_dir / "rust-profile.toml")
            plan, exact_plan_bytes = load_rust_api_plan(api_plan_path)
            validate_rust_profile_api_plan(profile, plan, exact_plan_bytes)
        except ValueError as exc:
            raise RuntimeSourceAssetError(str(exc)) from exc

        closure_refs = {
            "dependencies.lock": source.dependencies.lock,
            "dependencies.offline_store": source.dependencies.offline_store,
            "dependencies.inventory": source.dependencies.inventory,
            "tests.commands_artifact": source.tests.commands_artifact,
            "tests.test_bundle": source.tests.test_bundle,
            "verifier.bundle": source.verifier.bundle if source.verifier else None,
            "oracle_bundle": source.oracle_bundle,
        }
        missing = [name for name, reference in closure_refs.items() if reference is None]
        invalid_refs = [
            name
            for name, reference in closure_refs.items()
            if reference is not None
            and (
                reference.visibility is not Visibility.PRIVATE
                or reference.media_type != _PRIVATE_MEDIA_TYPES[name]
            )
        ]
        if invalid_refs:
            raise RuntimeSourceAssetError(
                "Rust private closure refs have invalid visibility or media type: "
                + ", ".join(invalid_refs)
            )
        if production and (source.dependencies.status != "known" or missing):
            details = ", ".join(missing) or "dependencies.status=known"
            raise RuntimeSourceAssetError(
                f"Rust sources require the complete private closure: {details}"
            )


@dataclass(frozen=True, slots=True)
class RuntimeSourceAssetRegistry:
    validators: Mapping[RuntimeDiscriminator, RuntimeSourceAssetValidator]

    @classmethod
    def default(cls) -> RuntimeSourceAssetRegistry:
        rust = RustSourceAssetValidator()
        return cls({rust.identity: rust})

    def resolve(self, identity: RuntimeDiscriminator) -> RuntimeSourceAssetValidator:
        if not isinstance(identity, RuntimeDiscriminator):
            raise UnknownRuntimeSourceAssetValidatorError(
                "source asset resolution requires a validated RuntimeDiscriminator"
            )
        try:
            return self.validators[identity]
        except KeyError as exc:
            requested = f"{identity.language.value}+{identity.package_manager.value}"
            available = ", ".join(
                sorted(
                    f"{item.language.value}+{item.package_manager.value}"
                    for item in self.validators
                )
            )
            raise UnknownRuntimeSourceAssetValidatorError(
                f"no source asset validator for {requested}; registered: {available}"
            ) from exc

    def validate_source_assets(self, source_dir: Path, source: TaskSource) -> None:
        if source.environment.runtime is None:
            if source.metadata.language is RuntimeLanguage.RUST:
                RustSourceAssetValidator().validate_source_assets(source_dir, source)
            return
        identity = RuntimeDiscriminator.from_task_source(source)
        validator = self.validators.get(identity)
        if validator is not None:
            validator.validate_source_assets(source_dir, source)


__all__ = [
    "RuntimeSourceAssetError",
    "RuntimeSourceAssetRegistry",
    "RuntimeSourceAssetValidator",
    "RustSourceAssetValidator",
    "UnknownRuntimeSourceAssetValidatorError",
]
