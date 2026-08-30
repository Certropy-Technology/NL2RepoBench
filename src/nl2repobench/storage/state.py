"""Small SQLite state index for idempotent imports and future stage claims."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.canonical_contract import TaskManifest


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class StateStoreError(RuntimeError):
    """Raised when persisted state fails its integrity contract."""


class StateStore:
    """Persist task manifests without storing their large artifact bytes."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA busy_timeout=5000")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS task_manifests (
                task_id TEXT NOT NULL,
                version TEXT NOT NULL,
                manifest_digest TEXT NOT NULL,
                status TEXT NOT NULL,
                manifest_json BLOB NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (task_id, version)
            );
            CREATE INDEX IF NOT EXISTS idx_task_status ON task_manifests(status);
            """
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> StateStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def assert_task_writable(self, manifest: TaskManifest) -> None:
        """Reject content changes to an already published task version."""

        digest = manifest.content_digest()
        existing = self._connection.execute(
            """
            SELECT manifest_digest, status FROM task_manifests
            WHERE task_id = ? AND version = ?
            """,
            (manifest.task_id, manifest.version),
        ).fetchone()
        if (
            existing is not None
            and existing["status"] == "published"
            and existing["manifest_digest"] != digest
        ):
            raise StateStoreError(
                f"published manifest is immutable: {manifest.task_id}@{manifest.version}"
            )

    def upsert_task(self, manifest: TaskManifest) -> None:
        self.assert_task_writable(manifest)
        payload = canonical_json(manifest)
        digest = manifest.content_digest()
        now = utc_now()
        self._connection.execute(
            """
            INSERT INTO task_manifests
                (task_id, version, manifest_digest, status, manifest_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id, version) DO UPDATE SET
                manifest_digest = excluded.manifest_digest,
                status = excluded.status,
                manifest_json = excluded.manifest_json,
                updated_at = excluded.updated_at
            """,
            (
                manifest.task_id,
                manifest.version,
                digest,
                manifest.lifecycle.status.value,
                payload,
                now,
                now,
            ),
        )
        self._connection.commit()

    def get_task(self, task_id: str, version: str = "1.0.0") -> TaskManifest | None:
        row = self._connection.execute(
            """
            SELECT manifest_json, manifest_digest
            FROM task_manifests WHERE task_id = ? AND version = ?
            """,
            (task_id, version),
        ).fetchone()
        if row is None:
            return None
        manifest = TaskManifest.model_validate_json(row["manifest_json"])
        if manifest.content_digest() != row["manifest_digest"]:
            raise StateStoreError(f"stored manifest digest mismatch: {task_id}@{version}")
        return manifest

    def list_tasks(self) -> list[TaskManifest]:
        rows = self._connection.execute(
            "SELECT manifest_json FROM task_manifests ORDER BY task_id, version"
        ).fetchall()
        return [TaskManifest.model_validate_json(row["manifest_json"]) for row in rows]

    def export_index(self) -> list[dict[str, str]]:
        """Return a compact index suitable for diagnostics and reporting."""

        rows = self._connection.execute(
            """
            SELECT task_id, version, manifest_digest, status
            FROM task_manifests ORDER BY task_id, version
            """
        ).fetchall()
        return [dict(row) for row in rows]
