from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_script():
    path = Path(__file__).parents[1] / "scripts/package_queue_loop.py"
    spec = importlib.util.spec_from_file_location("package_queue_loop", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


loop = _load_script()


def _queue(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "queue": [
                    {
                        "candidate_id": "python-demo",
                        "package": "demo",
                        "language": "python",
                        "upstream_url": "https://github.com/example/demo",
                        "source_kind": "pypi",
                        "revision": "a" * 40,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _args(**values):
    return type("Args", (), values)()


def test_queue_claim_and_record_are_owner_bound(tmp_path: Path) -> None:
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    _queue(queue)
    loop.command_init(_args(queue=queue, state=state))
    claimed = _args(
        queue=queue,
        state=state,
        owner="worker-a",
        limit=1,
        lease_seconds=60,
        max_attempts=3,
        language=None,
    )
    assert loop.command_claim(claimed) == 0
    with pytest.raises(ValueError, match="not claimed"):
        loop.command_record(
            _args(
                queue=queue,
                state=state,
                candidate_id="python-demo",
                owner="worker-b",
                status="complete",
                reason=None,
                failure_class=None,
                artifact=[],
            )
        )
    assert (
        loop.command_record(
            _args(
                queue=queue,
                state=state,
                candidate_id="python-demo",
                owner="worker-a",
                status="complete",
                reason=None,
                failure_class=None,
                artifact=["authoring/demo/stage.json"],
            )
        )
        == 0
    )


def test_queue_rejects_changed_input_hash(tmp_path: Path) -> None:
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    _queue(queue)
    loop.command_init(_args(queue=queue, state=state))
    queue.write_text(queue.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="queue changed"):
        loop.command_status(_args(queue=queue, state=state))


def test_queue_terminalizes_expired_lease_at_attempt_limit(tmp_path: Path) -> None:
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    _queue(queue)
    loop.command_init(_args(queue=queue, state=state))
    with loop.locked_state(state) as payload:
        payload["items"]["python-demo"].update(
            {
                "status": "running",
                "owner": "dead-worker",
                "lease_expires_at": "2000-01-01T00:00:00+00:00",
                "attempts": 1,
            }
        )

    assert (
        loop.command_claim(
            _args(
                queue=queue,
                state=state,
                owner="worker-b",
                limit=1,
                lease_seconds=60,
                max_attempts=1,
                language=None,
            )
        )
        == 2
    )
    with loop.locked_state(state) as payload:
        record = payload["items"]["python-demo"]
        assert record["status"] == "blocked"
        assert record["failure_class"] == "infrastructure"


def test_queue_claim_can_target_one_candidate(tmp_path: Path) -> None:
    queue = tmp_path / "queue.json"
    state = tmp_path / "state.json"
    queue.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "queue": [
                    {"candidate_id": "first", "package": "first", "language": "python"},
                    {"candidate_id": "second", "package": "second", "language": "python"},
                ],
            }
        ),
        encoding="utf-8",
    )
    loop.command_init(_args(queue=queue, state=state))

    assert loop.command_claim(
        _args(
            queue=queue,
            state=state,
            owner="worker",
            limit=1,
            lease_seconds=60,
            max_attempts=3,
            language="python",
            candidate_id=["second"],
        )
    ) == 0
    with loop.locked_state(state) as payload:
        assert payload["items"]["second"]["status"] == "running"
        assert payload["items"]["first"]["status"] == "pending"
