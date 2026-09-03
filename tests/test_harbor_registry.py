from __future__ import annotations

from pathlib import Path

import tomli_w

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


def test_control_resolution_uses_the_compiled_java_runtime_identity(tmp_path: Path) -> None:
    task_root = tmp_path / "task"
    task_root.mkdir()
    (task_root / "task.toml").write_text(
        tomli_w.dumps(
            {
                "metadata": {
                    "language": "java",
                    "package_manager": "maven",
                }
            }
        ),
        encoding="utf-8",
    )
    registry = HarborCompilerRegistry.default()

    identity = registry._runtime_for_compiled_task(task_root)

    assert identity == RuntimeDiscriminator(
        language=RuntimeLanguage.JAVA,
        package_manager=PackageManager.MAVEN,
    )
