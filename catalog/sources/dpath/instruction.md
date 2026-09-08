# Project Description

`dpath` is a Python library that provides filesystem-like path manipulation and searching for dictionaries and nested data structures. It enables developers to access, search, modify, and traverse complex nested dictionaries using path strings similar to filesystem paths or XPath expressions. The library supports glob patterns for flexible matching and filtering, making it easy to work with deeply nested configuration files, JSON data, and hierarchical data structures.

The library operates on mutable mappings (dictionaries) and sequences (lists) without requiring specialized data types. It provides both simple path-based access and advanced pattern matching with wildcard support. All operations are performed in-place on the provided objects, with clear semantics for creating, reading, updating, and deleting values at arbitrary depths.

# Natural Language Instruction

Implement a Python package named `dpath` that provides dictionary path manipulation and searching capabilities. The package must:

1. Support path-based access to nested dictionaries and lists using slash-separated paths (e.g., `"a/b/c"`)
2. Provide glob pattern matching with `*` (single level) and `**` (recursive) wildcards
3. Support CRUD operations: get, set, create (new), and delete values at paths
4. Enable searching and filtering across nested structures
5. Implement deep merging of dictionaries with configurable merge strategies
6. Provide a segments module for low-level path segment manipulation
7. Support custom path separators and list/array access via numeric indices
8. Include proper exception types for path errors and invalid operations
9. Allow filtering operations via callback functions
10. Support both string paths and list-of-segments paths

The package name is `dpath`, the import name is `dpath`, and it must be installable via pip with a standard `setup.py`.

# Supports (Environment Configuration)

- Python: 3.7+
- Package Manager: pip
- Build System: setuptools (legacy setup.py)
- Runtime Dependencies: None (uses only Python standard library)
- Installation: `pip install .` or `pip install -e .`
- Testing: pytest (for development/testing only)
- No network access required during runtime

# Project Directory Structure

```
workspace/
├── setup.py
├── dpath/
│   ├── __init__.py
│   ├── util.py
│   ├── segments.py
│   ├── exceptions.py
│   ├── types.py
│   ├── options.py
│   ├── version.py
│   └── py.typed
```

# API Usage Guide

## Module: `dpath`

The root module provides the main API functions for dictionary path operations.

### `get(obj, glob, separator="/", default=<sentinel>) -> Any`

Get the value at the path indicated by glob. If the glob matches exactly one leaf, return that value. If the glob matches multiple leaves, raise ValueError. If the path is not found and no default is provided, raise KeyError.

- **Parameters:**
  - `obj` (MutableMapping): The dictionary to search
  - `glob` (str | Sequence[str]): Path glob pattern or list of segments
  - `separator` (str): Path separator character (default: "/")
  - `default` (Any): Value to return if path not found
- **Returns:** The value at the matched path
- **Raises:**
  - `KeyError` if path not found and no default provided
  - `ValueError` if glob matches multiple leaves
- **Special cases:**
  - `get(obj, "/")` returns the entire object
  - `get(obj, [])` returns the entire object
  - Numeric string indices access list elements: `"a/0"` accesses first element of list at key 'a'
- **Example:**
  ```python
  import dpath
  obj = {'a': {'b': {'c': 1}}}
  dpath.get(obj, 'a/b/c')  # Returns: 1
  dpath.get(obj, 'a/*/c')  # Returns: 1 (glob matches single path)
  dpath.get(obj, 'missing', default=42)  # Returns: 42
  ```

### `search(obj, glob, yielded=False, separator="/", afilter=None, dirs=True) -> dict | Generator`

Search for all paths matching the glob pattern and return a dictionary containing the matched keys and values. If `yielded=True`, return a generator of (path, value) tuples instead.

- **Parameters:**
  - `obj` (MutableMapping): The dictionary to search
  - `glob` (str | Sequence[str]): Path glob pattern (supports *, **, [...])
  - `yielded` (bool): If True, yield tuples instead of building dict
  - `separator` (str): Path separator character
  - `afilter` (Callable[[Any], bool] | None): Filter function for values
  - `dirs` (bool): If False, exclude intermediate directories from results
