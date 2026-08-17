"""Safe filesystem primitives shared by compilers and migration adapters."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from nl2repobench.domain.canonical import canonical_file_payload
from nl2repobench.domain.models import TaskManifest, TaskStatus


class UnsafePathError(ValueError):
    """Raised when a generated path escapes or aliases its declared root."""


def safe_child_directory(root: Path, child: str) -> Path:
    """Create one non-symlink child and prove it remains under ``root``."""

    root.mkdir(parents=True, exist_ok=True)
    resolved_root = root.resolve()
    candidate = root / child
    if candidate.is_symlink():
        raise UnsafePathError(f"generated directory must not be a symlink: {candidate}")
    resolved_candidate = candidate.resolve()
    if not resolved_candidate.is_relative_to(resolved_root):
        raise UnsafePathError(f"generated directory escapes output root: {candidate}")
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


def atomic_write(path: Path, data: bytes) -> None:
    """Replace one regular file without following a destination symlink."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise UnsafePathError(f"generated file must not be a symlink: {path}")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def assert_manifest_writable(path: Path, manifest: TaskManifest) -> None:
    """Fail closed before replacing an existing published manifest."""

    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink():
        raise UnsafePathError(f"generated manifest must not be a symlink: {path}")
    try:
        existing = TaskManifest.model_validate_json(canonical_file_payload(path.read_bytes()))
    except (OSError, ValueError) as exc:
        raise UnsafePathError(f"existing generated manifest is invalid: {path}: {exc}") from exc
    if (
        existing.lifecycle.status is TaskStatus.PUBLISHED
        and existing.content_digest() != manifest.content_digest()
    ):
        raise UnsafePathError(
            f"published filesystem manifest is immutable: {manifest.task_id}@{manifest.version}"
        )
