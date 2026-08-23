"""Bounded runner for private task-specific JSON verifier entrypoints."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MAX_REPORT_BYTES = 4 * 1024 * 1024
VALID_STATUSES = {"passed", "failed", "skipped"}


def _write_junit(path: Path, leaves: list[dict[str, object]]) -> None:
    suite = ET.Element("testsuite", name="custom-json-v1", tests=str(len(leaves)))
    for leaf in leaves:
        case = ET.SubElement(suite, "testcase", name=str(leaf["id"]), classname="custom")
        status = leaf["status"]
        if status == "failed":
            ET.SubElement(case, "failure", message=str(leaf.get("message", "failed")))
        elif status == "skipped":
            ET.SubElement(case, "skipped")
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element("testsuites", name="custom-json-v1")
    root.append(suite)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def run(entrypoint: Path, expected: int, junit: Path, collection: Path, timeout: float) -> int:
    if entrypoint.is_symlink() or not entrypoint.is_file():
        return 70
    try:
        completed = subprocess.run(
            [sys.executable, "-I", str(entrypoint)],
            cwd="/workspace" if Path("/workspace").is_dir() else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return 70
    if completed.returncode != 0:
        return 70
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines or len(completed.stdout.encode("utf-8")) > MAX_REPORT_BYTES:
        return 70
    try:
        report = json.loads(lines[-1])
        leaves = report["leaves"]
    except (KeyError, TypeError, json.JSONDecodeError):
        return 70
    if (
        report.get("schema_version") != "1.0"
        or not isinstance(leaves, list)
        or len(leaves) != expected
        or any(
            not isinstance(leaf, dict)
            or not isinstance(leaf.get("id"), str)
            or not leaf["id"]
            or leaf.get("status") not in VALID_STATUSES
            for leaf in leaves
        )
        or len({leaf["id"] for leaf in leaves}) != len(leaves)
    ):
        return 70
    collection.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "collected": len(leaves),
                "nodeids": [x["id"] for x in leaves],
                "collection_errors": [],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_junit(junit, leaves)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entrypoint", type=Path, required=True)
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--junit", type=Path, required=True)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--timeout-sec", type=float, default=300.0)
    args = parser.parse_args()
    raise SystemExit(
        run(args.entrypoint, args.expected, args.junit, args.collection, args.timeout_sec)
    )


if __name__ == "__main__":
    main()
