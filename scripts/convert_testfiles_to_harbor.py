#!/usr/bin/env python3
"""
Convert NL2RepoBench test_files/ tasks to Harbor 1.4 tasks.

Usage:
    python scripts/convert_testfiles_to_harbor.py <task-id> [--output examples/harbor]
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def detect_editable_install(test_commands: List[str]) -> bool:
    """检测是否需要 editable install"""
    return any('-e' in cmd or 'editable' in cmd for cmd in test_commands)


def extract_test_directory(test_files: List[str]) -> Optional[str]:
    """提取测试目录名"""
    if not test_files:
        return None
    return test_files[0] if len(test_files) == 1 else 'tests'


def parse_expected_total(test_case_count_file: Path) -> int:
    """从 test_case_count.txt 读取预期测试数"""
    if test_case_count_file.exists():
        content = test_case_count_file.read_text().strip()
        return int(content)
    return 0


def create_task_toml(
    task_id: str,
    expected_total: int,
    difficulty: str = "medium",
    category: str = "python-library",
) -> str:
    """生成 task.toml"""
    return f'''schema_version = "1.4"
artifacts = ["/workspace"]

[task]
name = "nl2repobench/{task_id}"
version = "1.0.0"
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
timeout_sec = 1800.0

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
network_mode = "public"
build_timeout_sec = 600.0
cpus = 2
memory_mb = 2048
storage_mb = 4096
'''


def create_test_sh_editable(task_id: str, test_dir: str, expected_total: int) -> str:
    """生成支持 editable install 的 test.sh"""
    return f'''#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

# Step 1: Copy workspace to candidate
rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \\
    > /logs/verifier/copy-stdout.txt \\
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected {expected_total} --reason artifact-copy-failed
    exit 0
fi

# Step 2: Copy hidden tests to candidate
echo "Copying hidden tests to candidate..."
cp -r /tests/{test_dir} /tmp/candidate/ \\
    > /logs/verifier/test-copy-stdout.txt \\
    2> /logs/verifier/test-copy-stderr.txt

# Step 3: Install candidate with editable mode
cd /tmp/candidate
if ! python -m pip install -e . \\
    > /logs/verifier/install-stdout.txt \\
    2> /logs/verifier/install-stderr.txt; then
    python /tests/grade.py --expected {expected_total} --reason installation-failed
    exit 0
fi

# Step 4: Run pytest in candidate directory
python -m pytest {test_dir} \\
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
'''


def create_test_sh_standard(task_id: str, expected_total: int) -> str:
    """生成标准的 test.sh（不需要 editable install）"""
    return f'''#!/usr/bin/env bash
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

python -m pytest \\
    --continue-on-collection-errors \\
    --junitxml=/logs/verifier/junit.xml \\
    /tests/test_{task_id}.py \\
    > /logs/verifier/pytest-stdout.txt \\
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py \\
    --expected {expected_total} \\
    --junit /logs/verifier/junit.xml \\
    --pytest-exit-code "$pytest_exit_code"
'''


def create_grade_py() -> str:
    """生成 grade.py"""
    return '''from __future__ import annotations

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

    passed = min(counts["passed"], args.expected)
    score = passed / args.expected if args.expected > 0 else 0.0

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
                "expected": args.expected,
                "pytest_exit_code": args.pytest_exit_code,
                "reason": reason,
                "reward": score,
            },
            indent=2,
            sort_keys=True,
        )
        + "\\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
'''


def create_verifier_dockerfile(dependencies: List[str]) -> str:
    """生成 verifier Dockerfile"""
    deps_line = " \\\n    ".join(dependencies)
    return f'''FROM python:3.12-slim

RUN pip install --no-cache-dir \\
    {deps_line}

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
COPY test /tests/test

RUN chmod +x /tests/test.sh

WORKDIR /tests
'''


def create_environment_dockerfile() -> str:
    """生成 agent environment Dockerfile"""
    return '''FROM python:3.12-slim

RUN apt-get update && \\
    apt-get install -y --no-install-recommends git && \\
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
'''


def create_solution_sh(task_id: str, upstream_url: str) -> str:
    """生成 Oracle solution"""
    return f'''#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream {task_id} source code ==="

# Clone upstream repository
git clone --depth 1 {upstream_url} /tmp/{task_id}-src

# Copy entire source tree to workspace
cd /tmp/{task_id}-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Remove git directory and unnecessary files
rm -rf /workspace/.git
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
'''


def convert_task(
    task_id: str,
    source_dir: Path,
    output_dir: Path,
    upstream_url: Optional[str] = None,
) -> None:
    """转换一个任务"""
    print(f"\n{'='*60}")
    print(f"Converting task: {task_id}")
    print(f"{'='*60}")

    # 读取源数据
    start_md = source_dir / "start.md"
    test_commands_json = source_dir / "test_commands.json"
    test_files_json = source_dir / "test_files.json"
    test_case_count_txt = source_dir / "test_case_count.txt"

    if not start_md.exists():
        print(f"  ❌ Missing start.md")
        return

    instruction = start_md.read_text()
    test_commands = json.loads(test_commands_json.read_text()) if test_commands_json.exists() else []
    test_files = json.loads(test_files_json.read_text()) if test_files_json.exists() else []
    expected_total = parse_expected_total(test_case_count_txt)

    print(f"  Expected tests: {expected_total}")
    print(f"  Test commands: {test_commands}")
    print(f"  Test files: {test_files}")

    # 检测特征
    needs_editable = detect_editable_install(test_commands)
    test_dir = extract_test_directory(test_files)

    print(f"  Editable install: {needs_editable}")
    print(f"  Test directory: {test_dir}")

    # 创建输出目录
    task_output = output_dir / task_id
    task_output.mkdir(parents=True, exist_ok=True)
    (task_output / "environment").mkdir(exist_ok=True)
    (task_output / "solution").mkdir(exist_ok=True)
    (task_output / "tests").mkdir(exist_ok=True)

    # 生成文件
    print(f"  📝 Generating files...")

    # task.toml
    (task_output / "task.toml").write_text(
        create_task_toml(task_id, expected_total)
    )
    print(f"    ✓ task.toml")

    # instruction.md
    (task_output / "instruction.md").write_text(instruction)
    print(f"    ✓ instruction.md")

    # environment/Dockerfile
    (task_output / "environment" / "Dockerfile").write_text(
        create_environment_dockerfile()
    )
    print(f"    ✓ environment/Dockerfile")

    # solution/solve.sh
    if upstream_url:
        solve_sh = create_solution_sh(task_id, upstream_url)
        solve_sh_path = task_output / "solution" / "solve.sh"
        solve_sh_path.write_text(solve_sh)
        solve_sh_path.chmod(0o755)
        print(f"    ✓ solution/solve.sh")
    else:
        print(f"    ⚠️  No upstream URL, skipping solution/solve.sh")

    # tests/test.sh
    if needs_editable and test_dir:
        test_sh = create_test_sh_editable(task_id, test_dir, expected_total)
    else:
        test_sh = create_test_sh_standard(task_id, expected_total)
    test_sh_path = task_output / "tests" / "test.sh"
    test_sh_path.write_text(test_sh)
    test_sh_path.chmod(0o755)
    print(f"    ✓ tests/test.sh")

    # tests/grade.py
    (task_output / "tests" / "grade.py").write_text(create_grade_py())
    print(f"    ✓ tests/grade.py")

    # tests/Dockerfile
    base_deps = ["pytest", "pytest-cov", "typing_extensions"]
    (task_output / "tests" / "Dockerfile").write_text(
        create_verifier_dockerfile(base_deps)
    )
    print(f"    ✓ tests/Dockerfile")

    # 复制测试文件（如果存在）
    if test_dir and (source_dir / test_dir).exists():
        shutil.copytree(
            source_dir / test_dir,
            task_output / "tests" / test_dir,
            dirs_exist_ok=True
        )
        print(f"    ✓ tests/{test_dir}/ (copied)")
    else:
        print(f"    ⚠️  Test directory not found, you need to manually add tests")

    print(f"\n✅ Task converted: {task_output}")
    print(f"   Next steps:")
    print(f"   1. Review and adjust task.toml")
    print(f"   2. Add upstream URL if missing")
    print(f"   3. Test Oracle: harbor run -p {task_output} -a oracle")


def main():
    parser = argparse.ArgumentParser(
        description="Convert NL2RepoBench test_files/ to Harbor 1.4 tasks"
    )
    parser.add_argument("task_id", help="Task ID to convert")
    parser.add_argument(
        "--output",
        default="examples/harbor",
        help="Output directory (default: examples/harbor)",
    )
    parser.add_argument(
        "--upstream-url",
        help="Upstream repository URL (for Oracle)",
    )
    args = parser.parse_args()

    source_dir = Path("test_files") / args.task_id
    output_dir = Path(args.output)

    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1

    convert_task(args.task_id, source_dir, output_dir, args.upstream_url)
    return 0


if __name__ == "__main__":
    exit(main())
