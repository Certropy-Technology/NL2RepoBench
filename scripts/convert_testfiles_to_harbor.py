#!/usr/bin/env python3
"""Convert a legacy NL2RepoBench task into a catalog-backed Harbor source.

The human-facing catalog remains at ``catalog/tasks/<task-id>``.  The
hand-authored Harbor bundle is kept below that source at ``harbor/`` so it can
be reviewed and run directly while the canonical compiler is being completed.
Run outputs belong under ``.nl2repo/runs`` and are never written into a task.
"""

import argparse
import csv
import json
import re
from pathlib import Path

PYTHON_BASE = "python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a"


def detect_editable_install(test_commands: list[str]) -> bool:
    """检测是否需要 editable install"""
    return any("-e" in cmd or "editable" in cmd for cmd in test_commands)


def extract_test_paths(test_files: list[str]) -> list[str]:
    """Return the exact upstream test paths from the legacy manifest."""
    return [path for path in test_files if path and path not in {".", "./"}]


def pytest_arguments(test_commands: list[str]) -> str:
    """Extract pytest arguments while preserving the upstream test selection."""
    for command in test_commands:
        if "pytest" not in command:
            continue
        before, _, after = command.partition("pytest")
        del before
        return after.strip()
    return "tests"


def parse_expected_total(test_case_count_file: Path) -> int:
    """从 test_case_count.txt 读取预期测试数"""
    if test_case_count_file.exists():
        content = test_case_count_file.read_text().strip()
        return int(content)
    return 0


def task_difficulty(task_id: str, path: Path = Path("test_files/task_difficulty.csv")) -> str:
    """Resolve legacy difficulty without guessing from the instruction."""
    if not path.is_file():
        return "unknown"
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["task-name"].casefold() == task_id.casefold():
                return row["Level"].casefold()
    return "unknown"


def create_catalog_task_toml(
    task_id: str,
    expected_total: int,
    test_commands: list[str],
    difficulty: str = "medium",
    category: str = "python-library",
    upstream_url: str | None = None,
    upstream_revision: str | None = None,
    source_digest: str | None = None,
    python_version: str = "3.12",
) -> str:
    """Generate the human-facing declarative catalog source."""
    commands = json.dumps(test_commands or ["pytest tests"])
    if upstream_url and upstream_revision and source_digest:
        source = f'''status = "known"
upstream_url = "{upstream_url}"
revision = "{upstream_revision}"
license_spdx = "unknown"
source_digest = "{source_digest}"'''
    else:
        source = 'status = "unknown"'
    return f'''schema_version = "1.0"
task_id = "{task_id}"
version = "0.1.0"
instruction = "instruction.md"

[metadata]
difficulty = "{difficulty}"
category = "{category}"
tags = ["python", "repository-generation"]
language = "python"

[source]
{source}

[environment]
status = "known"
python_version = "{python_version}"
os_name = "debian-12"
base_image = "python:3.12-slim"
base_image_digest = "sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a"
network_mode = "public"

[dependencies]
status = "unknown"
installer = "pip"
packages = []

[tests]
framework = "pytest"
expected_total = {expected_total}
expected_total_source = "unknown"
commands = {commands}

[metric]
contract_id = "fixed-test-pass-rate-v1"
passed_statuses = ["passed"]
excluded_statuses = ["skipped"]
collection_mismatch = "fail"
formula = "clamp(passed / frozen_total, 0, 1)"

[harbor]
description = "Build the {task_id} package from an empty workspace."
keywords = ["python", "repository-generation", "nl2repobench"]
agent_timeout_sec = 3600.0
verifier_timeout_sec = 600.0
candidate_install_timeout_sec = 60.0
candidate_total_timeout_sec = 300.0
agent_network_mode = "public"
verifier_network_mode = "no-network"
cpus = 2
memory_mb = 4096
storage_mb = 8192
workspace_artifact = "/workspace"

[lifecycle]
status = "discovered"
reason = "Imported legacy task; source, dependency and collection locks still require freeze."
'''


