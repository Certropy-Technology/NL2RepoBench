from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from nl2repobench.harbor import node_toolchain
from nl2repobench.harbor.go_compiler import GO_RUNTIME_LOCK_FILES, GoHarborCompiler
from nl2repobench.harbor.node_toolchain import load_node_toolchain_lock
from nl2repobench.harbor.task_writer import (
    _PYTHON_VERIFIER_FILES,
    RUNTIME_DIGEST_ALGORITHM,
    TaskWriterError,
    canonical_runtime_digest,
    copy_python_verifier_runtime,
    python_runtime_manifest,
    validate_python_runtime_manifest,
)
from nl2repobench.verification import candidate_client

ROOT = Path(__file__).parents[1]


def _load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".", "_"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_python_runtime_inventory_is_exact_and_closed() -> None:
    expected = {
        "__init__.py",
        "domain/__init__.py",
        "domain/canonical.py",
        "domain/canonical_contract.py",
        "domain/canonical_models.py",
        "domain/command_plan.py",
        "domain/network_policy.py",
        "domain/runtime.py",
        "package_managers/__init__.py",
        "package_managers/base.py",
        "package_managers/go_modules.py",
        "verification/__init__.py",
        "verification/cli.py",
        "verification/candidate_client.py",
        "verification/candidate_install.py",
        "verification/candidate_process_cli.py",
        "verification/candidate_runner.py",
        "verification/command_plan.py",
        "verification/custom_verifier.py",
        "verification/evaluator.py",
        "verification/go_grader.py",
        "verification/go_bridge_proxy.py",
        "verification/go_contract_runner.py",
        "verification/go_command_plan.py",
        "verification/go_supervisor.py",
        "verification/grader.py",
        "verification/integrity.py",
        "verification/junit.py",
        "verification/leaf_report.py",
        "verification/metric_contract.py",
        "verification/network_check.py",
        "verification/node_grader.py",
        "verification/process_cleanup.py",
        "verification/pytest_plugin.py",
        "verification/registry.py",
        "verification/run_pytest.py",
        "verification/subprocess_supervisor.py",
        "verification/taxonomy.py",
        "verification/workspace_copy.py",
        "verification/normalize/__init__.py",
        "verification/normalize/go_json.py",
        "verification/normalize/node_test_json.py",
        "verification/normalize/pytest_junit.py",
    }
    assert len(_PYTHON_VERIFIER_FILES) == 43
    assert set(_PYTHON_VERIFIER_FILES) == expected
    assert len(_PYTHON_VERIFIER_FILES) == len(set(_PYTHON_VERIFIER_FILES))


def test_python_runtime_digest_is_path_sorted_and_independent() -> None:
    root = ROOT / "src" / "nl2repobench"
    paths = tuple(_PYTHON_VERIFIER_FILES)
    expected = hashlib.sha256()
    for relative in sorted(paths, key=lambda value: value.encode("utf-8")):
        data = (root / relative).read_bytes()
        expected.update(relative.encode("utf-8"))
        expected.update(b"\0")
        expected.update(hashlib.sha256(data).digest())
    assert RUNTIME_DIGEST_ALGORITHM == "sha256:path-nul-raw-file-sha256-v1"
    assert canonical_runtime_digest(root, tuple(reversed(paths))) == (
        f"sha256:{expected.hexdigest()}"
    )


@pytest.mark.parametrize("kind", ["fifo", "symlink", "hardlink"])
def test_python_runtime_digest_rejects_non_regular_or_non_unique_entries(
    tmp_path: Path, kind: str
) -> None:
    if kind == "fifo":
        path = tmp_path / "entry"
        os.mkfifo(path)
    elif kind == "symlink":
        target = tmp_path / "target"
        target.write_bytes(b"target")
        path = tmp_path / "entry"
        path.symlink_to(target)
    else:
        target = tmp_path / "target"
        target.write_bytes(b"target")
        path = tmp_path / "entry"
        path.hardlink_to(target)
    with pytest.raises(TaskWriterError, match="regular|hardlink"):
        canonical_runtime_digest(tmp_path, ("entry",))


def test_python_runtime_manifest_is_deterministic_and_has_deployment_root() -> None:
    manifest = python_runtime_manifest(ROOT / "src" / "nl2repobench")
    assert manifest["schema_version"] == "1.0"
    assert manifest["digest_algorithm"] == RUNTIME_DIGEST_ALGORITHM
    assert re.fullmatch(
        r"/usr/local/lib/python[0-9]+\.[0-9]+/site-packages/nl2repobench",
        str(manifest["runtime_root"]),
    )
    files = manifest["files"]
    assert isinstance(files, list)
    paths = [str(entry["path"]) for entry in files]
    assert paths == sorted(paths, key=lambda value: value.encode("utf-8"))
    assert all(
        set(entry) == {"path", "sha256", "size_bytes", "mode", "type"}
        and entry["type"] == "file"
        for entry in files
    )
    assert manifest == python_runtime_manifest(ROOT / "src" / "nl2repobench")


