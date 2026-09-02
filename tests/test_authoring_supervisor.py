from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from nl2repobench.authoring.scheduler import STATUS_SCHEMA_VERSION, Scheduler


def _load():
    path = Path(__file__).parents[1] / "scripts/authoring_supervisor.py"
    spec = importlib.util.spec_from_file_location("authoring_supervisor", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


supervisor = _load()


def test_source_path_accepts_scoped_package_and_rejects_escape(tmp_path: Path) -> None:
    root = tmp_path / "worktree"
    (root / "catalog/sources/@scope/package").mkdir(parents=True)

    assert supervisor._source_path(root, "@scope/package").is_dir()
    with pytest.raises(ValueError, match="unsafe package"):
        supervisor._source_path(root, "../outside")


def test_copy_if_new_scans_secrets_and_refuses_collisions(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    (source / "task.toml").write_text("task_id = 'demo'", encoding="utf-8")

    assert supervisor._copy_if_new(source, target) is True
    assert (target / "task.toml").read_text(encoding="utf-8") == "task_id = 'demo'"
    assert supervisor._copy_if_new(source, target) is False

    (source / "secret.txt").write_text("sk-" + "a" * 48, encoding="utf-8")
    with pytest.raises(ValueError, match="secret-shaped"):
        supervisor._copy_if_new(source, tmp_path / "secret-target")


def test_sync_private_cas_copies_only_referenced_verified_objects(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = tmp_path / "worktree"
    source = worktree / "catalog/sources/demo"
    source.mkdir(parents=True)
    payload = b"private bundle"
    import hashlib

    digest = hashlib.sha256(payload).hexdigest()
    (source / "task.toml").write_text(
        f"bundle = {{ digest = 'sha256:{digest}' }}\n",
        encoding="utf-8",
    )
    artifact = worktree / ".nl2repo/artifacts/private/sha256" / digest[:2] / digest
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(payload)
    (worktree / ".nl2repo/artifacts/private/sha256/ff/unreferenced").parent.mkdir(
        parents=True
    )
    (worktree / ".nl2repo/artifacts/private/sha256/ff/unreferenced").write_bytes(
        b"unused"
    )

    copied = supervisor._sync_private_cas(root, worktree, source)

    assert copied == [f"sha256:{digest}"]
    central_artifact = root / ".nl2repo/artifacts/private/sha256" / digest[:2] / digest
    assert central_artifact.read_bytes() == payload
    assert not (root / ".nl2repo/artifacts/private/sha256/ff/unreferenced").exists()


def _integration_checkout(
    tmp_path: Path, monkeypatch, status_output: str = ""
) -> tuple[Callable[[], dict[str, Any]], list[str]]:
    """Build a fake integration checkout reporting `status_output` from git status.

    Returns the integration callable and the ordered list of git events it emits, so
    a caller can assert how far execution got. Only git plumbing is faked.
    """
    root = tmp_path / "repo"
    worktree = root / ".nl2repo/authoring-live/worktrees/batch/demo"
    source = worktree / "catalog/sources/demo"
    source.mkdir(parents=True)
    (source / "task.toml").write_text("task_id = 'demo'", encoding="utf-8")
    (source / "instruction.md").write_text("# Demo\n", encoding="utf-8")
    (source / "production-evidence.json").write_text("{}", encoding="utf-8")
    (worktree / ".nl2repo").mkdir(parents=True)
    (worktree / ".nl2repo/authoring-handoff.json").write_text("{}", encoding="utf-8")
    compiled = tmp_path / "compiled/demo"
    compiled.mkdir(parents=True)
    (compiled / "task.toml").write_text("task_id = 'demo'", encoding="utf-8")
    events: list[str] = []

    def fake_run(command, *, cwd, timeout):
        del cwd, timeout
        if command[:3] == ["git", "status", "--porcelain=v1"]:
            events.append("status")
            return {"command": command, "exit_code": 0, "output": status_output, "timeout": False}
        if command[:2] == ["git", "add"]:
            events.append("add")
            return {"command": command, "exit_code": 0, "output": "", "timeout": False}
        if command[:3] == ["git", "diff", "--cached"]:
            return {
                "command": command,
                "exit_code": 0,
                "output": "catalog/sources/demo/task.toml\ncatalog/tasks/demo/task.toml\n",
                "timeout": False,
            }
        if command[:2] == ["git", "commit"]:
            events.append("commit")
            return {"command": command, "exit_code": 0, "output": "committed", "timeout": False}
        if command[:3] == ["git", "rev-parse", "HEAD"]:
            return {"command": command, "exit_code": 0, "output": "abc123", "timeout": False}
        if command[:2] == ["git", "push"]:
            events.append("push")
            return {"command": command, "exit_code": 0, "output": "pushed", "timeout": False}
        if command[:3] == ["git", "worktree", "remove"]:
            events.append("remove")
            return {"command": command, "exit_code": 0, "output": "", "timeout": False}
        raise AssertionError(command)

    class FakeArchive:
        class Lane:
            def __init__(self, language, batch_id, queue_state):
                self.language = language
                self.batch_id = batch_id
                self.queue_state = queue_state

        @staticmethod
        def archive_task(*args, **kwargs):
            del args, kwargs
            events.append("archive")
            return {"status": "archived", "bytes_removed": 1}

    monkeypatch.setattr(supervisor, "_run", fake_run)
    monkeypatch.setattr(supervisor, "_worktree_processes", lambda worktree, procs: [])
    monkeypatch.setattr(supervisor, "_docker_uses", lambda worktree: False)
    monkeypatch.setattr(
        supervisor,
        "_validate_and_compile",
        lambda root, source, language: ({"status": "passed"}, compiled),
    )

    lane = supervisor.Lane(
        "python",
        "batch",
        tmp_path / "queue.json",
        tmp_path / "plan.json",
        tmp_path / "state.json",
    )

    def integrate() -> dict[str, Any]:
        return supervisor._integrate_task(
            root,
            lane,
            "demo",
            {"status": "complete", "attempts": 1},
            [],
            remote="origin",
            branch="main",
            archive_bucket=object(),
            archive_module=FakeArchive,
            receipt_root=tmp_path / "receipts",
            dry_run=False,
            timeout=60,
        )

    return integrate, events


def test_integrate_task_pushes_before_archive_and_removes_worktree(
    tmp_path: Path, monkeypatch
) -> None:
    integrate, events = _integration_checkout(tmp_path, monkeypatch)

    result = integrate()

    assert result["status"] == "integrated"
    assert events == ["status", "add", "commit", "push", "archive", "remove"]


def test_integrate_task_ignores_only_protected_root_scratch(tmp_path: Path, monkeypatch) -> None:
    integrate, events = _integration_checkout(
        tmp_path,
        monkeypatch,
        status_output="?? .scratch/rust-cargo-harbor/issues/01-scope.md\n",
    )

    result = integrate()

    assert result["status"] == "integrated"
    assert events[0] == "status"


@pytest.mark.parametrize(
    "status_output",
    [
        pytest.param("?? other.txt\n", id="untracked-other"),
        pytest.param(" M catalog/sources/demo/task.toml\n", id="tracked-modification"),
        pytest.param("?? .scratchfoo\n", id="scratch-name-prefix"),
        pytest.param("?? .scratch\n", id="scratch-is-file-or-symlink"),
        pytest.param("?? docs/.scratch/nested.md\n", id="nested-scratch-outside-root"),
        pytest.param(
            "?? .scratch/issue.md\n?? .nl2repo/authoring-live/stray\n", id="scratch-plus-stray"
        ),
    ],
)
def test_integrate_task_refuses_dirty_checkout(
    tmp_path: Path, monkeypatch, status_output: str
) -> None:
    integrate, events = _integration_checkout(tmp_path, monkeypatch, status_output)

    with pytest.raises(RuntimeError, match="integration checkout is dirty"):
        integrate()

    assert "add" not in events


PROTECTED_SCRATCH_LINES = [
    pytest.param("?? .scratch/rust-cargo-harbor/issues/01-scope.md\n", [], id="root-scratch-file"),
    pytest.param('?? ".scratch/issue with space.md"\n', [], id="root-scratch-spaces"),
    pytest.param('?? ".scratch/\\346\\226\\207.md"\n', [], id="root-scratch-escaped-name"),
    pytest.param("\n\n", [], id="blank-lines-only"),
]

DIRTY_STATUS_CASES = PROTECTED_SCRATCH_LINES + [
    pytest.param("?? other.txt\n", ["?? other.txt"], id="untracked-other"),
    pytest.param("?? .scratchfoo\n", ["?? .scratchfoo"], id="scratch-name-prefix"),
    pytest.param("?? .scratch\n", ["?? .scratch"], id="scratch-is-file-or-symlink"),
    pytest.param("?? .scratch-root-file\n", ["?? .scratch-root-file"], id="sibling-of-scratch"),
    pytest.param(
        "?? docs/.scratch/nested.md\n",
        ["?? docs/.scratch/nested.md"],
        id="nested-scratch-outside-root",
    ),
    pytest.param(
        " M catalog/sources/demo/task.toml\n",
        [" M catalog/sources/demo/task.toml"],
        id="tracked-modification",
    ),
    pytest.param(
        "A  catalog/tasks/demo/task.toml\n",
        ["A  catalog/tasks/demo/task.toml"],
        id="staged-add",
    ),
    pytest.param("D  readme.md\n", ["D  readme.md"], id="staged-delete"),
    pytest.param("R  a.md -> b.md\n", ["R  a.md -> b.md"], id="rename"),
    pytest.param("?? .scratch/x\n?? stray\n", ["?? stray"], id="scratch-plus-stray"),
]


@pytest.mark.parametrize("porcelain,expected", DIRTY_STATUS_CASES)
def test_dirty_status_lines_allows_only_root_scratch(porcelain: str, expected: list[str]) -> None:
    assert supervisor._dirty_status_lines(porcelain) == expected


def test_git_status_accepts_scratch_only_checkout(tmp_path: Path, monkeypatch) -> None:
    seen: list[list[str]] = []

    def fake_run(command, *, cwd, timeout):
        del cwd, timeout
        seen.append(command)
        return {
            "command": command,
            "exit_code": 0,
            "output": "?? .scratch/rust-cargo-harbor/issues/01-scope.md\n",
            "timeout": False,
        }

    monkeypatch.setattr(supervisor, "_run", fake_run)

    assert supervisor._git_status(tmp_path) == []
    assert seen == [["git", "status", "--porcelain=v1", "--untracked-files=all"]]


def test_git_status_keeps_dirty_lines_and_fails_closed(tmp_path: Path, monkeypatch) -> None:
    exit_code = {"value": 0}
    output = {"value": "?? .scratch/x\n?? other.txt\n"}

    def fake_run(command, *, cwd, timeout):
        del cwd, timeout
        return {
            "command": command,
            "exit_code": exit_code["value"],
            "output": output["value"],
            "timeout": False,
        }

    monkeypatch.setattr(supervisor, "_run", fake_run)

    assert supervisor._git_status(tmp_path) == ["?? other.txt"]

    exit_code["value"] = 128
    with pytest.raises(RuntimeError, match="git status failed"):
        supervisor._git_status(tmp_path)


def test_git_status_matches_real_porcelain_output(tmp_path: Path) -> None:
    """Pin the exemption prefixes against real `git status` formatting."""
    root = tmp_path / "repo"
    root.mkdir()

    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout

    git("init", "-q", "-b", "main")
    git("config", "user.email", "supervisor@example.invalid")
    git("config", "user.name", "supervisor")
    (root / "tracked.txt").write_text("committed\n", encoding="utf-8")
    git("add", "tracked.txt")
    git("commit", "-q", "-m", "seed")
    scratch = root / ".scratch" / "rust-cargo-harbor"
    scratch.mkdir(parents=True)
    (scratch / "issue.md").write_text("scratch\n", encoding="utf-8")
    (scratch / "issue with space.md").write_text("scratch\n", encoding="utf-8")

    assert supervisor._git_status(root) == []

    (root / "other.txt").write_text("stray\n", encoding="utf-8")
    assert supervisor._git_status(root) == ["?? other.txt"]

    (root / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    assert supervisor._git_status(root) == [" M tracked.txt", "?? other.txt"]


def test_queue_summary_counts_states(tmp_path: Path) -> None:
    queue_state = tmp_path / "state.json"
    queue_state.write_text(
        json.dumps(
            {
                "items": {
                    "one": {"status": "complete"},
                    "two": {"status": "pending"},
                    "three": {"status": "pending"},
                }
            }
        ),
        encoding="utf-8",
    )
    lane = supervisor.Lane("go", "batch", tmp_path / "queue", tmp_path / "plan", queue_state)

    assert supervisor._queue_summary(lane) == {
        "language": "go",
        "counts": {"complete": 1, "pending": 2},
        "claimable": True,
        "exhausted": 0,
    }


def test_lane_with_exhausted_pending_claims_is_not_claimable() -> None:
    records = [
        {"status": "pending", "attempts": 3},
        {"status": "complete", "attempts": 1},
    ]

    assert supervisor._lane_has_claimable_work(records, max_attempts=3) is False


def test_redact_removes_secret_values() -> None:
    text = "provider returned sk-" + "a" * 48

    redacted = supervisor._redact(text)

    assert "sk-" + "a" * 48 not in redacted
    assert "[REDACTED]" in redacted


def test_director_response_is_strict_json_and_bounded() -> None:
    response = json.dumps(
        {
            "action": "integrate",
            "language": "go",
            "discover_packages": [],
            "integrate_limit": 2,
            "worker_limit": 1,
            "reason": "integrate ready Go task",
        }
    )

    assert supervisor._parse_director_response(response)["action"] == "integrate"
    with pytest.raises(ValueError, match="plain JSON"):
        supervisor._parse_director_response("```json\n" + response + "\n```")


def test_runtime_config_is_bounded_and_operator_owned(tmp_path: Path) -> None:
    args = type(
        "Args",
        (),
        {"max_total_controllers": 6, "max_integrations": 3},
    )()
    config = tmp_path / "runtime-config.json"
    config.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "enabled": True,
                "max_total_controllers": 4,
                "controller_concurrency": 2,
                "max_integrations": 2,
            }
        ),
        encoding="utf-8",
    )

    assert supervisor._runtime_config(config, args) == {
        "schema_version": "1.0",
        "enabled": True,
        "max_total_controllers": 4,
        "controller_concurrency": 2,
        "max_integrations": 2,
        "agent_limit": None,
    }

    config.write_text(
        json.dumps({"max_total_controllers": 99}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="max_total_controllers"):
        supervisor._runtime_config(config, args)


def test_runtime_config_accepts_eight_controller_cap(tmp_path: Path) -> None:
    config = tmp_path / "runtime-config.json"
    config.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "enabled": True,
                "max_total_controllers": 8,
                "controller_concurrency": 4,
                "max_integrations": 3,
                "agent_limit": 8,
            }
        ),
        encoding="utf-8",
    )
    args = type("Args", (), {"max_total_controllers": 8, "max_integrations": 3})()
    assert supervisor._runtime_config(config, args)["max_total_controllers"] == 8
    assert supervisor._runtime_config(config, args)["agent_limit"] == 8


