#!/usr/bin/env python3
"""Fail closed when a Harbor agent task can reach arbitrary source hosts.

This is a publication/run preflight, not a replacement for Harbor's egress
sidecar. Production tasks must use no-network with preloaded dependencies, or
an exact hostname allowlist that does not include GitHub source endpoints.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

SAFE_HOST = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
)
BLOCKED_SUFFIXES = (
    "github.com",
    "githubusercontent.com",
    "githubassets.com",
    "gitlab.com",
    "bitbucket.org",
    "codeberg.org",
    "sourceforge.net",
)


def _toml(path: Path) -> dict[str, Any]:
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"invalid TOML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"TOML root must be an object: {path}")
    return value


def _hosts(table: dict[str, Any], *, field: str) -> list[str]:
    value = table.get(field, [])
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of hostnames")
    return [item.strip().lower().rstrip(".") for item in value]


def _check_policy(
    errors: list[str], *, label: str, mode: Any, allowed_hosts: list[str]
) -> None:
    if mode not in {"no-network", "allowlist", "public"}:
        errors.append(f"{label}: network mode must be no-network, got {mode!r}")
        return
    if mode != "no-network":
        errors.append(
            f"{label}: task baseline must be no-network; use run-scoped "
            "--allow-agent-host for Oracle or the LLM Provider"
        )
    if allowed_hosts:
        errors.append(
            f"{label}: static allowed_hosts are forbidden; use a run-scoped "
            "--allow-agent-host override"
        )
    if mode == "no-network":
        return
    for host in allowed_hosts:
        if host.startswith("*."):
            errors.append(f"{label}: wildcard host is forbidden: {host}")
            continue
        if "://" in host or "/" in host or ":" in host:
            errors.append(f"{label}: host must not contain URL/path/port syntax: {host}")
            continue
        if not SAFE_HOST.fullmatch(host):
            errors.append(f"{label}: invalid exact hostname: {host}")
            continue
        if any(host == suffix or host.endswith(f".{suffix}") for suffix in BLOCKED_SUFFIXES):
            errors.append(f"{label}: source-host domain is forbidden: {host}")


def check_task(root: Path) -> dict[str, Any]:
    root = root.resolve()
    source_path = root / "task.toml"
    harbor_path = root / "harbor/task.toml"
    compiled_path: Path | None = None
    source = _toml(source_path) if source_path.is_file() else {}
    if harbor_path.is_file():
        compiled_path = harbor_path
    elif source_path.is_file() and (
        "environment" in source or "verifier" in source or "agent" in source
    ):
        compiled_path = source_path
    if compiled_path is None:
        raise ValueError(f"missing task.toml or harbor/task.toml under {root}")

    errors: list[str] = []
    policies: list[dict[str, Any]] = []

    harbor = source.get("harbor")
    if isinstance(harbor, dict):
        source_hosts = _hosts(harbor, field="agent_allowed_hosts")
        _check_policy(
            errors,
            label=f"{source_path} [harbor]",
            mode=harbor.get("agent_network_mode"),
            allowed_hosts=source_hosts,
        )
        policies.append(
            {
                "path": str(source_path),
                "section": "harbor",
                "mode": harbor.get("agent_network_mode"),
                "allowed_hosts": source_hosts,
            }
        )

    compiled = _toml(compiled_path)
    environment = compiled.get("environment")
    if not isinstance(environment, dict):
        errors.append(f"{compiled_path} [environment] is missing")
    else:
        compiled_hosts = _hosts(environment, field="allowed_hosts")
        _check_policy(
            errors,
            label=f"{compiled_path} [environment]",
            mode=environment.get("network_mode"),
            allowed_hosts=compiled_hosts,
        )
        policies.append(
            {
                "path": str(compiled_path),
                "section": "environment",
                "mode": environment.get("network_mode"),
                "allowed_hosts": compiled_hosts,
            }
        )

    verifier = compiled.get("verifier")
    if isinstance(verifier, dict) and verifier.get("network_mode") not in {None, "no-network"}:
        errors.append(f"{compiled_path} [verifier]: verifier network must be no-network")

    agent_compose_paths = (
        root / "environment/docker-compose.yaml",
        root / "harbor/environment/docker-compose.yaml",
    )
    compose = next((path for path in agent_compose_paths if path.is_file()), None)
    if compose is not None and policies:
        agent_mode = policies[-1]["mode"]
        compose_text = compose.read_text(encoding="utf-8")
        explicit_service_networking = bool(
            re.search(r"(?m)^\s+(?:network_mode|networks)\s*:", compose_text)
        )
        if agent_mode == "no-network" and explicit_service_networking:
            errors.append(
                f"{compose}: agent services must not declare network_mode or networks; "
                "explicit Compose networking bypasses Harbor's egress sidecar and "
                "prevents run-scoped --allow-agent-host overrides"
            )

    return {
        "schema_version": "1.0",
        "task_root": str(root),
        "status": "passed" if not errors else "failed",
        "policies": policies,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = check_task(args.task_root)
    except (OSError, ValueError) as exc:
        print(f"network policy check failed: {exc}", file=sys.stderr)
        return 2
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