def create_harbor_task_toml(
    task_id: str,
    expected_total: int,
    difficulty: str = "medium",
    category: str = "python-library",
) -> str:
    """Generate the standalone Harbor 1.4 task descriptor."""
    return f'''schema_version = "1.4"
artifacts = ["/workspace"]

[task]
name = "nl2repobench/{task_id}"
version = "0.1.0"
description = "Build the {task_id} package from an empty workspace."
authors = [{{ name = "NL2RepoBench" }}]
keywords = ["python", "repository-generation", "nl2repobench"]

[metadata]
difficulty = "{difficulty}"
category = "{category}"
tags = ["python"]
metric_contract = "fixed-test-pass-rate-v1"
expected_test_count = {expected_total}

[agent]
timeout_sec = 3600.0

[verifier]
timeout_sec = 600.0
environment_mode = "separate"

[environment]
network_mode = "public"
build_timeout_sec = 600.0
cpus = 2
memory_mb = 4096
storage_mb = 8192

[verifier.environment]
network_mode = "no-network"
build_timeout_sec = 600.0
cpus = 2
memory_mb = 2048
storage_mb = 4096
'''


def create_test_sh_editable(
    task_id: str,
    pytest_args: str,
    expected_total: int,
) -> str:
    """生成支持 editable install 的 test.sh"""
    scm_name = re.sub(r"[^A-Za-z0-9]", "_", task_id).upper()
    return f"""#!/usr/bin/env bash
set -uo pipefail

# VCS-backed build systems cannot see the Oracle checkout metadata after
# Harbor materializes /workspace.  A deterministic fallback keeps packaging
# functional without making tests depend on a moving tag.
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_{scm_name}=0.0.0
export SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0

mkdir -p /logs/verifier

# Step 1: Copy workspace to candidate
rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \\
    > /logs/verifier/copy-stdout.txt \\
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected {expected_total} --reason artifact-copy-failed
    exit 0
fi

# Step 2: Copy the hidden upstream source tree to candidate
echo "Copying hidden tests to candidate..."
cp -a /tests/fixture/. /tmp/candidate/ \\
    > /logs/verifier/test-copy-stdout.txt \\
    2> /logs/verifier/test-copy-stderr.txt

# Step 3: Install candidate with editable mode
cd /tmp/candidate
if ! python -m pip install --no-build-isolation -e . \\
    > /logs/verifier/install-stdout.txt \\
    2> /logs/verifier/install-stderr.txt; then
    python /tests/grade.py --expected {expected_total} --reason installation-failed
    exit 0
fi

# Step 4: Run pytest in candidate directory
chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate python -m pytest {pytest_args} \\
    --continue-on-collection-errors \\
    --junitxml=/logs/verifier/junit.xml \\
    --tb=short \\
    > /logs/verifier/pytest-stdout.txt \\
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

# Step 5: Calculate reward
python /tests/grade.py \\
    --expected {expected_total} \\
    --junit /logs/verifier/junit.xml \\
    --pytest-exit-code "$pytest_exit_code"
"""


def create_test_sh_standard(pytest_args: str, expected_total: int) -> str:
    """生成标准的 test.sh（不需要 editable install）"""
    return f"""#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \\
    > /logs/verifier/copy-stdout.txt \\
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected {expected_total} --reason artifact-copy-failed
    exit 0
fi

if ! python -m pip install --no-deps --no-build-isolation /tmp/candidate \\
    > /logs/verifier/install-stdout.txt \\
    2> /logs/verifier/install-stderr.txt; then
    python /tests/grade.py --expected {expected_total} --reason installation-failed
    exit 0
fi

chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate python -m pytest {pytest_args} \\
    --continue-on-collection-errors \\
    --junitxml=/logs/verifier/junit.xml \\
    > /logs/verifier/pytest-stdout.txt \\
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py \\
    --expected {expected_total} \\
    --junit /logs/verifier/junit.xml \\
    --pytest-exit-code "$pytest_exit_code"
"""


