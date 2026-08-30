from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from nl2repobench.domain.canonical_contract import DependencyBundle, TaskManifest
from nl2repobench.domain.canonical_models import ArtifactRef, Visibility
from nl2repobench.harbor.compiler import HarborCompiler
from nl2repobench.harbor.dependency_contract import (
    DependencyContractError,
    validate_dependency_artifacts,
)
from nl2repobench.harbor.node_compiler import NodeHarborCompiler
from nl2repobench.harbor.pnpm_compiler import PnpmHarborCompiler
from nl2repobench.harbor.private_artifacts import PrivateArtifactsManifest
from nl2repobench.storage.artifacts import (
    FileArtifactStore,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.storage.canonical_ustar import decode_archive, encode_files, tree_digest
from nl2repobench.storage.materialize import TARGET_MEDIA_TYPES, ArchiveKind

ROOT = Path(__file__).parents[1]


def _section(kind: str, digest: str, archive: bytes) -> dict[str, object]:
    members = decode_archive(archive)
    entries = [member.entry for member in members]
    return {
        "archive_kind": kind,
        "archive_digest": digest,
        "tree_digest": tree_digest(entries),
        "entries": [
            {
                "path": entry.path,
                "type": entry.type,
                "mode": entry.mode,
                "size": entry.size,
                "sha256": entry.sha256,
            }
            for entry in entries
        ],
        "file_count": sum(entry.type == "file" for entry in entries),
        "directory_count": sum(entry.type == "directory" for entry in entries),
        "total_bytes": sum(entry.size for entry in entries),
    }


def _dependency_refs(
    store: FileArtifactStore,
    *,
    identity: str,
    lock_name: str,
    lock_data: bytes,
) -> tuple[ArtifactRef, ArtifactRef, ArtifactRef]:
    lock_archive = encode_files({lock_name: lock_data})
    store_archive = encode_files({"cache/content": b"cached"})
    lock = store.put_bytes(
        lock_archive,
        media_type=TARGET_MEDIA_TYPES[ArchiveKind.DEPENDENCY_LOCK],
        visibility=Visibility.PRIVATE,
    )
    offline_store = store.put_bytes(
        store_archive,
        media_type=TARGET_MEDIA_TYPES[ArchiveKind.OFFLINE_STORE],
        visibility=Visibility.PRIVATE,
    )
    payload = {
        "schema_version": "1.0",
        "identity": identity,
        "adapter_version": "test-v1",
        "toolchain_digest": (
            "sha256:"
            + hashlib.sha256((ROOT / "toolchain.node.dev.lock.toml").read_bytes()).hexdigest()
        ),
        "lock": _section("dependency-lock", lock.digest, lock_archive),
        "store": _section("offline-store", offline_store.digest, store_archive),
        "offline_smoke": {"status": "passed", "command_id": "offline-test-v1"},
    }
    inventory = store.put_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n",
        media_type="application/vnd.nl2repobench.inventory+json",
        visibility=Visibility.PRIVATE,
    )
    return lock, offline_store, inventory


