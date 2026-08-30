# ruff: noqa: E501
"""SQLite backup, verification, and guarded activation primitives."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import time
from collections.abc import Callable
from contextlib import nullcontext
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from .migration import MigrationError


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sync(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _sync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _regular(path: Path, label: str) -> None:
    info = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
        raise MigrationError(f"{label} must be a regular non-symlink file")


def _exclusive_empty(path: Path, label: str) -> None:
    if path.parent.is_symlink() or path.exists() or path.is_symlink():
        raise MigrationError(f"{label} must be exclusively created")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(fd)


def _exclusive_copy(source: Path, target: Path, label: str) -> None:
    if target.exists() or target.is_symlink() or target.parent.is_symlink():
        raise MigrationError(f"{label} must be exclusively created")
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with source.open("rb") as input_file, os.fdopen(fd, "wb") as output_file:
            shutil.copyfileobj(input_file, output_file)
            output_file.flush()
            os.fsync(output_file.fileno())
        fd = -1
    finally:
        if fd != -1:
            os.close(fd)


def _consumed_receipts(path: Path) -> set[str]:
    if path.is_symlink():
        raise MigrationError("consumed-receipt ledger must not be a symlink")
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError("consumed-receipt ledger is invalid") from exc
    return {str(value) for value in payload.get("receipts", [])} if isinstance(payload, dict) else set()


def _consume_receipt(path: Path, key: str) -> None:
    receipts = _consumed_receipts(path)
    if key in receipts:
        raise MigrationError("restore quiescence receipt was already used")
    receipts.add(key)
    temporary = path.with_name(f".{path.name}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise MigrationError("consumed-receipt staging path is occupied")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump({"schema_version": "restore-receipts/v1", "receipts": sorted(receipts)}, output)
            output.flush()
            os.fsync(output.fileno())
        fd = -1
        os.replace(temporary, path)
        _sync_dir(path.parent)
    finally:
        if fd != -1:
            os.close(fd)
        if temporary.exists():
            temporary.unlink()


def _database_summary(path: Path) -> dict[str, object]:
    with sqlite3.connect(path) as db:
        tables = [str(row[0]) for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )]
        counts = {name: int(db.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]) for name in tables}
        digest = hashlib.sha256()
        for name in tables:
            digest.update(name.encode())
            for row in db.execute(f'SELECT * FROM "{name}"'):
                digest.update(repr(tuple(row)).encode())
    return {"tables": counts, "digest": digest.hexdigest()}


def _manifest(directory: Path) -> dict[str, object]:
    database = next((path for path in directory.iterdir() if path.name.endswith(".sqlite3")), None)
    if database is None:
        raise MigrationError("backup database is missing")
    summary = _database_summary(database)
    files = []
    for path in sorted(directory.iterdir()):
        if path.name == "backup-manifest.json" or path.name.endswith(("-wal", "-shm")):
            continue
        _regular(path, f"backup entry {path.name}")
        files.append({"name": path.name, "size": path.stat().st_size, "sha256": _digest(path)})
    return {"schema_version": "authoring-backup/v2", "files": files,
            "database_summary": summary}


def backup_database(source: Path | str, destination: Path | str) -> dict[str, object]:
    """Create an online SQLite backup and a checksum manifest."""
    source_path, destination_path = Path(source).resolve(), Path(destination)
    _regular(Path(source), "source database")
    if destination_path.exists() or destination_path.is_symlink():
        raise MigrationError("backup destination must be a new directory")
    destination_path.mkdir(mode=0o700)
    dest = destination_path
    target = dest / "database.sqlite3"
    if target.exists() or target.is_symlink():
        raise MigrationError("backup target must be exclusively created")
    _exclusive_empty(target, "backup target")
    src = sqlite3.connect(source_path)
    dst = sqlite3.connect(target)
    try:
        src.backup(dst)
        dst.commit()
    finally:
        dst.close()
        src.close()
    _sync(target)
    manifest = _manifest(dest)
    manifest_path = dest / "backup-manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _sync(manifest_path)
    _sync_dir(dest)
    return manifest


def verify_backup(directory: Path | str) -> dict[str, object]:
    directory = Path(directory).resolve()
    manifest_path = directory / "backup-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError("backup manifest is missing or invalid") from exc
    if manifest.get("schema_version") != "authoring-backup/v2":
        raise MigrationError("unsupported backup manifest")
    expected = {str(item["name"]): item for item in manifest.get("files", [])}
    actual_files = {
        path.name for path in directory.iterdir()
        if path.name != "backup-manifest.json"
        and not path.name.endswith(("-wal", "-shm"))
    }
    if actual_files != set(expected):
        raise MigrationError("backup file set mismatch")
    for entry in directory.iterdir():
        if entry.name.endswith(("-wal", "-shm")) and (entry.is_symlink() or not entry.is_file()):
            raise MigrationError("backup sidecar must be a regular non-symlink file")
        if entry.name != "backup-manifest.json" and entry.name not in expected and not entry.name.endswith(("-wal", "-shm")):
            raise MigrationError("backup contains undeclared entry")
    for name, item in expected.items():
        path = directory / name
        _regular(path, f"backup entry {name}")
        if path.stat().st_size != int(item["size"]) or _digest(path) != item["sha256"]:
            raise MigrationError(f"backup checksum mismatch: {name}")
    database = next((directory / name for name in expected if name.endswith(".sqlite3")), None)
    if database is None:
        raise MigrationError("backup database is missing")
    with sqlite3.connect(database) as db:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = db.execute("PRAGMA foreign_key_check").fetchall()
    if integrity != "ok" or foreign_keys:
        raise MigrationError("backup database integrity check failed")
    actual_summary = _database_summary(database)
    if manifest.get("database_summary") != actual_summary:
        raise MigrationError("backup database content digest mismatch")
    return {"verified": True, "manifest": manifest, "integrity": integrity, "foreign_key_errors": len(foreign_keys)}


def activate_database(staged: Path | str, target: Path | str, *, activate: bool = False) -> None:
    """Checkpoint a staged DB and atomically replace the exact main file.

    This function is intentionally unusable without ``activate=True`` and is
    suitable for tests in temporary directories only.
    """
    if not activate:
        raise MigrationError("database activation requires explicit --activate")
    staged_path, target_path = Path(staged), Path(target)
    _regular(staged_path, "staged database")
    if target_path.parent.is_symlink():
        raise MigrationError("activation target directory must not be a symlink")
    with sqlite3.connect(staged_path) as db:
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        db.commit()
    _sync(staged_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staged_path, target_path)
    _sync(target_path.parent)


def restore_database(backup_directory: Path | str, target: Path | str, *, activate: bool = False,
                     quiescence_marker: Path | str | None = None,
                     quiesced: Callable[[], dict[str, Any] | bool] | None = None) -> dict[str, object]:
    """Validate and (only with activation) restore a backup with sidecar quarantine."""
    backup_raw, target_raw = Path(backup_directory), Path(target)
    if backup_raw.is_symlink() or target_raw.is_symlink():
        raise MigrationError("restore source and target must not be symlinks")
    backup_dir, target_path = backup_raw.resolve(), target_raw.resolve()
    lock_path = target_path.parent / f".{target_path.name}.lock"
    if lock_path.is_symlink():
        raise MigrationError("restore lock must not be a symlink")
    lock = None
    if activate:
        try:
            lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError:
            lock_fd = os.open(lock_path, os.O_RDWR | os.O_NOFOLLOW)
        lock = os.fdopen(lock_fd, "a+")
    elif lock_path.exists():
        lock = lock_path.open("r")
    with (lock if lock is not None else nullcontext()) as held_lock:
        if held_lock is not None:
            fcntl.flock(held_lock.fileno(), fcntl.LOCK_EX)
        try:
            verification = verify_backup(backup_dir)
            receipt = quiesced() if quiesced is not None else None
            marker_ok = isinstance(receipt, dict) and receipt.get("quiesced") is True
            if quiescence_marker is not None:
                try:
                    receipt = json.loads(Path(quiescence_marker).read_text(encoding="utf-8"))
                    marker_ok = isinstance(receipt, dict) and receipt.get("quiesced") is True
                except (OSError, json.JSONDecodeError):
                    marker_ok = False
            if (not marker_ok or not isinstance(receipt, dict) or not receipt.get("receipt_id")
                    or not receipt.get("generation") or receipt.get("database") != target_path.name
                    or not receipt.get("nonce") or not receipt.get("observed_at")):
                raise MigrationError("restore requires a fresh generation-bound quiescence receipt")
            try:
                observed = datetime.fromisoformat(str(receipt["observed_at"]).replace("Z", "+00:00"))
            except ValueError as exc:
                raise MigrationError("restore quiescence timestamp is invalid") from exc
            if observed.tzinfo is None or datetime.now(UTC) - observed > timedelta(hours=1):
                raise MigrationError("restore quiescence receipt is stale")
            receipt_key = f"{receipt['receipt_id']}:{receipt['nonce']}"
            backup_manifest = cast(dict[str, Any], verification["manifest"])
            if receipt.get("database_digest") != backup_manifest.get("database_summary", {}).get("digest"):
                raise MigrationError("restore receipt database digest does not match backup")
            consumed_path = target_path.parent / f".{target_path.name}.restore-consumed.json"
            if activate and receipt_key in _consumed_receipts(consumed_path):
                raise MigrationError("restore quiescence receipt was already used")
            source = next(backup_dir / str(item["name"]) for item in backup_manifest["files"] if str(item["name"]) == "database.sqlite3")
            if not activate:
                return {"dry_run": True, "verified": True, "target": str(target_path), "quiesced": True}
            quarantine = target_path.parent / f".restore-quarantine-{int(time.time())}"
            quarantine.mkdir(mode=0o700)
            for suffix in ("", "-wal", "-shm"):
                sidecar = Path(str(target_path) + suffix)
                if sidecar.exists():
                    os.replace(sidecar, quarantine / sidecar.name)
            _sync_dir(quarantine)
            stage_dir = target_path.parent / f".restore-stage-{receipt['nonce']}"
            if stage_dir.exists() or stage_dir.is_symlink():
                raise MigrationError("restore staging directory must be exclusively created")
            stage_dir.mkdir(mode=0o700)
            staged = stage_dir / target_path.name
            _exclusive_copy(source, staged, "restore staging path")
            activate_database(staged, target_path, activate=True)
            for suffix in ("-wal", "-shm"):
                sidecar = Path(str(staged) + suffix)
                if sidecar.exists():
                    sidecar.unlink()
            stage_dir.rmdir()
            _sync_dir(target_path.parent)
            with sqlite3.connect(target_path) as db:
                if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or db.execute("PRAGMA foreign_key_check").fetchall():
                    raise MigrationError("restored database integrity check failed")
            _consume_receipt(consumed_path, receipt_key)
            return {"dry_run": False, "verified": True, "target": str(target_path), "quarantine": str(quarantine), "quiesced": True}
        finally:
            if held_lock is not None:
                fcntl.flock(held_lock.fileno(), fcntl.LOCK_UN)
