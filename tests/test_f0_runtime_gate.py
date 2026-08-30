from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _gate_module():
    path = Path(__file__).parents[1] / "scripts/check_f0_runtime_contract.py"
    spec = importlib.util.spec_from_file_location("f0_runtime_gate", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_f0_runtime_gate_detects_old_model_and_private_bypasses(tmp_path: Path) -> None:
    module = _gate_module()
    source = tmp_path / "src/nl2repobench"
    source.mkdir(parents=True)
    (source / "runtime.py").write_text(
        "from nl2repobench.domain.models_v2 import V2RecordModel\nallow_private = True\n",
        encoding="utf-8",
    )
    (tmp_path / "catalog/sources").mkdir(parents=True)
    (tmp_path / "harbor-runner").mkdir()
    (tmp_path / "harbor-runner/private-staging-contract.json").write_text("{}\n")
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
    (tmp_path / "harbor-runner").mkdir()
    (tmp_path / "harbor-runner/private-staging-contract.json").write_text("{}\n")
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
    (tmp_path / "harbor-runner").mkdir()
    (tmp_path / "harbor-runner/private-staging-contract.json").write_text("{}\n")
    report = module.check(tmp_path)
    assert report["source_migration_gaps"] == [
        "catalog/sources/node-v2/task.toml",
        "catalog/sources/python-v1/task.toml",
    ]
    errors = report["source_migration_errors"]
    assert any("schema_version" in item for item in errors["catalog/sources/node-v2/task.toml"])
    assert any("python_version" in item for item in errors["catalog/sources/python-v1/task.toml"])
    assert any("commands" in item for item in errors["catalog/sources/python-v1/task.toml"])
