import json
import subprocess
import sys


def call(proxy, bridge, operation):
    payload = json.dumps({"operation": operation, "args": []}, separators=(",", ":"))
    completed = subprocess.run(
        [proxy, bridge], input=payload + "\n", capture_output=True, text=True, timeout=8
    )
    if completed.returncode != 0:
        return {"error_type": "CallFailed", "message": completed.stderr.strip()}
    lines = completed.stdout.splitlines()
    if len(lines) != 1:
        return {"error_type": "CallFailed", "message": "bridge emitted unexpected output"}
    return json.loads(lines[0])


def main():
    bridge, proxy = sys.argv[1:3]
    expected = {
        "basic": {
            "cardinality": 2,
            "contains_all": True,
            "contains_none": True,
            "sorted": ["alpha", "beta"],
        },
        "mutate": {
            "first_add": True,
            "second_add": False,
            "appended": 1,
            "before_clear": ["a", "c"],
            "empty_after_clear": True,
            "cardinality_cleared": 0,
        },
        "append_from": {
            "added": 2,
            "values": ["a", "b", "c", "d"],
            "unsafe_added": 1,
            "unsafe_values": [1, 2, 3],
        },
        "algebra": {
            "union": ["a", "b", "c", "d"],
            "intersection": ["b", "c"],
            "difference": ["a"],
            "symmetric": ["a", "d"],
            "left_unchanged": ["a", "b", "c"],
            "right_unchanged": ["b", "c", "d"],
        },
        "predicates": {
            "subset": True,
            "proper_subset": True,
            "not_proper_equal": False,
            "superset": True,
            "proper_superset": True,
            "equal": True,
            "not_equal": False,
            "contains_one": True,
            "contains_all": True,
            "contains_any": True,
            "contains_any_element": True,
            "contains_any_empty": False,
        },
        "clone": {"original": ["keep", "remove"], "clone": ["keep"]},
        "each_filter": {
            "sum": 6,
            "visits_before_stop": 1,
            "filtered": [1, 3],
            "original": [1, 2, 3],
        },
        "map_constructor": {
            "cardinality": 2,
            "sorted": ["x", "y"],
            "unsafe": ["a", "b"],
            "empty_safe": True,
            "empty_unsafe": True,
        },
        "concurrent": {"cardinality": 800, "contains_edges": True},
    }
    failures = []
    for operation, want in expected.items():
        result = call(proxy, bridge, operation)
        if result.get("value") != want:
            failures.append(operation + ": " + json.dumps(result, sort_keys=True))

    pop = call(proxy, bridge, "pop")
    expected_pop = {
        "removed_count": 2,
        "removed_unique": 2,
        "removed_disjoint": True,
        "first_ok": True,
        "first_was_remaining": True,
        "second_ok": True,
        "empty_ok": False,
        "empty_zero": 0,
        "empty_n": [],
        "empty_count": 0,
        "non_positive": [],
        "non_positive_count": 0,
        "bounded_unchanged": [7, 8],
    }
    if pop.get("value") != expected_pop:
        failures.append("pop: " + json.dumps(pop, sort_keys=True))

    for operation in ("invalid", "unknown"):
        result = call(proxy, bridge, operation)
        if result.get("error_type") != "InvalidInput":
            failures.append(operation + ": " + json.dumps(result, sort_keys=True))

    if failures:
        report = {
            "schema_version": "1.0",
            "framework": "go",
            "report_format": "go-test-json-v1",
            "collected": 1,
            "tests": [{"test_id": "contract::public-api", "status": "failed", "duration_ms": 0, "details": "; ".join(failures)}],
            "collection_errors": [],
            "runner_exit_code": 1,
        }
    else:
        report = {
            "schema_version": "1.0",
            "framework": "go",
            "report_format": "go-test-json-v1",
            "collected": 1,
            "tests": [{"test_id": "contract::public-api", "status": "passed", "duration_ms": 0}],
            "collection_errors": [],
            "runner_exit_code": 0,
        }
    print(json.dumps(report, separators=(",", ":")))
    raise SystemExit(report["runner_exit_code"])


if __name__ == "__main__":
    main()
