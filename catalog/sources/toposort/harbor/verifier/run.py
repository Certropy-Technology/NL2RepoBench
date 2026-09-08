"""Private deterministic scenarios for the toposort public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction. The candidate runner executes
the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    (
        'basic_simple',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {2: {11}, 9: {11, 8}, 10: {11, 3}, 11: {7, 5}, 8: {7, 3}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{3, 5, 7}", "{8, 11}", "{9, 2, 10}"]},
    ),
    (
        'basic_with_self_dep',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {2: {2, 11}, 9: {11, 8}, 10: {10, 11, 3}, 11: {7, 5}, 8: {7, 3}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{3, 5, 7}", "{8, 11}", "{9, 2, 10}"]},
    ),
    (
        'single_node_empty',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\nresult = list(toposort({1: set()}))\n',
        {"ok": True, "value": ["{1}"]},
    ),
    (
        'single_node_self_dep',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\nresult = list(toposort({1: {1}}))\n',
        {"ok": True, "value": ["{1}"]},
    ),
    (
        'empty_dict',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\nresult = list(toposort({}))\n',
        {"ok": True, "value": []},
    ),
    (
        'no_dependencies',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2}, 3: {4}, 5: {6}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{2, 4, 6}", "{1, 3, 5}"]},
    ),
    (
        'all_independent',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: set(), 3: set(), 5: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{1, 3, 5}"]},
    ),
    (
        'string_keys',
        "from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {'2': {'11'}, '9': {'11', '8'}, '10': {'11', '3'}, '11': {'7', '5'}, '8': {'7', '3'}}\nresult = [sorted(group) for group in toposort(data)]",
        {"ok": True, "value": [["3", "5", "7"], ["11", "8"], ["10", "2", "9"]]},
    ),
    (
        'circular_simple',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ntry:\n    list(toposort({1: {2}, 2: {1}}))\n    result = None\nexcept CircularDependencyError as e:\n    result = {"exception": True, "data": {k: sorted(list(v)) for k, v in e.data.items()}}\n',
        {"ok": True, "value": {"exception": True, "data": {"1": [2], "2": [1]}}},
    ),
    (
        'circular_indirect',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ntry:\n    list(toposort({1: {2}, 2: {3}, 3: {1}}))\n    result = None\nexcept CircularDependencyError as e:\n    result = {"exception": True, "data": {k: sorted(list(v)) for k, v in e.data.items()}}\n',
        {"ok": True, "value": {"exception": True, "data": {"1": [2], "2": [3], "3": [1]}}},
    ),
    (
        'circular_partial',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ntry:\n    list(toposort({1: {2}, 2: {3}, 3: {1}, 5: {4}, 4: {6}}))\n    result = None\nexcept CircularDependencyError as e:\n    result = {"exception": True, "data": {k: sorted(list(v)) for k, v in e.data.items()}}\n',
        {"ok": True, "value": {"exception": True, "data": {"1": [2], "2": [3], "3": [1]}}},
    ),
    (
        'flatten_basic',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {2: {11}, 9: {11, 8}, 10: {11, 3}, 11: {7, 5}, 8: {7, 3}}\nresult = toposort_flatten(data)\n',
        {"ok": True, "value": [3, 5, 7, 8, 11, 2, 9, 10]},
    ),
    (
        'flatten_unsorted',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {2: {11}, 9: {11, 8}, 10: {11, 3}, 11: {7, 5}, 8: {7, 3}}\nresult = toposort_flatten(data, sort=False)\n',
        {"ok": True, "value": [3, 5, 7, 8, 11, 9, 2, 10]},
    ),
    (
        'flatten_empty',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\nresult = toposort_flatten({})\n',
        {"ok": True, "value": []},
    ),
    (
        'flatten_single',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\nresult = toposort_flatten({1: set()})\n',
        {"ok": True, "value": [1]},
    ),
    (
        'long_chain',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2}, 2: {3}, 3: {4}, 4: {5}, 5: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{5}", "{4}", "{3}", "{2}", "{1}"]},
    ),
    (
        'diamond_dependency',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3}, 2: {4}, 3: {4}, 4: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{4}", "{2, 3}", "{1}"]},
    ),
    (
        'multiple_roots',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {3}, 2: {3}, 3: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{3}", "{1, 2}"]},
    ),
    (
        'deep_tree',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3}, 2: {4, 5}, 3: {6, 7}, 4: set(), 5: set(), 6: set(), 7: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{4, 5, 6, 7}", "{2, 3}", "{1}"]},
    ),
    (
        'mixed_deps',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3}, 2: set(), 3: {4}, 4: set(), 5: {1}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{2, 4}", "{3}", "{1}", "{5}"]},
    ),
    (
        'self_dep_only',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {1}, 2: {2}, 3: {3}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{1, 2, 3}"]},
    ),
    (
        'large_numbers',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {100: {200}, 200: {300}, 300: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{300}", "{200}", "{100}"]},
    ),
    (
        'negative_numbers',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {-1: {-2}, -2: {-3}, -3: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{-3}", "{-2}", "{-1}"]},
    ),
    (
        'alpha_strings',
        "from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {'a': {'b'}, 'b': {'c'}, 'c': set()}\nresult = list(toposort(data))\n",
        {"ok": True, "value": ["{'c'}", "{'b'}", "{'a'}"]},
    ),
    (
        'mixed_case_strings',
        "from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {'A': {'b'}, 'b': {'C'}, 'C': set()}\nresult = list(toposort(data))\n",
        {"ok": True, "value": ["{'C'}", "{'b'}", "{'A'}"]},
    ),
    (
        'star_topology',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: set(), 2: {1}, 3: {1}, 4: {1}, 5: {1}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{1}", "{2, 3, 4, 5}"]},
    ),
    (
        'two_layers',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3, 4}, 2: {5, 6}, 3: {5, 6}, 4: {5, 6}, 5: set(), 6: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{5, 6}", "{2, 3, 4}", "{1}"]},
    ),
    (
        'flatten_chain',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2}, 2: {3}, 3: {4}}\nresult = toposort_flatten(data)\n',
        {"ok": True, "value": [4, 3, 2, 1]},
    ),
    (
        'flatten_diamond',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3}, 2: {4}, 3: {4}}\nresult = toposort_flatten(data)\n',
        {"ok": True, "value": [4, 2, 3, 1]},
    ),
    (
        'flatten_unsorted_multi',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3}, 2: set(), 3: set()}\nresult = toposort_flatten(data, sort=False)\n',
        {"ok": True, "value": [2, 3, 1]},
    ),
    (
        'flatten_circular',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ntry:\n    toposort_flatten({1: {2}, 2: {1}})\n    result = None\nexcept CircularDependencyError as e:\n    result = {"exception": True, "data": {k: sorted(list(v)) for k, v in e.data.items()}}\n',
        {"ok": True, "value": {"exception": True, "data": {"1": [2], "2": [1]}}},
    ),
    (
        'partial_self_deps',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 1}, 2: {3, 2}, 3: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{3}", "{2}", "{1}"]},
    ),
    (
        'deps_not_in_keys',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{2, 3}", "{1}"]},
    ),
    (
        'multiple_levels',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2}, 2: {3, 4}, 3: {5}, 4: {5}, 5: {6}, 6: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{6}", "{5}", "{3, 4}", "{2}", "{1}"]},
    ),
    (
        'broad_shallow',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: set(), 2: set(), 3: set(), 4: set(), 5: set(), 6: {1, 2, 3, 4, 5}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{1, 2, 3, 4, 5}", "{6}"]},
    ),
    (
        'float_keys',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1.0: {2.0}, 2.0: {3.0}, 3.0: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{3.0}", "{2.0}", "{1.0}"]},
    ),
    (
        'tuple_keys',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {(1, 2): {(3, 4)}, (3, 4): {(5, 6)}, (5, 6): set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{(5, 6)}", "{(3, 4)}", "{(1, 2)}"]},
    ),
    (
        'circular_4_nodes',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ntry:\n    list(toposort({1: {2}, 2: {3}, 3: {4}, 4: {1}}))\n    result = None\nexcept CircularDependencyError as e:\n    result = {"exception": True, "data": {k: sorted(list(v)) for k, v in e.data.items()}}\n',
        {"ok": True, "value": {"exception": True, "data": {"1": [2], "2": [3], "3": [4], "4": [1]}}},
    ),
    (
        'circular_with_branch',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ntry:\n    list(toposort({1: {2}, 2: {3}, 3: {1}, 4: {5}, 5: set()}))\n    result = None\nexcept CircularDependencyError as e:\n    result = {"exception": True, "data": {k: sorted(list(v)) for k, v in e.data.items()}}\n',
        {"ok": True, "value": {"exception": True, "data": {"1": [2], "2": [3], "3": [1]}}},
    ),
    (
        'flatten_single_node_self_dep',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\nresult = toposort_flatten({1: {1}})\n',
        {"ok": True, "value": [1]},
    ),
    (
        'flatten_large_set',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {i: {i+1} for i in range(1, 11)}\ndata[10] = set()\nresult = toposort_flatten(data)\n',
        {"ok": True, "value": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]},
    ),
    (
        'parallel_chains',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2}, 2: {3}, 3: set(), 4: {5}, 5: {6}, 6: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{3, 6}", "{2, 5}", "{1, 4}"]},
    ),
    (
        'converging_paths',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {4}, 2: {4}, 3: {4}, 4: {5}, 5: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{5}", "{4}", "{1, 2, 3}"]},
    ),
    (
        'fork_and_join',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3}, 2: {4}, 3: {4}, 4: {5}, 5: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{5}", "{4}", "{2, 3}", "{1}"]},
    ),
    (
        'zero_in_deps',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {0}, 2: {0}, 0: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{0}", "{1, 2}"]},
    ),
    (
        'sequential_integers',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {i: {i-1} if i > 0 else set() for i in range(5)}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{0}", "{1}", "{2}", "{3}", "{4}"]},
    ),
    (
        'long_strings',
        "from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {'first': {'second'}, 'second': {'third'}, 'third': set()}\nresult = list(toposort(data))\n",
        {"ok": True, "value": ["{'third'}", "{'second'}", "{'first'}"]},
    ),
    (
        'unicode_strings',
        "from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {'α': {'β'}, 'β': {'γ'}, 'γ': set()}\nresult = list(toposort(data))\n",
        {"ok": True, "value": ["{'γ'}", "{'β'}", "{'α'}"]},
    ),
    (
        'flatten_star',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: set(), 2: {1}, 3: {1}, 4: {1}}\nresult = toposort_flatten(data)\n',
        {"ok": True, "value": [1, 2, 3, 4]},
    ),
    (
        'flatten_unsorted_complex',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3, 4}, 2: set(), 3: set(), 4: set()}\nresult = toposort_flatten(data, sort=False)\n',
        {"ok": True, "value": [2, 3, 4, 1]},
    ),
    (
        'circular_self_loop',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ntry:\n    list(toposort({1: {1, 2}, 2: {1}}))\n    result = None\nexcept CircularDependencyError as e:\n    result = {"exception": True, "data": {k: sorted(list(v)) for k, v in e.data.items()}}\n',
        {"ok": True, "value": {"exception": True, "data": {"1": [2], "2": [1]}}},
    ),
    (
        'explicit_empty_deps',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: set(), 2: {1}, 3: {1, 2}}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{1}", "{2}", "{3}"]},
    ),
    (
        'large_fanout',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: set()}\nfor i in range(2, 12):\n    data[i] = {1}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{1}", "{2, 3, 4, 5, 6, 7, 8, 9, 10, 11}"]},
    ),
    (
        'flatten_two_components',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2}, 2: set(), 3: {4}, 4: set()}\nresult = toposort_flatten(data)\n',
        {"ok": True, "value": [2, 4, 1, 3]},
    ),
    (
        'flatten_unsorted_single',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\nresult = toposort_flatten({1: set()}, sort=False)\n',
        {"ok": True, "value": [1]},
    ),
    (
        'layered_5',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {i: {i-1} if i > 1 else set() for i in range(1, 6)}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{1}", "{2}", "{3}", "{4}", "{5}"]},
    ),
    (
        'binary_tree_deps',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3}, 2: {4, 5}, 3: {6, 7}}\nfor i in range(4, 8):\n    data[i] = set()\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{4, 5, 6, 7}", "{2, 3}", "{1}"]},
    ),
    (
        'mixed_int_float',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2.0}, 2.0: {3}, 3: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{3}", "{2.0}", "{1}"]},
    ),
    (
        'many_empty_deps',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {i: set() for i in range(1, 11)}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}"]},
    ),
    (
        'single_dep_to_many',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2, 3, 4, 5, 6}, 2: set(), 3: set(), 4: set(), 5: set(), 6: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{2, 3, 4, 5, 6}", "{1}"]},
    ),
    (
        'deps_form_independent_groups',
        'from toposort import toposort, toposort_flatten, CircularDependencyError\n\ndata = {1: {2}, 2: set(), 3: {4}, 4: set(), 5: {6}, 6: set()}\nresult = list(toposort(data))\n',
        {"ok": True, "value": ["{2, 4, 6}", "{1, 3, 5}"]},
    ),
]

assert len(CASES) == 61, f"Expected 61 cases, got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True, default=repr)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
