from __future__ import annotations

import importlib.util
import json
import sys
from contextlib import redirect_stdout
from io import StringIO
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


def _load_loop():
    path = Path(__file__).parents[1] / "scripts/package_queue_loop.py"
    spec = importlib.util.spec_from_file_location("package_queue_loop_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


queue_loop = _load_loop()


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


def test_claim_skips_candidate_owned_by_another_state_file(tmp_path: Path) -> None:
    queue = tmp_path / "queue.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {
                        "candidate_id": "same-candidate",
                        "package": "same-package",
                        "language": "python",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    first_state = tmp_path / "queues" / "first.json"
    second_state = tmp_path / "queues" / "second.json"
    for state in (first_state, second_state):
        with redirect_stdout(StringIO()):
            queue_loop.command_init(type("Args", (), {"queue": queue, "state": state})())

    first_output = StringIO()
    with redirect_stdout(first_output):
        assert (
            queue_loop.command_claim(
                type(
                    "Args",
                    (),
                    {
                        "queue": queue,
                        "state": first_state,
                        "owner": "first",
                        "limit": 1,
                        "lease_seconds": 60,
                        "max_attempts": 3,
                        "language": "python",
                        "candidate_id": None,
                    },
                )()
            )
            == 0
        )
    assert json.loads(first_output.getvalue())["claimed"][0]["candidate_id"] == "same-candidate"

    second_output = StringIO()
    with redirect_stdout(second_output):
        assert (
            queue_loop.command_claim(
                type(
                    "Args",
                    (),
                    {
                        "queue": queue,
                        "state": second_state,
                        "owner": "second",
                        "limit": 1,
                        "lease_seconds": 60,
                        "max_attempts": 3,
                        "language": "python",
                        "candidate_id": None,
                    },
                )()
            )
            == 2
        )
    assert json.loads(second_output.getvalue())["claimed"] == []


def test_release_marks_exhausted_attempt_as_blocked(tmp_path: Path) -> None:
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {"candidate_id": "candidate", "package": "pkg", "language": "go"}
                ]
            }
        ),
        encoding="utf-8",
    )
    with redirect_stdout(StringIO()):
        queue_loop.command_init(type("Args", (), {"queue": queue, "state": state})())
        queue_loop.command_claim(
            type(
                "Args",
                (),
                {
                    "queue": queue,
                    "state": state,
                    "owner": "worker",
                    "limit": 1,
                    "lease_seconds": 60,
                    "max_attempts": 1,
                    "language": "go",
                    "candidate_id": None,
                },
            )()
        )
        queue_loop.command_release(
            type(
                "Args",
                (),
                {
                    "queue": queue,
                    "state": state,
                    "owner": "worker",
                    "candidate_id": "candidate",
                    "reason": "bounded authoring failure",
                    "max_attempts": 1,
                    "failure_class": "model",
                },
            )()
        )
    payload = json.loads(state.read_text(encoding="utf-8"))
    record = payload["items"]["candidate"]
    assert record["status"] == "retry-exhausted"
    assert record["failure_class"] == "model"


def test_release_can_refund_attempt_for_pre_agent_infrastructure_failure(
    tmp_path: Path,
) -> None:
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {
                        "candidate_id": "candidate",
                        "package": "pkg",
                        "language": "python",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with redirect_stdout(StringIO()):
        queue_loop.command_init(type("Args", (), {"queue": queue, "state": state})())
        queue_loop.command_claim(
            type(
                "Args",
                (),
                {
                    "queue": queue,
                    "state": state,
                    "owner": "worker",
                    "limit": 1,
                    "lease_seconds": 60,
                    "max_attempts": 3,
                    "language": "python",
                    "candidate_id": None,
                },
            )()
        )
        queue_loop.command_release(
            type(
                "Args",
                (),
                {
                    "queue": queue,
                    "state": state,
                    "owner": "worker",
                    "candidate_id": "candidate",
                    "reason": "worktree setup failed before Pi launch",
                    "max_attempts": 3,
                    "failure_class": "infrastructure",
                    "refund_attempt": True,
                },
            )()
        )
    record = json.loads(state.read_text(encoding="utf-8"))["items"]["candidate"]
    assert record["status"] == "pending"
    assert record["attempts"] == 0
    assert record["failure_class"] == "infrastructure"