def create_grade_py() -> str:
    """Generate a fixed-denominator grader with explicit validity."""
    return """from __future__ import annotations

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
        root = ET.parse(args.junit).getroot()
        cases = list(root.iter("testcase"))
        counts["collected"] = len(cases)
        counts["failed"] = sum(case.find("failure") is not None for case in cases)
        counts["errors"] = sum(case.find("error") is not None for case in cases)
        counts["skipped"] = sum(case.find("skipped") is not None for case in cases)
        counts["passed"] = (
            counts["collected"]
            - counts["failed"]
            - counts["errors"]
            - counts["skipped"]
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
        json.dumps({"reward": score, "test_pass_rate": score}, indent=2) + "\\n",
        encoding="utf-8",
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
        )
        + "\\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
"""


def create_verifier_dockerfile(dependencies: list[str]) -> str:
    """生成 verifier Dockerfile"""
    deps_line = " \\\n    ".join(dependencies)
    return f"""FROM --platform=linux/amd64 {PYTHON_BASE}

RUN pip install --no-cache-dir \\
    {deps_line}

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
COPY fixture /tests/fixture

RUN useradd --uid 10001 --create-home candidate \
    && chmod +x /tests/test.sh

WORKDIR /tests
"""


def create_environment_dockerfile() -> str:
    """生成 agent environment Dockerfile"""
    return f"""FROM --platform=linux/amd64 {PYTHON_BASE}

RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
        git \\
        build-essential \\
        libxml2-dev \\
        libxslt1-dev \\
        pkg-config && \\
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
"""


def create_solution_sh(
    task_id: str,
    upstream_url: str,
    upstream_revision: str | None = None,
) -> str:
    """生成 Oracle solution"""
    fetch_revision = upstream_revision or "HEAD"
    return f"""#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream {task_id} source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/{task_id}-src >/dev/null
git -C /tmp/{task_id}-src remote add origin {upstream_url}
git -C /tmp/{task_id}-src fetch --depth 1 origin {fetch_revision} >/dev/null
git -C /tmp/{task_id}-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/{task_id}-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
"""


