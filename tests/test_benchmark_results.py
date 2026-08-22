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
