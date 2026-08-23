from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_script(name: str):
    path = Path(__file__).parents[1] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


campaign = _load_script("validate_campaign")
published = _load_script("validate_published_datasets")


def _task(root: Path, task_id: str, language: str) -> tuple[Path, Path]:
    task = root / task_id
    (task / "harbor").mkdir(parents=True)
    source = task / "task.toml"
    source.write_text(
        f'''schema_version = "1.0"
task_id = "{task_id}"
[metadata]
language = "{language}"
[source]
status = "known"
upstream_url = "https://github.com/example/{task_id}"
revision = "{'a' * 40}"
license_spdx = "MIT"
[lifecycle]
status = "published"
''',
        encoding="utf-8",
    )
    harbor = task / "harbor/task.toml"
    harbor.write_text('schema_version = "1.4"\n', encoding="utf-8")
    return source, harbor


def _evidence(task_id: str, language: str, dataset_id: str) -> dict[str, object]:
    controls = {
        name: {
            "passed": True,
            "evidence": [f"controls/{name}/result.json"],
            "result": "low-score" if name in {"empty", "stub", "forgery"} else "completed",
            **(
                {"reward": 0.0}
                if name in {"empty", "stub", "forgery"}
                else {"completed": True}
            ),
        }
        for name in campaign.REQUIRED_CONTROLS
    }
    return {
        "task_id": task_id,
        "language": language,
        "dataset_id": dataset_id,
        "candidate": {
            "source_kind": "pypi" if language == "python" else "npm",
            "upstream_url": f"https://github.com/example/{task_id}",
            "revision": "a" * 40,
            "license_spdx": "MIT",
            "observed_at": "2026-08-20T00:00:00Z",
            "last_activity": "2026-01-01T00:00:00Z",
            "stars": 100,
            "monthly_downloads": 0,
            "evidence_url": "https://example.invalid/evidence",
        },
        "oracle_runs": [
            {
                "valid": True,
                "reward": 0.9,
                "expected_total": 10,
                "collected_total": 10,
                "oracle_ceiling": 0.9,
                "failure_set": ["test_failure"],
                "reason": "one stable upstream failure",
            }
        ],
        "controls": controls,
        "model_runs": [
            {
                "model": "gpt-5.6-sol",
                "attempts": 1,
                "status": "completed",
                "valid": True,
            },
            {
                "model": "claude-fable-5",
                "attempts": 1,
                "status": "completed",
                "valid": True,
            },
        ],
    }


