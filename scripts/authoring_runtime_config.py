#!/usr/bin/env python3
"""Inspect or atomically update live authoring runtime controls."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

MAX_CONTROLLERS = 8
MAX_CONCURRENCY = 4
MAX_INTEGRATIONS = 3
DEFAULTS: dict[str, Any] = {
    "schema_version": "1.0",
    "enabled": True,
    "max_total_controllers": 3,
    "controller_concurrency": 1,
    "max_integrations": 1,
    "agent_limit": None,
}


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return dict(DEFAULTS)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("runtime config must be a JSON object")
    result = dict(DEFAULTS)
    result.update(value)
    if result.get("schema_version") != "1.0":
        raise ValueError("schema_version must be 1.0")
    if not isinstance(result.get("enabled"), bool):
        raise ValueError("enabled must be boolean")
    for key, upper in (
        ("max_total_controllers", MAX_CONTROLLERS),
        ("controller_concurrency", MAX_CONCURRENCY),
        ("max_integrations", MAX_INTEGRATIONS),
        ("agent_limit", MAX_CONTROLLERS),
    ):
        value = result.get(key)
        if value is None and key == "agent_limit":
            continue
        if not isinstance(value, int) or not 0 <= value <= upper:
            raise ValueError(f"{key} must be an integer between 0 and {upper}")
    return {
        "schema_version": "1.0",
        "enabled": result["enabled"],
        "max_total_controllers": result["max_total_controllers"],
        "controller_concurrency": result["controller_concurrency"],
        "max_integrations": result["max_integrations"],
        "agent_limit": result["agent_limit"],
    }


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(".nl2repo/authoring-live/supervisor/runtime-config.json"),
    )
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("show")
    update = sub.add_parser("set")
    update.add_argument("--enabled", choices=("true", "false"))
    update.add_argument("--max-total-controllers", type=int)
    update.add_argument("--controller-concurrency", type=int)
    update.add_argument("--max-integrations", type=int)
    update.add_argument("--agent-limit", type=int)
    args = parser.parse_args()
    try:
        value = _load(args.path)
        if args.action == "set":
            for option, key in (
                ("enabled", "enabled"),
                ("max_total_controllers", "max_total_controllers"),
                ("controller_concurrency", "controller_concurrency"),
                ("max_integrations", "max_integrations"),
                ("agent_limit", "agent_limit"),
            ):
                selected = getattr(args, option)
                if selected is not None:
                    if option == "enabled":
                        selected = selected == "true"
                    value[key] = selected
            value = _load_value(value)
            _write(args.path, value)
        print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"runtime config update failed: {exc}")
        return 1


def _load_value(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(DEFAULTS)
    result.update(value)
    if result.get("schema_version") != "1.0":
        raise ValueError("schema_version must be 1.0")
    if not isinstance(result.get("enabled"), bool):
        raise ValueError("enabled must be boolean")
    for key, upper in (
        ("max_total_controllers", MAX_CONTROLLERS),
        ("controller_concurrency", MAX_CONCURRENCY),
        ("max_integrations", MAX_INTEGRATIONS),
        ("agent_limit", MAX_CONTROLLERS),
    ):
        selected = result.get(key)
        if selected is None and key == "agent_limit":
            continue
        if not isinstance(selected, int) or not 0 <= selected <= upper:
            raise ValueError(f"{key} must be an integer between 0 and {upper}")
    return {
        "schema_version": "1.0",
        "enabled": result["enabled"],
        "max_total_controllers": result["max_total_controllers"],
        "controller_concurrency": result["controller_concurrency"],
        "max_integrations": result["max_integrations"],
        "agent_limit": result["agent_limit"],
    }


if __name__ == "__main__":
    raise SystemExit(main())
