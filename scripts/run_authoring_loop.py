#!/usr/bin/env python3
"""Claim and materialize a bounded, resumable authoring worker batch.

This is the programmatic controller for Raw Package -> Harbor authoring. It
does not run models. It claims candidates through the process-safe queue state,
creates one detached worktree per worker, and writes a task-local brief that a
worker agent can consume. Shared catalog/dataset integration remains a parent
operation.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MAX_CONCURRENCY = 3


def _load_queue_loop():
    path = Path(__file__).with_name("package_queue_loop.py")
    spec = importlib.util.spec_from_file_location("package_queue_loop_driver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load queue loop: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _claim(
    queue: Path,
    state: Path,
    candidate_id: str,
    owner: str,
    language: str,
    lease: int,
    attempts: int,
) -> dict[str, Any] | None:
    loop = _load_queue_loop()
    args = type(
        "ClaimArgs",
        (),
        {
            "queue": queue,
            "state": state,
            "owner": owner,
            "limit": 1,
            "lease_seconds": lease,
            "max_attempts": attempts,
            "language": language,
            "candidate_id": [candidate_id],
        },
    )()
    # command_claim prints a bounded JSON record; capture it without changing
    # queue semantics so the driver remains a thin orchestration layer.
    from contextlib import redirect_stdout
    from io import StringIO

    output = StringIO()
    with redirect_stdout(output):
        result = loop.command_claim(args)
    if result == 2:
        return None
    if result != 0:
        raise RuntimeError(f"queue claim failed for {candidate_id}: rc={result}")
    payload = json.loads(output.getvalue())
    claimed = payload.get("claimed")
    if not isinstance(claimed, list) or len(claimed) != 1:
        raise RuntimeError(f"queue claim returned unexpected payload for {candidate_id}")
    return claimed[0]


def _worktree(path: Path) -> str:
    if path.exists():
        if not (path / ".git").exists():
            raise RuntimeError(f"worker path exists and is not a git worktree: {path}")
        return "reused"
    path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["git", "worktree", "add", "--detach", str(path), "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git worktree add failed: {completed.stderr[-1000:]}")
    return "created"


def run(args: argparse.Namespace) -> dict[str, Any]:
    if not 1 <= args.max_concurrency <= MAX_CONCURRENCY:
        raise ValueError(f"max-concurrency must be between 1 and {MAX_CONCURRENCY}")
    plan = _load_json(args.plan)
    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("author plan requires tasks")
    language = plan.get("language")
    if language not in {"python", "node"}:
        raise ValueError("author plan language must be python or node")
    selected = tasks[: args.max_concurrency]
    state_root = args.state_root / plan["batch_id"]
    claims_root = state_root / "claims"
    worktree_root = args.worktree_root / plan["batch_id"]
    claims_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for task in selected:
        if not isinstance(task, dict):
            raise ValueError("author plan task must be an object")
        package = task.get("package")
        candidate_id = task.get("candidate_id")
        if not isinstance(package, str) or not SAFE_NAME.fullmatch(package):
            raise ValueError(f"unsafe package name: {package!r}")
        if not isinstance(candidate_id, str):
            raise ValueError(f"missing candidate id for {package}")
        claimed = _claim(
            args.queue,
            args.queue_state,
            candidate_id,
            args.owner,
            language,
            args.lease_seconds,
            args.max_attempts,
        )
        if claimed is None:
            results.append(
                {
                    "package": package,
                    "candidate_id": candidate_id,
                    "status": "already-claimed-or-terminal",
                }
            )
            continue
        path = worktree_root / package
        worktree_status = _worktree(path)
        brief = {
            "schema_version": "1.0",
            "batch_id": plan["batch_id"],
            "package": package,
            "candidate_id": candidate_id,
            "language": language,
            "claim": claimed,
            "worktree": str(path),
            "task_scope": f"catalog/tasks/{package}/** only",
            "stages": plan.get("stages", []),
            "remediation_policy": plan.get("remediation_policy", {}),
            "worker_guidance": plan.get("worker_guidance"),
            "agent_run_boundary": plan.get("agent_run_boundary"),
            "must_not": [
                "run GPT/Fable",
                "edit shared datasets/reports",
                "publish without integrator",
            ],
        }
        brief_path = claims_root / f"{package}.json"
        brief_path.write_text(
            json.dumps(brief, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        results.append(
            {
                "package": package,
                "candidate_id": candidate_id,
                "status": "claimed",
                "worktree": str(path),
                "worktree_status": worktree_status,
                "brief": str(brief_path),
            }
        )
    return {
        "schema_version": "1.0",
        "batch_id": plan["batch_id"],
        "language": language,
        "owner": args.owner,
        "max_concurrency": args.max_concurrency,
        "model_runs_started": False,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--queue-state", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, default=Path(".nl2repo/authoring"))
    parser.add_argument("--worktree-root", type=Path, default=Path("/tmp/nl2repo-authoring"))
    parser.add_argument("--owner", required=True)
    parser.add_argument("--max-concurrency", type=int, default=3)
    parser.add_argument("--lease-seconds", type=int, default=7200)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"authoring loop execution failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "claimed": sum(x["status"] == "claimed" for x in result["results"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
