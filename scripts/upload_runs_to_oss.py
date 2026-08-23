#!/usr/bin/env python3
"""Upload NL2RepoBench Harbor tasks and run artifacts to Alibaba Cloud OSS.

The layout mirrors ``itbench-live/`` in the same bucket:

    nl2repobench/README.md
    nl2repobench/harbor-tasks/<task>/...          task definitions
    nl2repobench/runs/<model>/<task>/<trial>/...  model runs
    nl2repobench/runs/oracle/<task>/<trial>/...   Oracle gate evidence

There is no date or campaign level: the newest upload replaces the previous
state for the same object key, and trial directory names stay unique.

Credentials come from the environment and are never written to disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import oss2

ENDPOINT = "https://oss-ap-southeast-1.aliyuncs.com"
BUCKET = "dingshang-sg"
ROOT = "nl2repobench"

ORACLE_PATTERNS = (
    re.compile(r"^oracle-"),
    re.compile(r"^smoke-"),
    re.compile(r"^source-baseline"),
    re.compile(r"^adapter-install"),
)

MODEL_BY_PREFIX = {
    "gpt56-": "gpt-5.6-sol",
    "fable-": "claude-fable-5",
}

TIMESTAMP_DIR = re.compile(r"^\d{4}-\d{2}-\d{2}__\d{2}")
RUN_INDEX_DIR = re.compile(r"^run-?\d+$")

RUN_ROOT_ALIASES = {
    "oracle-rich-gate": "rich-click",
    "oracle-stable-v2": "stable-baselines3",
    "oracle-flask-v2": "flask-restful",
}

# Directory names that only group runs and never name a task.
CONTAINER_DIRS = frozenset({"results", "runs", "jobs", "output"})
INTERNAL_PATH_PARTS = frozenset({".pi-glla", ".git", "__pycache__"})
SECRET_PATTERNS = (
    re.compile(rb"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{40,256}(?![A-Za-z0-9_-])"),
    re.compile(rb"LTAI[A-Za-z0-9]{12,}"),
    re.compile(rb"AKIA[A-Z0-9]{12,}"),
)


def known_tasks(catalog: Path = Path("catalog/tasks")) -> frozenset[str]:
    if not catalog.is_dir():
        return frozenset()
    return frozenset(p.name for p in catalog.iterdir() if p.is_dir())


TASKS = known_tasks()


def has_symlink_component(path: Path) -> bool:
    current = path.absolute()
    parts = current.parts
    cursor = Path(parts[0])
    for part in parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            return True
    return False


def is_oracle_root(name: str) -> bool:
    return any(pattern.search(name) for pattern in ORACLE_PATTERNS)


def task_from_run_root(name: str) -> str:
    if name in RUN_ROOT_ALIASES:
        return RUN_ROOT_ALIASES[name]
    stripped = re.sub(r"^(oracle|smoke)-", "", name)
    for _ in range(4):
        if stripped in TASKS:
            return stripped
        nxt = re.sub(r"-(gate|v\d+|new\d*|retry)$", "", stripped)
        if nxt == stripped:
            break
        stripped = nxt
    return stripped or name


def task_from_prefixed_run(part: str, prefix: str) -> str:
    """Resolve the longest known task prefix before retry/timestamp suffixes."""

    candidate = part[len(prefix) :].removesuffix(".log")
    # Older campaign roots used names such as ``gpt56-new6-markupsafe``.
    # Keep those historical artifacts attributable to the real task while new
    # runs use the unambiguous ``gpt56-markupsafe`` form.
    candidate = re.sub(r"^(?:new\d*|resume\d*)-", "", candidate)
    matches = [task for task in TASKS if candidate == task or candidate.startswith(f"{task}-")]
    if matches:
        return max(matches, key=len)
    candidate = re.sub(r"-(?:retry-)?\d{8}T\d{6}Z$", "", candidate)
    return candidate


def infer_model(run_root: str, rel_parts: tuple[str, ...]) -> str:
    haystack = "/".join((run_root, *rel_parts)).lower()
    if "fable" in haystack or "claude" in haystack:
        return "claude-fable-5"
    if "opus" in haystack:
        return "claude-opus"
    if "gpt" in haystack:
        return "gpt-5.6-sol"
    return "unknown"


def classify(run_root: Path, path: Path) -> tuple[str, str, str]:
    """Return (model, task, trial-relative path) for one artifact."""
    rel_parts = path.relative_to(run_root).parts
    model = "oracle" if is_oracle_root(run_root.name) else ""
    task = ""
    trial_idx = 0

    # A trial directory ends the addressable prefix: anything at or below it is
    # opaque payload (including candidate source trees that may share a task
    # name).  Only segments before it may identify the model or task.
    boundary = len(rel_parts)
    for i, part in enumerate(rel_parts):
        if TIMESTAMP_DIR.match(part) or part.startswith("harbor__"):
            boundary = i
            break
    head_parts = tuple(p for p in rel_parts[:boundary] if p not in CONTAINER_DIRS)

    for i, part in enumerate(head_parts):
        for prefix, model_name in MODEL_BY_PREFIX.items():
            if part.startswith(prefix):
                model = model_name
                task = task_from_prefixed_run(part, prefix)
                trial_idx = i + 1
                break
        if task:
            break

    if not task:
        for i, part in enumerate(head_parts):
            candidate = re.sub(r"-(?:run-)?\d+$", "", part.removesuffix(".log"))
            if candidate in TASKS:
                task = candidate
                trial_idx = i + 1
                break

    if not model:
        model = infer_model(run_root.name, rel_parts)

    if not task:
        head = head_parts[0] if head_parts else ""
        if not head or RUN_INDEX_DIR.match(head) or "." in head:
            task = task_from_run_root(run_root.name)
            trial_idx = 0
        else:
            task = re.sub(r"-(?:run-)?\d+$", "", head)
            trial_idx = 1

    # Drop the identifying segments (and any grouping directories) from the
    # front, keeping the trial directory and everything below it intact.
    remaining = trial_idx
    rest_list: list[str] = []
    for part in rel_parts:
        if remaining and part in CONTAINER_DIRS:
            continue
        if remaining:
            remaining -= 1
            continue
        rest_list.append(part)
    rest = tuple(rest_list)

    # Prefix the trial directory with the run root so repeated runs of the
    # same task stay distinguishable, matching the itbench-live trial naming.
    if rest:
        trial = f"{run_root.name}--{rest[0]}"
        tail = "/".join(rest[1:])
    else:
        trial = run_root.name
        tail = path.name
    return model, task, f"{trial}/{tail}" if tail else trial


@dataclass
class Upload:
    local: Path
    key: str
    size: int

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.local.read_bytes()).hexdigest()


@dataclass
class Stats:
    uploaded: int = 0
    skipped: int = 0
    failed: int = 0
    bytes_sent: int = 0
    errors: list[str] = field(default_factory=list)


def iter_run_uploads(runs_dir: Path) -> Iterator[Upload]:
    if has_symlink_component(runs_dir):
        raise ValueError(f"runs directory contains a symlink component: {runs_dir}")
    for run_root in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        if run_root.is_symlink():
            raise ValueError(f"run root must not be a symlink: {run_root}")
        for path in sorted(run_root.rglob("*")):
            if path.is_symlink() and path.is_dir():
                raise ValueError(f"run directory contains symlink: {path}")
            if path.is_symlink() or not path.is_file() or any(
                part in INTERNAL_PATH_PARTS for part in path.relative_to(run_root).parts
            ):
                continue
            if path == run_root / "queue.log":
                yield Upload(
                    local=path,
                    key=f"{ROOT}/runs/_queue-logs/{run_root.name}--queue.log",
                    size=path.stat().st_size,
                )
                continue
            model, task, rel = classify(run_root, path)
            key = f"{ROOT}/runs/{model}/{task}/{rel}"
            yield Upload(local=path, key=key, size=path.stat().st_size)

    for path in sorted(p for p in runs_dir.glob("*") if p.is_file()):
        key = f"{ROOT}/runs/_queue-logs/{path.name}"
        yield Upload(local=path, key=key, size=path.stat().st_size)


def iter_task_uploads(catalog: Path) -> Iterator[Upload]:
    if has_symlink_component(catalog):
        raise ValueError(f"catalog contains a symlink component: {catalog}")
    for task_dir in sorted(p for p in catalog.iterdir() if p.is_dir()):
        # ``.pi-glla`` and similar control directories can live below the
        # catalog while an agent session is active.  They are never task
        # assets and must not cross the publication boundary.
        if task_dir.name.startswith("."):
            continue
        if task_dir.is_symlink():
            raise ValueError(f"task directory must not be a symlink: {task_dir}")
        for path in sorted(task_dir.rglob("*")):
            if (
                path.is_symlink() and path.is_dir()
            ):
                raise ValueError(f"task directory contains symlink: {path}")
            if (
                path.is_symlink()
                or not path.is_file()
                or any(part in INTERNAL_PATH_PARTS for part in path.relative_to(task_dir).parts)
            ):
                continue
            rel = path.relative_to(task_dir).as_posix()
            key = f"{ROOT}/harbor-tasks/{task_dir.name}/{rel}"
            yield Upload(local=path, key=key, size=path.stat().st_size)


def upload_one(bucket: oss2.Bucket, item: Upload, overwrite: bool) -> str:
    if not overwrite and bucket.object_exists(item.key):
        try:
            existing = bucket.head_object(item.key)
        except Exception as exc:  # noqa: BLE001 - surface collision evidence
            raise RuntimeError(
                f"cannot verify existing object before skip: {item.key}: {exc}"
            ) from exc
        existing_size = getattr(existing, "content_length", None)
        existing_digest = next(
            (
                str(value)
                for key, value in getattr(existing, "headers", {}).items()
                if str(key).casefold() == "x-oss-meta-sha256"
            ),
            None,
        )
        if existing_size != item.size or existing_digest != item.sha256:
            raise RuntimeError(
                f"remote object collision for {item.key}: "
                f"size={existing_size!r}, sha256={existing_digest!r}"
            )
        return "skipped"
    bucket.put_object_from_file(
        item.key,
        str(item.local),
        headers={"x-oss-meta-sha256": item.sha256},
    )
    return "uploaded"


def run_uploads(bucket, items, workers, overwrite, label) -> Stats:
    stats = Stats()
    print(f"{label}: {len(items)} objects, {sum(i.size for i in items) / 1e6:.1f}MB")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(upload_one, bucket, i, overwrite): i for i in items}
        done = 0
        for future in as_completed(futures):
            item = futures[future]
            done += 1
            try:
                outcome = future.result()
            except Exception as exc:  # noqa: BLE001 - report and continue
                stats.failed += 1
                stats.errors.append(f"{item.key}: {exc}")
            else:
                if outcome == "uploaded":
                    stats.uploaded += 1
                    stats.bytes_sent += item.size
                else:
                    stats.skipped += 1
            if done % 1000 == 0 or done == len(items):
                print(
                    f"  {done}/{len(items)} up={stats.uploaded} "
                    f"skip={stats.skipped} fail={stats.failed}",
                    flush=True,
                )
    return stats


def write_manifest(items: list[Upload], destination: Path) -> None:
    """Write a deterministic local manifest before any remote upload."""

    rows = []
    for item in sorted(items, key=lambda value: value.key):
        rows.append({"key": item.key, "size": item.size, "sha256": item.sha256})
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "hash_algorithm": "sha256",
                "objects": rows,
            },
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def secret_shaped_paths(items: list[Upload]) -> list[str]:
    """Scan exact upload files and return paths only, never secret bytes."""

    findings: list[str] = []
    for item in items:
        try:
            with item.local.open("rb") as handle:
                tail = b""
                found = False
                while chunk := handle.read(1024 * 1024):
                    data = tail + chunk
                    if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                        found = True
                        break
                    tail = data[-320:]
        except OSError:
            continue
        if found:
            findings.append(str(item.local))
    return findings


def validate_upload_plan(items: list[Upload], remote_manifest_key: str | None) -> None:
    keys = [item.key for item in items]
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate upload keys: {', '.join(duplicates[:10])}")
    if remote_manifest_key and remote_manifest_key in set(keys):
        raise ValueError("remote manifest key collides with a payload key")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", default=".nl2repo/runs", type=Path)
    parser.add_argument("--catalog", default="catalog/tasks", type=Path)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Write a local key/size/SHA-256 manifest before upload or dry-run output.",
    )
    parser.add_argument(
        "--remote-manifest-key",
        help=(
            "Upload the local manifest to this OSS key after payloads succeed. "
            "Required for remote checksum verification."
        ),
    )
    parser.add_argument("--skip-tasks", action="store_true")
    parser.add_argument("--skip-runs", action="store_true")
    parser.add_argument("--readme", type=Path)
    args = parser.parse_args()

    items: list[Upload] = []
    if not args.skip_tasks and args.catalog.is_dir():
        items += list(iter_task_uploads(args.catalog))
    if not args.skip_runs and args.runs_dir.is_dir():
        items += list(iter_run_uploads(args.runs_dir))
    if args.readme and args.readme.is_file():
        items.append(
            Upload(
                local=args.readme,
                key=f"{ROOT}/README.md",
                size=args.readme.stat().st_size,
            )
        )

    try:
        validate_upload_plan(items, args.remote_manifest_key)
    except ValueError as exc:
        print(f"upload plan rejected: {exc}", file=sys.stderr)
        return 2

    secret_paths = secret_shaped_paths(items)
    if secret_paths:
        for path in secret_paths[:20]:
            print(f"secret-shaped content blocks upload: {path}", file=sys.stderr)
        return 2

    if args.manifest:
        write_manifest(items, args.manifest)
        print(f"manifest={args.manifest} objects={len(items)}")

    if args.dry_run:
        print(f"objects={len(items)} bytes={sum(i.size for i in items) / 1e6:.1f}MB")
        for item in items[:20]:
            print(f"  {item.key}")
        if len(items) > 20:
            print(f"  ... {len(items) - 20} more")
        if args.remote_manifest_key and args.manifest:
            print(f"manifest_remote=oss://{BUCKET}/{args.remote_manifest_key}")
        return 0

    try:
        import oss2
    except ImportError:
        print("install the oss2 package before uploading", file=sys.stderr)
        return 2

    key_id = os.environ.get("OSS_ACCESS_KEY_ID")
    key_secret = os.environ.get("OSS_ACCESS_KEY_SECRET")
    if not (key_id and key_secret):
        print("set OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET", file=sys.stderr)
        return 2

    bucket = oss2.Bucket(oss2.Auth(key_id, key_secret), ENDPOINT, BUCKET)
    stats = run_uploads(bucket, items, args.workers, args.overwrite, "upload")

    if stats.failed == 0 and args.manifest and args.remote_manifest_key:
        try:
            manifest_item = Upload(
                local=args.manifest,
                key=args.remote_manifest_key,
                size=args.manifest.stat().st_size,
            )
            outcome = upload_one(bucket, manifest_item, args.overwrite)
            print(f"manifest_remote=oss://{BUCKET}/{args.remote_manifest_key} ({outcome})")
        except Exception as exc:  # noqa: BLE001 - preserve collision evidence
            print(f"manifest upload failed: {exc}", file=sys.stderr)
            return 1

    print(
        f"\nuploaded={stats.uploaded} skipped={stats.skipped} "
        f"failed={stats.failed} sent={stats.bytes_sent / 1e6:.1f}MB"
    )
    for err in stats.errors[:10]:
        print(f"  ERROR {err}", file=sys.stderr)
    return 1 if stats.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
