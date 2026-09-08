"""Private deterministic scenarios for the jsonpath-ng public contract.

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
        'field_access_name',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.name').find({'name': 'alice', 'age': 30})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["alice"]},
    ),
    (
        'field_access_age',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.age').find({'name': 'alice', 'age': 30})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [30]},
    ),
    (
        'field_access_missing',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.missing').find({'name': 'alice', 'age': 30})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": []},
    ),
    (
        'field_access_bool',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.active').find({'active': True, 'count': 0})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [True]},
    ),
    (
        'field_access_null',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.value').find({'value': None, 'other': 1})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [None]},
    ),
    (
        'root_access',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$').find({'x': 1, 'y': 2})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"x": 1, "y": 2}]},
    ),
    (
        'wildcard_all_fields',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = sorted([m.value for m in parse('$.*').find({'x': 1, 'y': 2, 'z': 3})])\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        'wildcard_empty_object',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.*').find({})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": []},
    ),
    (
        'field_with_underscore',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.user_name').find({'user_name': 'bob', 'age': 25})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["bob"]},
    ),
    (
        'field_with_number',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.item1').find({'item1': 'first', 'item2': 'second'})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["first"]},
    ),
    (
        'nested_two_level',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.user.name').find({'user': {'name': 'charlie', 'age': 28}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["charlie"]},
    ),
    (
        'nested_two_level_missing',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.user.email').find({'user': {'name': 'charlie', 'age': 28}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": []},
    ),
    (
        'nested_two_level_number',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.stats.count').find({'stats': {'count': 42, 'total': 100}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [42]},
    ),
    (
        'nested_three_level',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.a.b.c').find({'a': {'b': {'c': 'deep'}}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["deep"]},
    ),
    (
        'nested_three_level_missing',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.a.b.d').find({'a': {'b': {'c': 'deep'}}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": []},
    ),
    (
        'nested_wildcard',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = sorted([m.value for m in parse('$.user.*').find({'user': {'x': 1, 'y': 2}})])\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [1, 2]},
    ),
    (
        'nested_mixed_types',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.data.value').find({'data': {'value': [1, 2, 3]}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [[1, 2, 3]]},
    ),
    (
        'nested_four_level',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.a.b.c.d').find({'a': {'b': {'c': {'d': 'deepest'}}}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["deepest"]},
    ),
    (
        'nested_field_path_str',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.user.profile.email').find({'user': {'profile': {'email': 'test@test.com'}}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["((user.profile).email)"]},
    ),
    (
        'nested_empty_dict',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.a.b').find({'a': {}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": []},
    ),
    (
        'array_index_first',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[0]').find({'items': [10, 20, 30]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [10]},
    ),
    (
        'array_index_middle',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[1]').find({'items': [10, 20, 30]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [20]},
    ),
    (
        'array_index_last_positive',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[2]').find({'items': [10, 20, 30]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [30]},
    ),
    (
        'array_index_negative',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[-1]').find({'items': [10, 20, 30]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [30]},
    ),
    (
        'array_index_negative_second',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[-2]').find({'items': [10, 20, 30]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [20]},
    ),
    (
        'array_wildcard_simple',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[*]').find({'items': [1, 2, 3]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        'array_wildcard_strings',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.names[*]').find({'names': ['alice', 'bob', 'charlie']})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["alice", "bob", "charlie"]},
    ),
    (
        'array_wildcard_empty',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[*]').find({'items': []})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": []},
    ),
    (
        'array_slice_start_end',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[1:3]').find({'items': [0, 1, 2, 3, 4]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [1, 2]},
    ),
    (
        'array_slice_from_start',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[:2]').find({'items': [0, 1, 2, 3, 4]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [0, 1]},
    ),
    (
        'array_slice_to_end',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[2:]').find({'items': [0, 1, 2, 3, 4]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [2, 3, 4]},
    ),
    (
        'array_slice_full',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[:]').find({'items': [5, 6, 7]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [5, 6, 7]},
    ),
    (
        'array_of_objects_index',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.users[0]').find({'users': [{'name': 'alice'}, {'name': 'bob'}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"name": "alice"}]},
    ),
    (
        'array_nested_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.users[0].name').find({'users': [{'name': 'alice', 'age': 30}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["alice"]},
    ),
    (
        'array_wildcard_nested_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.users[*].name').find({'users': [{'name': 'alice'}, {'name': 'bob'}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["alice", "bob"]},
    ),
    (
        'path_str_root',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$').find({'x': 1})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["$"]},
    ),
    (
        'path_str_simple_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.name').find({'name': 'test'})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["name"]},
    ),
    (
        'path_str_nested',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.a.b').find({'a': {'b': 'val'}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["(a.b)"]},
    ),
    (
        'path_str_array_index',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.items[2]').find({'items': [0, 1, 2]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["(items.[2])"]},
    ),
    (
        'path_str_array_wildcard',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.items[*]').find({'items': [1, 2]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["(items.[0])", "(items.[1])"]},
    ),
    (
        'path_str_nested_array',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.data.items[1]').find({'data': {'items': [10, 20]}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["((data.items).[1])"]},
    ),
    (
        'path_str_array_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.users[0].name').find({'users': [{'name': 'bob'}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["((users.[0]).name)"]},
    ),
    (
        'path_str_deep_nested',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.a.b.c.d').find({'a': {'b': {'c': {'d': 99}}}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["(((a.b).c).d)"]},
    ),
    (
        'path_str_wildcard_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = sorted([str(m.full_path) for m in parse('$.*').find({'x': 1, 'y': 2})])\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["x", "y"]},
    ),
    (
        'path_str_array_slice',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.arr[1:3]').find({'arr': [0, 1, 2, 3]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["(arr.[1])", "(arr.[2])"]},
    ),
    (
        'update_simple_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.val').update({'val': 10}, 20)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"val": 20}},
    ),
    (
        'update_nested_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.user.age').update({'user': {'name': 'alice', 'age': 30}}, 31)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"user": {"name": "alice", "age": 31}}},
    ),
    (
        'update_array_element',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.items[1]').update({'items': [1, 2, 3]}, 99)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"items": [1, 99, 3]}},
    ),
    (
        'update_array_wildcard',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.items[*]').update({'items': [1, 2, 3]}, 0)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"items": [0, 0, 0]}},
    ),
    (
        'update_nested_array_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.users[*].age').update({'users': [{'name': 'a', 'age': 20}, {'name': 'b', 'age': 25}]}, 30)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"users": [{"name": "a", "age": 30}, {"name": "b", "age": 30}]}},
    ),
    (
        'update_to_string',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.val').update({'val': 123}, 'text')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"val": "text"}},
    ),
    (
        'update_to_null',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.val').update({'val': 'something'}, None)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"val": None}},
    ),
    (
        'update_to_bool',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.flag').update({'flag': False}, True)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"flag": True}},
    ),
    (
        'update_to_list',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.val').update({'val': 1}, [1, 2, 3])\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"val": [1, 2, 3]}},
    ),
    (
        'update_to_dict',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.val').update({'val': 'old'}, {'new': 'data'})\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"val": {"new": "data"}}},
    ),
    (
        'exception_invalid_bracket',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$..invalid[]]')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": False, "value": None, "exception_type": "jsonpath_ng.exceptions.JsonPathParserError", "exception_message": "Parse error at 1:11 near token ] (])"},
    ),
    (
        'exception_incomplete_bracket',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$..['))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": False, "value": None, "exception_type": "builtins.SyntaxError", "exception_message": "unmatched ')' (<s>, line 3)"},
    ),
    (
        'exception_unclosed_quote',
        'from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse(\'$."field\')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r',
        {"ok": False, "value": None, "exception_type": "jsonpath_ng.exceptions.JsonPathLexerError", "exception_message": "Unexpected EOF in string literal or identifier"},
    ),
    (
        'exception_empty_path',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": False, "value": None, "exception_type": "jsonpath_ng.exceptions.JsonPathParserError", "exception_message": "Parse error near the end of string!"},
    ),
    (
        'exception_invalid_array_idx',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.arr[abc]')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Child(Child(Root(), Fields('arr')), Fields('abc'))"},
    ),
    (
        'exception_unclosed_array',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.arr[0')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": False, "value": None, "exception_type": "jsonpath_ng.exceptions.JsonPathParserError", "exception_message": "Parse error near the end of string!"},
    ),
    (
        'exception_only_dots',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('...')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": False, "value": None, "exception_type": "jsonpath_ng.exceptions.JsonPathParserError", "exception_message": "Parse error at 1:0 near token .. (DOUBLEDOT)"},
    ),
    (
        'exception_double_dot_end',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.field..')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": False, "value": None, "exception_type": "jsonpath_ng.exceptions.JsonPathParserError", "exception_message": "Parse error near the end of string!"},
    ),
    (
        'exception_malformed_filter',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.arr[?(@.bad')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": False, "value": None, "exception_type": "jsonpath_ng.exceptions.JsonPathLexerError", "exception_message": "Error on line 1, col 6: Unexpected character: ? "},
    ),
    (
        'exception_bad_syntax',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$]['))\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": False, "value": None, "exception_type": "builtins.SyntaxError", "exception_message": "unmatched ')' (<s>, line 3)"},
    ),
    (
        'ext_filter_greater_than',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.items[?(@.price > 10)]').find({'items': [{'price': 5}, {'price': 15}, {'price': 20}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"price": 15}, {"price": 20}]},
    ),
    (
        'ext_filter_less_than',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.items[?(@.price < 15)]').find({'items': [{'price': 5}, {'price': 15}, {'price': 20}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"price": 5}]},
    ),
    (
        'ext_filter_equal',
        'from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse(\'$.items[?(@.name = "alice")]\').find({\'items\': [{\'name\': \'alice\'}, {\'name\': \'bob\'}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r',
        {"ok": True, "value": [{"name": "alice"}]},
    ),
    (
        'ext_filter_not_equal',
        'from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse(\'$.items[?(@.status != "inactive")]\').find({\'items\': [{\'status\': \'active\'}, {\'status\': \'inactive\'}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r',
        {"ok": True, "value": [{"status": "active"}]},
    ),
    (
        'ext_filter_gte',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.items[?(@.score >= 80)]').find({'items': [{'score': 70}, {'score': 80}, {'score': 90}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"score": 80}, {"score": 90}]},
    ),
    (
        'ext_filter_lte',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.items[?(@.score <= 80)]').find({'items': [{'score': 70}, {'score': 80}, {'score': 90}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"score": 70}, {"score": 80}]},
    ),
    (
        'ext_filter_no_match',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.items[?(@.price > 100)]').find({'items': [{'price': 5}, {'price': 15}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": []},
    ),
    (
        'ext_filter_all_match',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.items[?(@.price > 0)]').find({'items': [{'price': 5}, {'price': 15}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"price": 5}, {"price": 15}]},
    ),
    (
        'ext_arithmetic_add',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.a + $.b').find({'a': 10, 'b': 20})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [30]},
    ),
    (
        'ext_arithmetic_multiply',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.x * $.y').find({'x': 3, 'y': 4})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [12]},
    ),
    (
        'ext_filter_string',
        'from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse(\'$.items[?(@.type = "fruit")]\').find({\'items\': [{\'type\': \'fruit\', \'name\': \'apple\'}, {\'type\': \'vegetable\', \'name\': \'carrot\'}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r',
        {"ok": True, "value": [{"type": "fruit", "name": "apple"}]},
    ),
    (
        'ext_filter_bool_true',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.items[?(@.active = true)]').find({'items': [{'active': True}, {'active': False}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"active": True}]},
    ),
    (
        'ext_len',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.items.`len`').find({'items': [1, 2, 3, 4]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [4]},
    ),
    (
        'ext_keys',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = sorted([m.value for m in ext_parse('$.data.`keys`').find({'data': {'a': 1, 'b': 2}})])\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["a", "b"]},
    ),
    (
        'ext_parent_operator',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.a.b.`parent`').find({'a': {'b': 1, 'c': 2}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{"b": 1, "c": 2}]},
    ),
    (
        'edge_empty_string_value',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.text').find({'text': ''})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [""]},
    ),
    (
        'edge_zero_value',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.count').find({'count': 0})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [0]},
    ),
    (
        'edge_false_value',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.flag').find({'flag': False})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [False]},
    ),
    (
        'edge_empty_array',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items').find({'items': []})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [[]]},
    ),
    (
        'edge_empty_dict',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.data').find({'data': {}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [{}]},
    ),
    (
        'edge_nested_empty_array',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.data.items').find({'data': {'items': []}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [[]]},
    ),
    (
        'edge_array_of_nulls',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[*]').find({'items': [None, None, None]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [None, None, None]},
    ),
    (
        'edge_mixed_array_types',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[*]').find({'items': [1, 'two', True, None]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [1, "two", True, None]},
    ),
    (
        'edge_deeply_nested_empty',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.a.b.c.d').find({'a': {'b': {'c': {}}}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": []},
    ),
    (
        'edge_unicode_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.name').find({'name': 'José'})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["José"]},
    ),
    (
        'complex_nested_array_filter',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in ext_parse('$.users[?(@.age > 25)].name').find({'users': [{'name': 'alice', 'age': 30}, {'name': 'bob', 'age': 20}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["alice"]},
    ),
    (
        'complex_multiple_wildcards',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = len([m.value for m in parse('$.data[*].items[*]').find({'data': [{'items': [1, 2]}, {'items': [3, 4]}]})])\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 4},
    ),
    (
        'complex_update_nested_array',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = parse('$.config.settings[0].value').update({'config': {'settings': [{'value': 'old'}]}}, 'new')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": {"config": {"settings": [{"value": "new"}]}}},
    ),
    (
        'complex_path_with_numbers',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [str(m.full_path) for m in parse('$.data[*].id').find({'data': [{'id': 1}, {'id': 2}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["((data.[0]).id)", "((data.[1]).id)"]},
    ),
    (
        'complex_nested_wildcard',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = sorted([m.value for m in parse('$.*.value').find({'a': {'value': 1}, 'b': {'value': 2}})])\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [1, 2]},
    ),
    (
        'complex_array_slice_field',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.items[1:3].name').find({'items': [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}, {'name': 'd'}]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ["b", "c"]},
    ),
    (
        'complex_deep_array_access',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.data.level1.level2[0].value').find({'data': {'level1': {'level2': [{'value': 42}]}}})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [42]},
    ),
    (
        'complex_multiple_filters',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = len([m.value for m in ext_parse('$.items[?(@.price > 10)]').find({'items': [{'price': 15, 'stock': 5}, {'price': 20, 'stock': 0}, {'price': 5, 'stock': 10}]})])\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 2},
    ),
    (
        'complex_array_of_arrays',
        "from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse('$.matrix[1][0]').find({'matrix': [[1, 2], [3, 4]]})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": [3]},
    ),
    (
        'complex_quoted_field_name',
        'from jsonpath_ng import parse\nfrom jsonpath_ng.ext import parse as ext_parse\nr = [m.value for m in parse(\'$."field-with-dash"\').find({\'field-with-dash\': \'value\'})]\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r',
        {"ok": True, "value": ["value"]},
    ),
]

assert len(CASES) == 100, f"Expected 100 cases, got {len(CASES)}"


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