def _manifest(
    store: FileArtifactStore,
    *,
    manager: str,
    dependencies: tuple[ArtifactRef, ArtifactRef, ArtifactRef] | None,
) -> TaskManifest:
    instruction = store.put_bytes(b"instruction", visibility=Visibility.PUBLIC)
    command_id = "pnpm-pack-offline-v1" if manager == "pnpm" else "npm-pack-offline-v1"
    commands = store.put_bytes(
        json.dumps(
            {
                "schema_version": "1.0",
                "identity": f"node+{manager}",
                "runner": "node-test-subprocess-boundary-v1",
                "candidate_install": command_id,
                "report_format": "node-test-json-v1",
                "test_root": "/tests/private",
                "steps": [],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        + b"\n",
        visibility=Visibility.PRIVATE,
    )
    dependency_payload: dict[str, object] = {
        "status": "known",
        "package_manager": manager,
    }
    if dependencies is not None:
        dependency_payload.update(
            lock=dependencies[0],
            offline_store=dependencies[1],
            inventory=dependencies[2],
        )
    return TaskManifest.model_validate(
        {
            "task_id": f"node-{manager}",
            "metadata": {"language": "node"},
            "instruction": instruction,
            "environment_lock": {
                "status": "unknown",
                "runtime": {
                    "language": "node",
                    "runtime": "node",
                    "version": "22.23.1",
                    "package_manager": manager,
                    "package_manager_version": "9.15.0" if manager == "pnpm" else "10.9.8",
                },
            },
            "dependency_bundle": dependency_payload,
            "tests": {
                "framework": "node:test",
                "report_format": "node-test-json-v1",
                "commands_artifact": commands,
            },
            "harbor": {
                "description": "Canonical Node dependency fixture.",
                "keywords": ["node", manager, "canonical"],
                "verifier_timeout_sec": 600.0,
                "candidate_install_timeout_sec": 90.0,
                "candidate_total_timeout_sec": 300.0,
                "agent_network_mode": "no-network",
            },
        }
    )


def _resolver(
    store: FileArtifactStore,
    manifest: TaskManifest,
    tmp_path: Path,
) -> LocalArtifactResolver:
    digests = {
        reference.digest
        for reference in (
            manifest.dependency_bundle.lock,
            manifest.dependency_bundle.offline_store,
            manifest.dependency_bundle.inventory,
            manifest.tests.commands_artifact,
        )
        if reference is not None
    }
    authorization = PrivateArtifactAuthorization(
        task_id=manifest.task_id,
        manifest_digest=manifest.content_digest(),
        purpose="compile",
        allowed_digests=frozenset(digests),
        staging_root=(tmp_path / "compiled/private").resolve(),
    )
    return LocalArtifactResolver.scoped_private(
        store,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )


@pytest.mark.parametrize(
    ("manager", "lock_name", "lock_data", "compiler_type"),
    [
        (
            "npm",
            "package-lock.json",
            b'{"lockfileVersion":3,"packages":{"":{}}}',
            NodeHarborCompiler,
        ),
        ("pnpm", "pnpm-lock.yaml", b"lockfileVersion: '9.0'\n", PnpmHarborCompiler),
    ],
)
def test_node_adapters_consume_canonical_dependencies_and_command_plan(
    tmp_path: Path,
    manager: str,
    lock_name: str,
    lock_data: bytes,
    compiler_type: type[NodeHarborCompiler],
) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    refs = _dependency_refs(
        store,
        identity=f"node+{manager}",
        lock_name=lock_name,
        lock_data=lock_data,
    )
    manifest = _manifest(store, manager=manager, dependencies=refs)
    resolver = _resolver(store, manifest, tmp_path)
    compiler = compiler_type(ROOT / "toolchain.node.dev.lock.toml", artifact_resolver=resolver)

    compiler._validate_canonical_dependencies(manifest)  # noqa: SLF001
    plan = compiler._resolve_node_command_plan(manifest, False)  # noqa: SLF001
    script = compiler._test_script(manifest)  # noqa: SLF001

    assert plan.candidate_install.startswith(manager)
    assert '[[ "$network_exit" -eq 1 ]]' in script
    assert '[[ "$network_exit" -ne 0 ]]' in script
    assert "verifier-internal-error" in script


def test_dependency_inventory_tampering_fails_closed(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    refs = _dependency_refs(
        store,
        identity="node+npm",
        lock_name="package-lock.json",
        lock_data=b'{"lockfileVersion":3,"packages":{"":{}}}',
    )
    manifest = _manifest(store, manager="npm", dependencies=refs)
    resolver = _resolver(store, manifest, tmp_path)
    bad_bundle = manifest.dependency_bundle.model_copy(
        update={"inventory": refs[0]}
    )

    with pytest.raises(DependencyContractError, match="inventory media type"):
        validate_dependency_artifacts(
            bad_bundle,
            identity="node+npm",
            toolchain_digest=(
                "sha256:"
                + hashlib.sha256(
                    (ROOT / "toolchain.node.dev.lock.toml").read_bytes()
                ).hexdigest()
            ),
            resolver=resolver,
        )


def test_python_none_requires_canonical_empty_closure(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    instruction = store.put_bytes(b"instruction", visibility=Visibility.PUBLIC)
    commands = store.put_bytes(b"commands", visibility=Visibility.PRIVATE)
    empty_archive = b"\0" * 10240
    lock = store.put_bytes(
        empty_archive,
        media_type=TARGET_MEDIA_TYPES[ArchiveKind.DEPENDENCY_LOCK],
        visibility=Visibility.PRIVATE,
    )
    offline_store = store.put_bytes(
        empty_archive,
        media_type=TARGET_MEDIA_TYPES[ArchiveKind.OFFLINE_STORE],
        visibility=Visibility.PRIVATE,
    )
    toolchain_digest = "sha256:" + hashlib.sha256(
        (ROOT / "toolchain.lock.toml").read_bytes()
    ).hexdigest()
    payload = {
        "schema_version": "1.0",
        "identity": "python+none",
        "adapter_version": "test-v1",
        "toolchain_digest": toolchain_digest,
        "lock": _section("dependency-lock", lock.digest, empty_archive),
        "store": _section("offline-store", offline_store.digest, empty_archive),
        "offline_smoke": {"status": "passed", "command_id": "none-noop-v1"},
    }
    inventory = store.put_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n",
        media_type="application/vnd.nl2repobench.inventory+json",
        visibility=Visibility.PRIVATE,
    )
    manifest = TaskManifest.model_validate(
        {
            "task_id": "python-none",
            "metadata": {"language": "python"},
            "instruction": instruction,
            "environment_lock": {
                "status": "unknown",
                "runtime": {
                    "language": "python",
                    "runtime": "cpython",
                    "version": "3.12",
                    "package_manager": "none",
                },
            },
            "dependency_bundle": {
                "status": "known",
                "package_manager": "none",
                "lock": lock,
                "offline_store": offline_store,
                "inventory": inventory,
            },
            "tests": {
                "framework": "pytest",
                "report_format": "pytest-junit-xml-v1",
                "commands_artifact": commands,
            },
        }
    )
    resolver = _resolver(store, manifest, tmp_path)
    compiler = HarborCompiler(ROOT / "toolchain.lock.toml", artifact_resolver=resolver)

    assert compiler._resolve_dependency_lock(manifest, False) == b""  # noqa: SLF001
    assert not any(gap.startswith("dependency_bundle.") for gap in manifest.publication_gaps())
    compiler._write_environment(manifest, tmp_path / "task", b"", False)  # noqa: SLF001
    dockerfile = (tmp_path / "task/environment/Dockerfile").read_text(encoding="utf-8")
    assert 'agent-dependency-build="none-v1"' in dockerfile
    assert "candidate-requirements.lock.txt /tmp" not in dockerfile


def test_known_none_dependency_bundle_requires_all_three_private_refs() -> None:
    with pytest.raises(ValidationError, match="requires lock, offline_store, and inventory"):
        DependencyBundle.model_validate({"status": "known", "package_manager": "none"})


def test_node_private_artifact_projection_is_strict(tmp_path: Path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    refs = _dependency_refs(
        store,
        identity="node+npm",
        lock_name="package-lock.json",
        lock_data=b'{"lockfileVersion":3,"packages":{"":{}}}',
    )
    manifest = _manifest(store, manager="npm", dependencies=refs)
    compiler = NodeHarborCompiler(ROOT / "toolchain.node.dev.lock.toml")
    task_root = tmp_path / "task"
    task_root.mkdir()

    compiler._write_bundle_manifest(manifest, task_root, False)  # noqa: SLF001

    payload = json.loads((task_root / "bundle.manifest.json").read_text(encoding="utf-8"))
    private = PrivateArtifactsManifest.model_validate(payload["private_artifacts"])
    assert private.task_id == manifest.task_id
    assert private.canonical_manifest_digest == manifest.content_digest()
    assert private.verifier.bundle is None
