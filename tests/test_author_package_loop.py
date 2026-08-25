from __future__ import annotations

import hashlib
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


def _write_source(
    root: Path,
    *,
    status: str,
    reason: str = "",
    failure_class: str | None = None,
    next_step: str | None = None,
) -> None:
    root.mkdir(parents=True)
    (root / "instruction.md").write_text("# task\n", encoding="utf-8")
    (root / "task.toml").write_text(
        'schema_version = "1.0"\n'
        f'task_id = "{root.name}"\n'
        'instruction = "instruction.md"\n\n'
        "[lifecycle]\n"
        f'status = "{status}"\n'
        f"reason = {json.dumps(reason)}\n",
        encoding="utf-8",
    )
    if failure_class is not None:
        (root / "production-evidence.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "task_id": root.name,
                    "terminal_kind": "blocked",
                    "blocked": {
                        "failure_class": failure_class,
                        "next_step": next_step or "",
                    },
                }
            ),
            encoding="utf-8",
        )


def _write_complete_harbor_task(root: Path) -> None:
    files = {
        "environment/Dockerfile": "FROM scratch\n",
        "instruction.md": "# task\n",
        "solution/solve.sh": "#!/bin/sh\n",
        "task.toml": 'schema_version = "1.4"\n',
        "tests/test.sh": "#!/bin/sh\n",
    }
    rows = []
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        payload = content.encode()
        rows.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size_bytes": len(payload),
            }
        )
    (root / "bundle.manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "mode": "production",
                "files": sorted(rows, key=lambda row: row["path"]),
            }
        ),
        encoding="utf-8",
    )


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
    assert plan["tasks"][0]["handoff_status"] == "authoring-in-progress"
    assert plan["tasks"][0]["stages"] == list(loop.STAGES)
    assert "environment-remediation" in plan["stages"]
    assert plan["remediation_policy"]["missing_hash_locked_offline_closure"] == "must-remediate"
    assert plan["remediation_policy"]["storage"]["tmpfs_policy"].startswith("small bounded")
    assert plan["worker_guidance"].endswith("authoring-agent-remediation-guide.zh-CN.md")


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


def test_remediation_selects_missing_incomplete_and_repairable_blocked_sources(
    tmp_path: Path,
) -> None:
    sources = tmp_path / "catalog/sources"
    tasks = tmp_path / "catalog/tasks"
    _write_source(sources / "missing-task", status="discovered")
    _write_source(sources / "incomplete-task", status="discovered")
    (tasks / "incomplete-task").mkdir(parents=True)
    (tasks / "incomplete-task/instruction.md").write_text("# partial\n", encoding="utf-8")
    _write_source(sources / "complete-task", status="controls-passed")
    _write_complete_harbor_task(tasks / "complete-task")
    _write_source(sources / "drifted-task", status="controls-passed")
    _write_complete_harbor_task(tasks / "drifted-task")
    (tasks / "drifted-task/environment/Dockerfile").write_text("FROM changed\n", encoding="utf-8")
    _write_source(
        sources / "repairable-blocked",
        status="blocked",
        reason="The npm dependency closure is missing.",
        failure_class="environment",
        next_step="Freeze the package lock and rerun the offline install.",
    )
    _write_source(
        sources / "manual-blocked",
        status="blocked",
        reason="Two incompatible public contracts remain.",
        failure_class="spec",
        next_step="Choose one coherent version boundary.",
    )
    _write_source(
        sources / "terminal-blocked",
        status="blocked",
        reason="The only API requires a paid external service.",
        failure_class="environment",
        next_step="Obtain a paid service subscription.",
    )
    candidates = tmp_path / "candidates.json"
    packages = [
        "missing-task",
        "incomplete-task",
        "complete-task",
        "drifted-task",
        "repairable-blocked",
        "manual-blocked",
        "terminal-blocked",
        "source-missing",
    ]
    candidates.write_text(
        json.dumps(
            {
                "queue": [
                    {
                        "candidate_id": f"python-{package}",
                        "package": package,
                        "language": "python",
                        "status": "existing",
                    }
                    for package in packages
                ]
            }
        ),
        encoding="utf-8",
    )
    inventory = tmp_path / "oss.json"
    inventory.write_text(
        json.dumps({"runs": [{"source": "oss", "task_id": "missing-task"}]}),
        encoding="utf-8",
    )

    plan = loop.build_plan(
        candidates,
        language="python",
        catalog_root=sources,
        tasks_root=tasks,
        oss_inventory=inventory,
        limit=10,
        remediation=True,
        batch_id="python-remediation",
    )

    assert [task["package"] for task in plan["tasks"]] == [
        "drifted-task",
        "incomplete-task",
        "missing-task",
        "repairable-blocked",
    ]
    by_package = {task["package"]: task for task in plan["tasks"]}
    assert by_package["incomplete-task"]["remediation_reasons"] == ["harbor-task-incomplete"]
    assert by_package["drifted-task"]["remediation_reasons"] == ["harbor-task-incomplete"]
    assert by_package["missing-task"]["remediation_reasons"] == ["harbor-task-missing"]
    assert by_package["repairable-blocked"]["remediation_reasons"] == [
        "blocked-source-repairable",
        "harbor-task-missing",
    ]
    assert by_package["repairable-blocked"]["queue_reclaim_statuses"] == [
        "blocked",
        "complete",
    ]
    assert by_package["missing-task"]["source_root"] == "catalog/sources/missing-task"
    assert by_package["missing-task"]["harbor_task_root"] == ("catalog/tasks/missing-task")
    assert plan["remediation_mode"] is True
    skipped = {item["package"]: item["reason"] for item in plan["skipped"]}
    assert skipped == {
        "complete-task": "harbor-task-complete",
        "manual-blocked": "blocked-manual",
        "source-missing": "source-missing",
        "terminal-blocked": "blocked-terminal",
    }
