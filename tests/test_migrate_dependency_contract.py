from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import tomli_w


def _migration_module():
    script = Path(__file__).parents[1] / "scripts/migrate_dependency_contract.py"
    specification = importlib.util.spec_from_file_location(
        "migrate_dependency_contract", script
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    try:
        specification.loader.exec_module(module)
    finally:
        del sys.modules[specification.name]
    return module


def test_source_task_paths_include_scoped_sources_and_exclude_harbor_inputs(
    tmp_path: Path,
) -> None:
    sources = tmp_path / "sources"
    for relative in (
        "flat/task.toml",
        "@scope/package/task.toml",
        "flat/harbor/task.toml",
    ):
        path = sources / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('schema_version = "1.0"\n', encoding="utf-8")

    module = _migration_module()

    paths = [
        path.relative_to(sources).as_posix()
        for path in module._source_task_paths(sources)
    ]

    assert paths == [
        "@scope/package/task.toml",
        "flat/task.toml",
    ]


def test_canonical_dependency_block_is_stable_for_scoped_source(tmp_path: Path) -> None:
    sources = tmp_path / "sources"
    descriptor = sources / "@scope" / "package" / "task.toml"
    descriptor.parent.mkdir(parents=True)
    digest = "sha256:" + "a" * 64
    reference = {
        "digest": digest,
        "size_bytes": 1,
        "media_type": "application/octet-stream",
        "uri": "artifact://private/" + digest,
        "visibility": "private",
    }
    descriptor.write_text(
        tomli_w.dumps(
            {
                "dependencies": {
                    "status": "unknown",
                    "package_manager": "npm",
                    "packages": [],
                    "lock": reference,
                    "offline_store": reference,
                    "inventory": reference,
                }
            }
        ),
        encoding="utf-8",
    )

    module = _migration_module()
    report = module.migrate(
        tmp_path,
        sources,
        module.FileArtifactStore(tmp_path / "artifacts"),
        (tmp_path / "artifacts",),
        apply=False,
    )

    assert report["ok"] is True
    assert report["sources"] == 1


def test_missing_private_verifier_is_recovered_from_generated_runtime(
    tmp_path: Path,
) -> None:
    task_id = "example"
    source = {
        "verifier": {
            "bundle": {
                "digest": "sha256:" + "a" * 64,
                "size_bytes": 1,
                "media_type": "application/vnd.nl2repobench.private-bundle+tar",
                "uri": "artifact://private/sha256:" + "a" * 64,
                "visibility": "private",
            }
        }
    }
    verifier = tmp_path / "catalog/tasks" / task_id / "tests/verifier"
    verifier.mkdir(parents=True)
    (verifier / "run.py").write_text("print('trusted')\n", encoding="utf-8")
    module = _migration_module()
    store = module.FileArtifactStore(tmp_path / "artifacts")

    recovered = module._recover_runtime_private_artifacts(
        tmp_path,
        task_id,
        source,
        store,
        (tmp_path / "artifacts",),
    )

    replacement = source["verifier"]["bundle"]
    assert recovered == ["verifier.bundle"]
    assert replacement["digest"] != "sha256:" + "a" * 64
    artifact = module.ArtifactRef.model_validate(replacement)
    assert store.path_for(artifact, allow_private=True).is_file()
