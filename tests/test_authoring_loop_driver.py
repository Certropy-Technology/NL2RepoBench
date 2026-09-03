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


def _args(tmp_path: Path, plan: Path, queue: Path, state: Path):
    return type(
        "Args",
        (),
        {
            "plan": plan,
            "queue": queue,
            "queue_state": state,
            "state_root": tmp_path / "claims",
            "worktree_root": tmp_path / "worktrees",
            "owner": "pilot",
            "max_concurrency": 2,
            "lease_seconds": 60,
            "max_attempts": 3,
            "output": tmp_path / "execution.json",
            "pi_command": "pi",
            "provider": "z-open-api-gpt-openai-responses",
            "model": "gpt-5.6-sol",
            "thinking": "high",
            "models_file": tmp_path / "models.json",
            "credential_env": None,
            "session_root": tmp_path / "sessions",
            "agent_timeout_sec": 60,
            "exclude_tools": "subagent,subagent_supervisor,subagent_wait",
        },
    )()


def test_effective_concurrency_hot_reload_and_pause(tmp_path: Path) -> None:
    args = type("Args", (), {"max_concurrency": 2, "concurrency_file": None})()
    assert driver._effective_concurrency(args) == (True, 2)

    config = tmp_path / "runtime-config.json"
    config.write_text(
        json.dumps({"enabled": True, "controller_concurrency": 4}),
        encoding="utf-8",
    )
    args.concurrency_file = config
    assert driver._effective_concurrency(args) == (True, 4)

    config.write_text(
        json.dumps({"enabled": False, "controller_concurrency": 1}),
        encoding="utf-8",
    )
    assert driver._effective_concurrency(args) == (False, 1)


def test_worktree_enables_sparse_authoring_profile(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "task"
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        if command[:3] == ["git", "worktree", "add"]:
            (target / ".git").mkdir(parents=True)
        return type("Result", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr(driver.subprocess, "run", fake_run)

    assert driver._worktree(target) == "created"
    sparse = next(command for command in calls if "sparse-checkout" in command)
    assert "catalog/sources" in sparse
    assert "catalog/tasks" not in sparse
    assert "src" in sparse
    assert "tests" in sparse


def test_driver_launches_direct_pi_and_records_handoff(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(driver, "TMPFS_ROOTS", ())
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {"candidate_id": "python-one", "package": "one", "language": "python"}
                ]
            }
        ),
        encoding="utf-8",
    )
    queue_loop = driver._load_queue_loop()
    queue_loop.command_init(type("Args", (), {"queue": queue, "state": state})())
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "batch_id": "python-test-batch",
                "language": "python",
                "stages": ["environment-remediation"],
                "remediation_policy": {"missing_image": "must-remediate"},
                "worker_guidance": "docs/authoring-agent-remediation-guide.zh-CN.md",
                "tasks": [{"candidate_id": "python-one", "package": "one"}],
            }
        ),
        encoding="utf-8",
    )
    args = _args(tmp_path, plan, queue, state)
    monkeypatch.setattr(driver, "_worktree", lambda path: "created")

    calls: list[dict[str, object]] = []

    def fake_launch(_args, **kwargs):
        calls.append(kwargs)
        task_root = Path(kwargs["worktree"]) / "catalog/sources/one"
        task_root.mkdir(parents=True)
        (task_root / "task.toml").write_text("task_id = 'one'\n", encoding="utf-8")
        (task_root / "instruction.md").write_text("# one\n", encoding="utf-8")
        (task_root / "production-evidence.json").write_text("{}\n", encoding="utf-8")
        handoff = Path(kwargs["handoff_path"])
        handoff.write_text('{"status":"controls-passed"}\n', encoding="utf-8")
        return {
            "status": "exited",
            "exit_code": 0,
            "session_id": "python-test-batch-one-attempt-1",
            "session_dir": str(kwargs["session_dir"]),
            "log": str(kwargs["log_path"]),
            "handoff": str(handoff),
            "command": ["pi", "--print"],
        }

    monkeypatch.setattr(driver, "_launch_agent", fake_launch)
    monkeypatch.setattr(
        driver,
        "_run_network_policy_check",
        lambda worktree, task_root: {
            "status": "passed",
            "exit_code": 0,
            "report": str(Path(worktree) / ".nl2repo/evidence/network-policy.json"),
            "output": "passed",
        },
    )
    monkeypatch.setattr(
        driver,
        "_run_authoring_task_lint",
        lambda worktree, task_root: {
            "status": "passed",
            "exit_code": 0,
            "report": str(Path(worktree) / ".nl2repo/evidence/authoring-task-lint.json"),
            "output": "passed",
        },
    )
    monkeypatch.setattr(
        driver,
        "_run_production_gate_check",
        lambda *values: {
            "status": "passed",
            "exit_code": 0,
            "report": "gates",
            "output": "passed",
        },
    )
    output = driver.run(args)

    assert output["agent_mode"] == "top-level-pi-cli"
    assert output["agent_runs_started"] is True
    assert output["model_runs_started"] is False
    assert [x["package"] for x in output["results"]] == ["one"]
    assert output["results"][0]["status"] == "complete"
    assert calls[0]["worktree"] != tmp_path
    assert (tmp_path / "claims/python-test-batch/claims/one.json").is_file()

    status_output = []
    original_stdout = sys.stdout
    try:
        from io import StringIO

        sys.stdout = StringIO()
        queue_loop.command_status(type("Args", (), {"queue": queue, "state": state})())
        status_output.append(json.loads(sys.stdout.getvalue()))
    finally:
        sys.stdout = original_stdout
    assert status_output[0]["counts"] == {"complete": 1}


