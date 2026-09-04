"""Explicit Harbor compiler registry.

The registry is the single routing point between the unified runtime
discriminator and runtime-specific compiler implementations.  The generic
CLI does not contain language branches; adding a language or package manager
means registering one adapter and its focused tests.  Unknown combinations
fail closed instead of silently using a similar toolchain.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.runtime import (
    PackageManager,
    RuntimeDiscriminator,
    RuntimeLanguage,
)
from nl2repobench.storage.artifacts import LocalArtifactResolver


class HarborRuntimeCompiler(Protocol):
    """Minimal compiler surface owned by every runtime adapter."""

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path: ...

    def prepare_control_bundle(
        self,
        task_root: Path,
        kind: str,
        output_root: Path,
        *,
        private_cas_root: Path | None = None,
    ) -> Path: ...


class UnknownRuntimeAdapterError(ValueError):
    """Raised when no compiler is registered for a runtime identity."""


RuntimeKey = tuple[RuntimeLanguage, PackageManager]
CompilerFactory = Callable[[Path, LocalArtifactResolver | None], HarborRuntimeCompiler]


@dataclass(frozen=True)
class HarborCompilerRegistry:
    """Resolve explicit runtime identities to compiler instances.

    Factories are injected so registry tests can use fakes and future language
    adapters do not need Docker, Harbor, or filesystem setup.  The default
    registry imports concrete compilers lazily at resolution time, keeping the
    generic CLI import graph small and avoiding eager Node-only dependencies.
    """

    factories: Mapping[RuntimeKey, CompilerFactory]

    @classmethod
    def default(cls) -> HarborCompilerRegistry:
        """Create the production registry for currently implemented adapters."""

        def python_factory(
            toolchain: Path, resolver: LocalArtifactResolver | None
        ) -> HarborRuntimeCompiler:
            from nl2repobench.harbor.compiler import HarborCompiler

            return HarborCompiler(toolchain, artifact_resolver=resolver)

        def node_npm_factory(
            toolchain: Path, resolver: LocalArtifactResolver | None
        ) -> HarborRuntimeCompiler:
            from nl2repobench.harbor.node_compiler import NodeHarborCompiler

            return NodeHarborCompiler(toolchain, artifact_resolver=resolver)

        def node_pnpm_factory(
            toolchain: Path, resolver: LocalArtifactResolver | None
        ) -> HarborRuntimeCompiler:
            from nl2repobench.harbor.pnpm_compiler import PnpmHarborCompiler

            return PnpmHarborCompiler(toolchain, artifact_resolver=resolver)

        def go_modules_factory(
            toolchain: Path, resolver: LocalArtifactResolver | None
        ) -> HarborRuntimeCompiler:
            from nl2repobench.harbor.go_compiler import GoHarborCompiler

            return GoHarborCompiler(toolchain, artifact_resolver=resolver)

        def java_maven_factory(
            toolchain: Path, resolver: LocalArtifactResolver | None
        ) -> HarborRuntimeCompiler:
            from nl2repobench.harbor.java_compiler import JavaHarborCompiler

            return JavaHarborCompiler(toolchain, artifact_resolver=resolver)

        python_keys = {
            (RuntimeLanguage.PYTHON, PackageManager.UV),
            (RuntimeLanguage.PYTHON, PackageManager.PIP),
            (RuntimeLanguage.PYTHON, PackageManager.NONE),
        }
        factories = {key: python_factory for key in python_keys}
        factories[(RuntimeLanguage.NODE, PackageManager.NPM)] = node_npm_factory
        factories[(RuntimeLanguage.NODE, PackageManager.PNPM)] = node_pnpm_factory
        factories[(RuntimeLanguage.GO, PackageManager.GO_MODULES)] = go_modules_factory
        factories[(RuntimeLanguage.JAVA, PackageManager.MAVEN)] = java_maven_factory
        return cls(factories=factories)

    def resolve(self, identity: RuntimeDiscriminator) -> CompilerFactory:
        """Return the exact registered factory for ``identity``."""

        key = (identity.language, identity.package_manager)
        try:
            return self.factories[key]
        except KeyError as exc:
            available = ", ".join(
                f"{language.value}+{manager.value}"
                for language, manager in sorted(
                    self.factories, key=lambda item: (item[0].value, item[1].value)
                )
            )
            raise UnknownRuntimeAdapterError(
                f"no Harbor compiler for {identity.language.value}+"
                f"{identity.package_manager.value}; registered: {available}"
            ) from exc

    def compiler_for_source(
        self,
        source_dir: Path,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> HarborRuntimeCompiler:
        """Load a source, resolve its identity, and construct its compiler."""

        source = CatalogCompiler.load_task(source_dir)
        identity = RuntimeDiscriminator.from_catalog_source(source.model_dump(mode="python"))
        if artifact_resolver is not None:
            artifact_resolver = artifact_resolver.scoped(
                _private_artifact_digests(source.model_dump(mode="python"))
            )
        return self.resolve(identity)(toolchain_path, artifact_resolver)

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
        allow_incomplete: bool = False,
    ) -> Path:
        """Compile one source through its registered runtime adapter."""

        compiler = self.compiler_for_source(
            source_dir,
            toolchain_path,
            artifact_resolver=artifact_resolver,
        )
        return compiler.compile_task(
            source_dir,
            output_root,
            allow_incomplete=allow_incomplete,
        )
    def prepare_control_bundle(
        self,
        task_root: Path,
        kind: str,
        output_root: Path,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> Path:
        """Prepare a control through the compiler matching the bundle runtime.

        Compiled Harbor bundles carry their runtime identity in ``task.toml``.
        Reading that generated metadata keeps the CLI free of language branches
        and prevents a Node bundle from being passed to the Python lock parser.
        """

        identity = self._runtime_for_compiled_task(task_root)
        if artifact_resolver is not None:
            declared: dict[str, object] = {}
            for relative in (
                "tests/private-artifact-refs.json",
                "solution/oracle-ref.json",
            ):
                path = task_root / relative
                if path.is_file() and not path.is_symlink():
                    try:
                        value = json.loads(path.read_text(encoding="utf-8"))
                    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise UnknownRuntimeAdapterError(
                            f"invalid private artifact refs: {path}"
                        ) from exc
                    if isinstance(value, dict):
                        declared[relative] = value
            artifact_resolver = artifact_resolver.scoped(
                _private_artifact_digests(declared)
            )
        compiler = self.resolve(identity)(toolchain_path, artifact_resolver)
        if identity == RuntimeDiscriminator(
            language=RuntimeLanguage.JAVA,
            package_manager=PackageManager.MAVEN,
        ):
            prepare_java = cast(Any, compiler).prepare_control_bundle
            return cast(Path, prepare_java(
                task_root,
                kind,
                output_root,
                private_cas_root=output_root / ".private-cas",
            ))
        return compiler.prepare_control_bundle(task_root, kind, output_root)

    def prepare_run_bundle(
        self,
        task_root: Path,
        role: str,
        output_root: Path,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
        private_cas_root: Path | None = None,
    ) -> Path:
        """Prepare a runtime role copy with task-scoped private artifacts."""

        identity = self._runtime_for_compiled_task(task_root)
        compiler = self.resolve(identity)(toolchain_path, artifact_resolver)
        method = getattr(compiler, "prepare_run_bundle", None)
        if not callable(method):
            raise UnknownRuntimeAdapterError(
                f"runtime {identity.language.value}+{identity.package_manager.value} "
                "does not support role-scoped run preparation"
            )
        prepare = cast("Callable[..., Path]", method)
        return prepare(task_root, role, output_root, private_cas_root)

    @staticmethod
    def _runtime_for_compiled_task(task_root: Path) -> RuntimeDiscriminator:
        path = task_root / "task.toml"
        if path.is_symlink() or not path.is_file():
            raise UnknownRuntimeAdapterError(f"compiled task metadata is missing: {path}")
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            raise UnknownRuntimeAdapterError(
                f"invalid compiled task metadata {path}: {exc}"
            ) from exc

        metadata = data.get("metadata")
        if not isinstance(metadata, Mapping):
            raise UnknownRuntimeAdapterError("compiled task metadata must contain [metadata]")
        language = metadata.get("language")
        package_manager = metadata.get("package_manager")
        if language is None:
            manifest_path = task_root / "bundle.manifest.json"
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise UnknownRuntimeAdapterError(
                    f"compiled task runtime identity is missing: {manifest_path}"
                ) from exc
            if manifest.get("schema_version") == "1.0":
                # v1 Harbor task metadata predates the unified runtime fields.
                # Its compiler is Python-only, so preserve that established
                # dispatch while rejecting unknown bundle shapes.
                language = RuntimeLanguage.PYTHON.value
                package_manager = PackageManager.NONE.value
        if not isinstance(language, str) or not isinstance(package_manager, str):
            raise UnknownRuntimeAdapterError(
                "compiled task metadata must declare language and package_manager"
            )
        try:
            return RuntimeDiscriminator(
                language=RuntimeLanguage(language),
                package_manager=PackageManager(package_manager),
            )
        except ValueError as exc:
            raise UnknownRuntimeAdapterError(
                f"invalid compiled task runtime: {language}+{package_manager}"
            ) from exc


def _private_artifact_digests(value: object) -> frozenset[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        if value.get("visibility") == "private" and isinstance(value.get("digest"), str):
            found.add(value["digest"])
        for child in value.values():
            found.update(_private_artifact_digests(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_private_artifact_digests(child))
    return frozenset(found)


__all__ = [
    "HarborCompilerRegistry",
    "HarborRuntimeCompiler",
    "UnknownRuntimeAdapterError",
]
