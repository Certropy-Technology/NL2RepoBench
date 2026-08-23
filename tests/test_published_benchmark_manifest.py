from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parents[1] / "scripts/build_published_benchmark_manifest.py"
_SPEC = importlib.util.spec_from_file_location("published_manifest_script", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build_manifest = _MODULE.build_manifest
write_outputs = _MODULE.write_outputs


def _published_task(root: Path, task_id: str) -> None:
    task = root / task_id
    harbor = task / "harbor"
    (harbor / "solution").mkdir(parents=True)
    (harbor / "tests").mkdir()
    (harbor / "environment").mkdir()
    (task / "task.toml").write_text(
        """schema_version = "1.0"
version = "1.0.0"
[metadata]
language = "python"
category = "utility"
difficulty = "easy"
[lifecycle]
status = "published"
""",
        encoding="utf-8",
    )
    (harbor / "task.toml").write_text('schema_version = "1.4"\n', encoding="utf-8")
    (harbor / "instruction.md").write_text("instruction\n", encoding="utf-8")


def test_manifest_fails_closed_below_300(tmp_path: Path) -> None:
    _published_task(tmp_path, "one")
    with pytest.raises(ValueError, match="below required minimum 300"):
        build_manifest(
            tmp_path,
            dataset_id="test",
            dataset_release="1.0.0",
            minimum_tasks=300,
            allow_below_target=False,
        )


def test_diagnostic_manifest_is_deterministic_and_writes_parquet(tmp_path: Path) -> None:
    _published_task(tmp_path, "one")
    manifest = build_manifest(
        tmp_path,
        dataset_id="test",
        dataset_release="1.0.0",
        minimum_tasks=300,
        allow_below_target=True,
    )
    output = tmp_path / "manifest.json"
    parquet = tmp_path / "manifest.parquet"
    write_outputs(manifest, output, parquet)
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "below-target"
    assert parquet.is_file()