def test_driver_does_not_reuse_an_old_handoff_after_empty_agent_exit(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(driver, "TMPFS_ROOTS", ())
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {"candidate_id": "python-one", "package": "one", "language": "python"}
                ]
            }
        ),
        encoding="utf-8",
    )
    queue_loop = driver._load_queue_loop()
    queue_loop.command_init(type("Args", (), {"queue": queue, "state": state})())
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "batch_id": "python-stale-handoff-batch",
                "language": "python",
                "stages": [],
                "tasks": [{"candidate_id": "python-one", "package": "one"}],
            }
        ),
        encoding="utf-8",
    )
    args = _args(tmp_path, plan, queue, state)

    def fake_worktree(path: Path) -> str:
        path.mkdir(parents=True)
        old_handoff = path / ".nl2repo/authoring-handoff.json"
        old_handoff.parent.mkdir(parents=True)
        old_handoff.write_text('{"status":"awaiting-agent-run"}\n', encoding="utf-8")
        return "reused"

    monkeypatch.setattr(driver, "_worktree", fake_worktree)

    def fake_launch(_args, **kwargs):
        task_root = Path(kwargs["worktree"]) / "catalog/sources/one"
        task_root.mkdir(parents=True)
        (task_root / "task.toml").write_text("task_id = 'one'\n", encoding="utf-8")
        (task_root / "instruction.md").write_text("# one\n", encoding="utf-8")
        return {
            "status": "exited",
            "exit_code": 0,
            "log": str(kwargs["log_path"]),
            "handoff": str(kwargs["handoff_path"]),
        }

    monkeypatch.setattr(driver, "_launch_agent", fake_launch)
    monkeypatch.setattr(
        driver,
        "_run_network_policy_check",
        lambda *values: {
            "status": "passed",
            "exit_code": 0,
            "report": "network",
            "output": "passed",
        },
    )
    monkeypatch.setattr(
        driver,
        "_run_authoring_task_lint",
        lambda *values: {"status": "passed", "exit_code": 0, "report": "lint", "output": "passed"},
    )
    monkeypatch.setattr(
        driver,
        "_run_production_gate_check",
        lambda *values: {
            "status": "passed",
            "exit_code": 0,
            "report": "gates",
            "output": "passed",
        },
    )

    output = driver.run(args)

    assert output["results"][0]["status"] == "released"
    assert "fresh valid" in output["results"][0]["reason"]
    state_payload = json.loads(state.read_text(encoding="utf-8"))
    assert state_payload["items"]["python-one"]["status"] == "pending"


