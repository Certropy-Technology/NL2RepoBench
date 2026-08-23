#!/usr/bin/env python3
"""Plan and execute one serial Harbor queue per approved model."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from run_model_from_pi import normalize_harbor_model, provider_config

SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    model_id: str
    harbor_model: str
    run_prefix: str


MODEL_SPECS = (
    ModelSpec(
        provider="z-open-api-gpt-openai-responses",
        model_id="gpt-5.6-sol",
        harbor_model="openai/gpt-5.6-sol",
        run_prefix="gpt56",
    ),
    ModelSpec(
        provider="z-open-api-fabel5",
        model_id="claude-fable-5",
        harbor_model="anthropic/claude-fable-5",
        run_prefix="fable",
    ),
)


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
) -> dict[str, Any]:
    tasks = campaign_tasks(campaign_path)
    _, refs_by_task = existing_model_runs(existing_inventory)
    existing_tasks = set(refs_by_task)
    campaign = _json(campaign_path)
    campaign_id = campaign.get("campaign_id") or campaign_path.stem
    if not isinstance(campaign_id, str) or SAFE_NAME.fullmatch(campaign_id) is None:
        raise ValueError("campaign_id must be a safe name")
    queues: list[dict[str, Any]] = []
    for spec in MODEL_SPECS:
        api, _, _ = provider_config(models_file, spec.provider, spec.model_id)
        missing_tasks = [task for task in tasks if task not in existing_tasks]
        queues.append(
            {
                **asdict(spec),
                "api": api,
                "harbor_model": normalize_harbor_model(api, spec.harbor_model),
                "tasks": missing_tasks,
                "skipped_existing_tasks": sorted(set(tasks) - set(missing_tasks)),
                "run_root": str((run_root / spec.run_prefix).resolve()),
                "lock_root": str((lock_root / spec.run_prefix).resolve()),
                "retry_policy": "infrastructure-only",
                "concurrency": 1,
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
        "skipped_existing_tasks": sorted(existing_tasks.intersection(tasks)),
        "existing_oss_runs": {
            task: refs_by_task[task] for task in sorted(existing_tasks.intersection(tasks))
        },
        "models": queues,
        "credential_policy": "Pi provider config only; no key in plan or argv",
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
        "1",
        "--models-file",
        str(models_file),
    ]
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
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        plan = build_plan(
            args.campaign,
            run_root=args.run_root,
            lock_root=args.lock_root,
            models_file=args.models_file,
            existing_inventory=args.existing_inventory,
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
