from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace


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


def test_active_agent_slots_count_controller_concurrency() -> None:
    active = [
        (11, "python run_authoring_loop.py --max-concurrency 8"),
        (12, "python run_authoring_loop.py --max-concurrency=3"),
        (13, "python run_authoring_loop.py"),
    ]

    assert coordinator._active_agent_slots(active) == 12


def test_active_lease_slots_counts_unexpired_running_records(tmp_path: Path) -> None:
    queues = tmp_path / "queues"
    queues.mkdir()
    queues.joinpath("state.json").write_text(
        json.dumps(
            {
                "items": {
                    "live": {
                        "status": "running",
                        "lease_expires_at": "2099-01-01T00:00:00+00:00",
                    },
                    "expired": {
                        "status": "running",
                        "lease_expires_at": "2000-01-01T00:00:00+00:00",
                    },
                    "pending": {"status": "pending"},
                }
            }
        ),
        encoding="utf-8",
    )

    assert coordinator._active_lease_slots(tmp_path) == 1


def test_start_workers_stops_when_docker_disk_is_below_floor(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "repo"
    live = root / ".nl2repo/authoring-live"
    docker_root = tmp_path / "docker"
    root.mkdir()
    docker_root.mkdir()
    gib = 1024**3

    def disk_usage(path: Path):
        free = 100 * gib if Path(path) == root else 19 * gib
        return SimpleNamespace(total=100 * gib, used=100 * gib - free, free=free)

    monkeypatch.setattr(coordinator.shutil, "disk_usage", disk_usage)
    monkeypatch.setattr(
        coordinator,
        "_lane_registry",
        lambda _live: (_ for _ in ()).throw(
            AssertionError("low Docker capacity must stop before queue inspection")
        ),
    )
    args = SimpleNamespace(
        min_free_bytes=12 * gib,
        docker_root=docker_root,
        docker_min_free_bytes=20 * gib,
    )

    capacity = coordinator._worker_disk_capacity(root, args)
    assert capacity["can_start"] is False
    assert capacity["reason"] == "docker-disk-low"
    assert capacity["docker_free_bytes"] == 19 * gib
    assert coordinator._start_workers(root, live, args) == []


def test_worker_disk_capacity_fails_closed_when_docker_root_is_unavailable(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    gib = 1024**3

    def disk_usage(path: Path):
        if Path(path) == root:
            return SimpleNamespace(total=100 * gib, used=0, free=100 * gib)
        raise FileNotFoundError(path)

    monkeypatch.setattr(coordinator.shutil, "disk_usage", disk_usage)
    args = SimpleNamespace(
        min_free_bytes=12 * gib,
        docker_root=tmp_path / "missing-docker",
        docker_min_free_bytes=20 * gib,
    )

    capacity = coordinator._worker_disk_capacity(root, args)
    assert capacity["can_start"] is False
    assert capacity["reason"] == "docker-disk-unavailable"


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


def test_lane_registry_preserves_explicit_repair_flag(tmp_path: Path) -> None:
    live = tmp_path / "live"
    registry = live / "supervisor/generated-lanes.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            [
                {
                    "language": "go",
                    "batch_id": "go-repair",
                    "queue": str(live / "q.json"),
                    "plan": str(live / "p.json"),
                    "queue_state": str(live / "s.json"),
                    "repair_existing": True,
                }
            ]
        ),
        encoding="utf-8",
    )

    lanes = coordinator._lane_registry(live)
    assert len(lanes) == 1
    assert lanes[0].repair_existing is True
