"""Strict categorized private-artifact manifest and compile authorization factory."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from nl2repobench.domain.canonical_contract import TaskManifest
from nl2repobench.domain.canonical_models import ArtifactRef, Visibility
from nl2repobench.storage.artifacts import (
    FileArtifactStore,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)


class _StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DependencyArtifactDigests(_StrictRecord):
    lock: str | None
    store: str | None
    inventory: str | None


class TestArtifactDigests(_StrictRecord):
    commands: str | None
    protected_paths: str | None
    bundle: str | None


class SingleArtifactDigest(_StrictRecord):
    bundle: str | None


class PrivateArtifactsManifest(_StrictRecord):
    schema_version: Literal["1.0"] = "1.0"
    task_id: str
    canonical_manifest_digest: str
    dependencies: DependencyArtifactDigests
    tests: TestArtifactDigests
    verifier: SingleArtifactDigest
    oracle: SingleArtifactDigest

    def compile_digests(self) -> frozenset[str]:
        values = (
            self.dependencies.lock,
            self.dependencies.store,
            self.dependencies.inventory,
            self.tests.commands,
            self.tests.protected_paths,
            self.tests.bundle,
            self.verifier.bundle,
            self.oracle.bundle,
        )
        return frozenset(value for value in values if value is not None)

    def verify_digests(self) -> frozenset[str]:
        return self.compile_digests() - ({self.oracle.bundle} if self.oracle.bundle else set())


def _private_digest(reference: ArtifactRef | None, field: str) -> str | None:
    if reference is None:
        return None
    if reference.visibility is not Visibility.PRIVATE:
        raise ValueError(f"{field} must reference a private artifact")
    return reference.digest


def categorized_private_artifacts(manifest: TaskManifest) -> PrivateArtifactsManifest:
    dependency = manifest.dependency_bundle
    tests = manifest.tests
    return PrivateArtifactsManifest(
        task_id=manifest.task_id,
        canonical_manifest_digest=manifest.content_digest(),
        dependencies=DependencyArtifactDigests(
            lock=_private_digest(dependency.lock, "dependencies.lock"),
            store=_private_digest(dependency.offline_store, "dependencies.offline_store"),
            inventory=_private_digest(dependency.inventory, "dependencies.inventory"),
        ),
        tests=TestArtifactDigests(
            commands=_private_digest(tests.commands_artifact, "tests.commands_artifact"),
            protected_paths=_private_digest(
                tests.protected_paths_artifact, "tests.protected_paths_artifact"
            ),
            bundle=_private_digest(tests.test_bundle, "tests.test_bundle"),
        ),
        verifier=SingleArtifactDigest(
            bundle=_private_digest(
                manifest.verifier.bundle if manifest.verifier is not None else None,
                "verifier.bundle",
            )
        ),
        oracle=SingleArtifactDigest(
            bundle=_private_digest(manifest.oracle_bundle, "oracle.bundle")
        ),
    )


def compile_authorization(
    manifest: TaskManifest,
    *,
    compiled_root: Path,
) -> PrivateArtifactAuthorization:
    categorized = categorized_private_artifacts(manifest)
    digests = categorized.compile_digests()
    if not digests:
        raise ValueError("task declares no private artifacts to authorize")
    prefix = manifest.content_digest().removeprefix("sha256:")[:16]
    staging_root = (
        compiled_root / manifest.task_id / "private" / prefix
    ).resolve()
    return PrivateArtifactAuthorization(
        task_id=manifest.task_id,
        manifest_digest=manifest.content_digest(),
        purpose="compile",
        allowed_digests=digests,
        staging_root=staging_root,
    )


def compile_resolver_for_source(
    source_root: Path,
    *,
    artifact_store: FileArtifactStore,
    compiled_root: Path,
) -> LocalArtifactResolver:
    """Build the only supported task-scoped compile resolver from source truth."""

    from nl2repobench.domain.canonical_contract import TaskSource

    source = TaskSource.model_validate(
        tomllib.loads((source_root / "task.toml").read_text(encoding="utf-8"))
    )
    instruction = artifact_store.put_file(
        source_root / source.instruction,
        media_type="text/markdown; charset=utf-8",
    )
    authorization = compile_authorization(
        source.to_manifest(instruction),
        compiled_root=compiled_root,
    )
    return LocalArtifactResolver.scoped_private(
        artifact_store,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )


__all__ = [
    "PrivateArtifactsManifest",
    "categorized_private_artifacts",
    "compile_authorization",
    "compile_resolver_for_source",
]
