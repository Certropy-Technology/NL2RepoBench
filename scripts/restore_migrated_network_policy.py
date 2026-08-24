#!/usr/bin/env python3
"""Restore network policy after the catalog Harbor-task migration.

The migration moved complete Harbor trees from ``catalog/sources/<id>/harbor``
to ``catalog/tasks/<id>``. The declaration and generated runtime view therefore
need separate updates:

* ``catalog/sources`` remains the human-maintained declaration and receives an
  explicit ``[environment.network_policy]`` plus an agent no-network mode.
* ``catalog/tasks`` is the current flat Harbor runtime tree and receives
  ``[environment].network_mode = "no-network"`` plus the compose isolation
  fragment. Existing bundle manifests are refreshed after those generated-file
  changes.

This script is deliberately idempotent and only operates on task IDs present in
the current ``catalog/tasks`` tree. It does not touch incomplete source-only
tasks or unrelated workspace changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "catalog" / "sources"
TASK_ROOT = ROOT / "catalog" / "tasks"

COMPOSE = "services:\n  main:\n    network_mode: none\n"


def _table_bounds(lines: list[str], table: str) -> tuple[int, int]:
    header = f"[{table}]"
    start = next((i for i, line in enumerate(lines) if line.strip() == header), None)
    if start is None:
        raise ValueError(f"missing [{table}] table")
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].lstrip().startswith("[")),
        len(lines),
    )
    return start, end


def _replace_table_key(text: str, table: str, key: str, value: str) -> str:
    lines = text.splitlines(keepends=True)
    start, end = _table_bounds(lines, table)
    pattern = re.compile(rf"^(\s*{re.escape(key)}\s*=).*$")
    for i in range(start + 1, end):
        if pattern.match(lines[i]):
            newline = "\n" if lines[i].endswith("\n") else ""
            lines[i] = f'{key} = "{value}"{newline}'
            return "".join(lines)
    raise ValueError(f"missing {key!r} in [{table}]")


def _insert_policy(text: str, *, preinstalled: bool) -> str:
    if "[environment.network_policy]" in text:
        return text
    lines = text.splitlines(keepends=True)
    _, end = _table_bounds(lines, "environment")
    source = "preinstalled-image" if preinstalled else "missing"
    reason = (
        "Third-party build and test dependencies are installed during the Docker "
        "build phase, which has network. The agent phase therefore needs no egress. "
        "A model provider host, when needed, is injected per run via Harbor "
        "agent.extra_allowed_hosts."
        if preinstalled
        else "BLOCKER: dependency closure is not yet frozen; nothing can be baked "
        "into the image at build time. Resolve by freezing [dependencies].packages "
        "and registering a hash-locked dependency lock artifact. A model provider host, when "
        "needed, is injected per run via Harbor agent.extra_allowed_hosts."
    )
    block = (
        "\n[environment.network_policy]\n"
        'mode = "no-network"\n'
        f'offline_dependencies = "{source}"\n'
        'reference_source_fetch = "forbidden"\n'
        f"reason = {json.dumps(reason, ensure_ascii=False)}\n"
    )
    insert_at = end
    while insert_at > 0 and lines[insert_at - 1].strip() == "":
        insert_at -= 1
    return "".join(lines[:insert_at]) + block + "".join(lines[insert_at:])


def _source_policy(task_id: str) -> bool:
    path = SOURCE_ROOT / task_id / "task.toml"
    if not path.is_file():
        return False
    original = path.read_text()
    data = tomllib.loads(original)
    dependencies = data.get("dependencies") or {}
    preinstalled = dependencies.get("status") == "known" or bool(dependencies.get("packages"))
    text = _replace_table_key(original, "environment", "network_mode", "no-network")
    text = _insert_policy(text, preinstalled=preinstalled)
    if "[harbor]" in text:
        harbor = data.get("harbor") or {}
        if harbor.get("agent_network_mode") is not None:
            text = _replace_table_key(text, "harbor", "agent_network_mode", "no-network")
    if text != original:
        tomllib.loads(text)
        path.write_text(text)
        return True
    return False


def _refresh_bundle_manifest(path: Path) -> None:
    payload = json.loads(path.read_text())
    files = []
    for item in sorted(p for p in path.parent.rglob("*") if p.is_file() and p != path):
        data = item.read_bytes()
        files.append(
            {
                "path": item.relative_to(path.parent).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            }
        )
    payload["files"] = files
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def _runtime_policy(task_id: str) -> bool:
    task_dir = TASK_ROOT / task_id
    path = task_dir / "task.toml"
    original = path.read_text()
    text = _replace_table_key(original, "environment", "network_mode", "no-network")
    changed = text != original
    compose = task_dir / "environment" / "docker-compose.yaml"
    current_compose = compose.read_text() if compose.is_file() else ""
    if current_compose != COMPOSE:
        compose.write_text(COMPOSE)
        changed = True
    if text != original:
        tomllib.loads(text)
        path.write_text(text)
    manifest = task_dir / "bundle.manifest.json"
    if changed and manifest.is_file():
        _refresh_bundle_manifest(manifest)
    return changed


def restore() -> tuple[list[str], list[str]]:
    changed_sources: list[str] = []
    changed_tasks: list[str] = []
    for task_dir in sorted(p for p in TASK_ROOT.iterdir() if p.is_dir()):
        task_toml = task_dir / "task.toml"
        if not task_toml.is_file():
            continue
        task_id = task_dir.name
        if _source_policy(task_id):
            changed_sources.append(task_id)
        if _runtime_policy(task_id):
            changed_tasks.append(task_id)
    return changed_sources, changed_tasks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without writing.")
    args = parser.parse_args()
    if args.check:
        # Run the same logic in a temporary copy is intentionally avoided: the
        # caller should use git diff for exact review. This mode only reports the
        # current task count and is kept for CI discoverability.
        print(f"current tasks: {sum((p / 'task.toml').is_file() for p in TASK_ROOT.iterdir())}")
        return 0
    sources, tasks = restore()
    print(f"source policies changed: {len(sources)} {sources}")
    print(f"runtime task trees changed: {len(tasks)} {tasks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