def test_pi_command_is_top_level_and_excludes_subagent_tools(tmp_path: Path) -> None:
    args = type(
        "Args",
        (),
        {
            "pi_command": "pi",
            "provider": "z-open-api-gpt-openai-responses",
            "model": "gpt-5.6-sol",
            "thinking": "high",
            "exclude_tools": "subagent,subagent_supervisor,subagent_wait",
            "allow_internal_subagent": False,
        },
    )()
    command = driver._pi_command(
        args,
        prompt="author one",
        session_dir=tmp_path / "sessions",
        session_id="batch-one-attempt-1",
    )
    assert command[0] == "pi"
    assert "--print" in command
    assert "--session-id" in command
    assert command[command.index("--session-id") + 1] == "batch-one-attempt-1"
    assert command[command.index("--exclude-tools") + 1].startswith("subagent")
    assert command[-1] == "author one"


def test_pi_command_can_explicitly_allow_internal_subagent(tmp_path: Path) -> None:
    args = type(
        "Args",
        (),
        {
            "pi_command": "pi",
            "provider": "z-open-api-gpt-openai-responses",
            "model": "gpt-5.6-sol",
            "thinking": "high",
            "exclude_tools": "subagent,subagent_supervisor,subagent_wait",
            "allow_internal_subagent": True,
        },
    )()
    command = driver._pi_command(
        args,
        prompt="author one",
        session_dir=tmp_path / "sessions",
        session_id="batch-one-attempt-1",
    )
    assert command[command.index("--exclude-tools") + 1] == "subagent_wait"


def test_agent_prompt_names_required_tracked_production_evidence(tmp_path: Path) -> None:
    prompt = driver._agent_prompt(
        plan={"batch_id": "go-test", "language": "go"},
        task={"candidate_id": "go-demo", "package": "go-demo"},
        brief_path=tmp_path / "brief.json",
        worktree=tmp_path,
        handoff_path=tmp_path / ".nl2repo/authoring-handoff.json",
        allow_internal_subagent=False,
    )

    assert "catalog/sources/go-demo/production-evidence.json" in prompt
    assert "required tracked release files" in prompt


def test_driver_refills_from_pending_queue_after_plan_is_exhausted(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(driver, "TMPFS_ROOTS", ())
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {
                        "candidate_id": "python-one",
                        "package": "one",
                        "language": "python",
                        "status": "candidate",
                    },
                    {
                        "candidate_id": "python-two",
                        "package": "two",
                        "language": "python",
                        "status": "candidate",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    queue_loop = driver._load_queue_loop()
    queue_loop.command_init(type("Args", (), {"queue": queue, "state": state})())
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "batch_id": "python-refill-batch",
                "language": "python",
                "stages": [],
                "tasks": [{"candidate_id": "python-one", "package": "one"}],
            }
        ),
        encoding="utf-8",
    )
    args = _args(tmp_path, plan, queue, state)
    monkeypatch.setattr(driver, "_worktree", lambda path: "created")
    monkeypatch.setattr(
        driver,
        "_run_network_policy_check",
        lambda worktree, task_root: {
            "status": "passed",
            "exit_code": 0,
            "report": str(Path(worktree) / ".nl2repo/evidence/network-policy.json"),
            "output": "passed",
        },
    )
    monkeypatch.setattr(
        driver,
        "_run_authoring_task_lint",
        lambda worktree, task_root: {
            "status": "passed",
            "exit_code": 0,
            "report": str(Path(worktree) / ".nl2repo/evidence/authoring-task-lint.json"),
            "output": "passed",
        },
    )
    monkeypatch.setattr(
        driver,
        "_run_production_gate_check",
        lambda *values: {
            "status": "passed",
            "exit_code": 0,
            "report": "gates",
            "output": "passed",
        },
    )

    def fake_launch(_args, **kwargs):
        package = Path(kwargs["worktree"]).name
        task_root = Path(kwargs["worktree"]) / f"catalog/sources/{package}"
        task_root.mkdir(parents=True)
        (task_root / "task.toml").write_text("task_id = 'demo'\n", encoding="utf-8")
        (task_root / "instruction.md").write_text("# task\n", encoding="utf-8")
        (task_root / "production-evidence.json").write_text("{}\n", encoding="utf-8")
        handoff = Path(kwargs["handoff_path"])
        handoff.write_text('{"status":"controls-passed"}\n', encoding="utf-8")
        return {
            "status": "exited",
            "exit_code": 0,
            "session_id": "refill-attempt-1",
            "session_dir": str(kwargs["session_dir"]),
            "log": str(kwargs["log_path"]),
            "handoff": str(handoff),
            "command": ["pi", "--print"],
        }

    monkeypatch.setattr(driver, "_launch_agent", fake_launch)
    output = driver.run(args)

    assert output["queue_refill"] is True
    assert [item["package"] for item in output["results"]] == ["one", "two"]
    assert all(item["status"] == "complete" for item in output["results"])


