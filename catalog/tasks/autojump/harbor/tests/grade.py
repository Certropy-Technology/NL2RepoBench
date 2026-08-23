from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def _xfail_suffixes() -> set[str]:
    suffixes: set[str] = set()
    fixture_root = Path("/tests/fixture/tests")
    for path in sorted(fixture_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        module = path.stem
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    decorators = child.decorator_list
                    if any(_is_xfail_decorator(decorator) for decorator in decorators):
                        suffixes.add(f"{module}.{node.name}::{child.name}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(_is_xfail_decorator(decorator) for decorator in node.decorator_list):
                    suffixes.add(f"{module}::{node.name}")
    return suffixes


def _is_xfail_decorator(decorator: ast.expr) -> bool:
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    return (
        isinstance(decorator, ast.Attribute)
        and decorator.attr == "xfail"
    ) or (isinstance(decorator, ast.Name) and decorator.id == "xfail")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--expected-collected", type=int, default=32)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--reason")
    args = parser.parse_args()

    counts = {"collected": 0, "failed": 0, "errors": 0, "skipped": 0, "excluded": 0, "passed": 0}
    reason = args.reason
    valid = reason is None and args.expected == 23
    if reason is None and args.expected != 23:
        reason = "verifier-internal-error"

    xfail_suffixes = _xfail_suffixes()
    if len(xfail_suffixes) != 5 and reason is None:
        reason = "verifier-internal-error"
        valid = False

    if args.junit is not None and args.junit.is_file() and not args.junit.is_symlink():
        try:
            cases = list(ET.parse(args.junit).getroot().iter("testcase"))
        except (ET.ParseError, OSError):
            reason = reason or "junit-malformed"
            valid = False
        else:
            counts["collected"] = len(cases)
            scored_cases = []
            for case in cases:
                node_suffix = f"{case.get('classname', '')}::{case.get('name', '')}"
                if any(node_suffix.endswith(suffix) for suffix in xfail_suffixes):
                    counts["excluded"] += 1
                else:
                    scored_cases.append(case)
            counts["failed"] = sum(case.find("failure") is not None for case in scored_cases)
            counts["errors"] = sum(case.find("error") is not None for case in scored_cases)
            counts["skipped"] = sum(case.find("skipped") is not None for case in scored_cases)
            counts["passed"] = (
                len(scored_cases)
                - counts["failed"]
                - counts["errors"]
                - counts["skipped"]
            )
    elif reason is None:
        reason = "junit-missing"
        valid = False

    effective_total = counts["collected"] - counts["skipped"] - counts["excluded"]
    if reason is None and counts["collected"] != args.expected_collected:
        reason = "collection-mismatch"
        valid = False
    if reason is None and effective_total != args.expected:
        reason = "collection-mismatch"
        valid = False
    if reason is None and args.pytest_exit_code not in {0, 1}:
        reason = "pytest-abnormal-exit"
        valid = False

    reward = counts["passed"] / args.expected if valid and args.expected > 0 else 0.0
    reward = max(0.0, min(reward, 1.0))
    verifier_dir = Path("/logs/verifier")
    verifier_dir.mkdir(parents=True, exist_ok=True)
    (verifier_dir / "reward.json").write_text(
        json.dumps({"reward": reward, "test_pass_rate": reward}, indent=2) + "\n",
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
                "reward": reward,
                "valid": valid,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
