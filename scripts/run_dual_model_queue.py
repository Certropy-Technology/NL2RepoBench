#!/usr/bin/env python3
"""Plan and execute one serial Harbor queue per approved model."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from run_model_from_pi import provider_config, runtime_provider_config

SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")
RUNNABLE_LIFECYCLES = frozenset({"oracle-passed", "controls-passed", "reviewed", "piloted", "published"})


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    model_id: str
    harbor_model: str
    run_prefix: str
    credential_env: str | None = None


GPT_SPEC = ModelSpec(
    provider="z-open-api-gpt-openai-responses",
    model_id="gpt-5.6-sol",
    harbor_model="openai/gpt-5.6-sol",
    run_prefix="gpt56",
)

FABLE_SPEC = ModelSpec(
    provider="z-open-api-fabel5",
    model_id="claude-fable-5",
    harbor_model="anthropic/claude-fable-5",
    run_prefix="fable",
)

OPUS_SPEC = ModelSpec(
    provider="z-open-api-claude-anthropic-messages",
    model_id="claude-opus-5",
    harbor_model="anthropic/claude-opus-5",
    run_prefix="opus5",
)

MODEL_SETS = {
    "fable": (GPT_SPEC, FABLE_SPEC),
    "opus": (GPT_SPEC, OPUS_SPEC),
}

# Backward-compatible default for programmatic callers and the historical
# GPT/Fable campaign tests.
MODEL_SPECS = MODEL_SETS["fable"]


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid campaign JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"campaign JSON root must be an object: {path}")
    return value


def campaign_tasks(path: Path) -> tuple[str, ...]:
    payload = _json(path)
    raw_tasks = payload.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise ValueError("campaign.tasks must be a non-empty list")
    task_ids: list[str] = []
    for raw in raw_tasks:
        task_id = raw.get("task_id") if isinstance(raw, dict) else raw
        if not isinstance(task_id, str) or SAFE_NAME.fullmatch(task_id) is None:
            raise ValueError(f"unsafe or missing campaign task_id: {task_id!r}")
        task_ids.append(task_id)
    if len(set(task_ids)) != len(task_ids):
        raise ValueError("campaign task IDs must be unique")
    return tuple(task_ids)


def validate_runnable_tasks(
    tasks: tuple[str, ...], *, harbor_task_root: Path | None = None
) -> None:
    root = Path(__file__).parents[1]
    source_root = root / "catalog/sources"
    task_root = harbor_task_root or root / "catalog/tasks"
    for task_id in tasks:
        source_toml = source_root / task_id / "task.toml"
        runtime_toml = task_root / task_id / "task.toml"
        if not source_toml.is_file() or not runtime_toml.is_file():
            raise ValueError(f"task is not materialized for model execution: {task_id}")
        with source_toml.open("rb") as stream:
            source = tomllib.load(stream)
        lifecycle = source.get("lifecycle")
        status = lifecycle.get("status") if isinstance(lifecycle, dict) else None
        if status not in RUNNABLE_LIFECYCLES:
            raise ValueError(
                f"task lifecycle is not runnable for model execution: {task_id}={status!r}"
            )


def existing_model_runs(
    path: Path | None,
) -> tuple[dict[str, set[str]], dict[str, list[dict[str, Any]]]]:
    """Load a trusted OSS run inventory keyed by model and task."""

    if path is None:
        return {}, {}
    payload = _json(path)
    raw_runs = payload.get("runs")
    if not isinstance(raw_runs, list):
        raise ValueError("existing run inventory requires a runs list")
    result: dict[str, set[str]] = {}
    refs_by_task: dict[str, list[dict[str, Any]]] = {}
    for raw in raw_runs:
        if not isinstance(raw, dict):
            raise ValueError("existing run inventory entries must be objects")
        model = raw.get("model")
        task_id = raw.get("task_id")
        if not isinstance(model, str) or not isinstance(task_id, str):
            raise ValueError("existing run inventory requires model and task_id")
        if raw.get("source") != "oss":
            raise ValueError(f"existing run is not OSS-backed: {model}/{task_id}")
        if raw.get("status") not in {"completed", "errored"}:
            raise ValueError(f"existing run is not a finished trial: {model}/{task_id}")
        evidence_keys = raw.get("evidence_keys")
        if not isinstance(evidence_keys, list) or not any(
            isinstance(key, str) and key.endswith("result.json") for key in evidence_keys
        ):
            raise ValueError(f"existing run lacks result evidence: {model}/{task_id}")
        result.setdefault(model, set()).add(task_id)
        refs_by_task.setdefault(task_id, []).append(raw)
    return result, refs_by_task


def build_plan(
    campaign_path: Path,
    *,
    run_root: Path,
    lock_root: Path,
    models_file: Path,
    existing_inventory: Path | None = None,
    per_model_concurrency: int = 1,
    harbor_task_root: Path | None = None,
    model_specs: tuple[ModelSpec, ...] = MODEL_SPECS,
    agent_timeout_seconds: int = 18000,
) -> dict[str, Any]:
    if not 1 <= per_model_concurrency <= 4:
        raise ValueError("per_model_concurrency must be between 1 and 4")
    if agent_timeout_seconds < 1:
        raise ValueError("agent_timeout_seconds must be positive")
    tasks = campaign_tasks(campaign_path)
    validate_runnable_tasks(tasks, harbor_task_root=harbor_task_root)
    existing_by_model, refs_by_task = existing_model_runs(existing_inventory)
    campaign = _json(campaign_path)
    campaign_id = campaign.get("campaign_id") or campaign_path.stem
    if not isinstance(campaign_id, str) or SAFE_NAME.fullmatch(campaign_id) is None:
        raise ValueError("campaign_id must be a safe name")
    queues: list[dict[str, Any]] = []
    for spec in model_specs:
        api, base_url, _ = provider_config(
            models_file,
            spec.provider,
            spec.model_id,
            allow_unresolved_credential=bool(spec.credential_env),
        )
        runtime_api, runtime_base_url, runtime_model = runtime_provider_config(
            spec.provider,
            api,
            base_url,
            spec.model_id,
            spec.harbor_model,
        )
        existing_for_model = existing_by_model.get(spec.model_id, set())
        missing_tasks = [task for task in tasks if task not in existing_for_model]
        campaign_run_prefix = f"{spec.run_prefix}-{campaign_id}"
        if SAFE_NAME.fullmatch(campaign_run_prefix) is None:
            raise ValueError("campaign-specific run prefix is unsafe")
        queues.append(
            {
                **asdict(spec),
                "run_prefix": campaign_run_prefix,
                "api": runtime_api,
                "base_url": runtime_base_url,
                "harbor_model": runtime_model,
                "tasks": missing_tasks,
                "skipped_existing_tasks": sorted(existing_for_model.intersection(tasks)),
                "run_root": str((run_root / spec.run_prefix).resolve()),
                "lock_root": str((lock_root / spec.run_prefix).resolve()),
                "agent_timeout_seconds": agent_timeout_seconds,
                "retry_policy": "infrastructure-only",
                "concurrency": per_model_concurrency,
                "harbor_task_root": str(harbor_task_root.resolve())
                if harbor_task_root is not None
                else None,
            }
        )
    return {
        "schema_version": "1.0",
        "campaign_id": campaign_id,
        "campaign_sha256": "sha256:" + hashlib.sha256(campaign_path.read_bytes()).hexdigest(),
        "task_count": len(tasks),
        "tasks": list(tasks),
        "existing_inventory": str(existing_inventory) if existing_inventory else None,
        "existing_inventory_sha256": (
            "sha256:" + hashlib.sha256(existing_inventory.read_bytes()).hexdigest()
            if existing_inventory
            else None
        ),
        "skipped_existing_tasks": sorted(
            task
            for task in tasks
            if all(task in existing_by_model.get(spec.model_id, set()) for spec in model_specs)
        ),
        "existing_oss_runs": {
            task: [
                row
                for row in refs_by_task[task]
                if row.get("model") in {spec.model_id for spec in model_specs}
            ]
            for task in sorted(set(refs_by_task).intersection(tasks))
        },
        "models": queues,
        "credential_policy": "Pi provider config only; no key in plan or argv",
        "per_model_concurrency": per_model_concurrency,
        "agent_timeout_seconds": agent_timeout_seconds,
        "max_total_concurrency": per_model_concurrency * len(model_specs),
    }


def _run_queue(queue: dict[str, Any], models_file: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(Path(__file__).with_name("run_model_from_pi.py")),
        "--provider",
        queue["provider"],
        "--model-id",
        queue["model_id"],
        "--harbor-model",
        queue["harbor_model"],
        "--task",
        ",".join(queue["tasks"]),
        "--run-root",
        queue["run_root"],
        "--run-prefix",
        queue["run_prefix"],
        "--lock-root",
        queue["lock_root"],
        "--concurrency",
        str(queue.get("concurrency", 1)),
        "--agent-timeout-seconds",
        str(queue.get("agent_timeout_seconds", 18000)),
        "--models-file",
        str(models_file),
    ]
    if queue.get("harbor_task_root"):
        command.extend(["--harbor-task-root", queue["harbor_task_root"]])
    if queue.get("credential_env"):
        command.extend(["--credential-env", queue["credential_env"]])
    completed = subprocess.run(command, cwd=Path(__file__).parents[1], check=False)
    return {
        "model": queue["model_id"],
        "provider": queue["provider"],
        "run_root": queue["run_root"],
        "exit_code": completed.returncode,
        "status": "completed" if completed.returncode == 0 else "failed",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--lock-root", type=Path, required=True)
    parser.add_argument("--plan-output", type=Path, required=True)
    parser.add_argument(
        "--models-file", type=Path, default=Path.home() / ".pi/agent/models.json"
    )
    parser.add_argument(
        "--existing-inventory",
        type=Path,
        help="Trusted JSON inventory of OSS runs to skip; entries must declare source=oss.",
    )
    parser.add_argument("--per-model-concurrency", type=int, default=1)
    parser.add_argument("--agent-timeout-seconds", type=int, default=14400)
    parser.add_argument("--harbor-task-root", type=Path)
    parser.add_argument(
        "--second-model",
        choices=sorted(MODEL_SETS),
        default="fable",
        help="Run GPT-5.6 Sol with either Claude Fable 5 or Claude Opus 5.",
    )
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        plan = build_plan(
            args.campaign,
            run_root=args.run_root,
            lock_root=args.lock_root,
            models_file=args.models_file,
            existing_inventory=args.existing_inventory,
            per_model_concurrency=args.per_model_concurrency,
            harbor_task_root=args.harbor_task_root,
            model_specs=MODEL_SETS[args.second_model],
            agent_timeout_seconds=args.agent_timeout_seconds,
        )
    except (OSError, ValueError) as exc:
        print(f"dual model plan failed: {exc}", file=sys.stderr)
        return 2
    args.plan_output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(args.plan_output, plan)
    if not args.execute:
        print(json.dumps({"plan": str(args.plan_output), "execute": False}, sort_keys=True))
        return 0

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=len(plan["models"])) as pool:
        futures = {
            pool.submit(_run_queue, queue, args.models_file): queue["model_id"]
            for queue in plan["models"]
            if queue["tasks"]
        }
        for future in as_completed(futures):
            model_id = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001 - persist per-model failure
                result = {
                    "model": model_id,
                    "provider": next(
                        item["provider"] for item in plan["models"] if item["model_id"] == model_id
                    ),
                    "exit_code": None,
                    "status": "failed",
                    "failure_class": "infrastructure",
                    "failure_reason": type(exc).__name__,
                }
            results.append(result)
            plan["results"] = sorted(results, key=lambda item: item["model"])
            plan["execute"] = True
            _write_json(args.plan_output, plan)
    results.sort(key=lambda item: item["model"])
    print(json.dumps({"plan": str(args.plan_output), "results": results}, sort_keys=True))
    return 0 if all(result["exit_code"] == 0 for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
