"""Content-addressed artifact storage.

The first implementation is deliberately filesystem-backed. The public API is
small enough to replace with an object-store backend later without coupling
domain models or authoring stages to a storage vendor.
"""

from __future__ import annotations

import hashlib
import os
import stat
import tempfile
from pathlib import Path

from nl2repobench.domain.canonical import bytes_digest
from nl2repobench.domain.models import ArtifactRef, Visibility


class ArtifactStoreError(RuntimeError):
    """Raised when an artifact cannot be written, resolved, or verified."""


class FileArtifactStore:
    """Store immutable bytes in visibility-separated SHA-256 namespaces."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_component(self, path: Path) -> Path:
        if path.is_symlink():
            raise ArtifactStoreError(f"artifact namespace must not be a symlink: {path}")
        resolved_root = self.root.resolve()
        resolved = path.resolve()
        if not resolved.is_relative_to(resolved_root):
            raise ArtifactStoreError(f"artifact namespace escapes store root: {path}")
        return path

    def _path_for_digest(self, digest: str, visibility: Visibility) -> Path:
        if not digest.startswith("sha256:"):
            raise ArtifactStoreError(f"unsupported digest: {digest}")
        value = digest.removeprefix("sha256:")
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ArtifactStoreError(f"invalid SHA-256 digest: {digest}")
        namespace = self._safe_component(self.root / visibility.value)
        hash_root = self._safe_component(namespace / "sha256")
        prefix = self._safe_component(hash_root / value[:2])
        target = prefix / value
        if target.is_symlink():
            raise ArtifactStoreError(f"artifact leaf must not be a symlink: {target}")
        return target

    def _write_immutable(
        self,
        data: bytes,
        digest: str,
        visibility: Visibility,
    ) -> Path:
        target = self._path_for_digest(digest, visibility)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.stat().st_size != len(data) or self._digest_file(target) != digest:
                raise ArtifactStoreError(f"existing artifact does not match digest: {digest}")
            return target

        fd, temporary = tempfile.mkstemp(prefix=".artifact-", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return target

    @staticmethod
    def _digest_file(path: Path) -> str:
        digest = hashlib.sha256()
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            os.close(descriptor)
            raise ArtifactStoreError(f"artifact is not a regular file: {path}")
        with os.fdopen(descriptor, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return f"sha256:{digest.hexdigest()}"

    def put_bytes(
        self,
        data: bytes,
        *,
        media_type: str = "application/octet-stream",
        visibility: Visibility = Visibility.PUBLIC,
    ) -> ArtifactRef:
        """Write bytes atomically and return a stable reference."""

        digest = bytes_digest(data)
        self._write_immutable(data, digest, visibility)
        return ArtifactRef(
            digest=digest,
            size_bytes=len(data),
            media_type=media_type,
            uri=f"artifact://{visibility.value}/{digest}",
            visibility=visibility,
        )

    def put_file(
        self,
        path: Path,
        *,
        media_type: str = "application/octet-stream",
        visibility: Visibility = Visibility.PUBLIC,
    ) -> ArtifactRef:
        """Ingest a file without trusting its filename or mutable path."""

        data = path.read_bytes()
        return self.put_bytes(data, media_type=media_type, visibility=visibility)

    def path_for(self, reference: ArtifactRef, *, allow_private: bool = False) -> Path:
        """Resolve a reference and verify its stored bytes before returning it."""

        if reference.visibility is Visibility.PRIVATE and not allow_private:
            raise ArtifactStoreError("private artifact resolution is not authorized")
        path = self._path_for_digest(reference.digest, reference.visibility)
        if not path.is_file():
            raise ArtifactStoreError(f"artifact is missing: {reference.digest}")
        if (
            path.stat().st_size != reference.size_bytes
            or self._digest_file(path) != reference.digest
        ):
            raise ArtifactStoreError(f"artifact failed integrity check: {reference.digest}")
        return path

    def read_bytes(self, reference: ArtifactRef, *, allow_private: bool = False) -> bytes:
        path = self.path_for(reference, allow_private=allow_private)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as handle:
            data = handle.read()
        if len(data) != reference.size_bytes or bytes_digest(data) != reference.digest:
            raise ArtifactStoreError(f"artifact failed integrity check: {reference.digest}")
        return data


class LocalArtifactResolver:
    """Resolve local refs while enforcing the public/private boundary."""

    def __init__(self, store: FileArtifactStore, *, allow_private: bool = False) -> None:
        self.store = store
        self.allow_private = allow_private

    def resolve(self, reference: ArtifactRef) -> Path:
        if reference.visibility is Visibility.PRIVATE and not self.allow_private:
            raise ArtifactStoreError("private artifact resolution is not authorized")
        return self.store.path_for(reference, allow_private=self.allow_private)
