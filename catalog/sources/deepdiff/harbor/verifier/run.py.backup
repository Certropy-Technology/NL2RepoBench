#!/usr/bin/env python3
"""
DeepDiff verifier - custom-json-v1 protocol
Tests comprehensive diff scenarios with JSON-serializable expectations
"""

import json
import sys
from typing import Any

# Import the candidate execution client
from nl2repobench.verification.candidate_client import execute_script

# Define test cases: (id, script, expected)
# expected format: {"ok": True/False, "value": <json-serializable>}
# Exceptions: {"ok": False, "value": None, "exception_type": "...", "exception_message": "..."}
CASES: list[tuple[str, str, object]] = [
    # Basic equality and differences
    ("equal_empty_dicts", """
from deepdiff import DeepDiff
result = DeepDiff({}, {}).to_dict()
""", {"ok": True, "value": {}}),
    
    ("equal_simple_dicts", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1, 'b': 2}, {'a': 1, 'b': 2}).to_dict()
""", {"ok": True, "value": {}}),
    
    ("value_changed_simple", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1}, {'a': 2}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']": {"new_value": 2, "old_value": 1}}}}),
    
    ("value_changed_multiple", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1, 'b': 3}, {'a': 2, 'b': 4}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']": {"new_value": 2, "old_value": 1}, "root['b']": {"new_value": 4, "old_value": 3}}}}),
    
    ("dictionary_item_added", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1}, {'a': 1, 'b': 2}).to_dict()
""", {"ok": True, "value": {"dictionary_item_added": ["root['b']"]}}),
    
    ("dictionary_item_removed", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1, 'b': 2}, {'a': 1}).to_dict()
""", {"ok": True, "value": {"dictionary_item_removed": ["root['b']"]}}),
    
    # Type changes - MUST handle serialization
    ("type_change_int_to_str", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1}, {'a': '1'}).to_dict()
if 'type_changes' in result:
    for path, change in result['type_changes'].items():
        change['old_type'] = str(change['old_type'])
        change['new_type'] = str(change['new_type'])
result = result
""", {"ok": True, "value": {"type_changes": {"root['a']": {"old_type": "<class 'int'>", "new_type": "<class 'str'>", "old_value": 1, "new_value": "1"}}}}),
    
    ("type_change_dict_to_list", """
from deepdiff import DeepDiff
result = DeepDiff({'a': {}}, {'a': []}).to_dict()
if 'type_changes' in result:
    for path, change in result['type_changes'].items():
        change['old_type'] = str(change['old_type'])
        change['new_type'] = str(change['new_type'])
result = result
""", {"ok": True, "value": {"type_changes": {"root['a']": {"old_type": "<class 'dict'>", "new_type": "<class 'list'>", "old_value": {}, "new_value": []}}}}),
    
    # List differences
    ("list_equal", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2, 3], [1, 2, 3]).to_dict()
""", {"ok": True, "value": {}}),
    
    ("list_value_changed", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2, 3], [1, 5, 3]).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[1]": {"new_value": 5, "old_value": 2}}}}),
    
    ("list_item_added", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2], [1, 2, 3]).to_dict()
""", {"ok": True, "value": {"iterable_item_added": {"root[2]": 3}}}),
    
    ("list_item_removed", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2, 3], [1, 2]).to_dict()
""", {"ok": True, "value": {"iterable_item_removed": {"root[2]": 3}}}),
    
    ("list_multiple_changes", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2, 3], [1, 5]).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[1]": {"new_value": 5, "old_value": 2}}, "iterable_item_removed": {"root[2]": 3}}}),
    
    # Nested structures
    ("nested_dict_value_changed", """
