"""Trusted parent for deterministic funcy child scenarios."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ADAPTER = Path(__file__).with_name("adapter.py")
EXPECTED = json.loads(Path(__file__).with_name("expected.json").read_text(encoding="utf-8"))
SCHEMA_VERSION = "funcy-scenarios-v1"
CHILD_TIMEOUT_SEC = 15.0


def case(case_id, request, expected):
    return case_id, {"schema_version": SCHEMA_VERSION, **request}, expected


CASES = [
    case("api-surface", {"action": "api-surface"}, None),
    case("sequence-lmap-named-callback", {"action": "invoke", "api": "lmap", "args": [{"$callback": "double"}, [1, 2, 3]]}, None),
    case("sequence-lfilter-named-predicate", {"action": "invoke", "api": "lfilter", "args": [{"$callback": "even"}, [0, 1, 2, 3, 4]]}, None),
    case("sequence-keep-truthy-mapped-results", {"action": "invoke", "api": "keep", "args": [{"$callback": "modulo-3"}, [0, 1, 2, 3, 4]]}, None),
    case("sequence-take-is-eager", {"action": "invoke", "api": "take", "args": [3, {"$iterator": [4, 5, 6, 7]}]}, None),
    case("iterator-drop-is-lazy", {"action": "lazy-trace", "api": "drop", "source": [1, 2, 3, 4, 5], "args": [2, {"$source": True}], "count": 1}, None),
    case("iterator-iterate-prefix", {"action": "prefix", "api": "iterate", "callback": "double", "initial": 1, "count": 5}, None),
    case("iterator-flatten-depth-first", {"action": "invoke", "api": "flatten", "args": [[1, [2, [3, 4]], 5]]}, None),
    case("iterator-distinct-first-occurrence", {"action": "invoke", "api": "distinct", "args": [["a", "b", "a", "c", "b"]]}, None),
    case("iterator-split-shared-source", {"action": "invoke", "api": "split", "args": [{"$callback": "odd"}, {"$iterator": [0, 1, 2, 3, 4]}]}, None),
    case("sequence-chunks-include-tail", {"action": "invoke", "api": "chunks", "args": [2, [0, 1, 2, 3, 4]]}, None),
    case("iterator-pairwise", {"action": "invoke", "api": "pairwise", "args": [[1, 2, 3, 4]]}, None),
    case("sequence-group-by-encounter-order", {"action": "invoke", "api": "group_by", "args": [{"$callback": "modulo-2"}, [0, 1, 2, 3, 4]]}, None),
    case("iterator-partition-by-runs", {"action": "invoke", "api": "partition_by", "args": [{"$callback": "modulo-2"}, [1, 3, 2, 4, 5]]}, None),
    case("iterator-reductions-with-initial", {"action": "invoke", "api": "reductions", "args": [{"$callback": "add"}, [[1], [2], [3]], []]}, None),
    case("dict-merge-later-precedence", {"action": "invoke", "api": "merge", "args": [{"a": 1, "b": 2}, {"b": 9, "c": 3}]}, None),
    case("dict-merge-with-named-reducer", {"action": "invoke", "api": "merge_with", "args": [{"$callback": "sum-values"}, {"a": 1, "b": 2}, {"a": 4, "c": 3}]}, None),
    case("collection-walk-list-type", {"action": "invoke", "api": "walk", "args": [{"$callback": "increment"}, [1, 2, 3]]}, None),
    case("collection-walk-tuple-type", {"action": "invoke", "api": "walk", "args": [{"$callback": "increment"}, {"$tuple": [1, 2, 3]}]}, None),
    case("collection-walk-dict-pairs", {"action": "invoke", "api": "walk", "args": [{"$callback": "pair-value-double"}, {"a": 1, "b": 2}]}, None),
    case("iterator-walk-preserves-laziness", {"action": "lazy-trace", "api": "walk", "source": [1, 2, 3], "args": [{"$callback": "double"}, {"$source": True}], "count": 1}, None),
    case("dict-walk-keys", {"action": "invoke", "api": "walk_keys", "args": [{"$callback": "key-upper"}, {"a": 1, "b": 2}]}, None),
    case("dict-walk-values", {"action": "invoke", "api": "walk_values", "args": [{"$callback": "double"}, {"a": 1, "b": 2}]}, None),
    case("dict-select-pairs", {"action": "invoke", "api": "select", "args": [{"$callback": "second-gt-one"}, {"a": 1, "b": 2, "c": 3}]}, None),
    case("dict-compact-values", {"action": "invoke", "api": "compact", "args": [{"a": 0, "b": 2, "c": None, "d": 4}]}, None),
    case("dict-update-in-copies-path", {"action": "nested-update", "value": {"outer": {"value": 3}, "same": [1]}, "path": ["outer", "value"], "callback": "double"}, None),
    case("dict-update-in-creates-path", {"action": "nested-update", "value": {"same": 1}, "path": ["outer", "value"], "callback": "increment", "default": 4}, None),
    case("dict-get-in-default", {"action": "invoke", "api": "get_in", "args": [{"outer": [{"value": 7}]}, ["outer", 0, "missing"], "fallback"]}, None),
    case("function-compose-right-to-left", {"action": "compose", "api": "compose", "callbacks": ["increment", "double"], "args": [10]}, None),
    case("function-compose-empty-identity", {"action": "compose", "api": "compose", "callbacks": [], "args": [{"x": 1}]}, None),
    case("function-rcompose-left-to-right", {"action": "compose", "api": "rcompose", "callbacks": ["increment", "double"], "args": [10]}, None),
    case("function-curry-staged", {"action": "staged-call", "api": "curry", "callback": "ternary-concat", "stages": [{"args": ["a"]}, {"args": ["b"]}, {"args": ["c"]}]}, None),
    case("function-autocurry-mixed-stages", {"action": "staged-call", "api": "autocurry", "callback": "affine", "stages": [{"kwargs": {"offset": 3}}, {"kwargs": {"scale": 2}}, {"args": [4]}]}, None),
    case("function-juxt-lazy", {"action": "juxt", "api": "juxt", "callbacks": ["increment", "double", "square"], "args": [3]}, None),
    case("cache-memoize-invalidation", {"action": "memoize-trace", "recipe": "counted-affine", "steps": [{"operation": "call", "args": [2], "kwargs": {"scale": 3}}, {"operation": "call", "args": [2], "kwargs": {"scale": 3}}, {"operation": "invalidate", "args": [2], "kwargs": {"scale": 3}}, {"operation": "call", "args": [2], "kwargs": {"scale": 3}}, {"operation": "invalidate-all"}, {"operation": "call", "args": [2], "kwargs": {"scale": 3}}]}, None),
    case("cache-memoize-custom-key", {"action": "memoize-trace", "recipe": "counted-affine", "key_callback": "modulo-2", "steps": [{"operation": "call", "args": [1]}, {"operation": "call", "args": [3]}, {"operation": "call", "args": [2]}]}, None),
    case("cache-memoize-skip", {"action": "memoize-trace", "recipe": "skip-negative", "steps": [{"operation": "call", "args": [-1]}, {"operation": "call", "args": [-1]}, {"operation": "call", "args": [2]}, {"operation": "call", "args": [2]}]}, None),
    case("cache-timeout-and-invalidate", {"action": "cache-trace", "timeout": 5, "steps": [{"operation": "time", "value": 10}, {"operation": "call", "args": [2], "kwargs": {"scale": 3}}, {"operation": "time", "value": 14}, {"operation": "call", "args": [2], "kwargs": {"scale": 3}}, {"operation": "time", "value": 15}, {"operation": "call", "args": [2], "kwargs": {"scale": 3}}, {"operation": "invalidate", "args": [2], "kwargs": {"scale": 3}}, {"operation": "call", "args": [2], "kwargs": {"scale": 3}}]}, None),
    case("cache-cached-property-lifecycle", {"action": "cached-property", "callback": "computed-seven"}, None),
    case("cache-once-only-first-call", {"action": "once-trace", "callback": "record-affine", "calls": [{"args": [3], "kwargs": {"scale": 2}}, {"args": [9]}, {"args": [4], "kwargs": {"scale": 5}}]}, None),
]


def invoke(request):
    payload = json.dumps(request, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    command = [
        "runuser", "-u", "candidate", "--", "env",
        "HOME=/home/candidate", "PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0",
        "PYTHONNOUSERSITE=1", "LC_ALL=C.UTF-8", "TZ=UTC",
        sys.executable, "-I", "-B", "-",
        "--candidate-site", os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--request", payload,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") == "1":
        command = [
            sys.executable, "-I", "-B", "-",
            "--candidate-site", os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
            "--request", payload,
        ]
    try:
        completed = subprocess.run(
            command,
            input=ADAPTER.read_bytes(),
            capture_output=True,
            timeout=CHILD_TIMEOUT_SEC,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"exception_message": str(error), "exception_type": "VerifierProcessError", "ok": False}
    lines = [line for line in completed.stdout.decode("utf-8", "replace").splitlines() if line]
    if completed.returncode != 0 or len(lines) != 1:
        detail = completed.stderr.decode("utf-8", "replace") or completed.stdout.decode("utf-8", "replace")
        return {"exception_message": detail[-2000:], "exception_type": "CandidateProcessError", "ok": False}
    try:
        response = json.loads(lines[0])
    except json.JSONDecodeError as error:
        return {"exception_message": str(error), "exception_type": "CandidateProtocolError", "ok": False}
    return response if isinstance(response, dict) else {"ok": False}


def main():
    leaves = []
    if set(EXPECTED) != {case_id for case_id, _request, _expected in CASES}:
        raise RuntimeError("expected scenario IDs do not match requests")
    for case_id, request, _expected in CASES:
        expected = EXPECTED[case_id]
        response = invoke(request)
        passed = response.get("ok") is True and response.get("value") == expected
        leaf = {"id": f"funcy/{case_id}", "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = json.dumps(
                {"actual": response, "expected": expected}, ensure_ascii=False, sort_keys=True
            )[:1200]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
