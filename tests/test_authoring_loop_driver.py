from __future__ import annotations

import hashlib
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


def test_driver_launches_direct_pi_and_records_handoff(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(driver, "TMPFS_ROOTS", ())
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {"queue": [{"candidate_id": "python-one", "package": "one", "language": "python"}]}
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
        handoff = Path(kwargs["handoff_path"])
        handoff.write_text('{"status":"awaiting-agent-run"}\n', encoding="utf-8")
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


def _private_artifact(digest: str = "a" * 64) -> dict[str, object]:
    value = f"sha256:{digest}"
    return {
        "digest": value,
        "size_bytes": 1,
        "uri": f"artifact://private/{value}",
        "visibility": "private",
    }


def test_go_authoring_uses_production_toolchain_and_fail_closed_contract(
    tmp_path: Path,
) -> None:
    assert driver._authoring_toolchain(tmp_path, "go") == tmp_path / "toolchain.go.lock.toml"
    assert "go/packages" in driver._language_guidance("go")
    source_root = tmp_path / "catalog/sources/demo"
    compiled = tmp_path / "compiled/demo"
    source_root.mkdir(parents=True)
    compiled.mkdir(parents=True)
    toolchain = driver.SCRIPT_ROOT.parent / "toolchain.go.lock.toml"
    assert driver._go_toolchain_errors(toolchain) == []
    source = {
        "environment": {"status": "known", "runtime_version": "1.26.5"},
        "dependencies": {
            "status": "known",
            "module_bundle": _private_artifact("b" * 64),
        },
        "verifier": {"bundle": _private_artifact("c" * 64)},
        "oracle_bundle": _private_artifact("d" * 64),
    }
    generated_task = compiled / "task.toml"
    generated_task.write_text(
        'schema_version = "1.4"\n\n[metadata]\nlanguage = "go"\npackage_manager = "go-modules"\n',
        encoding="utf-8",
    )
    task_bytes = generated_task.read_bytes()
    (compiled / "bundle.manifest.json").write_text(
        json.dumps(
            {
                "mode": "production",
                "files": [
                    {
                        "path": "task.toml",
                        "sha256": hashlib.sha256(task_bytes).hexdigest(),
                        "size_bytes": len(task_bytes),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    passed = driver._go_production_contract(source_root, source, compiled, toolchain)
    assert passed == {"status": "passed", "errors": []}
    (source_root / "harbor/tests").mkdir(parents=True)
    (source_root / "harbor/tests/contract.sh").write_text("hidden\n", encoding="utf-8")
    failed = driver._go_production_contract(source_root, source, compiled, toolchain)
    assert failed["status"] == "failed"
    assert "public Go source retains private" in failed["errors"][0]


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

    def fake_launch(_args, **kwargs):
        package = Path(kwargs["worktree"]).name
        task_root = Path(kwargs["worktree"]) / f"catalog/sources/{package}"
        task_root.mkdir(parents=True)
        (task_root / "task.toml").write_text("task_id = 'demo'\n", encoding="utf-8")
        (task_root / "instruction.md").write_text("# task\n", encoding="utf-8")
        handoff = Path(kwargs["handoff_path"])
        handoff.write_text('{"status":"awaiting-agent-run"}\n', encoding="utf-8")
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
        handoff.write_text('{"status":"awaiting-agent-run"}\n', encoding="utf-8")
        return {"status": "exited", "exit_code": 0, "log": "log", "handoff": str(handoff)}

    monkeypatch.setattr(driver, "_launch_agent", fake_launch)
    output = driver.run(args)

    assert output["queue_refill"] is False
    assert [item["package"] for item in output["results"]] == ["one"]


def test_remediation_refill_selects_existing_source_and_reclaims_blocked_state(
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
                        "candidate_id": "python-repair",
                        "package": "repair",
                        "language": "python",
                        "status": "existing",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    queue_loop = driver._load_queue_loop()
    queue_loop.command_init(type("Args", (), {"queue": queue, "state": state})())
    with queue_loop.locked_state(state) as payload:
        payload["items"]["python-repair"].update(
            {
                "status": "blocked",
                "reason": "dependency closure missing",
                "failure_class": "environment",
                "attempts": 3,
            }
        )
    sources = tmp_path / "catalog/sources"
    source = sources / "repair"
    source.mkdir(parents=True)
    (source / "instruction.md").write_text("# repair\n", encoding="utf-8")
    (source / "task.toml").write_text(
        'schema_version = "1.0"\n'
        'task_id = "repair"\n'
        'instruction = "instruction.md"\n\n'
        "[lifecycle]\n"
        'status = "blocked"\n'
        'reason = "dependency closure missing"\n',
        encoding="utf-8",
    )
    (source / "production-evidence.json").write_text(
        json.dumps(
            {
                "task_id": "repair",
                "terminal_kind": "blocked",
                "blocked": {
                    "failure_class": "environment",
                    "next_step": "Freeze the dependency lock and rerun offline install.",
                },
            }
        ),
        encoding="utf-8",
    )
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "batch_id": "python-remediation-refill",
                "language": "python",
                "remediation_mode": True,
                "candidate_input_sha256": queue_loop._sha256(queue),
                "tasks": [
                    {
                        "candidate_id": "python-repair",
                        "package": "repair",
                        "source_root": "catalog/sources/repair",
                        "harbor_task_root": "catalog/tasks/repair",
                        "remediation_mode": True,
                        "queue_reclaim_statuses": ["blocked", "complete"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    args = _args(tmp_path, plan, queue, state)
    args.source_root = sources
    args.tasks_root = tmp_path / "catalog/tasks"
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
        task_root = Path(kwargs["worktree"]) / "catalog/sources/repair"
        task_root.mkdir(parents=True, exist_ok=True)
        (task_root / "task.toml").write_text('task_id = "repair"\n', encoding="utf-8")
        (task_root / "instruction.md").write_text("# repaired\n", encoding="utf-8")
        handoff = Path(kwargs["handoff_path"])
        handoff.write_text('{"status":"review-handoff"}\n', encoding="utf-8")
        return {
            "status": "exited",
            "exit_code": 0,
            "log": str(kwargs["log_path"]),
            "handoff": str(handoff),
        }

    monkeypatch.setattr(driver, "_launch_agent", fake_launch)
    output = driver.run(args)

    assert output["remediation_mode"] is True
    assert [(item["package"], item["status"]) for item in output["results"]] == [
        ("repair", "complete")
    ]
    with queue_loop.locked_state(state) as payload:
        record = payload["items"]["python-repair"]
        assert record["status"] == "complete"
        assert record["attempts"] == 1
        assert record["reopen_history"][0]["status"] == "blocked"


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
