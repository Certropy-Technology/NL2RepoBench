#!/usr/bin/env python3
"""Supervise Package authoring loops, integration, archival, and cleanup.

The supervisor is the single writer for the integration checkout. Workers only
write their detached worktrees. A task is removed only after its source and
generated Harbor projection have been validated, committed, pushed, and its
complete worktree payload has been verified in OSS.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

SAFE_PACKAGE = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*|@[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)$"
)
SECRET_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{40,256}(?![A-Za-z0-9_-])"),
    re.compile(r"LTAI[A-Za-z0-9]{12,}"),
    re.compile(r"AKIA[A-Z0-9]{12,}"),
)
DEFAULT_BATCHES = {
    "python": "python-author-wave2-20260828",
    "node": "node-author-wave2-20260828",
    "go": "go-author-wave2-20260828",
}
DEFAULT_QUEUE_FILES = {
    "python": "python-production-queue-wave2-20260826.json",
    "node": "npm-production-queue-wave2-20260826.json",
    "go": "go-production-queue-wave2-20260826.json",
}
DEFAULT_PLAN_FILES = {
    "python": "python-author-wave2-20260828.json",
    "node": "node-author-wave2-20260828.json",
    "go": "go-author-wave2-20260828.json",
}
DEFAULT_WORKERS = 3
DEFAULT_MAX_TOTAL_CONTROLLERS = 3
DEFAULT_MIN_FREE_BYTES = 12 * 1024**3
DEFAULT_WATCHER_MIN_FREE_BYTES = 2 * 1024**3
DEFAULT_FAILURE_BACKOFF_SECONDS = 1800
DEFAULT_DIRECTOR_INTERVAL_SECONDS = 600
DEFAULT_DIRECTOR_TIMEOUT_SECONDS = 300
DIRECTOR_ACTIONS = frozenset({"continue", "discover", "integrate", "pause"})


@dataclass(frozen=True)
class Lane:
    language: str
    batch_id: str
    queue: Path
    plan: Path
    queue_state: Path


@dataclass(frozen=True)
class Proc:
    pid: int
    state: str
    cwd: str
    command: str


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _archive_module(root: Path) -> Any:
    return _load_module("authoring_archive", root / "scripts/archive_authoring_live.py")


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_digest(root: Path) -> str:
    if not root.is_dir() or root.is_symlink():
        raise ValueError(f"expected regular directory: {root}")
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed in source tree: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix().encode()
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _secret_paths(root: Path) -> list[str]:
    findings: list[str] = []
    if root.is_symlink():
        return [str(root)]
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            findings.append(str(path))
            continue
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(str(path))
    return findings


def _referenced_digests(source: Path) -> set[str]:
    text = (source / "task.toml").read_text(encoding="utf-8")
    return set(re.findall(r"sha256:[0-9a-f]{64}", text))


def _cas_file(root: Path, digest: str) -> Path:
    value = digest.removeprefix("sha256:")
    return root / ".nl2repo/artifacts/private/sha256" / value[:2] / value


def _sync_private_cas(root: Path, worktree: Path, source: Path) -> list[str]:
    """Copy only this task's missing private artifacts into the central CAS."""

    copied: list[str] = []
    for digest in sorted(_referenced_digests(source)):
        source_file = _cas_file(worktree, digest)
        if not source_file.is_file() or source_file.is_symlink():
            continue
        if _sha256(source_file) != digest.removeprefix("sha256:"):
            raise ValueError(f"private artifact failed source hash: {digest}")
        target = _cas_file(root, digest)
        if target.exists() or target.is_symlink():
            if (
                target.is_symlink()
                or not target.is_file()
                or _sha256(target) != digest.removeprefix("sha256:")
            ):
                raise ValueError(f"central private artifact collision: {digest}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source_file, target)
        except OSError:
            temporary = target.with_name(f".{target.name}.supervisor.tmp")
            shutil.copyfile(source_file, temporary)
            if _sha256(temporary) != digest.removeprefix("sha256:"):
                temporary.unlink(missing_ok=True)
                raise ValueError(
                    f"private artifact copy failed hash: {digest}"
                ) from None
            os.replace(temporary, target)
        copied.append(digest)
    return copied


def _proc_table() -> list[Proc]:
    rows: list[Proc] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text(encoding="utf-8")
            state = stat.rsplit(")", 1)[1].split()[0]
            cwd = os.path.realpath(entry / "cwd")
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                errors="replace"
            ).strip()
        except (OSError, UnicodeDecodeError):
            continue
        if state != "Z":
            rows.append(Proc(int(entry.name), state, cwd, command))
    return rows


def _worktree_processes(worktree: Path, procs: list[Proc]) -> list[Proc]:
    target = str(worktree.resolve())
    return [
        proc
        for proc in procs
        if proc.cwd == target
        or proc.cwd.startswith(target + os.sep)
        or target in proc.command
    ]


def _docker_uses(worktree: Path) -> bool:
    listed = subprocess.run(
        ["docker", "ps", "-q"], capture_output=True, text=True, check=False
    )
    if listed.returncode != 0:
        return True
    ids = listed.stdout.split()
    if not ids:
        return False
    inspected = subprocess.run(
        ["docker", "inspect", *ids], capture_output=True, text=True, check=False
    )
    if inspected.returncode != 0:
        return True
    return str(worktree.resolve()) in inspected.stdout


