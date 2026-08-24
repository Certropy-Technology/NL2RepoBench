from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

from defusedxml import ElementTree


ROOT = Path("/tests/verifier")


def main() -> None:
    fixture = Path("/tmp/pyperclip-tests")
    junit = Path("/tmp/pyperclip-junit.xml")
    if fixture.exists():
        shutil.rmtree(fixture)
    shutil.copytree(ROOT / "fixture/tests", fixture, ignore=shutil.ignore_patterns("__pycache__"))
    fixture.chmod(0o555)
    for path in fixture.rglob("*"):
        path.chmod(0o555 if path.is_dir() else 0o444)
    print(
        f"fixture={fixture} exists={fixture.is_dir()} "
        f"test={fixture / 'test_contract.py'} "
        f"test_exists={(fixture / 'test_contract.py').is_file()}",
        file=os.sys.stderr,
    )
    junit.write_text("", encoding="utf-8")
    os.chown(junit, 10001, 10001)
    junit.chmod(0o660)
    completed = subprocess.run(
        [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "PYTHONNOUSERSITE=1",
            "PYTHONPATH=/tmp/candidate-site:/opt/candidate-dependencies/site",
            "/usr/local/bin/python",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            str(fixture / "test_contract.py"),
            f"--junitxml={junit}",
            "--tb=short",
        ],
        cwd="/workspace" if Path("/workspace").is_dir() else None,
        capture_output=True,
        text=True,
        timeout=360,
        check=False,
    )
    if not junit.is_file() or junit.stat().st_size == 0:
        print(
            f"pytest did not produce JUnit: rc={completed.returncode} "
            f"stdout={completed.stdout[-1000:]} stderr={completed.stderr[-2000:]}",
            file=os.sys.stderr,
        )
        print(completed.stderr[-4000:], file=os.sys.stderr)
        raise SystemExit(70)
    cases = list(ElementTree.parse(junit).getroot().iter("testcase"))
    if len(cases) != 10:
        print(
            f"unexpected case count: {len(cases)} rc={completed.returncode} "
            f"stdout={completed.stdout[-2000:]} stderr={completed.stderr[-4000:]}",
            file=os.sys.stderr,
        )
        raise SystemExit(70)
    leaves = []
    for case in cases:
        status = "failed"
        if case.find("skipped") is not None:
            status = "skipped"
        elif case.find("failure") is None and case.find("error") is None:
            status = "passed"
        leaves.append(
            {
                "id": f"{case.get('classname', 'pyperclip')}::{case.get('name', '')}",
                "status": status,
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
