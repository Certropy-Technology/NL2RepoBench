from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _load_script():
    path = SCRIPTS / "run_dual_model_queue.py"
    spec = importlib.util.spec_from_file_location("run_dual_model_queue", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


dual = _load_script()


def _models(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "providers": {
                    "z-open-api-gpt-openai-responses": {
                        "api": "openai-responses",
                        "baseUrl": "https://example.invalid/v1",
                        "apiKey": "${TEST_MODEL_KEY}",
                        "models": [{"id": "gpt-5.6-sol"}],
                    },
                    "z-open-api-fabel5": {
                        "api": "anthropic-messages",
                        "baseUrl": "https://example.invalid/v1",
                        "apiKey": "${TEST_MODEL_KEY}",
                        "models": [{"id": "claude-fable-5"}],
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    path.chmod(0o600)


def test_dual_plan_resolves_both_pi_providers_without_serializing_keys(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("TEST_MODEL_KEY", "test-key-not-written-to-plan")
    models = tmp_path / "models.json"
    _models(models)
    campaign = tmp_path / "campaign.json"
    campaign.write_text(
        json.dumps(
            {
                "campaign_id": "pilot",
                "tasks": [{"task_id": "demo"}, {"task_id": "second"}],
            }
        ),
        encoding="utf-8",
    )

    plan = dual.build_plan(
        campaign,
        run_root=tmp_path / "runs",
        lock_root=tmp_path / "locks",
        models_file=models,
    )

    assert plan["task_count"] == 2
    assert {item["model_id"] for item in plan["models"]} == {
        "gpt-5.6-sol",
        "claude-fable-5",
    }
    assert all(item["concurrency"] == 2 for item in plan["models"])
    assert plan["max_total_concurrency"] == 4
    by_model = {item["model_id"]: item for item in plan["models"]}
    assert by_model["claude-fable-5"]["provider"] == "z-open-api-fabel5"
    assert by_model["claude-fable-5"]["credential_env"] is None
    assert by_model["claude-fable-5"]["api"] == "openai-completions"
    assert by_model["claude-fable-5"]["base_url"].endswith("/v1")
    assert by_model["claude-fable-5"]["harbor_model"] == "openai/claude-fable-5"
    assert "test-key-not-written-to-plan" not in json.dumps(plan)


def test_dual_plan_allows_fable_provider_env_override_without_old_env(
    tmp_path: Path, monkeypatch
) -> None:
    models = tmp_path / "models.json"
    models.write_text(
        json.dumps(
            {
                "providers": {
                    "z-open-api-gpt-openai-responses": {
                        "api": "openai-responses",
                        "baseUrl": "https://example.invalid/v1",
                        "apiKey": "gpt-key",
                        "models": [{"id": "gpt-5.6-sol"}],
                    },
                    "z-open-api-fabel5": {
                        "api": "anthropic-messages",
                        "baseUrl": "https://example.invalid",
                        "apiKey": "${TEST_MODEL_KEY}",
                        "models": [{"id": "claude-fable-5"}],
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    models.chmod(0o600)
    monkeypatch.setenv("TEST_MODEL_KEY", "test-key-not-written-to-plan")
    campaign = tmp_path / "campaign.json"
    campaign.write_text(
        json.dumps({"campaign_id": "pilot", "tasks": [{"task_id": "demo"}]}),
        encoding="utf-8",
    )

    plan = dual.build_plan(
        campaign,
        run_root=tmp_path / "runs",
        lock_root=tmp_path / "locks",
        models_file=models,
    )

    assert len(plan["models"]) == 2


def test_dual_queue_invocation_keeps_credentials_out_of_argv(tmp_path: Path, monkeypatch) -> None:
    calls: list[list[str]] = []

    class Result:
        returncode = 0

    def fake_run(command, **kwargs):
        calls.append(command)
        assert "LLM_API_KEY" not in command
        del kwargs
        return Result()

    monkeypatch.setattr(dual.subprocess, "run", fake_run)
    queue = {
        "provider": "z-open-api-gpt-openai-responses",
        "model_id": "gpt-5.6-sol",
        "harbor_model": "openai/gpt-5.6-sol",
        "run_prefix": "gpt56",
        "run_root": str(tmp_path / "runs"),
        "lock_root": str(tmp_path / "locks"),
        "tasks": ["demo"],
    }
    models = tmp_path / "models.json"
    models.write_text("{}", encoding="utf-8")

    result = dual._run_queue(queue, models)

    assert result["status"] == "completed"
    assert calls
    assert "--models-file" in calls[0]
    assert "--credential-env" not in calls[0]
    assert all("test-key" not in value for value in calls[0])


def test_fable_queue_uses_explicit_credential_environment(
    tmp_path: Path, monkeypatch
) -> None:
    calls: list[list[str]] = []

    class Result:
        returncode = 0

    def fake_run(command, **kwargs):
        calls.append(command)
        del kwargs
        return Result()

    monkeypatch.setattr(dual.subprocess, "run", fake_run)
    queue = {
        "provider": "z-open-api-fabel5",
        "model_id": "claude-fable-5",
        "harbor_model": "openai/claude-fable-5",
        "run_prefix": "fable",
        "run_root": str(tmp_path / "runs"),
        "lock_root": str(tmp_path / "locks"),
        "tasks": ["demo"],
    }
    models = tmp_path / "models.json"
    models.write_text("{}", encoding="utf-8")

    result = dual._run_queue(queue, models)

    assert result["status"] == "completed"
    assert calls
    assert "--credential-env" not in calls[0]


def test_dual_plan_skips_only_oss_backed_existing_runs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("TEST_MODEL_KEY", "test-key-not-written-to-plan")
    models = tmp_path / "models.json"
    _models(models)
    campaign = tmp_path / "campaign.json"
    campaign.write_text(
        json.dumps({"campaign_id": "pilot", "tasks": [{"task_id": "demo"}]}),
        encoding="utf-8",
    )
    inventory = tmp_path / "oss-runs.json"
    inventory.write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "model": "gpt-5.6-sol",
                        "task_id": "demo",
                        "source": "oss",
                        "status": "completed",
                        "evidence_keys": ["nl2repobench/runs/gpt-5.6-sol/demo/trial/result.json"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    plan = dual.build_plan(
        campaign,
        run_root=tmp_path / "runs",
        lock_root=tmp_path / "locks",
        models_file=models,
        existing_inventory=inventory,
    )

    by_model = {model["model_id"]: model for model in plan["models"]}
    assert by_model["gpt-5.6-sol"]["tasks"] == []
    assert by_model["gpt-5.6-sol"]["skipped_existing_tasks"] == ["demo"]
    assert by_model["claude-fable-5"]["tasks"] == []
    assert by_model["claude-fable-5"]["skipped_existing_tasks"] == ["demo"]
