"""Run the frozen boto3 unit suite in a candidate-owned subprocess."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


EXPECTED = 552
SUITE_SOURCE = Path(__file__).parent / "suite"
SUITE = Path("/tmp/boto3-frozen-tests")


def _prepare_suite() -> None:
    if SUITE.exists():
        shutil.rmtree(SUITE)
    shutil.copytree(SUITE_SOURCE, SUITE)
    os.chmod(SUITE, 0o555)
    for path in sorted(SUITE.rglob("*"), reverse=True):
        if path.is_dir():
            os.chmod(path, 0o555)
        else:
            os.chmod(path, 0o444)


def _invoke() -> dict[str, object]:
    candidate_site = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
    dependency_site = os.environ.get(
        "NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"
    )
    python_executable = os.environ.get("NL2REPO_PYTHON", sys.executable)
    script = r'''
import os
import sys
import pytest

sys.path[:0] = [
    os.environ["NL2REPO_CANDIDATE_SITE"],
    os.environ["NL2REPO_CANDIDATE_DEPENDENCIES"],
    "/tmp/boto3-frozen-tests",
]
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
raise SystemExit(pytest.main([
    "-q",
    "-s",
    "-p", "no:cacheprovider",
    "-p", "report_plugin",
    "--rootdir", "/tmp/boto3-frozen-tests",
    "--log-file", "/tmp/candidate-build/tmp/pytest.log",
    "tests/unit",
]))
'''
    env = os.environ.copy()
    env.update(
        {
            "HOME": "/home/candidate",
            "TMPDIR": "/tmp/candidate-build/tmp",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONNOUSERSITE": "1",
            "LC_ALL": "C.UTF-8",
            "NL2REPO_CANDIDATE_SITE": candidate_site,
            "NL2REPO_CANDIDATE_DEPENDENCIES": dependency_site,
            "PYTEST_ADDOPTS": "",
            "PYTEST_PLUGINS": "",
            "NL2REPO_PYTHON": python_executable,
        }
    )
    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        *[f"{key}={value}" for key, value in env.items() if key in {
            "HOME", "TMPDIR", "PYTHONDONTWRITEBYTECODE", "PYTHONHASHSEED",
            "PYTHONNOUSERSITE", "LC_ALL", "NL2REPO_CANDIDATE_SITE",
            "PYTEST_ADDOPTS", "PYTEST_PLUGINS", "NL2REPO_CANDIDATE_DEPENDENCIES",
            "NL2REPO_PYTHON",
        }],
        python_executable,
        "-I",
        "-B",
        "-",
    ]
    try:
        completed = subprocess.run(
            command,
            input=script,
            cwd=SUITE,
            capture_output=True,
            text=True,
            timeout=360.0,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"error": f"candidate subprocess error: {exc}"}
    reports = [
        line.split("NL2REPO_REPORT=", 1)[1]
        for line in completed.stdout.splitlines()
        if "NL2REPO_REPORT=" in line
    ]
    if completed.returncode not in (0, 1) or len(reports) != 1:
        return {
            "error": (
                "candidate pytest did not emit one report; "
                f"returncode={completed.returncode}; "
                f"stdout={completed.stdout[-1000:]!r}; "
                f"stderr={completed.stderr[-1000:]!r}"
            ),
            "returncode": completed.returncode,
            "stdout": completed.stdout[-2000:],
            "stderr": completed.stderr[-2000:],
        }
    try:
        report = json.loads(reports[0])
        leaves = report["leaves"]
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        return {"error": f"invalid candidate report: {exc}"}
    if (
        report.get("schema_version") != "boto3-pytest-v1"
        or not isinstance(leaves, list)
        or len(leaves) != EXPECTED
        or len({leaf.get("id") for leaf in leaves}) != EXPECTED
        or any(leaf.get("status") not in {"passed", "failed", "skipped"} for leaf in leaves)
    ):
        return {"error": "candidate report failed frozen collection validation", "report": report}
    return {"leaves": leaves}


def main() -> None:
    _prepare_suite()
    result = _invoke()
    if "leaves" in result:
        print(
            json.dumps(
                {"schema_version": "1.0", "leaves": result["leaves"]},
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
    else:
        leaves = [
            {"id": f"boto3/verifier-{index:03d}", "status": "failed", "message": result["error"]}
            for index in range(EXPECTED)
        ]
        print(json.dumps({"schema_version": "1.0", "leaves": leaves}, separators=(",", ":")))


if __name__ == "__main__":
    main()