def test_worker_disk_capacity_requires_repository_and_docker_space() -> None:
    gib = 1024**3

    assert supervisor._worker_disk_capacity(
        30 * gib,
        25 * gib,
        repository_min_free_bytes=12 * gib,
        docker_min_free_bytes=20 * gib,
    )
    assert not supervisor._worker_disk_capacity(
        10 * gib,
        25 * gib,
        repository_min_free_bytes=12 * gib,
        docker_min_free_bytes=20 * gib,
    )
    assert not supervisor._worker_disk_capacity(
        30 * gib,
        18 * gib,
        repository_min_free_bytes=12 * gib,
        docker_min_free_bytes=20 * gib,
    )


def test_docker_storage_status_uses_docker_root_filesystem(monkeypatch) -> None:
    completed = type(
        "Completed",
        (),
        {"returncode": 0, "stdout": "/var/lib/docker\n", "stderr": ""},
    )()
    monkeypatch.setattr(supervisor.subprocess, "run", lambda *args, **kwargs: completed)
    monkeypatch.setattr(supervisor, "_free_bytes", lambda path: 23 * 1024**3)

    path, free, error = supervisor._docker_storage_status()

    assert path == Path("/var/lib/docker")
    assert free == 23 * 1024**3
    assert error is None


def test_docker_storage_status_fails_closed(monkeypatch) -> None:
    completed = type(
        "Completed",
        (),
        {"returncode": 1, "stdout": "", "stderr": "daemon unavailable"},
    )()
    monkeypatch.setattr(supervisor.subprocess, "run", lambda *args, **kwargs: completed)

    path, free, error = supervisor._docker_storage_status()

    assert path == Path("/")
    assert free == 0
    assert error == "daemon unavailable"


