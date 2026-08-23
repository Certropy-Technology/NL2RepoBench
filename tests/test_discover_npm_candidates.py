from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/discover_npm_candidates.py"
    spec = importlib.util.spec_from_file_location("discover_npm_candidates", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


discover = _load_script()


def test_repository_url_normalizes_common_registry_shapes() -> None:
    assert discover._repository_url(
        {"url": "git+https://github.com/a/b.git"}
    ) == "https://github.com/a/b"
    assert discover._repository_url("git@github.com:a/b.git") == "https://github.com/a/b"
