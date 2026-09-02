"""Fail-closed Harbor entry point for the Java/Maven runtime lane.

The Java domain and package-manager contracts are usable without Docker, but
this checkout does not contain an exact JDK/Maven toolchain lock.  Keeping the
compiler entry point explicit lets registry and source validation exercise the
lane without generating an unverifiable runtime bundle.
"""

from __future__ import annotations

from pathlib import Path

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.canonical_contract import PackageManager, RuntimeLanguage
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.harbor.java_toolchain import load_java_toolchain_lock
from nl2repobench.storage.artifacts import LocalArtifactResolver

JAVA_MAVEN = RuntimeDiscriminator(
    language=RuntimeLanguage.JAVA,
    package_manager=PackageManager.MAVEN,
)


class JavaHarborCompileError(ValueError):
    """Raised when Java compilation lacks an independently verified toolchain."""


class JavaHarborCompiler:
    """Expose the Java compiler seam while production inputs remain unavailable."""

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        self.toolchain_path = toolchain_path
        self.artifact_resolver = artifact_resolver

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        """Validate Java source identity, then stop before unverifiable packaging."""

        try:
            toolchain = load_java_toolchain_lock(self.toolchain_path)
        except ValueError as exc:
            raise JavaHarborCompileError(str(exc)) from exc
        source = CatalogCompiler.load_task(source_dir)
        runtime = source.environment.runtime
        if (
            runtime is None
            or runtime.language is not RuntimeLanguage.JAVA
            or runtime.package_manager is not PackageManager.MAVEN
        ):
            raise JavaHarborCompileError("Java compiler requires the java+maven runtime identity")
        if not toolchain.production_ready:
            raise JavaHarborCompileError(
                "Java/Maven toolchain is observed but not production-ready: "
                "Java Agent image binding and private verifier/Oracle artifacts are unavailable"
            )
        mode = "development" if allow_incomplete else "production"
        raise JavaHarborCompileError(
            f"Java/Maven {mode} compilation is blocked until an exact JDK 21/Maven "
            "toolchain lock and image-bound offline closure are supplied"
        )

    def prepare_control_bundle(
        self,
        task_root: Path,
        kind: str,
        output_root: Path,
    ) -> Path:
        """Never prepare controls before a Java runtime and verifier are bound."""

        del task_root, kind, output_root
        raise JavaHarborCompileError(
            "Java/Maven controls are blocked until the exact toolchain and verifier runtime exist"
        )


__all__ = ["JAVA_MAVEN", "JavaHarborCompileError", "JavaHarborCompiler"]
