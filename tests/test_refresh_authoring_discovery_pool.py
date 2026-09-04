from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load():
    path = Path(__file__).parents[1] / "scripts/refresh_authoring_discovery_pool.py"
    spec = importlib.util.spec_from_file_location("refresh_authoring_pool_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


refresh = _load()


def test_merge_pool_preserves_seed_and_adds_runtime_candidates() -> None:
    result = refresh.merge_pool(
        {
            "python": ["seed-python"],
            "node": ["seed-node"],
            "go": ["go-seed"],
            "go_repositories": {"go-seed": "owner/seed"},
        },
        {"python": ["old-python"], "node": [], "go": []},
        {
            "python": ["new-python", "../unsafe"],
            "node": ["@scope/new-node"],
            "go": ["go-new"],
        },
        {"go-new": "owner/new", "go-seed": "other/collision"},
        max_per_language=20,
    )

    assert result["python"] == ["new-python", "old-python", "seed-python"]
    assert result["node"] == ["@scope/new-node", "seed-node"]
    assert result["go"] == ["go-new", "go-seed"]
    assert result["go_repositories"] == {
        "go-new": "owner/new",
        "go-seed": "owner/seed",
    }


def test_go_package_disambiguates_repository_names() -> None:
    used = {"go-cache"}
    assert refresh._go_package("owner/cache", used) == "go-owner-cache"
    assert refresh._go_package("owner/!!!", used) is None
