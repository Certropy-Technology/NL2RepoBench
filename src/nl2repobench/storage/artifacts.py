"""Content-addressed artifact storage.

The first implementation is deliberately filesystem-backed. The public API is
small enough to replace with an object-store backend later without coupling
domain models or authoring stages to a storage vendor.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

from nl2repobench.domain.canonical import bytes_digest
from nl2repobench.domain.models import ArtifactRef, Visibility


class ArtifactStoreError(RuntimeError):
    """Raised when an artifact cannot be written, resolved, or verified."""


@dataclass(frozen=True, slots=True)
class PrivateArtifactAuthorization:
    """Task-scoped capability for resolving private CAS bytes.

    This object is constructed by trusted compiler/verifier orchestration and
    deliberately carries no filesystem authority beyond its staging root.
    """

    task_id: str
    manifest_digest: str
    purpose: str
    allowed_digests: frozenset[str]
    staging_root: Path

    def __post_init__(self) -> None:
        if not re.fullmatch(
            r"(?:[A-Za-z0-9][A-Za-z0-9._-]*|@[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)",
            self.task_id,
        ):
            raise ArtifactStoreError("authorization task_id is unsafe")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", self.manifest_digest):
            raise ArtifactStoreError("authorization manifest digest is invalid")
        if self.purpose not in {"compile", "verify"}:
            raise ArtifactStoreError("authorization purpose is invalid")
        if not self.allowed_digests:
            raise ArtifactStoreError("authorization must declare private digests")
        if not self.staging_root.is_absolute() or self.staging_root.is_symlink():
            raise ArtifactStoreError(
                "authorization staging root must be an absolute non-symlink path"
            )
        if any(not re.fullmatch(r"sha256:[0-9a-f]{64}", digest) for digest in self.allowed_digests):
            raise ArtifactStoreError("authorization contains an invalid digest")

    def permits(
        self,
        reference: ArtifactRef,
        *,
        task_id: str,
        manifest_digest: str,
        purpose: str,
        staging_root: Path,
    ) -> bool:
        return (
            reference.visibility is Visibility.PRIVATE
            and reference.digest in self.allowed_digests
            and task_id == self.task_id
            and manifest_digest == self.manifest_digest
            and purpose == self.purpose
            and staging_root.resolve() == self.staging_root.resolve()
        )


@dataclass(frozen=True, slots=True)
class PublicArtifactAuthorization:
    """Marker used when a caller intentionally permits public artifacts only."""

    task_id: str = "public"
    purpose: str = "public"


@dataclass(frozen=True, slots=True)
class MigrationArtifactAuthorization:
    """Explicit non-runtime authority used only by the one-shot migration tool."""

    migration_id: str
    allowed_digests: frozenset[str]
    workspace_root: Path

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", self.migration_id):
            raise ArtifactStoreError("migration authorization id is invalid")
        if not self.allowed_digests or any(
            not re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
            for digest in self.allowed_digests
        ):
            raise ArtifactStoreError("migration authorization digests are invalid")
        if not self.workspace_root.is_absolute() or self.workspace_root.is_symlink():
            raise ArtifactStoreError("migration workspace root must be absolute and non-symlink")

    def permits(self, reference: ArtifactRef) -> bool:
        return (
            reference.visibility is Visibility.PRIVATE
            and reference.digest in self.allowed_digests
        )


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

    def path_for(
        self,
        reference: ArtifactRef,
        authorization: PrivateArtifactAuthorization
        | MigrationArtifactAuthorization
        | PublicArtifactAuthorization
        | None = None,
        *,
        task_id: str | None = None,
        manifest_digest: str | None = None,
        purpose: str | None = None,
        staging_root: Path | None = None,
    ) -> Path:
        """Resolve a reference and verify its stored bytes before returning it."""

        private_permitted = (
            isinstance(authorization, PrivateArtifactAuthorization)
            and task_id is not None
            and manifest_digest is not None
            and purpose is not None
            and staging_root is not None
            and authorization.permits(
                reference,
                task_id=task_id,
                manifest_digest=manifest_digest,
                purpose=purpose,
                staging_root=staging_root,
            )
        ) or (
            isinstance(authorization, MigrationArtifactAuthorization)
            and authorization.permits(reference)
        )
        if reference.visibility is Visibility.PRIVATE and not private_permitted:
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

    def read_bytes(
        self,
        reference: ArtifactRef,
        authorization: PrivateArtifactAuthorization
        | MigrationArtifactAuthorization
        | PublicArtifactAuthorization
        | None = None,
        max_bytes: int | None = None,
        *,
        task_id: str | None = None,
        manifest_digest: str | None = None,
        purpose: str | None = None,
        staging_root: Path | None = None,
    ) -> bytes:
        path = self.path_for(
            reference,
            authorization,
            task_id=task_id,
            manifest_digest=manifest_digest,
            purpose=purpose,
            staging_root=staging_root,
        )
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as handle:
            data = handle.read(None if max_bytes is None else max_bytes + 1)
        if max_bytes is not None and len(data) > max_bytes:
            raise ArtifactStoreError("artifact exceeds requested read limit")
        if len(data) != reference.size_bytes or bytes_digest(data) != reference.digest:
            raise ArtifactStoreError(f"artifact failed integrity check: {reference.digest}")
        return data


class LocalArtifactResolver:
    """Resolve local refs while enforcing the public/private boundary."""

    def __init__(
        self,
        store: FileArtifactStore,
        authorization: PrivateArtifactAuthorization
        | MigrationArtifactAuthorization
        | PublicArtifactAuthorization
        | None = None,
    ) -> None:
        self.store = store
        self.authorization = authorization

    @classmethod
    def scoped_private(
        cls,
        store: FileArtifactStore,
        authorization: PrivateArtifactAuthorization,
        *,
        task_id: str,
        manifest_digest: str,
        purpose: str,
        staging_root: Path,
    ) -> LocalArtifactResolver:
        """Construct a resolver only when every operation scope field matches."""

        if (
            authorization.task_id != task_id
            or authorization.manifest_digest != manifest_digest
            or authorization.purpose != purpose
            or authorization.staging_root.resolve() != staging_root.resolve()
        ):
            raise ArtifactStoreError("private resolver scope does not match authorization")
        return cls(store, authorization)

    def assert_scope(
        self,
        *,
        task_id: str,
        manifest_digest: str,
        purpose: str,
        staging_root: Path | None = None,
    ) -> PrivateArtifactAuthorization:
        authorization = self.authorization
        if not isinstance(authorization, PrivateArtifactAuthorization):
            raise ArtifactStoreError("private artifact resolution is not authorized")
        expected_root = staging_root or authorization.staging_root
        if (
            authorization.task_id != task_id
            or authorization.manifest_digest != manifest_digest
            or authorization.purpose != purpose
            or authorization.staging_root.resolve() != expected_root.resolve()
        ):
            raise ArtifactStoreError("private resolver operation scope does not match")
        return authorization

    def resolve(
        self,
        reference: ArtifactRef,
        authorization: PrivateArtifactAuthorization
        | MigrationArtifactAuthorization
        | PublicArtifactAuthorization
        | None = None,
    ) -> Path:
        selected = authorization or self.authorization
        if isinstance(selected, PrivateArtifactAuthorization):
            return self.store.path_for(
                reference,
                selected,
                task_id=selected.task_id,
                manifest_digest=selected.manifest_digest,
                purpose=selected.purpose,
                staging_root=selected.staging_root,
            )
        return self.store.path_for(reference, selected)

    def read_bytes(
        self,
        reference: ArtifactRef,
        authorization: PrivateArtifactAuthorization
        | MigrationArtifactAuthorization
        | PublicArtifactAuthorization
        | None = None,
        max_bytes: int | None = None,
    ) -> bytes:
        selected = authorization or self.authorization
        if isinstance(selected, PrivateArtifactAuthorization):
            return self.store.read_bytes(
                reference,
                selected,
                max_bytes,
                task_id=selected.task_id,
                manifest_digest=selected.manifest_digest,
                purpose=selected.purpose,
                staging_root=selected.staging_root,
            )
        return self.store.read_bytes(reference, selected, max_bytes)


__all__ = [
    "ArtifactStoreError",
    "FileArtifactStore",
    "LocalArtifactResolver",
    "MigrationArtifactAuthorization",
    "PrivateArtifactAuthorization",
    "PublicArtifactAuthorization",
]
