#!/usr/bin/env python3
"""Plan verifier-only private release staging without changing repository state.

The planner is intentionally read-only.  It validates canonical source
manifests, checks referenced private CAS objects by digest and size, and
classifies whether a Node command artifact can be handed to the existing
private-release preparer.  It never materializes a release or changes a
source, generated task, CAS object, service, or SQLite database.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import stat
import tarfile
import tomllib
from pathlib import Path
from typing import Literal

from nl2repobench.domain.canonical_contract import PackageManager, TaskSource
from nl2repobench.domain.canonical_models import ArtifactRef, Visibility
from nl2repobench.verification.node_command_plan import load_node_command_plan

MAX_TASKS = 4096
MAX_REFS_PER_TASK = 32
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_CAS_BYTES = 2 * 1024**3
MAX_TAR_MEMBERS = 10_000
COMMAND_JSON_MEDIA_TYPES = frozenset(
    {
        "application/json",
        "application/vnd.nl2repobench.command-plan+json",
        "application/vnd.nl2repobench.node-command-plan+json",
        "application/vnd.nl2repobench.node-commands+json",
    }
)
COMMAND_ARCHIVE_MEDIA_TYPES = frozenset(
    {
        "application/vnd.nl2repobench.command-plan+tar",
        "application/vnd.nl2repobench.node-command-plan+tar",
        "application/vnd.nl2repobench.node-commands+tar",
    }
)
PRIVATE_ARCHIVE_MEDIA_TYPES = frozenset(
    {
        "application/vnd.nl2repobench.node-tests+tar",
        "application/vnd.nl2repobench.node-tests+gzip",
        "application/vnd.nl2repobench.test-bundle.tar",
        "application/vnd.nl2repobench.oracle+tar",
        "application/vnd.nl2repobench.oracle-bundle.tar",
        "application/vnd.nl2repobench.private-bundle+tar",
    }
)
INTERNAL_INVENTORY = "_nl2repo.bundle-inventory.json"


class BatchPlanningError(ValueError):
    """Raised when planner inputs are unsafe or exceed bounded limits."""


def _digest_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _safe_regular(path: Path, *, max_bytes: int) -> bytes:
    """Read a regular file without following symlinks in its path."""

    absolute = Path(os.path.abspath(path))
    cursor = absolute
    while True:
        if cursor.is_symlink():
            raise BatchPlanningError(f"path contains a symlink: {path}")
        if cursor == cursor.parent:
            break
        cursor = cursor.parent
    descriptor = -1
    try:
        descriptor = os.open(absolute, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise BatchPlanningError(f"path is not a regular file: {path}")
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            data = handle.read(max_bytes + 1)
    except OSError as exc:
        raise BatchPlanningError(f"cannot read file: {path}") from exc
    finally:
        if descriptor != -1:
            os.close(descriptor)
    if len(data) > max_bytes:
        raise BatchPlanningError(f"file exceeds size limit: {path}")
    return data


def _cas_path(cas_root: Path, reference: ArtifactRef) -> Path:
    if reference.visibility is not Visibility.PRIVATE:
        raise BatchPlanningError("planner only accepts private artifact references")
    digest = reference.digest.removeprefix("sha256:")
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise BatchPlanningError(f"invalid artifact digest: {reference.digest}")
    root = Path(os.path.abspath(cas_root))
    if cas_root.is_symlink() or not root.is_dir():
        raise BatchPlanningError(f"CAS root must be a real directory: {cas_root}")
    path = root / digest[:2] / digest
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise BatchPlanningError(f"CAS object path is unsafe: {reference.digest}")
    return path


def _inspect_ref(cas_root: Path, reference: ArtifactRef) -> dict[str, object]:
    """Return bounded CAS identity information, never payload bytes."""

    try:
        path = _cas_path(cas_root, reference)
    except BatchPlanningError as exc:
        return {"digest": reference.digest, "status": "invalid-reference", "reason": str(exc)}
    if not path.is_file():
        return {
            "digest": reference.digest,
            "status": "missing",
            "expected_size_bytes": reference.size_bytes,
        }
    try:
        data = _safe_regular(path, max_bytes=MAX_CAS_BYTES)
    except BatchPlanningError as exc:
        return {"digest": reference.digest, "status": "unsafe", "reason": str(exc)}
    actual = _digest_bytes(data)
    if len(data) != reference.size_bytes or actual != reference.digest:
        return {
            "digest": reference.digest,
            "status": "mismatch",
            "expected_size_bytes": reference.size_bytes,
            "actual_size_bytes": len(data),
            "actual_digest": actual,
        }
    return {
        "digest": reference.digest,
        "status": "available",
        "size_bytes": len(data),
        "media_type": reference.media_type,
    }


def _command_plan_shape(data: bytes, media_type: str, manager: str) -> str:
    candidate_install: Literal["npm-pack-offline-v1", "pnpm-pack-offline-v1"] = (
        "pnpm-pack-offline-v1" if manager == "pnpm" else "npm-pack-offline-v1"
    )

    def normalize_json(raw: bytes) -> bytes:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("command plan must be an object")
        normalized = dict(payload)
        if normalized.get("schema_version") == "2.0":
            normalized["schema_version"] = "1.0"
        normalized.setdefault("identity", "node+" + manager)
        normalized.setdefault("steps", [])
        return json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode() + b"\n"

    if media_type in COMMAND_JSON_MEDIA_TYPES:
        try:
            load_node_command_plan(normalize_json(data), candidate_install=candidate_install)
        except (TypeError, ValueError):
            return "json-invalid"
        if media_type == "application/vnd.nl2repobench.command-plan+json":
            return "canonical-json"
        return "legacy-json"
    if media_type not in COMMAND_ARCHIVE_MEDIA_TYPES:
        return "unsupported-media"
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            members = list(archive)
            plans = []
            for member in members:
                name = member.name.rstrip("/")
                if name in {"", "."}:
                    if member.size != 0:
                        return "archive-invalid"
                    continue
                if name.startswith("./"):
                    name = name[2:]
                if name == INTERNAL_INVENTORY:
                    return "archive-reserved-path"
                if not member.isfile() or name != "command-plan.json":
                    continue
                extracted = archive.extractfile(member)
                if extracted is not None:
                    plans.append(extracted.read(4 * 1024 * 1024 + 1))
    except (OSError, tarfile.TarError):
        return "archive-invalid"
    if len(members) > MAX_TAR_MEMBERS:
        return "archive-too-many-members"
    payload_members = []
    for member in members:
        name = member.name.rstrip("/")
        if name in {"", "."}:
            continue
        if name.startswith("./"):
            name = name[2:]
        if name == INTERNAL_INVENTORY:
            return "archive-reserved-path"
        payload_members.append(name)
    if payload_members != ["command-plan.json"] or len(plans) != 1:
        return "archive-no-unique-command-plan"
    try:
        load_node_command_plan(normalize_json(plans[0]), candidate_install=candidate_install)
    except (TypeError, ValueError):
        return "archive-command-plan-invalid"
    return "legacy-archive-command-plan"


def _artifact_refs(source: TaskSource) -> tuple[tuple[str, ArtifactRef], ...]:
    values: list[tuple[str, ArtifactRef]] = []

    def add(name: str, reference: ArtifactRef | None) -> None:
        if reference is not None:
            values.append((name, reference))

    add("tests.commands_artifact", source.tests.commands_artifact)
    add("tests.protected_paths_artifact", source.tests.protected_paths_artifact)
    add("tests.test_bundle", source.tests.test_bundle)
    add("verifier.bundle", source.verifier.bundle if source.verifier is not None else None)
    add("oracle_bundle", source.oracle_bundle)
    dependency = source.dependencies
    add("dependencies.lock", dependency.lock)
    add("dependencies.offline_store", dependency.offline_store)
    add("dependencies.inventory", dependency.inventory)
    if len(values) > MAX_REFS_PER_TASK:
        raise BatchPlanningError(f"task declares too many private references: {source.task_id}")
    return tuple(values)


def _source_dirs(sources_root: Path) -> tuple[Path, ...]:
    if sources_root.is_symlink() or not sources_root.is_dir():
        raise BatchPlanningError(f"sources root must be a real directory: {sources_root}")
    leaves: list[Path] = []
    for path in sources_root.iterdir():
        if not path.is_dir() or path.is_symlink():
            continue
        if (path / "task.toml").is_file():
            leaves.append(path)
            continue
        if path.name.startswith("@"):
            leaves.extend(
                child
                for child in path.iterdir()
                if child.is_dir() and not child.is_symlink() and (child / "task.toml").is_file()
            )
    directories = tuple(sorted(leaves, key=lambda path: path.relative_to(sources_root).as_posix()))
    if len(directories) > MAX_TASKS:
        raise BatchPlanningError("source count exceeds planner limit")
    return directories


def _plan_task(source_dir: Path, cas_root: Path) -> dict[str, object]:
    source_path = source_dir / "task.toml"
    base: dict[str, object] = {"task_id": source_dir.name, "source_path": str(source_path)}
    try:
        raw = _safe_regular(source_path, max_bytes=MAX_SOURCE_BYTES)
        source = TaskSource.model_validate(tomllib.loads(raw.decode("utf-8")))
    except (BatchPlanningError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        base.update(
            {
                "status": "blocked",
                "classification": "invalid-source",
                "blockers": [f"invalid canonical source: {exc}"],
                "artifacts": [],
            }
        )
        return base
    blockers: list[str] = []
    runtime = source.environment.runtime
    language = runtime.language.value if runtime is not None else source.metadata.language.value
    manager = (
        runtime.package_manager.value
        if runtime is not None
        else source.dependencies.package_manager.value
    )
    if runtime is None:
        blockers.append("environment.runtime is unavailable")
    if source.source.status.value != "known":
        blockers.append("source provenance is not known")
    if source.environment.status != "known":
        blockers.append("environment status is not known")
    policy = source.environment.network_policy
    if policy is None or policy.mode != "no-network" or policy.allowed_hosts:
        blockers.append("staging requires a no-network policy without allowed hosts")
    if source.lifecycle.status.value in {
        "published",
        "piloted",
        "reviewed",
        "controls-passed",
        "oracle-passed",
        "packaged",
    }:
        blockers.append("source is not an unreviewed staging candidate")
    if source.dependencies.status != "unknown":
        blockers.append(
            "dependency status is not unknown; preparer empty-closure assertion is inapplicable"
        )
    if source.dependencies.packages:
        blockers.append(
            "dependency package list is non-empty; empty-closure staging is inapplicable"
        )
    refs = _artifact_refs(source)
    artifact_rows: list[dict[str, object]] = []
    unavailable = 0
    command_shape = "not-applicable"
    for role, reference in refs:
        inspected = _inspect_ref(cas_root, reference)
        row = {"role": role, **inspected}
        if inspected.get("status") != "available":
            unavailable += 1
        if role == "tests.commands_artifact" and inspected.get("status") == "available":
            data = _safe_regular(_cas_path(cas_root, reference), max_bytes=MAX_CAS_BYTES)
            command_shape = _command_plan_shape(data, reference.media_type, manager)
            if command_shape in {
                "json-invalid",
                "archive-invalid",
                "archive-too-many-members",
                "archive-no-unique-command-plan",
                "archive-command-plan-invalid",
                "archive-reserved-path",
                "unsupported-media",
            }:
                blockers.append(f"unsupported command artifact shape: {command_shape}")
        artifact_rows.append(row)
    if unavailable:
        blockers.append(f"{unavailable} private CAS reference(s) unavailable or mismatched")
    if language != "node" or manager != PackageManager.NPM.value:
        blockers.append(f"staging preparer does not support {language}+{manager}")
    if not refs:
        blockers.append("no private artifacts declared")
    required_roles = {"tests.commands_artifact", "tests.test_bundle", "oracle_bundle"}
    missing_roles = sorted(required_roles - {role for role, _reference in refs})
    if missing_roles:
        blockers.append("required private artifacts are missing: " + ", ".join(missing_roles))
    classification = "ready-for-staging" if not blockers else "blocked"
    return {
        "task_id": source.task_id,
        "source_path": str(source_path),
        "status": source.lifecycle.status.value,
        "classification": classification,
        "language": language,
        "package_manager": manager,
        "source_version": source.version,
        "command_artifact_shape": command_shape,
        "artifact_count": len(artifact_rows),
        "artifacts": artifact_rows,
        "blockers": sorted(set(blockers)),
        "staging": {
            "allowed": classification == "ready-for-staging",
            "preparer": "scripts/prepare_private_release.py",
            "source_update": False,
            "oracle": False,
            "controls": False,
        },
    }


def plan_private_release_batch(sources_root: Path, cas_root: Path) -> dict[str, object]:
    """Build a deterministic, bounded staging queue from source/CAS state."""

    rows = [_plan_task(path, cas_root) for path in _source_dirs(sources_root)]
    rows.sort(key=lambda row: str(row["task_id"]))
    counts: dict[str, int] = {}
    for row in rows:
        classification = str(row["classification"])
        counts[classification] = counts.get(classification, 0) + 1
    return {
        "schema_version": "1.0",
        "planner": "private-release-batch-v1",
        "mode": "author-batch",
        "source_root": str(sources_root),
        "cas_root": str(cas_root),
        "task_count": len(rows),
        "counts": {key: counts[key] for key in sorted(counts)},
        "queue": [
            str(row["task_id"]) for row in rows if row["classification"] == "ready-for-staging"
        ],
        "tasks": rows,
        "claims": {
            "source_updates": False,
            "oracle": False,
            "controls": False,
            "publication": False,
        },
    }


def _write_output(path: Path, payload: dict[str, object]) -> None:
    data = (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        + b"\n"
    )
    if len(data) > 16 * 1024 * 1024:
        raise BatchPlanningError("planner output exceeds size limit")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise BatchPlanningError(f"output already exists: {path}")
    descriptor = -1
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    except FileExistsError as exc:
        raise BatchPlanningError(f"output already exists: {path}") from exc
    finally:
        if descriptor != -1:
            os.close(descriptor)
        if temporary.exists():
            temporary.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--cas", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        payload = plan_private_release_batch(args.sources, args.cas)
        _write_output(args.output, payload)
    except (BatchPlanningError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(
        json.dumps(
            {
                "output": str(args.output),
                "task_count": payload["task_count"],
                "counts": payload["counts"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["BatchPlanningError", "main", "plan_private_release_batch"]
