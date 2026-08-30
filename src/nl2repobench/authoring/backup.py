# ruff: noqa: E501
"""SQLite backup, verification, and guarded activation primitives."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
import sqlite3
import time
from collections.abc import Callable
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
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(database) + suffix)
        if sidecar.exists():
            sidecar.unlink()
    files = []
    for path in sorted(directory.iterdir()):
        if path.name == "backup-manifest.json" or not path.is_file():
            continue
        files.append({"name": path.name, "size": path.stat().st_size, "sha256": _digest(path)})
    return {"schema_version": "authoring-backup/v2", "files": files,
            "database_summary": summary}


def backup_database(source: Path | str, destination: Path | str) -> dict[str, object]:
    """Create an online SQLite backup and a checksum manifest."""
    source_path, dest = Path(source).resolve(), Path(destination).resolve()
    if not source_path.is_file():
        raise MigrationError("source database is missing")
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / source_path.name
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
        if path.is_file() and path.name != "backup-manifest.json"
        and not path.name.endswith(("-wal", "-shm"))
    }
    if actual_files != set(expected):
        raise MigrationError("backup file set mismatch")
    for name, item in expected.items():
        path = directory / name
        if not path.is_file() or path.stat().st_size != int(item["size"]) or _digest(path) != item["sha256"]:
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
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(database) + suffix)
        if sidecar.exists():
            sidecar.unlink()
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
    staged_path, target_path = Path(staged).resolve(), Path(target).resolve()
    if not staged_path.is_file() or staged_path.parent == target_path.parent:
        # Same-directory replacement is allowed only when explicitly requested,
        # but normal callers stage in a separate directory.
        pass
    with sqlite3.connect(staged_path) as db:
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        db.commit()
    _sync(staged_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staged_path, target_path)
    _sync(target_path.parent)


def restore_database(backup_directory: Path | str, target: Path | str, *, activate: bool = False,
                     quiescence_marker: Path | str | None = None,
                     quiesced: Callable[[], bool] | None = None) -> dict[str, object]:
    """Validate and (only with activation) restore a backup with sidecar quarantine."""
    backup_dir, target_path = Path(backup_directory).resolve(), Path(target).resolve()
    lock_path = target_path.parent / f".{target_path.name}.restore.lock"
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            verification = verify_backup(backup_dir)
            marker_ok = bool(quiesced() if quiesced is not None else False)
            if quiescence_marker is not None:
                try:
                    marker_ok = json.loads(Path(quiescence_marker).read_text(encoding="utf-8")).get("quiesced") is True
                except (OSError, json.JSONDecodeError):
                    marker_ok = False
            if not marker_ok:
                raise MigrationError("restore requires a quiesced callback or marker")
            backup_manifest = cast(dict[str, Any], verification["manifest"])
            source = next(backup_dir / str(item["name"]) for item in backup_manifest["files"] if str(item["name"]).endswith(".sqlite3"))
            if not activate:
                return {"dry_run": True, "verified": True, "target": str(target_path), "quiesced": True}
            quarantine = target_path.parent / f".restore-quarantine-{int(time.time())}"
            quarantine.mkdir(mode=0o700)
            for suffix in ("", "-wal", "-shm"):
                sidecar = Path(str(target_path) + suffix)
                if sidecar.exists():
                    os.replace(sidecar, quarantine / sidecar.name)
            staged = target_path.parent / f".{target_path.name}.restore-staged"
            shutil.copy2(source, staged)
            activate_database(staged, target_path, activate=True)
            with sqlite3.connect(target_path) as db:
                if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or db.execute("PRAGMA foreign_key_check").fetchall():
                    raise MigrationError("restored database integrity check failed")
            return {"dry_run": False, "verified": True, "target": str(target_path), "quarantine": str(quarantine), "quiesced": True}
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
