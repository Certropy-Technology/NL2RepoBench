# DeepDiff: Deep Difference and Search of Python Objects

## Project Description

DeepDiff is a Python library for comprehensive comparison and search of Python data structures. It recursively examines dictionaries, lists, sets, tuples, and other objects to identify differences, supporting advanced options like ignoring order, type changes, string case sensitivity, and floating-point precision control.

The library is designed for data validation, testing, configuration management, and debugging scenarios where developers need to understand structural changes between two Python objects. It produces detailed diff reports in dictionary format with path-based change descriptions.

This task focuses on the core comparison functionality (DeepDiff class) and does not include serialization-dependent features, third-party integrations, or visual rendering.

## Natural Language Instruction

Build a Python package named `deepdiff` that implements deep comparison of Python data structures.

**Required capabilities:**
1. Compare nested dictionaries, lists, tuples, sets, and mixed structures recursively
2. Detect value changes, type changes, item additions/removals at any depth
3. Support ignore_order for unordered comparison of iterables
4. Provide ignore_string_type_changes and ignore_numeric_type_changes flags
5. Allow excluding specific paths from comparison
6. Support significant_digits for floating-point comparison tolerance
7. Handle ignore_string_case for case-insensitive string comparison
8. Implement max_diffs to limit reported differences
9. Support verbose_level to control output detail (0 suppresses small changes)
10. Produce JSON-serializable dictionary output via to_dict()

The package must be installable via `pip install -e .` and importable as `from deepdiff import DeepDiff`. The primary interface is the DeepDiff class constructor that accepts two objects and comparison options, returning a diff object with a to_dict() method.

**Import structure:** The main export is `DeepDiff` from the `deepdiff` package. Additional exports may include `DeepSearch`, `DeepHash`, `Delta`, but this task focuses on DeepDiff functionality only.

## Supports (Environment Configuration)

- **Language:** Python 3.10+
- **Package Manager:** pip
- **Installation:** `python -m pip install --no-build-isolation --no-deps --no-index -e .`
- **Dependencies:** 
  - `orderly-set>=5.5.0,<6` (for consistent set/dict ordering)
  - `cachebox>=5.2,<6` (for performance optimization)
- **Network Mode:** no-network at runtime
- **Build Backend:** setuptools or hatchling with pyproject.toml

All dependencies are pre-installed in the environment. The candidate installation runs without network access.

## Project Directory Structure

```
workspace/
├── deepdiff/
│   ├── __init__.py          # Re-exports DeepDiff and other public classes
│   ├── diff.py              # Core DeepDiff class implementation
│   ├── helper.py            # Utility functions and constants
│   ├── base.py              # Base classes and comparison logic
│   ├── search.py            # DeepSearch implementation (stub acceptable)
│   ├── deephash.py          # DeepHash implementation (stub acceptable)
│   ├── delta.py             # Delta implementation (stub acceptable)
│   └── path.py              # Path utilities (extract, parse_path functions)
├── pyproject.toml           # Project metadata and dependencies
└── README.md                # Optional documentation
```

The primary module is `deepdiff/diff.py` which contains the DeepDiff class. The `__init__.py` must re-export at minimum: `DeepDiff`, and optionally `DeepSearch`, `DeepHash`, `Delta`, `extract`, `parse_path`, `grep`.

## API Usage Guide

### Core Class: DeepDiff

**Import:** `from deepdiff import DeepDiff`

**Constructor Signature:**
```python
DeepDiff(
    t1,                                    # First object to compare
    t2,                                    # Second object to compare
    ignore_order: bool = False,            # Ignore list/iterable order
    ignore_string_type_changes: bool = False,  # Treat str and bytes as compatible
    ignore_numeric_type_changes: bool = False, # Treat int and float as compatible
    ignore_type_in_groups: list[tuple] = None, # Custom type compatibility groups
    exclude_paths: list[str] = None,       # Paths to exclude from comparison
    significant_digits: int = None,        # Precision for float comparison
    ignore_string_case: bool = False,      # Case-insensitive string comparison
    max_diffs: int = None,                 # Limit number of differences reported
    verbose_level: int = 2,                # Detail level (0=minimal, 2=full)
    **kwargs                               # Additional options
) -> DeepDiff
```