def test_campaign_accepts_two_separate_language_lanes(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog" / "tasks"
    py_source, py_harbor = _task(catalog, "py-demo", "python")
    node_source, node_harbor = _task(catalog, "node-demo", "node")
    campaign_path = tmp_path / "campaign.json"
    payload = {
        "schema_version": "1.0",
        "campaign_id": "test",
        "as_of": "2026-08-23T00:00:00Z",
        "datasets": [
            {"dataset_id": "python-v1", "language": "python"},
            {"dataset_id": "node-v1", "language": "node"},
        ],
        "tasks": [
            _evidence("py-demo", "python", "python-v1"),
            _evidence("node-demo", "node", "node-v1"),
        ],
    }
    campaign_path.write_text(json.dumps(payload), encoding="utf-8")

    result = campaign.validate_campaign(
        campaign_path, catalog_root=catalog, minimum_tasks=2
    )

    assert result["status"] == "releaseable"
    assert result["task_count"] == 2
    assert all(
        path.is_file()
        for path in (py_source, py_harbor, node_source, node_harbor)
    )


def test_campaign_fails_closed_below_target(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog" / "tasks"
    _task(catalog, "demo", "python")
    payload = {
        "schema_version": "1.0",
        "as_of": "2026-08-23T00:00:00Z",
        "datasets": [{"dataset_id": "python-v1", "language": "python"}],
        "tasks": [_evidence("demo", "python", "python-v1")],
    }
    path = tmp_path / "campaign.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="below required minimum"):
        campaign.validate_campaign(path, catalog_root=catalog, minimum_tasks=2)


def test_campaign_allows_existing_oss_task_without_new_oracle_or_model_runs(
    tmp_path: Path,
) -> None:
    catalog = tmp_path / "catalog" / "tasks"
    source, harbor = _task(catalog, "demo", "python")
    payload = {
        "schema_version": "1.0",
        "as_of": "2026-08-23T00:00:00Z",
        "datasets": [{"dataset_id": "python-v1", "language": "python"}],
        "tasks": [
            {
                "task_id": "demo",
                "language": "python",
                "dataset_id": "python-v1",
                "existing_oss": True,
                "oss_run_refs": [
                    {
                        "source": "oss",
                        "task_id": "demo",
                        "model": "gpt-5.6-sol",
                        "prefix": "nl2repobench/runs/gpt-5.6-sol/demo/trial/",
                        "status": "completed",
                        "evidence_keys": [
                            "nl2repobench/runs/gpt-5.6-sol/demo/trial/result.json"
                        ],
                        "revision_binding": "unbound-legacy",
                    }
                ],
                "candidate": {
                    "source_kind": "pypi",
                    "upstream_url": "https://github.com/example/demo",
                    "revision": "a" * 40,
                    "license_spdx": "MIT",
                    "observed_at": "2026-08-20T00:00:00Z",
                    "last_activity": "2026-01-01T00:00:00Z",
                    "stars": 100,
                    "monthly_downloads": 0,
                    "evidence_url": "https://example.invalid/evidence",
                },
                "controls": {
                    name: {
                        "passed": True,
                        "evidence": [f"controls/{name}/result.json"],
                        "result": (
                            "low-score"
                            if name in {"empty", "stub", "forgery"}
                            else "completed"
                        ),
                        **(
                            {"reward": 0.0}
                            if name in {"empty", "stub", "forgery"}
                            else {"completed": True}
                        ),
                    }
                    for name in campaign.REQUIRED_CONTROLS
                },
            }
        ],
    }
    path = tmp_path / "campaign.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    result = campaign.validate_campaign(path, catalog_root=catalog, minimum_tasks=1)

    assert result["task_count"] == 1
    assert source.is_file() and harbor.is_file()


def test_campaign_binds_oss_inventory_hash(tmp_path: Path) -> None:
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps({"source": "oss", "runs": []}), encoding="utf-8"
    )
    import hashlib

    path = tmp_path / "campaign.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "as_of": "2026-08-23T00:00:00Z",
                "oss_run_inventory": {
                    "path": "inventory.json",
                    "sha256": "sha256:" + hashlib.sha256(inventory.read_bytes()).hexdigest(),
                },
                "datasets": [{"dataset_id": "python-v1", "language": "python"}],
                "tasks": [],
            }
        ),
        encoding="utf-8",
    )

    result = campaign.validate_campaign(
        path, catalog_root=tmp_path / "catalog", minimum_tasks=0, allow_below_target=True
    )

    assert result["task_count"] == 0


def test_published_dataset_validator_matches_compiled_entries(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog" / "tasks"
    source, harbor = _task(catalog, "demo", "python")
    dataset_source = tmp_path / "catalog" / "datasets" / "python.toml"
    dataset_source.parent.mkdir(parents=True)
    dataset_source.write_text(
        'dataset_id = "python-v1"\nversion = "1.0.0"\ntasks = ["demo"]\n',
        encoding="utf-8",
    )
    compiled = tmp_path / "build" / "python"
    (compiled / "demo").mkdir(parents=True)
    (compiled / "dataset.manifest.json").write_text(
        json.dumps(
            {
                "dataset_id": "python-v1",
                "version": "1.0.0",
                "tasks": [{"task_id": "demo"}],
            }
        ),
        encoding="utf-8",
    )
    (compiled / "demo/manifest.json").write_text(
        json.dumps({"lifecycle": {"status": "published"}}), encoding="utf-8"
    )
    campaign_path = tmp_path / "campaign.json"
    campaign_path.write_text(
        json.dumps(
            {
                "datasets": [
                    {
                        "dataset_id": "python-v1",
                        "language": "python",
                        "source": "catalog/datasets/python.toml",
                        "compiled": "build/python",
                    }
                ],
                "tasks": [
                    {
                        "task_id": "demo",
                        "source_manifest_sha256": "sha256:" + hashlib.sha256(
                            source.read_bytes()
                        ).hexdigest(),
                        "harbor_task_sha256": "sha256:" + hashlib.sha256(
                            harbor.read_bytes()
                        ).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = published.validate_published_datasets(campaign_path, catalog_root=catalog)

    assert result["task_count"] == 1
