"""Trusted comparator for deterministic cachetools child scenarios."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ADAPTER = Path(__file__).with_name("adapter.py")
SCHEMA_VERSION = "cachetools-scenarios-v1"
CHILD_TIMEOUT_SEC = 20.0

CASES = [
    (
        "api-surface-packaging-and-version",
        "api_surface",
        {"candidate_origin": True, "func_all": ["fifo_cache", "lfu_cache", "lru_cache", "rr_cache", "ttl_cache"], "keys_all": ["hashkey", "methodkey", "typedkey", "typedmethodkey"], "mutable_mappings": True, "py_typed": True, "root_all": ["Cache", "FIFOCache", "LFUCache", "LRUCache", "RRCache", "TLRUCache", "TTLCache", "cached", "cachedmethod"], "version": "7.1.7"},
    ),
    (
        "base-cache-sizing-errors-and-clear",
        "cache_sizing",
        {"before_clear": {"currsize": 1, "items": [["a", "x"]]}, "cleared": {"currsize": 0, "length": 0}, "default_size": 1, "initial_size": 5, "maxsize": 5, "negative_error": "ValueError", "oversized_error": "ValueError", "popped": "yyy", "replaced_size": 4, "zero_error": "ValueError"},
    ),
    (
        "missing-hook-versus-mapping-methods",
        "missing_mapping",
        {"default_value": 4, "get_value": "fallback", "items": [["four", 4]], "misses": ["one"], "pop_value": "fallback", "subscription": "generated:one"},
    ),
    (
        "fifo-read-and-replacement-order",
        "fifo_policy",
        {"empty_error": "KeyError", "victims": [["a", 1], ["c", 3], ["b", 20]]},
    ),
    (
        "lru-most-recently-used-order",
        "lru_mru_policy",
        {"remaining": [["d", 40]], "victims": [["b", 2], ["c", 3], ["a", 1]]},
    ),
    (
        "mru-child-subclass-most-recent-eviction",
        "mru_policy",
        {"remaining": [["d", 4], ["e", 5]], "victims": [["a", 1], ["c", 3], ["b", 2]]},
    ),
    (
        "lfu-unique-frequency-evictions",
        "lfu_policy",
        {"after_first_eviction": ["a", "b", "d"], "final_items": [["a", 1], ["d", 4], ["e", 5]]},
    ),
    (
        "random-replacement-injected-choice",
        "rr_policy",
        {"calls": [["a", "b"], ["a", "c"]], "choice_identity": True, "popped": ["c", 3], "remaining": [["a", 1]]},
    ),
    (
        "ttl-explicit-clock-and-exact-deadline",
        "ttl_expiration",
        {"contains_c_at_deadline": False, "expired_at_five": [["c", 3]], "expired_at_four": [["b", 2]], "expired_at_three": [["a", 1]], "get_c_error": "KeyError", "length": 0, "timer_identity": True, "ttl": 3},
    ),
    (
        "ttl-lru-fallback-and-frozen-timer",
        "ttl_lru_and_timer",
        {"frozen_timer_values": [0, 0, 0], "lru_items": [["a", 1], ["c", 3]], "outside_timer_value": 1},
    ),
    (
        "ttl-datetime-timedelta-domain",
        "ttl_datetime_domain",
        {"before_deadline": [], "exact_deadline": [["dated", 7]], "length": 0},
    ),
    (
        "tlru-ttu-expiry-and-dead-on-arrival",
        "tlru_expiration",
        {"after_dead_on_arrival": [["medium", 3]], "expires_at_one": [["short", 1]], "expires_at_three": [["medium", 3]], "final_items": [["fresh", 2]], "ttu_result": 6},
    ),
    (
        "key-order-typing-concatenation-and-pickle",
        "key_functions",
        {"concatenated": ["a", "b"], "concatenated_type": "_HashedTuple", "method_ignores_self": True, "ordered_kwargs": True, "pickle_roundtrip": True, "typed_distinct": True, "typed_method_ignores_self": True, "unhashable_error": "TypeError", "untyped_numeric_equal": True},
    ),
    (
        "cached-info-metadata-clear-and-oversize",
        "cached_function",
        {"calls": [[2, 3], [4, 1]], "info_after_clear": [0, 0, 2, 0], "info_before_clear": [1, 2, 2, 2], "metadata": {"cache_identity": True, "doc": "Multiply a value.", "name": "compute", "wrapped_name": "compute"}, "oversized_cache_length": 0, "oversized_call_count": 2, "oversized_results": ["large", "large"], "results": [6, 6, 4]},
    ),
    (
        "cachedmethod-per-instance-and-shared-cache",
        "cached_method",
        {"bound_cache_identity": True, "calls": [1, 1], "first_info": [1, 1, 2, 1], "metadata": ["value", "Return a labeled value.", "value"], "results": ["first:2", "first:2", "second:2"], "second_info": [0, 1, 2, 1], "shared_calls": [1, 0], "shared_results": ["left:1", "left:1"]},
    ),
    (
        "convenience-lru-typed-zero-and-parameters",
        "convenience_lru",
        {"parameters_after_mutation": {"maxsize": 2, "typed": True}, "typed_calls": ["int", "float"], "typed_info": [0, 2, 2, 2], "typed_results": ["int", "float"], "untyped_calls": ["int"], "untyped_info": [1, 1, 2, 1], "untyped_results": ["int", "int"], "zero_call_count": 2, "zero_info": [0, 2, 0, 0]},
    ),
    (
        "convenience-ttl-injected-clock",
        "convenience_ttl",
        {"after_deadline": [1, 2, 2, 1], "before_deadline": [1, 1, 2, 1], "calls": [3, 3], "parameters": {"maxsize": 2, "typed": False}, "results": [30, 30, 30]},
    ),
    (
        "condition-prevents-same-key-stampede",
        "condition_stampede",
        {"alive": [False, False], "call_count": 1, "info": [1, 1, 2, 1], "results": [10, 10]},
    ),
]


def invoke(operation: str) -> dict[str, object]:
    request = json.dumps(
        {"operation": operation, "schema_version": SCHEMA_VERSION},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/home/candidate",
        "PYTHONDONTWRITEBYTECODE=1",
        "PYTHONHASHSEED=0",
        "PYTHONNOUSERSITE=1",
        "LC_ALL=C.UTF-8",
        sys.executable,
        "-I",
        "-B",
        "-",
        "--candidate-site",
        os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--request",
        request,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") == "1":
        command = [
            sys.executable,
            "-I",
            "-B",
            "-",
            "--candidate-site",
            os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
            "--request",
            request,
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
        result = json.loads(lines[0])
    except json.JSONDecodeError as error:
        return {"exception_message": str(error), "exception_type": "CandidateProtocolError", "ok": False}
    if not isinstance(result, dict):
        return {"exception_message": "adapter response is not an object", "exception_type": "CandidateProtocolError", "ok": False}
    return result


def main() -> None:
    leaves = []
    for case_id, operation, expected in CASES:
        result = invoke(operation)
        passed = result.get("ok") is True and result.get("value") == expected
        leaf = {"id": "cachetools/" + case_id, "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = json.dumps(
                {"actual": result, "expected": expected},
                ensure_ascii=False,
                sort_keys=True,
            )[:1000]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
