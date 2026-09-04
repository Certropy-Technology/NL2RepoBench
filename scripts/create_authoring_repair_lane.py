#!/usr/bin/env python3
"""Create one versioned, priority repair lane for existing catalog sources."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
import tempfile
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SOURCE_KINDS = {"python": "pypi", "node": "npm", "go": "go-modules"}
BASE_PLANS = {
    "python": "python-author-wave2-20260828.json",
    "node": "node-author-wave2-20260828.json",
    "go": "go-author-wave2-20260828.json",
}
REQUIRED_CONTROLS = (
    "empty",
    "stub",
    "forgery",
    "install-failure",
    "panic",
    "hang",
    "oversized-output",
    "background-process",
    "offline",
)


@contextmanager
def _lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


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


def task_record(repository: Path, package: str, language: str, batch_id: str) -> dict[str, Any]:
    source = repository / "catalog/sources" / package / "task.toml"
    if not source.is_file():
        raise ValueError(f"catalog source is missing: {package}")
    with source.open("rb") as stream:
        payload = tomllib.load(stream)
    metadata = payload.get("metadata")
    actual_language = metadata.get("language") if isinstance(metadata, dict) else None
    if actual_language != language:
        raise ValueError(
            f"catalog source language mismatch: {package}={actual_language!r}, "
            f"expected {language!r}"
        )
    upstream = payload.get("source")
    upstream = upstream if isinstance(upstream, dict) else {}
    return {
        "candidate_id": f"repair-{package}-{batch_id}",
        "package": package,
        "language": language,
        "source_kind": SOURCE_KINDS[language],
        "upstream_url": upstream.get("upstream_url"),
        "revision": upstream.get("revision"),
        "license_spdx": upstream.get("license_spdx"),
        "repair_existing": True,
        "status": None,
    }


def create_lane(
    repository: Path,
    live: Path,
    *,
    language: str,
    batch_id: str,
    packages: list[str],
) -> dict[str, str]:
    if not SAFE_NAME.fullmatch(batch_id):
        raise ValueError(f"unsafe batch id: {batch_id}")
    if len(set(packages)) != len(packages):
        raise ValueError("repair packages must be unique")
    records = [task_record(repository, package, language, batch_id) for package in packages]
    queue = live / "supervisor/queues" / f"{batch_id}.json"
    state = live / "queues" / f"{batch_id}.json"
    plan = live / "plans" / f"{batch_id}.json"
    registry = live / "supervisor/generated-lanes.json"
    for path in (queue, state, plan):
        if path.exists():
            raise ValueError(f"repair lane output already exists: {path}")
    base_plan = json.loads((live / "plans" / BASE_PLANS[language]).read_text(encoding="utf-8"))
    base_plan.update(
        {
            "schema_version": "1.0",
            "batch_id": batch_id,
            "language": language,
            "repair_existing": True,
            "required_production_controls": list(REQUIRED_CONTROLS),
            "stages": [
                "repair-existing-package",
                "validate-source",
                "network-lint",
                "production-compile",
                "oracle-once",
                "controls",
                "controls-passed-handoff",
            ],
            "tasks": records,
            "status": "planned",
        }
    )
    _atomic_write(
        queue,
        {
            "schema_version": "1.0",
            "queue_id": batch_id,
            "language": language,
            "counts": {"repair": len(records)},
            "queue": records,
        },
    )
    _atomic_write(plan, base_plan)
    initialized = subprocess.run(
        [
            str(repository / ".venv/bin/python3"),
            str(repository / "scripts/package_queue_loop.py"),
            "init",
            "--queue",
            str(queue),
            "--state",
            str(state),
        ],
        cwd=repository,
        capture_output=True,
        text=True,
        check=False,
    )
    if initialized.returncode != 0:
        queue.unlink(missing_ok=True)
        plan.unlink(missing_ok=True)
        raise RuntimeError(f"repair queue init failed: {initialized.stderr[-2000:]}")
    lane = {
        "language": language,
        "batch_id": batch_id,
        "queue": str(queue),
        "plan": str(plan),
        "queue_state": str(state),
        "repair_existing": True,
    }
    with _lock(registry.with_suffix(".json.lock")):
        existing = json.loads(registry.read_text(encoding="utf-8")) if registry.is_file() else []
        if not isinstance(existing, list):
            raise ValueError("generated lane registry must be a list")
        if any(item.get("batch_id") == batch_id for item in existing if isinstance(item, dict)):
            raise ValueError(f"repair lane already registered: {batch_id}")
        _atomic_write(registry, [lane, *existing])
    return {"queue": str(queue), "state": str(state), "plan": str(plan), "registry": str(registry)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--live-root", type=Path, default=Path(".nl2repo/authoring-live"))
    parser.add_argument("--language", choices=sorted(SOURCE_KINDS), required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--package", action="append", required=True)
    args = parser.parse_args()
    repository = args.repository_root.resolve()
    live = (repository / args.live_root).resolve()
    try:
        result = create_lane(
            repository,
            live,
            language=args.language,
            batch_id=args.batch_id,
            packages=args.package,
        )
    except (
        OSError,
        ValueError,
        RuntimeError,
        json.JSONDecodeError,
        tomllib.TOMLDecodeError,
    ) as exc:
        print(f"repair lane creation failed: {exc}", file=__import__("sys").stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
