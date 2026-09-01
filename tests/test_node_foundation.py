from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nl2repobench.authoring.catalog import CatalogCompiler, scaffold_task
from nl2repobench.cli import app
from nl2repobench.domain.canonical_contract import (
    DependencyBundle,
    EnvironmentLock,
    RuntimeProfile,
)
from nl2repobench.domain.canonical_contract import (
    TestManifest as NodeTestsManifest,
)
from nl2repobench.domain.canonical_models import Visibility
from nl2repobench.harbor.node_compiler import NodeHarborCompileError, NodeHarborCompiler
from nl2repobench.harbor.node_dependencies import (
    NodeDependencyError,
    validate_npm_dependency_bundle,
    validate_npm_package_tarball,
)
from nl2repobench.harbor.node_toolchain import load_node_toolchain_lock
from nl2repobench.harbor.registry import HarborCompilerRegistry
from nl2repobench.storage.artifacts import (
    FileArtifactStore,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.materialize import ArchiveKind
from nl2repobench.verification import cli as verifier_cli
from nl2repobench.verification import node_candidate_client, node_candidate_install
from nl2repobench.verification.evaluator import EvaluationResult
from nl2repobench.verification.node_candidate_client import run_candidate
from nl2repobench.verification.node_command_plan import (
    EXPECTED_NODE_PLAN,
    validate_node_command_plan,
)
from nl2repobench.verification.node_grader import grade_node_test_report
from nl2repobench.verification.taxonomy import VerificationReason

ROOT = Path(__file__).parents[1]
NODE_TASK = ROOT / "catalog/sources/node-synthetic"
NODE_TOOLCHAIN = ROOT / "toolchain.node.dev.lock.toml"
NODE_PRODUCTION_TOOLCHAIN = ROOT / "toolchain.node.lock.toml"


def _node_source(tmp_path: Path) -> Path:
    source = tmp_path / "canonical-node-source"
    if source.exists():
        return source
    shutil.copytree(NODE_TASK, source)
    (source / "task.toml").write_text(
        '''schema_version = "1.0"
task_id = "node-synthetic"
version = "2.0.0"
instruction = "instruction.md"

[metadata]
difficulty = "easy"
category = "node-foundation"
tags = ["node", "npm", "node-test"]
language = "node"

[source]
status = "unknown"

[environment]
status = "unknown"
os_name = "debian-bookworm"
base_image = "node:22.23.1-bookworm-slim"

[environment.runtime]
language = "node"
runtime = "node"
version = "22.23.1"
package_manager = "npm"
package_manager_version = "10.9.8"

[environment.network_policy]
mode = "no-network"
offline_dependencies = "missing"
reference_source_fetch = "forbidden"
reason = "Development fixture closure is intentionally absent."

[dependencies]
status = "unknown"
package_manager = "npm"
packages = []

[tests]
framework = "node:test"
report_format = "node-test-json-v1"
expected_total = 8
expected_total_source = "frozen-collection"

[metric]
contract_id = "fixed-test-pass-rate-v1"
collection_mismatch = "fail"

[lifecycle]
status = "discovered"

[harbor]
description = "Development-only zero-dependency node:test foundation fixture."
keywords = ["node", "npm", "node-test"]
agent_timeout_sec = 600.0
verifier_timeout_sec = 600.0
candidate_install_timeout_sec = 90.0
candidate_total_timeout_sec = 300.0
agent_network_mode = "no-network"
verifier_network_mode = "no-network"
cpus = 1
memory_mb = 1024
storage_mb = 4096
workspace_artifact = "/workspace"
''',
        encoding="utf-8",
    )
    return source


def _report(
    cases: list[tuple[str, str]],
    *,
    exit_code: int = 0,
    collection_errors: list[dict[str, str]] | None = None,
    collected: int | None = None,
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "framework": "node:test",
        "report_format": "node-test-json-v1",
        "collected": len(cases) if collected is None else collected,
        "tests": [{"test_id": test_id, "status": status} for test_id, status in cases],
        "collection_errors": collection_errors or [],
        "runner_exit_code": exit_code,
    }


def _tar_bytes(members: list[tuple[str, bytes]]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        for name, data in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return output.getvalue()


def test_canonical_runtime_and_npm_versions_are_exact() -> None:
    profile = RuntimeProfile(
        language="node",
        runtime="node",
        version="22.23.1",
        package_manager="npm",
        package_manager_version="10.9.8",
    )
    assert profile.schema_version == "1.0"
    assert load_node_toolchain_lock(NODE_TOOLCHAIN).runtime.runtime_version == "22.23.1"
    production = load_node_toolchain_lock(NODE_PRODUCTION_TOOLCHAIN)
    assert production.status == "locked"
    assert production.node_grader == "locked"
    assert production.node_runtime_sha256 is not None
    assert production.runtime.runtime_version == "24.19.0"
    assert production.runtime.npm_version == "11.17.0"
    with pytest.raises(ValueError, match="supported 22.x.y or 24.x.y"):
        RuntimeProfile(
            language="node",
            runtime="node",
            version="22",
            package_manager="npm",
            package_manager_version="10.9.8",
        )
    with pytest.raises(ValueError, match="requires lock, offline_store, and inventory"):
        DependencyBundle(
            status="known",
            package_manager="npm",
        )


def test_canonical_environment_rejects_runtime_language_mismatch() -> None:
    with pytest.raises(ValueError, match="runtime does not match language"):
        EnvironmentLock(
            runtime={
                "language": "node",
                "runtime": "cpython",
                "version": "22.23.1",
                "package_manager": "npm",
                "package_manager_version": "10.9.8",
            },
        )


def test_canonical_blocked_task_can_record_unfrozen_collection() -> None:
    tests = NodeTestsManifest(
        framework="node:test",
        report_format="node-test-json-v1",
        expected_total=0,
        expected_total_source="unknown",
    )

    assert tests.expected_total == 0
    assert tests.expected_total_source == "unknown"


def test_node_agent_checks_declared_system_packages_without_runtime_install(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    shutil.copytree(_node_source(tmp_path), source)
    task_toml = source / "task.toml"
    task_toml.write_text(
        task_toml.read_text(encoding="utf-8").replace(
            '[environment]\nstatus = "unknown"',
            '[environment]\nstatus = "unknown"\n'
            'system_packages = ["git=1:2.39.5-0+deb12u3"]',
        ),
        encoding="utf-8",
    )

    task_root = NodeHarborCompiler(NODE_TOOLCHAIN).compile_task(
        source, tmp_path / "output", allow_incomplete=True
    )
    dockerfile = (task_root / "environment/Dockerfile").read_text(encoding="utf-8")

    assert "dpkg-query -W -f='${Version}' git" in dockerfile
    assert "1:2.39.5-0+deb12u3" in dockerfile
    assert "apt-get" not in dockerfile
    assert "COPY npm-bundle /opt/npm-bundle" in dockerfile


def test_canonical_catalog_dispatch_and_determinism(tmp_path: Path) -> None:
    source = _node_source(tmp_path)
    first = CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_task(
        source, tmp_path / "first"
    )
    second = CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_task(
        source, tmp_path / "second"
    )
    assert first.manifest.schema_version == "1.0"
    assert first.reference.manifest_digest == second.reference.manifest_digest
    assert first.path.read_bytes() == second.path.read_bytes()
    assert json.loads(first.path.read_text())["metadata"]["language"] == "node"


def test_canonical_development_compiler_is_deterministic_and_hides_private_fixture_from_agent(
    tmp_path: Path,
) -> None:
    compiler = NodeHarborCompiler(NODE_TOOLCHAIN)
    source = _node_source(tmp_path)
    first = compiler.compile_task(source, tmp_path / "first", allow_incomplete=True)
    second = compiler.compile_task(source, tmp_path / "second", allow_incomplete=True)
    first_files = {
        path.relative_to(first).as_posix(): path.read_bytes()
        for path in first.rglob("*")
        if path.is_file()
    }
    second_files = {
        path.relative_to(second).as_posix(): path.read_bytes()
        for path in second.rglob("*")
        if path.is_file()
    }
    assert first_files == second_files
    assert not list((first / "environment").rglob("contract.test.mjs"))
    agent_dockerfile = (first / "environment/Dockerfile").read_text()
    assert (
        "nl2repobench/openhands-sdk-fork:930e9b1da-bookworm"
        in agent_dockerfile
    )
    assert (
        'agent-runtime-image-id="sha256:'
        "c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f"
        '"' in agent_dockerfile
    )
    assert " AS node-runtime" in agent_dockerfile
    assert f"COPY --from=node-runtime /opt/nl2repobench-node /opt/nl2repobench-node" in agent_dockerfile
    assert "cp --dereference" in agent_dockerfile
    assert "runtime.manifest.json" in agent_dockerfile
    assert "/usr/local/bin/npm" not in agent_dockerfile
    assert "COPY npm-bundle /opt/npm-bundle" in agent_dockerfile
    assert "npm_config_offline=true" in agent_dockerfile
    assert not list((first / "environment").rglob("solution"))
    generated_test_script = (first / "tests/test.sh").read_text()
    assert "install_candidate.mjs" in generated_test_script
    assert "NODE_CANDIDATE_SITE=/tmp/candidate-site" in generated_test_script
    assert "NODE_TEST_CLIENT=/tests/private/test_client.mjs" in generated_test_script
    assert "candidate-installation-failed" in generated_test_script
    assert "nl2repobench.verification.network_check" in generated_test_script
    assert "network.json" in generated_test_script
    assert '[[ "$network_exit" -eq 1 ]]' in generated_test_script
    assert '[[ "$network_exit" -ne 0 ]]' in generated_test_script
    assert "--reason verifier-internal-error" in generated_test_script
    assert "candidate-call-failed" in generated_test_script
    assert 'schema_version = "1.4"' in (first / "task.toml").read_text()
    assert 'language = "node"' in (first / "task.toml").read_text()
    assert not (first / "environment/docker-compose.yaml").exists()
    assert "network_mode: none" in (first / "tests/docker-compose.yaml").read_text()
    bundle_manifest = json.loads((first / "bundle.manifest.json").read_text())
    assert bundle_manifest["schema_version"] == "2.0"
    declared_paths = {entry["path"] for entry in bundle_manifest["files"]}
    assert "bundle.manifest.json" not in declared_paths
    assert "tests/dependencies/bundle.manifest.json" in declared_paths


def test_node_compiler_supports_scoped_task_output(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shutil.copytree(_node_source(tmp_path), source)
    task_toml = source / "task.toml"
    task_toml.write_text(
        task_toml.read_text(encoding="utf-8").replace(
            'task_id = "node-synthetic"',
            'task_id = "@example/node-synthetic"',
        ),
        encoding="utf-8",
    )

    task_root = NodeHarborCompiler(NODE_TOOLCHAIN).compile_task(
        source, tmp_path / "output", allow_incomplete=True
    )

    assert task_root == tmp_path / "output/@example/node-synthetic"
    assert (task_root / "bundle.manifest.json").is_file()


def test_node_compiler_uses_valid_harbor_name_for_scoped_task() -> None:
    assert NodeHarborCompiler._harbor_task_name("@example/node-synthetic") == (
        "nl2repobench/example-node-synthetic"
    )


def test_node_control_dispatch_and_manifest_integrity(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shutil.copytree(_node_source(tmp_path), source)
    controls = source / "harbor/controls"
    controls.mkdir()
    (controls / "stub.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (controls / "forgery.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    task_root = NodeHarborCompiler(NODE_TOOLCHAIN).compile_task(
        source, tmp_path / "tasks", allow_incomplete=True
    )
    control = HarborCompilerRegistry.default().prepare_control_bundle(
        task_root, "stub", tmp_path / "controls", NODE_TOOLCHAIN
    )

    assert (task_root / "solution/solve.sh").read_bytes() != (
        control / "solution/solve.sh"
    ).read_bytes()
    manifest = json.loads((control / "bundle.manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "2.0"
    assert manifest["mode"] == "control-stub"
    assert "controls/stub.sh" in {entry["path"] for entry in manifest["files"]}
    for entry in manifest["files"]:
        file_path = control / entry["path"]
        assert file_path.is_file()
        assert entry["size_bytes"] == file_path.stat().st_size
        assert entry["sha256"] == hashlib.sha256(file_path.read_bytes()).hexdigest()


def test_node_control_rejects_python_only_kind(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shutil.copytree(_node_source(tmp_path), source)
    controls = source / "harbor/controls"
    controls.mkdir()
    (controls / "workspace-invalid.sh").write_text(
        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
    )
    task_root = NodeHarborCompiler(NODE_TOOLCHAIN).compile_task(
        source, tmp_path / "tasks", allow_incomplete=True
    )

    with pytest.raises(NodeHarborCompileError, match="unsupported control kind"):
        HarborCompilerRegistry.default().prepare_control_bundle(
            task_root, "workspace-invalid", tmp_path / "controls", NODE_TOOLCHAIN
        )


def test_node_network_runtime_writes_bounded_receipt(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    receipt = tmp_path / "logs/verifier/network.json"
    completed = subprocess.run(
        [
            node,
            str(ROOT / "src/nl2repobench/verification/node/network-check.mjs"),
            "--output",
            str(receipt),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert completed.returncode in {0, 1}, completed.stderr
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["public_network_available"] == any(payload["probes"].values())
    assert set(payload["probes"]) == {"registry.npmjs.org:443", "1.1.1.1:443"}
    assert all(isinstance(value, bool) for value in payload["probes"].values())
    assert isinstance(payload["network_namespace"], str)
    assert isinstance(payload["route_table"], str)
    assert len(payload["route_table"].encode()) <= 64 * 1024


def test_canonical_production_compilation_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(NodeHarborCompileError, match="development-only|unsupported"):
        NodeHarborCompiler(NODE_TOOLCHAIN).compile_task(_node_source(tmp_path), tmp_path / "output")


def test_locked_node_toolchain_rejects_runtime_helper_drift(tmp_path: Path) -> None:
    toolchain = tmp_path / "toolchain.node.lock.toml"
    (tmp_path / "harbor-runner").mkdir()
    shutil.copy2(ROOT / "harbor-runner/uv.lock", tmp_path / "harbor-runner/uv.lock")
    text = NODE_PRODUCTION_TOOLCHAIN.read_text(encoding="utf-8")
    current_digest = next(
        line.split('"', 2)[1]
        for line in text.splitlines()
        if line.startswith("node_runtime_sha256")
    )
    text = text.replace(current_digest, "sha256:" + "0" * 64)
    toolchain.write_text(text, encoding="utf-8")
    with pytest.raises(NodeHarborCompileError, match="runtime helper digest"):
        NodeHarborCompiler(toolchain)


def test_node_report_grades_leaf_statuses_and_todo_denominator() -> None:
    result = grade_node_test_report(
        expected_total=5,
        report_data=_report(
            [
                ("pass", "passed"),
                ("fail", "failed"),
                ("error", "error"),
                ("skip", "skipped"),
                ("todo", "todo"),
            ],
            exit_code=1,
        ),
    )
    assert result.valid is True
    assert result.reward == 0.2
    assert result.metric_contract == "fixed-test-pass-rate-v1"
    assert isinstance(result, EvaluationResult)
    assert result.counts.model_dump(mode="json") | {} == {
        "schema_version": "1.0",
        "collected": 5,
        "passed": 1,
        "failed": 1,
        "errors": 1,
        "skipped": 1,
        "todo": 1,
        "xfail": 0,
    }


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        (None, VerificationReason.REPORT_MISSING),
        (b"not-json", VerificationReason.REPORT_MALFORMED),
        (_report([("a", "passed"), ("a", "passed")]), VerificationReason.DUPLICATE_LEAF_ID),
        (_report([("a", "passed")], collected=2), VerificationReason.REPORT_COUNT_MISMATCH),
        (
            _report([("a", "passed")], collection_errors=[{"message": "syntax error"}]),
            VerificationReason.COLLECTION_ERROR,
        ),
    ],
)
def test_node_report_rejects_invalid_collection_and_shape(
    payload: object, reason: VerificationReason
) -> None:
    result = grade_node_test_report(expected_total=1, report_data=payload)  # type: ignore[arg-type]
    assert result.valid is False
    assert result.failure_reason is reason


def test_node_report_exit_semantics_and_model_install_failure() -> None:
    mismatch = grade_node_test_report(
        expected_total=1,
        report_data=_report([("a", "passed")], exit_code=1),
        runner_exit_code=1,
    )
    assert mismatch.failure_reason is VerificationReason.REPORT_EXIT_MISMATCH
    model_failure = grade_node_test_report(
        expected_total=1,
        report_data=None,
        explicit_reason=VerificationReason.CANDIDATE_INSTALLATION_FAILED,
    )
    assert model_failure.valid is True
    assert model_failure.failure_class.value == "model"


def test_node_command_plan_is_exact_and_fail_closed(tmp_path: Path) -> None:
    plan = tmp_path / "command-plan.json"
    plan.write_text(json.dumps(EXPECTED_NODE_PLAN), encoding="utf-8")
    validate_node_command_plan(plan)
    plan.write_text(json.dumps({**EXPECTED_NODE_PLAN, "runner": "shell"}), encoding="utf-8")
    with pytest.raises(ValueError, match="allowlisted"):
        validate_node_command_plan(plan)


def test_npm_bundle_rejects_missing_integrity(tmp_path: Path) -> None:
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "npm-cache").mkdir()
    (root / "bundle.manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "ecosystem": "npm",
                "lockfile_version": "3",
                "package_manager": "npm",
                "package_manager_version": "10.9.8",
                "install_mode": "offline",
                "lifecycle_scripts": "ignore-scripts",
                "cache_entries": [],
                "files": [],
            }
        ),
        encoding="utf-8",
    )
    (root / "package-lock.json").write_text(
        json.dumps(
            {
                "lockfileVersion": 3,
                "packages": {
                    "": {},
                    "node_modules/demo": {"resolved": "https://registry.invalid/demo.tgz"},
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(NodeDependencyError, match="integrity"):
        validate_npm_dependency_bundle(root, expected_npm_version="10.9.8")


def test_npm_package_tar_rejects_traversal_and_links(tmp_path: Path) -> None:
    traversal = tmp_path / "traversal.tgz"
    traversal.write_bytes(_tar_bytes([("../escape", b"bad")]))
    with pytest.raises(NodeDependencyError, match="escapes"):
        validate_npm_package_tarball(traversal)

    linked = tmp_path / "linked.tgz"
    with tarfile.open(linked, mode="w") as archive:
        info = tarfile.TarInfo("package/link")
        info.type = tarfile.SYMTYPE
        info.linkname = "/etc/passwd"
        archive.addfile(info)
    with pytest.raises(NodeDependencyError, match="link/device"):
        validate_npm_package_tarball(linked)


def test_npm_package_tar_allows_non_lifecycle_scripts(tmp_path: Path) -> None:
    archive = tmp_path / "scripts.tgz"
    package_json = json.dumps(
        {"name": "demo", "version": "1.0.0", "scripts": {"test": "node test.js"}}
    ).encode()
    archive.write_bytes(_tar_bytes([("package/package.json", package_json)]))

    validate_npm_package_tarball(archive)


def test_npm_package_tar_rejects_install_lifecycle_script(tmp_path: Path) -> None:
    archive = tmp_path / "lifecycle.tgz"
    package_json = json.dumps(
        {"name": "demo", "version": "1.0.0", "scripts": {"postinstall": "node build.js"}}
    ).encode()
    archive.write_bytes(_tar_bytes([("package/package.json", package_json)]))

    with pytest.raises(NodeDependencyError, match="lifecycle"):
        validate_npm_package_tarball(archive)


def test_node_runtime_report_script_collects_eight_leaf_tests(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    test_file = tmp_path / "simple.test.mjs"
    test_file.write_text(
        "import test from 'node:test';\n"
        + "\n".join(f"test('case-{index}', () => {{}});" for index in range(8))
        + "\n",
        encoding="utf-8",
    )
    report = tmp_path / "report.json"
    completed = subprocess.run(
        [
            node,
            str(ROOT / "src/nl2repobench/verification/node/run_tests.mjs"),
            "--tests",
            str(tmp_path),
            "--candidate",
            str(tmp_path),
            "--expected",
            "8",
            "--output",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(report.read_text())
    assert payload["collected"] == 8
    assert len(payload["tests"]) == 8
    assert payload["runner_exit_code"] == 0


def test_node_candidate_boundary_uses_json_subprocess(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    runtime = tmp_path / "node-runtime"
    executable = runtime / "bin/node"
    runner = runtime / "lib/candidate_runner.mjs"
    executable.parent.mkdir(parents=True)
    runner.parent.mkdir(parents=True)
    shutil.copy2(Path(node).resolve(), executable)
    shutil.copy2(ROOT / "src/nl2repobench/verification/node/candidate_runner.mjs", runner)
    executable.chmod(0o555)
    runner.chmod(0o444)
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(node_candidate_client, "NODE_RUNTIME_ROOT", runtime)
    monkeypatch.setattr(node_candidate_client, "NODE_EXECUTABLE", str(executable))
    monkeypatch.setattr(node_candidate_client, "NODE_RUNNER", str(runner))
    try:
        os.chmod(tmp_path.parent.parent, 0o755)
        os.chmod(tmp_path.parent, 0o755)
        os.chmod(tmp_path, 0o755)
        candidate_site = tmp_path / "workspace"
        candidate_site.mkdir()
        (candidate_site / "package.json").write_text(
            '{"name":"candidate","version":"1.0.0"}\n', encoding="utf-8"
        )
        package = candidate_site / "node_modules/demo"
        package.mkdir(parents=True)
        (package / "package.json").write_text(
            '{"name":"demo","version":"1.0.0","main":"index.cjs"}\n', encoding="utf-8"
        )
        (package / "index.cjs").write_text("exports.add=(a,b)=>a+b;\n", encoding="utf-8")
        result = run_candidate(
            candidate_site,
            b'{"package":"demo","export":"add","args":[2,5]}',
            node_executable=str(executable),
        )
    finally:
        monkeypatch.undo()
    assert result.ok is True
    assert result.value == 7


def test_node_workspace_copy_rejects_symlink_and_copies_regular_tree(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    (source / "package.json").write_text("{}\n", encoding="utf-8")
    copied = subprocess.run(
        [
            node,
            str(ROOT / "src/nl2repobench/verification/node/copy_workspace.mjs"),
            "--source",
            str(source),
            "--destination",
            str(destination),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert copied.returncode == 0
    assert (destination / "package.json").is_file()
    outside = tmp_path / "outside"
    outside.write_text("outside", encoding="utf-8")
    (source / "escape").symlink_to(outside)
    rejected = subprocess.run(
        [
            node,
            str(ROOT / "src/nl2repobench/verification/node/copy_workspace.mjs"),
            "--source",
            str(source),
            "--destination",
            str(tmp_path / "rejected"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode == 20


def test_v1_schema_export_is_byte_compatible(tmp_path: Path) -> None:
    output = tmp_path / "v1"
    result = CliRunner().invoke(
        app, ["schema", "export", "--version", "1.0", "--output", str(output)]
    )
    assert result.exit_code == 0, result.stdout
    tracked = ROOT / "schemas/v1"
    for path in output.glob("*.json"):
        assert path.read_bytes() == (tracked / path.name).read_bytes()


def test_verifier_cli_imports_without_retired_runtime_models(tmp_path: Path) -> None:
    package = tmp_path / "nl2repobench"
    shutil.copytree(ROOT / "src/nl2repobench", package)
    assert not (package / "domain/models_v2.py").exists()
    assert not (package / "harbor/models_v2.py").exists()
    probe = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            f"import sys; sys.path.insert(0, r'{tmp_path}'); "
            "import nl2repobench.verification.cli",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert probe.returncode == 0, probe.stderr


def test_schema_export_rejects_retired_node_schema_family(tmp_path: Path) -> None:
    output = tmp_path / "retired"
    result = CliRunner().invoke(
        app, ["schema", "export", "--version", "2.0", "--output", str(output)]
    )
    assert result.exit_code == 2
    assert not output.exists()


def test_npm_dependency_bundle_accepts_integrity_and_cache_closure(tmp_path: Path) -> None:
    root = tmp_path / "bundle"
    cache = root / "npm-cache"
    cache.mkdir(parents=True)
    cache_file = cache / "content.bin"
    cache_file.write_bytes(b"cached")
    lock = {
        "lockfileVersion": 3,
        "packages": {
            "": {"name": "root", "version": "1.0.0"},
            "node_modules/demo": {
                "version": "1.0.0",
                "resolved": "https://registry.invalid/demo.tgz",
                "integrity": "sha512-abc",
            },
        },
    }
    (root / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "ecosystem": "npm",
        "lockfile_version": "3",
        "package_manager": "npm",
        "package_manager_version": "10.9.8",
        "install_mode": "offline",
        "lifecycle_scripts": "ignore-scripts",
        "cache_entries": ["content.bin"],
        "files": [
            {
                "path": "package-lock.json",
                "sha256": hashlib.sha256((root / "package-lock.json").read_bytes()).hexdigest(),
            }
        ],
    }
    (root / "bundle.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    validate_npm_dependency_bundle(root, expected_npm_version="10.9.8")


def test_npm_dependency_bundle_accepts_declared_linux_x64_native_package(
    tmp_path: Path,
) -> None:
    root = tmp_path / "bundle"
    (root / "npm-cache").mkdir(parents=True)
    lock = {
        "lockfileVersion": 3,
        "packages": {
            "": {"name": "root", "version": "1.0.0"},
            "node_modules/@img/native-linux-x64": {
                "version": "1.2.3",
                "resolved": "https://registry.invalid/native.tgz",
                "integrity": "sha512-native",
                "os": ["linux"],
                "cpu": ["x64"],
            },
        },
    }
    (root / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "ecosystem": "npm",
        "lockfile_version": "3",
        "package_manager": "npm",
        "package_manager_version": "10.9.8",
        "install_mode": "offline",
        "lifecycle_scripts": "ignore-scripts",
        "cache_entries": [],
        "native_packages": [
            {
                "package": "@img/native-linux-x64",
                "version": "1.2.3",
                "integrity": "sha512-native",
                "os": "linux",
                "cpu": "x64",
                "libc": "glibc",
            }
        ],
    }
    (root / "bundle.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    validate_npm_dependency_bundle(root, expected_npm_version="10.9.8")


def test_npm_dependency_bundle_rejects_undeclared_native_package(tmp_path: Path) -> None:
    root = tmp_path / "bundle"
    (root / "npm-cache").mkdir(parents=True)
    lock = {
        "lockfileVersion": 3,
        "packages": {
            "": {"name": "root", "version": "1.0.0"},
            "node_modules/native": {
                "version": "1.2.3",
                "resolved": "https://registry.invalid/native.tgz",
                "integrity": "sha512-lock",
                "os": ["linux"],
                "cpu": ["x64"],
            },
        },
    }
    (root / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "ecosystem": "npm",
        "lockfile_version": "3",
        "package_manager": "npm",
        "package_manager_version": "10.9.8",
        "install_mode": "offline",
        "lifecycle_scripts": "ignore-scripts",
        "cache_entries": [],
    }
    (root / "bundle.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(NodeDependencyError, match="undeclared native or platform"):
        validate_npm_dependency_bundle(root, expected_npm_version="10.9.8")


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        (".npmrc", "forbidden npm bundle file"),
        ("node_modules/demo", "node_modules is forbidden"),
        ("run.sh", "forbidden npm bundle file"),
    ],
)
def test_npm_dependency_bundle_rejects_forbidden_paths(
    tmp_path: Path, entry: str, message: str
) -> None:
    root = tmp_path / "bundle"
    root.mkdir()
    path = root / entry
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("bad", encoding="utf-8")
    with pytest.raises(NodeDependencyError, match=message):
        validate_npm_dependency_bundle(root)


def test_npm_package_tarball_accepts_clean_package(tmp_path: Path) -> None:
    archive = tmp_path / "package.tgz"
    archive.write_bytes(
        _tar_bytes(
            [
                ("package/package.json", b'{"name":"demo","version":"1.0.0"}'),
                ("package/index.mjs", b"export const value = 1;\n"),
            ]
        )
    )
    validate_npm_package_tarball(archive)


@pytest.mark.parametrize(
    ("members", "message"),
    [
        (
                [
                    (
                        "package/package.json",
                        b'{"name":"demo","version":"1.0.0","scripts":{"postinstall":"bad"}}',
                    )
                ],
            "lifecycle",
        ),
        (
            [
                ("package/package.json", b'{"name":"demo","version":"1.0.0"}'),
                ("package/native.node", b"native"),
            ],
            "native",
        ),
        (
            [("package/package.json", b'{"name":"demo","version":"1.0.0","workspaces":[]}')],
            "workspaces",
        ),
    ],
)
def test_npm_package_tarball_rejects_scripts_native_and_workspaces(
    tmp_path: Path, members: list[tuple[str, bytes]], message: str
) -> None:
    archive = tmp_path / "package.tgz"
    archive.write_bytes(_tar_bytes(members))
    with pytest.raises(NodeDependencyError, match=message):
        validate_npm_package_tarball(archive)


def test_node_compiler_extracts_private_bundle_and_rejects_missing_resolver(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    reference = store.put_bytes(
        _tar_bytes([("nested/test.mjs", b"test\n")]), visibility=Visibility.PRIVATE
    )
    authorization = PrivateArtifactAuthorization(
        task_id="node-synthetic",
        manifest_digest="sha256:" + "a" * 64,
        purpose="compile",
        allowed_digests=frozenset({reference.digest}),
        staging_root=(tmp_path / "compiled/node/private/aaaaaaaaaaaaaaaa").resolve(),
    )
    resolver = LocalArtifactResolver.scoped_private(
        store,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )
    compiler = NodeHarborCompiler(NODE_TOOLCHAIN, artifact_resolver=resolver)
    destination = tmp_path / "extracted"
    with pytest.raises(NodeHarborCompileError, match="media type"):
        compiler._extract_private_bundle(  # noqa: SLF001
            reference, destination, ArchiveKind.TEST_BUNDLE
        )
    with pytest.raises(NodeHarborCompileError, match="private artifact resolver"):
        NodeHarborCompiler(NODE_TOOLCHAIN)._extract_private_bundle(  # noqa: SLF001
            reference, tmp_path / "missing", ArchiveKind.TEST_BUNDLE
        )


def test_node_compiler_rejects_python_source_and_existing_output(tmp_path: Path) -> None:
    python_source = scaffold_task(tmp_path / "python-sources", "python-task")
    with pytest.raises(NodeHarborCompileError, match="canonical Node runtime"):
        NodeHarborCompiler(NODE_TOOLCHAIN).compile_task(
            python_source, tmp_path / "out", allow_incomplete=True
        )
    compiler = NodeHarborCompiler(NODE_TOOLCHAIN)
    existing = tmp_path / "out/node-synthetic"
    existing.mkdir(parents=True)
    with pytest.raises(NodeHarborCompileError, match="already exists"):
        compiler.compile_task(_node_source(tmp_path), tmp_path / "out", allow_incomplete=True)


def test_node_candidate_install_protocol_and_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    environment = node_candidate_install.sanitized_node_environment(
        cache=Path("/cache"), tmpdir=Path("/tmp")
    )
    assert environment["npm_config_offline"] == "true"
    assert environment["npm_config_ignore_scripts"] == "true"
    assert "NODE_OPTIONS" not in environment
    assert "--ignore-scripts" in node_candidate_install.npm_ci_command(Path("/src"), Path("/cache"))
    assert "--ignore-scripts" in node_candidate_install.npm_pack_command(
        Path("/src"), Path("/pack")
    )
    assert "--offline" in node_candidate_install.npm_install_tar_command(
        Path("/pack/pkg.tgz"), Path("/target"), Path("/cache")
    )
    for command in (
        node_candidate_install.npm_ci_command(Path("/src"), Path("/cache")),
        node_candidate_install.npm_pack_command(Path("/src"), Path("/pack")),
        node_candidate_install.npm_install_tar_command(
            Path("/pack/pkg.tgz"), Path("/target"), Path("/cache")
        ),
    ):
        assert command[0] == node_candidate_install.NODE_EXECUTABLE
        assert command[1] == node_candidate_install.NPM_LAUNCHER
        assert command[0] == "/opt/nl2repobench-node/bin/node"
        assert command[1] == "/opt/nl2repobench-node/lib/npm/bin/npm-cli.js"
    assert "/usr/local/bin/npm" not in node_candidate_install.npm_ci_command(
        Path("/src"), Path("/cache")
    )
    pnpm_script = (
        ROOT / "src/nl2repobench/verification/node/install_candidate_pnpm.mjs"
    ).read_text()
    assert 'const NODE_ROOT = "/opt/nl2repobench-node"' in pnpm_script
    assert 'const PNPM = `${NODE_ROOT}/lib/pnpm/bin/pnpm.cjs`' in pnpm_script
    assert "/usr/local/bin/pnpm" not in pnpm_script
    assert "/usr/bin/prlimit" not in pnpm_script
    assert "timeout" in (
        ROOT / "catalog/sources/node-synthetic/harbor/tests/test_client.mjs"
    ).read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="regular directory"):
        node_candidate_install._check_directory(Path("/missing"), "source")  # noqa: SLF001


def test_node_supervisor_request_uses_dedicated_staged_runtime(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    executable = runtime / "bin/node"
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"node")
    executable.chmod(0o555)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    request, request_id = node_candidate_client._make_supervisor_request(  # noqa: SLF001
        [str(executable), "--no-addons", str(runtime / "lib/runner.mjs")],
        cwd=workspace,
        write_root=workspace,
        timeout_sec=5,
        stdin_data=b"payload",
        environment={"HOME": str(workspace / "home")},
        context="call",
    )
    payload = json.loads(request)
    assert payload["request_id"] == request_id
    assert payload["context"] == "call"
    assert payload["command"]["argv"][0] == str(executable)
    assert payload["command"]["argv"][0] != "/usr/bin/node"
    assert payload["policy"]["allowed_executable_roots"] == [
        "/opt/nl2repobench-node/bin"
    ]
    assert "PATH" not in payload["policy"]["allowed_environment_names"]


def test_node_candidate_install_success_and_failure_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    target = tmp_path / "target"
    cache = tmp_path / "cache"
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> dict[str, object]:
        calls.append(command)
        if command[2] == "pack":
            destination = Path(command[command.index("--pack-destination") + 1])
            (destination / "node-synthetic.tgz").write_bytes(b"tar")
        return {"outcome": "success", "returncode": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr(node_candidate_install, "_run", fake_run)
    monkeypatch.setattr(node_candidate_install, "validate_npm_package_tarball", lambda path: None)
    result = node_candidate_install.install_candidate(source, target, cache=cache)
    assert result["outcome"] == "success"
    assert [command[2] for command in calls] == ["ci", "pack", "install"]

    monkeypatch.setattr(
        node_candidate_install,
        "_run",
        lambda command, **kwargs: {"outcome": "failed", "returncode": 1},
    )
    failed = node_candidate_install.install_candidate(source, tmp_path / "failed", cache=cache)
    assert failed["outcome"] == "install-failed"


def test_node_candidate_install_timeout_and_status_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        node_candidate_install,
        "run_node_command",
        lambda *args, **kwargs: node_candidate_client.NodeProcessResult(124),
    )
    timed = node_candidate_install._run(  # noqa: SLF001
        ["node"], cwd=tmp_path, write_root=tmp_path, env={}, timeout_sec=0.1
    )
    assert timed["outcome"] == "timeout"

    status = tmp_path / "status.json"
    source = tmp_path / "source"
    source.mkdir()
    monkeypatch.setattr(
        node_candidate_install,
        "install_candidate",
        lambda *args, **kwargs: {"outcome": "success"},
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "install",
            "--source",
            str(source),
            "--target",
            str(tmp_path / "target"),
            "--status",
            str(status),
        ],
    )
    node_candidate_install.main()
    assert json.loads(status.read_text())["outcome"] == "success"


def test_node_verifier_cli_writes_canonical_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = tmp_path / "report.json"
    output = tmp_path / "output"
    report.write_text(json.dumps(_report([("a", "passed")])), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "grade-node",
            "--expected",
            "1",
            "--runtime",
            "node",
            "--report",
            str(report),
            "--runner-exit-code",
            "0",
            "--output",
            str(output),
        ],
    )
    verifier_cli.main()
    assert json.loads((output / "reward.json").read_text())["reward"] == 1.0
    assert json.loads((output / "grading.json").read_text())["schema_version"] == "1.0"


def test_node_runtime_report_normalizes_skip_todo_and_failure(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    test_file = tmp_path / "statuses.test.mjs"
    test_file.write_text(
        """import test from 'node:test';
import assert from 'node:assert/strict';
test('pass', () => {});
test('skip', {skip: 'later'}, () => {});
test('todo', {todo: 'later'}, () => {});
test('fail', () => assert.equal(1, 2));
""",
        encoding="utf-8",
    )
    report = tmp_path / "report.json"
    completed = subprocess.run(
        [
            node,
            str(ROOT / "src/nl2repobench/verification/node/run_tests.mjs"),
            "--tests",
            str(tmp_path),
            "--candidate",
            str(tmp_path),
            "--expected",
            "4",
            "--output",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    statuses = {
        case["test_id"].split("::")[-1]: case["status"]
        for case in json.loads(report.read_text())["tests"]
    }
    assert statuses == {"pass": "passed", "skip": "skipped", "todo": "todo", "fail": "failed"}


def test_node_runtime_grader_preserves_collected_count(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "framework": "node:test",
                "report_format": "node-test-json-v1",
                "collected": 2,
                "tests": [
                    {"schema_version": "1.0", "test_id": "a", "status": "passed", "duration_ms": 0},
                    {"schema_version": "1.0", "test_id": "b", "status": "failed", "duration_ms": 0},
                ],
                "collection_errors": [],
                "runner_exit_code": 1,
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "output"
    completed = subprocess.run(
        [
            node,
            str(ROOT / "src/nl2repobench/verification/node/grade-report.mjs"),
            "--expected",
            "2",
            "--report",
            str(report),
            "--runner-exit-code",
            "1",
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    grading = json.loads((output / "grading.json").read_text())
    assert grading["counts"]["collected"] == 2
    assert grading["metric_contract"] == "fixed-test-pass-rate-v1"