def test_go_discovery_pool_has_explicit_repository_mappings() -> None:
    assert supervisor.GO_DISCOVERY_REPOSITORIES["go-btree"] == "google/btree"
    assert supervisor.GO_DISCOVERY_REPOSITORIES["go-cast"] == "spf13/cast"
    assert supervisor.GO_DISCOVERY_REPOSITORIES["go-mapstructure"] == "mitchellh/mapstructure"
    assert supervisor.GO_DISCOVERY_REPOSITORIES["go-uuid"] == "google/uuid"
    assert supervisor.GO_DISCOVERY_REPOSITORIES["go-xxhash"] == "cespare/xxhash"


def test_controller_slots_count_process_groups_not_shared_owner(monkeypatch) -> None:
    lane = supervisor.Lane(
        "go", "batch", Path("/queue"), Path("/plan"), Path("/state")
    )
    procs = [
        supervisor.Proc(
            10,
            "S",
            "/repo",
            "uv run python run_authoring_loop.py --queue-state /state --owner slot-1",
        ),
        supervisor.Proc(
            11,
            "S",
            "/repo",
            "/repo/.venv/bin/python run_authoring_loop.py --queue-state /state --owner slot-1",
        ),
        supervisor.Proc(
            12,
            "S",
            "/repo",
            "uv run python run_authoring_loop.py --queue-state /state --owner slot-2",
        ),
    ]
    process_groups = {10: 100, 11: 100, 12: 120}
    monkeypatch.setattr(supervisor.os, "getpgid", process_groups.__getitem__)

    assert supervisor._controller_slots(lane, procs) == {
        "slot-1@100",
        "slot-2@120",
    }


