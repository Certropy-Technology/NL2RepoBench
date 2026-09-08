#!/usr/bin/env python3
"""Verifier for bidict task - custom-json-v1 protocol."""
import json
import subprocess
import sys
from pathlib import Path

CASES = [
    # Group 1: Construction (9 tests)
    ("empty_construction", "dict(bidict())", {"ok": True, "value": {}}),
    ("dict_construction", "dict(bidict({'a': 1, 'b': 2}))", {"ok": True, "value": {"a": 1, "b": 2}}),
    ("kwargs_construction", "dict(bidict(x=10, y=20))", {"ok": True, "value": {"x": 10, "y": 20}}),
    ("pairs_construction", "dict(bidict([('k1', 'v1'), ('k2', 'v2')]))", {"ok": True, "value": {"k1": "v1", "k2": "v2"}}),
    ("mixed_construction", "dict(bidict({'a': 1}, b=2))", {"ok": True, "value": {"a": 1, "b": 2}}),
    ("single_pair", "dict(bidict({'key': 'value'}))", {"ok": True, "value": {"key": "value"}}),
    ("int_keys", "dict(bidict({1: 'a', 2: 'b'}))", {"ok": True, "value": {1: "a", 2: "b"}}),
    ("str_values", "dict(bidict({'x': 'foo', 'y': 'bar'}))", {"ok": True, "value": {"x": "foo", "y": "bar"}}),
    ("mixed_types", "dict(bidict({'a': 1, 'b': 'two', 'c': 3.0}))", {"ok": True, "value": {"a": 1, "b": "two", "c": 3.0}}),
    
    # Group 2: Access operations (10 tests)
    ("access_key", "bidict({'a': 1, 'b': 2})['a']", {"ok": True, "value": 1}),
    ("access_int_key", "bidict({1: 'one', 2: 'two'})[1]", {"ok": True, "value": "one"}),
    ("inverse_access", "bidict({'a': 1, 'b': 2}).inverse[1]", {"ok": True, "value": "a"}),
    ("inverse_access_str", "bidict({1: 'one', 2: 'two'}).inverse['one']", {"ok": True, "value": 1}),
    ("double_inverse_access", "bidict({'x': 10}).inverse.inverse['x']", {"ok": True, "value": 10}),
    ("get_present", "bidict({'a': 1}).get('a')", {"ok": True, "value": 1}),
    ("get_absent", "bidict({'a': 1}).get('z')", {"ok": True, "value": None}),
    ("get_with_default", "bidict({'a': 1}).get('z', -1)", {"ok": True, "value": -1}),
    ("get_zero_default", "bidict({'a': 1}).get('z', 0)", {"ok": True, "value": 0}),
    ("inverse_get", "bidict({'a': 1}).inverse.get(1)", {"ok": True, "value": "a"}),
    
    # Group 3: Inverse operations (9 tests)
    ("inverse_dict", "dict(bidict({'a': 1, 'b': 2}).inverse)", {"ok": True, "value": {1: "a", 2: "b"}}),
    ("inverse_len", "len(bidict({'a': 1, 'b': 2}).inverse)", {"ok": True, "value": 2}),
    ("inverse_keys", "sorted(bidict({'a': 1, 'b': 2}).inverse.keys())", {"ok": True, "value": [1, 2]}),
    ("inverse_values", "sorted(bidict({'a': 1, 'b': 2}).inverse.values())", {"ok": True, "value": ["a", "b"]}),
    ("inverse_items", "sorted(bidict({'a': 1, 'b': 2}).inverse.items())", {"ok": True, "value": [[1, "a"], [2, "b"]]}),
    ("inverse_contains", "1 in bidict({'a': 1}).inverse", {"ok": True, "value": True}),
    ("inverse_not_contains", "99 in bidict({'a': 1}).inverse", {"ok": True, "value": False}),
    ("inverse_inverse", "dict(bidict({'a': 1}).inverse.inverse)", {"ok": True, "value": {"a": 1}}),
    ("inverse_empty", "dict(bidict().inverse)", {"ok": True, "value": {}}),
    
    # Group 4: Modification - setdefault (6 tests)
    ("setdefault_new", "(lambda b: (b.setdefault('b', 2), dict(b)))(bidict({'a': 1}))[1]", {"ok": True, "value": {"a": 1, "b": 2}}),
    ("setdefault_existing", "(lambda b: (b.setdefault('a', 99), dict(b)))(bidict({'a': 1}))[1]", {"ok": True, "value": {"a": 1}}),
    ("setdefault_return_new", "bidict({'a': 1}).setdefault('b', 2)", {"ok": True, "value": 2}),
    ("setdefault_return_existing", "bidict({'a': 1}).setdefault('a', 99)", {"ok": True, "value": 1}),
    ("setdefault_zero", "bidict().setdefault('x', 0)", {"ok": True, "value": 0}),
    ("setdefault_none", "bidict().setdefault('x', None)", {"ok": True, "value": None}),
    
    # Group 5: Update operations (6 tests)
    ("update_dict", "(lambda b: (b.update({'c': 3}), dict(b)))(bidict({'a': 1}))[1]", {"ok": True, "value": {"a": 1, "c": 3}}),
    ("update_pairs", "(lambda b: (b.update([('x', 10)]), dict(b)))(bidict({'a': 1}))[1]", {"ok": True, "value": {"a": 1, "x": 10}}),
    ("update_kwargs", "(lambda b: (b.update(z=26), dict(b)))(bidict({'a': 1}))[1]", {"ok": True, "value": {"a": 1, "z": 26}}),
    ("update_empty", "(lambda b: (b.update({}), dict(b)))(bidict({'a': 1}))[1]", {"ok": True, "value": {"a": 1}}),
    ("update_overwrite", "(lambda b: (b.update({'a': 99}), dict(b)))(bidict({'a': 1}))[1]", {"ok": True, "value": {"a": 99}}),
    ("assignment_new", "(lambda b: (b.__setitem__('c', 3), dict(b)))(bidict({'a': 1, 'b': 2}))[1]", {"ok": True, "value": {"a": 1, "b": 2, "c": 3}}),
    
    # Group 6: Deletion operations (6 tests)
    ("del_key", "(lambda b: (b.__delitem__('a'), dict(b)))(bidict({'a': 1, 'b': 2}))[1]", {"ok": True, "value": {"b": 2}}),
    ("pop_key", "(lambda b: (b.pop('a'), dict(b)))(bidict({'a': 1, 'b': 2}))[1]", {"ok": True, "value": {"b": 2}}),
    ("pop_return", "bidict({'a': 1, 'b': 2}).pop('a')", {"ok": True, "value": 1}),
    ("pop_default", "bidict({'a': 1}).pop('z', 'default')", {"ok": True, "value": "default"}),
    ("popitem_return", "list(bidict({'a': 1}).popitem())", {"ok": True, "value": ["a", 1]}),
    ("clear_result", "(lambda b: (b.clear(), len(b)))(bidict({'a': 1, 'b': 2}))[1]", {"ok": True, "value": 0}),
    
    # Group 7: View operations (6 tests)
    ("keys_list", "sorted(bidict({'b': 2, 'a': 1}).keys())", {"ok": True, "value": ["a", "b"]}),
    ("values_list", "sorted(bidict({'a': 2, 'b': 1}).values())", {"ok": True, "value": [1, 2]}),
    ("items_list", "sorted(bidict({'b': 2, 'a': 1}).items())", {"ok": True, "value": [["a", 1], ["b", 2]]}),
    ("keys_len", "len(bidict({'a': 1, 'b': 2}).keys())", {"ok": True, "value": 2}),
    ("values_contains", "1 in bidict({'a': 1, 'b': 2}).values()", {"ok": True, "value": True}),
    ("items_contains", "('a', 1) in bidict({'a': 1}).items()", {"ok": True, "value": True}),
    
    # Group 8: Properties (8 tests)
    ("len_empty", "len(bidict())", {"ok": True, "value": 0}),
    ("len_one", "len(bidict({'a': 1}))", {"ok": True, "value": 1}),
    ("len_many", "len(bidict({'a': 1, 'b': 2, 'c': 3}))", {"ok": True, "value": 3}),
    ("contains_true", "'a' in bidict({'a': 1, 'b': 2})", {"ok": True, "value": True}),
    ("contains_false", "'z' in bidict({'a': 1, 'b': 2})", {"ok": True, "value": False}),
    ("bool_empty", "bool(bidict())", {"ok": True, "value": False}),
    ("bool_nonempty", "bool(bidict({'a': 1}))", {"ok": True, "value": True}),
    ("copy_independent", "(lambda: (lambda b, c: (c.__setitem__('b', 2), dict(b)))(bidict({'a': 1}), bidict({'a': 1}).copy()))()", {"ok": True, "value": [None, {"a": 1}]}),
    
    # Group 9: Equality and comparison (6 tests)
    ("eq_same", "bidict({'a': 1}) == bidict({'a': 1})", {"ok": True, "value": True}),
    ("eq_different", "bidict({'a': 1}) == bidict({'b': 2})", {"ok": True, "value": False}),
    ("eq_empty", "bidict() == bidict())", {"ok": True, "value": True}),
    ("ne_different", "bidict({'a': 1}) != bidict({'b': 2})", {"ok": True, "value": True}),
    ("ne_same", "bidict({'a': 1}) != bidict({'a': 1})", {"ok": True, "value": False}),
    ("eq_dict", "bidict({'a': 1}) == {'a': 1}", {"ok": True, "value": True}),
    
    # Group 10: Edge cases and errors (8 tests)
    ("duplicate_value_error", "bidict({'a': 1}).__setitem__('b', 1)", {"ok": False, "value": "bidict.ValueDuplicationError"}),
    ("keyerror_access", "bidict({'a': 1})['z']", {"ok": False, "value": "builtins.KeyError"}),
    ("keyerror_del", "bidict({'a': 1}).__delitem__('z')", {"ok": False, "value": "builtins.KeyError"}),
    ("keyerror_pop", "bidict({'a': 1}).pop('z')", {"ok": False, "value": "builtins.KeyError"}),
    ("empty_popitem", "bidict().popitem()", {"ok": False, "value": "builtins.KeyError"}),
    ("inverse_keyerror", "bidict({'a': 1}).inverse[99]", {"ok": False, "value": "builtins.KeyError"}),
    ("inverse_duplicate", "bidict({1: 'a'}).inverse.__setitem__('a', 2)", {"ok": False, "value": "bidict.ValueDuplicationError"}),
    ("update_dup_value", "(lambda b: b.update({'b': 1}))(bidict({'a': 1}))", {"ok": False, "value": "bidict.ValueDuplicationError"}),
]