from deepdiff import DeepDiff
result = DeepDiff({'a': {'b': 1}}, {'a': {'b': 2}}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']['b']": {"new_value": 2, "old_value": 1}}}}),
    
    ("nested_dict_deep", """
from deepdiff import DeepDiff
result = DeepDiff({'a': {'b': {'c': 1}}}, {'a': {'b': {'c': 2}}}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']['b']['c']": {"new_value": 2, "old_value": 1}}}}),
    
    ("nested_list_in_dict", """
from deepdiff import DeepDiff
result = DeepDiff({'a': [1, 2]}, {'a': [1, 3]}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a'][1]": {"new_value": 3, "old_value": 2}}}}),
    
    ("nested_dict_in_list", """
from deepdiff import DeepDiff
result = DeepDiff([{'a': 1}], [{'a': 2}]).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[0]['a']": {"new_value": 2, "old_value": 1}}}}),
    
    # ignore_order parameter
    ("ignore_order_list", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2, 3], [3, 2, 1], ignore_order=True).to_dict()
""", {"ok": True, "value": {}}),
    
    ("ignore_order_list_with_diff", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2, 3], [1, 2, 4], ignore_order=True).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[2]": {"new_value": 4, "old_value": 3}}}}),
    
    ("without_ignore_order", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2, 3], [3, 2, 1], ignore_order=False).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[0]": {"new_value": 3, "old_value": 1}, "root[2]": {"new_value": 1, "old_value": 3}}}}),
    
    # ignore_string_type_changes - MUST handle bytes serialization
    ("string_type_change_default", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 'hello'}, {'a': b'hello'}).to_dict()
if 'type_changes' in result:
    for path, change in result['type_changes'].items():
        if isinstance(change.get('new_value'), bytes):
            change['new_value'] = change['new_value'].decode('utf-8')
        if isinstance(change.get('old_value'), bytes):
            change['old_value'] = change['old_value'].decode('utf-8')
        change['old_type'] = str(change['old_type'])
        change['new_type'] = str(change['new_type'])
result = result
""", {"ok": True, "value": {"type_changes": {"root['a']": {"old_type": "<class 'str'>", "new_type": "<class 'bytes'>", "old_value": "hello", "new_value": "hello"}}}}),
    
    ("ignore_string_type_changes", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 'hello'}, {'a': b'hello'}, ignore_string_type_changes=True).to_dict()
""", {"ok": True, "value": {}}),
    
    # ignore_numeric_type_changes
    ("numeric_type_change_default", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1}, {'a': 1.0}).to_dict()
if 'type_changes' in result:
    for path, change in result['type_changes'].items():
        change['old_type'] = str(change['old_type'])
        change['new_type'] = str(change['new_type'])
result = result
""", {"ok": True, "value": {"type_changes": {"root['a']": {"old_type": "<class 'int'>", "new_type": "<class 'float'>", "old_value": 1, "new_value": 1.0}}}}),
    
    ("ignore_numeric_type_changes", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1}, {'a': 1.0}, ignore_numeric_type_changes=True).to_dict()
""", {"ok": True, "value": {}}),
    
    # ignore_type_in_groups
    ("ignore_type_in_groups_int_float", """
from deepdiff import DeepDiff
result = DeepDiff(1, 1.0, ignore_type_in_groups=[(int, float)]).to_dict()
""", {"ok": True, "value": {}}),
    
    ("ignore_type_in_groups_str_bytes", """
from deepdiff import DeepDiff
result = DeepDiff('test', b'test', ignore_type_in_groups=[(str, bytes)]).to_dict()
""", {"ok": True, "value": {}}),
    
    # exclude_paths
    ("exclude_paths_single", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1, 'b': 2}, {'a': 5, 'b': 6}, exclude_paths=["root['a']"]).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['b']": {"new_value": 6, "old_value": 2}}}}),
    
    ("exclude_paths_multiple", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1, 'b': 2, 'c': 3}, {'a': 5, 'b': 6, 'c': 7}, exclude_paths=["root['a']", "root['b']"]).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['c']": {"new_value": 7, "old_value": 3}}}}),
    
    # significant_digits
    ("significant_digits_default", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1.23456}, {'a': 1.23457}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']": {"new_value": 1.23457, "old_value": 1.23456}}}}),
    
    ("significant_digits_2", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1.23456}, {'a': 1.23457}, significant_digits=2).to_dict()
