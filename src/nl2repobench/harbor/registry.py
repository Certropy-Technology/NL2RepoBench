"""Explicit Harbor compiler registry.

The registry is the single routing point between the unified runtime
discriminator and runtime-specific compiler implementations.  The generic
CLI does not contain language branches; adding a language or package manager
means registering one adapter and its focused tests.  Unknown combinations
fail closed instead of silently using a similar toolchain.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

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

        python_keys = {
            (RuntimeLanguage.PYTHON, PackageManager.UV),
            (RuntimeLanguage.PYTHON, PackageManager.PIP),
            (RuntimeLanguage.PYTHON, PackageManager.NONE),
        }
        factories = {key: python_factory for key in python_keys}
        factories[(RuntimeLanguage.NODE, PackageManager.NPM)] = node_npm_factory
        factories[(RuntimeLanguage.NODE, PackageManager.PNPM)] = node_pnpm_factory
        factories[(RuntimeLanguage.GO, PackageManager.GO_MODULES)] = go_modules_factory
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


__all__ = [
    "HarborCompilerRegistry",
    "HarborRuntimeCompiler",
    "UnknownRuntimeAdapterError",
]
