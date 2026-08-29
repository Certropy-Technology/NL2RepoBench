from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/build_package_queue.py"
    spec = importlib.util.spec_from_file_location("build_package_queue", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


queue_builder = _load_script()


def _report(path: Path, *, package: str = "demo", revision: str | None = "a" * 40) -> None:
    path.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "package": package,
                        "repository": f"owner/{package}",
                        "revision": revision,
                        "license_spdx": "MIT",
                        "stars_at_discovery": 150,
                        "last_update_at_discovery": "2026-08-20",
                        "category": "utility",
                        "risks": ["local-only"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_queue_deduplicates_reports_and_marks_existing_tasks(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    (catalog / "existing").mkdir(parents=True)
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _report(first)
    _report(second)
    payload = json.loads(first.read_text(encoding="utf-8"))
    payload["candidates"][0]["package"] = "existing"
    payload["candidates"][0]["repository"] = "owner/existing"
    second.write_text(json.dumps(payload), encoding="utf-8")

    result = queue_builder.build_queue(
        [first, second], catalog_root=catalog, observed_at="2026-08-23T00:00:00+00:00"
    )

    assert result["counts"] == {"candidate": 1, "existing": 1}
    demo = next(item for item in result["queue"] if item["package"] == "demo")
    assert len(demo["selection_sources"]) == 1


def test_queue_keeps_missing_revision_as_needs_evidence(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    report = tmp_path / "report.json"
    _report(report, revision=None)

    result = queue_builder.build_queue(
        [report], catalog_root=catalog, observed_at="2026-08-23T00:00:00+00:00"
    )

    assert result["counts"] == {"needs-evidence": 1}


def test_queue_rejects_stale_candidate_with_complete_evidence(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    report = tmp_path / "report.json"
    _report(report)
    payload = json.loads(report.read_text(encoding="utf-8"))
    payload["candidates"][0]["last_update_at_discovery"] = "2020-01-01"
    report.write_text(json.dumps(payload), encoding="utf-8")

    result = queue_builder.build_queue(
        [report], catalog_root=catalog, observed_at="2026-08-23T00:00:00+00:00"
    )

    assert result["counts"] == {"rejected": 1}


def test_queue_is_order_independent_and_preserves_github_language(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "package": "node-demo",
                        "repository": "owner/node-demo",
                        "language": "node",
                        "source_kind": "github",
                        "revision": "a" * 40,
                        "license_spdx": "MIT",
                        "stars": 150,
                        "last_activity": "2026-08-20",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    second.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "package": "node-demo",
                        "repository": "owner/node-demo",
                        "language": "node",
                        "source_kind": "github",
                        "revision": "b" * 40,
                        "license_spdx": "MIT",
                        "stars": 150,
                        "last_activity": "2026-08-20",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    left = queue_builder.build_queue(
        [first, second], catalog_root=catalog, observed_at="2026-08-23T00:00:00Z"
    )
    right = queue_builder.build_queue(
        [second, first], catalog_root=catalog, observed_at="2026-08-23T00:00:00Z"
    )

    assert left == right
    assert left["queue"][0]["language"] == "node"
    assert left["queue"][0]["status"] == "needs-evidence"
    assert left["queue"][0]["conflicts"] == ["revision"]


def test_queue_accepts_frozen_go_candidate(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    report = tmp_path / "go.json"
    report.write_text(
        json.dumps(
            {
                "language": "go",
                "source_kind": "go-modules",
                "candidates": [
                    {
                        "package": "go-demo",
                        "repository": "owner/go-demo",
                        "language": "go",
                        "source_kind": "go-modules",
                        "revision": "a" * 40,
                        "license_spdx": "MIT",
                        "stars": 150,
                        "last_activity": "2026-08-20",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = queue_builder.build_queue(
        [report], catalog_root=catalog, observed_at="2026-08-23T00:00:00Z"
    )

    assert result["counts"] == {"candidate": 1}
    assert result["queue"][0]["language"] == "go"