""", {"ok": True, "value": {}}),
    
    ("significant_digits_5", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1.234567}, {'a': 1.234569}, significant_digits=5).to_dict()
""", {"ok": True, "value": {}}),
    
    # String comparisons
    ("string_equal", """
from deepdiff import DeepDiff
result = DeepDiff("hello", "hello").to_dict()
""", {"ok": True, "value": {}}),
    
    ("string_different", """
from deepdiff import DeepDiff
result = DeepDiff("hello", "world").to_dict()
""", {"ok": True, "value": {"values_changed": {"root": {"new_value": "world", "old_value": "hello"}}}}),
    
    ("ignore_string_case", """
from deepdiff import DeepDiff
result = DeepDiff("Hello", "hello", ignore_string_case=True).to_dict()
""", {"ok": True, "value": {}}),
    
    ("ignore_string_case_false", """
from deepdiff import DeepDiff
result = DeepDiff("Hello", "hello", ignore_string_case=False).to_dict()
""", {"ok": True, "value": {"values_changed": {"root": {"new_value": "hello", "old_value": "Hello"}}}}),
    
    # Boolean comparisons
    ("bool_equal", """
from deepdiff import DeepDiff
result = DeepDiff(True, True).to_dict()
""", {"ok": True, "value": {}}),
    
    ("bool_different", """
from deepdiff import DeepDiff
result = DeepDiff(True, False).to_dict()
""", {"ok": True, "value": {"values_changed": {"root": {"new_value": False, "old_value": True}}}}),
    
    # None comparisons
    ("none_equal", """
from deepdiff import DeepDiff
result = DeepDiff(None, None).to_dict()
""", {"ok": True, "value": {}}),
    
    ("none_to_value", """
from deepdiff import DeepDiff
result = DeepDiff(None, 1).to_dict()
if 'type_changes' in result:
    for path, change in result['type_changes'].items():
        change['old_type'] = str(change['old_type'])
        change['new_type'] = str(change['new_type'])
result = result
""", {"ok": True, "value": {"type_changes": {"root": {"old_type": "<class 'NoneType'>", "new_type": "<class 'int'>", "old_value": None, "new_value": 1}}}}),
    
    ("value_to_none", """
from deepdiff import DeepDiff
result = DeepDiff(1, None).to_dict()
if 'type_changes' in result:
    for path, change in result['type_changes'].items():
        change['old_type'] = str(change['old_type'])
        change['new_type'] = str(change['new_type'])
result = result
""", {"ok": True, "value": {"type_changes": {"root": {"old_type": "<class 'int'>", "new_type": "<class 'NoneType'>", "old_value": 1, "new_value": None}}}}),
    
    # Set comparisons - MUST handle SetOrdered serialization
    ("set_equal", """
from deepdiff import DeepDiff
result = DeepDiff({1, 2, 3}, {1, 2, 3}).to_dict()
""", {"ok": True, "value": {}}),
    
    ("set_item_added", """
from deepdiff import DeepDiff
result = DeepDiff({1, 2}, {1, 2, 3}).to_dict()
if 'set_item_added' in result:
    result['set_item_added'] = list(result['set_item_added'])
result = result
""", {"ok": True, "value": {"set_item_added": ["root[3]"]}}),
    
    ("set_item_removed", """
from deepdiff import DeepDiff
result = DeepDiff({1, 2, 3}, {1, 2}).to_dict()
if 'set_item_removed' in result:
    result['set_item_removed'] = list(result['set_item_removed'])
result = result
""", {"ok": True, "value": {"set_item_removed": ["root[3]"]}}),
    
    # Tuple comparisons
    ("tuple_equal", """
from deepdiff import DeepDiff
result = DeepDiff((1, 2, 3), (1, 2, 3)).to_dict()
""", {"ok": True, "value": {}}),
    
    ("tuple_value_changed", """
from deepdiff import DeepDiff
result = DeepDiff((1, 2, 3), (1, 5, 3)).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[1]": {"new_value": 5, "old_value": 2}}}}),
    
    # Empty structures
    ("empty_list", """
from deepdiff import DeepDiff
result = DeepDiff([], []).to_dict()
""", {"ok": True, "value": {}}),
    
    ("empty_to_non_empty_list", """
from deepdiff import DeepDiff
result = DeepDiff([], [1]).to_dict()
""", {"ok": True, "value": {"iterable_item_added": {"root[0]": 1}}}),
    
    ("non_empty_to_empty_list", """
from deepdiff import DeepDiff
result = DeepDiff([1], []).to_dict()
""", {"ok": True, "value": {"iterable_item_removed": {"root[0]": 1}}}),
    
    # Complex nested structures
    ("complex_nested_1", """
from deepdiff import DeepDiff
t1 = {'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]}
t2 = {'users': [{'name': 'Alice', 'age': 31}, {'name': 'Bob', 'age': 25}]}
result = DeepDiff(t1, t2).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['users'][0]['age']": {"new_value": 31, "old_value": 30}}}}),
    
    ("complex_nested_2", """
from deepdiff import DeepDiff
t1 = {'data': {'items': [1, 2, 3], 'count': 3}}
t2 = {'data': {'items': [1, 2, 3, 4], 'count': 4}}
result = DeepDiff(t1, t2).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['data']['count']": {"new_value": 4, "old_value": 3}}, "iterable_item_added": {"root['data']['items'][3]": 4}}}),
    
    ("complex_nested_3", """
from deepdiff import DeepDiff
t1 = {'a': {'b': {'c': [1, 2, {'d': 'old'}]}}}
t2 = {'a': {'b': {'c': [1, 2, {'d': 'new'}]}}}
result = DeepDiff(t1, t2).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']['b']['c'][2]['d']": {"new_value": "new", "old_value": "old"}}}}),
    
    # List with duplicates
    ("list_with_duplicates", """
from deepdiff import DeepDiff
result = DeepDiff([1, 2, 2, 3], [1, 2, 3, 3]).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[2]": {"new_value": 3, "old_value": 2}}}}),
    
    # Mixed types in lists
    ("mixed_types_list", """
from deepdiff import DeepDiff
result = DeepDiff([1, 'two', 3.0], [1, 'two', 3.0]).to_dict()
""", {"ok": True, "value": {}}),
    
    ("mixed_types_list_changed", """
from deepdiff import DeepDiff
result = DeepDiff([1, 'two', 3.0], [1, 'THREE', 3.0]).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[1]": {"new_value": "THREE", "old_value": "two"}}}}),
    
    # Dictionary with numeric keys
    ("dict_numeric_keys", """
from deepdiff import DeepDiff
result = DeepDiff({1: 'a', 2: 'b'}, {1: 'a', 2: 'c'}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[2]": {"new_value": "c", "old_value": "b"}}}}),
    
    # Multiple operations - verbose_level affects output
    ("multiple_ops_dict", """
from deepdiff import DeepDiff
t1 = {'a': 1, 'b': 2, 'c': 3}
t2 = {'a': 5, 'd': 4}
result = DeepDiff(t1, t2).to_dict()
""", {"ok": True, "value": {"values_changed": {"root": {"new_value": {"a": 5, "d": 4}, "old_value": {"a": 1, "b": 2, "c": 3}}}}}),
    
    ("multiple_ops_list", """
from deepdiff import DeepDiff
t1 = [1, 2, 3, 4]
t2 = [1, 5, 6]
result = DeepDiff(t1, t2).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[1]": {"new_value": 5, "old_value": 2}, "root[2]": {"new_value": 6, "old_value": 3}}, "iterable_item_removed": {"root[3]": 4}}}),
    
    # Negative numbers
    ("negative_numbers", """
from deepdiff import DeepDiff
result = DeepDiff({'a': -5}, {'a': -10}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']": {"new_value": -10, "old_value": -5}}}}),
    
    # Float precision
    ("float_precision_1", """
from deepdiff import DeepDiff
result = DeepDiff(0.1 + 0.2, 0.3).to_dict()
""", {"ok": True, "value": {"values_changed": {"root": {"new_value": 0.3, "old_value": 0.30000000000000004}}}}),
    
    ("float_precision_2", """
from deepdiff import DeepDiff
result = DeepDiff(0.1 + 0.2, 0.3, significant_digits=10).to_dict()
""", {"ok": True, "value": {}}),
    
    # Large numbers
    ("large_numbers", """
from deepdiff import DeepDiff
result = DeepDiff(10**100, 10**100).to_dict()
""", {"ok": True, "value": {}}),
    
    ("large_numbers_diff", """
from deepdiff import DeepDiff
result = DeepDiff(10**100, 10**100 + 1).to_dict()
""", {"ok": True, "value": {"values_changed": {"root": {"new_value": 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001, "old_value": 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000}}}}),
    
    # Special string characters
    ("special_chars_string", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 'hello\\nworld'}, {'a': 'hello\\nworld'}).to_dict()
""", {"ok": True, "value": {}}),
    
    ("unicode_string", """
from deepdiff import DeepDiff
result = DeepDiff({'a': '你好'}, {'a': '你好'}).to_dict()
""", {"ok": True, "value": {}}),
    
    ("unicode_diff", """
from deepdiff import DeepDiff
result = DeepDiff({'a': '你好'}, {'a': '世界'}).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']": {"new_value": "世界", "old_value": "你好"}}}}),
    
    # verbose_level parameter (0 suppresses nested details)
    ("verbose_level_0", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1}, {'a': 2}, verbose_level=0).to_dict()
""", {"ok": True, "value": {}}),
    
    # List of dicts
    ("list_of_dicts_1", """
from deepdiff import DeepDiff
t1 = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
t2 = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bobby'}]
result = DeepDiff(t1, t2).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[1]['name']": {"new_value": "Bobby", "old_value": "Bob"}}}}),
    
    # Dict with list values
    ("dict_with_list_values", """
from deepdiff import DeepDiff
t1 = {'tags': ['python', 'diff']}
t2 = {'tags': ['python', 'comparison']}
result = DeepDiff(t1, t2).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['tags'][1]": {"new_value": "comparison", "old_value": "diff"}}}}),
    
    # Zero values
    ("zero_int", """
from deepdiff import DeepDiff
result = DeepDiff(0, 0).to_dict()
""", {"ok": True, "value": {}}),
    
    ("zero_to_one", """
from deepdiff import DeepDiff
result = DeepDiff(0, 1).to_dict()
""", {"ok": True, "value": {"values_changed": {"root": {"new_value": 1, "old_value": 0}}}}),
    
    # Empty string
    ("empty_string", """
from deepdiff import DeepDiff
result = DeepDiff('', '').to_dict()
""", {"ok": True, "value": {}}),
    
    ("empty_to_non_empty_string", """
from deepdiff import DeepDiff
result = DeepDiff('', 'hello').to_dict()
""", {"ok": True, "value": {"values_changed": {"root": {"new_value": "hello", "old_value": ""}}}}),
    
    # report_repetition parameter
    ("report_repetition_true", """
from deepdiff import DeepDiff
result = DeepDiff([1, 1, 1], [1, 1, 2], report_repetition=True).to_dict()
""", {"ok": True, "value": {"values_changed": {"root[2]": {"new_value": 2, "old_value": 1}}}}),
    
    # max_diffs parameter - stops after finding limit diffs
    ("max_diffs_param", """
from deepdiff import DeepDiff
result = DeepDiff({'a': 1, 'b': 2, 'c': 3}, {'a': 10, 'b': 20, 'c': 30}, max_diffs=2).to_dict()
""", {"ok": True, "value": {"values_changed": {"root['a']": {"new_value": 10, "old_value": 1}}}}),
]

def run_verifier():
    """Run all test cases and output custom-json-v1 format"""
    leaves = []
    
    for test_id, script, expected in CASES:
        try:
            # Execute the candidate script
            actual = execute_script(script)
            
            # Compare results
            if actual == expected:
                status = "passed"
            else:
                status = "failed"
        except Exception as e:
            # Verifier internal error
            status = "failed"
        
        leaves.append({
            "id": test_id,
            "status": status
        })
    
    # Output the final JSON result
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))

if __name__ == "__main__":
    run_verifier()
