from __future__ import annotations

import json

import pytest

from nl2repobench.legacy.importer import LegacyImporter, LegacyImportError
from nl2repobench.storage.artifacts import FileArtifactStore
from nl2repobench.storage.state import StateStore


def _write_task(root, task_id: str = "demo") -> None:
    task = root / task_id
    task.mkdir(parents=True)
    (task / "start.md").write_text("# Demo\n", encoding="utf-8")
    (task / "test_case_count.txt").write_text("2\n", encoding="utf-8")
    (task / "test_commands.json").write_text(
        json.dumps(["python -m pip install .", "pytest -q"]), encoding="utf-8"
    )
    (task / "test_files.json").write_text(json.dumps(["tests"]), encoding="utf-8")


def test_importer_keeps_private_bytes_out_of_manifest(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    _write_task(legacy)
    difficulty = legacy / "task_difficulty.csv"
    difficulty.write_text("task-name,Level\nDEMO,Easy\n", encoding="utf-8")

    output = tmp_path / "authoring"
    with StateStore(tmp_path / "state.db") as state:
        summary = LegacyImporter(
            legacy,
            output,
            FileArtifactStore(tmp_path / "artifacts"),
            difficulty_file=difficulty,
            state_store=state,
        ).run()

    manifest = json.loads((output / "demo" / "manifest.json").read_text())
    assert summary.imported_tasks == 1
    assert manifest["metadata"]["difficulty"] == "easy"
    assert manifest["tests"]["commands_artifact"]["visibility"] == "private"
    assert "pytest -q" not in (output / "demo" / "manifest.json").read_text()
    report = json.loads((output / "metadata-gap-report.json").read_text())
    assert report["task_count"] == 1
    assert report["complete_task_count"] == 0


def test_importer_is_repeatable(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    _write_task(legacy)
    first_output = tmp_path / "first"
    second_output = tmp_path / "second"
    first = LegacyImporter(legacy, first_output, FileArtifactStore(tmp_path / "artifacts")).run()
    second = LegacyImporter(legacy, second_output, FileArtifactStore(tmp_path / "artifacts")).run()

    assert first.manifest_digests == second.manifest_digests
    assert (first_output / "demo" / "manifest.json").read_bytes() == (
        second_output / "demo" / "manifest.json"
    ).read_bytes()


def test_importer_rejects_symlinked_file_outside_task_root(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    _write_task(legacy)
    outside = tmp_path / "outside.md"
    outside.write_text("private", encoding="utf-8")
    instruction = legacy / "demo/start.md"
    instruction.unlink()
    instruction.symlink_to(outside)

    with pytest.raises(LegacyImportError, match="outside its task root"):
        LegacyImporter(
            legacy,
            tmp_path / "output",
            FileArtifactStore(tmp_path / "artifacts"),
        ).run()


def test_importer_rejects_symlinked_output_directory(tmp_path) -> None:
    legacy = tmp_path / "test_files"
    _write_task(legacy)
    output = tmp_path / "output"
    outside = tmp_path / "outside"
    output.mkdir()
    outside.mkdir()
    (output / "demo").symlink_to(outside, target_is_directory=True)

    with pytest.raises(LegacyImportError, match="must not be a symlink"):
        LegacyImporter(
            legacy,
            output,
            FileArtifactStore(tmp_path / "artifacts"),
        ).run()