**Returns:** A DeepDiff object containing the comparison results.

**Key Methods:**

#### `to_dict() -> dict`
Returns a JSON-serializable dictionary representation of the differences. The dictionary may contain the following keys (only present when differences exist):

- `values_changed`: Dictionary mapping paths to `{old_value, new_value}` for value changes
- `type_changes`: Dictionary mapping paths to `{old_type, new_type, old_value, new_value}` for type changes
- `dictionary_item_added`: List of paths where dictionary keys were added
- `dictionary_item_removed`: List of paths where dictionary keys were removed
- `iterable_item_added`: Dictionary mapping paths to added values in lists/tuples
- `iterable_item_removed`: Dictionary mapping paths to removed values in lists/tuples
- `set_item_added`: List of paths where set items were added
- `set_item_removed`: List of paths where set items were removed

**Path Format:** Paths use root-relative notation:
- `root` for the top-level object
- `root['key']` for dictionary keys
- `root[0]` for list/tuple indices
- `root['key'][0]['nested']` for nested structures

**Empty Result:** When objects are equal, `to_dict()` returns an empty dictionary `{}`.

### Comparison Behavior

#### Basic Comparison
Compare two dictionaries and detect value changes:
```python
from deepdiff import DeepDiff

diff = DeepDiff({'a': 1, 'b': 2}, {'a': 1, 'b': 3})
result = diff.to_dict()
# result: {'values_changed': {"root['b']": {'old_value': 2, 'new_value': 3}}}
```

Equal objects return empty diff:
```python
diff = DeepDiff({'a': 1}, {'a': 1})
result = diff.to_dict()
# result: {}
```

#### Dictionary Operations
Detect added and removed keys:
```python
diff = DeepDiff({'a': 1}, {'a': 1, 'b': 2})
result = diff.to_dict()
# result: {'dictionary_item_added': ["root['b']"]}

diff = DeepDiff({'a': 1, 'b': 2}, {'a': 1})
result = diff.to_dict()
# result: {'dictionary_item_removed': ["root['b']"]}
```

#### List/Tuple Comparison
Detect value changes and additions/removals by index:
```python
diff = DeepDiff([1, 2, 3], [1, 5, 3])
result = diff.to_dict()
# result: {'values_changed': {'root[1]': {'old_value': 2, 'new_value': 5}}}

diff = DeepDiff([1, 2], [1, 2, 3])
result = diff.to_dict()
# result: {'iterable_item_added': {'root[2]': 3}}
```

#### Nested Structures
Track changes at any depth:
```python
diff = DeepDiff(
    {'users': [{'name': 'Alice', 'age': 30}]},
    {'users': [{'name': 'Alice', 'age': 31}]}
)
result = diff.to_dict()
# result: {'values_changed': {"root['users'][0]['age']": {'old_value': 30, 'new_value': 31}}}
```

#### Type Changes
Detect when values change type:
```python
diff = DeepDiff({'a': 1}, {'a': '1'})
result = diff.to_dict()
# result: {'type_changes': {"root['a']": {
#   'old_type': <class 'int'>, 
#   'new_type': <class 'str'>,
#   'old_value': 1,
#   'new_value': '1'
# }}}
```

**Note:** Type objects in `type_changes` are not JSON-serializable. To make them serializable, convert to strings:
```python
if 'type_changes' in result:
    for path, change in result['type_changes'].items():
        change['old_type'] = str(change['old_type'])
        change['new_type'] = str(change['new_type'])
```

#### Set Comparison
Detect added and removed set members:
```python
diff = DeepDiff({1, 2, 3}, {1, 2, 4})
result = diff.to_dict()
# result: {'set_item_added': ['root[4]'], 'set_item_removed': ['root[3]']}
```

**Note:** Set difference values may be returned as SetOrdered objects (from orderly-set dependency). Convert to lists for JSON serialization:
```python
if 'set_item_added' in result:
    result['set_item_added'] = list(result['set_item_added'])
if 'set_item_removed' in result:
    result['set_item_removed'] = list(result['set_item_removed'])
```

### Comparison Options

