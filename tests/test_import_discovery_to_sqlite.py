from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path
from typing import Any, cast

import pytest

from nl2repobench.authoring.scheduler import Scheduler

SCRIPT = Path(__file__).parents[1] / "scripts/import_discovery_to_sqlite.py"
SPEC = importlib.util.spec_from_file_location("import_discovery", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _setup(tmp_path: Path, *, language: str = "go") -> tuple[Path, Path, Path, Path]:
    root = tmp_path / "root"
    root.mkdir()
    db = root / "scheduler.sqlite3"
    scheduler = Scheduler(db, supplied_root=root)
    scheduler.init()
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
        reason="test prepared database",
    )
    scheduler.prepare_cutover_barrier("cutover-test", "a" * 64)
    queue = root / "queue.json"
    queue.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "queue": [
                    {
                        "candidate_id": "candidate-one",
                        "package": "go-demo",
                        "language": language,
                        "source_kind": "go-modules",
                        "upstream_url": "https://github.com/example/go-demo",
                        "revision": "a" * 40,
                        "status": "candidate",
                    },
                    {
                        "candidate_id": "candidate-two",
                        "package": "go-demo-two",
                        "language": language,
                        "source_kind": "go-modules",
                        "upstream_url": "https://github.com/example/go-demo-two",
                        "revision": "b" * 40,
                        "status": "candidate",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    plan = root / "plan.json"
    plan.write_text(
        json.dumps({"schema_version": "1.0", "batch_id": "batch-test", "language": language}),
        encoding="utf-8",
    )
    return root, db, queue, plan


def _import(tmp_path: Path, **updates: Any) -> dict[str, object]:
    root, db, queue, plan = _setup(tmp_path)
    args: dict[str, object] = {
        "root": root,
        "db": db,
        "queue": queue,
        "plan": plan,
        "batch_id": "batch-test",
        "language": "go",
        "authorization": "operator-approval-1",
        "owner": "owner-1",
    }
    args.update(updates)
    return cast(dict[str, object], MODULE.import_discovery(**args))


def test_imports_generated_lane_and_zero_attempt_tasks(tmp_path: Path) -> None:
    result = _import(tmp_path)
    assert result["status"] == "imported"
    assert result["candidate_count"] == 2
    root = tmp_path / "root"
    with sqlite3.connect(root / "scheduler.sqlite3") as db:
        lane = db.execute(
            "select lane_id,batch_id,language,kind,queue_path,plan_path "
            "from lanes where batch_id=?",
            ("batch-test",),
        ).fetchone()
        tasks = db.execute(
            "select state,authoring_attempts,attempt_limit,task_release "
            "from tasks where lane_id=? order by input_ordinal",
            (lane[0],),
        ).fetchall()
        source_reports = db.execute(
            "select source_reports_json from lanes where lane_id=?", (lane[0],)
        ).fetchone()[0]
    assert lane[:4] == ("generated-go-batch-test", "batch-test", "go", "generated")
    assert lane[4:6] == ("queue.json", "plan.json")
    assert tasks == [("pending", 0, 3, "discovery"), ("pending", 0, 3, "discovery")]
    assert "queue_sha256:" in source_reports and "plan_sha256:" in source_reports
    assert "authorization_sha256:" in source_reports and "owner_sha256:" in source_reports


def test_import_is_duplicate_safe_and_does_not_reset_existing_attempts(tmp_path: Path) -> None:
    root, db, queue, plan = _setup(tmp_path)
    kwargs = {
        "root": root,
        "db": db,
        "queue": queue,
        "plan": plan,
        "batch_id": "batch-test",
        "language": "go",
        "authorization": "operator-approval-1",
        "owner": "owner-1",
    }
    MODULE.import_discovery(**kwargs)
    with pytest.raises(MODULE.DiscoveryImportError, match="already exists"):
        MODULE.import_discovery(**kwargs)
    with sqlite3.connect(db) as connection:
        assert connection.execute("select count(*) from lanes").fetchone()[0] == 1
        assert connection.execute("select count(*) from tasks").fetchone()[0] == 2


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("language", "rust", "language"),
        ("batch_id", "../unsafe", "batch_id"),
        ("authorization", "TODO", "authorization"),
        ("owner", "", "owner"),
    ],
)
def test_import_rejects_unsafe_control_fields(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    with pytest.raises(MODULE.DiscoveryImportError, match=message):
        _import(tmp_path, **{field: value})


def test_import_rejects_malformed_candidate_and_plan_mismatch(tmp_path: Path) -> None:
    root, db, queue, plan = _setup(tmp_path)
    payload = json.loads(queue.read_text(encoding="utf-8"))
    payload["queue"][0]["revision"] = "A" * 40
    queue.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(MODULE.DiscoveryImportError, match="complete lowercase"):
        MODULE.import_discovery(
            root=root,
            db=db,
            queue=queue,
            plan=plan,
            batch_id="batch-test",
            language="go",
            authorization="operator-approval-1",
            owner="owner-1",
        )
    payload = json.loads(queue.read_text(encoding="utf-8"))
    payload["queue"][0]["revision"] = "a" * 40
    payload["queue"][1]["candidate_id"] = payload["queue"][0]["candidate_id"]
    queue.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(MODULE.DiscoveryImportError, match="duplicate"):
        MODULE.import_discovery(
            root=root,
            db=db,
            queue=queue,
            plan=plan,
            batch_id="batch-test",
            language="go",
            authorization="operator-approval-1",
            owner="owner-1",
        )
    plan.write_text(json.dumps({"batch_id": "other", "language": "go"}), encoding="utf-8")
    with pytest.raises(MODULE.DiscoveryImportError, match="plan.batch_id"):
        MODULE.import_discovery(
            root=root,
            db=db,
            queue=queue,
            plan=plan,
            batch_id="batch-test",
            language="go",
            authorization="operator-approval-1",
            owner="owner-1",
        )


def test_import_rejects_missing_barrier_and_unsafe_input_path(tmp_path: Path) -> None:
    root, db, queue, plan = _setup(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute("delete from cutover_barrier")
    with pytest.raises(MODULE.DiscoveryImportError, match="barrier"):
        MODULE.import_discovery(
            root=root,
            db=db,
            queue=queue,
            plan=plan,
            batch_id="batch-test",
            language="go",
            authorization="operator-approval-1",
            owner="owner-1",
        )
    outside = tmp_path / "outside.json"
    outside.write_text(queue.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(MODULE.DiscoveryImportError, match="inside"):
        MODULE.import_discovery(
            root=root,
            db=db,
            queue=outside,
            plan=plan,
            batch_id="batch-test",
            language="go",
            authorization="operator-approval-1",
            owner="owner-1",
        )
