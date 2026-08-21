from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "convert_testfiles_loop", ROOT / "scripts/convert_testfiles_loop.py"
)
assert SPEC and SPEC.loader
loop = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(loop)


def legacy_task(root: Path, task_id: str) -> None:
    task = root / task_id
    task.mkdir(parents=True)
    (task / "start.md").write_text("# Build demo\n", encoding="utf-8")
    (task / "test_case_count.txt").write_text("1\n", encoding="utf-8")
    (task / "test_commands.json").write_text('["pytest tests"]\n', encoding="utf-8")
    (task / "test_files.json").write_text('["tests"]\n', encoding="utf-8")


def complete_task(root: Path, task_id: str) -> None:
    task = root / task_id
    for relative in loop.REQUIRED_HARBOR:
        path = task / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n", encoding="utf-8")


def test_sync_marks_only_structurally_complete_bundles(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    catalog = tmp_path / "catalog/tasks"
    legacy_task(legacy, "done")
    legacy_task(legacy, "todo")
    complete_task(catalog, "done")
    state: dict[str, object] = {"tasks": {}}

    records = loop.sync_state(state, legacy, catalog)

    assert records["done"]["status"] == "complete"
    assert records["todo"]["status"] == "pending"


def test_claim_is_exclusive_and_expired_lease_can_be_reclaimed(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    catalog = tmp_path / "catalog/tasks"
    legacy_task(legacy, "demo")
    state_path = tmp_path / "state.json"
    args = type(
        "Args",
        (),
        {
            "state": state_path,
            "legacy_root": legacy,
            "catalog_root": catalog,
            "owner": "worker-a",
            "limit": 1,
            "tasks": None,
            "lease_seconds": 60,
        },
    )()
    assert loop.command_claim(args) == 0
    args.owner = "worker-b"
    assert loop.command_claim(args) == 2

    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["tasks"]["demo"]["lease_expires_at"] = "2000-01-01T00:00:00+00:00"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    assert loop.command_claim(args) == 0


def test_complete_bundle_requires_every_file(tmp_path) -> None:
    complete_task(tmp_path, "demo")
    assert loop.complete_bundle(tmp_path / "demo")
    (tmp_path / "demo/harbor/tests/grade.py").unlink()
    assert not loop.complete_bundle(tmp_path / "demo")


def test_reopen_preserves_blocker_history(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    catalog = tmp_path / "catalog/tasks"
    legacy_task(legacy, "demo")
    state_path = tmp_path / "state.json"
    with loop.locked_state(state_path) as state:
        records = loop.sync_state(state, legacy, catalog)
        records["demo"].update({"status": "blocked", "reason": "registry unavailable"})
    args = type(
        "Args",
        (),
        {
            "state": state_path,
            "legacy_root": legacy,
            "catalog_root": catalog,
            "task_id": "demo",
            "reason": "registry retry succeeded",
        },
    )()

    assert loop.command_reopen(args) == 0
    record = json.loads(state_path.read_text(encoding="utf-8"))["tasks"]["demo"]
    assert record["status"] == "pending"
    assert record["reopen_history"][0]["previous_reason"] == "registry unavailable"


def test_sync_does_not_overwrite_explicit_blocker_with_complete_bundle(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    catalog = tmp_path / "catalog/tasks"
    legacy_task(legacy, "demo")
    complete_task(catalog, "demo")
    state: dict[str, object] = {
        "tasks": {
            "demo": {
                **loop.default_record("demo"),
                "status": "blocked",
                "reason": "hidden test boundary incomplete",
            }
        }
    }

    records = loop.sync_state(state, legacy, catalog)

    assert records["demo"]["status"] == "blocked"


def test_block_command_can_record_integrator_decision(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    catalog = tmp_path / "catalog/tasks"
    legacy_task(legacy, "demo")
    state_path = tmp_path / "state.json"
    with loop.locked_state(state_path) as state:
        loop.sync_state(state, legacy, catalog)
    args = type(
        "Args",
        (),
        {
            "state": state_path,
            "legacy_root": legacy,
            "catalog_root": catalog,
            "task_id": "demo",
            "owner": "integrator",
            "reason": "no private test artifact",
            "artifact": [],
        },
    )()

    assert loop.command_block(args) == 0
    record = json.loads(state_path.read_text(encoding="utf-8"))["tasks"]["demo"]
    assert record["status"] == "blocked"
    assert record["block_history"][0]["previous_status"] == "pending"


def test_block_can_reclaim_expired_writer_lease(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    catalog = tmp_path / "catalog/tasks"
    legacy_task(legacy, "demo")
    state_path = tmp_path / "state.json"
    with loop.locked_state(state_path) as state:
        records = loop.sync_state(state, legacy, catalog)
        records["demo"].update(
            {
                "status": "running",
                "owner": "dead-worker",
                "lease_expires_at": "2000-01-01T00:00:00+00:00",
            }
        )
    args = type(
        "Args",
        (),
        {
            "state": state_path,
            "legacy_root": legacy,
            "catalog_root": catalog,
            "task_id": "demo",
            "owner": "integrator",
            "reason": "worker completed without state handoff",
            "artifact": [],
        },
    )()

    assert loop.command_block(args) == 0
    record = json.loads(state_path.read_text(encoding="utf-8"))["tasks"]["demo"]
    assert record["status"] == "blocked"


def test_block_takeover_records_explicit_integrator_override(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    catalog = tmp_path / "catalog/tasks"
    legacy_task(legacy, "demo")
    state_path = tmp_path / "state.json"
    with loop.locked_state(state_path) as state:
        records = loop.sync_state(state, legacy, catalog)
        records["demo"].update(
            {
                "status": "running",
                "owner": "finished-worker",
                "lease_expires_at": "2999-01-01T00:00:00+00:00",
            }
        )
    args = type(
        "Args",
        (),
        {
            "state": state_path,
            "legacy_root": legacy,
            "catalog_root": catalog,
            "task_id": "demo",
            "owner": "integrator",
            "reason": "worker handoff already completed",
            "artifact": [],
            "takeover": True,
        },
    )()

    assert loop.command_block(args) == 0
    record = json.loads(state_path.read_text(encoding="utf-8"))["tasks"]["demo"]
    assert record["takeover_history"][0]["previous_owner"] == "finished-worker"


def test_parse_manifest_descriptor_returns_digest_and_platform() -> None:
    data = json.dumps(
        {
            "Descriptor": {
                "digest": "sha256:" + "a" * 64,
                "platform": {"os": "linux", "architecture": "amd64"},
            }
        }
    )
    assert loop.parse_manifest_descriptor(data) == (
        "sha256:" + "a" * 64,
        "linux/amd64",
    )
