"""Runtime-specific source asset validation below the canonical task model."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from nl2repobench.domain.canonical_contract import (
    PackageManager,
    RuntimeLanguage,
    TaskSource,
)
from nl2repobench.domain.canonical_models import Visibility
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.verification.rust_profile import load_rust_profile

RUST_VERSION = "1.100.0-nightly"
MAX_API_PLAN_BYTES = 4 * 1024 * 1024


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
        if runtime is None or (
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
        if profile_assets != ("rust-profile.toml",):
            raise RuntimeSourceAssetError(
                "Rust authoring sources require exactly one root rust-profile.toml"
            )
        profile = load_rust_profile(source_dir / "rust-profile.toml")

        api_plan = source_dir / "rust-api-plan.json"
        if (
            api_plan.is_symlink()
            or not api_plan.is_file()
            or api_plan.stat().st_size > MAX_API_PLAN_BYTES
        ):
            raise RuntimeSourceAssetError(
                "Rust sources require one bounded regular rust-api-plan.json"
            )
        actual_digest = f"sha256:{hashlib.sha256(api_plan.read_bytes()).hexdigest()}"
        if actual_digest != profile.bridge.api_plan_digest:
            raise RuntimeSourceAssetError("Rust API plan digest does not match rust-profile.toml")

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
        non_private = [
            name
            for name, reference in closure_refs.items()
            if reference is not None and reference.visibility is not Visibility.PRIVATE
        ]
        if source.dependencies.status != "known" or missing or non_private:
            details = ", ".join((*missing, *non_private)) or "dependencies.status=known"
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
                raise RuntimeSourceAssetError(
                    "Rust sources require an explicit rust+cargo runtime profile"
                )
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
