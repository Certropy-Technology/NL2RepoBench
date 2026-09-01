from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest


def _load_scanner():
    path = Path(__file__).parents[1] / "scripts/check_candidate_spawn_boundary.py"
    spec = importlib.util.spec_from_file_location("candidate_spawn_gate", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = _load_scanner()


def _scan_file(tmp_path: Path, relative: str, text: str) -> dict[str, object]:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    gate._DEFAULT_ROOTS = (relative,)  # noqa: SLF001
    return gate.scan(tmp_path)


@pytest.mark.parametrize(
    "text",
    [
        "import subprocess as sp\nsp.run(['candidate'])\n",
        "from subprocess import Popen as launch\nlaunch(['candidate'])\n",
        "import os as operating\noperating.system('candidate')\n",
        "from os import spawnv as launch\nlaunch(0, 'candidate', [])\n",
        "import resource\nresource.setrlimit(resource.RLIMIT_AS, (1, 1))\n",
        "import subprocess\nsubprocess.run(['candidate'], shell=True)\n",
    ],
)
def test_python_aliases_and_memory_controls_are_blocked(tmp_path: Path, text: str) -> None:
    report = _scan_file(tmp_path, "src/pkg.py", text)
    assert report["passed"] is False
    assert report["violations"]


def test_python_near_name_is_not_a_trusted_exception(tmp_path: Path) -> None:
    report = _scan_file(
        tmp_path,
        "src/nl2repobench/verification/candidate_client_extra.py",
        "import subprocess as transport\n"
        "transport.run(['python', '-I', '-c', 'candidate_process_cli'], stdin=b'{}')\n",
    )
    assert report["passed"] is False
    assert any(item["reason"] == "python-direct-spawn" for item in report["violations"])


def test_exact_candidate_transport_exception_is_path_bound(tmp_path: Path) -> None:
    report = _scan_file(
        tmp_path,
        "src/nl2repobench/verification/candidate_client.py",
        "import subprocess\n"
        "def invoke():\n"
        "    command = ['python', '-I', 'candidate_process_cli']\n"
        "    return subprocess.run(command, stdin=b'{}')\n",
    )
    assert report["passed"] is True
    assert report["violations"] == []


def test_exact_supervisor_exception_allows_explicit_os_fork(tmp_path: Path) -> None:
    report = _scan_file(
        tmp_path,
        "src/nl2repobench/verification/subprocess_supervisor.py",
        "import os\n"
        "pid = os.fork()\n"
        "os.execve('/bin/true', ['true'], {})\n",
    )
    assert report["passed"] is True


@pytest.mark.parametrize(
    "text",
    [
        "import { spawnSync as launch } from 'node:child_process';\nlaunch('x');\n",
        "import * as child from 'node:child_process';\nchild.spawnSync('x');\n",
        "const { spawnSync: launch } = require('node:child_process');\nlaunch('x');\n",
        "const cp = require('node:child_process');\ncp.execFile('x');\n",
    ],
)
def test_node_aliases_are_blocked(tmp_path: Path, text: str) -> None:
    report = _scan_file(tmp_path, "src/client.mjs", text)
    assert report["passed"] is False
    assert any(item["reason"] == "node-direct-spawn" for item in report["violations"])


def test_exact_node_verifier_exception_is_path_bound(tmp_path: Path) -> None:
    report = _scan_file(
        tmp_path,
        "src/nl2repobench/verification/node/run_tests.mjs",
        "import { spawnSync } from 'node:child_process';\n"
        "const client = process.env.NODE_TEST_CLIENT;\n"
        "spawnSync(process.execPath, ['--test', client]);\n",
    )
    assert report["passed"] is True


def test_near_name_node_exception_and_historical_private_client_are_blocked(
    tmp_path: Path,
) -> None:
    near = tmp_path / "src/nl2repobench/verification/node/run_tests_copy.mjs"
    near.parent.mkdir(parents=True)
    near.write_text(
        "import { spawnSync } from 'node:child_process';\nspawnSync('candidate');\n",
        encoding="utf-8",
    )
    historical = tmp_path / "catalog/sources/ansi-styles/harbor/tests/private/test_client.mjs"
    historical.parent.mkdir(parents=True)
    historical.write_text(
        "const { spawnSync } = require('node:child_process');\nspawnSync('candidate');\n",
        encoding="utf-8",
    )
    gate._DEFAULT_ROOTS = ("src", "catalog/sources")  # noqa: SLF001
    report = gate.scan(tmp_path)
    paths = {item["path"] for item in report["violations"]}
    assert "src/nl2repobench/verification/node/run_tests_copy.mjs" in paths
    assert "catalog/sources/ansi-styles/harbor/tests/private/test_client.mjs" in paths


def test_symlink_and_special_paths_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "src"
    root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("import subprocess\nsubprocess.run(['x'])\n", encoding="utf-8")
    (root / "escape.py").symlink_to(outside)
    fifo = root / "special"
    os.mkfifo(fifo)
    gate._DEFAULT_ROOTS = ("src",)  # noqa: SLF001
    report = gate.scan(tmp_path)
    assert report["passed"] is False
    reasons = {item["reason"] for item in report["violations"]}
    assert "unsafe-path" in reasons or "symlink-path" in reasons
    assert "special-path" in reasons
