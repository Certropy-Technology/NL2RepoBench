from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
import tomli_w

from nl2repobench.harbor.registry import HarborCompilerRegistry
from nl2repobench.harbor.rust_compiler import RustHarborCompileError, RustHarborCompiler
from nl2repobench.verification.rust_grader import grade_rust_report

ROOT = Path(__file__).parents[1]


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "rust-synthetic"
    source.mkdir()
    (source / "instruction.md").write_text("Build the Rust package.\n", encoding="utf-8")
    (source / "harbor/tests").mkdir(parents=True)
    (source / "harbor/tests/contract.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (source / "harbor/solution").mkdir()
    (source / "harbor/solution/solve.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (source / "harbor/controls").mkdir()
    (source / "harbor/controls/stub.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    payload = {
        "schema_version": "1.0",
        "task_id": "rust-synthetic",
        "version": "0.1.0",
        "instruction": "instruction.md",
        "metadata": {
            "difficulty": "easy",
            "category": "rust-synthetic",
            "tags": ["rust", "cargo", "synthetic"],
            "language": "rust",
        },
        "source": {"status": "unknown"},
        "environment": {
            "status": "unknown",
            "runtime": {
                "language": "rust",
                "runtime": "rust",
                "version": "1.100.0-nightly",
                "package_manager": "cargo",
                "package_manager_version": "1.100.0-nightly",
            },
        },
        "dependencies": {"status": "unknown", "package_manager": "cargo"},
        "tests": {
            "framework": "rust-harness",
            "report_format": "rust-bridge-json-v1",
            "expected_total": 1,
        },
        "harbor": {
            "description": "Rust R0 synthetic bundle.",
            "keywords": ["rust", "cargo", "synthetic"],
            "agent_network_mode": "no-network",
            "verifier_network_mode": "no-network",
        },
        "lifecycle": {"status": "discovered"},
    }
    (source / "task.toml").write_text(tomli_w.dumps(payload), encoding="utf-8")
    return source


def test_rust_compiler_renders_development_bundle_without_private_inputs(tmp_path: Path) -> None:
    source = _source(tmp_path)
    output = tmp_path / "output"
    compiler = RustHarborCompiler(ROOT / "toolchain.rust.dev.lock.toml")
    result = compiler.compile_task(source, output, allow_incomplete=True)

    assert (result / "instruction.md").is_file()
    assert (result / "tests/private/contract.sh").is_file()
    assert (result / "solution/solve.sh").is_file()
    manifest = json.loads((result / "bundle.manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "development"
    assert manifest["canonical_manifest_digest"].startswith("sha256:")
    assert (
        tomllib.loads((result / "task.toml").read_text(encoding="utf-8"))["metadata"]["r0_status"]
        == "development-only"
    )


def test_rust_compiler_refuses_production_compile(tmp_path: Path) -> None:
    source = _source(tmp_path)
    with pytest.raises(RustHarborCompileError, match="development-only"):
        RustHarborCompiler(ROOT / "toolchain.rust.dev.lock.toml").compile_task(
            source, tmp_path / "output"
        )


def test_rust_registry_routes_exact_identity(tmp_path: Path) -> None:
    source = _source(tmp_path)
    compiler = HarborCompilerRegistry.default().compiler_for_source(
        source, ROOT / "toolchain.rust.dev.lock.toml"
    )
    assert isinstance(compiler, RustHarborCompiler)


def test_rust_grader_uses_fixed_leaf_metric() -> None:
    result = grade_rust_report(
        expected_total=1,
        report_data={
            "schema_version": "1.0",
            "framework": "rust-harness",
            "report_format": "rust-bridge-json-v1",
            "collected": 1,
            "leaves": [
                {
                    "leaf_id": "leaf.one",
                    "status": "passed",
                    "duration_ms": 1.0,
                    "details": "ok",
                }
            ],
            "collection_errors": [],
            "runner_exit_code": 0,
        },
        runner_exit_code=0,
    )
    assert result.valid is True
    assert result.reward == 1.0