def _idle(worktree: Path, procs: list[Proc]) -> bool:
    return not _worktree_processes(worktree, procs) and not _docker_uses(worktree)


def _free_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free


def _redact(text: str) -> str:
    result = text
    for pattern in SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result[-2000:]


def _director_prompt(snapshot: dict[str, Any]) -> str:
    return f"""You are the top-level NL2RepoBench Director.

You only choose an operational action. A deterministic pipeline executes it.
Return exactly one JSON object and no Markdown:
{{
  "action": "continue|discover|integrate|pause",
  "language": "python|node|go|all|none",
  "discover_packages": [],
  "integrate_limit": 0,
  "worker_limit": 0,
  "reason": "short reason"
}}

Rules: limits are integers 0..3; discover_packages has at most 8 names;
discover package names must come from discovery_pool; pause uses zero limits;
do not invent commands, paths, credentials, or package names. Prefer safe
integration/archive work. Pause when disk is low, checkout is dirty, or
evidence is ambiguous.

STATUS:
{json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2)}
"""


def _parse_director_response(text: str) -> dict[str, Any]:
    if not text.strip() or text.lstrip().startswith("```"):
        raise ValueError("Director response must be plain JSON")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("Director response must be an object")
    required = {
        "action",
        "language",
        "discover_packages",
        "integrate_limit",
        "worker_limit",
        "reason",
    }
    if set(value) != required or value["action"] not in DIRECTOR_ACTIONS:
        raise ValueError("Director response schema is invalid")
    if value["language"] not in {"python", "node", "go", "all", "none"}:
        raise ValueError("Director language is invalid")
    packages = value["discover_packages"]
    if not isinstance(packages, list) or len(packages) > 8 or not all(
        isinstance(package, str) and SAFE_PACKAGE.fullmatch(package)
        for package in packages
    ):
        raise ValueError("Director discover_packages is invalid")
    for field in ("integrate_limit", "worker_limit"):
        if not isinstance(value[field], int) or not 0 <= value[field] <= 3:
            raise ValueError(f"Director {field} is invalid")
    if not isinstance(value["reason"], str) or not value["reason"].strip():
        raise ValueError("Director reason is required")
    if value["action"] == "pause" and (
        value["integrate_limit"] or value["worker_limit"]
    ):
        raise ValueError("pause must use zero limits")
    return value


def _director_decision(
    args: argparse.Namespace,
    root: Path,
    live: Path,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    cache_path = live / "supervisor/director-decision.json"
    if not args.refresh_director and cache_path.is_file():
        try:
            cached = _json(cache_path)
            age = time.time() - cache_path.stat().st_mtime
            if age < args.director_interval_sec:
                decision = _parse_director_response(str(cached["response"]))
                decision["cached"] = True
                return decision
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            pass
    if args.director_mode == "rules":
        decision = {
            "action": "continue",
            "language": "all",
            "discover_packages": [],
            "integrate_limit": min(args.max_integrations, 3),
            "worker_limit": min(args.workers, 3),
            "reason": "explicit deterministic rules mode",
        }
        _atomic_write(
            cache_path,
            {"response": json.dumps(decision, sort_keys=True), "decision": decision},
        )
        return decision
    command = shlex.split(args.director_command)
    if not command:
        raise ValueError("director-command must not be empty")
    command.extend(
        [
            "--print",
            "--no-tools",
            "--no-session",
            "--no-extensions",
            "--no-skills",
            "--no-context-files",
            "--provider",
            args.director_provider,
            "--model",
            args.director_model,
            "--thinking",
            args.director_thinking,
            "--",
            _director_prompt(snapshot),
        ]
    )
    completed = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=args.director_timeout_sec,
        env={**os.environ, "NL2REPO_DIRECTOR": "1"},
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Director exited with {completed.returncode}: {_redact(completed.stderr)}"
        )
    decision = _parse_director_response(completed.stdout)
    _atomic_write(
        cache_path,
        {"response": completed.stdout, "decision": decision},
    )
    return decision


