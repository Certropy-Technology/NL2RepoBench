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


def provider_config(models_file: Path, provider: str, model_id: str) -> tuple[str, str, str]:
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
    api = record.get("api")
    api_key = record.get("apiKey")
    if api not in {"anthropic-messages", "openai-completions", "openai-responses"}:
        raise ValueError(f"unsupported Pi provider API: {api!r}")
    if not isinstance(base_url, str) or not base_url.startswith("https://"):
        raise ValueError("Pi provider requires an HTTPS baseUrl")
    if not isinstance(api_key, str) or not api_key or api_key.startswith("!"):
        raise ValueError("Pi provider requires a literal in-memory credential source")
    if api_key.startswith("$"):
        match = re.fullmatch(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?", api_key)
        if match is None:
            raise ValueError("Pi apiKey environment reference is malformed")
        api_key = os.environ.get(match.group(1), "")
        if not api_key:
            raise ValueError(f"Pi credential environment variable is empty: {match.group(1)}")
    return api, base_url, api_key


def provider_credentials(models_file: Path, provider: str, model_id: str) -> tuple[str, str]:
    """Return base URL and key while preserving the small test/helper API."""

    _, base_url, api_key = provider_config(models_file, provider, model_id)
    return base_url, api_key


def normalize_harbor_model(api: str, harbor_model: str) -> str:
    """Align LiteLLM's provider prefix with the selected Pi API protocol."""

    if api == "anthropic-messages":
        if harbor_model.startswith("openai/"):
            return "anthropic/" + harbor_model.removeprefix("openai/")
        if not harbor_model.startswith("anthropic/"):
            return "anthropic/" + harbor_model
    return harbor_model


def provider_runtime_env(api: str, model_id: str) -> dict[str, str]:
    """Return protocol-specific runtime knobs without changing Pi config.

    The relay's Anthropic ``thinking=enabled`` path can emit empty tool input
    for Fable.  Fable's supported adaptive-thinking path preserves the tool
    schema, so keep this workaround explicit and model-scoped.
    """

    if api == "anthropic-messages" and model_id == "claude-fable-5":
        return {
            "LLM_ANTHROPIC_THINKING_MODE": "adaptive",
            "LLM_ANTHROPIC_NATIVE_TOOLS": "0",
        }
    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--harbor-model", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument(
        "--harbor-task-path",
        type=Path,
        help="Use a compiled Harbor task path instead of catalog/tasks/<task>/harbor.",
    )
    parser.add_argument(
        "--harbor-task-root",
        type=Path,
        help="Resolve each task as <root>/<task-id> for a compiled batch.",
    )
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--run-prefix", required=True)
    parser.add_argument("--lock-root", type=Path, required=True)
    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Bounded concurrent Harbor trials (default: 2).",
    )
    parser.add_argument(
        "--credential-env",
        help="Use this already-exported environment variable instead of the Pi literal key.",
    )
    parser.add_argument("--base-url", help="Override the provider base URL without storing it.")
    parser.add_argument(
        "--models-file",
        type=Path,
        default=Path.home() / ".pi/agent/models.json",
    )
    args = parser.parse_args()

    if args.harbor_task_path is not None and args.harbor_task_root is not None:
        raise SystemExit("use only one of --harbor-task-path and --harbor-task-root")

    if not 1 <= args.concurrency <= 8:
        raise SystemExit("--concurrency must be between 1 and 8")

    task_names = [item.strip() for item in args.task.split(",") if item.strip()]
    if not task_names:
        raise SystemExit("--task must contain at least one task ID")
    for label, value in {
        "run prefix": args.run_prefix,
        "model ID": args.model_id,
    }.items():
        if not SAFE_NAME.fullmatch(value):
            raise SystemExit(f"unsafe {label}: {value!r}")
    for task_name in task_names:
        if not SAFE_NAME.fullmatch(task_name):
            raise SystemExit(f"unsafe task: {task_name!r}")
        task_root = (
            args.harbor_task_path.resolve()
            if args.harbor_task_path is not None
            else (args.harbor_task_root.resolve() / task_name)
            if args.harbor_task_root is not None
            else ROOT / "catalog/tasks" / task_name / "harbor"
        )
        if task_root.is_symlink():
            raise SystemExit(f"Harbor task path must not be a symlink: {task_root}")
        if not (task_root / "task.toml").is_file():
            raise SystemExit(f"missing Harbor task: {task_root}")
    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    lock_root = args.lock_root if args.lock_root.is_absolute() else ROOT / args.lock_root
    if run_root.exists():
        raise SystemExit(f"run root already exists: {run_root}")

    api, base_url, configured_key = provider_config(
        args.models_file, args.provider, args.model_id
    )
    harbor_model = normalize_harbor_model(api, args.harbor_model)
    api_key = configured_key
    if args.credential_env:
        if not SAFE_NAME.fullmatch(args.credential_env):
            raise SystemExit(f"unsafe credential environment name: {args.credential_env!r}")
        api_key = os.environ.get(args.credential_env, "")
        if not api_key:
            raise SystemExit(f"credential environment variable is empty: {args.credential_env}")
    if args.base_url:
        if not args.base_url.startswith("https://"):
            raise SystemExit("--base-url must use HTTPS")
        base_url = args.base_url
    environment = os.environ.copy()
    environment.update(
        {
            "TASKS": ",".join(task_names),
            "MODEL": harbor_model,
            "LLM_BASE_URL": base_url,
            "LLM_API_KEY": api_key,
            "RUN_ROOT": str(run_root),
            "HARBOR_TASK_PATH": str(args.harbor_task_path.resolve())
            if args.harbor_task_path is not None
            else "",
            "HARBOR_TASK_ROOT": str(args.harbor_task_root.resolve())
            if args.harbor_task_root is not None
            else "",
            "RUN_PREFIX": args.run_prefix,
            "LOCK_ROOT": str(lock_root),
            "MAX_CONCURRENCY": str(args.concurrency),
            "AGENT_TIMEOUT_SECONDS": "18000",
            "AGENT_SETUP_TIMEOUT_MULTIPLIER": "3",
            "REASONING_EFFORT": "max",
            "MAX_RETRIES": "3",
            "LLM_NUM_RETRIES": "10",
            "LLM_TIMEOUT": "600",
            "LLM_RETRY_MIN_WAIT": "8",
            "LLM_RETRY_MAX_WAIT": "120",
        }
    )
    environment.update(provider_runtime_env(api, args.model_id))
    print(f"launch task={args.task} model={harbor_model} run_root={run_root}")
    completed = subprocess.run(
        [str(ROOT / "scripts/run_model_queue.sh")],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
