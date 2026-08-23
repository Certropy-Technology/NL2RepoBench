from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/build_oss_run_inventory.py"
    spec = importlib.util.spec_from_file_location("build_oss_run_inventory", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


inventory_module = _load_script()


class _Object:
    def __init__(self, key: str) -> None:
        self.key = key


class _Bucket:
    def __init__(self, keys: list[str]) -> None:
        self.keys = keys

    def get_object(self, key: str):
        class Response:
            def read(self):
                return (
                    b'{"finished_at":"2026-08-23T00:00:00Z",'
                    b'"stats":{"n_completed_trials":1,"n_errored_trials":0}}'
                )

        del key
        return Response()


def test_oss_inventory_deduplicates_objects_and_ignores_oracle_and_unknown() -> None:
    keys = [
        "nl2repobench/runs/gpt-5.6-sol/demo/trial-a/grading.json",
        "nl2repobench/runs/gpt-5.6-sol/demo/trial-a/result.json",
        "nl2repobench/runs/gpt-5.6-sol/demo/trial-a/trajectory.json",
        "nl2repobench/runs/claude-fable-5/demo/trial-b/grading.json",
        "nl2repobench/runs/claude-fable-5/demo/trial-b/result.json",
        "nl2repobench/runs/oracle/demo/trial-c/grading.json",
        "nl2repobench/runs/oracle/demo/trial-c/result.json",
        "nl2repobench/runs/unknown/demo/trial-d/grading.json",
        "nl2repobench/runs/_queue-logs/queue.log",
    ]
    original = inventory_module._objects
    inventory_module._objects = lambda bucket, prefix: (_Object(key) for key in bucket.keys)
    try:
        report = inventory_module.inventory(_Bucket(keys), known_tasks={"demo"})
    finally:
        inventory_module._objects = original

    assert report["object_count_scanned"] == len(keys)
    assert report["run_count"] == 3
    assert {(row["model"], row["task_id"]) for row in report["runs"]} == {
        ("gpt-5.6-sol", "demo"),
        ("claude-fable-5", "demo"),
        ("oracle", "demo"),
    }


def test_oss_inventory_normalizes_historical_task_prefixes() -> None:
    keys = [
        "nl2repobench/runs/claude-fable-5/arguably-fable5-final/trial-a/grading.json",
        "nl2repobench/runs/claude-fable-5/arguably-fable5-final/trial-a/result.json",
        "nl2repobench/runs/gpt-5.6-sol/batch-gpt-boto/trial-b/grading.json",
        "nl2repobench/runs/gpt-5.6-sol/batch-gpt-boto/trial-b/result.json",
        "nl2repobench/runs/gpt-5.6-sol/expansion-gpt/trial-c/queue.log",
    ]
    original = inventory_module._objects
    inventory_module._objects = lambda bucket, prefix: (_Object(key) for key in keys)
    try:
        report = inventory_module.inventory(_Bucket(keys), known_tasks={"arguably", "boto"})
    finally:
        inventory_module._objects = original

    assert {(row["model"], row["task_id"]) for row in report["runs"]} == {
        ("claude-fable-5", "arguably"),
        ("gpt-5.6-sol", "boto"),
    }