def _discovery_pool(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {"python": [], "node": [], "go": []}
    value = _json(path)
    pool: dict[str, list[str]] = {"python": [], "node": [], "go": []}
    for language in pool:
        entries = value.get(language, [])
        if isinstance(entries, list):
            pool[language] = sorted(
                {
                    package
                    for package in entries
                    if isinstance(package, str) and SAFE_PACKAGE.fullmatch(package)
                }
            )
    return pool


def _run_discovery(
    args: argparse.Namespace,
    root: Path,
    live: Path,
    decision: dict[str, Any],
    lanes: list[Lane],
) -> dict[str, Any]:
    language = decision.get("language")
    if language not in {"python", "node", "go"}:
        return {"status": "discovery-rejected", "reason": "Director chose no single language"}
    pool = _discovery_pool(args.discovery_pool)
    known = {
        record.get("package")
        for lane in lanes
        for record in _lane_records(lane)
        if isinstance(record.get("package"), str)
    }
    requested = decision.get("discover_packages") or pool[language]
    packages = [
        package
        for package in requested
        if package in pool[language] and package not in known
    ][:8]
    if not packages:
        return {"status": "discovery-rejected", "reason": "discovery pool has no new packages"}
    script = {
        "python": root / "scripts/discover_python_candidates.py",
        "node": root / "scripts/discover_npm_candidates.py",
        "go": root / "scripts/discover_go_candidates.py",
    }[language]
    if not script.is_file():
        return {"status": "discovery-rejected", "reason": f"missing {script.name}"}
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output = live / "supervisor/discovery" / f"{language}-{stamp}.json"
    command = [sys.executable, str(script)]
    for package in packages:
        command.extend(("--package", package))
    command.extend(("--output", str(output), "--workers", "4"))
    result = _run(command, cwd=root, timeout=args.command_timeout)
    return {
        "status": "discovered" if result["exit_code"] == 0 else "discovery-failed",
        "language": language,
        "packages": packages,
        "output": str(output),
        "exit_code": result["exit_code"],
        "output_tail": result["output"],
    }


def _run(
    command: list[str],
    *,
    cwd: Path,
    timeout: int,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": 124,
            "timeout": True,
            "raw_output": str(exc),
            "output": _redact(str(exc)),
        }
    raw_output = completed.stdout or completed.stderr
    return {
        "command": command,
        "exit_code": completed.returncode,
        "timeout": False,
        "raw_output": raw_output,
        "output": _redact(raw_output),
    }


def _command_output(result: dict[str, Any]) -> str:
    value = result.get("raw_output", result.get("output", ""))
    return value if isinstance(value, str) else str(value)


def _lane_records(lane: Lane) -> list[dict[str, Any]]:
    payload = _json(lane.queue_state)
    items = payload.get("items")
    if not isinstance(items, dict):
        raise ValueError(f"queue state has no items: {lane.queue_state}")
    return [record for record in items.values() if isinstance(record, dict)]


def _queue_summary(lane: Lane) -> dict[str, Any]:
    records = _lane_records(lane)
    counts: dict[str, int] = {}
    for record in records:
        status = str(record.get("status"))
        counts[status] = counts.get(status, 0) + 1
    return {
        "language": lane.language,
        "counts": dict(sorted(counts.items())),
        "claimable": _lane_has_claimable_work(records, max_attempts=3),
        "exhausted": sum(
            1
            for record in records
            if record.get("status") == "pending"
            and int(record.get("attempts", 0)) >= 3
        ),
    }


def _lane_has_claimable_work(
    records: list[dict[str, Any]], *, max_attempts: int
) -> bool:
    return any(
        record.get("status") == "pending"
        and int(record.get("attempts", 0)) < max_attempts
        for record in records
    )


def _release_stale_claims(
    root: Path, lane: Lane, procs: list[Proc], *, max_attempts: int
) -> list[dict[str, Any]]:
    now = datetime.now(UTC)
    actions: list[dict[str, Any]] = []
    queue_loop = root / "scripts/package_queue_loop.py"
    for record in _lane_records(lane):
        if record.get("status") != "running":
            continue
        expires_value = record.get("lease_expires_at")
        owner = record.get("owner")
        package = record.get("package")
        candidate_id = record.get("candidate_id")
        if not isinstance(expires_value, str) or not isinstance(owner, str):
            continue
        if not isinstance(package, str) or not isinstance(candidate_id, str):
            continue
        try:
            expired = datetime.fromisoformat(expires_value) <= now
        except ValueError:
            expired = True
        if not expired:
            continue
        worktree = root / ".nl2repo/authoring-live/worktrees" / lane.batch_id / package
        active = worktree.is_dir() and (
            _worktree_processes(worktree, procs) or _docker_uses(worktree)
        )
        if active:
            actions.append(
                {"language": lane.language, "package": package, "status": "stale-but-active"}
            )
            continue
        owner_active = any(
            proc
            for proc in _controller_processes(lane, procs)
            if f"--owner {owner}" in proc.command
        )
        if owner_active:
            continue
        attempts = int(record.get("attempts", 0))
        if attempts >= max_attempts:
            actions.append(
                {
                    "language": lane.language,
                    "package": package,
                    "status": "stale-at-retry-limit",
                    "owner": owner,
                }
            )
            continue
        released = _run(
            [
                sys.executable,
                str(queue_loop),
                "release",
                candidate_id,
                "--queue",
                str(lane.queue),
                "--state",
                str(lane.queue_state),
                "--owner",
                owner,
                "--reason",
                "supervisor released expired lease with no live process or container",
            ],
            cwd=root,
            timeout=120,
        )
        actions.append(
            {
                "language": lane.language,
                "package": package,
                "status": (
                    "stale-released"
                    if released["exit_code"] == 0
                    else "stale-release-error"
                ),
                "output": released["output"],
            }
        )
    return actions


def _controller_processes(lane: Lane, procs: list[Proc]) -> list[Proc]:
    needle = str(lane.queue_state.resolve())
    return [
        proc
        for proc in procs
        if "run_authoring_loop.py" in proc.command
        and (needle in proc.command or lane.batch_id in proc.command)
    ]


def _controller_slots(lane: Lane, procs: list[Proc]) -> set[str]:
    owners: set[str] = set()
    for proc in _controller_processes(lane, procs):
        match = re.search(r"(?:^|\s)--owner\s+(\S+)", proc.command)
        if match:
            owners.add(match.group(1))
    return owners


def _watcher_processes(procs: list[Proc]) -> list[Proc]:
    return [proc for proc in procs if "archive_authoring_live.py" in proc.command]


@contextmanager
def _exclusive_lock(path: Path, *, blocking: bool) -> Iterator[bool]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as stream:
        try:
            flags = fcntl.LOCK_EX
            if not blocking:
                flags |= fcntl.LOCK_NB
            fcntl.flock(stream, flags)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def _source_path(worktree: Path, package: str) -> Path:
    if not SAFE_PACKAGE.fullmatch(package):
        raise ValueError(f"unsafe package name: {package}")
    path = worktree / "catalog" / "sources" / package
    root = (worktree / "catalog" / "sources").resolve()
    resolved = path.resolve()
    if resolved != root / package or root not in resolved.parents:
        raise ValueError(f"source path escapes catalog: {package}")
    return path


def _copy_if_new(source: Path, target: Path) -> bool:
    if not source.is_dir() or source.is_symlink():
        raise ValueError(f"source directory is missing or unsafe: {source}")
    findings = _secret_paths(source)
    if findings:
        raise ValueError(f"secret-shaped source content: {findings[0]}")
    if target.exists() or target.is_symlink():
        if target.is_symlink() or _tree_digest(source) != _tree_digest(target):
            raise ValueError(f"integration source collision: {target}")
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=False)
    return True