def convert_task(
    task_id: str,
    source_dir: Path,
    output_dir: Path,
    upstream_url: str | None = None,
    upstream_revision: str | None = None,
    source_digest: str | None = None,
    python_version: str = "3.12",
) -> None:
    """转换一个任务"""
    print(f"\n{'=' * 60}")
    print(f"Converting task: {task_id}")
    print(f"{'=' * 60}")

    # 读取源数据
    start_md = source_dir / "start.md"
    test_commands_json = source_dir / "test_commands.json"
    test_files_json = source_dir / "test_files.json"
    test_case_count_txt = source_dir / "test_case_count.txt"

    if not start_md.exists():
        print("  ❌ Missing start.md")
        return

    instruction = start_md.read_text()
    test_commands = (
        json.loads(test_commands_json.read_text()) if test_commands_json.exists() else []
    )
    test_files = json.loads(test_files_json.read_text()) if test_files_json.exists() else []
    expected_total = parse_expected_total(test_case_count_txt)

    print(f"  Expected tests: {expected_total}")
    print(f"  Test commands: {test_commands}")
    print(f"  Test files: {test_files}")

    # 检测特征
    needs_editable = detect_editable_install(test_commands)
    test_paths = extract_test_paths(test_files)
    pytest_args = pytest_arguments(test_commands)

    print(f"  Editable install: {needs_editable}")
    print(f"  Test paths: {test_paths}")

    # 创建输出目录
    difficulty = task_difficulty(task_id)
    task_output = output_dir / task_id
    task_output.mkdir(parents=True, exist_ok=True)

    # 生成文件
    print("  📝 Generating files...")

    harbor_output = task_output / "harbor"
    harbor_output.mkdir(exist_ok=True)
    (harbor_output / "environment").mkdir(exist_ok=True)
    (harbor_output / "solution").mkdir(exist_ok=True)
    (harbor_output / "tests").mkdir(exist_ok=True)
    (harbor_output / "tests" / "fixture").mkdir(exist_ok=True)

    # Human-facing catalog source and standalone Harbor descriptor.
    (task_output / "task.toml").write_text(
        create_catalog_task_toml(
            task_id,
            expected_total,
            test_commands,
            difficulty=difficulty,
            upstream_url=upstream_url,
            upstream_revision=upstream_revision,
            source_digest=source_digest,
            python_version=python_version,
        )
    )
    print("    ✓ task.toml")

    # instruction.md
    (task_output / "instruction.md").write_text(instruction)
    (harbor_output / "instruction.md").write_text(instruction)
    print("    ✓ instruction.md")

    # environment/Dockerfile
    (harbor_output / "environment" / "Dockerfile").write_text(create_environment_dockerfile())
    print("    ✓ environment/Dockerfile")

    # solution/solve.sh
    if upstream_url:
        solve_sh = create_solution_sh(task_id, upstream_url, upstream_revision)
        solve_sh_path = harbor_output / "solution" / "solve.sh"
        solve_sh_path.write_text(solve_sh)
        solve_sh_path.chmod(0o755)
        print("    ✓ solution/solve.sh")
    else:
        print("    ⚠️  No upstream URL, skipping solution/solve.sh")

    # tests/test.sh
    if needs_editable:
        test_sh = create_test_sh_editable(task_id, pytest_args, expected_total)
    else:
        test_sh = create_test_sh_standard(pytest_args, expected_total)
    test_sh_path = harbor_output / "tests" / "test.sh"
    test_sh_path.write_text(test_sh)
    test_sh_path.chmod(0o755)
    print("    ✓ tests/test.sh")

    # tests/grade.py
    (harbor_output / "tests" / "grade.py").write_text(create_grade_py())
    print("    ✓ tests/grade.py")

    # tests/Dockerfile
    base_deps = [
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "pytest-randomly",
        "pytest-benchmark",
        "pytest-codspeed",
        "typing_extensions",
        "mock",
        "freezegun",
        "hatchling",
        "hatch-vcs",
        "editables",
        "poetry-core",
        "setuptools",
        "wheel",
    ]
    (harbor_output / "tests" / "Dockerfile").write_text(create_verifier_dockerfile(base_deps))
    print("    ✓ tests/Dockerfile")

    # 复制测试文件（如果存在）
    if upstream_url:
        print("    ⚠️  Upstream tests are copied by the batch fetch step")
    else:
        print("    ⚠️  No upstream URL; add tests under harbor/tests/fixture")

    (harbor_output / "task.toml").write_text(
        create_harbor_task_toml(task_id, expected_total, difficulty=difficulty)
    )

    print(f"\n✅ Task converted: {task_output}")
    print("   Next steps:")
    print("   1. Review and adjust task.toml")
    print("   2. Add upstream URL if missing")
    print(f"   3. Test Oracle: harbor run -p {task_output} -a oracle")


def main():
    parser = argparse.ArgumentParser(
        description="Convert a legacy task into catalog source plus Harbor assets"
    )
    parser.add_argument("task_id", help="Task ID to convert")
    parser.add_argument(
        "--output",
        default="catalog/tasks",
        help="Catalog task root (default: catalog/tasks)",
    )
    parser.add_argument(
        "--upstream-url",
        help="Upstream repository URL (for Oracle)",
    )
    parser.add_argument(
        "--upstream-revision",
        help="Immutable upstream commit or tag used by the Oracle",
    )
    parser.add_argument(
        "--source-digest",
        help="SHA-256 digest of a deterministic source archive",
    )
    parser.add_argument(
        "--python-version",
        default="3.12",
        help="Python version used by the frozen legacy image",
    )
    args = parser.parse_args()

    source_dir = Path("test_files") / args.task_id
    output_dir = Path(args.output)

    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1

    convert_task(
        args.task_id,
        source_dir,
        output_dir,
        args.upstream_url,
        args.upstream_revision,
        args.source_digest,
        args.python_version,
    )
    return 0


if __name__ == "__main__":
    exit(main())
