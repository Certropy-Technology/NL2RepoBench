from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


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


def test_select_missing_for_model_keeps_lanes_independent() -> None:
    tasks = [
        model.Task(name, "go", "controls-passed", name, 300 - index, "s", "r")
        for index, name in enumerate(("one", "two", "three"))
    ]
    completed = {
        "gpt-5.6-sol": {"one"},
        "claude-opus-5": {"one", "two"},
    }

    sol = model.select_missing_for_model(
        tasks, completed, "gpt-5.6-sol", batch_size=1
    )
    opus = model.select_missing_for_model(
        tasks, completed, "claude-opus-5", batch_size=1
    )

    assert [task.task_id for task in sol] == ["two"]
    assert [task.task_id for task in opus] == ["three"]


def test_active_models_reads_each_model_queue_independently(monkeypatch) -> None:
    monkeypatch.setattr(
        model,
        "_process_commands",
        lambda: [
            ["python", "run_model_from_pi.py", "--model-id", "gpt-5.6-sol"],
            ["python", "other.py", "--model-id", "claude-opus-5"],
        ],
    )

    assert model._active_models() == {"gpt-5.6-sol"}


def test_cycle_starts_only_idle_model_lane(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "repo"
    state_root = repository / ".nl2repo/model-auto"
    docker_root = tmp_path / "docker"
    repository.joinpath(".venv/bin").mkdir(parents=True)
    docker_root.mkdir()
    task = model.Task("demo", "go", "controls-passed", "abc", 200, "s", "r")
    monkeypatch.setattr(model, "_active_models", lambda: {"gpt-5.6-sol"})
    monkeypatch.setattr(
        model.shutil,
        "disk_usage",
        lambda _path: SimpleNamespace(free=100 * 1024**3),
    )
    monkeypatch.setattr(model, "runnable_tasks", lambda *_args, **_kwargs: [task])
    monkeypatch.setattr(
        model,
        "fresh_inventory",
        lambda *_args: (
            {"schema_version": "1.0", "source": "oss", "runs": []},
            {"gpt-5.6-sol": set(), "claude-opus-5": set()},
        ),
    )

    def fake_run(command, **_kwargs):
        output = Path(command[command.index("--output") + 1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text('{"runs":[]}', encoding="utf-8")
        return {"command": command, "exit_code": 0, "output": "ok"}

    launches = []
    monkeypatch.setattr(model, "_run", fake_run)
    monkeypatch.setattr(
        model,
        "_launch_model_queue",
        lambda *args, **kwargs: launches.append(kwargs) or {
            "model_id": kwargs["model_id"]
        },
    )
    args = SimpleNamespace(
        docker_root=docker_root,
        min_free_bytes=20 * 1024**3,
        inventory_timeout_seconds=30,
        max_integration_age_days=30,
        batch_size=4,
    )

    event = model.cycle(repository, state_root, args)

    assert event["event"] == "model-queues-started"
    assert [item["model_id"] for item in event["started"]] == ["claude-opus-5"]
    assert [launch["model_id"] for launch in launches] == ["claude-opus-5"]


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