#### ignore_order
When True, compares iterables ignoring element order:
```python
diff = DeepDiff([1, 2, 3], [3, 2, 1], ignore_order=True)
result = diff.to_dict()
# result: {} (considered equal)

diff = DeepDiff([1, 2, 3], [3, 2, 1], ignore_order=False)
result = diff.to_dict()
# result: {'values_changed': {'root[0]': ..., 'root[2]': ...}}
```

#### ignore_string_type_changes
When True, treats str and bytes as compatible types:
```python
diff = DeepDiff('hello', b'hello', ignore_string_type_changes=True)
result = diff.to_dict()
# result: {} (considered equal)
```

**Note:** When comparing str and bytes without this flag, bytes values in type_changes must be decoded for JSON serialization:
```python
if isinstance(change.get('new_value'), bytes):
    change['new_value'] = change['new_value'].decode('utf-8')
```

#### ignore_numeric_type_changes
When True, treats int and float as compatible:
```python
diff = DeepDiff(1, 1.0, ignore_numeric_type_changes=True)
result = diff.to_dict()
# result: {} (considered equal)
```

#### ignore_type_in_groups
Custom type compatibility groups:
```python
diff = DeepDiff(1, 1.0, ignore_type_in_groups=[(int, float)])
result = diff.to_dict()
# result: {}

diff = DeepDiff('test', b'test', ignore_type_in_groups=[(str, bytes)])
result = diff.to_dict()
# result: {}
```

#### exclude_paths
Exclude specific paths from comparison:
```python
diff = DeepDiff(
    {'a': 1, 'b': 2, 'c': 3},
    {'a': 5, 'b': 6, 'c': 7},
    exclude_paths=["root['a']", "root['b']"]
)
result = diff.to_dict()
# result: {'values_changed': {"root['c']": {'old_value': 3, 'new_value': 7}}}
```

#### significant_digits
Control floating-point comparison precision:
```python
diff = DeepDiff(1.23456, 1.23457, significant_digits=2)
result = diff.to_dict()
# result: {} (considered equal within 2 significant digits)

diff = DeepDiff(1.23456, 1.23457, significant_digits=5)
result = diff.to_dict()
# result: {} (equal within 5 digits)
```

Special case for floating-point arithmetic:
```python
diff = DeepDiff(0.1 + 0.2, 0.3)
result = diff.to_dict()
# result: {'values_changed': {'root': {'old_value': 0.30000000000000004, 'new_value': 0.3}}}

diff = DeepDiff(0.1 + 0.2, 0.3, significant_digits=10)
result = diff.to_dict()
# result: {} (equal within tolerance)
```

#### ignore_string_case
Case-insensitive string comparison:
```python
diff = DeepDiff("Hello", "hello", ignore_string_case=True)
result = diff.to_dict()
# result: {}

diff = DeepDiff("Hello", "hello", ignore_string_case=False)
result = diff.to_dict()
# result: {'values_changed': {'root': {'old_value': 'Hello', 'new_value': 'hello'}}}
```

#### max_diffs
Limit the number of differences reported:
```python
diff = DeepDiff(
    {'a': 1, 'b': 2, 'c': 3},
    {'a': 10, 'b': 20, 'c': 30},
    max_diffs=1
)
result = diff.to_dict()
# result: {'values_changed': {"root['a']": {'old_value': 1, 'new_value': 10}}}
# (stops after finding 1 difference)
```

**Note:** When max_diffs is reached, a warning may be printed to stderr. The returned dict contains only the differences found before reaching the limit.

#### verbose_level
Control output detail level (default is 2):
- `verbose_level=0`: Minimal output, may suppress detailed change information for small differences
- `verbose_level=2`: Full detailed output (default)

```python
diff = DeepDiff({'a': 1}, {'a': 2}, verbose_level=0)
result = diff.to_dict()
# result: {} (small change suppressed at level 0)

diff = DeepDiff({'a': 1}, {'a': 2}, verbose_level=2)
result = diff.to_dict()
# result: {'values_changed': {"root['a']": {'old_value': 1, 'new_value': 2}}}
```

## Implementation Notes

### Recursive Comparison Strategy
The comparison must traverse both objects recursively, handling cycles and maintaining path information. Use a queue or stack-based approach to track comparison state at each level.

