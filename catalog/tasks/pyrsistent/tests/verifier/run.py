"""Normalize the frozen pyrsistent fixture into custom-json-v1 leaves."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path("/tests/verifier")
FIXTURE = Path("/tmp/pyrsistent-tests")
JUNIT = Path("/tmp/pyrsistent-junit.xml")
NODE_IDS = ROOT / "nodeids.json"
CANDIDATE_UID = 10001


def _stage_fixture() -> None:
    if FIXTURE.exists():
        shutil.rmtree(FIXTURE)
    shutil.copytree(ROOT / "fixture", FIXTURE)
    shutil.copy2(ROOT / "adapter.py", FIXTURE / "adapter.py")
    for path in FIXTURE.rglob("*"):
        path.chmod(0o555 if path.is_dir() else 0o444)
    FIXTURE.chmod(0o555)


def _run_tests() -> subprocess.CompletedProcess[str]:
    JUNIT.write_text("", encoding="utf-8")
    subprocess.run(
        ["chown", f"{CANDIDATE_UID}:{CANDIDATE_UID}", str(JUNIT)],
        check=True,
    )
    JUNIT.chmod(0o600)
    command = [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "HOME=/tmp",
            "PYTHONNOUSERSITE=1",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            "/usr/local/bin/python",
            "-I",
            "-B",
            str(FIXTURE / "adapter.py"),
            "-p",
            "no:cacheprovider",
            "--continue-on-collection-errors",
            f"--junitxml={JUNIT}",
            "-q",
            ".",
        ]
    try:
        return subprocess.run(
            command,
            cwd=FIXTURE,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            command,
            124,
            exc.stdout or "",
            (exc.stderr or "") + "\ncandidate-timeout",
        )


def _junit_statuses() -> dict[tuple[str, str], str]:
    if not JUNIT.is_file() or JUNIT.stat().st_size == 0:
        return {}
    try:
        cases = list(ET.parse(JUNIT).getroot().iter("testcase"))
    except (ET.ParseError, OSError):
        return {}
    statuses: dict[tuple[str, str], str] = {}
    for case in cases:
        status = "failed"
        if case.find("skipped") is not None:
            status = "skipped"
        elif case.find("failure") is None and case.find("error") is None:
            status = "passed"
        statuses[(case.get("classname", ""), case.get("name", ""))] = status
    return statuses


def _junit_key(node_id: str) -> tuple[str, str]:
    parts = node_id.split("::")
    module = parts[0].replace("/", ".").removesuffix(".py")
    if len(parts) == 2:
        return module, parts[1]
    return f"{module}.{parts[1]}", parts[2]


def main() -> None:
    frozen_node_ids = json.loads(NODE_IDS.read_text(encoding="utf-8"))
    _stage_fixture()
    completed = _run_tests()
    statuses = _junit_statuses()
    if not statuses:
        print(
            f"frozen suite produced no JUnit cases: rc={completed.returncode}; "
            f"stderr={completed.stderr[-2000:]}",
            file=sys.stderr,
        )
    leaves = [
        {"id": node_id, "status": statuses.get(_junit_key(node_id), "failed")}
        for node_id in frozen_node_ids
    ]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
