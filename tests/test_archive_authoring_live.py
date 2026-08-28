from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts/archive_authoring_live.py"
SPEC = importlib.util.spec_from_file_location("archive_authoring_live", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
archive = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = archive
SPEC.loader.exec_module(archive)


def test_worktrees_with_runs_supports_scoped_packages(tmp_path: Path) -> None:
    state = tmp_path / "state.json"
    state.write_text(
        json.dumps(
            {
                "items": {
                    "one": {"status": "complete", "package": "@scope/package"},
                    "two": {"status": "running", "package": "active"},
                }
            }
        ),
        encoding="utf-8",
    )
    root = tmp_path / "worktrees"
    task = root / "node-batch/@scope/package"
    (task / ".git").mkdir(parents=True)
    (task / ".nl2repo/runs/trial").mkdir(parents=True)
    (task / ".nl2repo/runs/trial/result.json").write_text("{}", encoding="utf-8")
    lane = archive.Lane("node", "node-batch", state)

    assert archive.worktrees_with_runs(lane, root) == [
        ("@scope/package", task, "complete", None, 0)
    ]


def test_archive_files_includes_candidate_workspace_and_scans_secrets(tmp_path: Path) -> None:
    worktree = tmp_path / "task"
    (worktree / ".nl2repo/runs/trial/artifacts/workspace").mkdir(parents=True)
    (worktree / ".nl2repo/runs/trial/verifier").mkdir(parents=True)
    (worktree / ".nl2repo/authoring-handoff.json").write_text("{}", encoding="utf-8")
    (worktree / ".nl2repo/runs/trial/artifacts/workspace/source.js").write_text(
        "export default 1;", encoding="utf-8"
    )
    (worktree / ".nl2repo/runs/trial/verifier/grading.json").write_text(
        '{"valid":true}', encoding="utf-8"
    )

    paths = {file.relative for file in archive.archive_files(worktree)}

    assert ".nl2repo/authoring-handoff.json" in paths
    assert ".nl2repo/runs/trial/verifier/grading.json" in paths
    assert ".nl2repo/runs/trial/artifacts/workspace/source.js" in paths


def test_secret_shaped_workspace_blocks_authoring_archive(tmp_path: Path) -> None:
    worktree = tmp_path / "task"
    workspace = worktree / ".nl2repo/runs/trial/artifacts/workspace"
    workspace.mkdir(parents=True)
    (workspace / "credentials.txt").write_text("AKIA" + "A" * 16, encoding="utf-8")

    with pytest.raises(ValueError, match="secret-shaped"):
        archive.archive_files(worktree)


def test_cleanup_verified_task_preserves_source_evidence_and_cas(tmp_path: Path) -> None:
    worktree = tmp_path / "task"
    removable = (
        worktree / ".nl2repo/runs/trial/result.json",
        worktree / "jobs/trial/result.json",
        worktree / ".venv/file",
        worktree / ".nl2repo/compiled-task/file",
    )
    retained = (
        worktree / "catalog/sources/task/task.toml",
        worktree / ".nl2repo/evidence/proof.json",
        worktree / ".nl2repo/artifacts/private/sha256/aa/aabb",
        worktree / ".nl2repo/authoring-handoff.json",
    )
    for path in (*removable, *retained):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("payload", encoding="utf-8")

    removed = archive.cleanup_verified_task(worktree)

    assert removed == sum(len("payload") for _ in removable)
    assert all(not path.exists() for path in removable)
    assert all(path.is_file() for path in retained)


def test_archive_files_includes_harbor_runs_under_authoring_work(tmp_path: Path) -> None:
    worktree = tmp_path / "task"
    run = worktree / ".nl2repo/authoring-work/task/runs/trial/artifacts/workspace"
    run.mkdir(parents=True)
    (run / "src.py").write_text("print(1)", encoding="utf-8")

    files = archive.archive_files(worktree)

    assert any(
        file.relative.endswith("artifacts/workspace/src.py") for file in files
    )
    assert not any(
        file.relative.endswith("authoring-work/task/source/package.py") for file in files
    )


def test_cleanup_orphan_containers_removes_only_non_running_tasks(
    tmp_path: Path, monkeypatch
) -> None:
    state = tmp_path / "state.json"
    state.write_text(
        json.dumps(
            {
                "items": {
                    "one": {"status": "pending", "package": "idle"},
                    "two": {"status": "running", "package": "active"},
                }
            }
        ),
        encoding="utf-8",
    )
    root = tmp_path / "worktrees"
    idle = (root / "python-batch/idle").resolve()
    active = (root / "python-batch/active").resolve()
    idle.mkdir(parents=True)
    active.mkdir(parents=True)
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        if command[:3] == ["docker", "ps", "-q"]:
            return type("Result", (), {"returncode": 0, "stdout": "idle-id\nactive-id\n"})()
        if command[:2] == ["docker", "inspect"]:
            return type(
                "Result",
                (),
                {
                    "returncode": 0,
                    "stdout": json.dumps(
                        [
                            {"Id": "idle-id", "Config": {"Labels": {"cwd": str(idle)}}},
                            {"Id": "active-id", "Config": {"Labels": {"cwd": str(active)}}},
                        ]
                    ),
                },
            )()
        return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(archive.subprocess, "run", fake_run)
    monkeypatch.setattr(archive, "_process_uses", lambda _path: False)

    removed = archive.cleanup_orphan_containers(
        [archive.Lane("python", "python-batch", state)], root
    )

    assert removed == ["idle-id"]
    assert ["docker", "rm", "-f", "idle-id"] in calls
