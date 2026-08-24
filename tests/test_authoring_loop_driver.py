from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load():
    path = Path(__file__).parents[1] / "scripts/run_authoring_loop.py"
    spec = importlib.util.spec_from_file_location("run_authoring_loop_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


driver = _load()


def test_driver_claims_bounded_plan_and_writes_worker_brief(tmp_path: Path, monkeypatch) -> None:
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {"candidate_id": "python-one", "package": "one", "language": "python"},
                    {"candidate_id": "python-two", "package": "two", "language": "python"},
                ]
            }
        ),
        encoding="utf-8",
    )
    queue_loop = driver._load_queue_loop()
    args = type("Args", (), {"queue": queue, "state": state})()
    queue_loop.command_init(args)
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "batch_id": "python-test-batch",
                "language": "python",
                "stages": ["environment-remediation"],
                "remediation_policy": {"missing_image": "must-remediate"},
                "worker_guidance": "docs/authoring-agent-remediation-guide.zh-CN.md",
                "tasks": [
                    {"candidate_id": "python-one", "package": "one"},
                    {"candidate_id": "python-two", "package": "two"},
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(driver, "_worktree", lambda path: "created")
    output = driver.run(
        type(
            "Args",
            (),
            {
                "plan": plan,
                "queue": queue,
                "queue_state": state,
                "state_root": tmp_path / "claims",
                "worktree_root": tmp_path / "worktrees",
                "owner": "pilot",
                "max_concurrency": 1,
                "lease_seconds": 60,
                "max_attempts": 3,
            },
        )()
    )

    assert output["model_runs_started"] is False
    assert [x["package"] for x in output["results"]] == ["one"]
    assert (tmp_path / "claims/python-test-batch/claims/one.json").is_file()


def test_driver_default_worktree_root_is_disk_backed() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--worktree-root",
        type=Path,
        default=Path(".nl2repo/authoring-work/worktrees"),
    )
    assert parser.parse_args([]).worktree_root == Path(".nl2repo/authoring-work/worktrees")