def test_task_source_ready_requires_production_evidence(tmp_path: Path) -> None:
    task_root = tmp_path / "catalog/sources/demo"
    task_root.mkdir(parents=True)
    (task_root / "task.toml").write_text("task_id = 'demo'\n", encoding="utf-8")
    (task_root / "instruction.md").write_text("# demo\n", encoding="utf-8")

    assert driver._task_source_ready(task_root) is False

    (task_root / "production-evidence.json").write_text("{}\n", encoding="utf-8")
    assert driver._task_source_ready(task_root) is True


def test_driver_can_disable_queue_refill(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(driver, "TMPFS_ROOTS", ())
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {
                        "candidate_id": "python-one",
                        "package": "one",
                        "language": "python",
                        "status": "candidate",
                    },
                    {
                        "candidate_id": "python-two",
                        "package": "two",
                        "language": "python",
                        "status": "candidate",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    queue_loop = driver._load_queue_loop()
    queue_loop.command_init(type("Args", (), {"queue": queue, "state": state})())
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "batch_id": "python-no-refill-batch",
                "language": "python",
                "stages": [],
                "tasks": [{"candidate_id": "python-one", "package": "one"}],
            }
        ),
        encoding="utf-8",
    )
    args = _args(tmp_path, plan, queue, state)
    args.refill_queue = False
    monkeypatch.setattr(driver, "_worktree", lambda path: "created")
    monkeypatch.setattr(
        driver,
        "_run_network_policy_check",
        lambda *args: {
            "status": "passed",
            "exit_code": 0,
            "report": "network",
            "output": "passed",
        },
    )
    monkeypatch.setattr(
        driver,
        "_run_authoring_task_lint",
        lambda *args: {
            "status": "passed",
            "exit_code": 0,
            "report": "lint",
            "output": "passed",
        },
    )

    def fake_launch(_args, **kwargs):
        task_root = Path(kwargs["worktree"]) / "catalog/sources/one"
        task_root.mkdir(parents=True)
        (task_root / "task.toml").write_text("task_id = 'one'\n", encoding="utf-8")
        (task_root / "instruction.md").write_text("# one\n", encoding="utf-8")
        handoff = Path(kwargs["handoff_path"])
        handoff.write_text('{"status":"controls-passed"}\n', encoding="utf-8")
        return {"status": "exited", "exit_code": 0, "log": "log", "handoff": str(handoff)}

    monkeypatch.setattr(driver, "_launch_agent", fake_launch)
    output = driver.run(args)

    assert output["queue_refill"] is False
    assert [item["package"] for item in output["results"]] == ["one"]


