from __future__ import annotations

import hashlib
import importlib.util
import tomllib
from pathlib import Path

import pytest

from nl2repobench.domain.models import Visibility
from nl2repobench.storage.artifacts import (
    ArtifactStoreError,
    FileArtifactStore,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.canonical_ustar import EMPTY_TREE_DIGEST, encode_files, tree_digest


def _migration_module():
    path = Path(__file__).parents[1] / "tools/migrations/unified_runtime_contract_20260830.py"
    spec = importlib.util.spec_from_file_location("f0_migration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_empty_ustar_and_tree_digest_are_canonical() -> None:
    archive = encode_files({})
    assert len(archive) == 10240
    assert hashlib.sha256(archive).hexdigest() == (
        "84ff92691f909a05b224e1c56abb4864f01b4f8e3c854e4bb4c7baf1d3f6d652"
    )
    assert tree_digest([]) == EMPTY_TREE_DIGEST


def test_private_resolution_requires_matching_task_capability(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "cas")
    reference = store.put_bytes(b"private", visibility=Visibility.PRIVATE)
    with pytest.raises(ArtifactStoreError, match="not authorized"):
        LocalArtifactResolver(store).resolve(reference)
    authorization = PrivateArtifactAuthorization(
        task_id="task-a",
        manifest_digest="sha256:" + "a" * 64,
        purpose="compile",
        allowed_digests=frozenset({reference.digest}),
        staging_root=tmp_path / "compiled" / "task-a",
    )
    assert LocalArtifactResolver(store, authorization).resolve(reference).is_file()
    denied = PrivateArtifactAuthorization(
        task_id="task-b",
        manifest_digest=authorization.manifest_digest,
        purpose="compile",
        allowed_digests=frozenset(),
        staging_root=tmp_path / "compiled" / "task-b",
    )
    with pytest.raises(ArtifactStoreError, match="not authorized"):
        LocalArtifactResolver(store, denied).resolve(reference)


def test_migration_plan_requires_all_selected_ids(tmp_path: Path) -> None:
    module = _migration_module()

    root = tmp_path / "sources"
    root.mkdir()
    (root / "ministats").mkdir()
    (root / "ministats" / "task.toml").write_text('schema_version="1.0"\ntask_id="ministats"\n')
    with pytest.raises(module.MigrationError, match="selected migration tasks are missing"):
        module.make_plan(root, tmp_path / "artifacts", tmp_path / "plan.json")


def test_migration_transaction_is_idempotent(tmp_path: Path) -> None:
    module = _migration_module()

    root = tmp_path / "sources"
    root.mkdir()
    for task_id in ("ministats", "canonicalize", "node-pnpm-synthetic", "go-google-uuid"):
        task = root / task_id
        task.mkdir()
        (task / "task.toml").write_text(
            f'schema_version="1.0"\ntask_id="{task_id}"\n'
            '[metadata]\nlanguage="python"\n'
            '[dependencies]\ninstaller="uv"\n'
            '[tests]\nframework="pytest"\nexpected_total=0\n'
        )
        (task / "instruction.md").write_text("instruction")
    plan_path = tmp_path / "migration" / "plan.json"
    module.make_plan(root, tmp_path / "artifacts", plan_path)
    transaction = module.apply_plan(plan_path)
    assert transaction["state"] == "complete"
    assert module.recover(plan_path.parent / "transaction.json")["state"] == "complete"
    assert tomllib.loads((root / "ministats" / "task.toml").read_text())["task_id"] == "ministats"