- **Returns:** Dictionary with matched paths or generator of (path_string, value) tuples
- **Glob patterns:**
  - `*` matches any key at a single level
  - `**` matches zero or more levels recursively
  - `[abc]` matches any character in the bracket set
  - `?` matches any single character
- **Example:**
  ```python
  import dpath
  obj = {'a': {'b': 1, 'c': 2}}
  dpath.search(obj, 'a/*')  # Returns: {'a': {'b': 1, 'c': 2}}
  dpath.search(obj, '**')  # Returns: entire nested structure
  
  # With filter
  dpath.search(obj, 'a/*', afilter=lambda x: x > 1)  # Returns: {'a': {'c': 2}}
  
  # Yielded mode
  list(dpath.search(obj, 'a/*', yielded=True))  # Returns: [('a/b', 1), ('a/c', 2)]
  ```

### `values(obj, glob, separator="/", afilter=None, dirs=True) -> list`

Return a list of all values that match the glob pattern. Equivalent to extracting values from search() results.

- **Parameters:** Same as search()
- **Returns:** List of values (not paths)
- **Example:**
  ```python
  import dpath
  obj = {'a': {'b': 1, 'c': 2, 'd': 3}}
  dpath.values(obj, 'a/*')  # Returns: [1, 2, 3] (order may vary)
  ```

### `new(obj, path, value, separator="/", creator=None) -> MutableMapping`

Create a new path in the object and set it to value. Unlike `set()`, this creates missing intermediate keys. The path is NOT treated as a glob; any glob characters become literal key names.

- **Parameters:**
  - `obj` (MutableMapping): The dictionary to modify
  - `path` (str | Sequence[PathSegment]): Path to create (not a glob)
  - `value` (Any): Value to set at the path
  - `separator` (str): Path separator character
  - `creator` (Callable | None): Custom creator function for intermediate keys
- **Returns:** The modified object
- **Behavior:**
  - Creates nested dictionaries for missing keys by default
  - Empty string keys are allowed (they create a key named "")
  - Leading separator is stripped: `"/a/b"` becomes `"a/b"`
- **Example:**
  ```python
  import dpath
  obj = {}
  dpath.new(obj, 'a/b/c', 42)
  # obj is now: {'a': {'b': {'c': 42}}}
  
  obj = {'a': {'x': 1}}
  dpath.new(obj, 'a/b/c', 99)
  # obj is now: {'a': {'x': 1, 'b': {'c': 99}}}
  ```

### `set(obj, glob, value, separator="/", afilter=None) -> int`

Set all existing paths matching the glob to value. Does NOT create new paths. Returns the count of modified entries.

- **Parameters:**
  - `obj` (MutableMapping): The dictionary to modify
  - `glob` (str | Sequence[str]): Path glob pattern
  - `value` (Any): Value to set for all matching paths
  - `separator` (str): Path separator character
  - `afilter` (Callable[[Any], bool] | None): Only set values that pass the filter
- **Returns:** Integer count of values changed
- **Example:**
  ```python
  import dpath
  obj = {'a': {'b': 1, 'c': 2}}
  count = dpath.set(obj, 'a/*', 99)
  # count is 2, obj is now: {'a': {'b': 99, 'c': 99}}
  
  # With filter
  obj = {'a': {'b': 1, 'c': 2, 'd': 3}}
  count = dpath.set(obj, 'a/*', 0, afilter=lambda x: x > 1)
  # count is 2, obj is now: {'a': {'b': 1, 'c': 0, 'd': 0}}
  ```

### `delete(obj, glob, separator="/", afilter=None) -> int`

Delete all paths matching the glob pattern. Returns the count of deleted entries. Raises PathNotFound if no paths match.

- **Parameters:**
  - `obj` (MutableMapping): The dictionary to modify
  - `glob` (str | Sequence[str]): Path glob pattern
  - `separator` (str): Path separator character
  - `afilter` (Callable[[Any], bool] | None): Only delete values that pass the filter