def _compiled_task_id(source: Path) -> str:
    payload = tomllib.loads((source / "task.toml").read_text(encoding="utf-8"))
    task_id = payload.get("task_id")
    if not isinstance(task_id, str) or not task_id or task_id.startswith("/"):
        raise ValueError(f"invalid task_id in {source / 'task.toml'}")
    pure = PurePosixPath(task_id)
    if ".." in pure.parts:
        raise ValueError(f"task_id escapes generated root: {task_id}")
    return task_id


def _validate_and_compile(root: Path, source: Path, language: str) -> tuple[dict[str, Any], Path]:
    validation = _run(
        ["uv", "run", "nl2repo", "task", "validate-source", str(source)],
        cwd=root,
        timeout=600,
    )
    if validation["exit_code"] != 0:
        raise RuntimeError(f"source validation failed: {validation['output']}")
    network = _run(
        [
            "uv",
            "run",
            "nl2repo",
            "task",
            "lint-network",
            "--tasks-root",
            str(root / "catalog/sources"),
        ],
        cwd=root,
        timeout=600,
    )
    if network["exit_code"] != 0:
        raise RuntimeError(f"network lint failed: {network['output']}")
    toolchain = root / {
        "python": "toolchain.lock.toml",
        "node": "toolchain.node.lock.toml",
        "go": "toolchain.go.lock.toml",
    }[language]
    compile_root = root / ".nl2repo/supervisor/compile" / re.sub(
        r"[^A-Za-z0-9._-]+", "_", source.name
    )
    if compile_root.exists():
        shutil.rmtree(compile_root)
    compile_root.mkdir(parents=True, exist_ok=True)
    compiled = _run(
        [
            "uv",
            "run",
            "nl2repo",
            "harbor",
            "compile",
            str(source),
            "--output",
            str(compile_root),
            "--toolchain",
            str(toolchain),
            "--artifact-root",
            str(root / ".nl2repo/artifacts"),
            "--allow-private",
        ],
        cwd=root,
        timeout=1800,
    )
    if compiled["exit_code"] != 0:
        raise RuntimeError(f"Harbor compile failed: {compiled['output']}")
    compiled_path = compile_root / _compiled_task_id(source)
    if not compiled_path.is_dir():
        raise RuntimeError(f"compiler did not produce expected task: {compiled_path}")
    return {"validation": validation, "network": network, "compile": compiled}, compiled_path


def _copy_generated(compiled: Path, target: Path) -> bool:
    if target.exists() or target.is_symlink():
        if target.is_symlink() or _tree_digest(compiled) != _tree_digest(target):
            raise ValueError(f"generated task collision: {target}")
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(compiled, target, symlinks=False)
    return True


def _git_status(root: Path) -> list[str]:
    result = _run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root,
        timeout=60,
    )
    if result["exit_code"] != 0:
        raise RuntimeError(f"git status failed: {result['output']}")
    return [line for line in _command_output(result).splitlines() if line]


def _remote_sync(root: Path, remote: str, branch: str) -> None:
    result = _run(
        ["git", "push", remote, f"HEAD:{branch}"], cwd=root, timeout=600
    )
    if result["exit_code"] != 0:
        raise RuntimeError(f"git push failed: {result['output']}")


