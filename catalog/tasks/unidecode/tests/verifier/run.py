#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import subprocess
import sys


ADAPTER = Path(__file__).with_name("adapter.py")
CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
EXPECTED = {
    "api-surface": {
        "alias": True,
        "cache_type": "dict",
        "error_base": True,
        "error_index": None,
        "signatures": [
            "(string: str, errors: str = 'ignore', replace_str: str = '?') -> str",
            "(string: str, errors: str = 'ignore', replace_str: str = '?') -> str",
        ],
    },
    "package-contract": {"version": "1.4.0", "typed": True},
    "ascii-identity": {"all_equal": True, "all_str": True},
    "western": ["kozuscek", "CZSczs", "prilis zlutoucky kun pel dabelske ody"],
    "multiscript": ["Knosos", "Privet mir!", "a", "konnichihaShi Jie ", "Bei Jing "],
    "mixed-text": ["Hello, Shi Jie !", "Efficient", "30 km/h +- 5%", "degFdegC"],
    "wide-unicode": ["Aa0123456789", "km/h"],
    "enclosed-fullwidth": ["aA20(20)20.20100", "the quick"],
    "entrypoint-equivalence": ["CZSczs", "CZSczs", "CZSczs"],
    "empty-and-controls": ["", "Hello, World!\r\n", "\u0000\t\n"],
    "errors-ignore": "test  test",
    "errors-replace": ["test ? test", "test [?]  test"],
    "errors-strict": ["UnidecodeError", 5, True, True],
    "errors-preserve": ["test \U000f0000 test", False],
    "errors-invalid": ["UnidecodeError", None, True],
    "surrogate-warning": ["", 1, "RuntimeWarning", True],
    "cache-lazy-hit": [False, "C", True, [1], "Z", True],
    "cache-missing-block": ["", [165], True, "", True],
    "cli-command-text": [0, "Bei Jing \n", ""],
    "cli-streams": [0, "Ge ", 0, "Ge "],
}


def run_case(case: str) -> dict[str, object]:
    command = [sys.executable, "-I", "-B", "-", CANDIDATE_SITE, case]
    try:
        pwd.getpwnam("candidate")
    except KeyError:
        pass
    else:
        command = [
            "runuser", "-u", "candidate", "--", "env",
            "HOME=/home/candidate", "PYTHONDONTWRITEBYTECODE=1", *command,
        ]
    try:
        completed = subprocess.run(
            command,
            input=ADAPTER.read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"id": case, "status": "failed", "message": type(exc).__name__}
    lines = [line for line in completed.stdout.decode("utf-8", "replace").splitlines() if line]
    try:
        response = json.loads(lines[-1]) if lines else None
    except json.JSONDecodeError:
        response = None
    passed = (
        completed.returncode == 0
        and isinstance(response, dict)
        and response.get("case") == case
        and response.get("ok") is True
        and response.get("result") == EXPECTED[case]
    )
    detail = completed.stderr.decode("utf-8", "replace")[-1200:]
    if isinstance(response, dict) and response.get("error"):
        detail = str(response["error"])[-1200:]
    return {"id": case, "status": "passed" if passed else "failed", "message": "" if passed else detail}


def main() -> int:
    leaves = [run_case(case) for case in EXPECTED]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
