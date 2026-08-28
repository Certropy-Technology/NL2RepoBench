from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts/archive_authoring_live.py"
SPEC = importlib.util.spec_from_file_location("archive_authoring_live", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
archive = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = archive
SPEC.loader.exec_module(archive)


def test_complete_worktrees_supports_scoped_packages(tmp_path: Path) -> None:
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
    lane = archive.Lane("node", "node-batch", state)

    assert archive.complete_worktrees(lane, root) == [("@scope/package", task)]


def test_archive_files_excludes_candidate_workspace(tmp_path: Path) -> None:
    worktree = tmp_path / "task"
    (worktree / ".nl2repo/runs/trial/artifacts/workspace").mkdir(parents=True)
    (worktree / ".nl2repo/runs/trial/verifier").mkdir(parents=True)
    (worktree / ".nl2repo/authoring-handoff.json").write_text("{}", encoding="utf-8")
    (worktree / ".nl2repo/runs/trial/artifacts/workspace/secret.txt").write_text(
        "AKIAABCDEFGHIJKLMNOP", encoding="utf-8"
    )
    (worktree / ".nl2repo/runs/trial/verifier/grading.json").write_text(
        '{"valid":true}', encoding="utf-8"
    )

    paths = {file.relative for file in archive.archive_files(worktree)}

    assert ".nl2repo/authoring-handoff.json" in paths
    assert ".nl2repo/runs/trial/verifier/grading.json" in paths
    assert not any("artifacts/workspace" in path for path in paths)


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
