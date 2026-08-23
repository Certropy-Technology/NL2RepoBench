from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/plan_missing_oss_runs.py"
    spec = importlib.util.spec_from_file_location("plan_missing_oss_runs", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


planner = _load_script()


def test_missing_oss_plan_skips_existing_and_blocked(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    for task_id, status in (("existing", "packaged"), ("blocked", "blocked"), ("new", "packaged")):
        task = catalog / task_id / "harbor"
        task.mkdir(parents=True)
        (task / "task.toml").write_text("schema_version = '1.4'\n", encoding="utf-8")
        for relative in planner.REQUIRED_HARBOR[1:]:
            path = task / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x", encoding="utf-8")
        (catalog / task_id / "task.toml").write_text(
            f'[metadata]\nlanguage = "python"\n[lifecycle]\nstatus = "{status}"\n',
            encoding="utf-8",
        )
    inventory = tmp_path / "oss.json"
    inventory.write_text(
        json.dumps({"runs": [{"source": "oss", "task_id": "existing"}]}),
        encoding="utf-8",
    )

    result = planner.plan(catalog, inventory, 10)

    assert [row["task_id"] for row in result["selected"]] == ["new"]
    assert {row["reason"] for row in result["skipped"]} == {
        "oss-run-exists",
        "lifecycle-blocked",
    }
