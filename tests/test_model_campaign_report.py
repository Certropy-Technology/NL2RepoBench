from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_script():
    path = Path(__file__).parents[1] / "scripts/build_model_campaign_report.py"
    spec = importlib.util.spec_from_file_location("build_model_campaign_report", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


reporter = _load_script()


def _run(root: Path, task_id: str, model: str) -> None:
    trial = root / f"{model}-{task_id}" / "2026-08-23__00-00-00" / "harbor__abc"
    verifier = trial / "verifier"
    verifier.mkdir(parents=True)
    (trial / "result.json").write_text(
        json.dumps(
            {
                "task_name": task_id,
                "trial_name": f"{model}-{task_id}",
                "config": {"agent": {"model_name": model}},
                "verifier_result": {"rewards": {"reward": 1.0, "test_pass_rate": 1.0}},
                "agent_result": {"n_input_tokens": 10, "n_output_tokens": 5},
            }
        ),
        encoding="utf-8",
    )
    (verifier / "grading.json").write_text(
        json.dumps(
            {
                "valid": True,
                "expected_total": 2,
                "counts": {"passed": 2},
            }
        ),
        encoding="utf-8",
    )


def test_model_campaign_report_requires_both_models(tmp_path: Path) -> None:
    gpt = tmp_path / "gpt"
    fable = tmp_path / "fable"
    _run(gpt, "demo", "openai/gpt-5.6-sol")
    _run(fable, "demo", "anthropic/claude-fable-5")
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "campaign_id": "pilot",
                "tasks": ["demo"],
                "models": [
                    {"model_id": "gpt-5.6-sol", "run_root": str(gpt)},
                    {"model_id": "claude-fable-5", "run_root": str(fable)},
                ],
            }
        ),
        encoding="utf-8",
    )

    report = reporter.build_report(plan)

    assert report["task_count"] == 1
    assert {item["model"] for item in report["tasks"][0]["model_runs"]} == {
        "gpt-5.6-sol",
        "claude-fable-5",
    }
    assert report["summary"]["task_scores"]


def test_model_campaign_report_fails_on_missing_result(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "tasks": ["demo"],
                "models": [{"model_id": "gpt-5.6-sol", "run_root": str(tmp_path / "missing")}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing model results"):
        reporter.build_report(plan)


def test_model_campaign_report_rejects_foreign_model_rows(tmp_path: Path) -> None:
    gpt = tmp_path / "gpt"
    _run(gpt, "demo", "anthropic/claude-fable-5")
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "tasks": ["demo"],
                "models": [{"model_id": "gpt-5.6-sol", "run_root": str(gpt)}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="model mismatch"):
        reporter.build_report(plan)


def test_model_campaign_report_retains_oss_exemption_without_new_results(
    tmp_path: Path,
) -> None:
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "campaign_id": "pilot",
                "tasks": ["demo"],
                "skipped_existing_tasks": ["demo"],
                "existing_oss_runs": {
                    "demo": [{"source": "oss", "task_id": "demo"}]
                },
                "models": [
                    {"model_id": "gpt-5.6-sol", "run_root": str(tmp_path / "gpt"), "tasks": []},
                    {
                        "model_id": "claude-fable-5",
                        "run_root": str(tmp_path / "fable"),
                        "tasks": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    report = reporter.build_report(plan)

    assert report["missing"] == []
    assert report["tasks"][0]["existing_oss"] is True


def test_model_campaign_report_allows_in_progress_rows_for_diagnostics(tmp_path: Path) -> None:
    root = tmp_path / "gpt"
    trial = root / "gpt-demo" / "2026-08-23__00-00-00" / "harbor__abc"
    trial.mkdir(parents=True)
    (trial / "result.json").write_text(
        json.dumps(
            {
                "task_name": "demo",
                "trial_name": "gpt-demo",
                "config": {"agent": {"model_name": "openai/gpt-5.6-sol"}},
                "agent_result": {},
            }
        ),
        encoding="utf-8",
    )
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "tasks": ["demo"],
                "models": [{"model_id": "gpt-5.6-sol", "run_root": str(root)}],
            }
        ),
        encoding="utf-8",
    )

    report = reporter.build_report(plan, require_all=False)

    assert report["tasks"][0]["model_runs"][0]["status"] == "in-progress"


def test_model_campaign_report_marks_missing_rows_for_diagnostics(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "tasks": ["demo"],
                "models": [{"model_id": "gpt-5.6-sol", "run_root": str(tmp_path / "missing")}],
            }
        ),
        encoding="utf-8",
    )

    report = reporter.build_report(plan, require_all=False)

    assert report["tasks"][0]["model_runs"][0]["status"] == "missing"


def test_model_campaign_report_keeps_terminal_failure_over_pending_result(tmp_path: Path) -> None:
    root = tmp_path / "gpt"
    trial = root / "gpt-demo" / "2026-08-23__00-00-00" / "harbor__abc"
    verifier = trial / "verifier"
    verifier.mkdir(parents=True)
    (trial / "result.json").write_text(
        json.dumps(
            {
                "task_name": "demo",
                "trial_name": "gpt-demo",
                "config": {"agent": {"model_name": "openai/gpt-5.6-sol"}},
                "verifier_result": {},
                "exception_info": {"exception_type": "RuntimeError"},
            }
        ),
        encoding="utf-8",
    )
    (verifier / "grading.json").write_text(
        json.dumps({"valid": None, "failure_class": "verifier"}),
        encoding="utf-8",
    )
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "tasks": ["demo"],
                "models": [{"model_id": "gpt-5.6-sol", "run_root": str(root)}],
            }
        ),
        encoding="utf-8",
    )

    report = reporter.build_report(plan, require_all=False)

    model_run = report["tasks"][0]["model_runs"][0]
    assert model_run["status"] == "failed"
    assert model_run["failure_class"] == "verifier"
