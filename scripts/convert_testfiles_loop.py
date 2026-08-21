#!/usr/bin/env python3
"""Coordinate resumable conversion of legacy ``test_files`` into Harbor tasks.

The loop does not invent source provenance or verifier-image metadata.  It
provides process-safe claims for human/subagent writers and validates their
handoff before a task can be marked complete.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import subprocess
import tempfile
import tomllib
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

REQUIRED_LEGACY = (
    "start.md",
    "test_case_count.txt",
    "test_commands.json",
    "test_files.json",
)
REQUIRED_HARBOR = (
    "task.toml",
    "instruction.md",
    "harbor/task.toml",
    "harbor/environment/Dockerfile",
    "harbor/solution/solve.sh",
    "harbor/tests/Dockerfile",
    "harbor/tests/test.sh",
    "harbor/tests/grade.py",
)
TERMINAL = {"complete", "blocked"}


def now() -> str:
    return datetime.now(UTC).isoformat()


def default_record(task_id: str) -> dict[str, object]:
    return {
        "task_id": task_id,
        "status": "pending",
        "owner": None,
        "lease_expires_at": None,
        "attempts": 0,
        "reason": None,
        "artifacts": [],
        "updated_at": now(),
    }


def complete_bundle(task_root: Path) -> bool:
    return all((task_root / relative).is_file() for relative in REQUIRED_HARBOR)


def legacy_tasks(legacy_root: Path) -> list[str]:
    tasks: list[str] = []
    for candidate in sorted(path for path in legacy_root.iterdir() if path.is_dir()):
        missing = [name for name in REQUIRED_LEGACY if not (candidate / name).is_file()]
        if missing:
            raise ValueError(f"legacy task {candidate.name} is missing: {', '.join(missing)}")
        tasks.append(candidate.name)
    return tasks


@contextlib.contextmanager
def locked_state(path: Path) -> Iterator[dict[str, object]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.is_file():
            state = json.loads(path.read_text(encoding="utf-8"))
        else:
            state = {"schema_version": "1.0", "tasks": {}, "updated_at": now()}
        yield state
        state["updated_at"] = now()
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        fcntl.flock(lock, fcntl.LOCK_UN)


def sync_state(
    state: dict[str, object], legacy_root: Path, catalog_root: Path
) -> dict[str, dict[str, object]]:
    records = state.setdefault("tasks", {})
    if not isinstance(records, dict):
        raise ValueError("state tasks must be an object")
    for task_id in legacy_tasks(legacy_root):
        record = records.setdefault(task_id, default_record(task_id))
        if not isinstance(record, dict):
            raise ValueError(f"invalid state record: {task_id}")
        if record["status"] in {"pending", "complete"} and complete_bundle(catalog_root / task_id):
            record.update(
                {
                    "status": "complete",
                    "owner": None,
                    "lease_expires_at": None,
                    "reason": None,
                    "updated_at": now(),
                }
            )
    return records


def lease_expired(record: dict[str, object]) -> bool:
    expires = record.get("lease_expires_at")
    if not isinstance(expires, str):
        return True
    return datetime.fromisoformat(expires) <= datetime.now(UTC)


def validate_bundle(task_id: str, catalog_root: Path, repo_root: Path) -> list[str]:
    task_root = catalog_root / task_id
    errors = [
        str(path)
        for path in (task_root / item for item in REQUIRED_HARBOR)
        if not path.is_file()
    ]
    if errors:
        return [f"missing required file: {path}" for path in errors]
    for relative in ("task.toml", "harbor/task.toml"):
        try:
            with (task_root / relative).open("rb") as handle:
                tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"invalid TOML {relative}: {exc}")
    for relative in ("harbor/solution/solve.sh", "harbor/tests/test.sh"):
        completed = subprocess.run(
            ["bash", "-n", str(task_root / relative)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            errors.append(f"invalid shell {relative}: {completed.stderr.strip()}")
    completed = subprocess.run(
        ["uv", "run", "nl2repo", "task", "validate-source", str(task_root)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        output = (completed.stderr or completed.stdout).strip()
        errors.append(f"catalog validation failed: {output}")
    return errors


def command_status(args: argparse.Namespace) -> int:
    with locked_state(args.state) as state:
        records = sync_state(state, args.legacy_root, args.catalog_root)
        counts: dict[str, int] = {}
        for record in records.values():
            status = str(record["status"])
            counts[status] = counts.get(status, 0) + 1
        output = {
            "state": str(args.state),
            "total": len(records),
            "counts": counts,
            "remaining": sorted(
                task_id for task_id, record in records.items() if record["status"] not in TERMINAL
            ),
            "blocked": sorted(
                (
                    {
                    "task_id": task_id,
                    "reason": record.get("reason"),
                    }
                    for task_id, record in records.items()
                    if record["status"] == "blocked"
                ),
                key=lambda item: item["task_id"],
            ),
        }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_claim(args: argparse.Namespace) -> int:
    with locked_state(args.state) as state:
        records = sync_state(state, args.legacy_root, args.catalog_root)
        selected: list[dict[str, object]] = []
        for task_id in sorted(records):
            if len(selected) >= args.limit:
                break
            record = records[task_id]
            if args.tasks and task_id not in args.tasks:
                continue
            if record["status"] == "running" and not lease_expired(record):
                continue
            if record["status"] not in {"pending", "running"}:
                continue
            record.update(
                {
                    "status": "running",
                    "owner": args.owner,
                    "lease_expires_at": (
                        datetime.now(UTC) + timedelta(seconds=args.lease_seconds)
                    ).isoformat(),
                    "attempts": int(record.get("attempts", 0)) + 1,
                    "updated_at": now(),
                }
            )
            selected.append(dict(record))
    print(json.dumps({"claimed": selected}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if selected else 2


def command_record(args: argparse.Namespace) -> int:
    with locked_state(args.state) as state:
        records = sync_state(state, args.legacy_root, args.catalog_root)
        record = records.get(args.task_id)
        if record is None:
            raise ValueError(f"unknown legacy task: {args.task_id}")
        if record.get("owner") != args.owner or record.get("status") != "running":
            raise ValueError(f"{args.task_id} is not claimed by {args.owner}")
        if args.status == "complete":
            errors = validate_bundle(args.task_id, args.catalog_root, args.repo_root)
            if errors:
                raise ValueError("; ".join(errors))
        record.update(
            {
                "status": args.status,
                "owner": None,
                "lease_expires_at": None,
                "reason": args.reason,
                "artifacts": args.artifact,
                "updated_at": now(),
            }
        )
    print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    errors = validate_bundle(args.task_id, args.catalog_root, args.repo_root)
    print(json.dumps({"task_id": args.task_id, "errors": errors}, indent=2, sort_keys=True))
    return 1 if errors else 0


def command_reopen(args: argparse.Namespace) -> int:
    with locked_state(args.state) as state:
        records = sync_state(state, args.legacy_root, args.catalog_root)
        record = records.get(args.task_id)
        if record is None:
            raise ValueError(f"unknown legacy task: {args.task_id}")
        if record["status"] != "blocked":
            raise ValueError(f"{args.task_id} is not blocked")
        history = record.setdefault("reopen_history", [])
        if not isinstance(history, list):
            raise ValueError(f"invalid reopen history: {args.task_id}")
        history.append(
            {
                "previous_reason": record.get("reason"),
                "reason": args.reason,
                "reopened_at": now(),
            }
        )
        record.update(
            {
                "status": "pending",
                "owner": None,
                "lease_expires_at": None,
                "reason": args.reason,
                "updated_at": now(),
            }
        )
    print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_block(args: argparse.Namespace) -> int:
    with locked_state(args.state) as state:
        records = sync_state(state, args.legacy_root, args.catalog_root)
        record = records.get(args.task_id)
        if record is None:
            raise ValueError(f"unknown legacy task: {args.task_id}")
        if record["status"] == "running" and record.get("owner") != args.owner:
            raise ValueError(f"{args.task_id} is claimed by another owner")
        history = record.setdefault("block_history", [])
        if not isinstance(history, list):
            raise ValueError(f"invalid block history: {args.task_id}")
        history.append(
            {
                "previous_status": record.get("status"),
                "reason": args.reason,
                "blocked_at": now(),
                "owner": args.owner,
            }
        )
        record.update(
            {
                "status": "blocked",
                "owner": None,
                "lease_expires_at": None,
                "reason": args.reason,
                "artifacts": args.artifact,
                "updated_at": now(),
            }
        )
    print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def parse_manifest_descriptor(data: str) -> tuple[str, str]:
    parsed = json.loads(data)
    descriptor = parsed.get("Descriptor")
    if not isinstance(descriptor, dict):
        raise ValueError("registry response is missing Descriptor")
    digest = descriptor.get("digest")
    platform = descriptor.get("platform")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError("registry response has no sha256 manifest digest")
    if not isinstance(platform, dict):
        raise ValueError("registry response is missing platform")
    os_name = platform.get("os")
    architecture = platform.get("architecture")
    if not isinstance(os_name, str) or not isinstance(architecture, str):
        raise ValueError("registry response has an invalid platform")
    return digest, f"{os_name}/{architecture}"


def probe_image(task_id: str, registry: str) -> dict[str, object]:
    tagged_ref = f"{registry.rstrip('/')}/{task_id.lower()}:1.0"
    completed = subprocess.run(
        ["docker", "manifest", "inspect", "--verbose", tagged_ref],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if completed.returncode:
        return {
            "task_id": task_id,
            "status": "error",
            "tagged_ref": tagged_ref,
            "error": (completed.stderr or completed.stdout).strip(),
        }
    try:
        digest, platform = parse_manifest_descriptor(completed.stdout)
    except (json.JSONDecodeError, ValueError) as exc:
        return {
            "task_id": task_id,
            "status": "error",
            "tagged_ref": tagged_ref,
            "error": str(exc),
        }
    return {
        "task_id": task_id,
        "status": "available",
        "tagged_ref": tagged_ref,
        "digest": digest,
        "platform": platform,
        "immutable_ref": f"{registry.rstrip('/')}/{task_id}@{digest}",
    }


def command_probe_images(args: argparse.Namespace) -> int:
    with locked_state(args.state) as state:
        records = sync_state(state, args.legacy_root, args.catalog_root)
        selected = sorted(args.tasks or records)
        unknown = sorted(set(selected) - set(records))
        if unknown:
            raise ValueError(f"unknown legacy tasks: {', '.join(unknown)}")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda task_id: probe_image(task_id, args.registry), selected))
    with locked_state(args.state) as state:
        records = sync_state(state, args.legacy_root, args.catalog_root)
        for result in results:
            record = records[str(result["task_id"])]
            record["verifier_image"] = result
            record["updated_at"] = now()
    print(json.dumps({"images": results}, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if any(result["status"] == "error" for result in results) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--legacy-root", type=Path, default=Path("test_files"))
    parser.add_argument("--catalog-root", type=Path, default=Path("catalog/tasks"))
    parser.add_argument("--state", type=Path, default=Path(".nl2repo/conversion-loop/state.json"))
    commands = parser.add_subparsers(dest="command", required=True)

    status = commands.add_parser("status")
    status.set_defaults(func=command_status)

    claim = commands.add_parser("claim")
    claim.add_argument("--owner", required=True)
    claim.add_argument("--limit", type=int, default=1)
    claim.add_argument("--lease-seconds", type=int, default=7200)
    claim.add_argument("--tasks", nargs="*")
    claim.set_defaults(func=command_claim)

    record = commands.add_parser("record")
    record.add_argument("task_id")
    record.add_argument("--owner", required=True)
    record.add_argument("--status", required=True, choices=("complete", "blocked", "pending"))
    record.add_argument("--reason")
    record.add_argument("--artifact", action="append", default=[])
    record.set_defaults(func=command_record)

    validate = commands.add_parser("validate")
    validate.add_argument("task_id")
    validate.set_defaults(func=command_validate)

    reopen = commands.add_parser("reopen")
    reopen.add_argument("task_id")
    reopen.add_argument("--reason", required=True)
    reopen.set_defaults(func=command_reopen)

    block = commands.add_parser("block")
    block.add_argument("task_id")
    block.add_argument("--owner", required=True)
    block.add_argument("--reason", required=True)
    block.add_argument("--artifact", action="append", default=[])
    block.set_defaults(func=command_block)

    probe = commands.add_parser("probe-images")
    probe.add_argument("--tasks", nargs="*")
    probe.add_argument("--workers", type=int, default=6)
    probe.add_argument(
        "--registry",
        default="ghcr.io/multimodal-art-projection/nl2repobench",
    )
    probe.set_defaults(func=command_probe_images)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "limit", 1) < 1:
        parser.error("--limit must be positive")
    if getattr(args, "lease_seconds", 1) < 1:
        parser.error("--lease-seconds must be positive")
    if getattr(args, "workers", 1) < 1:
        parser.error("--workers must be positive")
    for name in ("repo_root", "legacy_root", "catalog_root", "state"):
        value = getattr(args, name)
        if not value.is_absolute():
            setattr(args, name, args.repo_root / value if name != "repo_root" else value.resolve())
    try:
        return int(args.func(args))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"conversion loop failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
