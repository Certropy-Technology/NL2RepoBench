from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest


class LeafCollector:
    def __init__(self) -> None:
        self.nodeids: list[str] = []
        self.status: dict[str, str] = {}
        self.messages: dict[str, str] = {}

    def pytest_collection_modifyitems(self, items: list[Any]) -> None:
        self.nodeids = [item.nodeid for item in items]

    def pytest_runtest_logreport(self, report: Any) -> None:
        if report.when not in {"setup", "call", "teardown"}:
            return
        if report.outcome == "failed":
            self.status[report.nodeid] = "failed"
            self.messages[report.nodeid] = str(report.longrepr)[-1200:]
        elif report.outcome == "skipped" and report.nodeid not in self.status:
            self.status[report.nodeid] = "skipped"
        elif report.when == "call" and report.nodeid not in self.status:
            self.status[report.nodeid] = "passed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site", required=True)
    parser.add_argument("--tests", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    if not Path(args.dependency_site).is_dir():
        raise ValueError("dependency site is unavailable")
    sys.path.insert(0, args.candidate_site)
    sys.path.insert(1, args.dependency_site)

    collector = LeafCollector()
    exit_code = pytest.main(
        ["-q", "-o", "addopts=", str(Path(args.tests).resolve())],
        plugins=[collector],
    )
    leaves = []
    for nodeid in collector.nodeids:
        status = collector.status.get(nodeid, "failed")
        leaves.append(
            {
                "id": f"furl/{nodeid}",
                "status": status,
                "message": collector.messages.get(nodeid, ""),
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0 if exit_code in {0, 1} else 2


if __name__ == "__main__":
    raise SystemExit(main())
