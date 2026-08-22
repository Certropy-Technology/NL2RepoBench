#!/usr/bin/env python3
"""Launch one Harbor model cell with a Pi credential held only in memory/env."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def provider_credentials(models_file: Path, provider: str, model_id: str) -> tuple[str, str]:
    mode = stat.S_IMODE(models_file.stat().st_mode)
    if mode & 0o077:
        raise ValueError(f"Pi models file must not be group/world accessible: mode {mode:o}")
    payload: dict[str, Any] = json.loads(models_file.read_text(encoding="utf-8"))
    providers = payload.get("providers", payload)
    record = providers.get(provider) if isinstance(providers, dict) else None
    if not isinstance(record, dict):
        raise ValueError(f"Pi provider is not configured: {provider}")
    models = record.get("models")
    model_ids = {
        item.get("id")
        for item in models
        if isinstance(models, list) and isinstance(item, dict)
    }
    if model_id not in model_ids:
        raise ValueError(f"Pi model {model_id!r} is not configured under {provider!r}")
    base_url = record.get("baseUrl")
    api_key = record.get("apiKey")
    if not isinstance(base_url, str) or not base_url.startswith("https://"):
        raise ValueError("Pi provider requires an HTTPS baseUrl")
    if not isinstance(api_key, str) or not api_key or api_key.startswith("!"):
        raise ValueError("Pi provider requires a literal in-memory credential source")
    return base_url, api_key


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--harbor-model", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--run-prefix", required=True)
    parser.add_argument("--lock-root", type=Path, required=True)
    parser.add_argument(
        "--models-file",
        type=Path,
        default=Path.home() / ".pi/agent/models.json",
    )
    args = parser.parse_args()

    for label, value in {
        "task": args.task,
        "run prefix": args.run_prefix,
        "model ID": args.model_id,
    }.items():
        if not SAFE_NAME.fullmatch(value):
            raise SystemExit(f"unsafe {label}: {value!r}")
    task_root = ROOT / "catalog/tasks" / args.task / "harbor"
    if not (task_root / "task.toml").is_file():
        raise SystemExit(f"missing Harbor task: {task_root}")
    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    lock_root = args.lock_root if args.lock_root.is_absolute() else ROOT / args.lock_root
    if run_root.exists():
        raise SystemExit(f"run root already exists: {run_root}")

    base_url, api_key = provider_credentials(args.models_file, args.provider, args.model_id)
    environment = os.environ.copy()
    environment.update(
        {
            "TASKS": args.task,
            "MODEL": args.harbor_model,
            "LLM_BASE_URL": base_url,
            "LLM_API_KEY": api_key,
            "RUN_ROOT": str(run_root),
            "RUN_PREFIX": args.run_prefix,
            "LOCK_ROOT": str(lock_root),
            "AGENT_TIMEOUT_SECONDS": "18000",
            "REASONING_EFFORT": "max",
            "MAX_RETRIES": "3",
            "LLM_NUM_RETRIES": "10",
            "LLM_TIMEOUT": "600",
            "LLM_RETRY_MIN_WAIT": "8",
            "LLM_RETRY_MAX_WAIT": "120",
        }
    )
    print(f"launch task={args.task} model={args.harbor_model} run_root={run_root}")
    completed = subprocess.run(
        [str(ROOT / "scripts/run_model_queue.sh")],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
