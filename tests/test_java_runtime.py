from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.canonical_contract import (
    DependencyBundle,
    EnvironmentLock,
    PackageManager,
    RuntimeLanguage,
    RuntimeProfile,
    TaskMetadata,
    TaskSource,
)
from nl2repobench.domain.canonical_contract import TestManifest as CanonicalTestManifest
from nl2repobench.domain.command_plan import CommandPlan
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.harbor.java_compiler import JavaHarborCompileError, JavaHarborCompiler
from nl2repobench.harbor.registry import HarborCompilerRegistry
from nl2repobench.harbor.task_writer import copy_python_verifier_runtime
from nl2repobench.runtimes.java import JavaRuntimeAdapter
from nl2repobench.verification.leaf_report import LeafCase


def test_java_profile_and_runtime_identity_are_exact() -> None:
    profile = RuntimeProfile(
        language="java",
        runtime="jdk",
        version="temurin-21.0.5+11",
        package_manager="maven",
        package_manager_version="3.9.9",
    )
    assert profile.language is RuntimeLanguage.JAVA
    assert profile.package_manager is PackageManager.MAVEN
    assert JavaRuntimeAdapter.identity == RuntimeDiscriminator(
        language=RuntimeLanguage.JAVA,
        package_manager=PackageManager.MAVEN,
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("runtime", "java", "Input should be"),
        ("version", "21", "distribution and exact JDK 21"),
        ("version", "latest", "distribution and exact JDK 21"),
        ("version", "temurin-17.0.12+7", "distribution and exact JDK 21"),
        ("package_manager_version", "3.8.8", "exact supported 3.9.x"),
        ("package_manager_version", "3.9.x", "exact supported 3.9.x"),
    ],
)
def test_java_profile_rejects_inexact_or_unsupported_values(
    field: str, value: str, message: str
) -> None:
    payload = {
        "language": "java",
        "runtime": "jdk",
        "version": "temurin-21.0.5+11",
        "package_manager": "maven",
        "package_manager_version": "3.9.9",
    }
    payload[field] = value
    with pytest.raises(ValidationError, match=message):
        RuntimeProfile.model_validate(payload)


def test_java_junit_pair_and_command_report_are_canonical() -> None:
    tests = CanonicalTestManifest(
        framework="junit-platform",
        report_format="junit-open-test-report-xml-v1",
    )
    plan = CommandPlan(
        identity="java+maven",
        runner="junit-open-test-subprocess-boundary-v1",
        candidate_install="maven-source-compile-offline-v1",
        report_format="junit-open-test-report-xml-v1",
    )
    assert tests.framework == "junit-platform"
    assert plan.identity == "java+maven"
    source = TaskSource(
        task_id="java-synthetic",
        metadata=TaskMetadata(language="java"),
        environment=EnvironmentLock(
            status="unknown",
            runtime=RuntimeProfile(
                language="java",
                runtime="jdk",
                version="temurin-21.0.5+11",
                package_manager="maven",
                package_manager_version="3.9.9",
            ),
        ),
        dependencies=DependencyBundle(status="unknown", package_manager="maven"),
        tests=tests,
    )
    assert source.environment.runtime is not None
    with pytest.raises(ValidationError):
        CanonicalTestManifest(
            framework="custom", report_format="junit-open-test-report-xml-v1"
        )
    with pytest.raises(ValidationError):
        CanonicalTestManifest(framework="junit-platform", report_format="custom-json-v1")


def test_java_harbor_compiler_is_registered_and_fails_closed_without_toolchain(
    tmp_path: Path,
) -> None:
    factory = HarborCompilerRegistry.default().resolve(JavaRuntimeAdapter.identity)
    compiler = factory(tmp_path / "toolchain.java.lock.toml", None)
    assert isinstance(compiler, JavaHarborCompiler)
    with pytest.raises(JavaHarborCompileError, match="toolchain lock is unavailable"):
        compiler.compile_task(tmp_path / "source", tmp_path / "output")


def test_java_grader_export_is_lazy_and_strict() -> None:
    source_root = Path(__file__).parents[1] / "src"
    probe = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            (
                "import sys\n"
                f"sys.path.insert(0, {str(source_root)!r})\n"
                "import nl2repobench.verification as verification\n"
                "print('java_grader' in sys.modules)\n"
                "print('grade_java_report' in verification.__all__)\n"
                "from nl2repobench.verification import grade_java_report\n"
                "print(callable(grade_java_report))\n"
                "try:\n"
                "    verification.not_a_public_export\n"
                "except AttributeError:\n"
                "    print('strict')\n"
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert probe.returncode == 0, probe.stderr
    assert probe.stdout.splitlines() == ["False", "True", "True", "strict"]


def test_copied_verifier_runtime_imports_without_java_modules(tmp_path: Path) -> None:
    destination = tmp_path / "runtime"
    copy_python_verifier_runtime(destination)
    assert not (destination / "nl2repobench/verification/java_grader.py").exists()
    assert not (
        destination / "nl2repobench/verification/normalize/junit_open_test_report.py"
    ).exists()
    probe = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            (
                "import sys\n"
                f"sys.path.insert(0, {str(destination)!r})\n"
                "import nl2repobench.verification.cli\n"
                "print('imported')\n"
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert probe.returncode == 0, probe.stderr
    assert probe.stdout.strip() == "imported"


def test_leaf_display_name_is_optional_and_null_serialization_is_unchanged() -> None:
    old_shape = LeafCase(leaf_id="test.py::test_ok", status="passed")
    assert canonical_json(old_shape) == (
        b'{"duration_ms":0.0,"leaf_id":"test.py::test_ok",'
        b'"schema_version":"1.0","status":"passed"}'
    )
    named = LeafCase(leaf_id="[engine:junit]", display_name="works", status="passed")
    assert b'"display_name":"works"' in canonical_json(named)


@pytest.mark.parametrize(
    ("framework", "report_format"),
    [
        ("pytest", "pytest-junit-xml-v1"),
        ("node:test", "node-test-json-v1"),
        ("go", "go-test-json-v1"),
    ],
)
def test_existing_runtime_leaf_report_bytes_omit_null_display_name(
    framework: str, report_format: str
) -> None:
    from nl2repobench.verification.leaf_report import LeafReport

    report = LeafReport(
        framework=framework,
        report_format=report_format,
        collected=1,
        leaves=(LeafCase(leaf_id="case", status="passed"),),
        frozen_total=1,
    )
    assert b"display_name" not in canonical_json(report)
