from __future__ import annotations

import json
from pathlib import Path

from nl2repobench.analysis.results import load_results, summarize_results


def _write_trial(
    root: Path,
    name: str,
    *,
    reward: float,
    valid: bool,
    failure_class: str | None = None,
) -> None:
    trial = root / name
    verifier = trial / "verifier"
    verifier.mkdir(parents=True)
    (trial / "result.json").write_text(
        json.dumps(
            {
                "task_name": "demo",
                "trial_name": name,
                "config": {"agent": {"model_name": "test/model"}},
                "verifier_result": {"rewards": {"reward": reward, "test_pass_rate": reward}},
                "agent_result": {"n_input_tokens": 10, "n_output_tokens": 5, "cost_usd": 0.1},
                "started_at": "2026-01-01T00:00:00Z",
                "finished_at": "2026-01-01T00:00:01Z",
            }
        ),
        encoding="utf-8",
    )
    (verifier / "grading.json").write_text(
        json.dumps(
            {
                "valid": valid,
                "reward": reward,
                "expected_total": 10,
                "counts": {"passed": int(reward * 10)},
                "failure_class": failure_class,
            }
        ),
        encoding="utf-8",
    )


def test_results_use_valid_task_macro_average(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    _write_trial(root, "trial-1", reward=1.0, valid=True)
    _write_trial(root, "trial-2", reward=0.5, valid=True)
    _write_trial(root, "trial-3", reward=0.0, valid=False, failure_class="infrastructure")
    (root / "job-result.json").write_text(json.dumps({"stats": {}}), encoding="utf-8")

    frame, errors = load_results([root])
    assert errors == []
    assert frame.height == 3
    summary = summarize_results(frame)
    assert summary["task_scores"] == [
        {"model": "test/model", "task_id": "demo", "task_score": 0.75, "attempts": 2}
    ]
    assert summary["model_summary"][0]["macro_task_score"] == 0.75
    assert summary["failure_summary"] == [{"classification": "infrastructure", "trials": 1}]


def test_results_reclassify_legacy_fable_empty_workspace(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    _write_trial(root, "fable-trial", reward=0.0, valid=False, failure_class=None)
    trial = root / "fable-trial"
    (trial / "result.json").write_text(
        json.dumps(
            {
                "task_name": "demo",
                "trial_name": "fable-trial",
                "config": {"agent": {"model_name": "anthropic/claude-fable-5"}},
                "verifier_result": {"rewards": {"reward": 0.0}},
                "exception_info": None,
            }
        ),
        encoding="utf-8",
    )
    (trial / "agent").mkdir()
    (trial / "agent" / "openhands_sdk.txt").write_text(
        "Error validating tool 'terminal'\nLLM produced empty response\n",
        encoding="utf-8",
    )

    frame, errors = load_results([root])

    assert errors == []
    assert frame.to_dicts()[0]["failure_class"] == "infrastructure"
    assert frame.to_dicts()[0]["failure_reason"] == "provider-tool-schema-empty-input"


def test_results_classify_verifier_build_exception(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    _write_trial(root, "verifier-trial", reward=0.0, valid=False, failure_class=None)
    trial = root / "verifier-trial"
    (trial / "result.json").write_text(
        json.dumps(
            {
                "task_name": "demo",
                "trial_name": "verifier-trial",
                "config": {"agent": {"model_name": "anthropic/claude-fable-5"}},
                "verifier_result": {},
                "exception_info": {
                    "exception_type": "RuntimeError",
                    "exception_message": "Docker compose command failed during build",
                },
            }
        ),
        encoding="utf-8",
    )

    frame, errors = load_results([root])

    assert errors == []
    assert frame.to_dicts()[0]["failure_class"] == "verifier"
    assert frame.to_dicts()[0]["failure_reason"] == "verifier-build-failed"


def test_results_summary_includes_invalid_verifier_rows_with_null_valid(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    _write_trial(root, "verifier-trial", reward=0.0, valid=False, failure_class="verifier")
    trial = root / "verifier-trial"
    payload = json.loads((trial / "result.json").read_text(encoding="utf-8"))
    payload["task_name"] = "nl2repobench/pss"
    (trial / "result.json").write_text(json.dumps(payload), encoding="utf-8")
    grading = json.loads((trial / "verifier/grading.json").read_text(encoding="utf-8"))
    grading["valid"] = None
    (trial / "verifier/grading.json").write_text(json.dumps(grading), encoding="utf-8")

    frame, errors = load_results([root])

    assert errors == []
    assert summarize_results(frame)["failure_summary"] == [
        {"classification": "verifier", "trials": 1}
    ]


def test_results_strip_harbor_namespace_from_task_name(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    _write_trial(root, "namespaced-trial", reward=1.0, valid=True)
    trial = root / "namespaced-trial"
    payload = json.loads((trial / "result.json").read_text(encoding="utf-8"))
    payload["task_name"] = "nl2repobench/flasky"
    (trial / "result.json").write_text(json.dumps(payload), encoding="utf-8")

    frame, errors = load_results([root])

    assert errors == []
    assert frame.to_dicts()[0]["task_id"] == "flasky"
