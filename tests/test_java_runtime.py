from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.harbor.java_compiler import JavaHarborCompileError, JavaHarborCompiler
from nl2repobench.harbor.java_toolchain import load_java_toolchain_lock
from nl2repobench.verification.java_process import run_java_process

ROOT = Path(__file__).parents[1]


def test_observed_java_toolchain_is_exact_but_not_production_ready() -> None:
    toolchain = load_java_toolchain_lock(ROOT / "toolchain.java.dev.lock.toml")

    assert toolchain.jdk_version == "temurin-21.0.12+8"
    assert toolchain.maven_version == "3.9.11"
    assert toolchain.agent_runtime_build_ref == "python:3.12"
    assert toolchain.runtime_base_ref == toolchain.runtime_build_ref
    assert toolchain.agent_runtime_base_ref == toolchain.agent_runtime_build_ref
    assert toolchain.production_ready is False


def test_locked_java_toolchain_uses_digest_refs_for_docker_inputs() -> None:
    toolchain = load_java_toolchain_lock(ROOT / "toolchain.java.lock.toml")

    assert toolchain.runtime_base_ref == toolchain.runtime_image
    assert toolchain.agent_runtime_base_ref == toolchain.agent_runtime_image
    assert "@sha256:" in toolchain.runtime_base_ref
    assert "@sha256:" in toolchain.agent_runtime_base_ref
    assert toolchain.runtime_build_ref == toolchain.runtime_image
    assert toolchain.agent_runtime_build_ref == toolchain.agent_runtime_image


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

    assert "nl2repobench.verification.java_process" in script
    assert "--timeout-sec 90" in script
    assert "--timeout-sec 300" in script
    assert "--uid 10001" in script
    assert "--uid 0" in script
    assert "runuser" not in script
    assert "-Xmx256m" in script
    assert "MaxMetaspaceSize=128m" in script
    assert "CompressedClassSpaceSize=64m" in script
    assert "--release 21" in script
    assert "find /tmp/java-harness -type d -exec chmod 0555" in script
    assert "find /tmp/java-harness -type f -exec chmod 0444" in script
    assert "verifier-internal-error" in script


def test_java_process_supervisor_bounds_and_cleans_a_process_group(tmp_path: Path) -> None:
    result = run_java_process(
        ["/bin/sh", "-c", "printf bounded"],
        cwd=tmp_path,
        uid=0,
        timeout_sec=1,
        environment={"PATH": "/usr/bin:/bin"},
    )

    assert result.return_code == 0
    assert result.signal is None
    assert result.timed_out is False
    assert result.stdout == "bounded"


def test_java_process_supervisor_reports_timeout(tmp_path: Path) -> None:
    result = run_java_process(
        ["/bin/sh", "-c", "sleep 1"],
        cwd=tmp_path,
        uid=0,
        timeout_sec=0.1,
        environment={"PATH": "/usr/bin:/bin"},
    )

    assert result.timed_out is True
    assert result.return_code is None
    assert result.spawn_error is None


def test_java_process_supervisor_allows_jvm_virtual_reservations() -> None:
    from nl2repobench.verification.java_process import DEFAULT_ADDRESS_SPACE_BYTES

    assert DEFAULT_ADDRESS_SPACE_BYTES == 4 * 1024 * 1024 * 1024
