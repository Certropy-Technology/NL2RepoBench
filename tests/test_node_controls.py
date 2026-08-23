from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/prepare_node_controls.py"
    spec = importlib.util.spec_from_file_location("prepare_node_controls", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


controls = _load_script()


def test_prepare_node_controls_isolated_and_executable(tmp_path: Path) -> None:
    bundle = tmp_path / "canonicalize"
    (bundle / "solution").mkdir(parents=True)
    (bundle / "task.toml").write_text("task", encoding="utf-8")
    (bundle / "solution/solve.sh").write_text("old", encoding="utf-8")
    outputs = controls.prepare(bundle, tmp_path / "controls", ("stub", "forgery"))

    assert [path.name for path in outputs] == ["canonicalize-stub", "canonicalize-forgery"]
    assert all((path / "solution/solve.sh").stat().st_mode & 0o111 for path in outputs)
    assert "forged" in (outputs[1] / "solution/solve.sh").read_text(encoding="utf-8")
    assert (bundle / "solution/solve.sh").read_text(encoding="utf-8") == "old"
