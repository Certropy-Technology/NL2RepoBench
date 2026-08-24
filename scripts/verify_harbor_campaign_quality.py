#!/usr/bin/env python3
"""Run the repository-wide deterministic quality checks for Harbor production."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any


def _run(command: list[str], *, cwd: Path, timeout: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": None,
            "timeout_sec": timeout,
            "output_tail": str(exc.stdout or "")[-4000:],
            "passed": False,
        }
    return {
        "command": command,
        "exit_code": completed.returncode,
        "timeout_sec": timeout,
        "output_tail": completed.stdout[-4000:],
        "passed": completed.returncode == 0,
    }


def _parse_tree(root: Path, suffix: str, parser) -> tuple[int, list[str]]:
    count = 0
    failures: list[str] = []
    for path in sorted(root.rglob(f"*{suffix}")):
        if any(part in {".git", ".nl2repo", "node_modules", "__pycache__"} for part in path.parts):
            continue
        try:
            parser(path)
        except (OSError, UnicodeDecodeError, ValueError, tomllib.TOMLDecodeError) as exc:
            failures.append(f"{path}: {exc}")
        count += 1
    return count, failures


def _schema_snapshot(root: Path) -> dict[str, Any]:
    results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="nl2repo-schema-quality-") as temp:
        temp_root = Path(temp)
        for version in ("1.0", "2.0"):
            output = temp_root / f"v{version.replace('.', '')}"
            result = _run(
                [
                    "uv",
                    "run",
                    "nl2repo",
                    "schema",
                    "export",
                    "--version",
                    version,
                    "--output",
                    str(output),
                ],
                cwd=root,
                timeout=120,
            )
            if not result["passed"]:
                results[version] = result
                continue
            expected_root = root / "schemas" / f"v{version.split('.')[0]}"
            mismatches: list[str] = []
            for generated in sorted(output.glob("*.json")):
                expected = expected_root / generated.name
                if not expected.is_file() or generated.read_bytes() != expected.read_bytes():
                    mismatches.append(generated.name)
            results[version] = {
                "command": result["command"],
                "exit_code": result["exit_code"],
                "passed": not mismatches,
                "mismatches": mismatches,
            }
    return {"passed": all(result.get("passed") is True for result in results.values()), **results}


def _gitignore_check(root: Path) -> dict[str, Any]:
    ignored: list[str] = []
    tracked = subprocess.check_output(
        ["git", "ls-files", "catalog/tasks"], cwd=root, text=True
    ).splitlines()
    for relative in tracked:
        path = root / relative
        if not path.is_file() or path.name == ".gitignore":
            continue
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-q", relative],
            cwd=root,
            check=False,
        )
        if result.returncode == 0:
            ignored.append(path.relative_to(root).as_posix())
    return {"passed": not ignored, "ignored_task_files": ignored}


def verify(root: Path, gate_report: Path) -> dict[str, Any]:
    try:
        gate = json.loads(gate_report.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid gate report: {exc}") from exc
    if not isinstance(gate, dict) or gate.get("ok") is not True:
        raise ValueError("production gate report is not successful")

    checks: dict[str, Any] = {}
    checks["ruff"] = _run(
        ["uv", "run", "ruff", "check", "src", "scripts", "tests"], cwd=root, timeout=300
    )
    checks["mypy"] = _run(["uv", "run", "mypy"], cwd=root, timeout=300)
    checks["pytest"] = _run(
        ["uv", "run", "pytest", "-q", "-p", "no:cacheprovider"], cwd=root, timeout=1800
    )
    checks["vendor_audit"] = _run(
        [
            "uv",
            "run",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--no-cov",
            "tests/test_no_vendor_install.py",
        ],
        cwd=root,
        timeout=300,
    )
    checks["network_lint"] = _run(
        ["uv", "run", "nl2repo", "task", "lint-network", "--include-generated"],
        cwd=root,
        timeout=300,
    )
    checks["git_diff_check"] = _run(["git", "diff", "--check"], cwd=root, timeout=120)
    checks["schema_snapshot"] = _schema_snapshot(root)
    toml_count, toml_failures = _parse_tree(
        root / "catalog", ".toml", lambda p: tomllib.loads(p.read_text())
    )
    json_count, json_failures = _parse_tree(
        root / "catalog", ".json", lambda p: json.loads(p.read_text())
    )
    checks["toml_json_parse"] = {
        "passed": not toml_failures and not json_failures,
        "toml_files": toml_count,
        "json_files": json_count,
        "failures": toml_failures + json_failures,
    }
    checks["task_tree_gitignore"] = _gitignore_check(root)
    failed = [name for name, result in checks.items() if result.get("passed") is not True]
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "report_kind": "harbor-campaign-quality",
        "gate_report": str(gate_report.relative_to(root)),
        "checks": checks,
        "failed_checks": failed,
        "ok": not failed,
    }
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    report["content_sha256"] = "sha256:" + hashlib.sha256(payload.encode()).hexdigest()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    try:
        report = verify(root, args.report.resolve())
    except (OSError, ValueError) as exc:
        print(f"Harbor campaign quality gate failed: {exc}", file=sys.stderr)
        return 1
    if args.output:
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
