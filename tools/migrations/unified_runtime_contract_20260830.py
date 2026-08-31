#!/usr/bin/env python3
"""Offline v1/v2 -> canonical source migration.

Historical decoding is deliberately confined to this executable.  Runtime
packages must never import it or accept the old field names.
"""

from __future__ import annotations

import argparse
import ctypes
import fcntl
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, cast

import tomli_w
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

from nl2repobench.authoring.network_lint import lint_catalog
from nl2repobench.domain.canonical_contract import TaskSource
from nl2repobench.domain.canonical_models import ArtifactRef, Visibility
from nl2repobench.domain.command_plan import CommandPlan
from nl2repobench.domain.runtime import (
    PackageManager as RuntimePackageManager,
)
from nl2repobench.domain.runtime import (
    RuntimeDiscriminator,
)
from nl2repobench.domain.runtime import (
    RuntimeLanguage as DiscriminatorLanguage,
)
from nl2repobench.package_managers.registry import PackageManagerRegistry
from nl2repobench.storage.artifacts import (
    ArtifactStoreError,
    FileArtifactStore,
    LocalArtifactResolver,
    MigrationArtifactAuthorization,
    PublicArtifactAuthorization,
)
from nl2repobench.storage.canonical_ustar import (
    decode_archive,
    encode_files,
    tree_digest,
    tree_entries,
)
from nl2repobench.storage.materialize import TARGET_MEDIA_TYPES, ArchiveKind

ROOT_NAME = "unified-runtime-20260830"
STATES = {
    "planned",
    "staged-validated",
    "exchange-intent",
    "exchanged-unverified",
    "verified",
    "old-tree-retained",
    "complete",
    "rollback-intent",
    "rolled-back",
    "recovery-required",
}
SELECTED = ("ministats", "canonicalize", "node-pnpm-synthetic", "go-google-uuid")
MAX_LEGACY_ARCHIVE_BYTES = 2 * 1024 * 1024 * 1024
MAX_LEGACY_MEMBERS = 100_000
MAX_LEGACY_MEMBER_BYTES = 512 * 1024 * 1024
MAX_LEGACY_JSON_MEMBERS = 1024
MAX_LEGACY_JSON_MEMBER_BYTES = 4 * 1024 * 1024
MAX_LEGACY_JSON_TOTAL_BYTES = 8 * 1024 * 1024
MAX_LEGACY_PROTECTED_PATHS = 10_000
PRIVATE_STAGING_CONTRACT = Path(__file__).parents[2] / "harbor-runner/private-staging-contract.json"


class MigrationError(RuntimeError):
    def __init__(self, code: str, stage: str, message: str, observed: tuple[str, ...] = ()) -> None:
        self.code, self.stage, self.observed = code, stage, tuple(sorted(observed))[:4]
        super().__init__(message[:4096])


def digest_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def digest_tree(root: Path) -> str:
    h = hashlib.sha256(b"nl2repobench-source-tree-v1\0")
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix().encode()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise MigrationError("ambiguous-tree", "preflight", f"unsafe source member: {relative}")
        raw = relative.encode()
        h.update(b"D" if path.is_dir() else b"F")
        h.update(len(raw).to_bytes(8, "big"))
        h.update(raw)
        if path.is_file():
            data = path.read_bytes()
            h.update(len(data).to_bytes(8, "big"))
            h.update(hashlib.sha256(data).digest())
        else:
            h.update((0).to_bytes(8, "big"))
            h.update(b"\0" * 32)
    return f"sha256:{h.hexdigest()}"


def _ref(value: Any) -> dict[str, Any] | None:
    return dict(value) if isinstance(value, dict) else None