- **Returns:** Integer count of deleted entries
- **Raises:** `PathNotFound` if no matching paths found
- **List deletion behavior:**
  - Deleting the last element removes it completely
  - Deleting a middle element sets it to None (preserves indices)
- **Example:**
  ```python
  import dpath
  from dpath.exceptions import PathNotFound
  
  obj = {'a': {'b': 1, 'c': 2}}
  count = dpath.delete(obj, 'a/b')
  # count is 1, obj is now: {'a': {'c': 2}}
  
  # List deletion
  obj = {'a': [1, 2, 3]}
  dpath.delete(obj, 'a/2')  # Deletes last element
  # obj is now: {'a': [1, 2]}
  
  obj = {'a': [1, 2, 3, 4]}
  dpath.delete(obj, 'a/1')  # Deletes middle element
  # obj is now: {'a': [1, None, 3, 4]}
  ```

### `merge(dst, src, separator="/", afilter=None, flags=MergeType.ADDITIVE) -> MutableMapping`

Recursively merge src into dst. Like dict.update() but performs deep merging of nested structures.

- **Parameters:**
  - `dst` (MutableMapping): Destination dictionary (modified in place)
  - `src` (MutableMapping): Source dictionary to merge from
  - `separator` (str): Path separator for filter operations
  - `afilter` (Callable[[Any], bool] | None): Only merge values that pass filter
  - `flags` (MergeType): Merge behavior flags (can be OR'ed together)
- **Returns:** The modified dst dictionary
- **Warning:** merge() creates references, not deep copies. Source lists/dicts are referenced in destination.
- **Flags:**
  - `MergeType.ADDITIVE`: Concatenate lists (default)
  - `MergeType.REPLACE`: Replace lists instead of concatenating
  - `MergeType.TYPESAFE`: Raise TypeError if merging incompatible types
- **Example:**
  ```python
  import dpath
  from dpath import MergeType
  
  dst = {'a': {'b': 1}}
  src = {'a': {'c': 2}}
  dpath.merge(dst, src)
  # dst is now: {'a': {'b': 1, 'c': 2}}
  
  # List merging
  dst = {'a': [1, 2]}
  src = {'a': [3, 4]}
  dpath.merge(dst, src, flags=MergeType.ADDITIVE)
  # dst is now: {'a': [1, 2, 3, 4]}
  
  dpath.merge(dst, src, flags=MergeType.REPLACE)
  # dst is now: {'a': [3, 4]}
  
  # Type safety
  dst = {'a': 1}
  src = {'a': 'string'}
  dpath.merge(dst, src, flags=MergeType.TYPESAFE)  # Raises TypeError
  ```

## Enum: `MergeType`

Flags for controlling merge behavior. These are IntFlag enum members that can be combined with bitwise OR.

- **MergeType.ADDITIVE**: List objects are concatenated (default behavior)
- **MergeType.REPLACE**: Lists are replaced instead of concatenated
- **MergeType.TYPESAFE**: Raise TypeError when merging incompatible types

**Example:**
```python
from dpath import MergeType

# Combine flags
flags = MergeType.ADDITIVE | MergeType.TYPESAFE
dpath.merge(dst, src, flags=flags)
```

## Module: `dpath.segments`

Low-level segment-based operations. Paths are represented as sequences of segments (keys) rather than strings.

### `get(obj, segments) -> Any`

Get the value at the path indicated by segments.

- **Parameters:**
  - `obj`: The object to traverse
  - `segments` (Sequence[PathSegment]): List of keys to follow
- **Returns:** Value at the path
- **Raises:** `PathNotFound` if path doesn't exist
- **Example:**
  ```python
  import dpath.segments as seg
  obj = {'a': {'b': 1}}
  seg.get(obj, ['a', 'b'])  # Returns: 1
  ```

### `has(obj, segments) -> bool`

Check if a path exists in the object.

- **Parameters:**
  - `obj`: The object to check
  - `segments` (Sequence[PathSegment]): Path segments
- **Returns:** True if path exists, False otherwise

### `set(obj, segments, value, creator=None, hints=()) -> None`

Set the value at the path, creating intermediate keys if needed.

- **Parameters:**
  - `obj`: The object to modify
  - `segments` (Sequence[PathSegment]): Path segments
  - `value`: Value to set
  - `creator` (Callable | None): Custom creator function
  - `hints` (Sequence[Tuple[PathSegment, type]]): Type hints for creation

### `leaf(thing) -> bool`

Return True if thing is a leaf value (not traversable).

- **Leaf types:** bytes, str, int, float, bool, None
- **Example:**
  ```python
  import dpath.segments as seg
  seg.leaf(42)  # True
  seg.leaf("text")  # True
  seg.leaf({})  # False
  seg.leaf([])  # False
  ```

### `leafy(thing) -> bool`

Like leaf(), but also treats empty containers as leaves.

- **Returns:** True for leaf values OR empty dict/list/tuple

### `walk(obj, location=()) -> Generator[Tuple[Tuple[PathSegment, ...], Any], None, None]`

Yield all (path_segments, value) pairs in breadth-first order.

- **Example:**
  ```python
  import dpath.segments as seg
  obj = {'a': {'b': 1}}
  for path, value in seg.walk(obj):
      print(path, value)
  # Output: ('a',) {'b': 1}
  #         ('a', 'b') 1
  ```

### `match(segments, glob) -> bool`

Check if segments match a glob pattern.

- **Parameters:**
  - `segments` (Sequence[PathSegment]): Path to test
  - `glob` (Sequence[PathSegment]): Glob pattern
- **Returns:** True if segments match the glob
- **Supports:** `*`, `**`, character classes `[...]`, and `?` wildcards

### `int_str(segment) -> str | PathSegment`

Convert integer segments to strings; pass through other segments unchanged.

### `make_walkable(node) -> Iterator[Tuple[PathSegment, Any]]`

Return an iterator of (key, value) pairs suitable for walking the node.

- **For dicts:** Returns `node.items()`
- **For sequences:** Returns `zip(indices, values)` with ListIndex objects
- **Otherwise:** Returns empty iterator

## Module: `dpath.exceptions`

### `PathNotFound(Exception)`

Raised when one or more elements of a requested path don't exist.

### `InvalidKeyName(Exception)`

Raised when a key contains invalid characters (e.g., separator in key name when not using list paths).

### `InvalidGlob(Exception)`

Raised when a glob pattern is malformed.

### `FilteredValue(Exception)`

Raised when unable to return a value because it was rejected by a filter.

## Module: `dpath.types`

Type aliases and helper types for type hinting.

### `PathSegment = Union[int, str, bytes]`

Type for individual path components.

### `Path = Union[str, Sequence[PathSegment]]`

Type for path parameters (string or list).

### `Glob = Union[str, Sequence[str]]`

Type for glob patterns.

### `Filter = Callable[[Any], bool]`

Type for filter functions.

### `Creator = Callable[[Union[MutableMapping, List], Path, int, Optional[Hints]], None]`

Type for creator functions used by new() and set().

### `Hints = Sequence[Tuple[PathSegment, type]]`

Type hints for path creation.

### `MergeType(IntFlag)`

Enum class for merge flags (also exported from main module).

### `ListIndex(int)`

Special int subclass that supports negative index comparison for list access.

## Module: `dpath.options`

Global configuration options.

### `ALLOW_EMPTY_STRING_KEYS`

Boolean flag (default: False). When False, empty string keys ("") are still allowed but operations that walk the structure will raise InvalidKeyName when certain conditions are met.

## Module: `dpath.version`

### `VERSION`

String constant containing the package version ("2.2.0").

# Implementation Notes

## Path Resolution

- Paths can be strings with separators or lists of segments
- String paths: leading separator is stripped, then split by separator
- List paths: each element is a literal key (separator not interpreted)
- Numeric string keys in lists are converted to integers for indexing
- Negative indices work with lists: `-1` accesses last element

## Glob Semantics

- `*` matches any single key at the current level
- `**` matches zero or more levels recursively
- `[abc]` matches any single character in the set (uses fnmatch)
- `?` matches any single character (uses fnmatch)
- Glob matching uses fnmatch.fnmatchcase internally (case-sensitive)

## Mutability

All modification operations (new, set, delete, merge) modify the input object in place and return either the object or a count of modifications. No copies are made.

## Merge Behavior

The merge() function creates references, not deep copies. If you merge two dictionaries with list values, both the source and destination will share references to the same list objects after the merge. Use copy.deepcopy() on the source if you need independent copies.

## Determinism

- Search results maintain insertion order (Python 3.7+ dict ordering)
- Walk order is breadth-first, right-to-left for sequences
- Values returned by values() maintain the order from search()

# Examples

## Basic Path Access

```python
import dpath

# Simple get
data = {'users': {'alice': {'age': 30}}}
age = dpath.get(data, 'users/alice/age')  # 30

# Create nested path
config = {}
dpath.new(config, 'database/host', 'localhost')
dpath.new(config, 'database/port', 5432)
# config = {'database': {'host': 'localhost', 'port': 5432}}
```

## Pattern Matching

```python
import dpath

data = {
    'users': {
        'alice': {'age': 30, 'role': 'admin'},
        'bob': {'age': 25, 'role': 'user'}
    }
}

# Find all ages
ages = dpath.values(data, 'users/*/age')  # [30, 25]

# Search with glob
admins = dpath.search(data, 'users/*', afilter=lambda u: u.get('role') == 'admin')
# {'users': {'alice': {'age': 30, 'role': 'admin'}}}

# Recursive search
all_values = dpath.search(data, '**')  # Returns entire structure
```

## Modification

```python
import dpath

# Set multiple values
data = {'a': {'b': 1, 'c': 2, 'd': 3}}
dpath.set(data, 'a/*', 0)  # Sets all values under 'a' to 0

# Delete with pattern
data = {'logs': {'error': [...], 'warning': [...], 'info': [...]}}
dpath.delete(data, 'logs/[ei]*')  # Deletes 'error' and 'info' keys
```

## List Operations

```python
import dpath

# Access list elements
data = {'items': [10, 20, 30]}
value = dpath.get(data, 'items/1')  # 20
value = dpath.get(data, ['items', -1])  # 30 (last element)

# Modify list
dpath.set(data, 'items/0', 99)  # {'items': [99, 20, 30]}
```

# Error Handling and Boundary Conditions

## Missing Paths

```python
import dpath

obj = {'a': 1}

# With default
value = dpath.get(obj, 'missing/path', default=None)  # Returns: None

# Without default
try:
    value = dpath.get(obj, 'missing/path')
except KeyError:
    print("Path not found")
```

## Multiple Matches

```python
import dpath

obj = {'a': {'b': 1, 'c': 2}}

# get() with multiple matches raises ValueError
try:
    value = dpath.get(obj, 'a/*')
except ValueError:
    print("Glob matched multiple paths")

# Use search() or values() for multiple results
results = dpath.search(obj, 'a/*')
```

## Empty Containers

```python
import dpath

obj = {'a': [], 'b': {}}

# Empty containers are leaf values
dpath.get(obj, 'a')  # Returns: []
dpath.get(obj, 'b')  # Returns: {}
```

## Type Safety in Merge

```python
import dpath
from dpath import MergeType

dst = {'config': {'timeout': 30}}
src = {'config': {'timeout': "30"}}  # String instead of int

# Without TYPESAFE, src overwrites dst
dpath.merge(dst, src)  # Works, dst['config']['timeout'] = "30"

# With TYPESAFE, raises TypeError
dst = {'config': {'timeout': 30}}
try:
    dpath.merge(dst, src, flags=MergeType.TYPESAFE)
except TypeError:
    print("Type mismatch detected")
```

## Custom Separators

```python
import dpath

obj = {}
dpath.new(obj, 'a.b.c', 42, separator='.')
# obj = {'a': {'b': {'c': 42}}}

# Useful when keys contain slashes
obj = {'url': {'http://example.com': {'status': 200}}}
dpath.get(obj, ['url', 'http://example.com', 'status'])  # 200
```
