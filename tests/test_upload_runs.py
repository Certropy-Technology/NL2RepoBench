from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.modules.setdefault("oss2", types.ModuleType("oss2"))
SPEC = importlib.util.spec_from_file_location(
    "upload_runs_to_oss", ROOT / "scripts/upload_runs_to_oss.py"
)
assert SPEC and SPEC.loader
uploader = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = uploader
SPEC.loader.exec_module(uploader)


def test_prefixed_timestamped_run_keeps_canonical_task_id(tmp_path: Path) -> None:
    run_root = tmp_path / "batch-fable-boto-retry"
    path = (
        run_root
        / "fable-boto-retry-20260821T063037Z"
        / "2026-08-21__14-30-39"
        / "harbor__abc"
        / "verifier"
        / "grading.json"
    )
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")

    model, task, relative = uploader.classify(run_root, path)

    assert model == "claude-fable-5"
    assert task == "boto"
    assert relative.startswith("batch-fable-boto-retry--2026-08-21__14-30-39/")


def test_longest_task_prefix_wins_for_hyphenated_task() -> None:
    original = uploader.TASKS
    uploader.TASKS = frozenset({"python", "python-pathspec"})
    try:
        assert (
            uploader.task_from_prefixed_run(
                "gpt56-python-pathspec-retry-20260821T010203Z", "gpt56-"
            )
            == "python-pathspec"
        )
    finally:
        uploader.TASKS = original
