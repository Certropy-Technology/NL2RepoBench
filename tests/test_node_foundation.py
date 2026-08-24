from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.cli import app
from nl2repobench.domain.models import Visibility
from nl2repobench.domain.models_v2 import (
    DependencyBundleV2,
    EnvironmentLockV2,
    RuntimeProfileV2,
)
from nl2repobench.domain.models_v2 import (
    TestManifestV2 as NodeTestsManifest,
)
from nl2repobench.harbor.models_v2 import load_node_toolchain_lock
from nl2repobench.harbor.node_compiler import NodeHarborCompileError, NodeHarborCompiler
from nl2repobench.harbor.node_dependencies import (
    NodeDependencyError,
    validate_npm_dependency_bundle,
    validate_npm_package_tarball,
)
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.verification import cli as verifier_cli
from nl2repobench.verification import node_candidate_install
from nl2repobench.verification.node_candidate_client import run_candidate
from nl2repobench.verification.node_command_plan import (
    EXPECTED_NODE_PLAN,
    validate_node_command_plan,
)
from nl2repobench.verification.node_grader import grade_node_test_report
from nl2repobench.verification.node_models import NodeVerificationReason

ROOT = Path(__file__).parents[1]
NODE_TASK = ROOT / "catalog/sources/node-synthetic"
NODE_TOOLCHAIN = ROOT / "toolchain.node.dev.lock.toml"
NODE_PRODUCTION_TOOLCHAIN = ROOT / "toolchain.node.lock.toml"


