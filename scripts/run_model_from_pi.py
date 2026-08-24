#!/usr/bin/env python3
"""Launch one Harbor model cell with a Pi credential held only in memory/env."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import tomllib
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def provider_config(
    models_file: Path,
    provider: str,
    model_id: str,
    *,
    allow_unresolved_credential: bool = False,
) -> tuple[str, str, str]:
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
        if not api_key and not allow_unresolved_credential:
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


def provider_hostname(base_url: str) -> str:
    """Return the exact HTTPS hostname used for the run-scoped allowlist."""

    parsed = urlsplit(base_url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("Pi provider requires an HTTPS URL with a hostname")
    if parsed.username or parsed.password:
        raise ValueError("Pi provider base URL must not contain URL credentials")
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("Pi provider base URL contains an invalid port") from exc
    return parsed.hostname.rstrip(".").lower()


def check_compiled_task_network_policy(task_root: Path) -> None:
    """Reject generated tasks that bypass Harbor's dynamic egress sidecar."""

    task_toml = task_root / "task.toml"
    with task_toml.open("rb") as handle:
        task = tomllib.load(handle)
    environment = task.get("environment")
    mode = environment.get("network_mode") if isinstance(environment, dict) else None
    if mode not in {"no-network", "allowlist"}:
        raise SystemExit(
            f"compiled Harbor task must restrict agent egress, got {mode!r}: {task_toml}"
        )
    compose = task_root / "environment/docker-compose.yaml"
    if compose.is_file() and re.search(
        r"(?m)^\s+(?:network_mode|networks)\s*:",
        compose.read_text(encoding="utf-8"),
    ):
        raise SystemExit(
            "compiled Agent compose declares explicit networking and bypasses "
            f"Harbor's egress sidecar: {compose}"
        )


def provider_runtime_env(api: str, model_id: str) -> dict[str, str]:
    """Return protocol-specific runtime knobs without changing Pi config.

    The Fable relay rejects OpenHands' verbose built-in security policy with a
    ``content_filter`` finish reason. Keep the remaining OpenHands prompt and
    select the concise adapter-owned policy verified against the relay.
    """

    if api == "anthropic-messages" and model_id == "claude-fable-5":
        return {
            "LLM_ANTHROPIC_THINKING_MODE": "adaptive",
            "LLM_OPENHANDS_SECURITY_PROFILE": "fable-relay-safe",
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
        help="Use a compiled Harbor task path instead of catalog/tasks/<task>.",
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
            else ROOT / "catalog/tasks" / task_name
        )
        if task_root.is_symlink():
            raise SystemExit(f"Harbor task path must not be a symlink: {task_root}")
        if not (task_root / "task.toml").is_file():
            raise SystemExit(f"missing Harbor task: {task_root}")
        check_compiled_task_network_policy(task_root)
    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    lock_root = args.lock_root if args.lock_root.is_absolute() else ROOT / args.lock_root
    if run_root.exists():
        raise SystemExit(f"run root already exists: {run_root}")

    api, base_url, configured_key = provider_config(
        args.models_file,
        args.provider,
        args.model_id,
        allow_unresolved_credential=bool(args.credential_env),
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
    provider_host = provider_hostname(base_url)
    environment = os.environ.copy()
    environment.update(
        {
            "TASKS": ",".join(task_names),
            "MODEL": harbor_model,
            "LLM_BASE_URL": base_url,
            "LLM_PROVIDER_HOST": provider_host,
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
