"""Mechanical checks for the unified verifier contract.

This check is intentionally local and deterministic. It reports generated
legacy projections separately from current source truth instead of silently
rewriting them during validation.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tomllib
from pathlib import Path

CURRENT_CONTRACT = "fixed-test-pass-rate-v1"


def _source_contracts(root: Path) -> tuple[set[str], list[str]]:
    contracts: set[str] = set()
    errors: list[str] = []
    for path in sorted((root / "catalog/sources").glob("*/task.toml")):
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{path}: parse error: {exc}")
            continue
        metric = data.get("metric", {})
        if isinstance(metric, dict) and isinstance(metric.get("contract_id"), str):
            contracts.add(metric["contract_id"])
        else:
            errors.append(f"{path}: metric.contract_id is missing")
    return contracts, errors


def _generated_contracts(root: Path) -> set[str]:
    contracts: set[str] = set()
    for path in sorted((root / "catalog/tasks").glob("*/task.toml")):
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
            continue
        metadata = data.get("metadata", {})
        if isinstance(metadata, dict) and isinstance(metadata.get("metric_contract"), str):
            contracts.add(metadata["metric_contract"])
    return contracts


def _has_language_branch(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "node_mode":
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    source_contracts, source_errors = _source_contracts(root)
    errors.extend(source_errors)
    generated_contracts = _generated_contracts(root)
    required = {
        root / "src/nl2repobench/verification/leaf_report.py",
        root / "src/nl2repobench/verification/evaluator.py",
        root / "src/nl2repobench/verification/metric_contract.py",
        root / "src/nl2repobench/verification/taxonomy.py",
        root / "src/nl2repobench/verification/registry.py",
        root / "src/nl2repobench/harbor/task_writer.py",
        root / "reports/p2-unified-verifier-state.md",
    }
    missing = sorted(str(path.relative_to(root)) for path in required if not path.is_file())
    errors.extend(f"missing required artifact: {path}" for path in missing)
    if source_contracts != {CURRENT_CONTRACT}:
        errors.append(
            f"source contract IDs are {sorted(source_contracts)}, "
            f"expected [{CURRENT_CONTRACT}]"
        )
    if generated_contracts != {CURRENT_CONTRACT}:
        errors.append(
            f"generated contract IDs are {sorted(generated_contracts)}, "
            f"expected [{CURRENT_CONTRACT}]"
        )
    cli = root / "src/nl2repobench/verification/cli.py"
    if _has_language_branch(cli):
        errors.append("verification CLI still contains implicit node_mode dispatch")
    if "--runtime" not in cli.read_text(encoding="utf-8"):
        errors.append("verification CLI has no explicit --runtime argument")
    node_grader = root / "src/nl2repobench/verification/node/grade-report.mjs"
    node_text = node_grader.read_text(encoding="utf-8") if node_grader.is_file() else ""
    if "nl2repobench.verification.cli" not in node_text:
        errors.append("Node runtime grader does not delegate to the canonical evaluator")
    if "counts.passed /" in node_text or "counts.passed / expected" in node_text:
        errors.append("Node runtime grader contains an independent reward formula")
    go_compiler = root / "src/nl2repobench/harbor/go_compiler.py"
    go_text = go_compiler.read_text(encoding="utf-8") if go_compiler.is_file() else ""
    if "go_contract_runner" not in go_text or "go_bridge_proxy" not in go_text:
        errors.append("Go Harbor compiler does not use the bounded bridge supervisor path")
    payload = {
        "contract_id": CURRENT_CONTRACT,
        "source_contracts": sorted(source_contracts),
        "generated_contracts": sorted(generated_contracts),
        "generated_legacy_projection": sorted(
            generated_contracts - {CURRENT_CONTRACT}
        ),
        "required_artifacts": len(required) - len(missing),
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
