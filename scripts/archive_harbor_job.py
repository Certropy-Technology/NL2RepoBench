#!/usr/bin/env python3
"""Upload one Harbor job, including the Agent workspace, to OSS."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

ENDPOINT = "https://oss-ap-southeast-1.aliyuncs.com"
BUCKET = "dingshang-sg"
DEFAULT_PREFIX = "nl2repobench/harbor-runs"
MAX_FILES = 100_000
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BYTES = 10 * 1024 * 1024 * 1024
SECRET_PATTERNS = (
    re.compile(rb"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{40,256}(?![A-Za-z0-9_-])"),
    re.compile(rb"LTAI[A-Za-z0-9]{12,}"),
    re.compile(rb"AKIA[A-Z0-9]{12,}"),
)


@dataclass(frozen=True)
class JobFile:
    path: Path
    relative: str
    size: int
    sha256: str


class ArchiveError(RuntimeError):
    """Raised when a Harbor job cannot be safely archived."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _secret_shaped(path: Path) -> bool:
    tail = b""
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            data = tail + chunk
            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                return True
            tail = data[-320:]
    return False


def _active_processes(root: Path) -> list[str]:
    prefix = str(root.resolve())
    active: list[str] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            cwd = os.path.realpath(entry / "cwd")
        except OSError:
            continue
        if cwd == prefix or cwd.startswith(prefix + os.sep):
            active.append(entry.name)
    return active


def collect_job_files(job_dir: Path) -> list[JobFile]:
    if not job_dir.is_dir() or job_dir.is_symlink():
        raise ArchiveError(f"job directory is missing or symlinked: {job_dir}")
    files: list[JobFile] = []
    total = 0
    for path in sorted(job_dir.rglob("*")):
        if path.is_symlink():
            raise ArchiveError(f"job contains a symlink: {path.relative_to(job_dir)}")
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ArchiveError(f"job file exceeds limit: {path.relative_to(job_dir)}")
        total += size
        if total > MAX_TOTAL_BYTES:
            raise ArchiveError("job exceeds total archive size limit")
        if _secret_shaped(path):
            raise ArchiveError(
                f"secret-shaped content blocks archive: {path.relative_to(job_dir)}"
            )
        files.append(JobFile(path, path.relative_to(job_dir).as_posix(), size, _sha256(path)))
        if len(files) > MAX_FILES:
            raise ArchiveError("job exceeds file count limit")
    if not files:
        raise ArchiveError("Harbor job contains no files")
    return files


def _remote_bytes(bucket: object, key: str) -> tuple[int, str]:
    response = bucket.get_object(key)  # type: ignore[attr-defined]
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = response.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
        size += len(chunk)
    return size, digest.hexdigest()


def _upload_and_verify(bucket: object, key: str, item: JobFile) -> None:
    if bucket.object_exists(key):  # type: ignore[attr-defined]
        size, digest = _remote_bytes(bucket, key)
        if size != item.size or digest != item.sha256:
            raise ArchiveError(f"remote object collision: {key}")
        return
    bucket.put_object_from_file(  # type: ignore[attr-defined]
        key, str(item.path), headers={"x-oss-meta-sha256": item.sha256}
    )
    size, digest = _remote_bytes(bucket, key)
    if size != item.size or digest != item.sha256:
        raise ArchiveError(f"remote payload verification failed: {key}")


def _segment(value: str, label: str) -> str:
    if not value or "\n" in value or "\r" in value:
        raise ArchiveError(f"invalid {label}")
    return quote(value, safe="")


def _prefix(value: str) -> str:
    value = value.strip("/")
    parts = value.split("/")
    if not value or any(not part or part in {".", ".."} for part in parts):
        raise ArchiveError("invalid prefix")
    return "/".join(_segment(part, "prefix component") for part in parts)


def archive_job(
    job_dir: Path,
    *,
    model: str,
    task_id: str,
    run_id: str,
    bucket: object,
    prefix: str = DEFAULT_PREFIX,
    workers: int = 8,
    receipt_path: Path | None = None,
) -> dict[str, object]:
    if workers < 1 or workers > 32:
        raise ArchiveError("workers must be between 1 and 32")
    active = _active_processes(job_dir)
    if active:
        raise ArchiveError(f"Harbor job still has active processes: {','.join(active)}")
    files = collect_job_files(job_dir)
    remote_prefix = "/".join(
        (_prefix(prefix), _segment(model, "model"),
         _segment(task_id, "task_id"), _segment(run_id, "run_id"))
    )
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_upload_and_verify, bucket, f"{remote_prefix}/{item.relative}", item): item
            for item in files
        }
        for future in as_completed(futures):
            future.result()
    workspace = [item for item in files if item.relative.startswith("artifacts/workspace/")]
    manifest: dict[str, object] = {
        "schema_version": "1.0",
        "manifest_kind": "harbor-job-archive",
        "model": model,
        "task_id": task_id,
        "run_id": run_id,
        "workspace_included": True,
        "workspace_file_count": len(workspace),
        "workspace_bytes": sum(item.size for item in workspace),
        "object_count": len(files),
        "bytes_verified": sum(item.size for item in files),
        "objects": [
            {"path": item.relative, "key": f"{remote_prefix}/{item.relative}",
             "size": item.size, "sha256": item.sha256}
            for item in files
        ],
    }
    data = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    manifest_path = job_dir.parent / f".{_segment(run_id, 'run_id')}.oss-manifest.json"
    manifest_path.write_bytes(data)
    try:
        manifest_item = JobFile(
            manifest_path, "manifest.json", len(data), hashlib.sha256(data).hexdigest()
        )
        manifest_key = f"{remote_prefix}/manifest.json"
        _upload_and_verify(bucket, manifest_key, manifest_item)
        if receipt_path is None:
            receipt_path = job_dir.parent / "oss-archive-receipts" / (
                f"{_segment(task_id, 'task_id')}-{_segment(run_id, 'run_id')}.json"
            )
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt = {"manifest": manifest, "remote_manifest_key": manifest_key,
                   "remote_manifest_sha256": manifest_item.sha256}
        receipt_path.write_text(
            json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
        return receipt
    finally:
        manifest_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-dir", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--prefix", default=os.environ.get("OSS_HARBOR_ARCHIVE_PREFIX", DEFAULT_PREFIX))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--receipt-path", type=Path, required=True)
    args = parser.parse_args()
    try:
        import oss2  # type: ignore[import-untyped]
        key_id = os.environ.get("OSS_ACCESS_KEY_ID")
        key_secret = os.environ.get("OSS_ACCESS_KEY_SECRET")
        if not key_id or not key_secret:
            raise ArchiveError("OSS credentials are missing; local job was retained")
        bucket = oss2.Bucket(oss2.Auth(key_id, key_secret), ENDPOINT, BUCKET)
        receipt = archive_job(args.job_dir.resolve(), model=args.model, task_id=args.task_id,
                              run_id=args.run_id, bucket=bucket, prefix=args.prefix,
                              workers=args.workers, receipt_path=args.receipt_path)
    except (OSError, ArchiveError, ValueError, ImportError) as exc:
        print(f"Harbor job OSS archive failed; local job retained: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"remote_manifest_key": receipt["remote_manifest_key"],
                      "object_count": receipt["object_count"],
                      "workspace_file_count": receipt["workspace_file_count"],
                      "workspace_bytes": receipt["workspace_bytes"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
