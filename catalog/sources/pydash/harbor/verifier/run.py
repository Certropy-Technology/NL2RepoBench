#!/usr/bin/env python3
"""
Custom JSON v1 verifier for pydash.
Protocol: LAST stdout line = {"schema_version":"1.0","leaves":[{id,status}...]}
"""
import json
import sys
from nl2repobench.verification.candidate_client import execute_script

CASES = [
    ("chunk_1", "import pydash\nresult = pydash.chunk([1, 2, 3, 4, 5], 2)", {"ok": True, "value": [[1, 2], [3, 4], [5]]}),
    ("chunk_2", "import pydash\nresult = pydash.chunk(['a', 'b', 'c', 'd'], 3)", {"ok": True, "value": [["a", "b", "c"], ["d"]]}),
    ("compact_1", "import pydash\nresult = pydash.compact([0, 1, False, 2, '', 3, None])", {"ok": True, "value": [1, 2, 3]}),
    ("compact_2", "import pydash\nresult = pydash.compact([[], {}, [1], {'a': 1}])", {"ok": True, "value": [[1], {"a": 1}]}),
    ("first_1", "import pydash\nresult = pydash.head([1, 2, 3])", {"ok": True, "value": 1}),
    ("first_2", "import pydash\nresult = pydash.head([])", {"ok": True, "value": None}),
    ("last_1", "import pydash\nresult = pydash.last([1, 2, 3])", {"ok": True, "value": 3}),
    ("last_2", "import pydash\nresult = pydash.last([5])", {"ok": True, "value": 5}),
    ("flatten_1", "import pydash\nresult = pydash.flatten([1, [2, 3], [[4]]])", {"ok": True, "value": [1, 2, 3, [4]]}),
    ("flatten_2", "import pydash\nresult = pydash.flatten([[1, 2], [3, [4, 5]]])", {"ok": True, "value": [1, 2, 3, [4, 5]]}),
    ("flatten_deep_1", "import pydash\nresult = pydash.flatten_deep([1, [2, [3, [4]]]])", {"ok": True, "value": [1, 2, 3, 4]}),
    ("flatten_deep_2", "import pydash\nresult = pydash.flatten_deep([[[1]], [2, [3]], 4])", {"ok": True, "value": [1, 2, 3, 4]}),
    ("initial_1", "import pydash\nresult = pydash.initial([1, 2, 3])", {"ok": True, "value": [1, 2]}),
    ("take_1", "import pydash\nresult = pydash.take([1, 2, 3, 4, 5], 3)", {"ok": True, "value": [1, 2, 3]}),
    ("take_2", "import pydash\nresult = pydash.take([1, 2], 5)", {"ok": True, "value": [1, 2]}),
    ("take_right_1", "import pydash\nresult = pydash.take_right([1, 2, 3, 4, 5], 2)", {"ok": True, "value": [4, 5]}),
    ("union_1", "import pydash\nresult = pydash.union([1, 2], [2, 3], [3, 4])", {"ok": True, "value": [1, 2, 3, 4]}),
    ("uniq_1", "import pydash\nresult = pydash.uniq([1, 2, 2, 3, 3, 3])", {"ok": True, "value": [1, 2, 3]}),
    ("uniq_2", "import pydash\nresult = pydash.uniq(['a', 'b', 'a', 'c'])", {"ok": True, "value": ["a", "b", "c"]}),
    ("without_1", "import pydash\nresult = pydash.without([1, 2, 3, 4], 2, 4)", {"ok": True, "value": [1, 3]}),
    ("get_1", "import pydash\nresult = pydash.get({'a': {'b': {'c': 3}}}, 'a.b.c')", {"ok": True, "value": 3}),
    ("get_2", "import pydash\nresult = pydash.get({'a': [{'b': 1}]}, 'a[0].b')", {"ok": True, "value": 1}),
    ("get_3", "import pydash\nresult = pydash.get({'x': 1}, 'y', default=10)", {"ok": True, "value": 10}),
    ("has_1", "import pydash\nresult = pydash.has({'a': {'b': 2}}, 'a.b')", {"ok": True, "value": True}),
    ("has_2", "import pydash\nresult = pydash.has({'a': 1}, 'a.b')", {"ok": True, "value": False}),
    ("set_1", "import pydash\nobj = {}\npydash.set_(obj, 'a.b.c', 5)\nresult = obj", {"ok": True, "value": {"a": {"b": {"c": 5}}}}),
    ("set_2", "import pydash\nobj = {'x': 1}\npydash.set_(obj, 'y', 2)\nresult = obj", {"ok": True, "value": {"x": 1, "y": 2}}),
    ("unset_1", "import pydash\nobj = {'a': {'b': {'c': 3}}, 'd': 4}\npydash.unset(obj, 'a.b.c')\nresult = obj", {"ok": True, "value": {"a": {"b": {}}, "d": 4}}),
    ("map_1", "import pydash\nresult = pydash.map_([1, 2, 3], lambda x: x * 2)", {"ok": True, "value": [2, 4, 6]}),
    ("map_2", "import pydash\nresult = pydash.map_([{'a': 1}, {'a': 2}], 'a')", {"ok": True, "value": [1, 2]}),
    ("filter_1", "import pydash\nresult = pydash.filter_([1, 2, 3, 4], lambda x: x % 2 == 0)", {"ok": True, "value": [2, 4]}),
    ("filter_2", "import pydash\nresult = pydash.filter_([{'a': 1}, {'a': 2}, {'a': 1}], {'a': 1})", {"ok": True, "value": [{"a": 1}, {"a": 1}]}),
    ("reduce_1", "import pydash\nresult = pydash.reduce_([1, 2, 3, 4], lambda acc, x: acc + x, 0)", {"ok": True, "value": 10}),
    ("reduce_2", "import pydash\nresult = pydash.reduce_([1, 2, 3], lambda acc, x: acc * x, 1)", {"ok": True, "value": 6}),
    ("group_by_1", "import pydash\nresult = pydash.group_by([1.3, 2.1, 2.4], lambda x: int(x))", {"ok": True, "value": {"1": [1.3], "2": [2.1, 2.4]}}),
    ("group_by_2", "import pydash\nresult = pydash.group_by(['one', 'two', 'three'], len)", {"ok": True, "value": {"3": ["one", "two"], "5": ["three"]}}),
    ("key_by_1", "import pydash\nresult = pydash.key_by([{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}], 'id')", {"ok": True, "value": {"1": {"id": 1, "name": "a"}, "2": {"id": 2, "name": "b"}}}),
    ("key_by_2", "import pydash\nresult = pydash.key_by(['a', 'b', 'c'], lambda x: x.upper())", {"ok": True, "value": {"A": "a", "B": "b", "C": "c"}}),
    ("find_1", "import pydash\nresult = pydash.find([1, 2, 3, 4], lambda x: x > 2)", {"ok": True, "value": 3}),
    ("find_2", "import pydash\nresult = pydash.find([{'a': 1}, {'a': 2}], {'a': 2})", {"ok": True, "value": {"a": 2}}),
    ("find_index_1", "import pydash\nresult = pydash.find_index([1, 2, 3, 4], lambda x: x == 3)", {"ok": True, "value": 2}),
    ("find_index_2", "import pydash\nresult = pydash.find_index([1, 2, 3], lambda x: x > 10)", {"ok": True, "value": -1}),
    ("every_1", "import pydash\nresult = pydash.every([2, 4, 6], lambda x: x % 2 == 0)", {"ok": True, "value": True}),
    ("every_2", "import pydash\nresult = pydash.every([2, 3, 4], lambda x: x % 2 == 0)", {"ok": True, "value": False}),
    ("some_1", "import pydash\nresult = pydash.some([1, 2, 3], lambda x: x > 2)", {"ok": True, "value": True}),
    ("some_2", "import pydash\nresult = pydash.some([1, 2, 3], lambda x: x > 10)", {"ok": True, "value": False}),
    ("includes_1", "import pydash\nresult = pydash.includes([1, 2, 3], 2)", {"ok": True, "value": True}),
    ("includes_2", "import pydash\nresult = pydash.includes([1, 2, 3], 5)", {"ok": True, "value": False}),
    ("is_empty_1", "import pydash\nresult = pydash.is_empty([])", {"ok": True, "value": True}),
    ("is_empty_2", "import pydash\nresult = pydash.is_empty([1, 2])", {"ok": True, "value": False}),
    ("is_empty_3", "import pydash\nresult = pydash.is_empty({})", {"ok": True, "value": True}),
    ("is_equal_1", "import pydash\nresult = pydash.is_equal([1, 2, 3], [1, 2, 3])", {"ok": True, "value": True}),
    ("is_equal_2", "import pydash\nresult = pydash.is_equal({'a': 1}, {'a': 1})", {"ok": True, "value": True}),
    ("is_equal_3", "import pydash\nresult = pydash.is_equal([1, 2], [2, 1])", {"ok": True, "value": False}),
    ("merge_1", "import pydash\nresult = pydash.merge({'a': 1}, {'b': 2})", {"ok": True, "value": {"a": 1, "b": 2}}),
    ("merge_2", "import pydash\nresult = pydash.merge({'a': 1, 'b': 2}, {'b': 3, 'c': 4})", {"ok": True, "value": {"a": 1, "b": 3, "c": 4}}),
    ("pick_1", "import pydash\nresult = pydash.pick({'a': 1, 'b': 2, 'c': 3}, 'a', 'c')", {"ok": True, "value": {"a": 1, "c": 3}}),
    ("pick_2", "import pydash\nresult = pydash.pick({'x': 1, 'y': 2}, 'x')", {"ok": True, "value": {"x": 1}}),
    ("omit_1", "import pydash\nresult = pydash.omit({'a': 1, 'b': 2, 'c': 3}, 'b')", {"ok": True, "value": {"a": 1, "c": 3}}),
    ("omit_2", "import pydash\nresult = pydash.omit({'x': 1, 'y': 2, 'z': 3}, 'x', 'z')", {"ok": True, "value": {"y": 2}}),
    ("keys_1", "import pydash\nresult = sorted(pydash.keys({'a': 1, 'b': 2}))", {"ok": True, "value": ["a", "b"]}),
    ("values_1", "import pydash\nresult = sorted(pydash.values({'a': 1, 'b': 2, 'c': 3}))", {"ok": True, "value": [1, 2, 3]}),
    ("invert_1", "import pydash\nresult = pydash.invert({'a': 1, 'b': 2})", {"ok": True, "value": {"1": "a", "2": "b"}}),
    ("defaults_1", "import pydash\nresult = pydash.defaults({'a': 1}, {'a': 2, 'b': 2})", {"ok": True, "value": {"a": 1, "b": 2}}),
    ("negate_1", "import pydash\nis_even = lambda x: x % 2 == 0\nis_odd = pydash.negate(is_even)\nresult = is_odd(3)", {"ok": True, "value": True}),
    ("negate_2", "import pydash\nis_positive = lambda x: x > 0\nis_not_positive = pydash.negate(is_positive)\nresult = is_not_positive(-5)", {"ok": True, "value": True}),
    ("times_1", "import pydash\nresult = pydash.times(3, lambda i: i * 2)", {"ok": True, "value": [0, 2, 4]}),
    ("times_2", "import pydash\nresult = pydash.times(5, lambda i: i)", {"ok": True, "value": [0, 1, 2, 3, 4]}),
    ("identity_1", "import pydash\nresult = pydash.identity(42)", {"ok": True, "value": 42}),
    ("identity_2", "import pydash\nresult = pydash.identity([1, 2, 3])", {"ok": True, "value": [1, 2, 3]}),
    ("constant_1", "import pydash\nconst_func = pydash.constant(42)\nresult = const_func()", {"ok": True, "value": 42}),
    ("range_1", "import pydash\nresult = list(pydash.range_(5))", {"ok": True, "value": [0, 1, 2, 3, 4]}),
    ("range_2", "import pydash\nresult = list(pydash.range_(1, 6))", {"ok": True, "value": [1, 2, 3, 4, 5]}),
    ("range_3", "import pydash\nresult = list(pydash.range_(0, 10, 2))", {"ok": True, "value": [0, 2, 4, 6, 8]}),
    ("camel_case_1", "import pydash\nresult = pydash.camel_case('hello world')", {"ok": True, "value": "helloWorld"}),
    ("snake_case_1", "import pydash\nresult = pydash.snake_case('helloWorld')", {"ok": True, "value": "hello_world"}),
    ("kebab_case_1", "import pydash\nresult = pydash.kebab_case('helloWorld')", {"ok": True, "value": "hello-world"}),
    ("capitalize_1", "import pydash\nresult = pydash.capitalize('hello world')", {"ok": True, "value": "Hello world"}),
    ("upper_first_1", "import pydash\nresult = pydash.upper_first('hello')", {"ok": True, "value": "Hello"}),
    ("lower_first_1", "import pydash\nresult = pydash.lower_first('Hello')", {"ok": True, "value": "hello"}),
    ("truncate_1", "import pydash\nresult = pydash.truncate('hello world', 8)", {"ok": True, "value": "hello..."}),
    ("intersection_1", "import pydash\nresult = pydash.intersection([1, 2, 3], [2, 3, 4])", {"ok": True, "value": [2, 3]}),
    ("difference_1", "import pydash\nresult = pydash.difference([1, 2, 3], [2, 4])", {"ok": True, "value": [1, 3]}),
    ("zip_1", "import pydash\nresult = pydash.zip_([1, 2], ['a', 'b'], [True, False])", {"ok": True, "value": [[1, "a", True], [2, "b", False]]}),
    ("unzip_1", "import pydash\nresult = pydash.unzip([[1, 'a'], [2, 'b']])", {"ok": True, "value": [[1, 2], ["a", "b"]]}),
]

def main():
    leaves = []
    for test_id, script, expected in CASES:
        actual = execute_script(script)
        
        # Compare results
        if actual == expected:
            status = "passed"
        else:
            status = "failed"
        
        leaves.append({"id": test_id, "status": status})
    
    # Output final JSON on last line
    result = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(result, separators=(',', ':')))

if __name__ == "__main__":
    main()
