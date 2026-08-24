"""Trusted custom-json-v1 verifier for the frozen retrying hidden slice.

Runs as root under ``python -I`` from
``nl2repobench.verification.custom_verifier``. It never imports candidate code:
the hidden pytest slice is executed in a child process as the unprivileged
``candidate`` user, and only its JUnit XML is parsed here.

The denominator is fixed by ``FROZEN_NODE_IDS`` (23 leaves, frozen from
``git archive 3a435e8ba85d85d7300a3609cb6f3ba8cb4bc170``). Results are projected
onto that list, so a candidate that breaks collection or deletes tests yields
``failed`` leaves rather than a shrunken denominator.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

from defusedxml import ElementTree

ROOT = Path("/tests/verifier")
FIXTURE = Path("/tmp/retrying-tests")
JUNIT = Path("/tmp/retrying-junit.xml")
CANDIDATE_UID = 10001

FROZEN_NODE_IDS = (
    "test_retrying.py::TestStopConditions::test_legacy_explicit_stop_type",
    "test_retrying.py::TestStopConditions::test_never_stop",
    "test_retrying.py::TestStopConditions::test_stop_after_attempt",
    "test_retrying.py::TestStopConditions::test_stop_after_delay",
    "test_retrying.py::TestStopConditions::test_stop_func",
    "test_retrying.py::TestWaitConditions::test_exponential",
    "test_retrying.py::TestWaitConditions::test_exponential_with_max_wait",
    "test_retrying.py::TestWaitConditions::test_exponential_with_max_wait_and_multiplier",
    "test_retrying.py::TestWaitConditions::test_fixed_sleep",
    "test_retrying.py::TestWaitConditions::test_incrementing_sleep",
    "test_retrying.py::TestWaitConditions::test_legacy_explicit_wait_type",
    "test_retrying.py::TestWaitConditions::test_no_sleep",
    "test_retrying.py::TestWaitConditions::test_random_sleep",
    "test_retrying.py::TestWaitConditions::test_random_sleep_without_min",
    "test_retrying.py::TestWaitConditions::test_wait_func",
    "test_retrying.py::TestDecoratorWrapper::test_defaults",
    "test_retrying.py::TestDecoratorWrapper::test_retry_if_exception_of_type",
    "test_retrying.py::TestDecoratorWrapper::test_with_stop_on_exception",
    "test_retrying.py::TestDecoratorWrapper::test_with_stop_on_return_value",
    "test_retrying.py::TestDecoratorWrapper::test_with_wait",
    "test_retrying.py::TestDecoratorWrapper::test_wrapped_exception",
    "test_retrying.py::TestBeforeAfterAttempts::test_after_attempts",
    "test_retrying.py::TestBeforeAfterAttempts::test_before_attempts",
)


def _stage_fixture() -> Path:
    """Copy the hidden slice to a candidate-readable, read-only location."""

    if FIXTURE.exists():
        shutil.rmtree(FIXTURE)
    shutil.copytree(
        ROOT / "fixture", FIXTURE, ignore=shutil.ignore_patterns("__pycache__")
    )
    adapter = FIXTURE / "adapter.py"
    shutil.copy2(ROOT / "adapter.py", adapter)
    for path in FIXTURE.rglob("*"):
        path.chmod(0o555 if path.is_dir() else 0o444)
    FIXTURE.chmod(0o555)
    return adapter


def _run_slice(adapter: Path) -> subprocess.CompletedProcess[str]:
    JUNIT.write_text("", encoding="utf-8")
    # pytest writes JUnit as the candidate user, so the file must be owned by it.
    Path(JUNIT).chmod(0o666)
    subprocess.run(
        ["chown", f"{CANDIDATE_UID}:{CANDIDATE_UID}", str(JUNIT)], check=True
    )
    return subprocess.run(
        [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "PYTHONNOUSERSITE=1",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            "HOME=/tmp",
            "/usr/local/bin/python",
            "-I",
            "-B",
            str(adapter),
            "-p",
            "no:cacheprovider",
            str(FIXTURE / "test_retrying.py"),
            f"--junitxml={JUNIT}",
            "--tb=short",
            "-q",
        ],
        cwd="/tmp",
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )


def _leaf_key(class_name: str, test_name: str) -> tuple[str, str]:
    """Key a result by class and test name.

    pytest derives the JUnit ``classname`` from the module path relative to
    rootdir, which depends on where the fixture is staged. Only the trailing
    class component is stable, so the frozen ids are matched on
    ``(class, test)`` instead of on the full dotted path.
    """

    return (class_name.rpartition(".")[2], test_name)


def _parse_statuses() -> dict[tuple[str, str], str]:
    if not JUNIT.is_file() or JUNIT.stat().st_size == 0:
        return {}
    try:
        cases = list(ElementTree.parse(JUNIT).getroot().iter("testcase"))
    except ElementTree.ParseError:
        return {}
    statuses: dict[tuple[str, str], str] = {}
    for case in cases:
        status = "failed"
        if case.find("skipped") is not None:
            status = "skipped"
        elif case.find("failure") is None and case.find("error") is None:
            status = "passed"
        statuses[_leaf_key(case.get("classname", ""), case.get("name", ""))] = status
    return statuses


def main() -> None:
    adapter = _stage_fixture()
    completed = _run_slice(adapter)
    statuses = _parse_statuses()
    if not statuses:
        print(
            "hidden slice produced no JUnit cases: "
            f"rc={completed.returncode} stdout={completed.stdout[-2000:]} "
            f"stderr={completed.stderr[-2000:]}",
            file=sys.stderr,
        )
    leaves = []
    for node_id in FROZEN_NODE_IDS:
        _, _, tail = node_id.partition("::")
        class_name, _, test_name = tail.partition("::")
        leaves.append(
            {
                "id": node_id,
                "status": statuses.get(_leaf_key(class_name, test_name), "failed"),
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
