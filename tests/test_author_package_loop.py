from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/author_package_loop.py"
    spec = importlib.util.spec_from_file_location("author_package_loop", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


loop = _load_script()


def test_author_loop_filters_catalog_and_oss_but_remediates_candidates(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    (catalog / "already-catalog").mkdir(parents=True)
    candidates = tmp_path / "candidates.json"
    candidates.write_text(
        json.dumps(
            {
                "queue": [
                    {"package": "already-catalog", "language": "node", "status": "candidate"},
                    {"package": "already-oss", "language": "node", "status": "candidate"},
                    {
                        "package": "new-node",
                        "language": "node",
                        "status": "candidate",
                        "revision": "a" * 40,
                    },
                    {
                        "package": "risky",
                        "language": "node",
                        "status": "candidate",
                        "risk_flags": ["native"],
                    },
                    {"package": "needs", "language": "node", "status": "needs-evidence"},
                ]
            }
        ),
        encoding="utf-8",
    )
    inventory = tmp_path / "oss.json"
    inventory.write_text(
        json.dumps({"runs": [{"source": "oss", "task_id": "already-oss"}]}),
        encoding="utf-8",
    )

    plan = loop.build_plan(
        candidates,
        language="node",
        catalog_root=catalog,
        oss_inventory=inventory,
        limit=5,
        batch_id="node-test",
    )

    assert [task["package"] for task in plan["tasks"]] == ["needs", "new-node", "risky"]
    assert {item["reason"] for item in plan["skipped"]} == {
        "catalog-task-exists",
        "oss-run-exists",
    }
    assert plan["tasks"][0]["remediation_required"] is True
    assert plan["tasks"][0]["remediation_reasons"] == ["candidate-evidence-incomplete"]
    assert plan["tasks"][2]["remediation_reasons"] == ["risk-adaptation-required:native"]
    assert plan["agent_run_loop"].startswith("separate downstream")
    assert plan["tasks"][0]["stages"] == list(loop.STAGES)


def test_author_loop_can_resume_selected_packages_only(tmp_path: Path) -> None:
    candidates = tmp_path / "candidates.json"
    candidates.write_text(
        json.dumps(
            {
                "queue": [
                    {"package": "first", "language": "python", "status": "candidate"},
                    {"package": "second", "language": "python", "status": "candidate"},
                ]
            }
        ),
        encoding="utf-8",
    )

    plan = loop.build_plan(
        candidates,
        language="python",
        catalog_root=tmp_path / "catalog",
        oss_inventory=None,
        limit=5,
        packages={"second"},
    )

    assert [task["package"] for task in plan["tasks"]] == ["second"]
