from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tomllib
from pathlib import Path

import pytest
import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.models import Visibility
from nl2repobench.harbor.java_compiler import JavaHarborCompileError, JavaHarborCompiler
from nl2repobench.harbor.java_toolchain import load_java_toolchain_lock
from nl2repobench.package_managers.dependency_artifacts import (
    LOCK_MEDIA_TYPE,
    STORE_MEDIA_TYPE,
    put_dependency_archive,
    put_dependency_inventory,
)
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.canonical_ustar import CanonicalEntry, encode_ustar
from nl2repobench.verification import java_process
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


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("jdk_version", "openjdk-21", "exact Temurin"),
        ("maven_version", "4.0.0", "exact Maven"),
        ("expected_jdk_base", "eclipse-temurin:21", "JDK base image digest"),
        ("expected_maven_base", "maven:3.9", "Maven base image digest"),
        ("runtime_image", "java:latest", "digest pinned"),
        ("runtime_build_ref", "local tag", "valid local image"),
        ("java_runtime_sha256", None, "runtime helper digest"),
        ("java_oracle_agent_sha256", None, "Oracle agent digest"),
    ],
)
def test_locked_java_toolchain_rejects_invalid_identity(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    data = tomllib.loads((ROOT / "toolchain.java.lock.toml").read_text())
    if value is None:
        data.pop(field)
    else:
        data[field] = value
    path = tmp_path / "toolchain.toml"
    path.write_text(tomli_w.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_java_toolchain_lock(path)


def test_java_toolchain_loader_rejects_symlink_and_oversized_file(tmp_path: Path) -> None:
    target = tmp_path / "target.toml"
    target.write_text("schema_version = '1.0'\n", encoding="utf-8")
    linked = tmp_path / "linked.toml"
    linked.symlink_to(target)
    with pytest.raises(ValueError, match="regular file"):
        load_java_toolchain_lock(linked)

    oversized = tmp_path / "oversized.toml"
    oversized.write_bytes(b" " * (64 * 1024 + 1))
    with pytest.raises(ValueError, match="size limit"):
        load_java_toolchain_lock(oversized)


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
package_manager = "maven"

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
    assert "candidate-classes" in script
    assert "trusted-classes" in script
    assert "candidate.classpath" in script
    assert "candidate.timeout=300" in script
    assert "-Dmaven.repo.local=/tmp/java-dependencies/maven-repository" in script
    assert "java_private_artifacts" in script
    assert "private-artifact-refs.json" in script
    assert "/nl2repo/private-cas" in script
    assert "rm -rf /tmp/java-harness/src" in script
    assert "find /tmp/java-harness/candidate-src" in script
    assert "verifier-internal-error" in script


def test_java_production_verifier_uses_cas_refs_instead_of_private_tree() -> None:
    source = ROOT / "tests/fixtures/java-ministats"
    descriptor = CatalogCompiler.load_task(source)
    assert descriptor.harbor is not None
    script = JavaHarborCompiler._test_script(
        descriptor.tests.expected_total,
        descriptor.harbor,
        allow_incomplete=False,
    )

    assert "java_private_artifacts" in script
    assert "/tests/private-artifact-refs.json" in script
    assert "/nl2repo/private-cas" in script
    assert "/tests/private/harness" not in script
    assert "/opt/maven/repository" not in script


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


def test_java_timeout_reason_is_preserved_in_legacy_grading_output() -> None:
    from nl2repobench.verification.evaluator import failure_result_for_reason
    from nl2repobench.verification.java_grader import write_java_grading_outputs
    from nl2repobench.verification.metric_contract import MetricContract
    from nl2repobench.verification.taxonomy import VerificationReason

    result = failure_result_for_reason(
        contract=MetricContract(),
        expected_total=4,
        reason=VerificationReason.CANDIDATE_TIMEOUT,
        runner_exit_code=None,
    )
    output = ROOT / "tests/.tmp-java-grading"
    try:
        write_java_grading_outputs(result, output)
        grading = json.loads((output / "grading.json").read_text(encoding="utf-8"))
        assert grading["expected_total"] == 4
        assert grading["failure_reason"] == "candidate-timeout"
    finally:
        shutil.rmtree(output, ignore_errors=True)


def test_java_process_supervisor_rejects_untrusted_environment_variables(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsafe variable"):
        run_java_process(
            ["/bin/true"],
            cwd=tmp_path,
            uid=0,
            timeout_sec=1,
            environment={"API_KEY": "must-not-leak"},
        )


def test_java_process_supervisor_does_not_inherit_secret_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("API_KEY", "must-not-leak")
    monkeypatch.setenv("MAVEN_OPTS", "-Dmust.not.inherit=true")
    result = run_java_process(
        ["/usr/bin/env"],
        cwd=tmp_path,
        uid=0,
        timeout_sec=1,
        environment={"PATH": "/usr/bin:/bin"},
    )

    assert result.return_code == 0
    assert "API_KEY" not in result.stdout
    assert "MAVEN_OPTS" not in result.stdout


def test_java_process_supervisor_kills_descendant_process_group(tmp_path: Path) -> None:
    pid_file = tmp_path / "child.pid"
    result = run_java_process(
        ["/bin/sh", "-c", f"sleep 30 & echo $! > {pid_file}; wait"],
        cwd=tmp_path,
        uid=0,
        timeout_sec=0.1,
        environment={"PATH": "/usr/bin:/bin"},
    )

    assert result.timed_out is True
    child_pid = int(pid_file.read_text(encoding="utf-8"))
    with pytest.raises(ProcessLookupError):
        __import__("os").kill(child_pid, 0)


def test_java_process_supervisor_allows_jvm_virtual_reservations() -> None:
    from nl2repobench.verification.java_process import DEFAULT_ADDRESS_SPACE_BYTES

    assert DEFAULT_ADDRESS_SPACE_BYTES == 4 * 1024 * 1024 * 1024


def test_java_harness_rejects_parallel_runuser_launcher(tmp_path: Path) -> None:
    harness = tmp_path / "harness"
    source = harness / "src/main/java/nl2repobench/harness"
    source.mkdir(parents=True)
    (harness / "pom.xml").write_text("<project/>", encoding="utf-8")
    (source / "CandidateMain.java").write_text("class CandidateMain {}", encoding="utf-8")
    (source / "ContractMain.java").write_text(
        'class ContractMain { String launcher = "runuser"; }',
        encoding="utf-8",
    )

    with pytest.raises(JavaHarborCompileError, match="contract_sha256"):
        JavaHarborCompiler._validate_harness(tmp_path)  # noqa: SLF001


def test_java_process_cli_writes_success_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = tmp_path / "report.json"
    stdout = tmp_path / "stdout.txt"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "java-process",
            "--report",
            str(report),
            "--stdout-path",
            str(stdout),
            "--cwd",
            str(tmp_path),
            "--uid",
            str(os.getuid()),
            "--timeout-sec",
            "2",
            "--",
            "/bin/echo",
            "cli-output",
        ],
    )

    assert java_process._main() == 0  # noqa: SLF001
    assert json.loads(report.read_text())["return_code"] == 0
    assert stdout.read_text() == "cli-output\n"


def test_java_process_cli_maps_timeout_and_spawn_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = tmp_path / "timeout.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "java-process",
            "--report",
            str(report),
            "--cwd",
            str(tmp_path),
            "--uid",
            str(os.getuid()),
            "--timeout-sec",
            "0.05",
            "--",
            "/bin/sleep",
            "1",
        ],
    )
    assert java_process._main() == 2  # noqa: SLF001

    report = tmp_path / "spawn.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "java-process",
            "--report",
            str(report),
            "--cwd",
            str(tmp_path),
            "--uid",
            str(os.getuid()),
            "--timeout-sec",
            "1",
            "--",
            "/missing-command",
        ],
    )
    assert java_process._main() == 3  # noqa: SLF001


