from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _load():
    path = Path(__file__).parents[1] / "scripts/model_auto_coordinator.py"
    spec = importlib.util.spec_from_file_location("model_auto_coordinator_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


model = _load()


def _git(repository: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repository, text=True).strip()


def test_runnable_tasks_require_integration_lifecycle_and_projection(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _git(tmp_path, "config", "user.name", "Test")
    source = tmp_path / "catalog/sources/demo"
    runtime = tmp_path / "catalog/tasks/demo"
    source.mkdir(parents=True)
    runtime.mkdir(parents=True)
    source.joinpath("task.toml").write_text(
        '[metadata]\nlanguage = "go"\n[lifecycle]\nstatus = "controls-passed"\n',
        encoding="utf-8",
    )
    runtime.joinpath("task.toml").write_text("schema_version = \"1.4\"\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "Integrate authored task demo")

    tasks = model.runnable_tasks(tmp_path, max_age_days=30)

    assert [task.task_id for task in tasks] == ["demo"]
    assert tasks[0].lifecycle == "controls-passed"


def test_fresh_inventory_requires_run_after_current_integration() -> None:
    task = model.Task("demo", "go", "controls-passed", "abc", 200, "s", "r")
    inventory = {
        "runs": [
            {"model": "gpt-5.6-sol", "task_id": "demo", "finished_at": "1970-01-01T00:01:40+00:00"},
            {
                "model": "claude-opus-5",
                "task_id": "demo",
                "finished_at": "1970-01-01T00:05:00+00:00",
            },
        ]
    }

    filtered, completed = model.fresh_inventory(inventory, [task])

    assert len(filtered["runs"]) == 1
    assert completed["gpt-5.6-sol"] == set()
    assert completed["claude-opus-5"] == {"demo"}


def test_select_missing_tasks_is_bounded_and_accepts_partial_model_coverage() -> None:
    tasks = [
        model.Task(name, "go", "controls-passed", name, 300 - index, "s", "r")
        for index, name in enumerate(("one", "two", "three"))
    ]
    completed = {
        "gpt-5.6-sol": {"one", "two"},
        "claude-opus-5": {"one"},
    }

    selected = model.select_missing_tasks(tasks, completed, batch_size=1)

    assert [task.task_id for task in selected] == ["two"]


def test_campaign_payload_binds_current_task_metadata(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        model,
        "_run",
        lambda *args, **kwargs: {"exit_code": 0, "output": "deadbeef\n"},
    )
    task = model.Task("demo", "go", "controls-passed", "abc", 200, "sha256:s", "sha256:r")

    payload = model._campaign_payload(tmp_path, "auto-2x1-test", [task])

    assert payload["max_total_concurrency"] == 2
    assert payload["tasks"][0]["integration_commit"] == "abc"
    assert payload["tasks"][0]["runtime_toml_sha256"] == "sha256:r"
