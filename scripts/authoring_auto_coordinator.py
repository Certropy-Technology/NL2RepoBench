#!/usr/bin/env python3
"""Keep the direct authoring fleet supplied with versioned discovery lanes.

This process is deliberately separate from the integration supervisor.  The
integration supervisor owns the checkout, generated projections, OSS archive,
and worktree removal.  This coordinator owns only discovery lanes and direct
authoring loop processes.  It never edits catalog sources or generated tasks.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SAFE_PACKAGE = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*|@[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)$"
)
LANGUAGES = ("python", "node", "go")
TERMINAL_ATTEMPTS = 3
DEFAULT_MAX_AGENTS = 8
DEFAULT_PENDING_THRESHOLD = 20
DEFAULT_DISCOVERY_BATCH_SIZE = 4
DEFAULT_DISCOVERY_COOLDOWN_SECONDS = 900
DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_AGENT_TIMEOUT_SECONDS = 14_400
DEFAULT_LEASE_SECONDS = 18_000
DEFAULT_MIN_FREE_BYTES = 12 * 1024**3
GO_POOL_FALLBACK: dict[str, str] = {
    "go-brotli": "andybalholm/brotli",
    "go-colorable": "mattn/go-colorable",
    "go-difflib": "sergi/go-diff",
    "go-ini": "go-ini/ini",
    "go-isatty": "mattn/go-isatty",
    "go-ordered-map": "iancoleman/orderedmap",
    "go-pkg-errors": "pkg/errors",
    "go-runewidth": "mattn/go-runewidth",
    "go-errgroup": "golang/sync",
    "go-jwt": "golang-jwt/jwt",
    "go-logrus": "sirupsen/logrus",
    "go-metrics": "rcrowley/go-metrics",
    "go-nanoid": "matoous/go-nanoid",
    "go-set": "deckarep/golang-set",
    "go-version": "hashicorp/go-version",
    "go-zerolog": "rs/zerolog",
}


@dataclass(frozen=True)
class Lane:
    language: str
    batch_id: str
    queue: Path
    plan: Path
    state: Path


@dataclass
class History:
    packages: set[str] = field(default_factory=set)
    candidate_ids: set[str] = field(default_factory=set)
    identities: set[str] = field(default_factory=set)
    revisions: set[tuple[str, str]] = field(default_factory=set)
    licenses: set[tuple[str, str, str]] = field(default_factory=set)
    source_digests: set[str] = field(default_factory=set)
    fingerprints: set[str] = field(default_factory=set)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
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


def _audit(live: Path, event: dict[str, Any]) -> None:
    path = live / "supervisor/auto-coordinator-audit.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {"schema_version": "1.0", "recorded_at": _now(), **event},
        ensure_ascii=False,
        sort_keys=True,
    )
    with _exclusive_lock(path.with_suffix(path.suffix + ".lock")):
        with path.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")
            stream.flush()
            os.fsync(stream.fileno())


def _run(command: list[str], *, cwd: Path, timeout: int) -> dict[str, Any]:
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
        return {"command": command, "exit_code": 124, "timeout": True, "output": str(exc)}
    output = (completed.stdout or completed.stderr or "").strip()
    return {
        "command": command,
        "exit_code": completed.returncode,
        "timeout": False,
        "output": output[-4000:],
    }


def _lane_registry(live: Path) -> list[Lane]:
    path = live / "supervisor/generated-lanes.json"
    if not path.is_file():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("generated lane registry must be a list")
    lanes: list[Lane] = []
    for record in value:
        if not isinstance(record, dict):
            continue
        fields = ("language", "batch_id", "queue", "plan", "queue_state")
        if not all(isinstance(record.get(field), str) for field in fields):
            continue
        language = str(record["language"])
        if language not in LANGUAGES:
            continue
        lanes.append(
            Lane(
                language=language,
                batch_id=str(record["batch_id"]),
                queue=Path(str(record["queue"])).resolve(),
                plan=Path(str(record["plan"])).resolve(),
                state=Path(str(record["queue_state"])).resolve(),
            )
        )
    return lanes


def _state_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        value = _load_json(path).get("items", {})
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return []
    if not isinstance(value, dict):
        return []
    return [record for record in value.values() if isinstance(record, dict)]


def _catalog_packages(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }


def _metadata(
    value: dict[str, Any],
) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    source_value = value.get("source")
    source = source_value if isinstance(source_value, dict) else {}
    package = value.get("package") or value.get("task_id")
    upstream = value.get("upstream_url") or source.get("upstream_url")
    revision = (
        value.get("source_revision")
        or value.get("revision")
        or source.get("revision")
    )
    license_spdx = value.get("license_spdx") or source.get("license_spdx")
    source_digest = value.get("source_digest") or source.get("source_digest")
    return tuple(
        item if isinstance(item, str) and item else None
        for item in (package, upstream, revision, license_spdx, source_digest)
    )  # type: ignore[return-value]


def _fingerprint(
    package: str | None,
    upstream: str | None,
    revision: str | None,
    license_spdx: str | None,
    source_digest: str | None,
) -> str:
    payload = json.dumps(
        {
            "package": package,
            "upstream_url": upstream.rstrip("/") if upstream else None,
            "revision": revision,
            "license_spdx": license_spdx,
            "source_digest": source_digest,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _history(root: Path, live: Path) -> History:
    history = History(packages=_catalog_packages(root / "catalog/sources"))
    for state_path in (live / "queues").glob("*.json"):
        for record in _state_records(state_path):
            package, upstream, revision, license_spdx, source_digest = _metadata(record)
            candidate_id = record.get("candidate_id")
            if isinstance(candidate_id, str):
                history.candidate_ids.add(candidate_id)
            if package:
                history.packages.add(package)
            if upstream:
                history.identities.add(upstream.rstrip("/"))
            if upstream and revision:
                history.revisions.add((upstream.rstrip("/"), revision))
            if package and upstream and license_spdx:
                history.licenses.add((package, upstream.rstrip("/"), license_spdx))
            if source_digest:
                history.source_digests.add(source_digest)
            history.fingerprints.add(
                _fingerprint(package, upstream, revision, license_spdx, source_digest)
            )
    for handoff_path in (live / "worktrees").rglob("authoring-handoff.json"):
        try:
            value = _load_json(handoff_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            continue
        package, upstream, revision, license_spdx, source_digest = _metadata(value)
        if package:
            history.packages.add(package)
        if upstream:
            history.identities.add(upstream.rstrip("/"))
        if upstream and revision:
            history.revisions.add((upstream.rstrip("/"), revision))
        if package and upstream and license_spdx:
            history.licenses.add((package, upstream.rstrip("/"), license_spdx))
        if source_digest:
            history.source_digests.add(source_digest)
        history.fingerprints.add(
            _fingerprint(package, upstream, revision, license_spdx, source_digest)
        )
    return history


def _claimable(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if record.get("status") == "pending"
        and int(record.get("attempts", 0)) < TERMINAL_ATTEMPTS
    ]


def _candidate_duplicate(record: dict[str, Any], history: History) -> str | None:
    package, upstream, revision, license_spdx, source_digest = _metadata(record)
    candidate_id = record.get("candidate_id")
    if package and package in history.packages:
        return "package-already-in-catalog-or-history"
    if isinstance(candidate_id, str) and candidate_id in history.candidate_ids:
        return "candidate-id-already-in-history"
    normalized_upstream = upstream.rstrip("/") if upstream else None
    if normalized_upstream and normalized_upstream in history.identities:
        return "upstream-identity-already-in-history"
    if (
        normalized_upstream
        and revision
        and (normalized_upstream, revision) in history.revisions
    ):
        return "revision-already-in-history"
    if source_digest and source_digest in history.source_digests:
        return "source-digest-already-in-history"
    if package and normalized_upstream and license_spdx:
        if (package, normalized_upstream, license_spdx) in history.licenses:
            return "license-fingerprint-already-in-history"
    if _fingerprint(
        package, normalized_upstream, revision, license_spdx, source_digest
    ) in history.fingerprints:
        return "candidate-fingerprint-already-in-history"
    return None


def _load_pool(path: Path) -> dict[str, list[str]]:
    value = _load_json(path)
    pool: dict[str, list[str]] = {}
    for language in LANGUAGES:
        entries = value.get(language, [])
        pool[language] = sorted(
            {
                entry
                for entry in entries
                if isinstance(entry, str) and SAFE_PACKAGE.fullmatch(entry)
            }
        ) if isinstance(entries, list) else []
    return pool


def _select_packages(
    pool: dict[str, list[str]], language: str, history: History, limit: int
) -> list[str]:
    return [
        package for package in pool.get(language, []) if package not in history.packages
    ][:limit]


def _go_repositories(root: Path) -> dict[str, str]:
    path = root / "scripts/authoring_supervisor.py"
    try:
        spec = importlib.util.spec_from_file_location(
            "nl2repo_authoring_supervisor_for_discovery", path
        )
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            value = getattr(module, "GO_DISCOVERY_REPOSITORIES", {})
            if isinstance(value, dict):
                return {str(key): str(item) for key, item in value.items()}
    except (OSError, ImportError, AttributeError, TypeError):
        pass
    return dict(GO_POOL_FALLBACK)


def _register_lane(live: Path, lane: Lane) -> None:
    registry = live / "supervisor/generated-lanes.json"
    lock = registry.with_suffix(registry.suffix + ".lock")
    with _exclusive_lock(lock):
        existing = json.loads(registry.read_text(encoding="utf-8")) if registry.is_file() else []
        if not isinstance(existing, list):
            raise ValueError("generated lane registry must be a list")
        existing.append(
            {
                "language": lane.language,
                "batch_id": lane.batch_id,
                "queue": str(lane.queue),
                "plan": str(lane.plan),
                "queue_state": str(lane.state),
            }
        )
        temporary = registry.with_name(f".{registry.name}.list-tmp")
        try:
            temporary.write_text(
                json.dumps(existing, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            os.replace(temporary, registry)
        finally:
            if temporary.exists():
                temporary.unlink()


def _python_bin(root: Path) -> Path:
    candidate = root / ".venv/bin/python3"
    return candidate if candidate.is_file() else Path(sys.executable)


def _discover_language(
    root: Path,
    live: Path,
    args: argparse.Namespace,
    language: str,
    packages: list[str],
    history: History,
) -> dict[str, Any]:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_path = live / "supervisor/discovery" / f"auto-{language}-{stamp}.json"
    script = root / "scripts" / {
        "python": "discover_python_candidates.py",
        "node": "discover_npm_candidates.py",
        "go": "discover_go_candidates.py",
    }[language]
    discovery_workers = 1 if language == "python" else 4
    command = [
        _python_bin(root),
        script,
        "--output",
        report_path,
        "--workers",
        str(discovery_workers),
    ]
    if language == "go":
        repositories = _go_repositories(root)
        missing = [package for package in packages if package not in repositories]
        if missing:
            return {
                "event": "discovery",
                "language": language,
                "status": "missing-repository-map",
                "packages": packages,
                "missing": missing,
            }
        for package in packages:
            command.extend(("--repository", f"{package}={repositories[package]}"))
    else:
        for package in packages:
            command.extend(("--package", package))
    result = _run([str(item) for item in command], cwd=root, timeout=args.command_timeout_seconds)
    event: dict[str, Any] = {
        "event": "discovery",
        "language": language,
        "packages_requested": packages,
        "report": str(report_path),
        "command": result["command"],
        "exit_code": result["exit_code"],
        "status": "discovery-failed" if result["exit_code"] else "discovered",
        "output": result["output"],
    }
    if result["exit_code"]:
        return event
    build_queue = live / "supervisor/queues" / f"{language}-auto-{stamp}.json"
    built = _run(
        [
            str(_python_bin(root)),
            str(root / "scripts/build_package_queue.py"),
            "--input",
            str(report_path),
            "--catalog-root",
            str(root / "catalog/sources"),
            "--output",
            str(build_queue),
        ],
        cwd=root,
        timeout=args.command_timeout_seconds,
    )
    event["queue_build"] = built
    if built["exit_code"]:
        event["status"] = "queue-build-failed"
        return event
    queue = _load_json(build_queue)
    accepted: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for record in queue.get("queue", []):
        if not isinstance(record, dict) or record.get("status") not in {
            "candidate",
            "needs-evidence",
        }:
            continue
        duplicate_reason = _candidate_duplicate(record, history)
        if duplicate_reason:
            skipped.append(
                {"package": str(record.get("package")), "reason": duplicate_reason}
            )
        else:
            accepted.append(record)
            package_value = record.get("package")
            if isinstance(package_value, str):
                history.packages.add(package_value)
    queue["queue"] = accepted
    queue["counts"] = {
        "candidate": sum(r.get("status") == "candidate" for r in accepted),
        "needs-evidence": sum(r.get("status") == "needs-evidence" for r in accepted),
    }
    _atomic_write(build_queue, queue)
    event["accepted"] = [record.get("package") for record in accepted]
    event["skipped"] = skipped
    if not accepted:
        event["status"] = "discovery-empty"
        return event
    batch_id = f"{language}-author-auto-{stamp}"
    state_path = live / "queues" / f"{batch_id}.json"
    plan_path = live / "plans" / f"{batch_id}.json"
    base_plan = _load_json(live / "plans" / {
        "python": "python-author-wave2-20260828.json",
        "node": "node-author-wave2-20260828.json",
        "go": "go-author-wave2-20260828.json",
    }[language])
    base_plan.update({"batch_id": batch_id, "tasks": [], "status": "planned"})
    _atomic_write(plan_path, base_plan)
    initialized = _run(
        [
            str(_python_bin(root)),
            str(root / "scripts/package_queue_loop.py"),
            "init",
            "--queue",
            str(build_queue),
            "--state",
            str(state_path),
        ],
        cwd=root,
        timeout=120,
    )
    event["state_init"] = initialized
    if initialized["exit_code"]:
        event["status"] = "state-init-failed"
        return event
    lane = Lane(
        language,
        batch_id,
        build_queue.resolve(),
        plan_path.resolve(),
        state_path.resolve(),
    )
    _register_lane(live, lane)
    event.update(
        {
            "status": "lane-created",
            "batch_id": batch_id,
            "queue": str(build_queue),
            "state": str(state_path),
            "plan": str(plan_path),
        }
    )
    return event


def _proc_commands() -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text(encoding="utf-8")
            if stat.rsplit(")", 1)[1].split()[0] == "Z":
                continue
            command = (
                entry.joinpath("cmdline")
                .read_bytes()
                .replace(b"\0", b" ")
                .decode(errors="replace")
                .strip()
            )
        except (OSError, UnicodeDecodeError):
            continue
        rows.append((int(entry.name), command))
    return rows


def _active_workers(root: Path, live: Path) -> list[tuple[int, str]]:
    absolute_state = str((live / "state").resolve())
    relative_state = os.path.relpath(live / "state", root)
    absolute_worktree = str((live / "worktrees").resolve())
    relative_worktree = os.path.relpath(live / "worktrees", root)
    return [
        (pid, command)
        for pid, command in _proc_commands()
        if "run_authoring_loop.py" in command
        and (
            f"--state-root {absolute_state}" in command
            or f"--state-root {relative_state}" in command
        )
        and (
            f"--worktree-root {absolute_worktree}" in command
            or f"--worktree-root {relative_worktree}" in command
        )
    ]


def _start_workers(
    root: Path, live: Path, args: argparse.Namespace
) -> list[dict[str, Any]]:
    active = _active_workers(root, live)
    available = max(0, args.max_agents - len(active))
    if available == 0:
        return []
    lanes = _lane_registry(live)
    capacities = {
        lane.batch_id: len(_claimable(_state_records(lane.state)))
        for lane in lanes
    }
    candidates = [lane for lane in lanes if capacities.get(lane.batch_id, 0) > 0]
    if not candidates:
        return []
    python = _python_bin(root)
    started: list[dict[str, Any]] = []
    slot = 0
    while available > 0 and candidates:
        lane = candidates[slot % len(candidates)]
        if capacities[lane.batch_id] <= 0:
            candidates = [item for item in candidates if capacities[item.batch_id] > 0]
            continue
        capacities[lane.batch_id] -= 1
        owner = (
            f"auto-authoring-{lane.language}-{lane.batch_id}-"
            f"{int(time.time())}-{slot}"
        )
        log = live / "logs" / f"{owner}.log"
        output = live / "results" / f"{owner}.json"
        log.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(python),
            str(args.runner),
            "--plan",
            str(lane.plan),
            "--queue",
            str(lane.queue),
            "--queue-state",
            str(lane.state),
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
            str(args.lease_seconds),
            "--max-attempts",
            str(TERMINAL_ATTEMPTS),
            "--refill-queue",
            "--output",
            str(output),
            "--provider",
            args.provider,
            "--model",
            args.model,
            "--thinking",
            args.thinking,
            "--models-file",
            str(Path.home() / ".pi/agent/models.json"),
            "--session-root",
            str(live / "sessions"),
            "--agent-timeout-sec",
            str(args.agent_timeout_seconds),
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
        started.append(
            {
                "event": "worker-start",
                "language": lane.language,
                "batch_id": lane.batch_id,
                "owner": owner,
                "pid": process.pid,
                "command": command,
                "log": str(log),
                "output": str(output),
            }
        )
        available -= 1
        slot += 1
    return started


def _load_runtime_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"last_discovery_epoch": {}}
    try:
        value = _load_json(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return {"last_discovery_epoch": {}}
    value.setdefault("last_discovery_epoch", {})
    return value


def _cycle(
    root: Path,
    live: Path,
    args: argparse.Namespace,
    runtime_state: dict[str, Any],
) -> dict[str, Any]:
    lanes = _lane_registry(live)
    history = _history(root, live)
    counts = {language: 0 for language in LANGUAGES}
    for lane in lanes:
        counts[lane.language] += len(_claimable(_state_records(lane.state)))
    pending_total = sum(counts.values())
    event: dict[str, Any] = {
        "event": "cycle",
        "pending_by_language": counts,
        "pending_total": pending_total,
        "active_workers_before": len(_active_workers(root, live)),
        "threshold": args.pending_threshold,
    }
    discovery_events: list[dict[str, Any]] = []
    if pending_total <= args.pending_threshold and not args.dry_run:
        pool = _load_pool(args.discovery_pool)
        for language in LANGUAGES:
            last = float(runtime_state.get("last_discovery_epoch", {}).get(language, 0))
            if time.time() - last < args.discovery_cooldown_seconds:
                continue
            packages = _select_packages(pool, language, history, args.discovery_batch_size)
            if not packages:
                discovery_events.append(
                    {
                        "event": "discovery",
                        "language": language,
                        "status": "pool-exhausted",
                    }
                )
                runtime_state["last_discovery_epoch"][language] = time.time()
                continue
            discovery_event = _discover_language(
                root, live, args, language, packages, history
            )
            discovery_events.append(discovery_event)
            if discovery_event.get("status") in {
                "discovery-failed",
                "queue-build-failed",
                "state-init-failed",
            }:
                runtime_state["last_discovery_epoch"][language] = (
                    time.time()
                    - args.discovery_cooldown_seconds
                    + min(args.discovery_cooldown_seconds, 300)
                )
            else:
                runtime_state["last_discovery_epoch"][language] = time.time()
    started = [] if args.dry_run else _start_workers(root, live, args)
    event["discoveries"] = discovery_events
    event["workers_started"] = started
    event["active_workers_after"] = len(_active_workers(root, live))
    return event


def supervise(args: argparse.Namespace) -> int:
    root = args.repository_root.resolve()
    live = (root / args.live_root).resolve()
    args.discovery_pool = (
        (root / args.discovery_pool).resolve()
        if not args.discovery_pool.is_absolute()
        else args.discovery_pool.resolve()
    )
    args.runner = args.runner.resolve()
    state_path = live / "supervisor/auto-coordinator-state.json"
    lock_path = live / "supervisor/auto-coordinator.lock"
    with _exclusive_lock(lock_path):
        runtime_state = _load_runtime_state(state_path)
        while True:
            if not args.dry_run:
                status = _run(["git", "status", "--porcelain"], cwd=root, timeout=60)
                if status["exit_code"] or status["output"]:
                    _audit(
                        live,
                        {
                            "event": "cycle-skipped",
                            "reason": "integration-checkout-dirty",
                            "status": status,
                        },
                    )
                elif shutil.disk_usage(root).free < args.min_free_bytes:
                    _audit(
                        live,
                        {"event": "cycle-skipped", "reason": "repository-disk-low"},
                    )
                else:
                    event = _cycle(root, live, args, runtime_state)
                    _audit(live, event)
            else:
                _audit(live, _cycle(root, live, args, runtime_state))
            _atomic_write(state_path, runtime_state)
            if args.once:
                return 0
            time.sleep(args.interval_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--live-root", type=Path, default=Path(".nl2repo/authoring-live"))
    parser.add_argument(
        "--discovery-pool",
        type=Path,
        default=Path("reports/authoring-discovery-pool.json"),
    )
    parser.add_argument(
        "--runner",
        type=Path,
        default=Path("/data/pi-tmp/root/c1-runtime/run_authoring_loop.py"),
    )
    parser.add_argument(
        "--provider",
        default=os.environ.get("PI_PROVIDER", "z-open-api-gpt-openai-responses"),
    )
    parser.add_argument("--model", default=os.environ.get("PI_MODEL", "gpt-5.6-sol"))
    parser.add_argument("--thinking", default=os.environ.get("PI_THINKING", "high"))
    parser.add_argument("--max-agents", type=int, default=DEFAULT_MAX_AGENTS)
    parser.add_argument(
        "--pending-threshold", type=int, default=DEFAULT_PENDING_THRESHOLD
    )
    parser.add_argument(
        "--discovery-batch-size", type=int, default=DEFAULT_DISCOVERY_BATCH_SIZE
    )
    parser.add_argument(
        "--discovery-cooldown-seconds",
        type=int,
        default=DEFAULT_DISCOVERY_COOLDOWN_SECONDS,
    )
    parser.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    parser.add_argument(
        "--agent-timeout-seconds", type=int, default=DEFAULT_AGENT_TIMEOUT_SECONDS
    )
    parser.add_argument("--lease-seconds", type=int, default=DEFAULT_LEASE_SECONDS)
    parser.add_argument("--command-timeout-seconds", type=int, default=900)
    parser.add_argument("--min-free-bytes", type=int, default=DEFAULT_MIN_FREE_BYTES)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if (
        not 1 <= args.max_agents <= DEFAULT_MAX_AGENTS
        or args.pending_threshold < 0
        or args.discovery_batch_size < 1
    ):
        parser.error(
            "max-agents must be 1..8; pending-threshold must be non-negative; "
            "discovery-batch-size must be positive"
        )
    if (
        args.agent_timeout_seconds < 1
        or args.lease_seconds <= args.agent_timeout_seconds
        or args.interval_seconds < 1
        or args.discovery_cooldown_seconds < 1
    ):
        parser.error("timeouts, lease, interval, and cooldown values are invalid")
    try:
        return supervise(args)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"authoring auto coordinator failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