def test_controller_counts_and_owners_do_not_collide_between_lanes() -> None:
    base = supervisor.Lane(
        "go", "go-author-wave2", Path("/queue-a"), Path("/plan-a"), Path("/state-a")
    )
    generated = supervisor.Lane(
        "go", "go-author-discover-20260829", Path("/queue-b"), Path("/plan-b"), Path("/state-b")
    )
    procs = [
        supervisor.Proc(
            10,
            "S",
            "/repo",
            "run_authoring_loop.py --queue-state /state-a --owner old-go-owner",
        ),
        supervisor.Proc(
            11,
            "S",
            "/repo",
            "run_authoring_loop.py --queue-state /state-b --owner new-go-owner",
        ),
    ]

    assert supervisor._controller_counts([base, generated], procs) == {"go": 2}
    assert supervisor._controller_owner(
        base, 0, launch_nonce="same"
    ) != supervisor._controller_owner(
        generated, 0, launch_nonce="same"
    )


def test_controller_owner_is_unique_across_restarts() -> None:
    lane = supervisor.Lane(
        "python", "batch", Path("/queue"), Path("/plan"), Path("/state")
    )

    assert supervisor._controller_owner(
        lane, 0, launch_nonce="first"
    ) != supervisor._controller_owner(lane, 0, launch_nonce="second")


