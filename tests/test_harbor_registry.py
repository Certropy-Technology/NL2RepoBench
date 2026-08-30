from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.harbor.node_compiler import NodeHarborCompiler
from nl2repobench.harbor.pnpm_compiler import PnpmHarborCompiler
from nl2repobench.harbor.registry import HarborCompilerRegistry

ROOT = Path(__file__).parents[1]


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


@pytest.mark.parametrize(
    ("manager", "version", "compiler_type"),
    [
        ("npm", "10.9.8", NodeHarborCompiler),
        ("pnpm", "9.15.0", PnpmHarborCompiler),
    ],
)
def test_registry_routes_canonical_node_sources_to_concrete_adapters(
    tmp_path: Path,
    manager: str,
    version: str,
    compiler_type: type[NodeHarborCompiler],
) -> None:
    source = tmp_path / manager
    source.mkdir()
    (source / "instruction.md").write_text("# Canonical Node source\n", encoding="utf-8")
    (source / "task.toml").write_text(
        f'''schema_version = "1.0"
task_id = "node-{manager}"
instruction = "instruction.md"

[metadata]
language = "node"

[source]
status = "unknown"

[environment]
status = "unknown"

[environment.runtime]
language = "node"
runtime = "node"
version = "22.23.1"
package_manager = "{manager}"
package_manager_version = "{version}"

[dependencies]
status = "unknown"
package_manager = "{manager}"

[tests]
framework = "node:test"
report_format = "node-test-json-v1"
''',
        encoding="utf-8",
    )

    compiler = HarborCompilerRegistry.default().compiler_for_source(
        source,
        ROOT / "toolchain.node.dev.lock.toml",
    )

    assert isinstance(compiler, compiler_type)