def test_java_production_compile_and_role_scoped_preparation(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    lock_data = (
        b'{"artifacts":[],"effective_project":{"artifact_id":"harness",'
        b'"group_id":"example","packaging":"jar","release":21,"version":"1.0.0"},'
        b'"jdk_version":"temurin-21.0.12+8","maven_version":"3.9.11",'
        b'"offline_smoke":{"status":"passed"},"plugins":[],"repositories":[],'
        b'"schema_version":"1.0"}\n'
    )
    lock_entries = (CanonicalEntry("maven-lock-v1.json", "file", 0o444, lock_data),)
    store_entries = (CanonicalEntry("maven-repository/", "directory", 0o555),)
    lock_ref = put_dependency_archive(store, lock_entries, media_type=LOCK_MEDIA_TYPE)
    store_ref = put_dependency_archive(store, store_entries, media_type=STORE_MEDIA_TYPE)
    toolchain_digest = "sha256:" + hashlib.sha256(
        (ROOT / "toolchain.java.lock.toml").read_bytes()
    ).hexdigest()
    inventory_ref = put_dependency_inventory(
        store,
        identity="java+maven",
        adapter_version="maven-offline-v1",
        toolchain_digest=toolchain_digest,
        lock_ref=lock_ref,
        lock_entries=lock_entries,
        store_ref=store_ref,
        store_entries=store_entries,
        smoke_command_id="maven-validate-offline-v1",
    )
    contract_data = (
        b"package nl2repobench.harness; class ContractMain { void run() { "
        b'new ProcessBuilder("nl2repobench.verification.candidate_process_cli"); } }\n'
    )
    verifier_ref = store.put_bytes(
        encode_ustar(
            tuple(sorted((
                CanonicalEntry("harness/", "directory", 0o555),
                CanonicalEntry("harness/src/", "directory", 0o555),
                CanonicalEntry("harness/src/main/", "directory", 0o555),
                CanonicalEntry("harness/src/main/java/", "directory", 0o555),
                CanonicalEntry(
                    "harness/src/main/java/nl2repobench/", "directory", 0o555
                ),
                CanonicalEntry(
                    "harness/src/main/java/nl2repobench/harness/", "directory", 0o555
                ),
                CanonicalEntry("harness/pom.xml", "file", 0o444, b"<project/>\n"),
                CanonicalEntry(
                    "harness/src/main/java/nl2repobench/harness/CandidateMain.java",
                    "file",
                    0o444,
                    b"package nl2repobench.harness; class CandidateMain {}\n",
                ),
                CanonicalEntry(
                    "harness/src/main/java/nl2repobench/harness/ContractMain.java",
                    "file",
                    0o444,
                    contract_data,
                ),
            ), key=lambda entry: entry.path.encode("utf-8")))
        ),
        media_type="application/vnd.nl2repobench.verifier+tar",
        visibility=Visibility.PRIVATE,
    )
    oracle_ref = store.put_bytes(
        encode_ustar(
            (
                CanonicalEntry("solve.sh", "file", 0o555, b"#!/bin/sh\nexit 0\n"),
            )
        ),
        media_type="application/vnd.nl2repobench.oracle+tar",
        visibility=Visibility.PRIVATE,
    )
    source = tmp_path / "source"
    source.mkdir()
    (source / "instruction.md").write_text("# Java contract\n", encoding="utf-8")
    data = tomllib.loads((ROOT / "catalog/sources/java-semver4j/task.toml").read_text())
    data["task_id"] = "java-coverage-fixture"
    data["instruction"] = "instruction.md"
    data["dependencies"]["lock"] = lock_ref.model_dump(mode="json")
    data["dependencies"]["offline_store"] = store_ref.model_dump(mode="json")
    data["dependencies"]["inventory"] = inventory_ref.model_dump(mode="json")
    data["verifier"]["bundle"] = verifier_ref.model_dump(mode="json")
    data["verifier"]["contract_sha256"] = (
        "sha256:" + hashlib.sha256(contract_data).hexdigest()
    )
    data["oracle_bundle"] = oracle_ref.model_dump(mode="json")
    (source / "task.toml").write_text(tomli_w.dumps(data), encoding="utf-8")
    controls = source / "harbor/controls"
    controls.mkdir(parents=True)
    (controls / "stub.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    resolver = LocalArtifactResolver(store, allow_private=True)
    compiler = JavaHarborCompiler(
        ROOT / "toolchain.java.lock.toml", artifact_resolver=resolver
    )

    task = compiler.compile_task(source, tmp_path / "tasks")
    model = compiler.prepare_run_bundle(task, "model", tmp_path / "model")
    oracle = compiler.prepare_run_bundle(task, "oracle", tmp_path / "oracle")
    control = compiler.prepare_control_bundle(task, "stub", tmp_path / "controls")

    assert not (task / "tests/private").exists()
    assert not (model / "solution/oracle-ref.json").exists()
    assert (oracle / "solution/oracle-bundle/solve.sh").is_file()
    assert (control / "solution/solve.sh").read_text() == "#!/bin/sh\nexit 0\n"
    assert "${NL2REPO_PRIVATE_CAS" not in (
        control / "tests/docker-compose.yaml"
    ).read_text()


def test_java_compiler_rejects_invalid_control_and_run_preparation(tmp_path: Path) -> None:
    compiler = JavaHarborCompiler(ROOT / "toolchain.java.lock.toml")
    task = tmp_path / "task"
    task.mkdir()

    with pytest.raises(JavaHarborCompileError, match="unsupported Java control"):
        compiler.prepare_control_bundle(task, "unknown", tmp_path / "controls")
    with pytest.raises(JavaHarborCompileError, match="control script is missing"):
        compiler.prepare_control_bundle(task, "stub", tmp_path / "controls")
    with pytest.raises(JavaHarborCompileError, match="unsupported Java run role"):
        compiler.prepare_run_bundle(task, "admin", tmp_path / "runs")
    with pytest.raises(JavaHarborCompileError, match="private artifact resolver"):
        compiler.prepare_run_bundle(task, "model", tmp_path / "runs")


def test_java_compiler_rejects_invalid_generated_refs_and_cas_marker(tmp_path: Path) -> None:
    refs = tmp_path / "refs.json"
    with pytest.raises(JavaHarborCompileError, match="refs are missing"):
        JavaHarborCompiler._load_generated_refs(refs, keys={"schema_version"})  # noqa: SLF001
    refs.write_text('{"schema_version":"2.0"}', encoding="utf-8")
    with pytest.raises(JavaHarborCompileError, match="refs are invalid"):
        JavaHarborCompiler._load_generated_refs(  # noqa: SLF001
            refs, keys={"schema_version"}
        )
    with pytest.raises(JavaHarborCompileError, match="artifact_ref is invalid"):
        JavaHarborCompiler._artifact_ref({}, "artifact_ref")  # noqa: SLF001

    task = tmp_path / "task"
    (task / "tests").mkdir(parents=True)
    (task / "tests/docker-compose.yaml").write_text(
        "services:\n  main: {}\n", encoding="utf-8"
    )
    with pytest.raises(JavaHarborCompileError, match="CAS mount is invalid"):
        JavaHarborCompiler._bind_scoped_cas(  # noqa: SLF001
            task, tmp_path / "temporary-cas", tmp_path / "final-cas"
        )