def test_authoring_settings_keep_capabilities_but_disable_lark_and_raise_retry(
    tmp_path: Path, monkeypatch
) -> None:
    global_settings = tmp_path / "global-settings.json"
    global_settings.write_text(
        json.dumps(
            {
                "packages": [
                    "npm:pi-lark-notify",
                    "npm:pi-subagents",
                    {"source": "npm:context-mode"},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(driver, "PI_SETTINGS_PATH", global_settings)

    settings = driver._write_authoring_settings(tmp_path / "worktree")
    payload = json.loads(settings.read_text(encoding="utf-8"))

    assert payload["packages"] == ["npm:pi-subagents", {"source": "npm:context-mode"}]
    assert payload["lark-notify"] == {"enabled": False}
    assert payload["retry"]["maxRetries"] == 10
    assert payload["retry"]["provider"]["maxRetries"] == 5


def test_launch_agent_falls_back_after_bounded_transient_provider_retries(
    tmp_path: Path, monkeypatch
) -> None:
    plan = {"batch_id": "go-fallback", "language": "go"}
    task = {"candidate_id": "go-demo", "package": "go-demo"}
    args = _args(
        tmp_path,
        tmp_path / "plan.json",
        tmp_path / "queue.json",
        tmp_path / "state.json",
    )
    args.fallback_provider = "aliyun-qwen-openai-responses"
    args.fallback_model = "qwen3.8-flash"
    args.fallback_thinking = "high"
    calls: list[list[str]] = []
    primary_errors = [
        "too many pending requests",
        "unknown provider for model gpt-5.6-sol",
        "stream_read_error",
    ]

    class FakeProcess:
        def __init__(self, command, **kwargs):
            self.pid = 1000 + len(calls)
            calls.append(command)
            provider = command[command.index("--provider") + 1]
            if provider == args.provider:
                kwargs["stdout"].write(primary_errors[len(calls) - 1] + "\n")
                kwargs["stdout"].flush()
                self.returncode = 1
            else:
                self.returncode = 0

        def wait(self, timeout=None):
            del timeout
            return self.returncode

    monkeypatch.setattr(driver.subprocess, "Popen", FakeProcess)
    monkeypatch.setattr(driver.time, "sleep", lambda _seconds: None)

    result = driver._launch_agent(
        args,
        plan=plan,
        task=task,
        brief_path=tmp_path / "brief.md",
        worktree=tmp_path,
        session_dir=tmp_path / "sessions",
        log_path=tmp_path / "agent.log",
        handoff_path=tmp_path / "handoff.json",
        attempt=1,
    )

    providers = [call[call.index("--provider") + 1] for call in calls]
    models = [call[call.index("--model") + 1] for call in calls]
    assert providers == [args.provider] * 3 + [args.fallback_provider]
    assert models[-1] == args.fallback_model
    assert result["exit_code"] == 0
    assert result["provider"] == args.fallback_provider
    assert result["model"] == args.fallback_model
    assert result["fallback_used"] is True
    assert result["fallback_reason"] == "transient provider retries exhausted"


def test_driver_rejects_tmpfs_worktree_root(tmp_path: Path) -> None:
    del tmp_path
    try:
        driver._ensure_disk_root(Path("/tmp/nl2repo-authoring-test"))
    except ValueError as exc:
        assert "tmpfs" in str(exc)
    else:
        raise AssertionError("tmpfs root was accepted")


def test_driver_default_worktree_root_is_disk_backed() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--worktree-root",
        type=Path,
        default=Path(".nl2repo/authoring-work/worktrees"),
    )
    assert parser.parse_args([]).worktree_root == Path(".nl2repo/authoring-work/worktrees")


def test_production_gate_receipt_requires_oracle_and_all_controls(tmp_path: Path) -> None:
    evidence = tmp_path / ".nl2repo/evidence"
    evidence.mkdir(parents=True)

    def evidence_file(name: str) -> str:
        path = evidence / name
        path.write_text("{}\n", encoding="utf-8")
        return str(path.relative_to(tmp_path))

    compile_manifest = evidence_file("bundle.manifest.json")
    oracle = {
        "valid": True,
        "passed": 1,
        "collected": 1,
        "frozen_total": 1,
        "reward": 1.0,
        "result": evidence_file("oracle-result.json"),
        "grading": evidence_file("oracle-grading.json"),
        "network": evidence_file("oracle-network.json"),
    }
    controls = {}
    for kind in driver.REQUIRED_CONTROL_KINDS:
        controls[kind] = {
            "valid": True,
            "reward": 1.0 if kind == "offline" else 0.0,
            "result": evidence_file(f"{kind}-result.json"),
            "grading": evidence_file(f"{kind}-grading.json"),
            "network": evidence_file(f"{kind}-network.json"),
        }
    controls["offline"]["public_network_available"] = False
    receipt = tmp_path / ".nl2repo/authoring-production-gates.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)

    def write_receipt() -> None:
        receipt.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "task_id": "demo",
                    "status": "controls-passed",
                    "compile": {
                        "status": "passed",
                        "bundle_manifest": compile_manifest,
                    },
                    "oracle": oracle,
                    "controls": controls,
                }
            ),
            encoding="utf-8",
        )

    write_receipt()
    result = driver._run_production_gate_check(tmp_path, "demo")
    assert result["status"] == "passed"

    controls["stub"]["reward"] = 0.1
    write_receipt()
    result = driver._run_production_gate_check(tmp_path, "demo")
    assert result["status"] == "failed"
    assert "control stub reward is not zero" in result["output"]
