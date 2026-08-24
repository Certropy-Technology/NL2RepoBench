"""Untrusted-side adapter: runs the frozen schedule suite against candidate code.

This program is executed as the unprivileged ``candidate`` user via
``python -I``, which ignores ``PYTHONPATH``. Both the candidate site and the
locked runtime dependency site are therefore inserted onto ``sys.path``
explicitly. The candidate site is inserted last so it takes precedence for the
``schedule`` import while ``pytest`` and ``pytz`` resolve from the locked
dependency site.

The adapter writes a JSON report mapping pytest node ids to outcomes into a
trusted-created report file, so pytest's own console output can never pollute
the protocol boundary. It never receives Python source, import paths or shell
commands from its caller: only fixed trusted directory arguments chosen by
``run.py``.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys


def _worst(previous: str | None, candidate: str) -> str:
    """Fold per-phase pytest outcomes into one status per node id."""

    rank = {"passed": 0, "skipped": 1, "failed": 2}
    if previous is None:
        return candidate
    return candidate if rank[candidate] > rank[previous] else previous


class OutcomeCollector:
    """Record the worst outcome across setup/call/teardown for every node id."""

    def __init__(self) -> None:
        self.outcomes: dict[str, str] = {}
        self.collection_errors: list[str] = []

    def pytest_runtest_logreport(self, report: object) -> None:
        nodeid = getattr(report, "nodeid", "")
        if not nodeid:
            return
        if getattr(report, "outcome", "") == "failed":
            status = "failed"
        elif getattr(report, "outcome", "") == "skipped":
            status = "skipped"
        elif getattr(report, "when", "") == "call":
            status = "passed"
        else:
            return
        self.outcomes[nodeid] = _worst(self.outcomes.get(nodeid), status)

    def pytest_collectreport(self, report: object) -> None:
        if getattr(report, "outcome", "") == "failed":
            self.collection_errors.append(str(getattr(report, "nodeid", "") or "<root>"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site", required=True)
    parser.add_argument("--scratch", required=True)
    parser.add_argument("--test-file", required=True)
    parser.add_argument("--report", required=True)
    arguments = parser.parse_args()

    def emit(payload: dict[str, object]) -> None:
        with open(arguments.report, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, sort_keys=True)

    # Deterministic, offline interpreter behaviour for the graded run.
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    sys.path.insert(0, arguments.dependency_site)
    sys.path.insert(0, arguments.candidate_site)

    os.chdir(arguments.scratch)
    sys.path.insert(0, arguments.scratch)

    try:
        import pytest
    except Exception as error:  # pragma: no cover - locked dependency is present
        emit(
            {
                "ok": False,
                "error": type(error).__name__,
                "message": str(error),
                "outcomes": {},
                "collection_errors": ["pytest-unavailable"],
            }
        )
        return

    collector = OutcomeCollector()
    try:
        # pytest writes progress to stdout; send it to stderr so the trusted
        # side only ever consumes the JSON report file.
        with contextlib.redirect_stdout(sys.stderr):
            pytest.main(
                [
                    arguments.test_file,
                    "-p",
                    "no:cacheprovider",
                    "--confcutdir",
                    arguments.scratch,
                    "--continue-on-collection-errors",
                    "-q",
                    "--no-header",
                    "-o",
                    "addopts=",
                ],
                plugins=[collector],
            )
    except BaseException as error:  # noqa: BLE001 - report, never crash the boundary
        emit(
            {
                "ok": False,
                "error": type(error).__name__,
                "message": str(error)[:2000],
                "outcomes": collector.outcomes,
                "collection_errors": collector.collection_errors,
            }
        )
        return

    emit(
        {
            "ok": True,
            "outcomes": collector.outcomes,
            "collection_errors": collector.collection_errors,
        }
    )


if __name__ == "__main__":
    main()
