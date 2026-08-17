"""Safe filesystem primitives shared by compilers and migration adapters."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import IO

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


def atomic_copy(path: Path, source: IO[bytes], *, expected_size: int, max_size: int) -> None:
    """Stream a bounded file to an atomic destination."""

    if expected_size < 0 or expected_size > max_size:
        raise UnsafePathError(f"file size {expected_size} exceeds limit {max_size}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise UnsafePathError(f"generated file must not be a symlink: {path}")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    written = 0
    try:
        with os.fdopen(descriptor, "wb") as handle:
            while chunk := source.read(min(1024 * 1024, max_size - written + 1)):
                written += len(chunk)
                if written > max_size:
                    raise UnsafePathError(f"file exceeds limit {max_size}: {path}")
                handle.write(chunk)
            if written != expected_size:
                raise UnsafePathError(
                    f"file size {written} does not match declared {expected_size}: {path}"
                )
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
