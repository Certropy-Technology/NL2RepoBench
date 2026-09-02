from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path
from typing import cast

import pytest
import tomli_w

SCRIPT = Path(__file__).parents[1] / "scripts/plan_private_release_batch.py"
SPEC = importlib.util.spec_from_file_location("plan_private_release_batch", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _tar(files: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.mode = 0o644
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _write_cas(root: Path, data: bytes) -> tuple[str, int]:
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    target = root / digest[7:9] / digest[7:]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return digest, len(data)


def _source(
    root: Path,
    cas: Path,
    *,
    task_id: str = "demo",
    command_media: str = "application/json",
) -> None:
    command = (
        json.dumps(
            {
                "schema_version": "1.0",
                "identity": "node+npm",
                "runner": "node-test-subprocess-boundary-v1",
                "candidate_install": "npm-pack-offline-v1",
                "report_format": "node-test-json-v1",
                "test_root": "/tests/private",
                "steps": [],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        + b"\n"
    )
    command_data = (
        command if command_media == "application/json" else _tar({"command-plan.json": command})
    )
    test_data = _tar({"contract.test.mjs": b"test"})
    oracle_data = _tar({"solve.sh": b"#!/bin/sh\n"})
    command_digest, command_size = _write_cas(cas, command_data)
    test_digest, test_size = _write_cas(cas, test_data)
    oracle_digest, oracle_size = _write_cas(cas, oracle_data)

    def ref(digest: str, size: int, media: str) -> dict[str, object]:
        return {
            "digest": digest,
            "size_bytes": size,
            "media_type": media,
            "uri": f"artifact://private/{digest}",
            "visibility": "private",
        }

    payload = {
        "schema_version": "1.0",
        "task_id": task_id,
        "version": "1.0.0",
        "instruction": "instruction.md",
        "metadata": {
            "difficulty": "easy",
            "category": "demo",
            "tags": ["node", "npm"],
            "language": "node",
        },
        "source": {
            "status": "known",
            "upstream_url": "https://example.invalid/demo",
            "revision": "a" * 40,
            "license_spdx": "MIT",
            "source_digest": "sha256:" + "b" * 64,
        },
        "environment": {
            "status": "known",
            "os_name": "debian-bookworm",
            "base_image": "node@sha256:" + "c" * 64,
            "base_image_digest": "sha256:" + "c" * 64,
            "network_policy": {
                "mode": "no-network",
                "offline_dependencies": "preinstalled-image",
                "reference_source_fetch": "forbidden",
                "reason": "test",
            },
            "runtime": {
                "language": "node",
                "runtime": "node",
                "version": "24.19.0",
                "package_manager": "npm",
                "package_manager_version": "11.17.0",
            },
        },
        "dependencies": {"status": "unknown", "package_manager": "npm", "packages": []},
        "tests": {
            "framework": "node:test",
            "report_format": "node-test-json-v1",
            "expected_total": 1,
            "expected_total_source": "frozen-collection",
            "commands_artifact": ref(command_digest, command_size, command_media),
            "test_bundle": ref(
                test_digest,
                test_size,
                "application/vnd.nl2repobench.node-tests+tar",
            ),
        },
        "lifecycle": {"status": "blocked", "reason": "planner test"},
        "oracle_bundle": ref(oracle_digest, oracle_size, "application/vnd.nl2repobench.oracle+tar"),
    }
    task = root / task_id
    task.mkdir(parents=True)
    (task / "task.toml").write_text(tomli_w.dumps(payload), encoding="utf-8")
    (task / "instruction.md").write_text("Build demo.\n", encoding="utf-8")


def test_planner_classifies_available_legacy_json_without_claims(tmp_path: Path) -> None:
    sources = tmp_path / "sources"
    cas = tmp_path / "cas"
    sources.mkdir()
    cas.mkdir()
    _source(sources, cas)
    result = MODULE.plan_private_release_batch(sources, cas)
    tasks = cast(list[dict[str, object]], result["tasks"])
    task = tasks[0]
    assert task["classification"] == "ready-for-staging"
    assert task["command_artifact_shape"] == "legacy-json"
    assert task["staging"] == {
        "allowed": True,
        "preparer": "scripts/prepare_private_release.py",
        "source_update": False,
        "oracle": False,
        "controls": False,
    }
    assert result["claims"] == {
        "source_updates": False,
        "oracle": False,
        "controls": False,
        "publication": False,
    }
    assert all("contract.test.mjs" not in json.dumps(row) for row in tasks)


def test_planner_classifies_legacy_command_archive(tmp_path: Path) -> None:
    sources = tmp_path / "sources"
    cas = tmp_path / "cas"
    sources.mkdir()
    cas.mkdir()
    _source(sources, cas, command_media="application/vnd.nl2repobench.node-commands+tar")
    result = MODULE.plan_private_release_batch(sources, cas)
    tasks = cast(list[dict[str, object]], result["tasks"])
    task = tasks[0]
    assert task["command_artifact_shape"] == "legacy-archive-command-plan"


def test_planner_reports_missing_cas_and_is_deterministic(tmp_path: Path) -> None:
    sources = tmp_path / "sources"
    cas = tmp_path / "cas"
    sources.mkdir()
    cas.mkdir()
    _source(sources, cas)
    ref = next(path for path in cas.rglob("*") if path.is_file())
    ref.unlink()
    first = MODULE.plan_private_release_batch(sources, cas)
    second = MODULE.plan_private_release_batch(sources, cas)
    assert first == second
    tasks = cast(list[dict[str, object]], first["tasks"])
    task = tasks[0]
    assert task["classification"] == "blocked"
    blockers = cast(list[str], task["blockers"])
    assert any("unavailable" in item for item in blockers)


def test_planner_rejects_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "queue.json"
    output.write_text("keep", encoding="utf-8")
    with pytest.raises(MODULE.BatchPlanningError, match="already exists"):
        MODULE._write_output(output, {"schema_version": "1.0"})


def test_planner_enumerates_scoped_source_leaves(tmp_path: Path) -> None:
    sources = tmp_path / "sources"
    cas = tmp_path / "cas"
    sources.mkdir()
    cas.mkdir()
    _source(sources, cas, task_id="@scope/demo")
    result = MODULE.plan_private_release_batch(sources, cas)
    tasks = cast(list[dict[str, object]], result["tasks"])
    assert [task["task_id"] for task in tasks] == ["@scope/demo"]
    assert result["queue"] == ["@scope/demo"]
