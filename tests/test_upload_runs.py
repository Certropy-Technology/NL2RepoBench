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


def test_historical_new6_marker_does_not_change_task_identity() -> None:
    original = uploader.TASKS
    uploader.TASKS = frozenset({"markupsafe"})
    try:
        assert (
            uploader.task_from_prefixed_run("gpt56-new6-markupsafe", "gpt56-")
            == "markupsafe"
        )
    finally:
        uploader.TASKS = original


def test_historical_new6_job_path_is_classified_to_canonical_task(tmp_path: Path) -> None:
    original = uploader.TASKS
    uploader.TASKS = frozenset({"markupsafe"})
    try:
        run_root = tmp_path / "batch-fable-new6-20260821T"
        path = (
            run_root
            / "fable-new6-markupsafe"
            / "2026-08-21__18-53-58"
            / "harbor__abc"
            / "verifier"
            / "grading.json"
        )
        path.parent.mkdir(parents=True)
        path.write_text("{}", encoding="utf-8")

        model, task, _ = uploader.classify(run_root, path)

        assert model == "claude-fable-5"
        assert task == "markupsafe"
    finally:
        uploader.TASKS = original


def test_queue_log_is_archived_as_a_queue_log(tmp_path: Path) -> None:
    run_root = tmp_path / "batch-gpt-resume-20260822T000000Z"
    run_root.mkdir(parents=True)
    queue = run_root / "queue.log"
    queue.write_text("queue", encoding="utf-8")

    items = list(uploader.iter_run_uploads(tmp_path))

    assert len(items) == 1
    assert items[0].key == (
        "nl2repobench/runs/_queue-logs/"
        "batch-gpt-resume-20260822T000000Z--queue.log"
    )


def test_manifest_contains_sha256_for_each_object(tmp_path: Path) -> None:
    run_root = tmp_path / "batch-gpt-resume-20260822T000000Z"
    file_path = run_root / "gpt56-markupsafe" / "trial.log"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("payload", encoding="utf-8")
    manifest = tmp_path / "manifest.json"

    uploader.write_manifest(list(uploader.iter_run_uploads(tmp_path)), manifest)

    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["objects"][0]["sha256"] == __import__("hashlib").sha256(
        b"payload"
    ).hexdigest()