### Path Tracking
Generate path strings in the format `root['key'][index]` as you traverse. These paths must be consistent and unambiguous for nested structures.

### Type Handling
Before comparing values:
1. Check if types match (unless ignore flags permit type compatibility)
2. For containers (dict, list, tuple, set), recurse into elements
3. For primitives, use direct equality with float tolerance if specified

### JSON Serialization Constraints
The output of `to_dict()` must be JSON-serializable:
- Convert Python type objects to strings: `str(type_obj)`
- Convert bytes to strings: `bytes_obj.decode('utf-8')`
- Convert orderly_set.StableSetEq (or similar) to lists: `list(set_obj)`
- Ensure all dictionary keys are strings

### Deterministic Output
Results should be deterministic for the same input. Dictionary iteration order is preserved in Python 3.7+, but be aware that set operations may need consistent ordering (use orderly-set dependency).

### Error Handling
- Invalid path formats: raise ValueError with descriptive message
- Unsupported types: handle gracefully or document limitations
- Circular references: detect and handle to prevent infinite recursion

### Performance Considerations
- Use the cachebox dependency for memoization if comparing large structures repeatedly
- Short-circuit comparison when max_diffs is reached
- Optimize common cases (equal primitives, empty collections)

## Examples

### Example 1: Configuration Validation
```python
from deepdiff import DeepDiff

old_config = {
    'database': {'host': 'localhost', 'port': 5432},
    'features': ['auth', 'logging']
}

new_config = {
    'database': {'host': '192.168.1.10', 'port': 5432},
    'features': ['auth', 'logging', 'caching']
}

diff = DeepDiff(old_config, new_config)
changes = diff.to_dict()
# Detects host change and added feature
```

### Example 2: Test Data Comparison
```python
from deepdiff import DeepDiff

expected = [
    {'id': 1, 'name': 'Alice', 'score': 95.5},
    {'id': 2, 'name': 'Bob', 'score': 87.3}
]

actual = [
    {'id': 1, 'name': 'Alice', 'score': 95.5},
    {'id': 2, 'name': 'Bob', 'score': 87.2}
]

diff = DeepDiff(expected, actual, significant_digits=1)
result = diff.to_dict()
# Empty if scores within 1 significant digit, otherwise shows difference
```

## Error Handling and Boundary Conditions

### Empty Structures
```python
diff = DeepDiff({}, {})
# result: {}

diff = DeepDiff([], [])
# result: {}

diff = DeepDiff(None, None)
# result: {}
```

### None vs. Values
```python
diff = DeepDiff(None, 1)
# result: {'type_changes': {'root': {'old_type': <NoneType>, 'new_type': <int>, ...}}}

diff = DeepDiff({'a': None}, {'a': 1})
# result: {'type_changes': {"root['a']": ...}}
```

### Special Numeric Values
```python
diff = DeepDiff(0, 0)
# result: {}

diff = DeepDiff(-5, -10)
# result: {'values_changed': {'root': {'old_value': -5, 'new_value': -10}}}

diff = DeepDiff(10**100, 10**100)
# result: {}
```

### Unicode and Special Characters
```python
diff = DeepDiff({'text': '你好'}, {'text': '你好'})
# result: {}

diff = DeepDiff({'text': 'hello\nworld'}, {'text': 'hello\nworld'})
# result: {}

diff = DeepDiff('', 'hello')
# result: {'values_changed': {'root': {'old_value': '', 'new_value': 'hello'}}}
```

### Large Differences
When comparing objects with many differences, use max_diffs to prevent excessive output:
```python
diff = DeepDiff(range(1000), range(1000, 2000), max_diffs=10)
# Stops after finding 10 differences
```

## Security

- **Input Validation:** Handle arbitrary Python objects safely without executing code
- **Resource Limits:** Respect max_diffs to prevent memory exhaustion
- **Circular References:** Detect and prevent infinite loops when comparing self-referential structures
- **Side Effects:** Comparison should not modify the input objects (t1, t2)

## Additional Exports (Optional)

The package may export additional classes for compatibility:

```python
from deepdiff import DeepSearch, DeepHash, Delta, extract, parse_path, grep
```

These exports may raise `NotImplementedError` if not implemented, as they are not the focus of this task. The primary requirement is a working DeepDiff implementation.
