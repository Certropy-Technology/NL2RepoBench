from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def _load_script() -> Any:
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
            "valid": False,
            "failure_class": "verifier",
            "failure_reason": "node-collection-error",
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


def test_node_control_summary_ignores_workspace_forgery_and_accepts_bounded_hang(
    tmp_path: Path,
) -> None:
    values = {
        "empty": {"valid": True, "reward": 0, "failure_class": "model"},
        "stub": {"valid": True, "reward": 0.1},
        "forgery": {"valid": True, "reward": 0.0},
        "install-script": {
            "valid": True,
            "failure_reason": "candidate-installation-failed",
        },
        "loader-hook": {"valid": True, "reward": 0.2},
        "hang": {
            "valid": True,
            "reward": 0.0,
            "failure_class": "model",
            "failure_reason": "candidate-call-failed",
        },
        "offline": {"valid": True, "reward": 0.0},
    }
    for kind, grading in values.items():
        verifier = tmp_path / kind / "trial" / "verifier"
        verifier.mkdir(parents=True)
        (verifier / "grading.json").write_text(json.dumps(grading), encoding="utf-8")

    forged = tmp_path / "forgery" / "trial" / "artifacts" / "workspace" / "logs" / "verifier"
    forged.mkdir(parents=True)
    (forged / "grading.json").write_text(
        json.dumps({"valid": True, "reward": 1.0}), encoding="utf-8"
    )

    report = summary.summarize(tmp_path)

    assert all(item["passed"] for item in report["controls"].values())
    assert report["controls"]["forgery"]["reward"] == 0.0