def test_python_runtime_manifest_rejects_unlisted_special_file(tmp_path: Path) -> None:
    destination = tmp_path / "runtime"
    copy_python_verifier_runtime(destination)
    os.mkfifo(destination / "unlisted-fifo")
    manifest = python_runtime_manifest(destination / "nl2repobench")
    with pytest.raises(TaskWriterError, match="extra|missing|special"):
        validate_python_runtime_manifest(destination / "nl2repobench", manifest)


def test_python_transport_uses_fixed_isolated_bootstrap_and_cleans_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    request_id = "a" * 32
    response = {
        "schema_version": "1.0",
        "request_id": request_id,
        "returncode": 0,
        "stdout_base64": base64.b64encode(b"ok").decode("ascii"),
        "stderr_base64": "",
        "timed_out": False,
        "output_limit_exceeded": False,
        "cleanup_complete": True,
        "spawn_error": None,
        "cleanup_error": None,
    }

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, json.dumps(response).encode(), b"")

    monkeypatch.setenv("PYTHONPATH", "/attacker/controlled")
    monkeypatch.setattr(candidate_client.subprocess, "run", fake_run)
    result = candidate_client._invoke_cli(request_id, b"{}", 1.0)  # noqa: SLF001
    assert result.process.returncode == 0
    command = captured["command"]
    assert isinstance(command, list)
    assert "-I" in command and "-B" in command and "-c" in command
    assert candidate_client.PYTHON_RUNTIME_ROOT in str(command)
    environment = captured["kwargs"]["env"]
    assert "PYTHONPATH" not in environment
    assert environment == {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent"}


def test_python_compiler_generated_paths_have_no_address_space_limit() -> None:
    compiler = (ROOT / "src/nl2repobench/harbor/compiler.py").read_text(encoding="utf-8")
    runner = (ROOT / "src/nl2repobench/verification/candidate_runner.py").read_text(
        encoding="utf-8"
    )
    assert "--address-space-bytes" not in compiler
    assert "RLIMIT_AS" not in runner
    assert "verifier_memory_bytes" not in compiler


def test_node_staged_runtime_contract_has_no_wrapper_launchers() -> None:
    compiler = (ROOT / "src/nl2repobench/harbor/node_compiler.py").read_text(encoding="utf-8")
    pnpm = (ROOT / "src/nl2repobench/harbor/pnpm_compiler.py").read_text(encoding="utf-8")
    assert "NODE_RUNTIME_ROOT" in compiler
    assert "node_runtime_manifest" in compiler
    assert (
        "COPY --from=node-runtime /usr/local/bin/node /opt/nl2repobench-node/bin/node"
        in compiler
    )
    assert "ln -sf" not in compiler
    assert "npm install --global" not in pnpm
    assert "/opt/nl2repobench-node/lib/pnpm/bin/pnpm.cjs" in pnpm


def test_locked_node_toolchain_requires_manifest_identity() -> None:
    data = node_toolchain.tomllib.loads(
        (ROOT / "toolchain.node.lock.toml").read_text(encoding="utf-8")
    )
    data["runtime"].pop("node_runtime_manifest", None)
    data["runtime"].pop("node_runtime_manifest_sha256", None)
    data["runtime"].pop("node_runtime_tree_sha256", None)
    with pytest.raises(ValueError, match="manifest|runtime"):
        node_toolchain.NodeHarborToolchainLock.model_validate(data)
    lock = load_node_toolchain_lock(ROOT / "toolchain.node.lock.toml")
    assert lock.runtime.runtime_root == "/opt/nl2repobench-node"
    assert lock.runtime.node_runtime_manifest
    assert lock.runtime.node_runtime_manifest_sha256
    assert lock.runtime.node_runtime_tree_sha256


def test_go_lock_covers_full_shared_boundary_and_test_uses_one_interpreter() -> None:
    expected = {
        "src/nl2repobench/domain/command_plan.py",
        "src/nl2repobench/package_managers/go_modules.py",
        "src/nl2repobench/verification/candidate_process_cli.py",
        "src/nl2repobench/verification/go_bridge.py",
        "src/nl2repobench/verification/go_bridge_proxy.py",
        "src/nl2repobench/verification/go_command_plan.py",
        "src/nl2repobench/verification/go_contract_runner.py",
        "src/nl2repobench/verification/go_grader.py",
        "src/nl2repobench/verification/go_supervisor.py",
        "src/nl2repobench/verification/normalize/go_json.py",
        "src/nl2repobench/verification/process_cleanup.py",
        "src/nl2repobench/verification/subprocess_supervisor.py",
        "src/nl2repobench/verification/workspace_copy.py",
    }
    assert set(GO_RUNTIME_LOCK_FILES) == expected
    assert len(GO_RUNTIME_LOCK_FILES) == len(set(GO_RUNTIME_LOCK_FILES))
    compiler = GoHarborCompiler(ROOT / "toolchain.go.dev.lock.toml")
    script = compiler._test_script()  # noqa: SLF001
    assert "/usr/local/bin/python3" in script
    assert "/usr/bin/python3" not in script
    assert "python3 -I" not in script


def test_generated_docker_contexts_copy_and_validate_runtime_manifests() -> None:
    compiler = (ROOT / "src/nl2repobench/harbor/compiler.py").read_text(encoding="utf-8")
    node = (ROOT / "src/nl2repobench/harbor/node_compiler.py").read_text(encoding="utf-8")
    go = (ROOT / "src/nl2repobench/harbor/go_compiler.py").read_text(encoding="utf-8")
    assert "COPY runtime-manifest.json" in compiler
    assert "validate_python_runtime_manifest" in compiler
    assert "COPY python-runtime-manifest.json" in node
    assert "validate_python_runtime_manifest" in node
    assert "COPY runtime-manifest.json" in go
    assert "validate_python_runtime_manifest" in go


def test_private_migration_validator_rejects_placeholder_and_unbound_receipts() -> None:
    validator = _load_script("validate_private_artifact_migration.py")
    placeholder = {
        field: "placeholder"
        for field in validator.REQUIRED_FIELDS
        if field not in {"controls_receipts", "agent_visible"}
    }
    placeholder.update(
        {
            "controls_receipts": {name: "ok" for name in ("empty", "stub", "forgery", "offline")},
            "agent_visible": False,
            "old_task_version": "1.0.0",
            "new_task_version": "2.0.0",
            "old_artifact_digest": "sha256:" + "a" * 64,
            "new_artifact_digest": "sha256:" + "b" * 64,
        }
    )
    errors = validator.validate(placeholder)
    assert errors
    assert any(
        "digest" in error
        or "receipt" in error
        or "revision" in error
        or "verifier-only" in error
        for error in errors
    )

    bound = dict(placeholder)
    bound.update(
        {
            "migration_id": "migration-1",
            "task_id": "demo",
            "source_revision": "c" * 40,
            "old_manifest_digest": "sha256:" + "d" * 64,
            "new_manifest_digest": "sha256:" + "e" * 64,
            "runtime_digest": "sha256:" + "f" * 64,
            "toolchain_digest": "sha256:" + "1" * 64,
            "image_digest": "sha256:" + "2" * 64,
            "visibility": "verifier-only",
            "oracle_receipt": {"task_id": "other-task", "task_version": "2.0.0"},
            "reviewer_signoff": {"reviewer": "sol", "approved": True},
            "audit_receipt": {"task_id": "demo", "new_task_version": "2.0.0"},
        }
    )
    errors = validator.validate(bound)
    assert any("task" in error or "receipt" in error for error in errors)


def test_zero_bypass_scanner_rejects_aliases_and_suffix_trust(tmp_path: Path) -> None:
    scanner = _load_script("check_candidate_spawn_boundary.py")
    verification = tmp_path / "src/nl2repobench/verification"
    verification.mkdir(parents=True)
    (verification / "alias.py").write_text(
        "from subprocess import Popen\nPopen(['candidate'])\n", encoding="utf-8"
    )
    nested = verification / "nested" / "src/nl2repobench/verification"
    nested.mkdir(parents=True)
    (nested / "subprocess_supervisor.py").write_text(
        "import subprocess\nsubprocess.Popen(['candidate'])\n", encoding="utf-8"
    )
    node = verification / "alias.mjs"
    node.write_text(
        'import { spawnSync as launch } from "node:child_process";\nlaunch("candidate");\n',
        encoding="utf-8",
    )
    report = scanner.scan(tmp_path)
    assert not report["passed"]
    paths = {str(item["path"]) for item in report["violations"]}
    assert "src/nl2repobench/verification/alias.py" in paths
    assert (
        "src/nl2repobench/verification/nested/src/nl2repobench/verification/"
        "subprocess_supervisor.py"
        in paths
    )
    assert "src/nl2repobench/verification/alias.mjs" in paths


def test_zero_bypass_scanner_rejects_os_spawn_and_system(tmp_path: Path) -> None:
    scanner = _load_script("check_candidate_spawn_boundary.py")
    verification = tmp_path / "src/nl2repobench/verification"
    verification.mkdir(parents=True)
    (verification / "os_spawn.py").write_text(
        "import os\nos.system('candidate')\nos.spawnv(os.P_WAIT, 'candidate', [])\n",
        encoding="utf-8",
    )
    report = scanner.scan(tmp_path)
    assert not report["passed"]
    assert any(item["path"].endswith("os_spawn.py") for item in report["violations"])
