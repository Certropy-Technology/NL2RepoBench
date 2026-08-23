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
