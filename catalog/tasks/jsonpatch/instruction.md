# Project Description

Implement a Python library that applies JSON Patches according to RFC 6902. The library provides functionality to apply, create, and manipulate JSON patches - structured descriptions of changes to JSON documents. JSON Patch is a format for describing changes to JSON documents, allowing you to add, remove, replace, move, copy, and test values within JSON structures.

The library must support all six operations defined in RFC 6902: add, remove, replace, move, copy, and test. It should work with both Python dictionaries and lists, handle nested structures, and provide both functional and object-oriented interfaces. The implementation must preserve JSON Patch semantics including pointer resolution, conflict detection, and proper error handling.

# Natural Language Instruction

You are tasked with implementing a complete JSON Patch library in Python that conforms to RFC 6902. The package must be named `jsonpatch` and should be installable via pip as a single-module package.

The library must provide:

1. **Core Functions**: `apply_patch()` and `make_patch()` for applying patches and generating patches from document diffs
2. **Main Class**: `JsonPatch` class that encapsulates a patch and provides methods to apply it
3. **Operation Classes**: Individual operation classes for each RFC 6902 operation type
4. **Exception Hierarchy**: Custom exceptions for different failure modes
5. **CLI Tools**: Two command-line utilities - `jsondiff` for generating patches and `jsonpatch` for applying patches
6. **JSON Pointer Support**: Integration with `jsonpointer` library for path resolution

The package must handle edge cases including: operations on nested structures, array indexing, special path characters, Unicode strings, copy-on-write vs in-place modification, and proper conflict detection for operations that cannot be applied.

# Supports

- **Language**: Python 3.7+
- **Package Manager**: pip
- **Installation**: `pip install -e .` from workspace root
- **Dependencies**: `jsonpointer>=1.9`
- **Test Framework**: unittest (tests.py)
- **Package Type**: Single-module package with CLI scripts
- **NoNetwork**: All operations run offline after installation

# Project Directory Structure

```
workspace/
├── jsonpatch.py           # Main module with all classes and functions
├── setup.py               # Package metadata and installation configuration
├── setup.cfg              # Setup configuration
├── requirements.txt       # Runtime dependencies (jsonpointer>=1.9)
├── requirements-dev.txt   # Development dependencies
├── LICENSE                # BSD-3-Clause license
├── README.md              # Package documentation
├── MANIFEST.in            # Package manifest
├── bin/
│   ├── jsondiff          # CLI tool for generating patches
│   └── jsonpatch         # CLI tool for applying patches
├── tests.py              # Test suite
└── doc/                  # Documentation files
```

# API Usage Guide

## Core Functions

### `apply_patch(doc, patch, in_place=False, pointer_cls=JsonPointer)`

Apply a JSON patch to a document.

**Parameters:**
- `doc` (dict or list): The JSON document to patch
- `patch` (list or str): JSON patch as a list of operation dicts or JSON-encoded string
- `in_place` (bool, optional): If True, modify the document in-place. Default: False (creates a copy)
- `pointer_cls` (type, optional): JSON pointer class to use. Default: JsonPointer

**Returns:**
- dict or list: The patched document

**Raises:**
- `InvalidJsonPatch`: If the patch format is invalid
- `JsonPatchConflict`: If the patch cannot be applied due to conflicts
- `JsonPatchTestFailed`: If a test operation fails

**Example:**
```python
import jsonpatch

doc = {'foo': 'bar'}
patch = [{'op': 'add', 'path': '/baz', 'value': 'qux'}]
result = jsonpatch.apply_patch(doc, patch)
# result: {'foo': 'bar', 'baz': 'qux'}
# doc unchanged: {'foo': 'bar'}

# In-place modification
jsonpatch.apply_patch(doc, patch, in_place=True)
# doc modified: {'foo': 'bar', 'baz': 'qux'}
```

### `make_patch(src, dst, pointer_cls=JsonPointer)`

Generate a JSON patch by comparing two documents.

**Parameters:**
- `src` (dict or list): Source document
- `dst` (dict or list): Destination document
- `pointer_cls` (type, optional): JSON pointer class to use. Default: JsonPointer

**Returns:**
- `JsonPatch`: A patch object that transforms src into dst