def _integrate_task(
    root: Path,
    lane: Lane,
    package: str,
    record: dict[str, Any],
    procs: list[Proc],
    *,
    remote: str,
    branch: str,
    archive_bucket: Any | None,
    archive_module: Any,
    receipt_root: Path,
    dry_run: bool,
    timeout: int,
) -> dict[str, Any]:
    worktree = root / ".nl2repo/authoring-live/worktrees" / lane.batch_id / package
    if not worktree.is_dir():
        return {"package": package, "status": "missing-worktree"}
    if not dry_run and archive_bucket is None:
        return {"package": package, "status": "oss-unavailable"}
    active = _worktree_processes(worktree, procs)
    if active or _docker_uses(worktree):
        return {
            "package": package,
            "status": "active",
            "processes": [proc.pid for proc in active],
        }
    source = _source_path(worktree, package)
    if (
        not (source / "task.toml").is_file()
        or not (source / "instruction.md").is_file()
        or not (source / "production-evidence.json").is_file()
        or not (worktree / ".nl2repo/authoring-handoff.json").is_file()
    ):
        return {"package": package, "status": "not-ready"}
    if dry_run:
        return {"package": package, "status": "ready", "dry_run": True}
    if _git_status(root):
        raise RuntimeError("integration checkout is dirty; supervisor refuses to mix changes")
    source_target = root / "catalog/sources" / package
    source_changed = False
    generated_changed = False
    generated_target: Path | None = None
    cas_copied: list[str] = []
    try:
        source_changed = _copy_if_new(source, source_target)
        cas_copied = _sync_private_cas(root, worktree, source_target)
        checks, compiled = _validate_and_compile(root, source_target, lane.language)
        task_id = _compiled_task_id(source_target)
        generated_target = root / "catalog/tasks" / task_id
        generated_changed = _copy_generated(compiled, generated_target)
    except Exception:
        if generated_changed and generated_target is not None:
            shutil.rmtree(generated_target, ignore_errors=True)
        if source_changed:
            shutil.rmtree(source_target, ignore_errors=True)
        raise
    allowed = {
        f"catalog/sources/{Path(package).as_posix()}",
        f"catalog/tasks/{Path(task_id).as_posix()}",
    }
    staged = _run(
        [
            "git",
            "add",
            "--",
            f"catalog/sources/{package}",
            f"catalog/tasks/{task_id}",
        ],
        cwd=root,
        timeout=60,
    )
    if staged["exit_code"] != 0:
        _run(
            [
                "git",
                "reset",
                "--",
                f"catalog/sources/{package}",
                f"catalog/tasks/{task_id}",
            ],
            cwd=root,
            timeout=60,
        )
        if generated_changed:
            shutil.rmtree(generated_target, ignore_errors=True)
        if source_changed:
            shutil.rmtree(source_target, ignore_errors=True)
        raise RuntimeError(f"git add failed: {staged['output']}")
    staged_paths = _run(
        ["git", "diff", "--cached", "--name-only"], cwd=root, timeout=60
    )
    if staged_paths["exit_code"] != 0:
        _run(
            ["git", "reset", "--", f"catalog/sources/{package}", f"catalog/tasks/{task_id}"],
            cwd=root,
            timeout=60,
        )
        if generated_changed:
            shutil.rmtree(generated_target, ignore_errors=True)
        if source_changed:
            shutil.rmtree(source_target, ignore_errors=True)
        raise RuntimeError(f"staged diff failed: {staged_paths['output']}")
    changed_paths = set(_command_output(staged_paths).splitlines())
    allowed_changes = {
        path
        for path in changed_paths
        if any(path == prefix or path.startswith(prefix + "/") for prefix in allowed)
    }
    if allowed_changes != changed_paths:
        _run(
            ["git", "reset", "--", f"catalog/sources/{package}", f"catalog/tasks/{task_id}"],
            cwd=root,
            timeout=60,
        )
        if generated_changed:
            shutil.rmtree(generated_target, ignore_errors=True)
        if source_changed:
            shutil.rmtree(source_target, ignore_errors=True)
        raise RuntimeError(f"supervisor staged unexpected paths: {sorted(changed_paths - allowed)}")
    commit = None
    if changed_paths:
        committed = _run(
            ["git", "commit", "-m", f"Integrate authored task {package}"],
            cwd=root,
            timeout=600,
        )
        if committed["exit_code"] != 0:
            _run(
                ["git", "reset", "--", f"catalog/sources/{package}", f"catalog/tasks/{task_id}"],
                cwd=root,
                timeout=60,
            )
            if generated_changed:
                shutil.rmtree(generated_target, ignore_errors=True)
            if source_changed:
                shutil.rmtree(source_target, ignore_errors=True)
            raise RuntimeError(f"git commit failed: {committed['output']}")
        commit = _command_output(
            _run(["git", "rev-parse", "HEAD"], cwd=root, timeout=60)
        ).strip()
    _remote_sync(root, remote, branch)
    if archive_bucket is None:
        raise RuntimeError("OSS credentials are missing; worktree retained")
    archived = archive_module.archive_task(
        archive_bucket,
        lane=archive_module.Lane(
            lane.language, lane.batch_id, lane.queue_state
        ),
        package=package,
        worktree=worktree,
        receipt_root=receipt_root,
        workers=8,
        cleanup=True,
        queue_status=str(record.get("status")),
        owner=record.get("owner") if isinstance(record.get("owner"), str) else None,
        attempts=int(record.get("attempts", 0)),
    )
    if archived.get("status") not in {"archived", "already-archived"}:
        raise RuntimeError(f"OSS archive did not complete: {archived}")
    removed = _run(
        ["git", "worktree", "remove", "--force", str(worktree)],
        cwd=root,
        timeout=600,
    )
    if removed["exit_code"] != 0:
        raise RuntimeError(f"worktree removal failed: {removed['output']}")
    return {
        "package": package,
        "status": "integrated",
        "source_changed": source_changed,
        "generated_changed": generated_changed,
        "private_cas_copied": cas_copied,
        "commit": commit,
        "archive": archived,
        "checks": checks,
    }


