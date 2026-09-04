#!/usr/bin/env python3
"""Continuously launch bounded Sol/Opus Harbor campaigns for fresh tasks."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RUNNABLE_LIFECYCLES = frozenset(
    {"oracle-passed", "controls-passed", "reviewed", "piloted", "published"}
)
MODEL_IDS = ("gpt-5.6-sol", "claude-opus-5")
INTEGRATION_SUBJECT = re.compile(r"^Integrate authored task ([A-Za-z0-9._-]+)$")


@dataclass(frozen=True)
class Task:
    task_id: str
    language: str
    lifecycle: str
    integration_commit: str
    integrated_at_epoch: int
    source_toml_sha256: str
    runtime_toml_sha256: str


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def _exclusive_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def _audit(root: Path, event: dict[str, Any]) -> None:
    path = root / "audit.jsonl"
    with _exclusive_lock(path.with_suffix(".jsonl.lock")):
        with path.open("a", encoding="utf-8") as stream:
            stream.write(
                json.dumps(
                    {"schema_version": "1.0", "recorded_at": _now(), **event},
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )
            stream.flush()
            os.fsync(stream.fileno())


def _run(command: list[str], *, cwd: Path, timeout: int | None = None) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "output": ((completed.stdout or "") + (completed.stderr or ""))[-8000:],
    }


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _integration_commits(repository: Path) -> dict[str, tuple[str, int]]:
    completed = subprocess.run(
        ["git", "log", "--format=%H%x09%ct%x09%s", "HEAD"],
        cwd=repository,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"cannot read integration history: {completed.stderr[-2000:]}")
    commits: dict[str, tuple[str, int]] = {}
    for line in completed.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        commit, epoch_text, subject = parts
        match = INTEGRATION_SUBJECT.fullmatch(subject)
        if match is None or match.group(1) in commits:
            continue
        commits[match.group(1)] = (commit, int(epoch_text))
    return commits


def runnable_tasks(repository: Path, *, max_age_days: int) -> list[Task]:
    commits = _integration_commits(repository)
    cutoff = int(time.time()) - max_age_days * 86_400
    tasks: list[Task] = []
    for source_toml in sorted((repository / "catalog/sources").glob("*/task.toml")):
        task_id = source_toml.parent.name
        runtime_toml = repository / "catalog/tasks" / task_id / "task.toml"
        integration = commits.get(task_id)
        if integration is None or integration[1] < cutoff or not runtime_toml.is_file():
            continue
        with source_toml.open("rb") as stream:
            source = tomllib.load(stream)
        lifecycle = source.get("lifecycle")
        status = lifecycle.get("status") if isinstance(lifecycle, dict) else None
        metadata = source.get("metadata")
        language = metadata.get("language") if isinstance(metadata, dict) else None
        if status not in RUNNABLE_LIFECYCLES or not isinstance(language, str):
            continue
        tasks.append(
            Task(
                task_id=task_id,
                language=language,
                lifecycle=status,
                integration_commit=integration[0],
                integrated_at_epoch=integration[1],
                source_toml_sha256=_sha256(source_toml),
                runtime_toml_sha256=_sha256(runtime_toml),
            )
        )
    return sorted(tasks, key=lambda task: (-task.integrated_at_epoch, task.task_id))


def _finished_epoch(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        normalized = value.removesuffix("Z") + (
            "+00:00" if value.endswith("Z") else ""
        )
        return datetime.fromisoformat(normalized).timestamp()
    except ValueError:
        return None


def fresh_inventory(
    inventory: dict[str, Any], tasks: list[Task]
) -> tuple[dict[str, Any], dict[str, set[str]]]:
    by_task = {task.task_id: task for task in tasks}
    fresh: list[dict[str, Any]] = []
    completed: dict[str, set[str]] = {model: set() for model in MODEL_IDS}
    runs = inventory.get("runs", [])
    if not isinstance(runs, list):
        raise ValueError("OSS inventory requires a runs list")
    for raw in runs:
        if not isinstance(raw, dict):
            continue
        model = raw.get("model")
        task_id = raw.get("task_id")
        task = by_task.get(task_id) if isinstance(task_id, str) else None
        finished = _finished_epoch(raw.get("finished_at"))
        if (
            model not in MODEL_IDS
            or task is None
            or finished is None
            or finished < task.integrated_at_epoch
        ):
            continue
        fresh.append(raw)
        completed[model].add(task.task_id)
    return {
        "schema_version": "1.0",
        "source": "oss",
        "runs": fresh,
    }, completed


def select_missing_tasks(
    tasks: list[Task], completed: dict[str, set[str]], *, batch_size: int
) -> list[Task]:
    return [
        task
        for task in tasks
        if any(task.task_id not in completed.get(model, set()) for model in MODEL_IDS)
    ][:batch_size]


def _runner_active() -> bool:
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = entry.joinpath("cmdline").read_bytes().replace(b"\0", b" ")
        except OSError:
            continue
        if b"run_dual_model_queue.py" in command:
            return True
    return False


def _campaign_payload(repository: Path, campaign_id: str, tasks: list[Task]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "campaign_id": campaign_id,
        "campaign_kind": "continuous-post-integration-not-dataset-score",
        "created_at": _now(),
        "harness_commit": _run(
            ["git", "rev-parse", "HEAD"], cwd=repository, timeout=30
        )["output"].strip(),
        "attempts": 1,
        "per_model_concurrency": 1,
        "max_total_concurrency": 2,
        "network": "provider-host-allowlist; candidate/verifier offline",
        "oss_archive_prefix": "nl2repobench/harbor-runs",
        "tasks": [task.__dict__ for task in tasks],
    }


def cycle(repository: Path, state_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    if _runner_active():
        return {"event": "cycle-skipped", "reason": "model-runner-active"}
    docker_free = shutil.disk_usage(args.docker_root).free
    if docker_free < args.min_free_bytes:
        return {
            "event": "cycle-skipped",
            "reason": "docker-disk-low",
            "docker_free_bytes": docker_free,
        }
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    inventory_path = state_root / "inventory" / f"oss-{stamp}.json"
    inventory_result = _run(
        [
            str(repository / ".venv/bin/python3"),
            str(repository / "scripts/build_oss_run_inventory.py"),
            "--output",
            str(inventory_path),
        ],
        cwd=repository,
        timeout=args.inventory_timeout_seconds,
    )
    if inventory_result["exit_code"] != 0:
        return {"event": "inventory-failed", **inventory_result}
    tasks = runnable_tasks(repository, max_age_days=args.max_integration_age_days)
    filtered, completed = fresh_inventory(_load_object(inventory_path), tasks)
    selected = select_missing_tasks(tasks, completed, batch_size=args.batch_size)
    if not selected:
        return {
            "event": "cycle-idle",
            "runnable_tasks": len(tasks),
            "inventory": str(inventory_path),
        }
    campaign_id = f"auto-2x1-{stamp}"
    campaign_root = repository / ".nl2repo/model-campaigns/auto" / campaign_id
    campaign = campaign_root / "campaign.json"
    eligible_inventory = campaign_root / "eligible-oss-inventory.json"
    plan = campaign_root / "plan.json"
    _atomic_write(campaign, _campaign_payload(repository, campaign_id, selected))
    _atomic_write(eligible_inventory, filtered)
    command = [
        str(repository / ".venv/bin/python3"),
        str(repository / "scripts/run_dual_model_queue.py"),
        "--campaign",
        str(campaign),
        "--run-root",
        str(repository / ".nl2repo/runs/model/auto" / campaign_id),
        "--lock-root",
        str(repository / ".nl2repo/locks/model/auto-2x1"),
        "--plan-output",
        str(plan),
        "--models-file",
        str(args.models_file),
        "--existing-inventory",
        str(eligible_inventory),
        "--per-model-concurrency",
        "1",
        "--agent-timeout-seconds",
        str(args.agent_timeout_seconds),
        "--second-model",
        "opus",
        "--execute",
    ]
    result = _run(command, cwd=repository, timeout=None)
    return {
        "event": "campaign-complete" if result["exit_code"] == 0 else "campaign-failed",
        "campaign_id": campaign_id,
        "tasks": [task.task_id for task in selected],
        "inventory": str(inventory_path),
        **result,
    }


def supervise(args: argparse.Namespace) -> int:
    repository = args.repository_root.resolve()
    state_root = (repository / args.state_root).resolve()
    state_root.mkdir(parents=True, exist_ok=True)
    with _exclusive_lock(state_root / "coordinator.lock"):
        while True:
            try:
                event = cycle(repository, state_root, args)
            except Exception as exc:  # noqa: BLE001 - keep daemon alive and audit
                event = {
                    "event": "cycle-error",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            _audit(state_root, event)
            if args.once:
                return 0 if event["event"] not in {"cycle-error", "inventory-failed"} else 1
            time.sleep(args.interval_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--state-root", type=Path, default=Path(".nl2repo/model-auto"))
    parser.add_argument("--docker-root", type=Path, default=Path("/data/docker-runtime/docker"))
    parser.add_argument("--models-file", type=Path, default=Path.home() / ".pi/agent/models.json")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--inventory-timeout-seconds", type=int, default=900)
    parser.add_argument("--agent-timeout-seconds", type=int, default=14400)
    parser.add_argument("--max-integration-age-days", type=int, default=30)
    parser.add_argument("--min-free-bytes", type=int, default=20 * 1024**3)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if (
        not 1 <= args.batch_size <= 20
        or args.interval_seconds < 1
        or args.inventory_timeout_seconds < 1
        or args.agent_timeout_seconds < 1
        or args.max_integration_age_days < 1
        or args.min_free_bytes < 0
    ):
        parser.error("invalid model coordinator bounds")
    return supervise(args)


if __name__ == "__main__":
    raise SystemExit(main())
