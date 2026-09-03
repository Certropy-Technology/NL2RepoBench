from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.harbor.java_compiler import JavaHarborCompileError, JavaHarborCompiler
from nl2repobench.harbor.java_toolchain import load_java_toolchain_lock

ROOT = Path(__file__).parents[1]


def test_observed_java_toolchain_is_exact_but_not_production_ready() -> None:
    toolchain = load_java_toolchain_lock(ROOT / "toolchain.java.dev.lock.toml")

    assert toolchain.jdk_version == "temurin-21.0.12+8"
    assert toolchain.maven_version == "3.9.11"
    assert toolchain.agent_runtime_build_ref == "python:3.12"
    assert toolchain.production_ready is False


def test_java_compiler_fails_closed_until_the_vertical_slice_is_complete(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "instruction.md").write_text("# Java\n", encoding="utf-8")
    (source / "task.toml").write_text(
        """schema_version = "1.0"
task_id = "java-synthetic"
instruction = "instruction.md"

[metadata]
language = "java"

[environment]
status = "unknown"

[environment.runtime]
language = "java"
runtime = "jdk"
version = "temurin-21.0.12+8"
package_manager = "maven"
package_manager_version = "3.9.11"

[dependencies]
status = "unknown"
installer = "maven"

[tests]
framework = "junit-platform"
report_format = "junit-open-test-report-xml-v1"
expected_total = 1
commands = ["mvn -o test"]
""",
        encoding="utf-8",
    )

    with pytest.raises(JavaHarborCompileError, match=r"missing \[harbor\]"):
        JavaHarborCompiler(ROOT / "toolchain.java.dev.lock.toml").compile_task(
            source, tmp_path / "out"
        )


def test_java_verifier_script_bounds_candidate_execution() -> None:
    source = ROOT / "tests/fixtures/java-ministats"
    descriptor = CatalogCompiler.load_task(source)
    assert descriptor.harbor is not None
    script = JavaHarborCompiler._test_script(descriptor.tests.expected_total, descriptor.harbor)

    assert "timeout --signal=KILL 90s" in script
    assert "timeout --signal=KILL 300s" in script
    assert "--uid 10001" in script
    assert "verifier-internal-error" in script