def _report(
    cases: list[tuple[str, str]],
    *,
    exit_code: int = 0,
    collection_errors: list[dict[str, str]] | None = None,
    collected: int | None = None,
) -> dict[str, object]:
    return {
        "schema_version": "2.0",
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


def test_v2_runtime_and_npm_versions_are_exact() -> None:
    profile = RuntimeProfileV2(
        language="node",
        runtime="node",
        version="22.23.1",
        package_manager="npm",
        package_manager_version="10.9.8",
        libc="glibc",
    )
    assert profile.schema_version == "2.0"
    assert load_node_toolchain_lock(NODE_TOOLCHAIN).runtime.runtime_version == "22.23.1"
    production = load_node_toolchain_lock(NODE_PRODUCTION_TOOLCHAIN)
    assert production.status == "locked"
    assert production.node_grader == "locked"
    assert production.node_runtime_sha256 is not None
    assert production.runtime.runtime_version == "24.19.0"
    assert production.runtime.npm_version == "11.17.0"
    with pytest.raises(ValueError, match="supported 22.x.y or 24.x.y"):
        RuntimeProfileV2(
            language="node",
            runtime="node",
            version="22",
            package_manager="npm",
            package_manager_version="10.9.8",
            libc="glibc",
        )
    with pytest.raises(ValueError, match="lockfile version 3"):
        DependencyBundleV2(
            ecosystem="npm",
            consumer="candidate-runtime",
            lockfile_name="package-lock.json",
            lockfile_version="2",
            package_manager="npm",
            package_manager_version="10.9.8",
        )


def test_v2_environment_rejects_runtime_language_mismatch() -> None:
    with pytest.raises(ValueError, match="Node language requires"):
        EnvironmentLockV2(
            status="known",
            os_name="linux",
            base_image="node:22",
            base_image_digest="sha256:" + "a" * 64,
            runtime={
                "language": "node",
                "runtime": "cpython",
                "version": "22.23.1",
                "package_manager": "npm",
                "package_manager_version": "10.9.8",
                "libc": "glibc",
            },
            network_mode="no-network",
        )


def test_v2_blocked_task_can_record_unfrozen_collection() -> None:
    tests = NodeTestsManifest(expected_total=0, expected_total_source="unknown")

    assert tests.expected_total == 0
    assert tests.expected_total_source == "unknown"


def test_v2_catalog_dispatch_and_determinism(tmp_path: Path) -> None:
    first = CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_task(
        NODE_TASK, tmp_path / "first"
    )
    second = CatalogCompiler(FileArtifactStore(tmp_path / "artifacts")).compile_task(
        NODE_TASK, tmp_path / "second"
    )
    assert first.manifest.schema_version == "2.0"
    assert first.reference.manifest_digest == second.reference.manifest_digest
    assert first.path.read_bytes() == second.path.read_bytes()
    assert json.loads(first.path.read_text())["metadata"]["language"] == "node"


def test_v2_development_compiler_is_deterministic_and_hides_private_fixture_from_agent(
    tmp_path: Path,
) -> None:
    compiler = NodeHarborCompiler(NODE_TOOLCHAIN)
    first = compiler.compile_task(NODE_TASK, tmp_path / "first", allow_incomplete=True)
    second = compiler.compile_task(NODE_TASK, tmp_path / "second", allow_incomplete=True)
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
    generated_test_script = (first / "tests/test.sh").read_text()
    assert "install_candidate.mjs" in generated_test_script
    assert "NODE_CANDIDATE_SITE=/tmp/candidate-site" in generated_test_script
    assert "NODE_TEST_CLIENT=/tests/private/test_client.mjs" in generated_test_script
    assert "candidate-installation-failed" in generated_test_script
    assert 'schema_version = "1.4"' in (first / "task.toml").read_text()
    assert 'language = "node"' in (first / "task.toml").read_text()
    assert not (first / "environment/docker-compose.yaml").exists()
    assert "network_mode: none" in (first / "tests/docker-compose.yaml").read_text()


def test_v2_production_compilation_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(NodeHarborCompileError, match="development-only|unsupported"):
        NodeHarborCompiler(NODE_TOOLCHAIN).compile_task(NODE_TASK, tmp_path / "output")


def test_locked_node_toolchain_rejects_runtime_helper_drift(tmp_path: Path) -> None:
    toolchain = tmp_path / "toolchain.node.lock.toml"
    (tmp_path / "harbor-runner").mkdir()
    shutil.copy2(ROOT / "harbor-runner/uv.lock", tmp_path / "harbor-runner/uv.lock")
    text = NODE_PRODUCTION_TOOLCHAIN.read_text(encoding="utf-8").replace(
        "f3d988ea38f439082388183bb825eb5001c903b0cbeee3bc48f005a8a7d7e756",
        "0" * 64,
    )
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
    assert result.counts.model_dump(mode="json") | {} == {
        "schema_version": "2.0",
        "collected": 5,
        "passed": 1,
        "failed": 1,
        "errors": 1,
        "skipped": 1,
        "todo": 1,
    }


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        (None, NodeVerificationReason.REPORT_MISSING),
        (b"not-json", NodeVerificationReason.REPORT_MALFORMED),
        (_report([("a", "passed"), ("a", "passed")]), NodeVerificationReason.DUPLICATE_TEST_ID),
        (_report([("a", "passed")], collected=2), NodeVerificationReason.REPORT_COUNT_MISMATCH),
        (
            _report([("a", "passed")], collection_errors=[{"message": "syntax error"}]),
            NodeVerificationReason.COLLECTION_ERROR,
        ),
    ],
)
def test_node_report_rejects_invalid_collection_and_shape(
    payload: object, reason: NodeVerificationReason
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
    assert mismatch.failure_reason is NodeVerificationReason.REPORT_EXIT_MISMATCH
    model_failure = grade_node_test_report(
        expected_total=1,
        report_data=None,
        explicit_reason=NodeVerificationReason.CANDIDATE_INSTALLATION_FAILED,
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
    (tmp_path / "package.json").write_text(
        '{"name":"candidate","version":"1.0.0"}\n', encoding="utf-8"
    )
    package = tmp_path / "node_modules/demo"
    package.mkdir(parents=True)
    (package / "package.json").write_text(
        '{"name":"demo","version":"1.0.0","main":"index.cjs"}\n', encoding="utf-8"
    )
    (package / "index.cjs").write_text("exports.add=(a,b)=>a+b;\n", encoding="utf-8")
    result = run_candidate(
        tmp_path,
        b'{"package":"demo","export":"add","args":[2,5]}',
        node_executable=node,
    )
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


def test_v1_verifier_cli_imports_without_v2_runtime_files(tmp_path: Path) -> None:
    package = tmp_path / "nl2repobench"
    shutil.copytree(ROOT / "src/nl2repobench", package)
    for relative in (
        "domain/models_v2.py",
        "harbor/models_v2.py",
        "harbor/node_compiler.py",
        "harbor/node_dependencies.py",
        "verification/models_v2.py",
        "verification/node_command_plan.py",
        "verification/node_grader.py",
        "verification/node_candidate_client.py",
        "verification/node_candidate_install.py",
    ):
        (package / relative).unlink(missing_ok=True)
    shutil.rmtree(package / "verification/node", ignore_errors=True)
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


def test_v2_schema_export_is_additive(tmp_path: Path) -> None:
    output = tmp_path / "v2"
    result = CliRunner().invoke(
        app, ["schema", "export", "--version", "2.0", "--output", str(output)]
    )
    assert result.exit_code == 0, result.stdout
    assert (output / "test-report.schema.json").is_file()
    assert json.loads((output / "test-report.schema.json").read_text())["$defs"]["NodeTestCaseV2"]


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
    compiler = NodeHarborCompiler(
        NODE_TOOLCHAIN,
        artifact_resolver=LocalArtifactResolver(store, allow_private=True),
    )
    destination = tmp_path / "extracted"
    compiler._extract_private_bundle(reference, destination)  # noqa: SLF001
    assert (destination / "nested/test.mjs").read_text() == "test\n"
    with pytest.raises(NodeHarborCompileError, match="private artifact resolver"):
        NodeHarborCompiler(NODE_TOOLCHAIN)._extract_private_bundle(  # noqa: SLF001
            reference, tmp_path / "missing"
        )


def test_node_compiler_rejects_python_source_and_existing_output(tmp_path: Path) -> None:
    with pytest.raises(NodeHarborCompileError, match="schema_version=2.0"):
        NodeHarborCompiler(NODE_TOOLCHAIN).compile_task(
            ROOT / "catalog/sources/ministats", tmp_path / "out", allow_incomplete=True
        )
    compiler = NodeHarborCompiler(NODE_TOOLCHAIN)
    existing = tmp_path / "out/node-synthetic"
    existing.mkdir(parents=True)
    with pytest.raises(NodeHarborCompileError, match="already exists"):
        compiler.compile_task(NODE_TASK, tmp_path / "out", allow_incomplete=True)


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
    assert "timeout" in (
        ROOT / "catalog/sources/node-synthetic/harbor/tests/test_client.mjs"
    ).read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="regular directory"):
        node_candidate_install._check_directory(Path("/missing"), "source")  # noqa: SLF001


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
        if command[1] == "pack":
            destination = Path(command[command.index("--pack-destination") + 1])
            (destination / "node-synthetic.tgz").write_bytes(b"tar")
        return {"outcome": "success", "returncode": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr(node_candidate_install, "_run", fake_run)
    monkeypatch.setattr(node_candidate_install, "validate_npm_package_tarball", lambda path: None)
    monkeypatch.setattr(node_candidate_install, "terminate_uid_processes", lambda uid: None)
    result = node_candidate_install.install_candidate(source, target, cache=cache)
    assert result["outcome"] == "success"
    assert [command[1] for command in calls] == ["ci", "pack", "install"]

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
    process = SimpleNamespace(pid=123, returncode=0)

    def communicate(*, timeout: float | None = None) -> tuple[bytes, bytes]:
        if timeout is not None:
            raise subprocess.TimeoutExpired([], timeout)
        return b"", b""

    process.communicate = communicate
    monkeypatch.setattr(node_candidate_install.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(node_candidate_install.os, "killpg", lambda *args: None)
    timed = node_candidate_install._run(["node"], cwd=tmp_path, env={}, timeout_sec=0.1)  # noqa: SLF001
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


def test_node_verifier_cli_writes_v2_outputs(
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
    assert json.loads((output / "grading.json").read_text())["schema_version"] == "2.0"


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
                "schema_version": "2.0",
                "framework": "node:test",
                "report_format": "node-test-json-v1",
                "collected": 2,
                "tests": [
                    {"schema_version": "2.0", "test_id": "a", "status": "passed", "duration_ms": 0},
                    {"schema_version": "2.0", "test_id": "b", "status": "failed", "duration_ms": 0},
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
