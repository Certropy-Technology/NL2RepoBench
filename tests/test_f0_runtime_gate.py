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
        "from nl2repobench.domain.models_v2 import V2RecordModel\n"
        "allow_private = True\n",
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
