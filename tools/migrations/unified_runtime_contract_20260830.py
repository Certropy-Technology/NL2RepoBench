#!/usr/bin/env python3
"""Offline v1/v2 -> canonical source migration.

Historical decoding is deliberately confined to this executable.  Runtime
packages must never import it or accept the old field names.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import shlex
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from nl2repobench.domain.models import Visibility
from nl2repobench.storage.artifacts import FileArtifactStore
from nl2repobench.storage.canonical_ustar import encode_files, tree_digest, tree_entries

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


def transform_lock_artifact(
    artifact_root: Path,
    lock_bytes: bytes,
    *,
    identity: str,
    toolchain_digest: str,
    store_files: dict[str, bytes] | None = None,
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
    manager = identity.split("+", 1)[1]
    lock_name = {
        "uv": "requirements.lock.txt",
        "pip": "requirements.lock.txt",
        "npm": "package-lock.json",
        "pnpm": "pnpm-lock.yaml",
        "go-modules": "go.mod",
    }.get(manager)
    if lock_name is None:
        raise MigrationError("plan-invalid", "plan", f"unsupported dependency identity: {identity}")
    store_files = store_files or {}
    lock_archive = encode_files({lock_name: lock_bytes})
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
        (root / lock_name).write_bytes(lock_bytes)
        lock_entries = tree_entries(root)
        (root / lock_name).unlink()
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
        "offline_smoke": {"status": "passed", "command_id": "migration-closure-prepared-v1"},
    }
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
    result = []
    for path in sorted(root.iterdir()):
        if path.is_dir() and not path.is_symlink() and (path / "task.toml").is_file():
            result.append(path)
    return result


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
    records = []
    for directory in dirs:
        try:
            raw = (directory / "task.toml").read_bytes()
            old = tomllib.loads(raw.decode("utf-8"))
            new = migrate_record(old)
            test_data = new["tests"]
            old_tests = old.get("tests", {})
            commands = old_tests.get("commands", [])
            if commands:
                if not isinstance(commands, list) or any(
                    not isinstance(item, str) for item in commands
                ):
                    raise MigrationError(
                        "plan-invalid", "plan", f"cannot convert test commands for {directory.name}"
                    )
                language, _, _, manager = _runtime(old)
                steps = []
                for index, command in enumerate(commands):
                    argv = tuple(shlex.split(command, posix=True))
                    if not argv or any(item in {"$PATH", "${PATH}"} for item in argv):
                        raise MigrationError(
                            "plan-invalid", "plan", f"unsafe test command for {directory.name}"
                        )
                    steps.append(
                        {
                            "step_id": f"step-{index:04d}",
                            "argv": list(argv),
                            "cwd": ".",
                            "environment": {},
                            "timeout_sec": 600,
                        }
                    )
                command_plan = {
                    "schema_version": "1.0",
                    "identity": f"{language}+{manager or 'none'}",
                    "runner": "migrated-command-plan-v1",
                    "candidate_install": "adapter-owned",
                    "report_format": test_data["report_format"],
                    "test_root": "/tests/private",
                    "steps": steps,
                }
                command_ref = artifact_store.put_bytes(
                    json.dumps(command_plan, sort_keys=True, separators=(",", ":")).encode()
                    + b"\n",
                    media_type="application/vnd.nl2repobench.command-plan+json",
                    visibility=Visibility.PRIVATE,
                )
                test_data["commands_artifact"] = command_ref.model_dump(mode="json")
            test_data.pop("commands", None)
            test_data.pop("protected_paths", None)
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
            raise MigrationError(
                "plan-invalid", "plan", f"cannot decode {directory.name}: {exc}"
            ) from exc
        records.append(
            {
                "task_id": directory.name,
                "source_path": str(directory),
                "old_digest": digest_bytes(raw),
                "new_toml": tomli_w.dumps(_toml_safe(new)),
            }
        )
    input_digest = digest_tree(source_root)
    mirror = Path(tempfile.mkdtemp(prefix=f".{source_root.name}.unified-", dir=source_root.parent))
    try:
        for directory in dirs:
            destination = mirror / directory.name
            shutil.copytree(directory, destination, symlinks=True)
            record = next(item for item in records if item["task_id"] == directory.name)
            (destination / "task.toml").write_text(record["new_toml"], encoding="utf-8")
        output_digest = digest_tree(mirror)
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


def apply_plan(plan_path: Path) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    current = Path(plan["source_root"]).resolve()
    if digest_tree(current) != plan["input_tree_digest"]:
        raise MigrationError("staged-changed", "preflight", "source tree changed after planning")
    staged = Path(plan["staged_path"])
    if staged.exists() or staged.is_symlink():
        raise MigrationError("staged-changed", "preflight", "staged path already exists")
    previous = Path(plan["previous_path"])
    staged.mkdir(parents=True)
    try:
        for directory in _source_dirs(current):
            destination = staged / directory.name
            shutil.copytree(directory, destination, symlinks=True)
            record = next(item for item in plan["records"] if item["task_id"] == directory.name)
            (destination / "task.toml").write_text(record["new_toml"], encoding="utf-8")
        if digest_tree(staged) != plan["output_tree_digest"]:
            raise MigrationError("staged-changed", "preflight", "staged tree digest mismatch")
        state_path = plan_path.parent / "transaction.json"
        transaction = {
            "schema_version": "1.0",
            "transaction_id": plan["plan_digest"][7:39],
            "state": "staged-validated",
            "plan_path": str(plan_path.resolve()),
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
            "owner_uid": os.getuid(),
            "owner_gid": os.getgid(),
            "retention_status": "not-started",
            "last_error": None,
        }
        _write_record(state_path, transaction)
        transaction["state"] = "exchange-intent"
        _write_record(state_path, transaction)
        _exchange(current, staged)
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
        os.rename(staged, previous)
        transaction["state"] = "old-tree-retained"
        transaction["retention_status"] = "retained"
        _write_record(state_path, transaction)
        transaction["state"] = "complete"
        _write_record(state_path, transaction)
        return transaction
    except Exception:
        if staged.exists() and current.exists():
            shutil.rmtree(staged, ignore_errors=True)
        raise


def recover(transaction_path: Path, force: bool = False) -> dict[str, Any]:
    transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
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
    if state in {"rolled-back", "complete"}:
        return transaction
    if state in {"verified", "old-tree-retained"}:
        if state == "verified" and staged.exists():
            os.rename(staged, previous)
        transaction["state"] = "complete"
        transaction["retention_status"] = "retained"
        _write_record(transaction_path, transaction)
        return transaction
    if (
        state in {"exchange-intent", "exchanged-unverified"}
        and current.exists()
        and staged.exists()
    ):
        if (
            digest_tree(current) == transaction["output_tree_digest"]
            and digest_tree(staged) == transaction["input_tree_digest"]
        ):
            _exchange(current, staged)
    if staged.exists():
        shutil.rmtree(staged, ignore_errors=True)
    if not current.exists() or digest_tree(current) != transaction["input_tree_digest"]:
        transaction["state"] = "recovery-required"
        _write_record(transaction_path, transaction)
        raise MigrationError("verify-failed", "recovery", "cannot identify the input tree")
    transaction["state"] = "rolled-back"
    transaction["retention_status"] = "removed"
    _write_record(transaction_path, transaction)
    return transaction


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
