from __future__ import annotations

from pathlib import Path

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.harbor.registry import HarborCompilerRegistry


class _FakeCompiler:
    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        del source_dir, allow_incomplete
        return output_root / "fake"

    def prepare_control_bundle(
        self,
        task_root: Path,
        kind: str,
        output_root: Path,
    ) -> Path:
        del task_root, kind
        return output_root / "control"


def test_registry_resolves_exact_identity_without_language_branch() -> None:
    calls: list[tuple[Path, bool]] = []

    def factory(toolchain: Path, resolver: object) -> _FakeCompiler:
        del resolver
        calls.append((toolchain, True))
        return _FakeCompiler()

    identity = RuntimeDiscriminator(
        language=RuntimeLanguage.NODE,
        package_manager=PackageManager.PNPM,
    )
    registry = HarborCompilerRegistry(
        factories={(RuntimeLanguage.NODE, PackageManager.PNPM): factory}
    )
    resolved = registry.resolve(identity)
    assert resolved(Path("toolchain.lock.toml"), None).compile_task(
        Path("source"), Path("output"), allow_incomplete=True
    ) == Path("output/fake")
    assert calls == [(Path("toolchain.lock.toml"), True)]


def test_registry_resolves_registered_pnpm_identity() -> None:
    registry = HarborCompilerRegistry.default()
    factory = registry.resolve(
        RuntimeDiscriminator(
            language=RuntimeLanguage.NODE,
            package_manager=PackageManager.PNPM,
        )
    )
    assert factory.__name__ == "node_pnpm_factory"


def test_registry_resolves_registered_java_maven_identity() -> None:
    registry = HarborCompilerRegistry.default()
    factory = registry.resolve(
        RuntimeDiscriminator(
            language=RuntimeLanguage.JAVA,
            package_manager=PackageManager.MAVEN,
        )
    )
    assert factory.__name__ == "java_maven_factory"
