"""Trusted custom-json-v1 verifier for the pss task.

This module runs as root inside the verifier image under ``python -I``. It must
never import candidate code. The frozen upstream test fixture is executed in a
child process as the unprivileged ``candidate`` user, and exactly
``len(SCORED_NODES)`` leaves are reported on one line of JSON.

The frozen upstream revision collects 46 items, all of which are scored, so the
denominator is the full collection. The child process runs from a neutral empty
directory rather than the candidate repository root, so the candidate cannot put
``psslib`` or a shadowing ``test`` package on ``sys.path`` through the working
directory. ``psslib`` must therefore come from the installed candidate site.
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
CANDIDATE_SITE = Path("/tmp/candidate-site")
DEPENDENCY_SITE = Path("/opt/candidate-dependencies/site")
FIXTURE_ROOT = Path("/tmp/pss-fixture")
RUN_ROOT = Path("/tmp/pss-run")
RESULT_ROOT = Path("/tmp/pss-results")
JUNIT = RESULT_ROOT / "junit.xml"
INTERNAL_ERROR_EXIT = 70

# Names the candidate could install into its own site directory to shadow the
# frozen fixture or to execute code at interpreter start-up. ``psslib`` is the
# package under test and is deliberately not removed.
SHADOW_NAMES = (
    "test",
    "test.py",
    "conftest.py",
    "sitecustomize.py",
    "usercustomize.py",
    "pytest.ini",
    "tox.ini",
    "setup.cfg",
    "pyproject.toml",
)


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
    required = (
        "test/__init__.py",
        "test/utils.py",
        "test/test_contentmatcher.py",
        "test/test_driver.py",
        "test/test_filefinder.py",
        "test/test_pssmain.py",
        "test/testdirs/testdir1/filea.c",
    )
    for relative in required:
        if not (FIXTURE_ROOT / relative).is_file():
            _fail(f"frozen fixture is incomplete: {relative}")


def _prepare_candidate_site() -> None:
    """Remove candidate paths that could shadow the fixture or run at start-up."""

    for name in SHADOW_NAMES:
        target = CANDIDATE_SITE / name
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.is_dir():
            shutil.rmtree(target)


def _prepare_run_root() -> None:
    """Provide a neutral, candidate-writable working directory for pytest."""

    if RUN_ROOT.exists():
        shutil.rmtree(RUN_ROOT)
    RUN_ROOT.mkdir(parents=True)
    os.chown(RUN_ROOT, CANDIDATE_UID, CANDIDATE_UID)
    RUN_ROOT.chmod(0o700)


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
        "LANG=C.UTF-8",
        "LC_ALL=C.UTF-8",
        "PYTHONHASHSEED=0",
        "PYTHONDONTWRITEBYTECODE=1",
        "PYTHONNOUSERSITE=1",
        f"PYTHONPATH={CANDIDATE_SITE}:{DEPENDENCY_SITE}",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
        "/usr/local/bin/python",
        "-B",
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "--continue-on-collection-errors",
        f"--rootdir={FIXTURE_ROOT}",
        str(FIXTURE_ROOT / "test"),
        f"--junitxml={JUNIT}",
        "--tb=short",
    ]
    return subprocess.run(
        command,
        cwd=str(RUN_ROOT),
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
    _prepare_candidate_site()
    _prepare_run_root()
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
        matched = [status for key, status in statuses.items() if key == node]
        status = "passed" if matched and all(item == "passed" for item in matched) else "failed"
        leaves.append({"id": node, "status": status})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