def _toml_safe(value: Any) -> Any:
    """TOML has no null; canonical optional fields are omitted on disk."""
    if isinstance(value, dict):
        return {key: _toml_safe(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [_toml_safe(item) for item in value]
    return value


def _leaf_fields(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in sorted(value.items()):
            path = f"{prefix}.{key}" if prefix else key
            result.update(_leaf_fields(item, path))
        return result
    return {prefix: value}


def _field_mapping(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, str]]:
    old_fields = _leaf_fields(old)
    return [
        {
            "target": target,
            "source": target if target in old_fields else "migration-derived",
            "value_digest": digest_bytes(
                json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
            ),
        }
        for target, value in sorted(_leaf_fields(new).items())
    ]


def transform_lock_artifact(
    artifact_root: Path,
    lock_bytes: bytes,
    *,
    identity: str,
    toolchain_digest: str,
    store_files: dict[str, bytes] | None = None,
    lock_files: dict[str, bytes] | None = None,
    offline_smoke_command_id: str | None = None,
    expected_toolchain: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Repackage legacy lock/closure bytes into the three canonical CAS refs.

    The migration caller supplies the already controlled offline closure.  No
    network operation is hidden in this helper and candidate source bytes are
    never included in ``store_files``.
    """

    if not identity or "+" not in identity:
        raise MigrationError(
            "plan-invalid", "plan", "dependency identity must be language-qualified"
        )
    language, manager = identity.split("+", 1)
    if not offline_smoke_command_id:
        raise MigrationError(
            "plan-invalid", "plan", "dependency closure has no executed offline smoke"
        )
    lock_name = {
        "uv": "requirements.lock.txt",
        "pip": "requirements.lock.txt",
        "npm": "package-lock.json",
        "pnpm": "pnpm-lock.yaml",
        "go-modules": "go.mod",
        "none": None,
    }.get(manager)
    if manager not in {"uv", "pip", "npm", "pnpm", "go-modules", "none"}:
        raise MigrationError("plan-invalid", "plan", f"unsupported dependency identity: {identity}")
    if manager == "none" and language != "python":
        raise MigrationError("plan-invalid", "plan", "only python+none may have a known closure")
    if store_files is None:
        raise MigrationError("plan-invalid", "plan", "offline dependency closure was not prepared")
    lock_files = {} if lock_name is None else (lock_files or {lock_name: lock_bytes})
    if lock_name is not None and lock_name not in lock_files:
        lock_files[lock_name] = lock_bytes
    lock_archive = encode_files(lock_files)
    store_archive = encode_files(store_files)
    store = FileArtifactStore(artifact_root)
    lock_ref = store.put_bytes(
        lock_archive,
        media_type="application/vnd.nl2repobench.package-lock.tar",
        visibility=Visibility.PRIVATE,
    )
    store_ref = store.put_bytes(
        store_archive,
        media_type="application/vnd.nl2repobench.offline-store.tar",
        visibility=Visibility.PRIVATE,
    )
    with tempfile.TemporaryDirectory(prefix="nl2repo-inventory-") as temporary:
        root = Path(temporary)
        for name, data in lock_files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        lock_entries = tree_entries(root)
        shutil.rmtree(root)
        root.mkdir()
        for name, data in store_files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        store_entries = tree_entries(root)

    def inventory(kind: str, ref: Any, entries: Any) -> dict[str, Any]:
        return {
            "archive_kind": kind,
            "archive_digest": ref.digest,
            "tree_digest": tree_digest(entries),
            "entries": [
                {
                    "path": entry.path,
                    "type": entry.type,
                    "mode": entry.mode,
                    "size": entry.size,
                    "sha256": entry.sha256,
                }
                for entry in entries
                if entry.type in {"file", "directory"}
            ],
            "file_count": sum(entry.type == "file" for entry in entries),
            "directory_count": sum(entry.type == "directory" for entry in entries),
            "total_bytes": sum(entry.size for entry in entries),
        }

    payload = {
        "schema_version": "1.0",
        "identity": identity,
        "adapter_version": "f0-migration-1",
        "toolchain_digest": toolchain_digest,
        "lock": inventory("dependency-lock", lock_ref, lock_entries),
        "store": inventory("offline-store", store_ref, store_entries),
        "offline_smoke": {"status": "passed", "command_id": offline_smoke_command_id},
    }
    if not expected_toolchain:
        raise MigrationError("plan-invalid", "plan", "package-manager toolchain is unknown")
    try:
        runtime_identity = RuntimeDiscriminator(
            language=DiscriminatorLanguage(language),
            package_manager=RuntimePackageManager(manager),
        )
        adapter = PackageManagerRegistry.default().resolve(runtime_identity)
        with tempfile.TemporaryDirectory(prefix="nl2repo-adapter-lock-") as lock_temporary:
            lock_root = Path(lock_temporary)
            _write_regular_files(lock_root, lock_files)
            lock_summary = adapter.validate_lock(lock_root, expected_toolchain)
        with tempfile.TemporaryDirectory(prefix="nl2repo-adapter-store-") as store_temporary:
            store_root = Path(store_temporary)
            _write_regular_files(store_root, store_files)
            summary = adapter.validate_offline_store(
                store_root,
                lock_summary,
                payload,
                expected_toolchain,
            )
            if not summary.offline_smoke:
                raise ValueError("adapter did not confirm offline smoke")
    except (OSError, ValueError) as exc:
        raise MigrationError(
            "plan-invalid", "plan", f"package-manager adapter validation failed: {exc}"
        ) from exc
    inventory_ref = store.put_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n",
        media_type="application/vnd.nl2repobench.inventory+json",
        visibility=Visibility.PRIVATE,
    )
    return {
        "lock": lock_ref.model_dump(mode="json"),
        "offline_store": store_ref.model_dump(mode="json"),
        "inventory": inventory_ref.model_dump(mode="json"),
    }


def _runtime(data: dict[str, Any]) -> tuple[str, str, str, str | None]:
    metadata = data.get("metadata", {})
    language = metadata.get("language", "python")
    environment = data.get("environment", {})
    old = environment.get("runtime", {})
    if language == "node":
        return (
            "node",
            str(old.get("runtime", "node")),
            str(old.get("version", "unknown")),
            old.get("package_manager"),
        )
    if language == "go":
        return "go", "go", str(environment.get("runtime_version", "unknown")), "go-modules"
    installer = data.get("dependencies", {}).get("installer")
    manager = installer if installer in {"uv", "pip"} else "none"
    return "python", "cpython", str(environment.get("python_version", "unknown")), manager


def migrate_record(data: dict[str, Any]) -> dict[str, Any]:
    """Convert a decoded historical TOML mapping without reading source bytes."""
    language, runtime, version, manager = _runtime(data)
    environment = dict(data.get("environment", {}))
    environment.pop("python_version", None)
    environment.pop("runtime_version", None)
    environment.pop("network_mode", None)
    environment["runtime"] = {
        "language": language,
        "runtime": runtime,
        "version": version,
        "package_manager": manager or "none",
        "package_manager_version": (
            data.get("environment", {}).get("runtime", {}).get("package_manager_version")
            if language == "node"
            else None
        ),
    }
    environment = {k: v for k, v in environment.items() if v is not None}
    dependencies = dict(data.get("dependencies", {}))
    old_ref = (
        dependencies.get("lock_artifact")
        or dependencies.get("module_bundle")
        or dependencies.get("artifact")
    )
    dependencies.pop("lock_artifact", None)
    dependencies.pop("module_bundle", None)
    dependencies.pop("artifact", None)
    dependencies.pop("installer", None)
    dependencies.pop("ecosystem", None)
    dependencies.pop("consumer", None)
    dependencies.pop("lockfile_name", None)
    dependencies.pop("lockfile_version", None)
    dependencies.pop("package_manager_version", None)
    dependencies.pop("install_mode", None)
    dependencies.pop("lifecycle_scripts", None)
    dependencies.update(
        {
            "status": "known" if old_ref else "unknown",
            "package_manager": manager or "none",
            "lock": _ref(old_ref),
            "offline_store": None,
            "inventory": None,
        }
    )
    tests = dict(data.get("tests", {}))
    if language == "python":
        framework, report = (
            ("custom", "custom-json-v1")
            if "verifier" in data
            else ("pytest", "pytest-junit-xml-v1")
        )
    elif language == "node":
        framework, report = "node:test", "node-test-json-v1"
    else:
        framework, report = "go-bridge", "go-test-json-v1"
    tests = {
        k: v
        for k, v in tests.items()
        if k not in {"framework", "report_format", "commands", "protected_paths"}
    }
    tests.update({"framework": framework, "report_format": report})
    tests.setdefault("expected_total_source", "unknown")
    result = {
        k: v
        for k, v in data.items()
        if k not in {"schema_version", "environment", "dependencies", "tests", "legacy_projection"}
    }
    result.update(
        {
            "schema_version": "1.0",
            "environment": environment,
            "dependencies": dependencies,
            "tests": tests,
        }
    )
    return result


def _source_dirs(root: Path) -> list[Path]:
    result: list[Path] = []
    for task_file in sorted(
        (path for path in root.rglob("task.toml") if path.is_file() and not path.is_symlink()),
        key=lambda path: path.relative_to(root).as_posix().encode(),
    ):
        candidate = task_file.parent
        # A Harbor task asset is nested below a canonical source.  Only the
        # nearest source root owns a task.toml migration record.
        if any((parent / "task.toml").is_file() for parent in candidate.parents if parent != root):
            continue
        result.append(candidate)
    return result


def _source_artifact_refs(source: TaskSource) -> tuple[ArtifactRef, ...]:
    refs = [
        source.dependencies.lock,
        source.dependencies.offline_store,
        source.dependencies.inventory,
        source.tests.commands_artifact,
        source.tests.protected_paths_artifact,
        source.tests.test_bundle,
        source.verifier.bundle if source.verifier is not None else None,
        source.oracle_bundle,
        *source.lifecycle.evidence,
    ]
    return tuple(ref for ref in refs if ref is not None)


def _validate_selected_compiles(staged: Path, artifact_root: Path) -> tuple[dict[str, Any], ...]:
    """Compile each selected task twice, or report the F0.5 blocker explicitly."""

    if not PRIVATE_STAGING_CONTRACT.is_file():
        return tuple(
            {
                "task_id": task_id,
                "status": "blocked",
                "reason": "private-staging-contract-missing",
            }
            for task_id in SELECTED
        )
    toolchains = {
        "ministats": "toolchain.lock.toml",
        "canonicalize": "toolchain.node.lock.toml",
        "node-pnpm-synthetic": "toolchain.node.lock.toml",
        "go-google-uuid": "toolchain.go.lock.toml",
    }
    repository_root = Path(__file__).parents[2]
    results: list[dict[str, Any]] = []
    for task_id in SELECTED:
        digests: list[str] = []
        with tempfile.TemporaryDirectory(prefix=f"nl2repo-selected-{task_id}-") as temporary:
            for attempt in (1, 2):
                output_root = Path(temporary) / f"compile-{attempt}"
                command = [
                    sys.executable,
                    "-m",
                    "nl2repobench",
                    "harbor",
                    "compile",
                    str(staged / task_id),
                    "--output",
                    str(output_root),
                    "--toolchain",
                    str(repository_root / toolchains[task_id]),
                    "--artifact-root",
                    str(artifact_root),
                    "--authorize-task-private-artifacts",
                ]
                completed = subprocess.run(
                    command,
                    cwd=repository_root,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    timeout=1200,
                    check=False,
                )
                if completed.returncode != 0:
                    detail = completed.stderr[-4096:].decode("utf-8", errors="replace")
                    raise MigrationError(
                        "plan-invalid",
                        "plan",
                        f"selected compile failed for {task_id}: {detail}",
                    )
                generated = output_root / task_id
                if not generated.is_dir():
                    raise MigrationError(
                        "plan-invalid", "plan", f"selected compile omitted {task_id}"
                    )
                digests.append(digest_tree(generated))
        if len(set(digests)) != 1:
            raise MigrationError(
                "plan-invalid", "plan", f"selected compile is nondeterministic: {task_id}"
            )
        results.append({"task_id": task_id, "status": "passed", "output_tree_digest": digests[0]})
    return tuple(results)


def validate_staged_tree(
    staged: Path,
    artifact_root: Path,
    *,
    run_selected_compiles: bool = True,
) -> dict[str, Any]:
    """Run every canonical pre-apply validation stage against a mirror."""

    schema = TaskSource.model_json_schema()
    validator = Draft202012Validator(schema)
    store = FileArtifactStore(artifact_root)
    parsed: list[TaskSource] = []
    artifact_digests: set[str] = set()
    seen_ids: set[str] = set()
    for directory in _source_dirs(staged):
        task_file = directory / "task.toml"
        try:
            payload = tomllib.loads(task_file.read_text(encoding="utf-8"))
            validator.validate(payload)
            source = TaskSource.model_validate(payload)
        except Exception as exc:
            raise MigrationError(
                "plan-invalid", "plan", f"canonical source validation failed for {task_file}: {exc}"
            ) from exc
        if source.task_id in seen_ids:
            raise MigrationError("plan-invalid", "plan", f"duplicate task_id: {source.task_id}")
        seen_ids.add(source.task_id)
        instruction = directory / source.instruction
        if instruction.is_symlink() or not instruction.is_file():
            raise MigrationError(
                "plan-invalid", "plan", f"source instruction is missing: {source.task_id}"
            )
        parsed.append(source)
        artifact_digests.update(ref.digest for ref in _source_artifact_refs(source))
    if artifact_digests:
        authorization = MigrationArtifactAuthorization(
            migration_id=ROOT_NAME,
            allowed_digests=frozenset(artifact_digests),
            workspace_root=staged.parent.resolve(),
        )
        resolver = LocalArtifactResolver(store, authorization)
        for source in parsed:
            for ref in _source_artifact_refs(source):
                selected_authorization = (
                    authorization
                    if ref.visibility is Visibility.PRIVATE
                    else PublicArtifactAuthorization(
                        task_id=source.task_id, purpose="migration-validation"
                    )
                )
                resolver.read_bytes(
                    ref,
                    selected_authorization,
                    max_bytes=MAX_LEGACY_ARCHIVE_BYTES,
                )
    network = lint_catalog(staged)
    if network.errors:
        raise MigrationError(
            "plan-invalid",
            "plan",
            "network lint failed: "
            + "; ".join(f"{item.task_id}:{item.rule}" for item in network.errors[:20]),
        )
    compiles = _validate_selected_compiles(staged, artifact_root) if run_selected_compiles else ()
    blocked = [item for item in compiles if item["status"] == "blocked"]
    return {
        "model": {"status": "passed", "task_count": len(parsed)},
        "schema": {"status": "passed", "task_count": len(parsed)},
        "source_validator": {"status": "passed", "task_count": len(parsed)},
        "artifact_resolver": {"status": "passed", "artifact_count": len(artifact_digests)},
        "network_lint": network.as_dict(),
        "selected_compiles": list(compiles),
        "status": "blocked" if blocked else "passed",
        "blockers": sorted({str(item["reason"]) for item in blocked}),
    }


def _legacy_archive_files(data: bytes) -> tuple[dict[str, bytes], dict[str, bytes]]:
    """Boundedly split a legacy dependency archive into lock and store files."""

    if len(data) > MAX_LEGACY_ARCHIVE_BYTES:
        raise MigrationError("plan-invalid", "plan", "legacy dependency archive is too large")
    lock_files: dict[str, bytes] = {}
    store_files: dict[str, bytes] = {}
    total = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            for index, member in enumerate(archive, start=1):
                if index > MAX_LEGACY_MEMBERS:
                    raise ValueError("legacy dependency archive has too many members")
                if member.issym() or member.islnk() or member.isdev():
                    raise ValueError("legacy dependency archive contains unsafe member")
                name = PurePosixPath(member.name)
                if name.is_absolute() or ".." in name.parts:
                    raise ValueError("legacy dependency archive contains unsafe path")
                if member.isdir():
                    continue
                if not member.isfile() or member.size > MAX_LEGACY_MEMBER_BYTES:
                    raise ValueError("legacy dependency archive contains unsupported member")
                total += member.size
                if total > MAX_LEGACY_ARCHIVE_BYTES:
                    raise ValueError("legacy dependency payload exceeds size limit")
                payload = archive.extractfile(member)
                if payload is None:
                    raise ValueError("legacy dependency member cannot be read")
                member_data = payload.read(member.size + 1)
                if len(member_data) != member.size:
                    raise ValueError("legacy dependency member size does not match")
                clean = name.as_posix()
                target = (
                    lock_files
                    if clean in {"package-lock.json", "pnpm-lock.yaml", "go.mod", "go.sum"}
                    else store_files
                )
                if clean in target:
                    raise ValueError("legacy dependency archive contains duplicate path")
                target[clean] = member_data
    except (OSError, tarfile.TarError, ValueError) as exc:
        raise MigrationError(
            "plan-invalid", "plan", f"dependency archive conversion failed: {exc}"
        ) from exc
    return lock_files, store_files


def _legacy_bundle_payload(data: bytes) -> tuple[dict[str, bytes], frozenset[str]]:
    """Read one legacy runtime bundle without changing payload paths or bytes."""

    if len(data) > MAX_LEGACY_ARCHIVE_BYTES:
        raise MigrationError("plan-invalid", "plan", "legacy runtime bundle is too large")
    files: dict[str, bytes] = {}
    executable: set[str] = set()
    total = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            for index, member in enumerate(archive, start=1):
                if index > MAX_LEGACY_MEMBERS:
                    raise ValueError("legacy runtime bundle has too many members")
                if member.issym() or member.islnk() or member.isdev():
                    raise ValueError("legacy runtime bundle contains an unsafe member")
                path = PurePosixPath(member.name.rstrip("/"))
                if path.is_absolute() or not path.parts or ".." in path.parts:
                    raise ValueError("legacy runtime bundle contains an unsafe path")
                if member.isdir():
                    continue
                if not member.isfile() or member.size > MAX_LEGACY_MEMBER_BYTES:
                    raise ValueError("legacy runtime bundle contains an unsupported member")
                total += member.size
                if total > MAX_LEGACY_ARCHIVE_BYTES:
                    raise ValueError("legacy runtime payload exceeds size limit")
                payload = archive.extractfile(member)
                if payload is None:
                    raise ValueError("legacy runtime member cannot be read")
                member_data = payload.read(member.size + 1)
                if len(member_data) != member.size:
                    raise ValueError("legacy runtime member size does not match")
                name = path.as_posix()
                if name == "_nl2repo.bundle-inventory.json" or name in files:
                    raise ValueError("legacy runtime bundle contains a reserved or duplicate path")
                files[name] = member_data
                if member.mode & 0o111:
                    if path.name not in {
                        "test.sh",
                        "solve.sh",
                        "run.py",
                        "contract.sh",
                        "verifier.sh",
                    }:
                        raise ValueError(f"legacy runtime executable is not allowlisted: {name}")
                    executable.add(name)
    except (OSError, tarfile.TarError, ValueError) as exc:
        raise MigrationError(
            "plan-invalid", "plan", f"runtime bundle conversion failed: {exc}"
        ) from exc
    return files, frozenset(executable)


def _legacy_json_payload(data: bytes) -> Any:
    """Decode exactly one bounded JSON payload from a legacy artifact archive."""

    if len(data) > MAX_LEGACY_JSON_TOTAL_BYTES:
        raise MigrationError("plan-invalid", "plan", "legacy JSON artifact is too large")
    try:
        return json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass

    candidates: list[bytes] = []
    total = 0
    paths: set[str] = set()
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            for index, member in enumerate(archive, start=1):
                if index > MAX_LEGACY_JSON_MEMBERS:
                    raise ValueError("legacy JSON artifact has too many members")
                if member.issym() or member.islnk() or member.isdev():
                    raise ValueError("legacy JSON artifact contains an unsafe member")
                path = PurePosixPath(member.name.rstrip("/"))
                if path.is_absolute() or not path.parts or ".." in path.parts or "" in path.parts:
                    raise ValueError("legacy JSON artifact contains an unsafe path")
                if member.isdir():
                    continue
                if not member.isfile() or member.size > MAX_LEGACY_JSON_MEMBER_BYTES:
                    raise ValueError("legacy JSON artifact contains an unsupported member")
                total += member.size
                if total > MAX_LEGACY_JSON_TOTAL_BYTES:
                    raise ValueError("legacy JSON artifact payload exceeds size limit")
                name = path.as_posix()
                if name in paths:
                    raise ValueError("legacy JSON artifact contains a duplicate path")
                paths.add(name)
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError("legacy JSON artifact member cannot be read")
                member_data = stream.read(member.size + 1)
                if len(member_data) != member.size:
                    raise ValueError("legacy JSON artifact member size does not match")
                try:
                    json.loads(member_data)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                candidates.append(member_data)
    except (OSError, tarfile.TarError) as exc:
        raise MigrationError(
            "plan-invalid", "plan", "legacy JSON artifact is not decodable"
        ) from exc
    except ValueError as exc:
        raise MigrationError("plan-invalid", "plan", str(exc)) from exc
    if len(candidates) != 1:
        if len(candidates) > 1:
            raise MigrationError("plan-invalid", "plan", "legacy JSON artifact is ambiguous")
        raise MigrationError("plan-invalid", "plan", "legacy JSON artifact is not decodable")
    return json.loads(candidates[0])


def _canonical_command_plan(
    payload: Any, *, identity: str, report_format: str
) -> dict[str, Any]:
    """Convert old command arrays/records to the one current plan shape."""

    adapter_fields = {
        "python": ("pytest-subprocess-boundary-v1", "pip-target-no-deps-v1"),
        "node+npm": ("node-test-subprocess-boundary-v1", "npm-pack-offline-v1"),
        "node+pnpm": ("node-test-subprocess-boundary-v1", "pnpm-pack-offline-v1"),
        "go+go-modules": ("go-test-subprocess-boundary-v1", "go-modules-offline-v1"),
    }
    language = identity.split("+", 1)[0]
    adapter_identity = language if language == "python" else identity
    try:
        runner, candidate_install = adapter_fields[adapter_identity]
    except KeyError as exc:
        raise MigrationError(
            "plan-invalid", "plan", f"no command-plan adapter for runtime identity {identity}"
        ) from exc
    raw_steps = payload.get("steps") if isinstance(payload, dict) else payload
    if isinstance(payload, dict) and "commands" in payload:
        raw_steps = payload["commands"]
    elif isinstance(payload, dict) and "steps" not in payload:
        raw_steps = []
    if not isinstance(raw_steps, list):
        raise MigrationError("plan-invalid", "plan", "legacy command artifact has no command list")
    if raw_steps:
        raise MigrationError(
            "plan-invalid",
            "setup-not-supported",
            "legacy command steps require the candidate supervisor and cannot be migrated",
        )
    steps: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_steps):
        if isinstance(raw, str):
            argv = shlex.split(raw, posix=True)
            step_id = f"step-{index:04d}"
            cwd, environment, timeout = ".", {}, 600
        elif isinstance(raw, dict):
            argv_value = raw.get("argv", raw.get("command"))
            if isinstance(argv_value, str):
                argv = shlex.split(argv_value, posix=True)
            elif isinstance(argv_value, list) and all(isinstance(item, str) for item in argv_value):
                argv = argv_value
            else:
                raise MigrationError("plan-invalid", "plan", "legacy command step argv is invalid")
            step_id = str(raw.get("step_id") or f"step-{index:04d}")
            cwd = str(raw.get("cwd") or ".")
            environment = raw.get("environment") or {}
            timeout = int(raw.get("timeout_sec") or 600)
        else:
            raise MigrationError("plan-invalid", "plan", "legacy command step is invalid")
        if not argv or cwd.startswith("/") or ".." in PurePosixPath(cwd).parts:
            raise MigrationError("plan-invalid", "plan", "legacy command step is unsafe")
        if not isinstance(environment, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in environment.items()
        ):
            raise MigrationError("plan-invalid", "plan", "legacy command environment is invalid")
        steps.append(
            {
                "step_id": step_id,
                "argv": argv,
                "cwd": cwd,
                "environment": environment,
                "timeout_sec": timeout,
            }
        )
    plan = {
        "schema_version": "1.0",
        "identity": identity,
        "runner": runner,
        "candidate_install": candidate_install,
        "report_format": report_format,
        "test_root": "/tests/private",
        "steps": steps,
    }
    try:
        return CommandPlan.model_validate(plan).model_dump(mode="json")
    except ValueError as exc:
        raise MigrationError(
            "plan-invalid", "plan", f"canonical command plan is invalid: {exc}"
        ) from exc


def _migrate_command_reference(
    artifact_store: FileArtifactStore,
    value: object,
    *,
    identity: str,
    report_format: str,
    task_id: str,
    workspace_root: Path,
) -> dict[str, Any] | None:
    if value is None:
        return None
    try:
        reference = ArtifactRef.model_validate(value)
        authorization = MigrationArtifactAuthorization(
            migration_id=ROOT_NAME,
            allowed_digests=frozenset({reference.digest}),
            workspace_root=workspace_root.resolve(),
        )
        data = artifact_store.read_bytes(reference, authorization, max_bytes=4 * 1024 * 1024)
        plan = _canonical_command_plan(
            _legacy_json_payload(data), identity=identity, report_format=report_format
        )
        return artifact_store.put_bytes(
            json.dumps(plan, sort_keys=True, separators=(",", ":")).encode() + b"\n",
            media_type="application/vnd.nl2repobench.command-plan+json",
            visibility=Visibility.PRIVATE,
        ).model_dump(mode="json")
    except (ArtifactStoreError, OSError, ValueError) as exc:
        raise MigrationError(
            "plan-invalid", "plan", f"command plan unavailable for {task_id}: {exc}"
        ) from exc


def _migrate_protected_reference(
    artifact_store: FileArtifactStore,
    value: object,
    *,
    task_id: str,
    workspace_root: Path,
) -> dict[str, Any] | None:
    if value is None:
        return None
    try:
        reference = ArtifactRef.model_validate(value)
        authorization = MigrationArtifactAuthorization(
            migration_id=ROOT_NAME,
            allowed_digests=frozenset({reference.digest}),
            workspace_root=workspace_root.resolve(),
        )
        data = artifact_store.read_bytes(reference, authorization, max_bytes=1024 * 1024)
        payload = _legacy_json_payload(data)
        paths = payload.get("paths") if isinstance(payload, dict) else payload
        if (
            not isinstance(paths, list)
            or len(paths) > MAX_LEGACY_PROTECTED_PATHS
            or not all(isinstance(item, str) for item in paths)
        ):
            raise MigrationError(
                "plan-invalid", "plan", "legacy protected-path artifact is invalid"
            )
        normalized: set[str] = set()
        for item in paths:
            path = PurePosixPath(item.lstrip("/"))
            if not path.parts or ".." in path.parts or "." in path.parts:
                raise MigrationError("plan-invalid", "plan", "legacy protected path is unsafe")
            normalized.add(path.as_posix())
        protected = {"schema_version": "1.0", "paths": sorted(normalized)}
        return artifact_store.put_bytes(
            json.dumps(protected, sort_keys=True, separators=(",", ":")).encode() + b"\n",
            media_type="application/vnd.nl2repobench.protected-paths+json",
            visibility=Visibility.PRIVATE,
        ).model_dump(mode="json")
    except (ArtifactStoreError, OSError, ValueError) as exc:
        raise MigrationError(
            "plan-invalid", "plan", f"protected paths unavailable for {task_id}: {exc}"
        ) from exc


def repackage_runtime_bundle(
    artifact_store: FileArtifactStore,
    legacy_bytes: bytes,
    *,
    kind: ArchiveKind,
) -> ArtifactRef:
    """Repackage a test, verifier, or Oracle bundle as canonical USTAR."""

    if kind not in {
        ArchiveKind.TEST_BUNDLE,
        ArchiveKind.VERIFIER_BUNDLE,
        ArchiveKind.ORACLE_BUNDLE,
    }:
        raise MigrationError("plan-invalid", "plan", "runtime bundle kind is invalid")
    files, executable = _legacy_bundle_payload(legacy_bytes)
    payload_members = decode_archive(encode_files(files, executable))
    entries = [member.entry for member in payload_members]
    inventory = {
        "schema_version": "1.0",
        "archive_kind": kind.value,
        "tree_digest": tree_digest(entries),
        "entries": [
            {
                "path": entry.path,
                "type": entry.type,
                "mode": entry.mode,
                "size": entry.size,
                "sha256": entry.sha256,
            }
            for entry in entries
        ],
        "file_count": sum(entry.type == "file" for entry in entries),
        "directory_count": sum(entry.type == "directory" for entry in entries),
        "total_bytes": sum(entry.size for entry in entries),
    }
    files["_nl2repo.bundle-inventory.json"] = (
        json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    return artifact_store.put_bytes(
        encode_files(files, executable),
        media_type=TARGET_MEDIA_TYPES[kind],
        visibility=Visibility.PRIVATE,
    )


def _migrate_bundle_reference(
    artifact_store: FileArtifactStore,
    value: object,
    *,
    kind: ArchiveKind,
    task_id: str,
    workspace_root: Path,
) -> dict[str, Any] | None:
    if value is None:
        return None
    try:
        reference = ArtifactRef.model_validate(value)
        authorization = MigrationArtifactAuthorization(
            migration_id=ROOT_NAME,
            allowed_digests=frozenset({reference.digest}),
            workspace_root=workspace_root.resolve(),
        )
        legacy_bytes = artifact_store.read_bytes(
            reference,
            authorization,
            max_bytes=MAX_LEGACY_ARCHIVE_BYTES,
        )
        migrated = repackage_runtime_bundle(artifact_store, legacy_bytes, kind=kind)
    except (ArtifactStoreError, OSError, ValueError) as exc:
        raise MigrationError(
            "plan-invalid",
            "plan",
            f"{kind.value} unavailable for {task_id}: {exc}",
        ) from exc
    return migrated.model_dump(mode="json")


def _write_regular_files(root: Path, files: dict[str, bytes]) -> None:
    for name, data in sorted(files.items()):
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise MigrationError("plan-invalid", "plan", f"unsafe closure path: {name}")
        target = root.joinpath(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            raise MigrationError("plan-invalid", "plan", f"duplicate closure path: {name}")
        target.write_bytes(data)


def _run_smoke(
    argv: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    command_id: str,
) -> str:
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MigrationError(
            "plan-invalid", "plan", f"offline smoke {command_id} could not run: {exc}"
        ) from exc
    if result.returncode != 0:
        detail = result.stderr[-4096:].decode("utf-8", errors="replace")
        raise MigrationError(
            "plan-invalid",
            "plan",
            f"offline smoke {command_id} failed with {result.returncode}: {detail}",
        )
    return command_id


def _prepare_python_closure(
    lock_bytes: bytes,
    *,
    manager: str,
) -> tuple[dict[str, bytes], str, str]:
    """Fetch a hash-locked wheel closure, then prove a fresh offline install."""

    with tempfile.TemporaryDirectory(prefix="nl2repo-python-closure-") as temporary:
        root = Path(temporary)
        lock = root / "requirements.lock.txt"
        store = root / "store"
        smoke = root / "smoke"
        store.mkdir()
        lock.write_bytes(lock_bytes)
        prepare = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--require-hashes",
            "--only-binary=:all:",
            "--dest",
            str(store),
            "--requirement",
            str(lock),
        ]
        _run_smoke(
            prepare,
            cwd=root,
            environment=dict(os.environ),
            command_id=f"python-{manager}-closure-prepare-v1",
        )
        offline_environment = {
            **os.environ,
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        }
        _run_smoke(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-index",
                "--require-hashes",
                "--find-links",
                str(store),
                "--target",
                str(smoke),
                "--requirement",
                str(lock),
            ],
            cwd=root,
            environment=offline_environment,
            command_id=f"python-{manager}-offline-install-v1",
        )
        files = {
            path.relative_to(store).as_posix(): path.read_bytes()
            for path in sorted(store.rglob("*"))
            if path.is_file() and not path.is_symlink()
        }
        pip_version = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split()[1]
        return files, f"python-{manager}-offline-install-v1", pip_version


def _execute_bundle_smoke(
    identity: str,
    *,
    lock_files: dict[str, bytes],
    store_files: dict[str, bytes],
    runtime_version: str,
    package_manager_version: str | None,
) -> tuple[str, str]:
    language, manager = identity.split("+", 1)
    with tempfile.TemporaryDirectory(prefix="nl2repo-bundle-smoke-") as temporary:
        root = Path(temporary)
        _write_regular_files(root, {**store_files, **lock_files})
        environment = dict(os.environ)
        if manager == "npm":
            executable = shutil.which("npm")
            if executable is None:
                raise MigrationError("plan-invalid", "plan", "npm executable is unavailable")
            version = subprocess.run(
                [executable, "--version"], check=True, capture_output=True, text=True
            ).stdout.strip()
            if package_manager_version and version != package_manager_version:
                raise MigrationError("plan-invalid", "plan", "npm toolchain version mismatch")
            environment.update(
                {
                    "npm_config_offline": "true",
                    "npm_config_ignore_scripts": "true",
                    "npm_config_cache": str(root / "npm-cache"),
                }
            )
            command = [executable, "ci", "--offline", "--ignore-scripts", "--audit=false"]
        elif manager == "pnpm":
            executable = shutil.which("pnpm")
            if executable is None:
                raise MigrationError("plan-invalid", "plan", "pnpm executable is unavailable")
            version = subprocess.run(
                [executable, "--version"], check=True, capture_output=True, text=True
            ).stdout.strip()
            if package_manager_version and version != package_manager_version:
                raise MigrationError("plan-invalid", "plan", "pnpm toolchain version mismatch")
            command = [
                executable,
                "install",
                "--offline",
                "--frozen-lockfile",
                "--ignore-scripts",
                "--store-dir",
                str(root / "pnpm-store"),
            ]
        elif manager == "go-modules":
            executable = shutil.which("go")
            if executable is None:
                raise MigrationError("plan-invalid", "plan", "Go executable is unavailable")
            version = (
                subprocess.run(
                    [executable, "env", "GOVERSION"], check=True, capture_output=True, text=True
                )
                .stdout.strip()
                .removeprefix("go")
            )
            if version != runtime_version:
                raise MigrationError("plan-invalid", "plan", "Go toolchain version mismatch")
            environment.update({"GOPROXY": "off", "GOSUMDB": "off", "GOWORK": "off"})
            command = [executable, "list", "-mod=vendor", "all"]
        else:
            raise MigrationError(
                "plan-invalid", "plan", f"unsupported bundle smoke identity: {identity}"
            )
        command_id = f"{language}-{manager}-offline-smoke-v1"
        return (
            _run_smoke(command, cwd=root, environment=environment, command_id=command_id),
            version,
        )


def make_plan(source_root: Path, artifact_root: Path, output: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    dirs = _source_dirs(source_root)
    artifact_store = FileArtifactStore(artifact_root)
    names = {p.name for p in dirs}
    missing = sorted(set(SELECTED) - names)
    if missing:
        raise MigrationError(
            "plan-invalid", "plan", f"selected migration tasks are missing: {', '.join(missing)}"
        )
    if not PRIVATE_STAGING_CONTRACT.is_file():
        raise MigrationError(
            "plan-invalid",
            "plan",
            "private-staging-contract-missing: F0.5 Harbor staging capability is not installed",
        )
    records: list[dict[str, Any]] = []
    task_ids: set[str] = set()
    for directory in dirs:
        try:
            raw = (directory / "task.toml").read_bytes()
            old = tomllib.loads(raw.decode("utf-8"))
            task_id = old.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                raise MigrationError("plan-invalid", "plan", f"missing task_id for {directory}")
            if task_id in task_ids:
                raise MigrationError("plan-invalid", "plan", f"duplicate task_id: {task_id}")
            task_ids.add(task_id)
            new = migrate_record(old)
            dependencies = old.get("dependencies", {})
            old_dependency_ref = (
                dependencies.get("lock_artifact")
                or dependencies.get("module_bundle")
                or dependencies.get("artifact")
            )
            if old_dependency_ref is not None:
                try:
                    reference = ArtifactRef.model_validate(old_dependency_ref)
                    authorization = MigrationArtifactAuthorization(
                        migration_id=ROOT_NAME,
                        allowed_digests=frozenset({reference.digest}),
                        workspace_root=output.parent.resolve(),
                    )
                    legacy_bytes = artifact_store.read_bytes(
                        reference,
                        authorization,
                        max_bytes=MAX_LEGACY_ARCHIVE_BYTES,
                    )
                except (ArtifactStoreError, OSError, ValueError) as exc:
                    raise MigrationError(
                        "plan-invalid",
                        "plan",
                        f"dependency closure unavailable for {task_id}: {exc}",
                    ) from exc
                identity = f"{_runtime(old)[0]}+{_runtime(old)[3] or 'none'}"
                lock_files: dict[str, bytes] | None = None
                store_files: dict[str, bytes] | None = None
                manager = identity.split("+", 1)[1]
                runtime_version = _runtime(old)[2]
                package_manager_version = (
                    old.get("environment", {}).get("runtime", {}).get("package_manager_version")
                    if isinstance(old.get("environment"), dict)
                    else None
                )
                if manager in {"npm", "pnpm", "go-modules"}:
                    lock_files, store_files = _legacy_archive_files(legacy_bytes)
                    lock_name = {
                        "npm": "package-lock.json",
                        "pnpm": "pnpm-lock.yaml",
                        "go-modules": "go.mod",
                    }[manager]
                    if lock_name not in lock_files:
                        raise MigrationError(
                            "plan-invalid",
                            "plan",
                            f"dependency lock is missing for {task_id}: {lock_name}",
                        )
                    lock_bytes = lock_files[lock_name]
                    offline_smoke_command_id, expected_toolchain = _execute_bundle_smoke(
                        identity,
                        lock_files=lock_files,
                        store_files=store_files,
                        runtime_version=runtime_version,
                        package_manager_version=(
                            str(package_manager_version)
                            if package_manager_version is not None
                            else None
                        ),
                    )
                else:
                    lock_bytes = legacy_bytes
                    store_files, offline_smoke_command_id, expected_toolchain = (
                        _prepare_python_closure(lock_bytes, manager=manager)
                    )
                transformed = transform_lock_artifact(
                    artifact_root,
                    lock_bytes,
                    identity=identity,
                    toolchain_digest=digest_bytes(raw),
                    store_files=store_files,
                    lock_files=lock_files,
                    offline_smoke_command_id=offline_smoke_command_id,
                    expected_toolchain=expected_toolchain,
                )
                new["dependencies"].update(transformed)
            test_data = new["tests"]
            old_tests = old.get("tests", {})
            language, _, _, command_manager = _runtime(old)
            commands = old_tests.get("commands", [])
            if commands:
                if not isinstance(commands, list) or any(
                    not isinstance(item, str) for item in commands
                ):
                    raise MigrationError(
                        "plan-invalid", "plan", f"cannot convert test commands for {directory.name}"
                    )
                command_identity = f"{language}+{command_manager or 'none'}"
                try:
                    command_plan = _canonical_command_plan(
                        commands,
                        identity=command_identity,
                        report_format=test_data["report_format"],
                    )
                except (TypeError, ValueError) as exc:
                    raise MigrationError(
                        "plan-invalid",
                        "plan",
                        f"cannot convert test commands for {directory.name}: {exc}",
                    ) from exc
                command_ref = artifact_store.put_bytes(
                    json.dumps(command_plan, sort_keys=True, separators=(",", ":")).encode()
                    + b"\n",
                    media_type="application/vnd.nl2repobench.command-plan+json",
                    visibility=Visibility.PRIVATE,
                )
                test_data["commands_artifact"] = command_ref.model_dump(mode="json")
            elif old_tests.get("commands_artifact") is not None:
                test_data["commands_artifact"] = _migrate_command_reference(
                    artifact_store,
                    old_tests.get("commands_artifact"),
                    identity=f"{language}+{command_manager or 'none'}",
                    report_format=test_data["report_format"],
                    task_id=task_id,
                    workspace_root=output.parent,
                )
            test_data.pop("commands", None)
            protected_paths = old_tests.get("protected_paths", [])
            if protected_paths:
                if (
                    not isinstance(protected_paths, list)
                    or len(protected_paths) > MAX_LEGACY_PROTECTED_PATHS
                    or any(not isinstance(item, str) for item in protected_paths)
                ):
                    raise MigrationError(
                        "plan-invalid",
                        "plan",
                        f"cannot convert protected paths for {directory.name}",
                    )
                protected_ref = artifact_store.put_bytes(
                    json.dumps(
                        {"schema_version": "1.0", "paths": sorted(set(protected_paths))},
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode()
                    + b"\n",
                    media_type="application/vnd.nl2repobench.protected-paths+json",
                    visibility=Visibility.PRIVATE,
                )
                test_data["protected_paths_artifact"] = protected_ref.model_dump(mode="json")
            elif old_tests.get("protected_paths_artifact") is not None:
                test_data["protected_paths_artifact"] = _migrate_protected_reference(
                    artifact_store,
                    old_tests.get("protected_paths_artifact"),
                    task_id=task_id,
                    workspace_root=output.parent,
                )
            test_data.pop("protected_paths", None)

            test_data["test_bundle"] = _migrate_bundle_reference(
                artifact_store,
                old_tests.get("test_bundle"),
                kind=ArchiveKind.TEST_BUNDLE,
                task_id=task_id,
                workspace_root=output.parent,
            )
            verifier = new.get("verifier")
            if isinstance(verifier, dict):
                verifier["bundle"] = _migrate_bundle_reference(
                    artifact_store,
                    verifier.get("bundle"),
                    kind=ArchiveKind.VERIFIER_BUNDLE,
                    task_id=task_id,
                    workspace_root=output.parent,
                )
            new["oracle_bundle"] = _migrate_bundle_reference(
                artifact_store,
                old.get("oracle_bundle"),
                kind=ArchiveKind.ORACLE_BUNDLE,
                task_id=task_id,
                workspace_root=output.parent,
            )
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
            raise MigrationError(
                "plan-invalid", "plan", f"cannot decode {directory.name}: {exc}"
            ) from exc
        records.append(
            {
                "task_id": task_id,
                "source_path": str(directory),
                "relative_path": directory.relative_to(source_root).as_posix(),
                "old_digest": digest_bytes(raw),
                "new_toml": tomli_w.dumps(_toml_safe(new)),
                "field_mapping": _field_mapping(old, new),
            }
        )
    input_digest = digest_tree(source_root)
    mirror = Path(tempfile.mkdtemp(prefix=f".{source_root.name}.unified-", dir=source_root.parent))
    try:
        shutil.copytree(source_root, mirror, dirs_exist_ok=True, symlinks=True)
        for directory in dirs:
            destination = mirror / directory.relative_to(source_root)
            record = next(
                item
                for item in records
                if item["relative_path"] == directory.relative_to(source_root).as_posix()
            )
            (destination / "task.toml").write_text(record["new_toml"], encoding="utf-8")
        output_digest = digest_tree(mirror)
        validation = validate_staged_tree(mirror, artifact_root)
        if validation["status"] != "passed":
            blockers = ", ".join(cast(list[str], validation["blockers"]))
            raise MigrationError("plan-invalid", "plan", blockers)
    finally:
        shutil.rmtree(mirror, ignore_errors=True)
    task_mapping = digest_bytes(json.dumps(records, sort_keys=True, separators=(",", ":")).encode())
    plan = {
        "schema_version": "1.0",
        "input_tree_digest": input_digest,
        "output_tree_digest": output_digest,
        "source_root": str(source_root),
        "artifact_root": str(Path(artifact_root).resolve()),
        "staged_path": str(
            source_root.parent / f".sources.unified-{output_digest.removeprefix('sha256:')[:16]}"
        ),
        "previous_path": str(output.parent / "previous-sources"),
        "task_count": len(records),
        "task_mapping_digest": task_mapping,
        "records": records,
        "mapping_report": [
            {
                "task_id": record["task_id"],
                "source_path": record["relative_path"],
                "old_digest": record["old_digest"],
                "new_digest": digest_bytes(record["new_toml"].encode()),
                "fields": record["field_mapping"],
            }
            for record in records
        ],
        "new_artifact_refs": sorted(
            {
                ref.digest
                for directory in _source_dirs(source_root)
                for ref in _source_artifact_refs(
                    TaskSource.model_validate(
                        tomllib.loads(
                            next(
                                record["new_toml"]
                                for record in records
                                if record["relative_path"]
                                == directory.relative_to(source_root).as_posix()
                            )
                        )
                    )
                )
            }
        ),
        "migration_warnings": cast(dict[str, Any], validation["network_lint"])["findings"],
        "expected_git_diff": [
            {"path": f"{record['relative_path']}/task.toml", "change": "modify"}
            for record in records
        ],
        "validation": validation,
    }
    plan["plan_digest"] = digest_bytes(
        json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(json.dumps(plan, sort_keys=True, indent=2).encode() + b"\n")
    return plan


def _exchange(left: Path, right: Path) -> None:
    if sys.platform != "linux":
        raise MigrationError("exchange-failed", "exchange", "renameat2 exchange requires Linux")
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is None:
        raise MigrationError("exchange-failed", "exchange", "renameat2 is unavailable")
    result = renameat2(-100, os.fsencode(left), -100, os.fsencode(right), 2)
    if result != 0:
        error = ctypes.get_errno()
        raise MigrationError("exchange-failed", "exchange", os.strerror(error))


def _write_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(json.dumps(record, sort_keys=True, indent=2).encode() + b"\n")
    with temporary.open("rb") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def _exclusive_lock(root: Path) -> Iterator[None]:
    root.mkdir(parents=True, exist_ok=True)
    lock_path = root / "migration.lock"
    descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _validate_plan(plan: dict[str, Any], plan_path: Path) -> None:
    required = {
        "schema_version",
        "input_tree_digest",
        "output_tree_digest",
        "source_root",
        "artifact_root",
        "staged_path",
        "previous_path",
        "task_count",
        "task_mapping_digest",
        "records",
        "plan_digest",
    }
    report_fields = {
        "mapping_report",
        "new_artifact_refs",
        "migration_warnings",
        "expected_git_diff",
        "validation",
    }
    if (
        not required.issubset(plan)
        or not set(plan).issubset(required | report_fields)
        or plan.get("schema_version") != "1.0"
    ):
        raise MigrationError("plan-invalid", "preflight", "migration plan shape is invalid")
    unsigned = {key: value for key, value in plan.items() if key != "plan_digest"}
    expected = digest_bytes(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode())
    if plan.get("plan_digest") != expected:
        raise MigrationError("plan-invalid", "preflight", "migration plan digest is invalid")
    records = plan.get("records")
    if not isinstance(records, list) or not records or plan.get("task_count") != len(records):
        raise MigrationError("plan-invalid", "preflight", "migration task count is invalid")
    mapping = digest_bytes(json.dumps(records, sort_keys=True, separators=(",", ":")).encode())
    if mapping != plan.get("task_mapping_digest"):
        raise MigrationError("plan-invalid", "preflight", "migration task mapping is invalid")
    root = plan_path.parent.resolve()
    if plan_path.is_symlink() or not plan_path.resolve().is_relative_to(root):
        raise MigrationError("plan-invalid", "preflight", "migration plan path is unsafe")


def _validate_staged(plan: dict[str, Any], staged: Path) -> None:
    if staged.is_symlink() or digest_tree(staged) != plan["output_tree_digest"]:
        raise MigrationError("staged-changed", "preflight", "staged tree digest mismatch")
    directories = _source_dirs(staged)
    observed: list[str] = []
    for directory in directories:
        task_id = tomllib.loads((directory / "task.toml").read_text(encoding="utf-8")).get(
            "task_id"
        )
        if not isinstance(task_id, str):
            raise MigrationError("staged-changed", "preflight", "staged task ID is invalid")
        observed.append(task_id)
    observed.sort()
    expected = sorted(record["task_id"] for record in plan["records"])
    if observed != expected or len(observed) != plan["task_count"]:
        raise MigrationError("staged-changed", "preflight", "staged task mapping is invalid")
    if "validation" in plan:
        report = validate_staged_tree(staged, Path(plan["artifact_root"]))
        if report != plan["validation"]:
            raise MigrationError(
                "staged-changed", "preflight", "staged validation report differs from plan"
            )


def _allowed_root_for_source(source_root: Path) -> Path:
    """Return the repository/catalog root that bounds one migration record."""

    source_root = source_root.resolve()
    if source_root.parent.name == "catalog":
        return source_root.parent.parent
    return source_root.parent


def _validate_transaction(transaction: dict[str, Any], transaction_path: Path) -> None:
    required = {
        "schema_version",
        "transaction_id",
        "state",
        "plan_path",
        "allowed_root",
        "plan_digest",
        "current_path",
        "staged_path",
        "previous_path",
        "input_tree_digest",
        "output_tree_digest",
        "previous_tree_digest",
        "task_mapping_digest",
        "task_count",
        "filesystem_device",
        "owner_uid",
        "owner_gid",
        "retention_status",
        "last_error",
    }
    if set(transaction) != required or transaction.get("schema_version") != "1.0":
        raise MigrationError("plan-invalid", "recovery", "transaction record shape is invalid")
    if (
        not isinstance(transaction.get("transaction_id"), str)
        or not re.fullmatch(r"[0-9a-f]{32}", transaction["transaction_id"])
        or transaction.get("state") not in STATES
        or transaction.get("retention_status")
        not in {"not-started", "moving", "retained", "removed"}
        or not isinstance(transaction.get("task_count"), int)
        or transaction["task_count"] <= 0
    ):
        raise MigrationError("plan-invalid", "recovery", "transaction identity is invalid")
    for field in (
        "plan_digest",
        "input_tree_digest",
        "output_tree_digest",
        "task_mapping_digest",
    ):
        if not isinstance(transaction.get(field), str) or not re.fullmatch(
            r"sha256:[0-9a-f]{64}", transaction[field]
        ):
            raise MigrationError("plan-invalid", "recovery", f"transaction {field} is invalid")
    current, staged, previous, plan = map(
        Path,
        (
            transaction["current_path"],
            transaction["staged_path"],
            transaction["previous_path"],
            transaction["plan_path"],
        ),
    )
    allowed_root = Path(transaction["allowed_root"])
    if (
        not allowed_root.is_absolute()
        or allowed_root.is_symlink()
        or not allowed_root.is_dir()
        or allowed_root.resolve() != _allowed_root_for_source(current)
    ):
        raise MigrationError("plan-invalid", "recovery", "transaction allowed root is unsafe")
    root = allowed_root.resolve()

    def validate_path(path: Path, *, required: bool) -> Path:
        if not path.is_absolute() or path.is_symlink():
            raise MigrationError("plan-invalid", "recovery", "transaction path is unsafe")
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise MigrationError(
                "plan-invalid", "recovery", "transaction path escapes allowed root"
            )
        cursor = path
        while cursor != root and cursor != cursor.parent:
            if cursor.is_symlink():
                raise MigrationError(
                    "plan-invalid", "recovery", "transaction path contains symlink"
                )
            cursor = cursor.parent
        if required and not path.exists():
            raise MigrationError("plan-invalid", "recovery", "required transaction path is missing")
        if path.exists() and not path.is_dir() and path in {current, staged, previous}:
            raise MigrationError(
                "ambiguous-tree", "recovery", "transaction tree is not a directory"
            )
        return resolved

    validate_path(transaction_path, required=True)
    validate_path(plan, required=True)
    validate_path(current, required=True)
    validate_path(staged, required=False)
    validate_path(previous, required=False)
    if (
        current.parent.resolve() != staged.parent.resolve()
    ):
        raise MigrationError("plan-invalid", "recovery", "transaction paths are unsafe")
    expected_owner = (transaction["owner_uid"], transaction["owner_gid"])
    expected_device = transaction["filesystem_device"]
    for path in (current, staged, previous):
        if not path.exists():
            continue
        status = path.lstat()
        if path.is_symlink() or (status.st_uid, status.st_gid) != expected_owner:
            raise MigrationError("ambiguous-tree", "recovery", "transaction tree owner differs")
        if status.st_dev != expected_device:
            raise MigrationError("ambiguous-tree", "recovery", "transaction tree device differs")
    error = transaction.get("last_error")
    if error is not None:
        if not isinstance(error, dict) or set(error) != {
            "code",
            "stage",
            "message",
            "observed_digests",
        }:
            raise MigrationError("plan-invalid", "recovery", "transaction error is malformed")
        if (
            error.get("code")
            not in {
                "plan-invalid",
                "staged-changed",
                "exchange-failed",
                "verify-failed",
                "rollback-failed",
                "retention-failed",
                "ambiguous-tree",
            }
            or not isinstance(error.get("message"), str)
            or not error["message"]
            or len(error["message"]) > 4096
            or not isinstance(error.get("observed_digests"), (list, tuple))
            or len(error["observed_digests"]) > 4
            or error.get("stage")
            not in {"plan", "preflight", "exchange", "verify", "rollback", "retention", "recovery"}
        ):
            raise MigrationError("plan-invalid", "recovery", "transaction error is invalid")


def _apply_plan_unlocked(plan_path: Path) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    _validate_plan(plan, plan_path)
    current = Path(plan["source_root"]).resolve()
    if current.is_symlink() or not current.is_dir():
        raise MigrationError("staged-changed", "preflight", "current source tree is unsafe")
    if digest_tree(current) != plan["input_tree_digest"]:
        raise MigrationError("staged-changed", "preflight", "source tree changed after planning")
    staged = Path(plan["staged_path"])
    if not staged.is_absolute() or staged.parent.resolve() != current.parent.resolve():
        raise MigrationError(
            "staged-changed", "preflight", "staged tree must be an absolute source sibling"
        )
    if staged.exists() or staged.is_symlink():
        raise MigrationError("staged-changed", "preflight", "staged path already exists")
    previous = Path(plan["previous_path"])
    if (
        not previous.is_absolute()
        or not previous.resolve().is_relative_to(plan_path.parent.resolve())
        or previous.exists()
        or previous.is_symlink()
    ):
        raise MigrationError("staged-changed", "preflight", "retention path is unsafe")
    previous.parent.mkdir(parents=True, exist_ok=True)
    expected_uid, expected_gid = current.stat().st_uid, current.stat().st_gid
    if (expected_uid, expected_gid) != (os.getuid(), os.getgid()):
        raise MigrationError("staged-changed", "preflight", "source tree is not process-owned")
    parents = (current.parent, staged.parent, previous.parent)
    if len({parent.stat().st_dev for parent in parents}) != 1:
        raise MigrationError("staged-changed", "preflight", "migration trees cross filesystems")
    if any(
        (parent.stat().st_uid, parent.stat().st_gid) != (expected_uid, expected_gid)
        for parent in parents
    ):
        raise MigrationError("staged-changed", "preflight", "migration tree ownership differs")
    state_path = plan_path.parent / "transaction.json"
    if state_path.exists():
        existing = json.loads(state_path.read_text(encoding="utf-8"))
        if existing.get("state") not in {"complete", "rolled-back"}:
            raise MigrationError(
                "ambiguous-tree", "preflight", "non-terminal migration transaction exists"
            )
    transaction: dict[str, Any] = {
        "schema_version": "1.0",
        "transaction_id": plan["plan_digest"][7:39],
        "state": "planned",
        "plan_path": str(plan_path.resolve()),
        "allowed_root": str(_allowed_root_for_source(current)),
        "plan_digest": plan["plan_digest"],
        "current_path": str(current),
        "staged_path": str(staged),
        "previous_path": str(previous),
        "input_tree_digest": plan["input_tree_digest"],
        "output_tree_digest": plan["output_tree_digest"],
        "previous_tree_digest": None,
        "task_mapping_digest": plan["task_mapping_digest"],
        "task_count": plan["task_count"],
        "filesystem_device": current.stat().st_dev,
        "owner_uid": expected_uid,
        "owner_gid": expected_gid,
        "retention_status": "not-started",
        "last_error": None,
    }
    _write_record(state_path, transaction)
    try:
        staged.mkdir(parents=True)
        shutil.copytree(current, staged, dirs_exist_ok=True, symlinks=True)
        for directory in _source_dirs(current):
            destination = staged / directory.relative_to(current)
            record = next(
                item
                for item in plan["records"]
                if item["relative_path"] == directory.relative_to(current).as_posix()
            )
            (destination / "task.toml").write_text(record["new_toml"], encoding="utf-8")
        _validate_staged(plan, staged)
        _fsync_directory(staged)
        transaction["state"] = "staged-validated"
        _write_record(state_path, transaction)
        transaction["state"] = "exchange-intent"
        _write_record(state_path, transaction)
        _exchange(current, staged)
        _fsync_directory(current.parent)
        transaction["state"] = "exchanged-unverified"
        _write_record(state_path, transaction)
        if (
            digest_tree(staged) != plan["input_tree_digest"]
            or digest_tree(current) != plan["output_tree_digest"]
        ):
            raise MigrationError("verify-failed", "verify", "post-exchange tree digest mismatch")
        transaction["state"] = "verified"
        _write_record(state_path, transaction)
        previous.parent.mkdir(parents=True, exist_ok=True)
        transaction["retention_status"] = "moving"
        _write_record(state_path, transaction)
        os.rename(staged, previous)
        _fsync_directory(previous.parent)
        transaction["state"] = "old-tree-retained"
        transaction["retention_status"] = "retained"
        transaction["previous_tree_digest"] = plan["input_tree_digest"]
        _write_record(state_path, transaction)
        transaction["state"] = "complete"
        _write_record(state_path, transaction)
        return transaction
    except Exception as exc:
        # Before exchange the staged tree is disposable.  Once intent is
        # durable, both trees are rollback evidence and must never be deleted
        # by a generic exception handler.
        if transaction["state"] in {"verified", "old-tree-retained", "complete"}:
            transaction["last_error"] = {
                "code": "retention-failed",
                "stage": "retention",
                "message": str(exc)[:4096],
                "observed_digests": tuple(
                    digest
                    for digest in (
                        digest_tree(current) if current.exists() else None,
                        digest_tree(staged) if staged.exists() else None,
                        digest_tree(previous) if previous.exists() else None,
                    )
                    if digest is not None
                )[:4],
            }
            transaction["state"] = "old-tree-retained" if previous.exists() else "verified"
            transaction["retention_status"] = "retained" if previous.exists() else "moving"
            transaction["previous_tree_digest"] = (
                plan["input_tree_digest"] if previous.exists() else None
            )
            _write_record(state_path, transaction)
            raise
        if transaction["state"] in {
            "exchange-intent",
            "exchanged-unverified",
            "verified",
            "rollback-intent",
        }:
            transaction["last_error"] = {
                "code": "verify-failed",
                "stage": "rollback",
                "message": str(exc)[:4096],
                "observed_digests": tuple(
                    digest
                    for digest in (
                        digest_tree(current) if current.exists() else None,
                        digest_tree(staged) if staged.exists() else None,
                    )
                    if digest is not None
                )[:4],
            }
            transaction["state"] = "rollback-intent"
            _write_record(state_path, transaction)
            try:
                if current.exists() and staged.exists():
                    current_digest = digest_tree(current)
                    staged_digest = digest_tree(staged)
                    if (
                        current_digest == plan["output_tree_digest"]
                        and staged_digest == plan["input_tree_digest"]
                    ):
                        _exchange(current, staged)
                    if digest_tree(current) == plan["input_tree_digest"]:
                        transaction["state"] = "rolled-back"
                        transaction["retention_status"] = "removed"
                        _write_record(state_path, transaction)
                        shutil.rmtree(staged, ignore_errors=True)
                    else:
                        transaction["state"] = "recovery-required"
                        _write_record(state_path, transaction)
            except Exception as rollback_error:
                transaction["state"] = "recovery-required"
                transaction["last_error"] = {
                    "code": "rollback-failed",
                    "stage": "rollback",
                    "message": str(rollback_error)[:4096],
                    "observed_digests": (),
                }
                _write_record(state_path, transaction)
            raise
        if staged.exists():
            shutil.rmtree(staged, ignore_errors=True)
        transaction["state"] = "rolled-back"
        transaction["retention_status"] = "removed"
        transaction["last_error"] = {
            "code": getattr(exc, "code", "staged-changed"),
            "stage": getattr(exc, "stage", "preflight"),
            "message": str(exc)[:4096],
            "observed_digests": (),
        }
        _write_record(state_path, transaction)
        raise


def apply_plan(plan_path: Path) -> dict[str, Any]:
    with _exclusive_lock(plan_path.parent / "lock"):
        return _apply_plan_unlocked(plan_path)


def _recover_unlocked(transaction_path: Path, force: bool = False) -> dict[str, Any]:
    transaction = cast(dict[str, Any], json.loads(transaction_path.read_text(encoding="utf-8")))
    _validate_transaction(transaction, transaction_path)
    if force:
        print(
            json.dumps(
                {"diagnostic": "manual recovery required", "transaction": transaction},
                sort_keys=True,
            )
        )
        raise SystemExit(1)
    state = transaction["state"]
    current, staged, previous = map(
        Path,
        (transaction["current_path"], transaction["staged_path"], transaction["previous_path"]),
    )
    input_digest = transaction["input_tree_digest"]
    output_digest = transaction["output_tree_digest"]

    def observed(path: Path) -> str | None:
        return digest_tree(path) if path.exists() and not path.is_symlink() else None

    def recovery_required(message: str) -> None:
        transaction["state"] = "recovery-required"
        transaction["last_error"] = {
            "code": "ambiguous-tree",
            "stage": "recovery",
            "message": message,
            "observed_digests": tuple(
                sorted(
                    digest
                    for digest in (observed(current), observed(staged), observed(previous))
                    if digest is not None
                )
            )[:4],
        }
        _write_record(transaction_path, transaction)
        raise MigrationError("ambiguous-tree", "recovery", message)

    def rollback_failed(error: Exception) -> None:
        """Durably record rollback failure before surfacing the typed error."""

        message = str(error)[:4096] or "rollback exchange or fsync failed"
        transaction["state"] = "recovery-required"
        transaction["last_error"] = {
            "code": "rollback-failed",
            "stage": "rollback",
            "message": message,
            "observed_digests": tuple(
                sorted(
                    digest
                    for digest in (
                        observed(current),
                        observed(staged),
                        observed(previous),
                    )
                    if digest is not None
                )
            )[:4],
        }
        _write_record(transaction_path, transaction)
        raise MigrationError("rollback-failed", "rollback", message) from error

    current_digest = observed(current)
    staged_digest = observed(staged)
    previous_digest = observed(previous)
    if state == "rolled-back":
        if current_digest != input_digest:
            recovery_required("rolled-back transaction does not have the input tree active")
        return transaction
    if state == "complete":
        if current_digest != output_digest or previous_digest != input_digest:
            recovery_required("complete transaction trees do not match durable state")
        return transaction
    if state in {"verified", "old-tree-retained"}:
        if current_digest != output_digest:
            recovery_required("verified transaction does not have the output tree active")
        input_locations = [
            path
            for path, digest in ((staged, staged_digest), (previous, previous_digest))
            if digest == input_digest
        ]
        if len(input_locations) != 1:
            recovery_required("verified transaction has an ambiguous retained input tree")
        if input_locations[0] == staged:
            if previous.exists() or previous.is_symlink():
                recovery_required("retention destination is unexpectedly occupied")
            try:
                os.rename(staged, previous)
                _fsync_directory(previous.parent)
            except OSError as exc:
                recovery_required(f"retention move could not be made durable: {exc}")
        transaction["state"] = "old-tree-retained"
        transaction["retention_status"] = "retained"
        transaction["previous_tree_digest"] = input_digest
        _write_record(transaction_path, transaction)
        try:
            _fsync_directory(current.parent)
            _fsync_directory(previous.parent)
        except OSError as exc:
            recovery_required(f"retained trees could not be made durable: {exc}")
        transaction["state"] = "complete"
        _write_record(transaction_path, transaction)
        return transaction
    if state in {"exchange-intent", "exchanged-unverified", "rollback-intent"}:
        if current_digest == output_digest and staged_digest == input_digest:
            try:
                _exchange(current, staged)
                _fsync_directory(current.parent)
            except Exception as error:
                rollback_failed(error)
            current_digest, staged_digest = input_digest, output_digest
        elif not (current_digest == input_digest and staged_digest == output_digest):
            recovery_required("pre-verified transaction trees are ambiguous")
    elif state in {"planned", "staged-validated"}:
        if current_digest != input_digest or staged_digest not in {None, output_digest}:
            recovery_required("planned transaction trees are ambiguous")
    else:
        recovery_required(f"unsupported transaction state: {state}")
    if staged.exists() and staged_digest == output_digest:
        shutil.rmtree(staged)
    if observed(current) != input_digest:
        recovery_required("cannot restore the input tree")
    transaction["state"] = "rolled-back"
    transaction["retention_status"] = "removed"
    _write_record(transaction_path, transaction)
    return transaction


def recover(transaction_path: Path, force: bool = False) -> dict[str, Any]:
    with _exclusive_lock(transaction_path.parent / "lock"):
        return _recover_unlocked(transaction_path, force)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument("--source-root", type=Path, required=True)
    plan_parser.add_argument("--artifact-root", type=Path, required=True)
    plan_parser.add_argument("--output", type=Path, required=True)
    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("--plan", type=Path, required=True)
    recover_parser = sub.add_parser("recover")
    recover_parser.add_argument("--transaction", type=Path, required=True)
    recover_parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            make_plan(args.source_root, args.artifact_root, args.output)
        elif args.command == "apply":
            apply_plan(args.plan)
        else:
            recover(args.transaction, args.force)
    except MigrationError as exc:
        print(f"migration failed [{exc.code}/{exc.stage}]: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
