#!/usr/bin/env python3
"""Prepare, but do not publish, a versioned private task release.

This command is deliberately a staging operation.  It reads one canonical
source and immutable legacy CAS objects, writes newly canonicalized bytes into
an explicitly supplied staging tree, and emits a machine-readable update
plan.  It never changes ``catalog/sources`` or the input CAS.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import stat
import tomllib
from pathlib import Path
from typing import Any, cast

from nl2repobench.domain.canonical_contract import PackageManager, TaskSource
from nl2repobench.domain.canonical_models import ArtifactRef, Visibility
from nl2repobench.storage.canonical_ustar import decode_archive, encode_files, tree_digest
from nl2repobench.storage.materialize import TARGET_MEDIA_TYPES, ArchiveKind
from nl2repobench.verification.node_command_plan import load_node_command_plan

_MIGRATOR_PATH = Path(__file__).with_name("migrate_private_archive.py")
_MIGRATOR_SPEC = importlib.util.spec_from_file_location("private_archive_migration", _MIGRATOR_PATH)
if _MIGRATOR_SPEC is None or _MIGRATOR_SPEC.loader is None:  # pragma: no cover - packaging error
    raise ImportError(f"cannot load archive migrator: {_MIGRATOR_PATH}")
_MIGRATOR = importlib.util.module_from_spec(_MIGRATOR_SPEC)
_MIGRATOR_SPEC.loader.exec_module(_MIGRATOR)
MigrationResult = _MIGRATOR.MigrationResult
PrivateArchiveMigrationError = _MIGRATOR.PrivateArchiveMigrationError
migrate_private_archive = _MIGRATOR.migrate_private_archive

SHA256_PREFIX = "sha256:"
MAX_INPUT_BYTES = 2 * 1024**3
MAX_METADATA_BYTES = 4 * 1024 * 1024
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
COMMAND_JSON_MEDIA_TYPES = frozenset(
    {
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


class PrivateReleasePreparationError(ValueError):
    """Raised when a release cannot be safely staged."""


def _assert_no_symlink_ancestors(path: Path, label: str) -> None:
    """Reject a path whose existing lexical ancestors contain a symlink."""

    cursor = Path(os.path.abspath(path))
    while True:
        if cursor.is_symlink():
            raise PrivateReleasePreparationError(
                f"{label} and its ancestors must not contain symlinks: {path}"
            )
        if cursor == cursor.parent:
            return
        cursor = cursor.parent


def _digest_bytes(data: bytes) -> str:
    return f"{SHA256_PREFIX}{hashlib.sha256(data).hexdigest()}"


def _safe_regular(path: Path, *, max_bytes: int) -> bytes:
    """Read one regular file without following a final symlink."""

    cursor = path.parent
    while cursor != cursor.parent:
        if cursor.is_symlink():
            raise PrivateReleasePreparationError(
                f"input file parent must not contain symlinks: {path}"
            )
        cursor = cursor.parent
    if path.is_symlink():
        raise PrivateReleasePreparationError(f"input file must not be a symlink: {path}")
    descriptor = -1
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise PrivateReleasePreparationError(f"input file is not regular: {path}")
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            data = handle.read(max_bytes + 1)
    except OSError as exc:
        raise PrivateReleasePreparationError(f"cannot read input file: {path}") from exc
    finally:
        if descriptor != -1:
            os.close(descriptor)
    if len(data) > max_bytes:
        raise PrivateReleasePreparationError(f"input file exceeds size limit: {path}")
    return data


def _cas_file(cas_root: Path, digest: str) -> Path:
    if not digest.startswith(SHA256_PREFIX) or len(digest) != 71:
        raise PrivateReleasePreparationError(f"invalid CAS digest: {digest}")
    value = digest.removeprefix(SHA256_PREFIX)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise PrivateReleasePreparationError(f"invalid CAS digest: {digest}") from exc
    root = cas_root.resolve()
    if cas_root.is_symlink() or not root.is_dir():
        raise PrivateReleasePreparationError(f"CAS root must be a real directory: {cas_root}")
    path = root / value[:2] / value
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise PrivateReleasePreparationError(f"CAS object path is unsafe: {digest}")
    return path


def _read_cas(cas_root: Path, reference: ArtifactRef) -> bytes:
    path = _cas_file(cas_root, reference.digest)
    if not path.is_file():
        raise PrivateReleasePreparationError(f"CAS object is missing: {reference.digest}")
    data = _safe_regular(path, max_bytes=MAX_INPUT_BYTES)
    if len(data) != reference.size_bytes:
        raise PrivateReleasePreparationError(
            f"CAS size mismatch for {reference.digest}: {len(data)} != {reference.size_bytes}"
        )
    actual = _digest_bytes(data)
    if actual != reference.digest:
        raise PrivateReleasePreparationError(
            f"CAS digest mismatch for {reference.digest}: found {actual}"
        )
    return data


def _artifact_record(
    role: str,
    reference: ArtifactRef,
    result: Any,
    new_ref: ArtifactRef,
) -> dict[str, object]:
    return {
        "role": role,
        "old_ref": reference.uri,
        "old_sha256": result.old_sha256,
        "old_size": result.old_size,
        "new_ref": new_ref.uri,
        "new_sha256": result.new_sha256,
        "new_size": result.new_size,
        "media_type": new_ref.media_type,
        "file_count": result.file_count,
        "tree_digest": result.tree_digest,
    }


def _inventory_section(kind: str, archive_digest: str, archive: bytes) -> dict[str, object]:
    members = decode_archive(archive)
    entries = [member.entry for member in members]
    return {
        "archive_kind": kind,
        "archive_digest": archive_digest,
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


def _canonical_json(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def _write_staging_metadata(path: Path, data: bytes) -> None:
    if len(data) > MAX_METADATA_BYTES:
        raise PrivateReleasePreparationError("staging metadata exceeds size limit")
    if path.is_symlink():
        raise PrivateReleasePreparationError(f"staging metadata must not be a symlink: {path}")
    _assert_no_symlink_ancestors(path, "staging metadata")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        current = _safe_regular(path, max_bytes=MAX_METADATA_BYTES)
        if current != data:
            raise PrivateReleasePreparationError(f"staging metadata already differs: {path}")
        return
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_staging_artifact(store_root: Path, data: bytes, digest: str) -> None:
    """Write a task-local CAS leaf without replacing a concurrent winner."""

    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise PrivateReleasePreparationError(f"invalid staging digest: {digest}")
    root = store_root.resolve()
    if store_root.is_symlink() or not root.is_dir():
        raise PrivateReleasePreparationError(
            f"staging artifact root must be a real directory: {store_root}"
        )
    namespace = root / "private" / "sha256"
    _assert_no_symlink_ancestors(namespace, "staging artifact namespace")
    target = namespace / digest.removeprefix("sha256:")[:2] / digest.removeprefix("sha256:")
    target.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_symlink_ancestors(target, "staging artifact")
    if target.is_symlink():
        raise PrivateReleasePreparationError(
            f"staging artifact leaf must not be a symlink: {target}"
        )
    if target.exists():
        current = _safe_regular(target, max_bytes=MAX_INPUT_BYTES)
        if len(current) != len(data) or _digest_bytes(current) != digest:
            raise PrivateReleasePreparationError(f"staging artifact already differs: {digest}")
        return
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            current = _safe_regular(target, max_bytes=MAX_INPUT_BYTES)
            if len(current) != len(data) or _digest_bytes(current) != digest:
                raise PrivateReleasePreparationError(
                    f"staging artifact race differs: {digest}"
                ) from None
        temporary.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()


def _source_update_plan(
    source: TaskSource,
    new_version: str,
    artifact_records: list[dict[str, object]],
    dependency_refs: dict[str, ArtifactRef],
) -> dict[str, object]:
    updates: list[dict[str, object]] = [
        {"op": "replace", "path": "version", "old": source.version, "new": new_version},
    ]
    for record in artifact_records:
        role = cast(str, record["role"])
        field = {
            "commands": "tests.commands_artifact",
            "test": "tests.test_bundle",
            "oracle": "oracle_bundle",
        }[role]
        updates.append(
            {
                "op": "replace",
                "path": field,
                "old": record["old_ref"],
                "new": record["new_ref"],
            }
        )
    updates.extend(
        {
            "op": "replace",
            "path": f"dependencies.{name}",
            "old": None,
            "new": reference.uri,
        }
        for name, reference in dependency_refs.items()
    )
    return {
        "source_file": "task.toml",
        "apply": False,
        "operations": updates,
        "reason": "staging-only; Oracle, controls, and reviewer evidence are absent",
    }


def _migrate_command_artifact(
    data: bytes,
    reference: ArtifactRef,
) -> tuple[bytes, str, str]:
    """Extract and validate the canonical Node command plan from legacy bytes."""

    def canonicalize(plan_data: bytes) -> bytes:
        try:
            payload = json.loads(plan_data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PrivateReleasePreparationError("command-plan.json is not valid JSON") from exc
        if not isinstance(payload, dict):
            raise PrivateReleasePreparationError("command-plan.json must be a JSON object")
        # Historical Node plans used the old record shape but already carried
        # the exact runner contract. Only the shape version and omitted
        # canonical defaults are migrated; no command semantics are invented.
        normalized = dict(payload)
        if normalized.get("schema_version") == "2.0":
            normalized["schema_version"] = "1.0"
        normalized.setdefault("identity", "node+npm")
        normalized.setdefault("steps", [])
        try:
            plan = load_node_command_plan(
                _canonical_json(normalized),
                candidate_install="npm-pack-offline-v1",
            )
        except ValueError as exc:
            raise PrivateReleasePreparationError("command-plan.json is invalid") from exc
        return _canonical_json(plan.model_dump(mode="json"))

    if reference.media_type in COMMAND_JSON_MEDIA_TYPES:
        return (
            canonicalize(data),
            "application/vnd.nl2repobench.command-plan+json",
            "json",
        )

    if reference.media_type not in COMMAND_ARCHIVE_MEDIA_TYPES:
        raise PrivateReleasePreparationError(
            f"unsupported commands artifact media type: {reference.media_type}"
        )
    try:
        result = migrate_private_archive(data, ArchiveKind.TEST_BUNDLE)
        members = decode_archive(result.archive)
    except (PrivateArchiveMigrationError, TypeError, ValueError) as exc:
        raise PrivateReleasePreparationError("cannot migrate commands artifact") from exc
    payload_members = [
        member for member in members if member.entry.path != _MIGRATOR.INTERNAL_INVENTORY
    ]
    command_members = [
        member
        for member in payload_members
        if member.entry.type == "file" and member.entry.path == "command-plan.json"
    ]
    if len(payload_members) != 1 or len(command_members) != 1 or command_members[0].data is None:
        raise PrivateReleasePreparationError(
            "legacy commands artifact must contain exactly command-plan.json"
        )
    return (
        canonicalize(command_members[0].data),
        "application/vnd.nl2repobench.command-plan+json",
        "archive",
    )


def prepare_private_release(
    *,
    task_root: Path,
    cas_root: Path,
    staging_root: Path,
    toolchain: Path,
    new_version: str,
    empty_npm_closure: bool,
    apply_source_update: bool = False,
    allow_source_update: bool = False,
) -> dict[str, object]:
    """Stage one private release and return metadata without private payloads."""

    if apply_source_update and not allow_source_update:
        raise PrivateReleasePreparationError(
            "--apply-source-update requires the explicit --allow-source-update flag"
        )
    if not task_root.is_dir() or task_root.is_symlink():
        raise PrivateReleasePreparationError(f"task root must be a real directory: {task_root}")
    source_path = task_root / "task.toml"
    if source_path.is_symlink():
        raise PrivateReleasePreparationError("task.toml must not be a symlink")
    try:
        source = TaskSource.model_validate(
            tomllib.loads(source_path.read_text(encoding="utf-8"))
        )
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        raise PrivateReleasePreparationError(
            f"invalid canonical task source: {source_path}"
        ) from exc
    if source.task_id != task_root.name:
        raise PrivateReleasePreparationError("task_root name must match task_id")
    if source.source.status.value != "known":
        raise PrivateReleasePreparationError("source provenance must be known")
    environment = source.environment
    runtime = environment.runtime
    if environment.status != "known" or runtime is None:
        raise PrivateReleasePreparationError("exact known environment and runtime are required")
    policy = environment.network_policy
    if policy is None or policy.mode != "no-network" or policy.allowed_hosts:
        raise PrivateReleasePreparationError("release preparation requires a no-network policy")
    if runtime.language.value != "node" or runtime.package_manager is not PackageManager.NPM:
        raise PrivateReleasePreparationError("staging preparer currently supports only node+npm")
    if not VERSION_PATTERN.fullmatch(new_version):
        raise PrivateReleasePreparationError("new_version must be an exact semantic version")
    if new_version == source.version:
        raise PrivateReleasePreparationError("new_version must differ from the old task version")
    if not empty_npm_closure:
        raise PrivateReleasePreparationError(
            "dependency migration requires the explicit --empty-npm-closure assertion"
        )
    if (
        source.dependencies.status != "unknown"
        or source.dependencies.package_manager is not PackageManager.NPM
        or source.dependencies.packages
    ):
        raise PrivateReleasePreparationError(
            "--empty-npm-closure requires dependencies.status=unknown and an empty npm package list"
        )
    toolchain_data = _safe_regular(toolchain, max_bytes=MAX_METADATA_BYTES)
    toolchain_digest = _digest_bytes(toolchain_data)
    refs: list[tuple[str, ArtifactRef, ArchiveKind]] = []
    if source.tests.commands_artifact is None:
        raise PrivateReleasePreparationError("tests.commands_artifact is required")
    if source.tests.test_bundle is None:
        raise PrivateReleasePreparationError("tests.test_bundle is required")
    if source.oracle_bundle is None:
        raise PrivateReleasePreparationError("oracle_bundle is required")
    refs.extend(
        (
            ("commands", source.tests.commands_artifact, ArchiveKind.TEST_BUNDLE),
            ("test", source.tests.test_bundle, ArchiveKind.TEST_BUNDLE),
            ("oracle", source.oracle_bundle, ArchiveKind.ORACLE_BUNDLE),
        )
    )
    for role, reference, _kind in refs:
        if reference.visibility is not Visibility.PRIVATE:
            raise PrivateReleasePreparationError(f"{role} artifact must remain private")
    _assert_no_symlink_ancestors(staging_root, "staging root")
    artifact_root = staging_root / "artifacts"
    _assert_no_symlink_ancestors(artifact_root, "staging artifact root")
    artifact_root.mkdir(parents=True, exist_ok=True)
    if artifact_root.is_symlink() or not artifact_root.is_dir():
        raise PrivateReleasePreparationError(
            f"staging artifact root must be a real directory: {artifact_root}"
        )
    artifact_records: list[dict[str, object]] = []
    new_refs: dict[str, ArtifactRef] = {}
    for role, reference, kind in refs:
        old_data = _read_cas(cas_root, reference)
        if role == "commands":
            command_data, command_media_type, _command_shape = _migrate_command_artifact(
                old_data, reference
            )
            result = None
            old_sha256 = _digest_bytes(old_data)
            new_sha256 = _digest_bytes(command_data)
            new_size = len(command_data)
            file_count = 1
            artifact_media_type = command_media_type
            tree = None
        else:
            try:
                result = migrate_private_archive(old_data, kind)
            except (PrivateArchiveMigrationError, TypeError, ValueError) as exc:
                raise PrivateReleasePreparationError(f"cannot migrate {role} artifact") from exc
            if result.new_sha256 == result.old_sha256:
                raise PrivateReleasePreparationError(f"{role} migration did not mint a new digest")
            old_sha256 = result.old_sha256
            new_sha256 = result.new_sha256
            new_size = result.new_size
            file_count = result.file_count
            artifact_media_type = result.media_type
            tree = result.tree_digest
            command_data = result.archive
        new_sha256 = _digest_bytes(command_data)
        _write_staging_artifact(staging_root / "artifacts", command_data, new_sha256)
        new_ref = ArtifactRef(
            digest=new_sha256,
            size_bytes=len(command_data),
            media_type=artifact_media_type,
            uri=f"artifact://private/{new_sha256}",
            visibility=Visibility.PRIVATE,
        )
        new_refs[role] = new_ref
        artifact_records.append(
            {
                "role": role,
                "old_ref": reference.uri,
                "old_sha256": old_sha256,
                "old_size": len(old_data),
                "new_ref": new_ref.uri,
                "new_sha256": new_sha256,
                "new_size": new_size,
                "media_type": new_ref.media_type,
                "file_count": file_count,
                "tree_digest": tree,
            }
        )

    lock_data = _canonical_json({"lockfileVersion": 3, "packages": {"": {}}})
    lock_archive = encode_files({"package-lock.json": lock_data})
    store_archive = encode_files({})
    lock_digest = _digest_bytes(lock_archive)
    store_digest = _digest_bytes(store_archive)
    _write_staging_artifact(staging_root / "artifacts", lock_archive, lock_digest)
    _write_staging_artifact(staging_root / "artifacts", store_archive, store_digest)
    lock_ref = ArtifactRef(
        digest=lock_digest,
        size_bytes=len(lock_archive),
        media_type=TARGET_MEDIA_TYPES[ArchiveKind.DEPENDENCY_LOCK],
        uri=f"artifact://private/{lock_digest}",
        visibility=Visibility.PRIVATE,
    )
    store_ref = ArtifactRef(
        digest=store_digest,
        size_bytes=len(store_archive),
        media_type=TARGET_MEDIA_TYPES[ArchiveKind.OFFLINE_STORE],
        uri=f"artifact://private/{store_digest}",
        visibility=Visibility.PRIVATE,
    )
    inventory_payload = {
        "schema_version": "1.0",
        "identity": "node+npm",
        "adapter_version": "node-npm-migration-v1",
        "toolchain_digest": toolchain_digest,
        "lock": _inventory_section("dependency-lock", lock_ref.digest, lock_archive),
        "store": _inventory_section("offline-store", store_ref.digest, store_archive),
        "offline_smoke": {"status": "not-run", "command_id": "node-npm-offline-install-v1"},
    }
    inventory_data = _canonical_json(inventory_payload)
    inventory_digest = _digest_bytes(inventory_data)
    _write_staging_artifact(staging_root / "artifacts", inventory_data, inventory_digest)
    inventory_ref = ArtifactRef(
        digest=inventory_digest,
        size_bytes=len(inventory_data),
        media_type="application/vnd.nl2repobench.inventory+json",
        uri=f"artifact://private/{inventory_digest}",
        visibility=Visibility.PRIVATE,
    )
    dependency_refs = {"lock": lock_ref, "offline_store": store_ref, "inventory": inventory_ref}

    old_manifest_payload = {
        "schema_version": "1.0",
        "task_id": source.task_id,
        "task_version": source.version,
        "source_revision": source.source.revision,
        "toolchain_digest": toolchain_digest,
        "artifacts": [
            {"role": role, "ref": reference.uri, "size": reference.size_bytes}
            for role, reference, _kind in refs
        ],
    }
    new_manifest_payload = {
        "schema_version": "1.0",
        "task_id": source.task_id,
        "task_version": new_version,
        "source_revision": source.source.revision,
        "toolchain_digest": toolchain_digest,
        "artifacts": artifact_records,
        "dependencies": {name: reference.uri for name, reference in dependency_refs.items()},
    }
    old_manifest_data = _canonical_json(old_manifest_payload)
    new_manifest_data = _canonical_json(new_manifest_payload)
    old_manifest_digest = _digest_bytes(old_manifest_data)
    new_manifest_digest = _digest_bytes(new_manifest_data)
    _write_staging_artifact(staging_root / "artifacts", old_manifest_data, old_manifest_digest)
    _write_staging_artifact(staging_root / "artifacts", new_manifest_data, new_manifest_digest)
    old_manifest_ref = ArtifactRef(
        digest=old_manifest_digest,
        size_bytes=len(old_manifest_data),
        media_type="application/vnd.nl2repobench.private-manifest+json",
        uri=f"artifact://private/{old_manifest_digest}",
        visibility=Visibility.PRIVATE,
    )
    new_manifest_ref = ArtifactRef(
        digest=new_manifest_digest,
        size_bytes=len(new_manifest_data),
        media_type="application/vnd.nl2repobench.private-manifest+json",
        uri=f"artifact://private/{new_manifest_digest}",
        visibility=Visibility.PRIVATE,
    )
    plan = _source_update_plan(source, new_version, artifact_records, dependency_refs)
    metadata: dict[str, object] = {
        "schema_version": "1.0",
        "status": "blocked",
        "task_id": source.task_id,
        "old_version": source.version,
        "new_version": new_version,
        "source_revision": source.source.revision,
        "toolchain_digest": toolchain_digest,
        "artifacts": artifact_records,
        "dependencies": {
            name: {"ref": reference.uri, "digest": reference.digest, "size": reference.size_bytes}
            for name, reference in dependency_refs.items()
        },
        "old_manifest": {
            "ref": old_manifest_ref.uri,
            "digest": old_manifest_ref.digest,
            "size": old_manifest_ref.size_bytes,
        },
        "new_manifest": {
            "ref": new_manifest_ref.uri,
            "digest": new_manifest_ref.digest,
            "size": new_manifest_ref.size_bytes,
        },
        "oracle_receipt": None,
        "controls_receipts": {},
        "blocked_reasons": [
            "staging-only preparation does not run Oracle or controls",
            "reviewer signoff and release evidence are absent",
        ],
        "source_update_plan": plan,
    }
    metadata_data = _canonical_json(metadata)
    _write_staging_metadata(staging_root / "release-metadata.json", metadata_data)
    if apply_source_update:
        raise PrivateReleasePreparationError(
            "refusing source update: Oracle, controls, reviewer signoff, and "
            "release evidence are incomplete"
        )
    return metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-root", type=Path, required=True)
    parser.add_argument("--cas-root", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--new-version", required=True)
    parser.add_argument("--empty-npm-closure", action="store_true")
    parser.add_argument("--apply-source-update", action="store_true")
    parser.add_argument("--allow-source-update", action="store_true")
    args = parser.parse_args(argv)
    if args.apply_source_update and not args.allow_source_update:
        parser.error("--apply-source-update requires --allow-source-update")
    try:
        metadata = prepare_private_release(
            task_root=args.task_root,
            cas_root=args.cas_root,
            staging_root=args.staging_root,
            toolchain=args.toolchain,
            new_version=args.new_version,
            empty_npm_closure=args.empty_npm_closure,
            apply_source_update=args.apply_source_update,
            allow_source_update=args.allow_source_update,
        )
    except (OSError, PrivateReleasePreparationError, TypeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps(metadata, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["PrivateReleasePreparationError", "prepare_private_release", "main"]
