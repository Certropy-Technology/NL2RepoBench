from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load():
    path = Path(__file__).parents[1] / "scripts/authoring_auto_coordinator.py"
    spec = importlib.util.spec_from_file_location("authoring_auto_coordinator_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


coordinator = _load()


def test_candidate_dedup_checks_package_id_revision_license_and_source_digest() -> None:
    history = coordinator.History(
        packages={"known-package"},
        candidate_ids={"known-candidate"},
        identities={"https://github.com/known/repo"},
        revisions={("https://github.com/revision/repo", "a" * 40)},
        licenses={("licensed-package", "https://github.com/license/repo", "MIT")},
        source_digests={"sha256:source"},
    )
    assert coordinator._candidate_duplicate(
        {"package": "known-package", "candidate_id": "new"}, history
    ) == "package-already-in-catalog-or-history"
    assert coordinator._candidate_duplicate(
        {"package": "new", "candidate_id": "known-candidate"}, history
    ) == "candidate-id-already-in-history"
    assert coordinator._candidate_duplicate(
        {
            "package": "new",
            "candidate_id": "new",
            "upstream_url": "https://github.com/known/repo",
        },
        history,
    ) == "upstream-identity-already-in-history"
    assert coordinator._candidate_duplicate(
        {
            "package": "new",
            "candidate_id": "new",
            "upstream_url": "https://github.com/revision/repo",
            "revision": "a" * 40,
        },
        history,
    ) == "revision-already-in-history"
    assert coordinator._candidate_duplicate(
        {
            "package": "licensed-package",
            "candidate_id": "new",
            "upstream_url": "https://github.com/license/repo",
            "license_spdx": "MIT",
        },
        history,
    ) == "license-fingerprint-already-in-history"
    assert coordinator._candidate_duplicate(
        {"package": "new", "candidate_id": "new", "source_digest": "sha256:source"},
        history,
    ) == "source-digest-already-in-history"


def test_select_packages_excludes_all_historical_package_names() -> None:
    pool = {"python": ["a", "b", "c"], "node": [], "go": []}
    history = coordinator.History(packages={"b"})
    assert coordinator._select_packages(pool, "python", history, 8) == ["a", "c"]


def test_active_workers_only_counts_matching_authoring_roots(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    live = root / ".nl2repo/authoring-live"
    good = (
        "python3 /runner/run_authoring_loop.py --state-root "
        ".nl2repo/authoring-live/state --worktree-root .nl2repo/authoring-live/worktrees"
    )
    wrong_state = (
        "python3 /runner/run_authoring_loop.py --state-root /other/state "
        "--worktree-root .nl2repo/authoring-live/worktrees"
    )
    monkeypatch.setattr(
        coordinator,
        "_proc_commands",
        lambda: [(11, good), (12, wrong_state), (13, "python3 other.py")],
    )
    assert coordinator._active_workers(root, live) == [(11, good)]


def test_register_lane_preserves_registry_list(tmp_path: Path) -> None:
    live = tmp_path / "live"
    registry = live / "supervisor/generated-lanes.json"
    registry.parent.mkdir(parents=True)
    registry.write_text("[]\n", encoding="utf-8")
    lane = coordinator.Lane(
        "python",
        "python-author-auto-test",
        live / "supervisor/queues/q.json",
        live / "plans/p.json",
        live / "queues/s.json",
    )
    coordinator._register_lane(live, lane)
    payload = json.loads(registry.read_text(encoding="utf-8"))
    assert payload == [
        {
            "language": "python",
            "batch_id": "python-author-auto-test",
            "queue": str(lane.queue),
            "plan": str(lane.plan),
            "queue_state": str(lane.state),
        }
    ]
