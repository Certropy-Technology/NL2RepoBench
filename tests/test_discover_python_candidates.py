from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/discover_python_candidates.py"
    spec = importlib.util.spec_from_file_location("discover_python_candidates", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


discover = _load_script()


def test_repository_url_normalizes_source_url() -> None:
    assert discover._repo_url(
        {"url": "git+https://github.com/example/pkg.git"}
    ) == "https://github.com/example/pkg"


def test_repository_scans_common_project_url_labels() -> None:
    assert discover._repository(
        {
            "project_urls": {
                "Documentation": "https://example.invalid/docs",
                "Source Code": "https://github.com/example/pkg/tree/main",
            }
        }
    ) == "https://github.com/example/pkg"


def test_repository_ignores_non_github_homepage() -> None:
    assert discover._repository({"home_page": "https://example.invalid"}) is None
