#!/usr/bin/env python3
"""Generate Harbor verifier assets from frozen legacy verifier images.

The legacy images contain the exact test dependencies and hidden tests used by
the original four-file runner. Harbor supplies the candidate at /workspace.
The verifier copies only frozen test paths into a private candidate copy and
prepends candidate source paths through an executable .pth file. No candidate
build backend or network access is required.
"""

from __future__ import annotations

import stat
from pathlib import Path

REPO = Path(__file__).parent.parent
REGISTRY = "ghcr.io/multimodal-art-projection/nl2repobench"
IMAGE_DIGESTS = {
    "aiofiles": "c2c5990b82801b434d40d0be1fb21ae8b914a2336ff2486ebc7ea622924e4e7a",
    "arguably": "93563ba710a490978afdb11275583ac8357492bd41821a28d8b5fb9eccb84751",
    "boltons": "770deb94e716b3a1592900ab389ac628f7b2a41d360e55bdb633bbff4c948e52",
    "cerberus": "b097a72dfc814cc9cd26a418a4a413e2ea6bafafbef6e567413976ed70fba946",
    "decouple": "cb97d0b98c23641262708449c4de30d6294c90b139f7b01379c7e5b38ee553a6",
    "ftfy": "7b81cb54efc741a160aac403bdb672d6a724f0726cd9376d321d26efd4367afb",
    "humanize": "18407d80e95c1a277a5e6fb66c1174b7f2b3699ec10125adc7d6e180f2f6a626",
    "parse": "b62739aff75c836823bf0140ae6db4d329beb74cf79cdb170ed5adb85966ee18",
    "pytz": "c331cc311b7112b55f66e0eaa505f6a6e63fc97a40e963c5a4b21900341477fc",
    "six": "403962b64fa09689196c6d29a82bf7a9525a95dbb4459f12cca4a920a056dc91",
    "jsonlines": "53d4f953222214651e979d00d81b8b10af86adec9a24982be0ce95e5ece2c246",
    "freezegun": "c3525ea5c356aea4bd8e2ebef5f44db9fe9e1fbe40173ae270057d8c7641e3d5",
    "tinydb": "3db19fe6b19b93ed836def4c78e351fc95454018a3978057ffdf99e3bb2ff1cc",
    "tenacity": "d8de6dbe1756b785974c57baf2a033767a6fd0324ff2fd70c861940e6372cd2e",
}

TASKS: dict[str, dict[str, object]] = {
    "aiofiles": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 211,
    },
    "arguably": {
        "paths": ["test"],
        "pytest": "--continue-on-collection-errors test",
        "expected": 70,
    },
    "boltons": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 423,
    },
    "cerberus": {
        "paths": [
            "cerberus/tests",
            "cerberus/benchmarks/test_overall_performance_1.py",
            "cerberus/benchmarks/test_overall_performance_2.py",
        ],
        "pytest": (
            "--continue-on-collection-errors cerberus/tests "
            "cerberus/benchmarks/test_overall_performance_1.py "
            "cerberus/benchmarks/test_overall_performance_2.py"
        ),
        # One upstream test is intentionally skipped on this frozen image;
        # the metric denominator excludes skipped cases.
        "expected": 248,
    },
    "decouple": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 67,
    },
    "ftfy": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 336,
        "prepare": [
            "printf '#!/bin/sh\\nexec python -m ftfy.cli \\\"$@\\\"\\n' > /usr/local/bin/ftfy",
            "chmod 755 /usr/local/bin/ftfy",
        ],
    },
    "humanize": {
        "paths": [
            "tests/test_filesize.py",
            "tests/test_i18n.py",
            "tests/test_lists.py",
            "tests/test_number.py",
            "tests/test_time.py",
        ],
        "pytest": (
            "--continue-on-collection-errors tests/test_filesize.py "
            "tests/test_i18n.py tests/test_lists.py tests/test_number.py "
            "tests/test_time.py"
        ),
        "expected": 607,
        "prepare": [
            "mkdir -p /tmp/candidate/src/humanize",
            "test -f /tmp/candidate/src/humanize/_version.py || "
            "echo '__version__ = \"0.0.0\"' > "
            "/tmp/candidate/src/humanize/_version.py",
        ],
    },
    "parse": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 96,
    },
    "pytz": {
        "paths": ["test_docs.py", "test_lazy.py", "test_tzinfo.py"],
        "pytest": ("--continue-on-collection-errors test_docs.py test_lazy.py test_tzinfo.py"),
        "expected": 235,
        "blocked": (
            "The frozen image stores pytz as an egg and the source build requires "
            "generated zoneinfo data; needs a dedicated offline source-freeze stage."
        ),
    },
    "six": {
        "paths": ["test_six.py"],
        "pytest": "--continue-on-collection-errors test_six.py",
        "expected": 200,
    },
    "jsonlines": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 27,
    },
    "freezegun": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 133,
    },
    "tinydb": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 204,
    },
    "tenacity": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 124,
    },
}