def _integration_attempt(action: dict[str, Any]) -> bool:
    return action.get("status") not in {
        "active",
        "missing-worktree",
        "not-ready",
        "oss-unavailable",
        "ready",
    }


def _failure_key(worktree: Path, package: str) -> str:
    source = _source_path(worktree, package)
    handoff = worktree / ".nl2repo/authoring-handoff.json"
    digest = hashlib.sha256()
    for path in (source / "task.toml", handoff):
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _load_failure_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _save_failure_state(path: Path, value: dict[str, Any]) -> None:
    _atomic_write(path, value)


def _failure_is_in_backoff(
    state: dict[str, Any], worktree: Path, package: str
) -> bool:
    record = state.get(package)
    if not isinstance(record, dict):
        return False
    try:
        retry_after = float(record.get("retry_after", 0))
        fingerprint = str(record.get("fingerprint"))
        return retry_after > time.time() and fingerprint == _failure_key(worktree, package)
    except (OSError, ValueError):
        return False


def _oss_bucket() -> Any | None:
    key_id = os.environ.get("OSS_ACCESS_KEY_ID")
    key_secret = os.environ.get("OSS_ACCESS_KEY_SECRET")
    if not key_id or not key_secret:
        return None
    import oss2  # type: ignore[import-untyped]

    return oss2.Bucket(
        oss2.Auth(key_id, key_secret),
        "https://oss-ap-southeast-1.aliyuncs.com",
        "dingshang-sg",
    )


def _start_watcher(root: Path, lanes: list[Lane], live: Path) -> int:
    log = live / "logs/archive-watcher-supervisor.log"
    pid_path = live / "pids/archive-watcher-supervisor.pid"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [
                sys.executable,
                str(root / "scripts/archive_authoring_live.py"),
                *sum(
                    (
                        [
                            "--lane",
                            f"{lane.language}:{lane.batch_id}:{lane.queue_state}",
                        ]
                        for lane in lanes
                    ),
                    [],
                ),
                "--worktree-root",
                str(live / "worktrees"),
                "--receipt-root",
                str(live / "archive-receipts"),
                "--workers",
                "8",
                "--interval-sec",
                "60",
                "--cleanup",
                "--cleanup-orphan-containers",
                "--lock-file",
                str(live / "archive.lock"),
            ],
            cwd=root,
            env={**os.environ, "TMPDIR": str(live / "tmp")},
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    pid_path.write_text(f"{process.pid}\n", encoding="utf-8")
    return process.pid