**Example:**
```python
import jsonpatch

src = {'foo': 'bar', 'numbers': [1, 3, 4, 8]}
dst = {'baz': 'qux', 'numbers': [1, 4, 7]}
patch = jsonpatch.make_patch(src, dst)
result = patch.apply(src)
# result equals dst
```

## JsonPatch Class

### `JsonPatch(patch, pointer_cls=JsonPointer)`

Main class representing a JSON Patch.

**Parameters:**
- `patch` (list): List of operation dictionaries
- `pointer_cls` (type, optional): JSON pointer class for path resolution

**Class Methods:**

#### `from_string(patch_str, pointer_cls=JsonPointer)`
Create a JsonPatch from a JSON string.

#### `from_diff(src, dst, optimization=True, pointer_cls=JsonPointer)`
Create a patch by comparing two documents. Uses optimization to generate minimal patches.

**Instance Methods:**

#### `apply(obj, in_place=False)`
Apply the patch to a document.

**Attributes:**
- `patch` (list): The list of operations
- `operations` (list): Compiled operation objects

**Example:**
```python
patch_obj = jsonpatch.JsonPatch([
    {'op': 'add', 'path': '/foo', 'value': 'bar'},
    {'op': 'remove', 'path': '/baz'}
])
result = patch_obj.apply({'baz': 'qux'})
# result: {'foo': 'bar'}
```

## Exception Classes

### `JsonPatchException`
Base exception for all JSON Patch errors.

### `InvalidJsonPatch`
Raised when the patch format is invalid (missing required fields, invalid operation type, etc.).

### `JsonPatchConflict`
Raised when a patch operation cannot be applied due to:
- Attempting to add a key that already exists (in non-replace context)
- Attempting to remove a non-existent key or index
- Array index out of bounds
- Moving or copying from non-existent paths
- Attempting to move a path into its own child path