def execute_script(workspace: Path, code: str):
    """Execute code against candidate bidict and return result."""
    script = f'''
import sys
import json
sys.path.insert(0, str({repr(str(workspace))}))

try:
    from bidict import bidict
    result = eval({repr(code)})
    # Convert to JSON-serializable
    if isinstance(result, (list, tuple)):
        result = list(result)
        if result and isinstance(result[0], tuple):
            result = [list(item) for item in result]
    elif isinstance(result, dict):
        result = dict(result)
    elif hasattr(result, '__dict__') and 'bidict' in str(type(result)):
        result = dict(result)
    print(json.dumps({{"ok": True, "value": result}}))
except Exception as e:
    exc_name = type(e).__module__ + '.' + type(e).__name__
    print(json.dumps({{"ok": False, "value": exc_name}}))
'''
    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0:
        return {"ok": False, "value": f"subprocess-failed: {proc.stderr[:200]}"}
    try:
        return json.loads(proc.stdout.strip().split('\n')[-1])
    except Exception as e:
        return {"ok": False, "value": f"json-parse-error: {str(e)[:100]}"}

def main():
    workspace = Path("/workspace")
    
    leaves = []
    for test_id, code, expected in CASES:
        result = execute_script(workspace, code)
        passed = result == expected
        leaves.append({
            "nodeid": f"test_bidict.py::test_{test_id}",
            "outcome": "passed" if passed else "failed",
            "test_id": test_id,
            "expected": expected,
            "actual": result,
        })
    
    # Output as JSON on last line
    print(json.dumps(leaves))

if __name__ == "__main__":
    assert len(CASES) == 74, f"Expected 74 cases, got {len(CASES)}"
    main()
