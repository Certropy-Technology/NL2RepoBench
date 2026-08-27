"""Emit a bounded, deterministic pytest leaf report for the trusted wrapper."""

from __future__ import annotations

import json
import sys

_OUTCOMES = {}

def pytest_collection_modifyitems(session, config, items):  # noqa: ARG001
    config._nl2repo_items = [item.nodeid for item in items]


def pytest_runtest_logreport(report):
    if report.when == "call":
        _OUTCOMES[report.nodeid] = report.outcome
    elif report.when == "setup" and report.failed:
        _OUTCOMES[report.nodeid] = "failed"
    elif report.when == "setup" and report.skipped:
        _OUTCOMES[report.nodeid] = "skipped"


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001
    config = session.config
    items = getattr(config, "_nl2repo_items", [])
    leaves = [
        {"id": nodeid, "status": _OUTCOMES.get(nodeid, "failed")}
        for nodeid in items
    ]
    print(
        "NL2REPO_REPORT="
        + json.dumps(
            {"schema_version": "boto3-pytest-v1", "leaves": leaves},
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    sys.stdout.flush()