def test_integrate_task_does_not_mutate_without_oss(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    worktree = root / ".nl2repo/authoring-live/worktrees/batch/demo"
    source = worktree / "catalog/sources/demo"
    source.mkdir(parents=True)
    lane = supervisor.Lane(
        "python", "batch", tmp_path / "queue", tmp_path / "plan", tmp_path / "state"
    )

    result = supervisor._integrate_task(
        root,
        lane,
        "demo",
        {"status": "complete"},
        [],
        remote="origin",
        branch="main",
        archive_bucket=None,
        archive_module=object(),
        receipt_root=tmp_path / "receipts",
        dry_run=False,
        timeout=60,
    )

    assert result == {"package": "demo", "status": "oss-unavailable"}


def test_release_stale_claims_only_releases_expired_inactive_claims(
    tmp_path: Path, monkeypatch
) -> None:
    queue = tmp_path / "queue.json"
    queue.write_text("{}", encoding="utf-8")
    state = tmp_path / "state.json"
    state.write_text(
        json.dumps(
            {
                "items": {
                    "expired": {
                        "status": "running",
                        "package": "expired",
                        "candidate_id": "candidate-expired",
                        "owner": "dead-owner",
                        "lease_expires_at": "2020-01-01T00:00:00+00:00",
                        "attempts": 1,
                    },
                    "live": {
                        "status": "running",
                        "package": "live",
                        "candidate_id": "candidate-live",
                        "owner": "live-owner",
                        "lease_expires_at": "2999-01-01T00:00:00+00:00",
                        "attempts": 1,
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    lane = supervisor.Lane("go", "batch", queue, tmp_path / "plan", state)
    calls: list[list[str]] = []

    def fake_run(command, *, cwd, timeout):
        del cwd, timeout
        calls.append(command)
        return {"command": command, "exit_code": 0, "output": "released", "timeout": False}

    monkeypatch.setattr(supervisor, "_run", fake_run)
    monkeypatch.setattr(supervisor, "_docker_uses", lambda _worktree: False)

    actions = supervisor._release_stale_claims(tmp_path, lane, [], max_attempts=3)

    assert [action["package"] for action in actions] == ["expired"]
    assert calls and calls[0][1:3] == [str(tmp_path / "scripts/package_queue_loop.py"), "release"]


def _prepare_db_supervisor_env(tmp_path: Path, monkeypatch) -> None:
    """Make host-dependent supervisor probes deterministic in-process."""
    monkeypatch.setattr(supervisor, "_free_bytes", lambda _path: 100 * 1024**3)
    monkeypatch.setattr(supervisor, "_git_status", lambda _root: [])
    monkeypatch.setattr(
        supervisor,
        "_start_db_controller",
        lambda *args: pytest.fail("status-envelope test started a controller"),
    )
    monkeypatch.setattr(supervisor, "_start_db_watcher", lambda *args: 4321)


def test_prepared_disabled_db_status_uses_scheduler_status_schema_version(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _prepare_db_supervisor_env(tmp_path, monkeypatch)
    monkeypatch.setattr(
        supervisor, "_docker_storage_status", lambda: (tmp_path, 100 * 1024**3, None)
    )
    database = tmp_path / "prepared.sqlite3"
    scheduler = Scheduler(database, supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(
        enabled=False,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
    )
    scheduler.prepare_cutover_barrier("prepared", "a" * 64)

    exit_code = supervisor.supervise_db(
        SimpleNamespace(
            repository_root=tmp_path,
            live_root=Path("live"),
            scheduler_db=database,
            dry_run=False,
        )
    )

    assert exit_code == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "awaiting-first-enable"
    assert report["schema_version"] == STATUS_SCHEMA_VERSION == "authoring-scheduler/v4"


def test_normal_db_status_report_uses_scheduler_status_schema_version(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _prepare_db_supervisor_env(tmp_path, monkeypatch)
    monkeypatch.setattr(
        supervisor, "_docker_storage_status", lambda: (tmp_path, 0, "docker unavailable")
    )
    database = tmp_path / "normal.sqlite3"
    scheduler = Scheduler(database, supplied_root=tmp_path)
    scheduler.init()
    scheduler.configure(
        enabled=True,
        max_total_controllers=0,
        controller_concurrency=0,
        max_integrations=0,
        agent_limit=0,
    )

    exit_code = supervisor.supervise_db(
        SimpleNamespace(
            repository_root=tmp_path,
            live_root=Path("live"),
            scheduler_db=database,
            remote="fake",
            branch="main",
            interval_sec=1,
            command_timeout=10,
            dry_run=False,
        )
    )

    assert exit_code == 0
    report = json.loads(capsys.readouterr().out)
    assert report["schema_version"] == STATUS_SCHEMA_VERSION == "authoring-scheduler/v4"
    with scheduler.connect() as db:
        stored = json.loads(
            db.execute(
                "SELECT payload_json FROM status_snapshots ORDER BY snapshot_id DESC"
            ).fetchone()[0]
        )
    assert stored["schema_version"] == STATUS_SCHEMA_VERSION
