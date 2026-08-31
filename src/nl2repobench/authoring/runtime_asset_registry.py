"""Runtime-specific source asset validation below the canonical task model."""

from __future__ import annotations

import os
import re
import stat
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
_JAVA_JDK_VERSION = re.compile(
    r"^[A-Za-z][A-Za-z0-9._-]*-21\.0\.[0-9]+\+[0-9]+(?:\.[0-9]+)?$"
)
_JAVA_MAVEN_VERSION = re.compile(r"^3\.9\.[0-9]+$")
_JAVA_ALLOWED_ROOT_FILES = frozenset({"task.toml", "instruction.md"})
_JAVA_ALLOWED_METADATA_FILES = frozenset(
    {
        "api-inventory.json",
        "audit.md",
        "production-evidence.json",
        "provenance.json",
        "test-inventory.json",
    }
)
_JAVA_ALLOWED_METADATA_DIRECTORIES = frozenset({"evidence", "provenance"})
_JAVA_FORBIDDEN_PARTS = frozenset(
    {"target", ".mvn", "scripts", "script", "native", "plugins", "plugin"}
)
_JAVA_FORBIDDEN_FILES = frozenset(
    {
        "mvnw",
        "mvnw.cmd",
        "mvnw.ps1",
        "gradlew",
        "gradlew.bat",
        "build.gradle",
        "build.gradle.kts",
        "settings.gradle",
        "settings.gradle.kts",
    }
)
_JAVA_NATIVE_SUFFIXES = frozenset(
    {".so", ".dll", ".dylib", ".jnilib", ".a", ".o", ".exe", ".bat", ".cmd", ".sh"}
)
_JAVA_SOURCE_MAX_FILE_BYTES = 512 * 1024 * 1024
_JAVA_RESOURCE_MAX_FILE_BYTES = 512 * 1024 * 1024
_JAVA_METADATA_MAX_FILE_BYTES = 4 * 1024 * 1024
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
    "tests.protected_paths_artifact": "application/vnd.nl2repobench.protected-paths+json",
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
            "tests.protected_paths_artifact": source.tests.protected_paths_artifact,
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
class JavaSourceAssetValidator:
    """Validate the source-only Java workspace without executing Maven input."""

    identity = RuntimeDiscriminator(
        language=RuntimeLanguage.JAVA,
        package_manager=PackageManager.MAVEN,
    )

    def validate_source_assets(self, source_dir: Path, source: TaskSource) -> None:
        runtime = source.environment.runtime
        production = source.lifecycle.status in _PRODUCTION_STATUSES
        if runtime is None:
            if production:
                raise RuntimeSourceAssetError(
                    "production Java sources require an explicit java+maven runtime profile"
                )
        elif (
            runtime.runtime != "jdk"
            or not _JAVA_JDK_VERSION.fullmatch(runtime.version)
            or runtime.package_manager is not PackageManager.MAVEN
            or not _JAVA_MAVEN_VERSION.fullmatch(runtime.package_manager_version or "")
        ):
            raise RuntimeSourceAssetError(
                "Java sources require an exact JDK 21 and Maven 3.9.x profile"
            )

        if not source_dir.is_dir() or source_dir.is_symlink():
            raise RuntimeSourceAssetError("Java source directory must be a regular directory")
        for path in source_dir.rglob("*"):
            relative = path.relative_to(source_dir)
            parts = relative.parts
            try:
                path_stat = os.lstat(path)
            except OSError as exc:
                raise RuntimeSourceAssetError(
                    f"Java source asset cannot be inspected: {relative}"
                ) from exc
            if stat.S_ISLNK(path_stat.st_mode):
                raise RuntimeSourceAssetError(
                    f"Java source assets must not contain symlinks: {relative}"
                )
            if stat.S_ISDIR(path_stat.st_mode):
                if any(part in _JAVA_FORBIDDEN_PARTS for part in parts):
                    raise RuntimeSourceAssetError(f"Java source asset is forbidden: {relative}")
                continue
            if not stat.S_ISREG(path_stat.st_mode):
                raise RuntimeSourceAssetError(
                    f"Java source assets must be regular files or directories: {relative}"
                )
            if path_stat.st_nlink != 1:
                raise RuntimeSourceAssetError(
                    f"Java source assets must not contain hardlinks: {relative}"
                )
            name = path.name
            if name in _JAVA_FORBIDDEN_FILES or any(
                part in _JAVA_FORBIDDEN_PARTS for part in parts
            ):
                raise RuntimeSourceAssetError(f"Java source asset is forbidden: {relative}")
            if path.suffix.casefold() in _JAVA_NATIVE_SUFFIXES:
                raise RuntimeSourceAssetError(
                    f"Java source asset has a native or executable suffix: {relative}"
                )
            relative_text = relative.as_posix()
            if relative_text.startswith("src/main/java/"):
                max_bytes = _JAVA_SOURCE_MAX_FILE_BYTES
            elif relative_text.startswith("src/main/resources/"):
                max_bytes = _JAVA_RESOURCE_MAX_FILE_BYTES
            else:
                max_bytes = _JAVA_METADATA_MAX_FILE_BYTES
            if path_stat.st_size > max_bytes:
                raise RuntimeSourceAssetError(
                    f"Java source asset exceeds {max_bytes} byte limit: {relative}"
                )
            if relative_text == "pom.xml":
                try:
                    from nl2repobench.package_managers.maven import validate_candidate_pom

                    validate_candidate_pom(path.read_bytes())
                except (OSError, ValueError) as exc:
                    raise RuntimeSourceAssetError(f"Java candidate POM is invalid: {exc}") from exc
                continue
            if relative_text in _JAVA_ALLOWED_ROOT_FILES:
                continue
            if (
                len(parts) == 1 and name in _JAVA_ALLOWED_METADATA_FILES
            ) or parts[0] in _JAVA_ALLOWED_METADATA_DIRECTORIES:
                continue
            if relative_text.startswith("src/main/java/"):
                if path.suffix != ".java":
                    raise RuntimeSourceAssetError(
                        f"Java source path must contain only .java files: {relative}"
                    )
                continue
            if relative_text == "src/main/java":
                continue
            if relative_text.startswith("src/main/resources/"):
                continue
            if relative_text == "src/main/resources":
                continue
            # Authoring metadata is permitted, but executable project inputs are not.
            if relative.suffix in {".gradle", ".kts"}:
                raise RuntimeSourceAssetError(f"Java build script is forbidden: {relative}")
            raise RuntimeSourceAssetError(
                f"Java source asset is outside the allowed roots: {relative}"
            )

        java_files = tuple(
            path
            for path in source_dir.rglob("*.java")
            if path.is_file()
            and path.relative_to(source_dir).as_posix().startswith("src/main/java/")
        )
        if production and not java_files:
            raise RuntimeSourceAssetError("production Java sources require src/main/java/*.java")


@dataclass(frozen=True, slots=True)
class RuntimeSourceAssetRegistry:
    validators: Mapping[RuntimeDiscriminator, RuntimeSourceAssetValidator]

    @classmethod
    def default(cls) -> RuntimeSourceAssetRegistry:
        rust = RustSourceAssetValidator()
        java = JavaSourceAssetValidator()
        return cls({rust.identity: rust, java.identity: java})

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
            elif source.metadata.language is RuntimeLanguage.JAVA:
                JavaSourceAssetValidator().validate_source_assets(source_dir, source)
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
    "JavaSourceAssetValidator",
    "UnknownRuntimeSourceAssetValidatorError",
]
