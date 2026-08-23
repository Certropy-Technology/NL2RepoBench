from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/validate_node_production.py"
    spec = importlib.util.spec_from_file_location("validate_node_production", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gate = _load_script()


def test_node_production_gate_accepts_structured_vertical_slice(tmp_path: Path) -> None:
    task = tmp_path / "task"
    task.mkdir()
    (task / "task.toml").write_text(
        '[task]\n'  # unused section keeps this fixture compact
        'task_id = "demo"\n'
        '[tests]\nexpected_total = 1\n',
        encoding="utf-8",
    )
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "bundle.manifest.json").write_text(
        json.dumps({"mode": "production"}), encoding="utf-8"
    )
    toolchain = tmp_path / "toolchain.toml"
    toolchain.write_text(
        'status = "locked"\nnode_grader = "locked"\n'
        '[runtime]\nruntime_version = "24.19.0"\n',
        encoding="utf-8",
    )
    oracle = tmp_path / "oracle/verifier"
    oracle.mkdir(parents=True)
    (oracle / "grading.json").write_text(
        json.dumps(
            {
                "valid": True,
                "reward": 1.0,
                "expected_total": 1,
                "counts": {"collected": 1},
            }
        ),
        encoding="utf-8",
    )
    controls = tmp_path / "controls.json"
    controls.write_text(
        json.dumps({"controls": {name: {"passed": True} for name in gate.EXPECTED}}),
        encoding="utf-8",
    )

    result = gate.validate(task, bundle, toolchain, tmp_path / "oracle", controls)

    assert result["task_id"] == "demo"
