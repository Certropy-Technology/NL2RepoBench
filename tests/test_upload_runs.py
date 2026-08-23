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


def test_task_upload_skips_internal_agent_directories(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog" / "tasks"
    task = catalog / "demo"
    (task / "harbor").mkdir(parents=True)
    (task / "task.toml").write_text("task", encoding="utf-8")
    (task / ".pi-glla").mkdir()
    (task / ".pi-glla" / "session.json").write_text("secret-free", encoding="utf-8")
    (catalog / ".pi-glla").mkdir(parents=True)
    (catalog / ".pi-glla" / "owner.json").write_text("internal", encoding="utf-8")

    items = list(uploader.iter_task_uploads(catalog))

    assert [item.key for item in items] == ["nl2repobench/harbor-tasks/demo/task.toml"]


def test_task_upload_rejects_symlink_files(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog" / "tasks"
    task = catalog / "demo"
    task.mkdir(parents=True)
    (task / "task.toml").write_text("task", encoding="utf-8")
    outside = tmp_path / "outside-secret"
    outside.write_text("sk-abcdefghijklmnopqrstuvwxyz", encoding="utf-8")
    (task / "linked.log").symlink_to(outside)

    items = list(uploader.iter_task_uploads(catalog))

    assert [item.local.name for item in items] == ["task.toml"]


def test_secret_scan_requires_high_confidence_key_shape(tmp_path: Path) -> None:
    public_text = tmp_path / "public.txt"
    public_text.write_text("dask-@trio and mask-id", encoding="utf-8")
    secret_text = tmp_path / "secret.txt"
    secret_text.write_text("sk-" + "a" * 48, encoding="utf-8")
    items = [
        uploader.Upload(public_text, "nl2repobench/runs/public", public_text.stat().st_size),
        uploader.Upload(secret_text, "nl2repobench/runs/secret", secret_text.stat().st_size),
    ]

    findings = uploader.secret_shaped_paths(items)

    assert findings == [str(secret_text)]


def test_run_upload_skips_hidden_control_files(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    run_root = runs / "batch"
    (run_root / "gpt56-demo").mkdir(parents=True)
    (run_root / "gpt56-demo" / "result.json").write_text("{}", encoding="utf-8")
    (run_root / ".pi-glla").mkdir()
    (run_root / ".pi-glla" / "owner.json").write_text("internal", encoding="utf-8")

    items = list(uploader.iter_run_uploads(runs))

    assert len(items) == 1
    assert items[0].key == "nl2repobench/runs/gpt-5.6-sol/demo/batch--result.json"


class _Head:
    def __init__(self, size: int, digest: str) -> None:
        self.content_length = size
        self.headers = {"x-oss-meta-sha256": digest}


class _ExistingObjectBucket:
    def __init__(self, size: int, digest: str) -> None:
        self.head = _Head(size, digest)
        self.put_called = False

    def object_exists(self, key: str) -> bool:
        del key
        return True

    def head_object(self, key: str) -> _Head:
        del key
        return self.head

    def put_object_from_file(self, *args, **kwargs) -> None:
        del args, kwargs
        self.put_called = True


def test_existing_oss_object_skips_only_when_size_and_digest_match(tmp_path: Path) -> None:
    path = tmp_path / "payload"
    path.write_bytes(b"payload")
    item = uploader.Upload(path, "nl2repobench/runs/demo/payload", path.stat().st_size)
    bucket = _ExistingObjectBucket(item.size, item.sha256)

    assert uploader.upload_one(bucket, item, overwrite=False) == "skipped"
    assert bucket.put_called is False


def test_existing_oss_object_collision_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "payload"
    path.write_bytes(b"payload")
    item = uploader.Upload(path, "nl2repobench/runs/demo/payload", path.stat().st_size)
    bucket = _ExistingObjectBucket(item.size, "0" * 64)

    import pytest

    with pytest.raises(RuntimeError, match="collision"):
        uploader.upload_one(bucket, item, overwrite=False)
