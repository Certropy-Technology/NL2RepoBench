from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load():
    path = Path(__file__).parents[1] / "scripts/create_authoring_repair_lane.py"
    spec = importlib.util.spec_from_file_location("create_repair_lane_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


repair = _load()


def test_task_record_binds_existing_catalog_source(tmp_path: Path) -> None:
    source = tmp_path / "catalog/sources/demo"
    source.mkdir(parents=True)
    source.joinpath("task.toml").write_text(
        '''[metadata]
language = "python"
[source]
upstream_url = "https://github.com/example/demo"
revision = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
license_spdx = "MIT"
''',
        encoding="utf-8",
    )

    record = repair.task_record(tmp_path, "demo", "python", "repair-test")

    assert record["candidate_id"] == "repair-demo-repair-test"
    assert record["repair_existing"] is True
    assert record["source_kind"] == "pypi"
    assert record["revision"] == "a" * 40


def test_create_lane_prepends_priority_repair_registry(
    tmp_path: Path, monkeypatch
) -> None:
    repository = tmp_path / "repo"
    live = repository / ".nl2repo/authoring-live"
    source = repository / "catalog/sources/demo"
    source.mkdir(parents=True)
    source.joinpath("task.toml").write_text(
        '[metadata]\nlanguage = "node"\n[source]\nrevision = "' + "a" * 40 + '"\n',
        encoding="utf-8",
    )
    (live / "plans").mkdir(parents=True)
    (live / "plans/node-author-wave2-20260828.json").write_text(
        '{"schema_version":"1.0","tasks":[]}', encoding="utf-8"
    )
    registry = live / "supervisor/generated-lanes.json"
    registry.parent.mkdir(parents=True)
    registry.write_text('[{"batch_id":"normal","repair_existing":false}]', encoding="utf-8")

    class Result:
        returncode = 0
        stderr = ""

    def fake_run(command, **_kwargs):
        state = Path(command[command.index("--state") + 1])
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text('{"items":{}}', encoding="utf-8")
        return Result()

    monkeypatch.setattr(repair.subprocess, "run", fake_run)
    result = repair.create_lane(
        repository,
        live,
        language="node",
        batch_id="node-priority-repair",
        packages=["demo"],
    )

    lanes = json.loads(registry.read_text(encoding="utf-8"))
    assert lanes[0]["batch_id"] == "node-priority-repair"
    assert lanes[0]["repair_existing"] is True
    assert Path(result["queue"]).is_file()
    assert json.loads(Path(result["plan"]).read_text())["required_production_controls"] == list(
        repair.REQUIRED_CONTROLS
    )