### `JsonPatchTestFailed`
Raised when a test operation fails (the value at path doesn't match expected value).

## Operation Classes

These are internal implementation classes but understanding them helps:

### `PatchOperation`
Abstract base for all operations. Each operation has:
- `location` (str): The JSON pointer path
- `pointer` (JsonPointer): Compiled pointer object
- `operation` (dict): Original operation dictionary

### Concrete Operations

- **`AddOperation`**: Adds a value at the specified path
- **`RemoveOperation`**: Removes the value at the specified path
- **`ReplaceOperation`**: Replaces the value at the specified path
- **`MoveOperation`**: Moves a value from one path to another
- **`CopyOperation`**: Copies a value from one path to another
- **`TestOperation`**: Tests that a value at path matches expected value

Each operation type has its own validation and execution logic.

## CLI Tools

### `jsondiff`

Generate a JSON patch by comparing two JSON files.

**Usage:**
```bash
jsondiff FILE1 FILE2 [--indent N] [-u]
```

**Options:**
- `--indent N`: Indent output by N spaces
- `-u, --preserve-unicode`: Output Unicode characters as-is
- `-v, --version`: Show version

**Exit Code:**
- 0: Files are identical
- 1: Files differ (patch generated)

**Example:**
```bash
jsondiff original.json modified.json > changes.patch
```

### `jsonpatch`

Apply a JSON patch to a JSON file.

**Usage:**
```bash
jsonpatch ORIGINAL [PATCH] [options]
```

**Options:**
- `--indent N`: Indent output by N spaces
- `-b, --backup`: Create backup of original file
- `-i, --in-place`: Modify original file in-place
- `-u, --preserve-unicode`: Output Unicode as-is
- `-v, --version`: Show version

**Input:**
- PATCH file is read from stdin if omitted

**Example:**
```bash
jsonpatch original.json patch.json > result.json
jsonpatch original.json patch.json -i -b  # Modify in-place with backup
cat patch.json | jsonpatch original.json  # Read patch from stdin
```

# Implementation Notes

## Path Resolution

All paths are JSON Pointers (RFC 6901) starting with `/`. Special handling:
- `/` refers to the root document
- `/foo` refers to key "foo" in the root object
- `/foo/0` refers to first element of array at key "foo"
- `/foo/-` refers to the position after the last element of array (for append)
- Escape sequences: `~0` for `~`, `~1` for `/`

## Operation Semantics

### Add Operation
- For objects: adds or replaces the specified key
- For arrays: inserts at the specified index (existing elements shift right)
- Special index `-` means append to the end of array
- Adding to non-existent parent paths raises `JsonPatchConflict`

### Remove Operation
- Removes the value at the specified path
- Attempting to remove non-existent path raises `JsonPatchConflict`
- Array indices must be valid (not out of bounds)

### Replace Operation
- Equivalent to remove followed by add, but atomic
- The path must exist (unlike add which can create)
- Raises `JsonPatchConflict` if path doesn't exist

### Move Operation
- Moves value from `from` path to `path`
- Equivalent to copy + remove on the source, but atomic
- Cannot move a path into its own child (e.g., `/a` to `/a/b`)
- Both source and destination paths must be valid
- Raises `JsonPatchConflict` on invalid paths or cyclic moves

### Copy Operation
- Copies value from `from` path to `path`
- Source must exist; creates destination like add
- Deep copies the value (changes to copy don't affect source)
- Raises `JsonPatchConflict` if source doesn't exist

### Test Operation
- Verifies that the value at `path` equals `value`
- Raises `JsonPatchTestFailed` if values don't match
- Useful for conditional patches and conflict detection
- Value comparison uses standard Python equality

## Copy Semantics

By default, `apply_patch()` operates on a deep copy of the document unless `in_place=True`. This ensures the original document remains unchanged. The `JsonPatch.apply()` method has the same parameter.

## Patch Optimization

When creating patches with `make_patch()` or `JsonPatch.from_diff()`, the library optimizes by:
- Using `replace` instead of `remove` + `add` when possible
- Using `move` instead of `remove` from one location + `add` to another
- Generating minimal patches that achieve the transformation

Set `optimization=False` in `from_diff()` to disable optimization.

## Error Handling

The library uses a hierarchy of exceptions:
- Catch `JsonPatchException` to handle all library errors
- Catch specific exceptions (`InvalidJsonPatch`, `JsonPatchConflict`, `JsonPatchTestFailed`) for precise error handling
- All exceptions provide descriptive messages about what went wrong

## Unicode and String Handling

- Supports Python 2.7 and Python 3.x string types
- Handles Unicode in JSON documents, paths, and values correctly
- CLI tools support `--preserve-unicode` flag to output Unicode as-is

## Mutable vs Immutable Operations

Operations can modify structures in-place or create copies:
- `apply_patch(doc, patch, in_place=False)` creates a copy by default
- `in_place=True` modifies the original document
- The `JsonPatch.apply()` method respects the same parameter
- Useful for performance when the original document is no longer needed

## Array Index Handling

Array indices in paths:
- Must be non-negative integers or the special `-` character
- `-` always means "append" (position after last element)
- Out-of-bounds indices raise `JsonPatchConflict`
- For remove operations, exact index is required
- For add operations, index can be any valid position including one past the end

# Examples

## Basic Patching

```python
import jsonpatch

# Simple add
doc = {'foo': 'bar'}
patch = [{'op': 'add', 'path': '/baz', 'value': 'qux'}]
result = jsonpatch.apply_patch(doc, patch)
# {'foo': 'bar', 'baz': 'qux'}

# Array manipulation
doc = {'numbers': [1, 2, 3]}
patch = [{'op': 'add', 'path': '/numbers/1', 'value': 99}]
result = jsonpatch.apply_patch(doc, patch)
# {'numbers': [1, 99, 2, 3]}

# Append to array
patch = [{'op': 'add', 'path': '/numbers/-', 'value': 100}]
result = jsonpatch.apply_patch(doc, patch)
# {'numbers': [1, 2, 3, 100]}
```

## Creating Patches from Diffs

```python
src = {
    'name': 'John',
    'age': 30,
    'city': 'NYC'
}

dst = {
    'name': 'John',
    'age': 31,
    'city': 'LA',
    'country': 'USA'
}

patch = jsonpatch.make_patch(src, dst)
# Generates operations: replace age, replace city, add country
print(patch.patch)
# [{'op': 'replace', 'path': '/age', 'value': 31},
#  {'op': 'replace', 'path': '/city', 'value': 'LA'},
#  {'op': 'add', 'path': '/country', 'value': 'USA'}]
```

## Complex Operations

```python
doc = {
    'user': {
        'name': 'Alice',
        'settings': {'theme': 'dark'}
    },
    'posts': [1, 2, 3]
}

patch = [
    {'op': 'move', 'from': '/user/settings/theme', 'path': '/theme'},
    {'op': 'copy', 'from': '/user/name', 'path': '/author'},
    {'op': 'remove', 'path': '/posts/1'},
    {'op': 'test', 'path': '/user/name', 'value': 'Alice'}
]

result = jsonpatch.apply_patch(doc, patch)
# {
#     'user': {'name': 'Alice', 'settings': {}},
#     'posts': [1, 3],
#     'theme': 'dark',
#     'author': 'Alice'
# }
```

## String Patch Format

```python
import json

patch_str = '''[
    {"op": "add", "path": "/foo", "value": "bar"},
    {"op": "remove", "path": "/baz"}
]'''

doc = {'baz': 'qux', 'hello': 'world'}
result = jsonpatch.apply_patch(doc, patch_str)
# {'foo': 'bar', 'hello': 'world'}
```

# Error Handling and Boundary Conditions

## Invalid Operations

```python
import jsonpatch

# Missing required field
try:
    patch = jsonpatch.JsonPatch([{'op': 'add', 'path': '/foo'}])  # Missing 'value'
except jsonpatch.InvalidJsonPatch as e:
    print(f"Invalid patch: {e}")

# Invalid operation type
try:
    patch = jsonpatch.JsonPatch([{'op': 'invalid', 'path': '/foo'}])
except jsonpatch.InvalidJsonPatch as e:
    print(f"Invalid op: {e}")
```

## Conflict Scenarios

```python
# Remove non-existent key
doc = {'foo': 'bar'}
patch = [{'op': 'remove', 'path': '/baz'}]
try:
    jsonpatch.apply_patch(doc, patch)
except jsonpatch.JsonPatchConflict as e:
    print(f"Conflict: {e}")

# Array index out of bounds
doc = {'arr': [1, 2, 3]}
patch = [{'op': 'remove', 'path': '/arr/10'}]
try:
    jsonpatch.apply_patch(doc, patch)
except jsonpatch.JsonPatchConflict as e:
    print(f"Out of bounds: {e}")

# Move into own child
patch = [{'op': 'move', 'from': '/foo', 'path': '/foo/bar'}]
try:
    jsonpatch.apply_patch({'foo': {'x': 1}}, patch)
except jsonpatch.JsonPatchConflict as e:
    print(f"Cyclic move: {e}")
```

## Test Operation Failures

```python
doc = {'version': 1}
patch = [
    {'op': 'test', 'path': '/version', 'value': 2},  # Expects 2, but is 1
    {'op': 'replace', 'path': '/version', 'value': 3}
]

try:
    jsonpatch.apply_patch(doc, patch)
except jsonpatch.JsonPatchTestFailed as e:
    print(f"Test failed: {e}")
    # Patch not applied because test failed
```

## Edge Cases

```python
# Empty patch
patch = []
result = jsonpatch.apply_patch({'foo': 'bar'}, patch)
# Returns unchanged: {'foo': 'bar'}

# Root document replacement
patch = [{'op': 'replace', 'path': '', 'value': {'new': 'doc'}}]
result = jsonpatch.apply_patch({'old': 'doc'}, patch)
# {'new': 'doc'}

# Unicode in paths and values
doc = {'名前': 'Alice'}
patch = [{'op': 'add', 'path': '/年齢', 'value': 30}]
result = jsonpatch.apply_patch(doc, patch)
# {'名前': 'Alice', '年齢': 30}

# Escaped characters in paths
doc = {'a~b': 1, 'c/d': 2}
# Path '/a~0b' refers to key 'a~b'
# Path '/c~1d' refers to key 'c/d'
patch = [{'op': 'remove', 'path': '/a~0b'}]
result = jsonpatch.apply_patch(doc, patch)
# {'c/d': 2}
```

## Deep Copy Behavior

```python
import jsonpatch

doc = {'nested': {'value': [1, 2, 3]}}
patch = [{'op': 'add', 'path': '/nested/new', 'value': 'test'}]

# Without in_place: original unchanged
result = jsonpatch.apply_patch(doc, patch, in_place=False)
print(doc)    # {'nested': {'value': [1, 2, 3]}}
print(result) # {'nested': {'value': [1, 2, 3], 'new': 'test'}}

# With in_place: original modified
result = jsonpatch.apply_patch(doc, patch, in_place=True)
print(doc is result)  # True
print(doc)  # {'nested': {'value': [1, 2, 3], 'new': 'test'}}
```
