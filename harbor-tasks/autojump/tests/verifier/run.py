"""Trusted custom-json-v1 verifier for the autojump task.

This module runs as root inside the verifier image under ``python -I``. It must
never import candidate code. The frozen upstream test fixture is executed in a
child process as the unprivileged ``candidate`` user, and exactly
``len(SCORED_NODES)`` leaves are reported on one line of JSON.

The upstream fixture collects 32 items at the pinned revision: 23 scored nodes,
4 ``xfail`` nodes and 5 Python-2-only ``skipif`` nodes. Only the 23 scored nodes
form the frozen denominator, so a candidate cannot change the denominator by
altering platform detection helpers.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from defusedxml import ElementTree

ROOT = Path("/tests/verifier")
CANDIDATE_UID = 10001
CANDIDATE_ROOT = Path("/tmp/candidate")
FIXTURE_ROOT = Path("/tmp/autojump-fixture")
RESULT_ROOT = Path("/tmp/autojump-results")
JUNIT = RESULT_ROOT / "junit.xml"
INTERNAL_ERROR_EXIT = 70

# Candidate-controlled paths that could otherwise shadow the frozen ``tests``
# package or execute at interpreter start-up, because the candidate repository
# root is the working directory and therefore on ``sys.path``.
SHADOW_PATHS = ("tests", "tests.py", "conftest.py", "sitecustomize.py", "usercustomize.py")


def _fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(INTERNAL_ERROR_EXIT)


def _scored_nodes() -> list[str]:
    data = json.loads((ROOT / "scored-nodes.json").read_text(encoding="utf-8"))
    nodes = data["scored_nodes"]
    if not isinstance(nodes, list) or len(nodes) != len(set(nodes)) or not nodes:
        _fail("scored-nodes.json is not a unique non-empty list")
    return [str(node) for node in nodes]


def _install_fixture() -> None:
    """Copy the frozen fixture to a root-owned, candidate-readable location."""

    if FIXTURE_ROOT.exists():
        shutil.rmtree(FIXTURE_ROOT)
    shutil.copytree(
        ROOT / "fixture",
        FIXTURE_ROOT,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    for path in [FIXTURE_ROOT, *FIXTURE_ROOT.rglob("*")]:
        os.chown(path, 0, 0)
        path.chmod(0o555 if path.is_dir() else 0o444)
    if not (FIXTURE_ROOT / "tests/unit/autojump_utils_test.py").is_file():
        _fail("frozen fixture is incomplete")


def _prepare_candidate() -> None:
    """Remove candidate paths that could shadow or hijack the frozen fixture."""

    for name in SHADOW_PATHS:
        target = CANDIDATE_ROOT / name
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.is_dir():
            shutil.rmtree(target)


def _prepare_junit() -> None:
    if RESULT_ROOT.exists():
        shutil.rmtree(RESULT_ROOT)
    RESULT_ROOT.mkdir(parents=True)
    os.chown(RESULT_ROOT, 0, 0)
    # Traversable but not listable, so the candidate cannot enumerate the path.
    RESULT_ROOT.chmod(0o711)
    JUNIT.write_text("", encoding="utf-8")
    os.chown(JUNIT, CANDIDATE_UID, CANDIDATE_UID)
    JUNIT.chmod(0o600)


def _run_pytest() -> subprocess.CompletedProcess[str]:
    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/tmp/candidate-build/home",
        "TMPDIR=/tmp/candidate-build/tmp",
        "PYTHONDONTWRITEBYTECODE=1",
        "PYTHONNOUSERSITE=1",
        "PYTHONPATH=/tmp/candidate-site:/opt/candidate-dependencies/site",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
        "/usr/local/bin/python",
        "-B",
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "--continue-on-collection-errors",
        f"--rootdir={FIXTURE_ROOT}",
        str(FIXTURE_ROOT / "tests"),
        f"--junitxml={JUNIT}",
        "--tb=short",
    ]
    return subprocess.run(
        command,
        cwd=str(CANDIDATE_ROOT),
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )


def _observed_statuses() -> dict[str, str]:
    """Map ``classname::name`` to a status parsed from the JUnit report."""

    if not JUNIT.is_file() or JUNIT.is_symlink() or JUNIT.stat().st_size == 0:
        return {}
    try:
        cases = list(ElementTree.parse(str(JUNIT)).getroot().iter("testcase"))
    except Exception:  # noqa: BLE001 - a corrupt report is a candidate failure
        return {}
    statuses: dict[str, str] = {}
    for case in cases:
        node = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("failure") is not None or case.find("error") is not None:
            status = "failed"
        elif case.find("skipped") is not None:
            status = "skipped"
        else:
            status = "passed"
        # A duplicated node id is ambiguous, so keep the worst observed status.
        if statuses.get(node) == "failed":
            continue
        statuses[node] = status
    return statuses


def main() -> None:
    scored = _scored_nodes()
    _install_fixture()
    _prepare_candidate()
    _prepare_junit()
    try:
        completed = _run_pytest()
    except subprocess.TimeoutExpired:
        completed = None
    statuses = _observed_statuses()
    if not statuses and completed is not None:
        print(
            f"pytest produced no usable JUnit report: rc={completed.returncode} "
            f"stdout={completed.stdout[-2000:]} stderr={completed.stderr[-2000:]}",
            file=sys.stderr,
        )
    leaves = []
    for node in scored:
        # Only an observed pass counts. A missing, skipped or failed node is a
        # candidate failure, so the denominator stays fixed at len(scored).
        matched = [status for key, status in statuses.items() if key.endswith(node)]
        status = "passed" if matched and all(item == "passed" for item in matched) else "failed"
        leaves.append({"id": node, "status": status})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
