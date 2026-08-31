"""Strict typed reader for the Rust authoring profile."""

from __future__ import annotations

import hashlib
import re
import tomllib
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from nl2repobench.runtimes.rust import (
    SELECTED_TARGET,
    evaluate_target_selector,
    normalize_target_selector,
)
from nl2repobench.verification.rust_bridge import (
    RustApiPlan,
    canonical_json_bytes,
)

_PACKAGE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_FEATURE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_+.-]*$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_SEMVER = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
_RUST_VERSION = re.compile(r"^1\.[0-9]+(?:\.[0-9]+)?$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
MAX_PROFILE_BYTES = 4 * 1024 * 1024


def _utf8_sorted_unique(values: tuple[str, ...], description: str) -> tuple[str, ...]:
    if tuple(sorted(values, key=lambda item: item.encode("utf-8"))) != values:
        raise ValueError(f"{description} must be sorted by UTF-8 bytes")
    if len(set(values)) != len(values):
        raise ValueError(f"{description} must be unique")
    return values


class RustProfileRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class RustPackageProfile(RustProfileRecord):
    name: str
    version: str
    edition: Literal["2018", "2021", "2024"]
    rust_version: str | None = None
    library_path: Literal["src/lib.rs"]
    binaries: Annotated[tuple[str, ...], Field(max_length=8)]

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if not _PACKAGE_NAME.fullmatch(self.name):
            raise ValueError("package name is invalid")
        if not _SEMVER.fullmatch(self.version):
            raise ValueError("package version must be exact semantic version")
        if self.rust_version is not None and not _RUST_VERSION.fullmatch(self.rust_version):
            raise ValueError("rust_version must be an exact Rust 1.x version")
        _utf8_sorted_unique(self.binaries, "package binaries")
        if any(not _PACKAGE_NAME.fullmatch(name) for name in self.binaries):
            raise ValueError("binary names are invalid")
        return self


class RustTargetProfile(RustProfileRecord):
    triple: Literal["x86_64-unknown-linux-gnu"]


class RustFeatureProfile(RustProfileRecord):
    default_features: bool
    enabled: tuple[str, ...]
    declarations: dict[str, tuple[str, ...]]

    @model_validator(mode="after")
    def validate_features(self) -> Self:
        _utf8_sorted_unique(self.enabled, "enabled features")
        keys = tuple(self.declarations)
        _utf8_sorted_unique(keys, "feature declarations")
        if any(not _FEATURE_NAME.fullmatch(name) for name in (*keys, *self.enabled)):
            raise ValueError("feature names are invalid")
        if not set(self.enabled).issubset(self.declarations):
            raise ValueError("enabled features must be declared")
        for name, members in self.declarations.items():
            _utf8_sorted_unique(members, f"feature declaration {name}")
            if any(
                not member or any(character.isspace() for character in member)
                for member in members
            ):
                raise ValueError(f"feature declaration {name} contains an invalid member")
        return self


class CandidateDependency(RustProfileRecord):
    name: str
    version: str
    default_features: bool
    features: tuple[str, ...]
    target_selector: str | None = None

    @model_validator(mode="after")
    def validate_dependency(self) -> Self:
        if not _PACKAGE_NAME.fullmatch(self.name):
            raise ValueError("candidate dependency name is invalid")
        if not _SEMVER.fullmatch(self.version):
            raise ValueError("candidate dependency version must be exact semantic version")
        _utf8_sorted_unique(self.features, f"candidate dependency {self.name} features")
        if any(not _FEATURE_NAME.fullmatch(name) for name in self.features):
            raise ValueError("candidate dependency feature name is invalid")
        if self.target_selector is not None:
            normalize_target_selector(self.target_selector)
        return self

    @property
    def selected(self) -> bool:
        return self.target_selector is None or evaluate_target_selector(self.target_selector)


class RustBridgeProfile(RustProfileRecord):
    api_plan_digest: str
    max_operations_per_request: Literal[64]
    max_state_handles: Literal[32]
    max_state_bytes: Literal[8388608]
    unsafe_api_ids: tuple[str, ...]

    @model_validator(mode="after")
    def validate_bridge(self) -> Self:
        if not _SHA256.fullmatch(self.api_plan_digest):
            raise ValueError("bridge API plan digest must be SHA-256")
        _utf8_sorted_unique(self.unsafe_api_ids, "unsafe API IDs")
        if any(not _SAFE_ID.fullmatch(item) for item in self.unsafe_api_ids):
            raise ValueError("unsafe API ID is invalid")
        return self


class RustCliProfile(RustProfileRecord):
    profile_id: str
    binary_name: str
    argv_max_items: Annotated[int, Field(ge=1, le=64)]
    stdin_max_bytes: Annotated[int, Field(ge=0, le=1048576)]
    max_output_bytes: Annotated[int, Field(ge=1, le=8388608)]
    tempdir_policy: Literal["none", "empty", "fresh-writable", "fresh-readonly"]
    tempdir_max_entries: Annotated[int, Field(ge=0, le=256)]
    tempdir_max_bytes: Annotated[int, Field(ge=0, le=33554432)]
    tempdir_max_file_bytes: Annotated[int, Field(ge=0, le=8388608)]
    cli_timeout_sec: Annotated[float, Field(ge=0.001, le=120.0)]
    expected_exit_codes: Annotated[tuple[int, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_cli(self) -> Self:
        if not _SAFE_ID.fullmatch(self.profile_id):
            raise ValueError("CLI profile ID is invalid")
        if not _PACKAGE_NAME.fullmatch(self.binary_name):
            raise ValueError("CLI binary name is invalid")
        if tuple(sorted(self.expected_exit_codes)) != self.expected_exit_codes:
            raise ValueError("expected exit codes must be sorted")
        if len(set(self.expected_exit_codes)) != len(self.expected_exit_codes):
            raise ValueError("expected exit codes must be unique")
        if any(code < -128 or code > 127 for code in self.expected_exit_codes):
            raise ValueError("expected exit codes must be in [-128, 127]")
        if self.tempdir_policy == "none" and any(
            (self.tempdir_max_entries, self.tempdir_max_bytes, self.tempdir_max_file_bytes)
        ):
            raise ValueError("none tempdir policy requires zero tempdir limits")
        return self


class RustLimits(RustProfileRecord):
    build_timeout_sec: Annotated[int, Field(gt=0, le=600)]
    leaf_timeout_sec: Annotated[int, Field(gt=0, le=120)]
    cpu_sec: Annotated[int, Field(gt=0, le=120)]
    max_stdin_bytes: Annotated[int, Field(ge=0, le=1048576)]
    max_output_bytes: Annotated[int, Field(gt=0, le=8388608)]
    max_file_bytes: Annotated[int, Field(gt=0, le=536870912)]
    max_open_files: Annotated[int, Field(gt=0, le=256)]
    max_processes: Annotated[int, Field(gt=0, le=64)]


class RustProfile(RustProfileRecord):
    schema_version: Literal["1.0"]
    package: RustPackageProfile
    target: RustTargetProfile
    features: RustFeatureProfile
    candidate_dependencies: tuple[CandidateDependency, ...]
    bridge: RustBridgeProfile
    cli: tuple[RustCliProfile, ...]
    limits: RustLimits

    @model_validator(mode="after")
    def validate_cross_references(self) -> Self:
        dependencies = tuple(
            (item.name, item.version, item.target_selector or "")
            for item in self.candidate_dependencies
        )
        ordered = tuple(
            sorted(
                dependencies,
                key=lambda item: tuple(part.encode("utf-8") for part in item),
            )
        )
        if ordered != dependencies:
            raise ValueError("candidate dependencies must be sorted by UTF-8 bytes")
        if len(dependencies) != len(set(dependencies)):
            raise ValueError("candidate dependencies must be unique")
        profile_ids = tuple(item.profile_id for item in self.cli)
        _utf8_sorted_unique(profile_ids, "CLI profiles")
        if any(item.binary_name not in self.package.binaries for item in self.cli):
            raise ValueError("CLI profiles must reference declared package binaries")
        if self.target.triple != SELECTED_TARGET:
            raise ValueError("Rust target does not match selected target")
        return self

    @property
    def selected_candidate_dependencies(self) -> tuple[CandidateDependency, ...]:
        """Return only dependencies selected by the frozen target evaluator."""

        return tuple(item for item in self.candidate_dependencies if item.selected)


def load_rust_profile(path: Path) -> RustProfile:
    """Read one bounded, regular TOML source into the frozen profile model."""

    if path.is_symlink() or not path.is_file():
        raise ValueError("rust-profile.toml must be a regular file")
    try:
        if path.stat().st_size > MAX_PROFILE_BYTES:
            raise ValueError("rust-profile.toml exceeds the size limit")
        data = _freeze_arrays(tomllib.loads(path.read_text(encoding="utf-8")))
        return RustProfile.model_validate(data)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"invalid rust-profile.toml: {exc}") from exc


def canonical_rust_profile_bytes(profile: RustProfile) -> bytes:
    """Serialize the lossless compiler-owned JSON projection."""

    return canonical_json_bytes(profile.model_dump(mode="json"))


def rust_profile_projection_digest(profile: RustProfile) -> str:
    return f"sha256:{hashlib.sha256(canonical_rust_profile_bytes(profile)).hexdigest()}"


def validate_rust_profile_api_plan(
    profile: RustProfile,
    plan: RustApiPlan,
    exact_plan_bytes: bytes,
) -> None:
    """Bind the profile to both API-plan digests and public cross-references."""

    exact_digest = f"sha256:{hashlib.sha256(exact_plan_bytes).hexdigest()}"
    if profile.bridge.api_plan_digest != exact_digest:
        raise ValueError("Rust API plan exact-file digest does not match rust-profile.toml")
    if plan.package_name != profile.package.name:
        raise ValueError("Rust API plan package_name does not match rust-profile.toml")
    expected_cli = tuple((item.profile_id, item.binary_name) for item in profile.cli)
    actual_cli = tuple((item.profile_id, item.binary_name) for item in plan.cli_profiles)
    if actual_cli != expected_cli:
        raise ValueError("Rust API plan CLI profiles do not match rust-profile.toml")
    unsafe_api_ids = tuple(item.api_id for item in plan.functions if item.unsafe)
    if unsafe_api_ids != profile.bridge.unsafe_api_ids:
        raise ValueError("Rust API plan unsafe APIs do not match rust-profile.toml")


def _freeze_arrays(value: object) -> object:
    if isinstance(value, list):
        return tuple(_freeze_arrays(item) for item in value)
    if isinstance(value, dict):
        return {key: _freeze_arrays(item) for key, item in value.items()}
    return value


__all__ = [
    "CandidateDependency",
    "RustBridgeProfile",
    "RustCliProfile",
    "RustFeatureProfile",
    "RustLimits",
    "RustPackageProfile",
    "RustProfile",
    "RustTargetProfile",
    "canonical_rust_profile_bytes",
    "load_rust_profile",
    "rust_profile_projection_digest",
    "validate_rust_profile_api_plan",
]