GRADE_PY = r"""from __future__ import annotations
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--reason")
    args = parser.parse_args()

    counts = {"collected": 0, "failed": 0, "errors": 0, "skipped": 0, "passed": 0}
    reason = args.reason
    valid = reason is None
    if args.junit is not None and args.junit.is_file():
        cases = list(ET.parse(args.junit).getroot().iter("testcase"))
        counts["collected"] = len(cases)
        counts["failed"] = sum(c.find("failure") is not None for c in cases)
        counts["errors"] = sum(c.find("error") is not None for c in cases)
        counts["skipped"] = sum(c.find("skipped") is not None for c in cases)
        counts["passed"] = (
            counts["collected"] - counts["failed"] - counts["errors"] - counts["skipped"]
        )
    elif reason is None:
        reason = "junit-missing"
        valid = False

    effective_total = counts["collected"] - counts["skipped"]
    if reason is None and effective_total != args.expected:
        reason = "collection-mismatch"
        valid = False
    if reason is None and args.pytest_exit_code not in {0, 1}:
        reason = "pytest-abnormal-exit"
        valid = False
    score = counts["passed"] / args.expected if valid and args.expected > 0 else 0.0
    score = max(0.0, min(score, 1.0))

    verifier_dir = Path("/logs/verifier")
    verifier_dir.mkdir(parents=True, exist_ok=True)
    (verifier_dir / "reward.json").write_text(
        json.dumps({"reward": score, "test_pass_rate": score}, indent=2) + "\n"
    )
    (verifier_dir / "grading.json").write_text(
        json.dumps(
            {
                **counts,
                "effective_total": effective_total,
                "expected": args.expected,
                "pytest_exit_code": args.pytest_exit_code,
                "reason": reason,
                "reward": score,
                "valid": valid,
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
    )


if __name__ == "__main__":
    main()
"""


def dockerfile(task: str, config: dict[str, object]) -> str:
    save_paths = "\n".join(
        f"RUN mkdir -p /tests/fixture/$(dirname {path}) "
        f"&& cp -a /workspace/{path} /tests/fixture/{path}"
        for path in config["paths"]
    )
    prepare = "\n".join(f"RUN {command}" for command in config.get("docker_prepare", []))
    return f"""FROM {REGISTRY}/{task}@sha256:{IMAGE_DIGESTS[task]}

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
{save_paths}
{prepare}

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
"""


def test_script(config: dict[str, object]) -> str:
    expected = config["expected"]
    overlays = "\n".join(
        f"rm -rf /tmp/candidate/{path}\n"
        f"mkdir -p /tmp/candidate/$(dirname {path})\n"
        f"cp -a /tests/fixture/{path} /tmp/candidate/{path}"
        for path in config["paths"]
    )
    prepare = "\n".join(config.get("prepare", []))
    return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt 2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected {expected} --reason artifact-copy-failed
    exit 0
fi

# Replace candidate-created tests with the frozen test paths.
{overlays}

# Executable .pth lines run at interpreter start and put candidate code first.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']\n" \
    > "$SITEPKG/_candidate_override.pth"
{prepare}

chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate \
    sh -c "cd /tmp/candidate && python -m pytest {config["pytest"]} \
           --junitxml=/logs/verifier/junit.xml --tb=short" \
    > /logs/verifier/pytest-stdout.txt 2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py --expected {expected} \
    --junit /logs/verifier/junit.xml --pytest-exit-code "$pytest_exit_code"
"""


def write_task(task: str, config: dict[str, object]) -> None:
    if config.get("blocked"):
        print(f"  ! {task} blocked: {config['blocked']}")
        return
    tests = REPO / "catalog" / "tasks" / task / "harbor" / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    (tests / "Dockerfile").write_text(dockerfile(task, config), encoding="utf-8")
    (tests / "grade.py").write_text(GRADE_PY, encoding="utf-8")
    script = tests / "test.sh"
    script.write_text(test_script(config), encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> None:
    for task, config in TASKS.items():
        write_task(task, config)
        print(f"generated {task}")


if __name__ == "__main__":
    main()
