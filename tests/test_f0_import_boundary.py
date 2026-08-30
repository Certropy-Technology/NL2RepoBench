from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parents[1]
ACTIVE = (
    "authoring/catalog.py",
    "cli.py",
    "domain/canonical_contract.py",
    "harbor/compiler.py",
    "harbor/go_compiler.py",
    "harbor/node_compiler.py",
    "harbor/pnpm_compiler.py",
    "harbor/registry.py",
    "verification/evaluator.py",
    "verification/grader.py",
    "verification/go_grader.py",
    "verification/node_grader.py",
)


def test_active_runtime_imports_only_canonical_domain_records() -> None:
    source_root = ROOT / "src/nl2repobench"
    forbidden: list[str] = []
    for relative in ACTIVE:
        path = source_root / relative
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if (
                    module.startswith("nl2repobench.legacy")
                    or module == "nl2repobench.domain.models"
                    or (
                        module == "nl2repobench.domain.runtime"
                        and any(
                            alias.name in {"RuntimeLanguage", "PackageManager", "RuntimeProfile"}
                            for alias in node.names
                        )
                    )
                    or module
                    in {"nl2repobench.verification.models", "nl2repobench.verification.node_models"}
                ):
                    forbidden.append(f"{relative}:{node.lineno}:{module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if (
                        alias.name.startswith("nl2repobench.legacy")
                        or alias.name == "nl2repobench.domain.models"
                        or alias.name
                        in {
                            "nl2repobench.verification.models",
                            "nl2repobench.verification.node_models",
                        }
                    ):
                        forbidden.append(f"{relative}:{node.lineno}:{alias.name}")
    assert forbidden == []
    assert not (source_root / "domain/models.py").exists()
    assert not any(
        node.name in {"RuntimeLanguage", "PackageManager", "RuntimeProfile"}
        for node in ast.walk(ast.parse((source_root / "domain/runtime.py").read_text()))
        if isinstance(node, ast.ClassDef)
    )


def test_active_metric_has_no_excluded_status_field() -> None:
    from nl2repobench.domain.canonical_models import MetricContract

    contract = MetricContract()
    assert "excluded_statuses" not in MetricContract.model_fields
    assert contract.contract_id == "fixed-test-pass-rate-v1"


def test_no_active_source_imports_legacy_verifier_models_or_runtime_family() -> None:
    source_root = ROOT / "src/nl2repobench"
    violations: list[str] = []
    for path in source_root.rglob("*.py"):
        if "legacy" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in {
                "RuntimeLanguage",
                "PackageManager",
                "RuntimeProfile",
                "GradingResult",
                "NodeGradingResult",
            }:
                if path.name != "canonical_contract.py":
                    violations.append(f"{path.relative_to(source_root)}:{node.lineno}:{node.name}")
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in {
                    "nl2repobench.domain.runtime",
                    "nl2repobench.verification.models",
                    "nl2repobench.verification.node_models",
                } and any(
                    alias.name
                    in {
                        "RuntimeLanguage",
                        "PackageManager",
                        "RuntimeProfile",
                        "GradingResult",
                        "NodeGradingResult",
                    }
                    for alias in node.names
                ):
                    violations.append(f"{path.relative_to(source_root)}:{node.lineno}:{module}")
    assert violations == []
