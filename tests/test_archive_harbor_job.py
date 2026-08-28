from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts/archive_harbor_job.py"
SPEC = importlib.util.spec_from_file_location("archive_harbor_job", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
archive = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = archive
SPEC.loader.exec_module(archive)


class FakeResponse:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.done = False

    def read(self, _size: int = -1) -> bytes:
        if self.done:
            return b""
        self.done = True
        return self.data


class FakeBucket:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def object_exists(self, key: str) -> bool:
        return key in self.objects

    def put_object_from_file(self, key: str, path: str, headers: dict[str, str]) -> None:
        assert headers["x-oss-meta-sha256"]
        self.objects[key] = Path(path).read_bytes()

    def get_object(self, key: str) -> FakeResponse:
        return FakeResponse(self.objects[key])


def test_archive_includes_workspace_and_cleans_after_remote_verification(tmp_path: Path) -> None:
    job = tmp_path / "job"
    workspace = job / "artifacts/workspace"
    verifier = job / "verifier"
    workspace.mkdir(parents=True)
    verifier.mkdir()
    (workspace / "package.json").write_text("{}", encoding="utf-8")
    (workspace / "src.js").write_text("export default 1;", encoding="utf-8")
    (verifier / "grading.json").write_text('{"valid":true}', encoding="utf-8")
    bucket = FakeBucket()
    receipt = tmp_path / "receipt.json"

    result = archive.archive_job(
        job,
        model="openai/gpt-5.6-luna",
        task_id="demo",
        run_id="run-1",
        bucket=bucket,
        receipt_path=receipt,
        cleanup_local=True,
    )

    assert result["workspace_included"] is True
    assert result["workspace_file_count"] == 2
    assert result["cleanup_local_completed"] is True
    assert not job.exists()
    manifest_key = str(result["remote_manifest_key"])
    manifest = json.loads(bucket.objects[manifest_key])
    assert manifest["workspace_file_count"] == 2
    assert any(key.endswith("artifacts/workspace/src.js") for key in bucket.objects)
    assert receipt.is_file()
    assert not list(tmp_path.glob(".*.oss-manifest.json"))


def test_archive_rejects_unsafe_prefix(tmp_path: Path) -> None:
    job = tmp_path / "job"
    job.mkdir()
    (job / "result.json").write_text("{}", encoding="utf-8")

    with pytest.raises(archive.ArchiveError, match="prefix"):
        archive.archive_job(
            job,
            model="model",
            task_id="demo",
            run_id="run-1",
            prefix="nl2repobench/../escape",
            bucket=FakeBucket(),
        )


def test_secret_shaped_workspace_is_retained_and_not_uploaded(tmp_path: Path) -> None:
    job = tmp_path / "job"
    workspace = job / "artifacts/workspace"
    workspace.mkdir(parents=True)
    (workspace / "credentials.txt").write_text("sk-" + "a" * 48, encoding="utf-8")
    bucket = FakeBucket()

    try:
        archive.archive_job(
            job,
            model="model",
            task_id="demo",
            run_id="run-1",
            bucket=bucket,
        )
    except archive.ArchiveError as exc:
        assert "secret-shaped" in str(exc)
    else:
        raise AssertionError("secret-shaped workspace should block archive")
    assert job.exists()
    assert bucket.objects == {}


def test_archive_manifest_does_not_leave_local_temp_file(tmp_path: Path) -> None:
    job = tmp_path / "job"
    job.mkdir()
    (job / "result.json").write_text("{}", encoding="utf-8")

    archive.archive_job(
        job,
        model="model",
        task_id="demo",
        run_id="run/with-slash",
        bucket=FakeBucket(),
    )

    assert not list(tmp_path.glob(".*.oss-manifest.json"))
