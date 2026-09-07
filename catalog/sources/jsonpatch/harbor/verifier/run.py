"""Private deterministic scenarios for the jsonpatch public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/stefankoegl/python-json-patch,
v1.33, immutable revision 1ddce552cd1bdac5db3df931ba3df3bf9dac284c). The
candidate runner executes the script and reads the ``result`` binding.
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
    # apply_patch basic operations
    (
        "apply_patch-add-simple",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'add', 'path': '/baz', 'value': 'qux'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "bar", "baz": "qux"}},
    ),
    (
        "apply_patch-add-preserves-original",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'add', 'path': '/baz', 'value': 'qux'}]\nresult_doc = jsonpatch.apply_patch(doc, patch)\nresult = [doc, result_doc]",
        {"ok": True, "value": [{"foo": "bar"}, {"foo": "bar", "baz": "qux"}]},
    ),
    (
        "apply_patch-add-in-place",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'add', 'path': '/baz', 'value': 'qux'}]\nresult_doc = jsonpatch.apply_patch(doc, patch, in_place=True)\nresult = [doc, result_doc is doc]",
        {"ok": True, "value": [{"foo": "bar", "baz": "qux"}, True]},
    ),
    (
        "apply_patch-remove-simple",
        "import jsonpatch\ndoc = {'foo': 'bar', 'baz': 'qux'}\npatch = [{'op': 'remove', 'path': '/baz'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "bar"}},
    ),
    (
        "apply_patch-replace-simple",
        "import jsonpatch\ndoc = {'foo': 'bar', 'baz': 'qux'}\npatch = [{'op': 'replace', 'path': '/baz', 'value': 'new'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "bar", "baz": "new"}},
    ),
    (
        "apply_patch-move-simple",
        "import jsonpatch\ndoc = {'foo': 'bar', 'baz': 'qux'}\npatch = [{'op': 'move', 'from': '/baz', 'path': '/new'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "bar", "new": "qux"}},
    ),
    (
        "apply_patch-copy-simple",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'copy', 'from': '/foo', 'path': '/baz'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "bar", "baz": "bar"}},
    ),
    (
        "apply_patch-test-success",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'test', 'path': '/foo', 'value': 'bar'}, {'op': 'add', 'path': '/baz', 'value': 'qux'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "bar", "baz": "qux"}},
    ),
    (
        "apply_patch-test-failure",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'test', 'path': '/foo', 'value': 'wrong'}]\ntry:\n    jsonpatch.apply_patch(doc, patch)\n    result = 'no_exception'\nexcept jsonpatch.JsonPatchTestFailed:\n    result = 'JsonPatchTestFailed'",
        {"ok": True, "value": "JsonPatchTestFailed"},
    ),
    (
        "apply_patch-string-patch",
        "import jsonpatch\nimport json\ndoc = {'foo': 'bar'}\npatch_str = json.dumps([{'op': 'add', 'path': '/baz', 'value': 'qux'}])\nresult = jsonpatch.apply_patch(doc, patch_str)",
        {"ok": True, "value": {"foo": "bar", "baz": "qux"}},
    ),
    
    # Array operations
    (
        "apply_patch-array-add-index",
        "import jsonpatch\ndoc = {'numbers': [1, 2, 3]}\npatch = [{'op': 'add', 'path': '/numbers/1', 'value': 99}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"numbers": [1, 99, 2, 3]}},
    ),
    (
        "apply_patch-array-add-append",
        "import jsonpatch\ndoc = {'numbers': [1, 2, 3]}\npatch = [{'op': 'add', 'path': '/numbers/-', 'value': 100}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"numbers": [1, 2, 3, 100]}},
    ),
    (
        "apply_patch-array-remove",
        "import jsonpatch\ndoc = {'numbers': [1, 2, 3]}\npatch = [{'op': 'remove', 'path': '/numbers/1'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"numbers": [1, 3]}},
    ),
    (
        "apply_patch-array-replace",
        "import jsonpatch\ndoc = {'numbers': [1, 2, 3]}\npatch = [{'op': 'replace', 'path': '/numbers/1', 'value': 99}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"numbers": [1, 99, 3]}},
    ),
    
    # Nested operations
    (
        "apply_patch-nested-add",
        "import jsonpatch\ndoc = {'user': {'name': 'Alice', 'settings': {}}}\npatch = [{'op': 'add', 'path': '/user/settings/theme', 'value': 'dark'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"user": {"name": "Alice", "settings": {"theme": "dark"}}}},
    ),
    (
        "apply_patch-nested-remove",
        "import jsonpatch\ndoc = {'user': {'name': 'Alice', 'age': 30}}\npatch = [{'op': 'remove', 'path': '/user/age'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"user": {"name": "Alice"}}},
    ),
    (
        "apply_patch-nested-move",
        "import jsonpatch\ndoc = {'user': {'settings': {'theme': 'dark'}}}\npatch = [{'op': 'move', 'from': '/user/settings/theme', 'path': '/theme'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"user": {"settings": {}}, "theme": "dark"}},
    ),
    (
        "apply_patch-nested-copy",
        "import jsonpatch\ndoc = {'user': {'name': 'Alice'}}\npatch = [{'op': 'copy', 'from': '/user/name', 'path': '/author'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"user": {"name": "Alice"}, "author": "Alice"}},
    ),
    
    # Conflict detection
    (
        "apply_patch-remove-nonexistent",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'remove', 'path': '/baz'}]\ntry:\n    jsonpatch.apply_patch(doc, patch)\n    result = 'no_exception'\nexcept jsonpatch.JsonPatchConflict:\n    result = 'JsonPatchConflict'",
        {"ok": True, "value": "JsonPatchConflict"},
    ),
    (
        "apply_patch-replace-nonexistent",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'replace', 'path': '/baz', 'value': 'qux'}]\ntry:\n    jsonpatch.apply_patch(doc, patch)\n    result = 'no_exception'\nexcept jsonpatch.JsonPatchConflict:\n    result = 'JsonPatchConflict'",
        {"ok": True, "value": "JsonPatchConflict"},
    ),
    (
        "apply_patch-array-out-of-bounds",
        "import jsonpatch\ndoc = {'arr': [1, 2, 3]}\npatch = [{'op': 'remove', 'path': '/arr/10'}]\ntry:\n    jsonpatch.apply_patch(doc, patch)\n    result = 'no_exception'\nexcept jsonpatch.JsonPatchConflict:\n    result = 'JsonPatchConflict'",
        {"ok": True, "value": "JsonPatchConflict"},
    ),
    (
        "apply_patch-move-cyclic",
        "import jsonpatch\ndoc = {'foo': {'x': 1}}\npatch = [{'op': 'move', 'from': '/foo', 'path': '/foo/bar'}]\ntry:\n    jsonpatch.apply_patch(doc, patch)\n    result = 'no_exception'\nexcept jsonpatch.JsonPatchConflict:\n    result = 'JsonPatchConflict'",
        {"ok": True, "value": "JsonPatchConflict"},
    ),
    (
        "apply_patch-copy-nonexistent-source",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'copy', 'from': '/baz', 'path': '/qux'}]\ntry:\n    jsonpatch.apply_patch(doc, patch)\n    result = 'no_exception'\nexcept jsonpatch.JsonPatchConflict:\n    result = 'JsonPatchConflict'",
        {"ok": True, "value": "JsonPatchConflict"},
    ),
    
    # Invalid patch format
    (
        "apply_patch-missing-value",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'add', 'path': '/baz'}]\ntry:\n    jsonpatch.apply_patch(doc, patch)\n    result = 'no_exception'\nexcept jsonpatch.InvalidJsonPatch:\n    result = 'InvalidJsonPatch'",
        {"ok": True, "value": "InvalidJsonPatch"},
    ),
    (
        "apply_patch-invalid-op",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'invalid', 'path': '/baz'}]\ntry:\n    jsonpatch.apply_patch(doc, patch)\n    result = 'no_exception'\nexcept jsonpatch.InvalidJsonPatch:\n    result = 'InvalidJsonPatch'",
        {"ok": True, "value": "InvalidJsonPatch"},
    ),
    
    # Empty patch
    (
        "apply_patch-empty",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = []\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "bar"}},
    ),
    
    # Root document operations
    (
        "apply_patch-root-replace",
        "import jsonpatch\ndoc = {'old': 'doc'}\npatch = [{'op': 'replace', 'path': '', 'value': {'new': 'doc'}}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"new": "doc"}},
    ),
    
    # Unicode
    (
        "apply_patch-unicode-keys",
        "import jsonpatch\ndoc = {'名前': 'Alice'}\npatch = [{'op': 'add', 'path': '/年齢', 'value': 30}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"名前": "Alice", "年齢": 30}},
    ),
    (
        "apply_patch-unicode-values",
        "import jsonpatch\ndoc = {'name': 'Alice'}\npatch = [{'op': 'add', 'path': '/greeting', 'value': '你好'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"name": "Alice", "greeting": "你好"}},
    ),
    
    # Escaped characters in paths
    (
        "apply_patch-escaped-tilde",
        "import jsonpatch\ndoc = {'a~b': 1, 'c': 2}\npatch = [{'op': 'remove', 'path': '/a~0b'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"c": 2}},
    ),
    (
        "apply_patch-escaped-slash",
        "import jsonpatch\ndoc = {'c/d': 2}\npatch = [{'op': 'add', 'path': '/c~1d', 'value': 3}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"c/d": 3}},
    ),
    
    # make_patch function
    (
        "make_patch-simple",
        "import jsonpatch\nsrc = {'foo': 'bar'}\ndst = {'foo': 'bar', 'baz': 'qux'}\npatch = jsonpatch.make_patch(src, dst)\nresult = type(patch).__name__",
        {"ok": True, "value": "JsonPatch"},
    ),
    (
        "make_patch-apply-roundtrip",
        "import jsonpatch\nsrc = {'foo': 'bar', 'num': 1}\ndst = {'foo': 'baz', 'num': 2}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"foo": "baz", "num": 2}},
    ),
    (
        "make_patch-array-changes",
        "import jsonpatch\nsrc = {'numbers': [1, 3, 4, 8]}\ndst = {'numbers': [1, 4, 7]}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"numbers": [1, 4, 7]}},
    ),
    (
        "make_patch-nested-changes",
        "import jsonpatch\nsrc = {'user': {'name': 'Alice', 'age': 30}}\ndst = {'user': {'name': 'Alice', 'age': 31, 'city': 'NYC'}}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"user": {"name": "Alice", "age": 31, "city": "NYC"}}},
    ),
    (
        "make_patch-key-removal",
        "import jsonpatch\nsrc = {'foo': 'bar', 'baz': 'qux', 'num': 1}\ndst = {'foo': 'bar'}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"foo": "bar"}},
    ),
    
    # JsonPatch class
    (
        "JsonPatch-constructor",
        "import jsonpatch\npatch = jsonpatch.JsonPatch([{'op': 'add', 'path': '/foo', 'value': 'bar'}])\nresult = type(patch).__name__",
        {"ok": True, "value": "JsonPatch"},
    ),
    (
        "JsonPatch-apply",
        "import jsonpatch\npatch_obj = jsonpatch.JsonPatch([{'op': 'add', 'path': '/foo', 'value': 'bar'}, {'op': 'remove', 'path': '/baz'}])\nresult = patch_obj.apply({'baz': 'qux'})",
        {"ok": True, "value": {"foo": "bar"}},
    ),
    (
        "JsonPatch-apply-in-place",
        "import jsonpatch\ndoc = {'baz': 'qux'}\npatch_obj = jsonpatch.JsonPatch([{'op': 'add', 'path': '/foo', 'value': 'bar'}])\nresult_doc = patch_obj.apply(doc, in_place=True)\nresult = [doc, result_doc is doc]",
        {"ok": True, "value": [{"baz": "qux", "foo": "bar"}, True]},
    ),
    (
        "JsonPatch-from_string",
        "import jsonpatch\nimport json\npatch_str = json.dumps([{'op': 'add', 'path': '/foo', 'value': 'bar'}])\npatch = jsonpatch.JsonPatch.from_string(patch_str)\nresult = patch.apply({})",
        {"ok": True, "value": {"foo": "bar"}},
    ),
    (
        "JsonPatch-from_diff",
        "import jsonpatch\nsrc = {'foo': 'bar'}\ndst = {'foo': 'baz'}\npatch = jsonpatch.JsonPatch.from_diff(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"foo": "baz"}},
    ),
    (
        "JsonPatch-patch-attribute",
        "import jsonpatch\npatch_obj = jsonpatch.JsonPatch([{'op': 'add', 'path': '/foo', 'value': 'bar'}])\nresult = [type(patch_obj.patch).__name__, len(patch_obj.patch)]",
        {"ok": True, "value": ["list", 1]},
    ),
    (
        "JsonPatch-operations-attribute",
        "import jsonpatch\npatch_obj = jsonpatch.JsonPatch([{'op': 'add', 'path': '/foo', 'value': 'bar'}])\nresult = [type(patch_obj.operations).__name__, len(patch_obj.operations)]",
        {"ok": True, "value": ["list", 1]},
    ),
    (
        "JsonPatch-multiple-operations",
        "import jsonpatch\npatch = jsonpatch.JsonPatch([\n    {'op': 'add', 'path': '/a', 'value': 1},\n    {'op': 'add', 'path': '/b', 'value': 2},\n    {'op': 'add', 'path': '/c', 'value': 3}\n])\nresult = patch.apply({})",
        {"ok": True, "value": {"a": 1, "b": 2, "c": 3}},
    ),
    
    # Deep copy behavior
    (
        "apply_patch-deep-copy-default",
        "import jsonpatch\ndoc = {'nested': {'value': [1, 2, 3]}}\npatch = [{'op': 'add', 'path': '/nested/new', 'value': 'test'}]\nresult_doc = jsonpatch.apply_patch(doc, patch)\nresult = [doc, result_doc == {'nested': {'value': [1, 2, 3], 'new': 'test'}}]",
        {"ok": True, "value": [{"nested": {"value": [1, 2, 3]}}, True]},
    ),
    (
        "apply_patch-copy-independence",
        "import jsonpatch\ndoc = {'original': {'data': [1, 2]}}\npatch = [{'op': 'copy', 'from': '/original', 'path': '/copy'}]\nresult_doc = jsonpatch.apply_patch(doc, patch)\nresult_doc['copy']['data'].append(3)\nresult = result_doc['original']['data']",
        {"ok": True, "value": [1, 2]},
    ),
    
    # Complex multi-operation patches
    (
        "apply_patch-multi-op-complex",
        "import jsonpatch\ndoc = {'user': {'name': 'Alice', 'settings': {'theme': 'dark'}}, 'posts': [1, 2, 3]}\npatch = [\n    {'op': 'move', 'from': '/user/settings/theme', 'path': '/theme'},\n    {'op': 'copy', 'from': '/user/name', 'path': '/author'},\n    {'op': 'remove', 'path': '/posts/1'},\n    {'op': 'test', 'path': '/user/name', 'value': 'Alice'}\n]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"user": {"name": "Alice", "settings": {}}, "posts": [1, 3], "theme": "dark", "author": "Alice"}},
    ),
    
    # Exception hierarchy
    (
        "exception-hierarchy-base",
        "import jsonpatch\nresult = issubclass(jsonpatch.InvalidJsonPatch, jsonpatch.JsonPatchException)",
        {"ok": True, "value": True},
    ),
    (
        "exception-hierarchy-conflict",
        "import jsonpatch\nresult = issubclass(jsonpatch.JsonPatchConflict, jsonpatch.JsonPatchException)",
        {"ok": True, "value": True},
    ),
    (
        "exception-hierarchy-test-failed",
        "import jsonpatch\nresult = issubclass(jsonpatch.JsonPatchTestFailed, jsonpatch.JsonPatchException)",
        {"ok": True, "value": True},
    ),
    
    # Various data types
    (
        "apply_patch-value-null",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'add', 'path': '/null', 'value': None}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "bar", "null": None}},
    ),
    (
        "apply_patch-value-bool",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/flag', 'value': True}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"flag": True}},
    ),
    (
        "apply_patch-value-number",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/pi', 'value': 3.14159}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"pi": 3.14159}},
    ),
    (
        "apply_patch-value-array",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/items', 'value': [1, 2, 3]}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"items": [1, 2, 3]}},
    ),
    (
        "apply_patch-value-object",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/user', 'value': {'name': 'Bob', 'age': 25}}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"user": {"name": "Bob", "age": 25}}},
    ),
    
    # Array edge cases
    (
        "apply_patch-array-first",
        "import jsonpatch\ndoc = {'arr': [1, 2, 3]}\npatch = [{'op': 'add', 'path': '/arr/0', 'value': 0}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [0, 1, 2, 3]}},
    ),
    (
        "apply_patch-array-last-valid-index",
        "import jsonpatch\ndoc = {'arr': [1, 2, 3]}\npatch = [{'op': 'add', 'path': '/arr/3', 'value': 4}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [1, 2, 3, 4]}},
    ),
    (
        "apply_patch-array-empty-append",
        "import jsonpatch\ndoc = {'arr': []}\npatch = [{'op': 'add', 'path': '/arr/-', 'value': 1}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [1]}},
    ),
    (
        "apply_patch-array-remove-last",
        "import jsonpatch\ndoc = {'arr': [1, 2, 3]}\npatch = [{'op': 'remove', 'path': '/arr/2'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [1, 2]}},
    ),
    (
        "apply_patch-array-remove-first",
        "import jsonpatch\ndoc = {'arr': [1, 2, 3]}\npatch = [{'op': 'remove', 'path': '/arr/0'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [2, 3]}},
    ),
    
    # Move operation variants
    (
        "apply_patch-move-to-array",
        "import jsonpatch\ndoc = {'value': 42, 'arr': [1, 2]}\npatch = [{'op': 'move', 'from': '/value', 'path': '/arr/-'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [1, 2, 42]}},
    ),
    (
        "apply_patch-move-array-element",
        "import jsonpatch\ndoc = {'arr': [1, 2, 3, 4]}\npatch = [{'op': 'move', 'from': '/arr/1', 'path': '/arr/3'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [1, 3, 4, 2]}},
    ),
    (
        "apply_patch-move-nested-to-root",
        "import jsonpatch\ndoc = {'outer': {'inner': {'value': 123}}}\npatch = [{'op': 'move', 'from': '/outer/inner/value', 'path': '/extracted'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"outer": {"inner": {}}, "extracted": 123}},
    ),
    
    # Copy operation variants
    (
        "apply_patch-copy-to-array",
        "import jsonpatch\ndoc = {'value': 42, 'arr': [1, 2]}\npatch = [{'op': 'copy', 'from': '/value', 'path': '/arr/-'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"value": 42, "arr": [1, 2, 42]}},
    ),
    (
        "apply_patch-copy-nested",
        "import jsonpatch\ndoc = {'source': {'data': {'x': 1, 'y': 2}}}\npatch = [{'op': 'copy', 'from': '/source/data', 'path': '/target'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"source": {"data": {"x": 1, "y": 2}}, "target": {"x": 1, "y": 2}}},
    ),
    (
        "apply_patch-copy-array",
        "import jsonpatch\ndoc = {'arr': [1, 2, 3]}\npatch = [{'op': 'copy', 'from': '/arr', 'path': '/arr_copy'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [1, 2, 3], "arr_copy": [1, 2, 3]}},
    ),
    
    # Replace operation variants
    (
        "apply_patch-replace-type-change",
        "import jsonpatch\ndoc = {'value': 'string'}\npatch = [{'op': 'replace', 'path': '/value', 'value': 123}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"value": 123}},
    ),
    (
        "apply_patch-replace-array-with-object",
        "import jsonpatch\ndoc = {'data': [1, 2, 3]}\npatch = [{'op': 'replace', 'path': '/data', 'value': {'new': 'structure'}}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"data": {"new": "structure"}}},
    ),
    (
        "apply_patch-replace-nested",
        "import jsonpatch\ndoc = {'outer': {'inner': 'old'}}\npatch = [{'op': 'replace', 'path': '/outer/inner', 'value': 'new'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"outer": {"inner": "new"}}},
    ),
    
    # Test operation variants
    (
        "apply_patch-test-array-value",
        "import jsonpatch\ndoc = {'arr': [1, 2, 3]}\npatch = [{'op': 'test', 'path': '/arr/1', 'value': 2}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [1, 2, 3]}},
    ),
    (
        "apply_patch-test-nested",
        "import jsonpatch\ndoc = {'user': {'name': 'Alice'}}\npatch = [{'op': 'test', 'path': '/user/name', 'value': 'Alice'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"user": {"name": "Alice"}}},
    ),
    (
        "apply_patch-test-null",
        "import jsonpatch\ndoc = {'value': None}\npatch = [{'op': 'test', 'path': '/value', 'value': None}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"value": None}},
    ),
    (
        "apply_patch-test-bool",
        "import jsonpatch\ndoc = {'flag': True}\npatch = [{'op': 'test', 'path': '/flag', 'value': True}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"flag": True}},
    ),
    (
        "apply_patch-test-object",
        "import jsonpatch\ndoc = {'obj': {'a': 1}}\npatch = [{'op': 'test', 'path': '/obj', 'value': {'a': 1}}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"obj": {"a": 1}}},
    ),
    (
        "apply_patch-test-array",
        "import jsonpatch\ndoc = {'arr': [1, 2]}\npatch = [{'op': 'test', 'path': '/arr', 'value': [1, 2]}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"arr": [1, 2]}},
    ),
    
    # Sequential operations
    (
        "apply_patch-sequential-add-remove",
        "import jsonpatch\ndoc = {'a': 1}\npatch = [\n    {'op': 'add', 'path': '/b', 'value': 2},\n    {'op': 'remove', 'path': '/a'}\n]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"b": 2}},
    ),
    (
        "apply_patch-sequential-replace-chain",
        "import jsonpatch\ndoc = {'value': 1}\npatch = [\n    {'op': 'replace', 'path': '/value', 'value': 2},\n    {'op': 'replace', 'path': '/value', 'value': 3},\n    {'op': 'replace', 'path': '/value', 'value': 4}\n]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"value": 4}},
    ),
    (
        "apply_patch-sequential-move-chain",
        "import jsonpatch\ndoc = {'a': {'b': {'c': 123}}}\npatch = [\n    {'op': 'move', 'from': '/a/b/c', 'path': '/a/value'},\n    {'op': 'move', 'from': '/a/value', 'path': '/extracted'}\n]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"a": {"b": {}}, "extracted": 123}},
    ),
    
    # Add operation overwrite behavior (add can replace existing)
    (
        "apply_patch-add-overwrite-existing",
        "import jsonpatch\ndoc = {'foo': 'bar'}\npatch = [{'op': 'add', 'path': '/foo', 'value': 'new'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"foo": "new"}},
    ),
    
    # Edge cases with empty structures
    (
        "apply_patch-add-to-empty-object",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/first', 'value': 'value'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"first": "value"}},
    ),
    (
        "apply_patch-operations-on-empty-doc",
        "import jsonpatch\ndoc = {}\npatch = [\n    {'op': 'add', 'path': '/a', 'value': 1},\n    {'op': 'add', 'path': '/b', 'value': 2}\n]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"a": 1, "b": 2}},
    ),
    
    # Diff optimization behavior
    (
        "make_patch-no-changes",
        "import jsonpatch\nsrc = {'foo': 'bar'}\ndst = {'foo': 'bar'}\npatch = jsonpatch.make_patch(src, dst)\nresult = [type(patch).__name__, len(patch.patch)]",
        {"ok": True, "value": ["JsonPatch", 0]},
    ),
    (
        "make_patch-single-replace",
        "import jsonpatch\nsrc = {'value': 'old'}\ndst = {'value': 'new'}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"value": "new"}},
    ),
    (
        "make_patch-add-multiple-keys",
        "import jsonpatch\nsrc = {'a': 1}\ndst = {'a': 1, 'b': 2, 'c': 3}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"a": 1, "b": 2, "c": 3}},
    ),
    (
        "make_patch-remove-multiple-keys",
        "import jsonpatch\nsrc = {'a': 1, 'b': 2, 'c': 3}\ndst = {'a': 1}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"a": 1}},
    ),
    
    # Array list operations
    (
        "apply_patch-on-list-root",
        "import jsonpatch\ndoc = [1, 2, 3]\npatch = [{'op': 'add', 'path': '/-', 'value': 4}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": [1, 2, 3, 4]},
    ),
    (
        "apply_patch-list-root-remove",
        "import jsonpatch\ndoc = [1, 2, 3]\npatch = [{'op': 'remove', 'path': '/1'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": [1, 3]},
    ),
    (
        "apply_patch-list-root-replace",
        "import jsonpatch\ndoc = [1, 2, 3]\npatch = [{'op': 'replace', 'path': '/1', 'value': 99}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": [1, 99, 3]},
    ),
    
    # Complex nested structures
    (
        "apply_patch-deep-nesting",
        "import jsonpatch\ndoc = {'a': {'b': {'c': {'d': {'e': 'value'}}}}}\npatch = [{'op': 'replace', 'path': '/a/b/c/d/e', 'value': 'new'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"a": {"b": {"c": {"d": {"e": "new"}}}}}},
    ),
    (
        "apply_patch-mixed-nesting",
        "import jsonpatch\ndoc = {'users': [{'name': 'Alice', 'tags': ['admin']}]}\npatch = [{'op': 'add', 'path': '/users/0/tags/-', 'value': 'moderator'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"users": [{"name": "Alice", "tags": ["admin", "moderator"]}]}},
    ),
    
    # Integer keys in objects (treated as strings)
    (
        "apply_patch-integer-key-string",
        "import jsonpatch\ndoc = {'1': 'one', '2': 'two'}\npatch = [{'op': 'add', 'path': '/3', 'value': 'three'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"1": "one", "2": "two", "3": "three"}},
    ),
    
    # Operations preserving structure
    (
        "apply_patch-preserve-unaffected",
        "import jsonpatch\ndoc = {'keep': 'this', 'change': 'me', 'nested': {'keep': 'this too'}}\npatch = [{'op': 'replace', 'path': '/change', 'value': 'changed'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"keep": "this", "change": "changed", "nested": {"keep": "this too"}}},
    ),
    (
        "apply_patch-multiple-paths",
        "import jsonpatch\ndoc = {'a': {'x': 1}, 'b': {'y': 2}}\npatch = [\n    {'op': 'add', 'path': '/a/z', 'value': 3},\n    {'op': 'add', 'path': '/b/w', 'value': 4}\n]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"a": {"x": 1, "z": 3}, "b": {"y": 2, "w": 4}}},
    ),
    
    # Large numbers and precision
    (
        "apply_patch-large-integer",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/large', 'value': 9007199254740991}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"large": 9007199254740991}},
    ),
    (
        "apply_patch-float-precision",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/pi', 'value': 3.141592653589793}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"pi": 3.141592653589793}},
    ),
    
    # Empty string keys
    (
        "apply_patch-empty-string-key",
        "import jsonpatch\ndoc = {'': 'empty key', 'normal': 'value'}\npatch = [{'op': 'replace', 'path': '/', 'value': 'updated'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"": "updated", "normal": "value"}},
    ),
    
    # Whitespace in keys
    (
        "apply_patch-whitespace-key",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/key with spaces', 'value': 'value'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"key with spaces": "value"}},
    ),
    
    # Special characters
    (
        "apply_patch-special-chars",
        "import jsonpatch\ndoc = {}\npatch = [{'op': 'add', 'path': '/key@#$', 'value': 'special'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"key@#$": "special"}},
    ),
    
    # Verify exception types exist
    (
        "exception-types-exist",
        "import jsonpatch\nresult = [\n    hasattr(jsonpatch, 'JsonPatchException'),\n    hasattr(jsonpatch, 'InvalidJsonPatch'),\n    hasattr(jsonpatch, 'JsonPatchConflict'),\n    hasattr(jsonpatch, 'JsonPatchTestFailed')\n]",
        {"ok": True, "value": [True, True, True, True]},
    ),
    
    # Import paths
    (
        "import-main-module",
        "import jsonpatch\nresult = [hasattr(jsonpatch, 'apply_patch'), hasattr(jsonpatch, 'make_patch'), hasattr(jsonpatch, 'JsonPatch')]",
        {"ok": True, "value": [True, True, True]},
    ),
    # Additional scenarios to reach 110
    (
        "JsonPatch-from_diff-no-optimization",
        "import jsonpatch\nsrc = {'a': 1, 'b': 2}\ndst = {'a': 1, 'c': 3}\npatch = jsonpatch.JsonPatch.from_diff(src, dst, optimization=False)\nresult = patch.apply(src)",
        {"ok": True, "value": {"a": 1, "c": 3}},
    ),
    (
        "apply_patch-move-within-same-object",
        "import jsonpatch\ndoc = {'obj': {'a': 1, 'b': 2}}\npatch = [{'op': 'move', 'from': '/obj/a', 'path': '/obj/c'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"obj": {"b": 2, "c": 1}}},
    ),
    (
        "apply_patch-copy-overwrite",
        "import jsonpatch\ndoc = {'source': 'value', 'target': 'old'}\npatch = [{'op': 'copy', 'from': '/source', 'path': '/target'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"source": "value", "target": "value"}},
    ),
    (
        "apply_patch-test-with-subsequent-ops",
        "import jsonpatch\ndoc = {'version': 1, 'data': 'old'}\npatch = [\n    {'op': 'test', 'path': '/version', 'value': 1},\n    {'op': 'replace', 'path': '/data', 'value': 'new'},\n    {'op': 'replace', 'path': '/version', 'value': 2}\n]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"version": 2, "data": "new"}},
    ),
    (
        "apply_patch-array-move",
        "import jsonpatch\ndoc = {'items': ['a', 'b', 'c', 'd']}\npatch = [{'op': 'move', 'from': '/items/0', 'path': '/items/-'}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"items": ["b", "c", "d", "a"]}},
    ),
    (
        "apply_patch-nested-array-operations",
        "import jsonpatch\ndoc = {'matrix': [[1, 2], [3, 4]]}\npatch = [{'op': 'replace', 'path': '/matrix/0/1', 'value': 99}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"matrix": [[1, 99], [3, 4]]}},
    ),
    (
        "make_patch-empty-to-nonempty",
        "import jsonpatch\nsrc = {}\ndst = {'a': 1, 'b': 2}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {"a": 1, "b": 2}},
    ),
    (
        "make_patch-nonempty-to-empty",
        "import jsonpatch\nsrc = {'a': 1, 'b': 2}\ndst = {}\npatch = jsonpatch.make_patch(src, dst)\nresult = patch.apply(src)",
        {"ok": True, "value": {}},
    ),
    (
        "apply_patch-sequential-test-ops",
        "import jsonpatch\ndoc = {'a': 1, 'b': 2, 'c': 3}\npatch = [\n    {'op': 'test', 'path': '/a', 'value': 1},\n    {'op': 'test', 'path': '/b', 'value': 2},\n    {'op': 'test', 'path': '/c', 'value': 3}\n]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"a": 1, "b": 2, "c": 3}},
    ),
    (
        "apply_patch-complex-array-nested",
        "import jsonpatch\ndoc = {'users': [{'id': 1, 'active': False}, {'id': 2, 'active': False}]}\npatch = [{'op': 'replace', 'path': '/users/1/active', 'value': True}]\nresult = jsonpatch.apply_patch(doc, patch)",
        {"ok": True, "value": {"users": [{"id": 1, "active": False}, {"id": 2, "active": True}]}},
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
