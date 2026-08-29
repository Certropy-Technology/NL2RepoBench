#!/usr/bin/env python3
"""Run the frozen test suite in a child process and emit custom-json-v1."""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _failed(ids: list[str], message: str) -> list[dict[str, str]]:
    return [{"id": nodeid, "message": message, "status": "failed"} for nodeid in ids]


def main() -> int:
    root = Path(__file__).resolve().parent
    expected = json.loads((root / "expected_nodeids.json").read_text(encoding="utf-8"))
    expected_ids = [str(item) for item in expected]
    junit = Path("/tmp/trusted-results/pyasn1-modules-junit.xml")
    child = subprocess.run(
        [sys.executable, "-I", str(root / "child_runner.py"), str(root / "tests"), str(junit)],
        capture_output=True,
        text=True,
        cwd=root.parent,
        timeout=570,
        check=False,
    )
    if child.returncode not in {0, 1} or not junit.is_file():
        report = {"schema_version": "1.0", "leaves": _failed(expected_ids, "child test runner failed")}
        print(json.dumps(report, sort_keys=True))
        return 0

    observed: dict[str, dict[str, str]] = {}
    try:
        tree = ET.parse(junit)
        for case in tree.iter("testcase"):
            classname = case.attrib.get("classname", "")
            name = case.attrib.get("name", "")
            nodeid = f"{classname}::{name}"
            if case.find("failure") is not None or case.find("error") is not None:
                status = "failed"
                message = "test assertion or runtime error"
            elif case.find("skipped") is not None:
                status = "skipped"
                message = "skipped"
            else:
                status = "passed"
                message = ""
            leaf = {"id": nodeid, "message": message, "status": status}
            observed[nodeid] = leaf
            if nodeid.startswith("test_"):
                observed[f"tests.{nodeid}"] = leaf
    except (OSError, ET.ParseError):
        observed = {}

    leaves: list[dict[str, str]] = []
    for nodeid in expected_ids:
        leaf = observed.get(nodeid)
        if leaf is None:
            leaf = {"id": nodeid, "message": "test was not collected", "status": "failed"}
        leaves.append(leaf)
    report = {"schema_version": "1.0", "leaves": leaves}
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
