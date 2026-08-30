from __future__ import annotations

import pytest

from nl2repobench.domain.canonical_contract import TaskManifest
from nl2repobench.domain.canonical_models import ArtifactRef, Visibility
from nl2repobench.storage.artifacts import (
    ArtifactStoreError,
    FileArtifactStore,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.state import StateStore, StateStoreError


def test_file_artifact_store_is_immutable_and_verifies_bytes(tmp_path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    reference = store.put_bytes(b"hello", visibility=Visibility.PUBLIC)

    assert store.read_bytes(reference) == b"hello"
    assert store.put_bytes(b"hello", visibility=Visibility.PUBLIC).digest == reference.digest

    path = store.path_for(reference)
    path.write_bytes(b"tampered")
    with pytest.raises(ArtifactStoreError, match="integrity"):
        store.path_for(reference)


def test_private_artifact_requires_explicit_authorization(tmp_path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    reference = store.put_bytes(b"hidden", visibility=Visibility.PRIVATE)

    with pytest.raises(ArtifactStoreError, match="not authorized"):
        store.path_for(reference)
    with pytest.raises(ArtifactStoreError, match="not authorized"):
        store.read_bytes(reference)
    forged_public = reference.model_copy(
        update={
            "visibility": Visibility.PUBLIC,
            "uri": f"artifact://public/{reference.digest}",
        }
    )
    with pytest.raises(ArtifactStoreError, match="missing"):
        store.read_bytes(forged_public)
    with pytest.raises(ArtifactStoreError, match="not authorized"):
        LocalArtifactResolver(store).resolve(reference)
    authorization = PrivateArtifactAuthorization(
        task_id="test",
        manifest_digest="sha256:" + "a" * 64,
        purpose="compile",
        allowed_digests=frozenset({reference.digest}),
        staging_root=(tmp_path / "compiled/test/private/aaaaaaaaaaaaaaaa").resolve(),
    )
    resolver = LocalArtifactResolver.scoped_private(
        store,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )
    assert resolver.resolve(reference).is_file()


def test_artifact_store_rejects_symlinked_visibility_namespace(tmp_path) -> None:
    root = tmp_path / "artifacts"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (root / "public").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ArtifactStoreError, match="namespace must not be a symlink"):
        FileArtifactStore(root).put_bytes(b"public", visibility=Visibility.PUBLIC)


def test_public_digest_leaf_cannot_symlink_to_private_bytes(tmp_path) -> None:
    root = tmp_path / "artifacts"
    store = FileArtifactStore(root)
    private = store.put_bytes(b"same-digest", visibility=Visibility.PRIVATE)
    authorization = PrivateArtifactAuthorization(
        task_id="test",
        manifest_digest="sha256:" + "a" * 64,
        purpose="compile",
        allowed_digests=frozenset({private.digest}),
        staging_root=(tmp_path / "compiled/test/private/aaaaaaaaaaaaaaaa").resolve(),
    )
    private_path = store.path_for(
        private,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )
    digest = private.digest.removeprefix("sha256:")
    public_leaf = root / "public" / "sha256" / digest[:2] / digest
    public_leaf.parent.mkdir(parents=True)
    public_leaf.symlink_to(private_path)
    forged_public = private.model_copy(
        update={
            "visibility": Visibility.PUBLIC,
            "uri": f"artifact://public/{private.digest}",
        }
    )

    with pytest.raises(ArtifactStoreError, match="leaf must not be a symlink"):
        store.read_bytes(forged_public)


def test_state_store_upserts_and_lists_task(tmp_path, sample_manifest: TaskManifest) -> None:
    with StateStore(tmp_path / "state.db") as state:
        state.upsert_task(sample_manifest)
        state.upsert_task(sample_manifest)
        assert state.get_task(sample_manifest.task_id) == sample_manifest
        assert [item.task_id for item in state.list_tasks()] == [sample_manifest.task_id]


def test_state_store_detects_manifest_digest_corruption(
    tmp_path, sample_manifest: TaskManifest
) -> None:
    with StateStore(tmp_path / "state.db") as state:
        state.upsert_task(sample_manifest)
        state._connection.execute(  # noqa: SLF001 - intentional corruption injection
            "UPDATE task_manifests SET manifest_digest = ? WHERE task_id = ?",
            ("sha256:" + "0" * 64, sample_manifest.task_id),
        )
        state._connection.commit()  # noqa: SLF001 - intentional corruption injection
        with pytest.raises(StateStoreError, match="digest mismatch"):
            state.get_task(sample_manifest.task_id)


def test_state_store_cannot_overwrite_published_version(
    tmp_path, sample_manifest: TaskManifest
) -> None:
    with StateStore(tmp_path / "state.db") as state:
        state.upsert_task(sample_manifest)
        state._connection.execute(  # noqa: SLF001 - lifecycle transition injection
            "UPDATE task_manifests SET status = 'published' WHERE task_id = ?",
            (sample_manifest.task_id,),
        )
        state._connection.commit()  # noqa: SLF001 - lifecycle transition injection
        changed = sample_manifest.model_copy(
            update={"version": sample_manifest.version, "legacy_projection": None}
        )
        changed = changed.model_copy(
            update={"metadata": changed.metadata.model_copy(update={"category": "changed"})}
        )
        with pytest.raises(StateStoreError, match="published manifest is immutable"):
            state.upsert_task(changed)


@pytest.fixture
def sample_manifest(tmp_path) -> TaskManifest:
    instruction = ArtifactRef(
        digest="sha256:" + "b" * 64,
        size_bytes=10,
        uri="artifact://public/sha256:" + "b" * 64,
    )
    return TaskManifest.model_validate(
        {
            "task_id": "sample-task",
            "metadata": {"language": "python"},
            "instruction": instruction.model_dump(mode="json"),
            "environment_lock": {"status": "unknown"},
            "dependency_bundle": {"status": "unknown", "package_manager": "uv"},
            "tests": {
                "framework": "pytest",
                "report_format": "pytest-junit-xml-v1",
                "expected_total": 1,
            },
        }
    )