def _start_controller(root: Path, lane: Lane, live: Path, owner: str) -> int:
    log = live / "logs" / f"{owner}.log"
    output = live / "results" / f"{owner}.json"
    pid_path = live / "pids" / f"{owner}.pid"
    log.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(root / "scripts/run_authoring_loop.py"),
        "--plan",
        str(lane.plan),
        "--queue",
        str(lane.queue),
        "--queue-state",
        str(lane.queue_state),
        "--catalog-root",
        str(root / "catalog/sources"),
        "--state-root",
        str(live / "state"),
        "--worktree-root",
        str(live / "worktrees"),
        "--owner",
        owner,
        "--max-concurrency",
        "1",
        "--lease-seconds",
        "7200",
        "--max-attempts",
        "3",
        "--refill-queue",
        "--output",
        str(output),
        "--provider",
        os.environ.get("PI_PROVIDER", "z-open-api-gpt-openai-responses"),
        "--model",
        os.environ.get("PI_MODEL", "gpt-5.6-sol"),
        "--thinking",
        os.environ.get("PI_THINKING", "high"),
        "--models-file",
        str(Path.home() / ".pi/agent/models.json"),
        "--session-root",
        str(live / "sessions"),
        "--agent-timeout-sec",
        "3600",
        "--exclude-tools",
        "subagent,subagent_supervisor,subagent_wait",
    ]
    with log.open("a", encoding="utf-8") as stream:
        process = subprocess.Popen(
            command,
            cwd=root,
            env={**os.environ, "TMPDIR": str(live / "tmp")},
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    pid_path.write_text(f"{process.pid}\n", encoding="utf-8")
    return process.pid


def _resume_stopped_controllers(
    lanes: list[Lane], procs: list[Proc]
) -> list[int]:
    resumed: list[int] = []
    for lane in lanes:
        for proc in _controller_processes(lane, procs):
            if proc.state == "T":
                try:
                    os.kill(proc.pid, signal.SIGCONT)
                except ProcessLookupError:
                    continue
                resumed.append(proc.pid)
    return resumed


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _lanes(root: Path, live: Path, queue_root: Path) -> list[Lane]:
    return [
        Lane(
            language,
            DEFAULT_BATCHES[language],
            (queue_root / DEFAULT_QUEUE_FILES[language]).resolve(),
            (live / "plans" / DEFAULT_PLAN_FILES[language]).resolve(),
            (live / "queues" / f"{language}-wave2-20260828.json").resolve(),
        )
        for language in ("python", "node", "go")
    ]


def supervise(args: argparse.Namespace) -> int:
    root = Path(args.repository_root).resolve()
    live = (root / args.live_root).resolve()
    queue_root = Path(args.queue_root).resolve()
    lanes = _lanes(root, live, queue_root)
    for lane in lanes:
        if not lane.queue.is_file() or not lane.plan.is_file() or not lane.queue_state.is_file():
            raise ValueError(f"lane input is missing: {lane}")
    lock_path = live / "supervisor.lock"
    report_path = live / "supervisor/status.json"
    failure_state_path = live / "supervisor/integration-failures.json"
    with _exclusive_lock(lock_path, blocking=False) as acquired:
        if not acquired:
            print("another authoring supervisor owns the lock", file=sys.stderr)
            return 2
        while True:
            free = _free_bytes(root)
            procs = _proc_table()
            report: dict[str, Any] = {
                "schema_version": "1.0",
                "kind": "authoring-supervisor-status",
                "observed_at": datetime.now(UTC).isoformat(),
                "free_bytes": free,
                "lanes": [_queue_summary(lane) for lane in lanes],
                "controllers": {
                    lane.language: len(_controller_slots(lane, procs))
                    for lane in lanes
                },
                "watcher_count": len(_watcher_processes(procs)),
                "actions": [],
                "errors": [],
            }
            archive_module = _archive_module(root)
            integration_clean = not _git_status(root)
            report["integration_clean"] = integration_clean
            discovery_pool = _discovery_pool(args.discovery_pool)
            snapshot = {
                "free_bytes": free,
                "integration_clean": integration_clean,
                "lanes": report["lanes"],
                "controllers": report["controllers"],
                "watcher_count": report["watcher_count"],
                "discovery_pool": discovery_pool,
            }
            try:
                director = _director_decision(args, root, live, snapshot)
            except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
                director = {
                    "action": "pause",
                    "language": "none",
                    "discover_packages": [],
                    "integrate_limit": 0,
                    "worker_limit": 0,
                    "reason": f"Director unavailable: {_redact(str(exc))}",
                }
                report["errors"].append(
                    {"status": "director-error", "error": director["reason"]}
                )
            report["director"] = director
            selected_language = director.get("language")
            if selected_language not in {"python", "node", "go", "all"}:
                selected_language = "none"
            integration_limit = (
                min(int(director.get("integrate_limit", 0)), args.max_integrations)
                if director.get("action") in {"continue", "integrate"}
                else 0
            )
            worker_limit = (
                min(int(director.get("worker_limit", 0)), args.max_total_controllers)
                if director.get("action") in {"continue", "discover"}
                else 0
            )
            if (
                director.get("action") == "discover"
                and integration_clean
                and free >= args.min_free_bytes
            ):
                report["actions"].append(
                    _run_discovery(args, root, live, director, lanes)
                )
            failure_state = _load_failure_state(failure_state_path)
            report["actions"].extend(
                _release_stale_claims(root, lanes[0], procs, max_attempts=3)
                if lanes
                else []
            )
            for lane in lanes[1:]:
                report["actions"].extend(
                    _release_stale_claims(root, lane, procs, max_attempts=3)
                )
            with _exclusive_lock(live / "archive.lock", blocking=False) as archive_lock:
                if archive_lock:
                    bucket = _oss_bucket()
                    candidates = {
                        lane.language: [
                            record
                            for record in _lane_records(lane)
                            if record.get("status") == "complete"
                            and isinstance(record.get("package"), str)
                            and (
                                root
                                / ".nl2repo/authoring-live/worktrees"
                                / lane.batch_id
                                / record["package"]
                            ).is_dir()
                            and not _failure_is_in_backoff(
                                failure_state,
                                root
                                / ".nl2repo/authoring-live/worktrees"
                                / lane.batch_id
                                / record["package"],
                                record["package"],
                            )
                        ]
                        for lane in lanes
                        if selected_language in {"all", lane.language}
                    }
                    offsets = {lane.language: 0 for lane in lanes}
                    integration_attempts = 0
                    while integration_attempts < integration_limit:
                        progress = False
                        for lane in lanes:
                            if integration_attempts >= integration_limit:
                                break
                            records = candidates[lane.language]
                            offset = offsets[lane.language]
                            if offset >= len(records):
                                continue
                            offsets[lane.language] += 1
                            record = records[offset]
                            package = record["package"]
                            try:
                                action = _integrate_task(
                                    root,
                                    lane,
                                    package,
                                    record,
                                    procs,
                                    remote=args.remote,
                                    branch=args.branch,
                                    archive_bucket=bucket,
                                    archive_module=archive_module,
                                    receipt_root=live / "archive-receipts",
                                    dry_run=args.dry_run or not integration_clean,
                                    timeout=args.command_timeout,
                                )
                            except Exception as exc:  # noqa: BLE001 - persist task failure
                                error_text = _redact(f"{type(exc).__name__}: {exc}")
                                action = {
                                    "package": package,
                                    "status": "error",
                                    "error": error_text,
                                }
                                report["errors"].append(action)
                            report["actions"].append({"language": lane.language, **action})
                            if action.get("status") == "integrated":
                                failure_state.pop(package, None)
                            elif action.get("status") == "error" and not args.dry_run:
                                try:
                                    failure_state[package] = {
                                        "language": lane.language,
                                        "fingerprint": _failure_key(
                                            root
                                            / ".nl2repo/authoring-live/worktrees"
                                            / lane.batch_id
                                            / package,
                                            package,
                                        ),
                                        "retry_after": time.time()
                                        + args.failure_backoff_seconds,
                                        "error": action.get("error"),
                                        "recorded_at": datetime.now(UTC).isoformat(),
                                    }
                                except (OSError, ValueError):
                                    pass
                            if _integration_attempt(action):
                                integration_attempts += 1
                            progress = True
                        if not progress:
                            break
                    if not args.dry_run:
                        _save_failure_state(failure_state_path, failure_state)
                else:
                    report["actions"].append({"status": "archive-lock-busy"})
            can_start_workers = (
                not args.dry_run
                and integration_clean
                and free >= args.min_free_bytes
                and worker_limit > 0
            )
            if can_start_workers and free >= args.watcher_min_free_bytes:
                current = _watcher_processes(_proc_table())
                if not current and _oss_bucket() is not None:
                    try:
                        pid = _start_watcher(root, lanes, live)
                        report["actions"].append({"status": "watcher-started", "pid": pid})
                    except Exception as exc:  # noqa: BLE001
                        report["errors"].append(
                            {
                                "status": "watcher-start-error",
                                "error": _redact(str(exc)),
                            }
                        )
            if can_start_workers:
                current = _proc_table()
                if args.resume_stopped_controllers:
                    resumed = _resume_stopped_controllers(lanes, current)
                    if resumed:
                        report["actions"].append(
                            {"status": "controllers-resumed", "pids": resumed}
                        )
                        current = _proc_table()
                active_total = sum(
                    len(_controller_slots(lane, current)) for lane in lanes
                )
                lane_records = {
                    lane.language: _lane_records(lane) for lane in lanes
                }
                for slot in range(min(args.workers, worker_limit)):
                    for lane in lanes:
                        if active_total >= args.max_total_controllers:
                            break
                        records = lane_records[lane.language]
                        if not _lane_has_claimable_work(records, max_attempts=3):
                            continue
                        if len(_controller_slots(lane, current)) > slot:
                            continue
                        owner = f"supervisor-{lane.language}-{slot + 1}"
                        try:
                            pid = _start_controller(root, lane, live, owner)
                            active_total += 1
                            report["actions"].append(
                                {
                                    "status": "controller-started",
                                    "language": lane.language,
                                    "pid": pid,
                                }
                            )
                        except Exception as exc:  # noqa: BLE001
                            report["errors"].append(
                                {
                                    "status": "controller-start-error",
                                    "language": lane.language,
                                    "error": _redact(str(exc)),
                                }
                            )
            _atomic_write(report_path, report)
            print(json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)
            if args.once:
                return 1 if report["errors"] else 0
            time.sleep(args.interval_sec)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--live-root", type=Path, default=Path(".nl2repo/authoring-live"))
    parser.add_argument("--queue-root", type=Path, default=Path("/data/NL2RepoBench/reports"))
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument(
        "--max-total-controllers",
        type=int,
        default=DEFAULT_MAX_TOTAL_CONTROLLERS,
    )
    parser.add_argument("--max-integrations", type=int, default=3)
    parser.add_argument("--interval-sec", type=int, default=60)
    parser.add_argument("--command-timeout", type=int, default=1800)
    parser.add_argument("--director-mode", choices=("llm", "rules"), default="llm")
    parser.add_argument("--director-command", default="pi")
    parser.add_argument(
        "--director-provider",
        default=os.environ.get("PI_DIRECTOR_PROVIDER", "z-open-api-gpt-openai-responses"),
    )
    parser.add_argument(
        "--director-model",
        default=os.environ.get("PI_DIRECTOR_MODEL", "gpt-5.6-sol"),
    )
    parser.add_argument(
        "--director-thinking",
        default=os.environ.get("PI_DIRECTOR_THINKING", "medium"),
    )
    parser.add_argument(
        "--director-interval-sec",
        type=int,
        default=DEFAULT_DIRECTOR_INTERVAL_SECONDS,
    )
    parser.add_argument(
        "--director-timeout-sec",
        type=int,
        default=DEFAULT_DIRECTOR_TIMEOUT_SECONDS,
    )
    parser.add_argument("--refresh-director", action="store_true")
    parser.add_argument(
        "--discovery-pool",
        type=Path,
        default=Path("reports/authoring-discovery-pool.json"),
    )
    parser.add_argument(
        "--failure-backoff-seconds",
        type=int,
        default=DEFAULT_FAILURE_BACKOFF_SECONDS,
    )
    parser.add_argument("--min-free-bytes", type=int, default=DEFAULT_MIN_FREE_BYTES)
    parser.add_argument(
        "--watcher-min-free-bytes",
        type=int,
        default=DEFAULT_WATCHER_MIN_FREE_BYTES,
    )
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume-stopped-controllers", action="store_true")
    args = parser.parse_args()
    if (
        args.workers < 1
        or args.max_total_controllers < 1
        or args.max_integrations < 1
        or args.interval_sec < 1
        or args.failure_backoff_seconds < 1
        or args.director_interval_sec < 1
        or args.director_timeout_sec < 1
    ):
        parser.error(
            "workers, max-total-controllers, max-integrations, and interval-sec "
            "must be positive"
        )
    try:
        return supervise(args)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"authoring supervisor failed: {_redact(str(exc))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
