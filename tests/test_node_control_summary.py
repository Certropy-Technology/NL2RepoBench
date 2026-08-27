from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/summarize_node_controls.py"
    spec = importlib.util.spec_from_file_location("summarize_node_controls", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


summary = _load_script()


def test_node_control_summary_classifies_all_control_kinds(tmp_path: Path) -> None:
    values = {
        "empty": {"valid": True, "reward": 0, "failure_class": "model"},
        "stub": {"valid": True, "reward": 0.1},
        "forgery": {"valid": True, "reward": 0.6},
        "install-script": {"valid": True, "failure_reason": "candidate-installation-failed"},
        "loader-hook": {"valid": True, "reward": 0.6},
        "hang": {
            "valid": True,
            "reward": 0.0,
            "failure_class": "model",
            "failure_reason": "candidate-call-failed",
        },
        "offline": {"valid": True, "reward": 0.0},
    }
    for kind, grading in values.items():
        directory = tmp_path / kind
        directory.mkdir()
        (directory / "verifier").mkdir()
        (directory / "verifier/grading.json").write_text(
            json.dumps(grading), encoding="utf-8"
        )

    report = summary.summarize(tmp_path)

    assert all(item["passed"] for item in report["controls"].values())
