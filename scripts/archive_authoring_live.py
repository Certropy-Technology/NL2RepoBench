#!/usr/bin/env python3
"""Archive completed authoring runs to OSS and remove verified local caches."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

ENDPOINT = "https://oss-ap-southeast-1.aliyuncs.com"
BUCKET = "dingshang-sg"
SECRET_PATTERNS = (
    re.compile(rb"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{40,256}(?![A-Za-z0-9_-])"),
    re.compile(rb"LTAI[A-Za-z0-9]{12,}"),
    re.compile(rb"AKIA[A-Z0-9]{12,}"),
)
REBUILDABLE_PATHS = (
    ".venv",
    "harbor-runner/.venv",
    ".pi/npm",
    ".pi/git",
    "node_modules",
    "tools/node-inventory/node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
)


@dataclass(frozen=True)
class Lane:
    language: str
    batch_id: str
    queue_state: Path


@dataclass(frozen=True)
class ArchiveFile:
    local: Path
    relative: str
    size: int
    sha256: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_lane(raw: str) -> Lane:
    parts = raw.split(":", 2)
    if len(parts) != 3 or parts[0] not in {"python", "node", "go"}:
        raise ValueError("lane must be language:batch-id:queue-state")
    return Lane(parts[0], parts[1], Path(parts[2]).resolve())


def _package_slug(package: str) -> str:
    return quote(package, safe="")


def _secret_shaped(path: Path) -> bool:
    tail = b""
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            data = tail + chunk
            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                return True
            tail = data[-320:]
    return False


def archive_files(worktree: Path, package: str | None = None) -> list[ArchiveFile]:
    """Return trusted receipts, Agent workspaces, and one source snapshot."""

    candidates: list[tuple[Path, str]] = []
    for relative in (
        ".nl2repo/authoring-handoff.json",
        ".nl2repo/authoring-claim.json",
        ".nl2repo/authoring-production-gates.json",
    ):
        path = worktree / relative
        if path.is_file() and not path.is_symlink():
            candidates.append((path, relative))
    for relative in (
        ".nl2repo/evidence",
        ".nl2repo/authoring-evidence",
        ".nl2repo/runs",
        ".nl2repo/authoring-work",
        "jobs",
    ):
        base = worktree / relative
        if not base.is_dir() or base.is_symlink():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            archive_relative = path.relative_to(worktree)
            if relative == ".nl2repo/authoring-work":
                parts = archive_relative.parts
                if "runs" not in parts and "jobs" not in parts:
                    continue
            candidates.append((path, archive_relative.as_posix()))
    if package is not None:
        source_root = worktree / "catalog" / "sources" / package
        if source_root.is_symlink():
            raise ValueError(f"source snapshot is a symlink: catalog/sources/{package}")
        if not source_root.is_dir():
            raise ValueError(f"source snapshot is missing: catalog/sources/{package}")
        for path in sorted(source_root.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            archive_relative = path.relative_to(worktree)
            candidates.append((path, archive_relative.as_posix()))
    files: list[ArchiveFile] = []
    for path, relative in candidates:
        if _secret_shaped(path):
            raise ValueError(f"secret-shaped content blocks archive: {relative}")
        files.append(
            ArchiveFile(
                local=path,
                relative=relative,
                size=path.stat().st_size,
                sha256=_sha256(path),
            )
        )
    return files


def worktrees_with_runs(
    lane: Lane, worktree_root: Path
) -> list[tuple[str, Path, str, str | None, int]]:
    payload = json.loads(lane.queue_state.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, dict):
        raise ValueError(f"queue state has no items: {lane.queue_state}")
    rows: list[tuple[str, Path, str, str | None, int]] = []
    for record in items.values():
        if not isinstance(record, dict) or record.get("status") not in {"pending", "complete"}:
            continue
        package = record.get("package")
        if not isinstance(package, str):
            continue
        worktree = worktree_root / lane.batch_id / package
        has_runs = any(
            (worktree / relative).is_dir()
            and any((worktree / relative).rglob("*"))
            for relative in (".nl2repo/runs", ".nl2repo/authoring-work", "jobs")
        )
        if worktree.is_dir() and (worktree / ".git").exists() and has_runs:
            rows.append(
                (
                    package,
                    worktree,
                    str(record.get("status")),
                    record.get("owner") if isinstance(record.get("owner"), str) else None,
                    int(record.get("attempts", 0)),
                )
            )
    return sorted(rows)


def _process_uses(worktree: Path) -> bool:
    prefix = str(worktree.resolve())
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            cwd = os.path.realpath(entry / "cwd")
        except OSError:
            continue
        if cwd == prefix or cwd.startswith(prefix + os.sep):
            return True
    return False


def _docker_uses(worktree: Path) -> bool:
    completed = subprocess.run(
        ["docker", "ps", "-q"], capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        return True
    ids = completed.stdout.split()
    if not ids:
        return False
    inspected = subprocess.run(
        ["docker", "inspect", *ids], capture_output=True, text=True, check=False
    )
    if inspected.returncode != 0:
        return True
    return str(worktree.resolve()) in inspected.stdout


def task_is_idle(worktree: Path) -> bool:
    return not _process_uses(worktree) and not _docker_uses(worktree)


def cleanup_orphan_containers(lanes: list[Lane], worktree_root: Path) -> list[str]:
    """Remove containers for non-running queue items with no live worktree process."""

    tasks: list[tuple[str, Path, str]] = []
    for lane in lanes:
        payload = json.loads(lane.queue_state.read_text(encoding="utf-8"))
        items = payload.get("items")
        if not isinstance(items, dict):
            continue
        for record in items.values():
            if not isinstance(record, dict):
                continue
            package = record.get("package")
            status = record.get("status")
            if not isinstance(package, str) or status == "running":
                continue
            worktree = (worktree_root / lane.batch_id / package).resolve()
            if worktree.is_dir() and not _process_uses(worktree):
                tasks.append((str(worktree), worktree, str(status)))
    completed = subprocess.run(
        ["docker", "ps", "-q"], capture_output=True, text=True, check=False
    )
    if completed.returncode != 0 or not completed.stdout.split():
        return []
    ids = completed.stdout.split()
    inspected = subprocess.run(
        ["docker", "inspect", *ids], capture_output=True, text=True, check=False
    )
    if inspected.returncode != 0:
        return []
    records = json.loads(inspected.stdout)
    remove: list[str] = []
    for record in records:
        serialized = json.dumps(record, sort_keys=True)
        if any(prefix in serialized for prefix, _worktree, _status in tasks):
            container_id = record.get("Id")
            if isinstance(container_id, str):
                remove.append(container_id)
    if remove:
        removed = subprocess.run(
            ["docker", "rm", "-f", *remove], capture_output=True, text=True, check=False
        )
        if removed.returncode != 0:
            raise RuntimeError(f"orphan container cleanup failed: {removed.stderr[-1000:]}")
    return remove


def _remote_bytes(bucket: Any, key: str) -> tuple[int, str]:
    response = bucket.get_object(key)
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = response.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
        size += len(chunk)
    return size, digest.hexdigest()


def _upload_and_verify(bucket: Any, key: str, file: ArchiveFile) -> None:
    if bucket.object_exists(key):
        size, digest = _remote_bytes(bucket, key)
        if size != file.size or digest != file.sha256:
            raise RuntimeError(f"remote object collision: {key}")
        return
    bucket.put_object_from_file(
        key, str(file.local), headers={"x-oss-meta-sha256": file.sha256}
    )
    size, digest = _remote_bytes(bucket, key)
    if size != file.size or digest != file.sha256:
        raise RuntimeError(f"remote verification failed: {key}")


def _tree_size(path: Path) -> int:
    if not path.exists() or path.is_symlink():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(
        item.stat().st_size
        for item in path.rglob("*")
        if item.is_file() and not item.is_symlink()
    )


def cleanup_verified_task(worktree: Path) -> int:
    """Delete only run payloads and reproducible caches after OSS verification."""

    targets = [worktree / relative for relative in REBUILDABLE_PATHS]
    targets.extend(
        (worktree / ".nl2repo" / name) for name in ("runs", "authoring-work")
    )
    targets.append(worktree / "jobs")
    nl2repo = worktree / ".nl2repo"
    if nl2repo.is_dir():
        targets.extend(
            path
            for path in nl2repo.iterdir()
            if path.is_dir()
            and (
                path.name.startswith(("compiled", "control-bundles", "task-artifacts"))
                or path.name in {"authoring-gate", "test-tmp", "final-compile"}
            )
        )
    removed = 0
    seen: set[Path] = set()
    for path in targets:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen or not path.exists() or path.is_symlink():
            continue
        seen.add(resolved)
        removed += _tree_size(path)
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    return removed


def archive_task(
    bucket: Any,
    *,
    lane: Lane,
    package: str,
    worktree: Path,
    receipt_root: Path,
    workers: int,
    cleanup: bool,
    queue_status: str,
    owner: str | None,
    attempts: int,
) -> dict[str, Any]:
    handoff = worktree / ".nl2repo/authoring-handoff.json"
    if not task_is_idle(worktree):
        return {"package": package, "status": "active"}
    identity = {
        "archive_policy": "source-snapshot-v1",
        "package": package,
        "queue_status": queue_status,
        "owner": owner,
        "attempts": attempts,
        "handoff_sha256": _sha256(handoff) if handoff.is_file() else None,
    }
    identity_digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    receipt = receipt_root / lane.language / f"{_package_slug(package)}-{identity_digest[:16]}.json"
    if receipt.is_file():
        try:
            previous = json.loads(receipt.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            previous = None
        if isinstance(previous, dict) and previous.get("source_snapshot_included") is True:
            return {"package": package, "status": "already-archived", "receipt": str(receipt)}
        receipt.unlink(missing_ok=True)
    files = archive_files(worktree, package)
    prefix = (
        f"nl2repobench/authoring-live/archive/{lane.language}/"
        f"{_package_slug(package)}/{identity_digest}"
    )
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_upload_and_verify, bucket, f"{prefix}/{file.relative}", file): file
            for file in files
        }
        for future in as_completed(futures):
            future.result()
    manifest = {
        "schema_version": "1.0",
        "language": lane.language,
        "package": package,
        "handoff_sha256": identity["handoff_sha256"],
        "queue_status": queue_status,
        "attempts": attempts,
        "object_count": len(files),
        "bytes_verified": sum(file.size for file in files),
        "source_snapshot_included": True,
        "source_file_count": sum(
            1 for file in files if file.relative.startswith("catalog/sources/")
        ),
        "source_bytes": sum(
            file.size for file in files if file.relative.startswith("catalog/sources/")
        ),
        "workspace_file_count": sum(
            1 for file in files if "artifacts/workspace/" in file.relative
        ),
        "workspace_bytes": sum(
            file.size for file in files if "artifacts/workspace/" in file.relative
        ),
        "workspace_policy": "artifacts/workspace included; secret-shaped files block archive",
        "objects": [
            {
                "key": f"{prefix}/{file.relative}",
                "size": file.size,
                "sha256": file.sha256,
            }
            for file in files
        ],
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    manifest_temp = receipt.with_suffix(".manifest.json.tmp")
    manifest_temp.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    try:
        manifest_key = f"{prefix}/manifest.json"
        manifest_file = ArchiveFile(
            manifest_temp, "manifest.json", manifest_temp.stat().st_size, _sha256(manifest_temp)
        )
        _upload_and_verify(bucket, manifest_key, manifest_file)
        receipt.write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
    finally:
        manifest_temp.unlink(missing_ok=True)
    removed = cleanup_verified_task(worktree) if cleanup else 0
    return {
        "package": package,
        "status": "archived",
        "objects": len(files),
        "bytes_verified": manifest["bytes_verified"],
        "bytes_removed": removed,
        "receipt": str(receipt),
    }


def run_once(args: argparse.Namespace, bucket: Any) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if args.cleanup_orphan_containers:
        removed = cleanup_orphan_containers(args.lane, args.worktree_root)
        results.append(
            {
                "language": "all",
                "package": "<orphan-containers>",
                "status": "cleaned",
                "containers_removed": len(removed),
            }
        )
    for lane in args.lane:
        for package, worktree, queue_status, owner, attempts in worktrees_with_runs(
            lane, args.worktree_root
        ):
            try:
                result = archive_task(
                    bucket,
                    lane=lane,
                    package=package,
                    worktree=worktree,
                    receipt_root=args.receipt_root,
                    workers=args.workers,
                    cleanup=args.cleanup,
                    queue_status=queue_status,
                    owner=owner,
                    attempts=attempts,
                )
            except Exception as exc:  # noqa: BLE001 - one task must not stop the watcher
                result = {"package": package, "status": "error", "error": str(exc)}
            results.append({"language": lane.language, **result})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", action="append", type=_parse_lane, required=True)
    parser.add_argument("--worktree-root", type=Path, required=True)
    parser.add_argument("--receipt-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--interval-sec", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--cleanup-orphan-containers", action="store_true")
    parser.add_argument("--lock-file", type=Path, required=True)
    args = parser.parse_args()
    args.worktree_root = args.worktree_root.resolve()
    args.receipt_root = args.receipt_root.resolve()
    args.lock_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        import oss2  # type: ignore[import-untyped]
    except ImportError:
        print("install oss2 before archiving", file=sys.stderr)
        return 2
    key_id = os.environ.get("OSS_ACCESS_KEY_ID")
    key_secret = os.environ.get("OSS_ACCESS_KEY_SECRET")
    if not key_id or not key_secret:
        print("OSS credentials are missing", file=sys.stderr)
        return 2
    bucket = oss2.Bucket(oss2.Auth(key_id, key_secret), ENDPOINT, BUCKET)
    with args.lock_file.open("a+", encoding="utf-8") as lock:
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                if args.once:
                    print("another authoring archive watcher owns the lock", file=sys.stderr)
                    return 2
                time.sleep(args.interval_sec)
                continue
            try:
                results = run_once(args, bucket)
                print(json.dumps({"results": results}, sort_keys=True), flush=True)
                if args.once:
                    return 1 if any(result.get("status") == "error" for result in results) else 0
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)
            time.sleep(args.interval_sec)


if __name__ == "__main__":
    raise SystemExit(main())
