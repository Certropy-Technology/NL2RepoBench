from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _gate_module():
    path = Path(__file__).parents[1] / "scripts/check_f0_runtime_contract.py"
    spec = importlib.util.spec_from_file_location("f0_runtime_gate", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_valid_contract(root: Path) -> None:
    source = Path(__file__).parents[1] / "harbor-runner/private-staging-contract.json"
    target = root / "harbor-runner/private-staging-contract.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def test_f0_runtime_gate_detects_old_model_and_private_bypasses(tmp_path: Path) -> None:
    module = _gate_module()
    source = tmp_path / "src/nl2repobench"
    source.mkdir(parents=True)
    (source / "runtime.py").write_text(
        "from nl2repobench.domain.models_v2 import V2RecordModel\nallow_private = True\n",
        encoding="utf-8",
    )
    (tmp_path / "catalog/sources").mkdir(parents=True)
    _write_valid_contract(tmp_path)
    report = module.check(tmp_path)
    assert report["passed"] is False
    assert {item["token"] for item in report["runtime_violations"]} >= {
        "models_v2",
        "v2-model",
        "broad-private",
    }


def test_f0_runtime_gate_accepts_clean_target_tree(tmp_path: Path) -> None:
    module = _gate_module()
    source = tmp_path / "src/nl2repobench"
    source.mkdir(parents=True)
    (source / "runtime.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "catalog/sources").mkdir(parents=True)
    _write_valid_contract(tmp_path)
    assert module.check(tmp_path)["passed"] is True


def test_f0_runtime_gate_rejects_every_legacy_source_shape(tmp_path: Path) -> None:
    module = _gate_module()
    (tmp_path / "src/nl2repobench").mkdir(parents=True)
    source_root = tmp_path / "catalog/sources"
    (source_root / "python-v1").mkdir(parents=True)
    (source_root / "python-v1/task.toml").write_text(
        'schema_version = "1.0"\n'
        'task_id = "python-v1"\n'
        '[metadata]\nlanguage = "python"\n'
        '[environment]\npython_version = "3.12"\nnetwork_mode = "no-network"\n'
        '[dependencies]\ninstaller = "uv"\n'
        '[tests]\nframework = "pytest"\ncommands = ["pytest"]\n',
        encoding="utf-8",
    )
    (source_root / "node-v2").mkdir()
    (source_root / "node-v2/task.toml").write_text(
        'schema_version = "2.0"\n'
        'task_id = "node-v2"\n'
        '[metadata]\nlanguage = "node"\n'
        '[environment.runtime]\nlanguage = "node"\nruntime = "node"\n'
        'version = "22"\npackage_manager = "npm"\npackage_manager_version = "10"\n'
        '[dependencies]\npackage_manager = "npm"\nlock_artifact = {}\n'
        '[tests]\nframework = "node:test"\nreport_format = "node-test-json-v1"\n',
        encoding="utf-8",
    )
    _write_valid_contract(tmp_path)
    report = module.check(tmp_path)
    assert report["source_migration_gaps"] == [
        "catalog/sources/node-v2/task.toml",
        "catalog/sources/python-v1/task.toml",
    ]
    errors = report["source_migration_errors"]
    assert any("schema_version" in item for item in errors["catalog/sources/node-v2/task.toml"])
    assert any("python_version" in item for item in errors["catalog/sources/python-v1/task.toml"])
    assert any("commands" in item for item in errors["catalog/sources/python-v1/task.toml"])


def test_f0_runtime_gate_reports_missing_contract(tmp_path: Path) -> None:
    module = _gate_module()
    (tmp_path / "src/nl2repobench").mkdir(parents=True)
    (tmp_path / "catalog/sources").mkdir(parents=True)

    report = module.check(tmp_path)

    assert report["passed"] is False
    assert report["blockers"] == ["private-staging-contract-missing"]
    assert report["private_staging_contract_errors"] == []


def test_f0_runtime_gate_reports_malformed_contract_json(tmp_path: Path) -> None:
    module = _gate_module()
    (tmp_path / "src/nl2repobench").mkdir(parents=True)
    (tmp_path / "catalog/sources").mkdir(parents=True)
    contract_path = tmp_path / "harbor-runner/private-staging-contract.json"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_bytes(b"{\n")

    report = module.check(tmp_path)

    assert report["passed"] is False
    assert report["blockers"] == ["private-staging-contract-invalid"]
    assert report["private_staging_contract_errors"]


@pytest.mark.parametrize(
    ("path", "mutate", "message"),
    [
        (
            "lanes.python+uv.unknown",
            lambda contract: contract["lanes"].__setitem__("unknown", {}),
            "lanes must contain exactly",
        ),
        (
            "staging_roots.dependency.path",
            lambda contract: contract["staging_roots"]["dependency"].__setitem__(
                "path", "/tmp/private"
            ),
            "safe repository-relative",
        ),
        (
            "staging_roots.dependency.mode",
            lambda contract: contract["staging_roots"]["dependency"].__setitem__(
                "mode", "0755"
            ),
            "ephemeral mode 0700",
        ),
        (
            "staging_roots.dependency.uid",
            lambda contract: contract["staging_roots"]["dependency"].__setitem__(
                "uid", 10001
            ),
            "owned by uid/gid",
        ),
        (
            "staging_roots.dependency.duplicate-path",
            lambda contract: contract["staging_roots"]["oracle"].__setitem__(
                "path", contract["staging_roots"]["dependency"]["path"]
            ),
            "paths must be unique",
        ),
        (
            "artifact_kind_roots.mapping",
            lambda contract: contract["artifact_kind_roots"].__setitem__(
                "test-bundle", "oracle"
            ),
            "artifact_kind_roots must exactly bind",
        ),
        (
            "lanes.python+uv.mapping",
            lambda contract: contract["lanes"]["python+uv"]["artifact_kind_roots"].__setitem__(
                "test-bundle", "oracle"
            ),
            "artifact, root, or offline smoke",
        ),
        (
            "lanes.python+uv.toolchain_binding.digest_format",
            lambda contract: contract["lanes"]["python+uv"]["toolchain_binding"].__setitem__(
                "digest_format", "sha1:<40 hex>"
            ),
            "toolchain_binding is invalid",
        ),
    ],
)
def test_f0_runtime_gate_rejects_malformed_private_contract(
    tmp_path: Path, path: str, mutate, message: str
) -> None:
    module = _gate_module()
    (tmp_path / "src/nl2repobench").mkdir(parents=True)
    (tmp_path / "catalog/sources").mkdir(parents=True)
    _write_valid_contract(tmp_path)
    contract_path = tmp_path / "harbor-runner/private-staging-contract.json"
    mutated = copy.deepcopy(json.loads(contract_path.read_text(encoding="utf-8")))
    mutate(mutated)
    contract_path.write_text(json.dumps(mutated) + "\n", encoding="utf-8")

    report = module.check(tmp_path)

    assert report["passed"] is False
    assert report["blockers"] == ["private-staging-contract-invalid"]
    assert any(message in item for item in report["private_staging_contract_errors"])
