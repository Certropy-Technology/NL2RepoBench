from __future__ import annotations

import importlib.util
from pathlib import Path

from nl2repobench.harbor.node_compiler import NodeHarborCompiler

ROOT = Path(__file__).parents[1]


def _load_scanner():
    path = ROOT / "scripts/check_candidate_spawn_boundary.py"
    spec = importlib.util.spec_from_file_location("candidate_spawn_boundary", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_generated_python_trusted_invocations_are_absolute_isolated_and_no_as() -> None:
    compiler = _source("src/nl2repobench/harbor/compiler.py")
    trusted_helper = compiler.split("def _trusted_python_command", 1)[1].split(
        "def _select_command_plan", 1
    )[0]
    generated_sections = compiler.split("def _test_script", 1)[1]
    generated_sections += compiler.split("def _custom_test_script", 1)[1]
    for section in (trusted_helper, generated_sections):
        assert "--address-space-bytes" not in section
        assert "RLIMIT_AS" not in section
        assert "python -m nl2repobench" not in section
        assert "python3 -I" not in section
        assert "python -I -m" not in section
    assert "/usr/local/bin/python -I -B -c" in trusted_helper
    assert " -I -B " in trusted_helper


def test_generated_node_scripts_use_shared_install_boundary_and_python_manifest(
    tmp_path: Path,
) -> None:
    node = _source("src/nl2repobench/harbor/node_compiler.py")
    pnpm = _source("src/nl2repobench/harbor/pnpm_compiler.py")
    npm_adapter = tmp_path / "install_npm.py"
    pnpm_adapter = tmp_path / "install_pnpm.py"
    NodeHarborCompiler._write_npm_adapter(npm_adapter)  # noqa: SLF001
    NodeHarborCompiler._write_pnpm_adapter(pnpm_adapter)  # noqa: SLF001
    npm_adapter_source = npm_adapter.read_text(encoding="utf-8")
    pnpm_adapter_source = pnpm_adapter.read_text(encoding="utf-8")

    assert "install_candidate.mjs" not in node
    assert "install_candidate_pnpm.mjs" not in pnpm
    assert "node_candidate_install" in npm_adapter_source
    assert "run_node_command" in pnpm_adapter_source
    assert "/opt/nl2repobench-node/bin/node" in pnpm_adapter_source
    assert "/opt/nl2repobench-node/lib/pnpm/bin/pnpm.cjs" in pnpm_adapter_source
    assert "install_pnpm.py" not in pnpm_adapter_source
    for source in (node, pnpm):
        assert "COPY python-runtime /opt/nl2repobench-runtime" in source
        assert "COPY python-runtime-manifest.json /tests/python-runtime-manifest.json" in source
        assert (
            "COPY python-runtime-manifest-check.py /tests/python-runtime-manifest-check.py"
            in source
        )
        assert "python-runtime-manifest-check.py" in source
        assert "/usr/local/bin/python3 -I -B" in source
        assert "--root /opt/nl2repobench-runtime/nl2repobench" in source
        assert "--manifest /tests/python-runtime-manifest.json" in source


def test_node_trusted_bootstrap_has_no_interpreter_or_runtime_fallback() -> None:
    client = _source("src/nl2repobench/verification/node_candidate_client.py")
    grader = _source("src/nl2repobench/verification/node/grade-report.mjs")
    forbidden = (
        "sys.executable",
        "NL2REPO_PYTHON",
        "VIRTUAL_ENV",
        "NL2REPO_RUNTIME",
        "sourceRuntime",
        "pythonCandidates",
    )
    assert all(token not in client for token in forbidden)
    assert all(token not in grader for token in forbidden)
    assert "/usr/local/bin/python3" in grader or "/usr/local/bin/python" in grader
    assert "-I" in grader


def test_scanner_rejects_unapproved_trusted_file_calls_and_resource_prlimit(tmp_path: Path) -> None:
    scanner = _load_scanner()
    verification = tmp_path / "src/nl2repobench/verification"
    verification.mkdir(parents=True)
    (verification / "candidate_client.py").write_text(
        "import resource\nresource.prlimit(1, resource.RLIMIT_CPU, (1, 1))\n",
        encoding="utf-8",
    )
    (verification / "alias.py").write_text(
        "from os import system as launch\nlaunch('candidate')\n",
        encoding="utf-8",
    )
    (verification / "not_subprocess_supervisor.py").write_text(
        "import os\nos.fork()\n",
        encoding="utf-8",
    )
    report = scanner.scan(tmp_path)
    assert not report["passed"]
    paths = {str(item["path"]) for item in report["violations"]}
    assert "src/nl2repobench/verification/candidate_client.py" in paths
    assert "src/nl2repobench/verification/alias.py" in paths
    assert "src/nl2repobench/verification/not_subprocess_supervisor.py" in paths


def test_scanner_rejects_extra_spawn_inside_exact_trusted_node_runner(tmp_path: Path) -> None:
    scanner = _load_scanner()
    runner = tmp_path / "src/nl2repobench/verification/node/run_tests.mjs"
    runner.parent.mkdir(parents=True)
    runner.write_text(
        """
import { spawnSync } from "node:child_process";
const NODE_TEST_CLIENT = "fixed";
const command = process.execPath;
spawnSync(command, ["--test", "fixed-test.mjs"]);
spawnSync("/bin/sh", ["-c", "candidate"]);
""",
        encoding="utf-8",
    )
    report = scanner.scan(tmp_path)
    assert not report["passed"]
    assert any(
        item["path"] == "src/nl2repobench/verification/node/run_tests.mjs"
        and item["reason"] == "node-direct-spawn"
        for item in report["violations"]
    )


def test_scanner_accepts_exact_supervisor_fork_shape(tmp_path: Path) -> None:
    scanner = _load_scanner()
    supervisor = tmp_path / "src/nl2repobench/verification/subprocess_supervisor.py"
    supervisor.parent.mkdir(parents=True)
    supervisor.write_text("import os\npid = os.fork()\n", encoding="utf-8")
    report = scanner.scan(tmp_path)
    assert report["passed"]
