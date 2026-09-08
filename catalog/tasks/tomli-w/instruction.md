# Tomli-W: A TOML Writer Library

## Project Description

Tomli-W is a Python library for writing TOML (Tom's Obvious, Minimal Language) documents. It serves as a write-only counterpart to the Tomli TOML parser and is fully compatible with TOML v1.0.0 specification. The library takes Python data structures (dictionaries, lists, strings, numbers, dates, etc.) and serializes them into valid TOML format strings or files.

The library is designed for applications that need to generate configuration files, write structured data in TOML format, or perform round-trip operations with TOML documents. It does not support preserving comments or custom whitespace beyond configurable indentation.

## Natural Language Instruction

You are tasked with implementing a complete Python library called `tomli_w` that writes TOML v1.0.0 documents from Python data structures. The package must:

1. Provide a `dumps()` function that serializes a Python mapping to a TOML string
2. Provide a `dump()` function that writes a Python mapping to a binary file object
3. Support all standard TOML types: strings, integers, floats, booleans, dates, times, datetimes, arrays, tables, inline tables, and array-of-tables
4. Handle special numeric values: NaN, positive infinity, negative infinity
5. Support Decimal type from the decimal module
6. Correctly escape strings according to TOML basic string rules
7. Format arrays with configurable indentation
8. Optionally write multi-line strings when newlines are present
9. Preserve the insertion order of dictionary keys (not sort them)
10. Generate syntactically valid TOML output

The package name is `tomli_w`, installed as `tomli-w`. The public API is exposed through `tomli_w.dump()` and `tomli_w.dumps()`. The implementation must handle edge cases like bare keys, quoted keys, inline tables, nested structures, and proper escaping.

## Environment Configuration

- **Language**: Python 3.9+
- **Package Manager**: pip with flit_core as build backend
- **Installation**: The package uses `pyproject.toml` with flit_core for building
- **Dependencies**: No runtime dependencies (pure Python)
- **Development Dependencies**: pytest, tomli (for testing round-trips)

## Project Directory Structure

```
workspace/
├── pyproject.toml
├── README.md
├── LICENSE
└── src/
    └── tomli_w/
        ├── __init__.py
        ├── _writer.py
        └── py.typed
```

## API Usage Guide

### Module: tomli_w

**Import Path**: `import tomli_w`

The module exports two main functions and a version string.

#### Function: dumps

**Signature**:
```python
def dumps(
    obj: Mapping[str, Any],
    /,
    *,
    multiline_strings: bool = False,
    indent: int = 4
) -> str
```

**Parameters**:
- `obj`: A mapping (dict-like object) to serialize. Keys must be strings. Values can be: str, int, float, bool, datetime.date, datetime.time, datetime.datetime, list, tuple, dict, or decimal.Decimal.
- `multiline_strings`: Optional keyword-only boolean (default: False). If True, strings containing newlines will be written as multi-line strings (triple-quoted). If False, newlines are escaped.
- `indent`: Optional keyword-only integer (default: 4). The number of spaces to use for indenting array elements. Must be non-negative.

**Returns**: A string containing the TOML representation.

**Raises**:
- `TypeError`: If obj contains non-serializable types or invalid key types
- `ValueError`: If indent is negative, or if a time object has timezone info

**Behavior**:
- Tables are written in the order they appear in the input mapping
- Top-level key-value pairs are written first, followed by tables
- Arrays are formatted with each element on its own line, indented
- Inline tables are used for small mappings within arrays or values
- Keys are written bare if they contain only alphanumeric characters, hyphens, and underscores; otherwise quoted
- Special floats (NaN, Infinity) are written as `nan`, `inf`, `-inf`
- Decimal values are formatted with decimal point if they don't have one

**Example**:
```python
import tomli_w

doc = {"title": "Example", "count": 42, "enabled": True}
toml_string = tomli_w.dumps(doc)
# Returns: 'title = "Example"\ncount = 42\nenabled = true\n'
```

#### Function: dump

**Signature**:
```python
def dump(
    obj: Mapping[str, Any],
    fp: IO[bytes],
    /,
    *,
    multiline_strings: bool = False,
    indent: int = 4
) -> None
```

**Parameters**:
- `obj`: A mapping to serialize (same requirements as dumps)
- `fp`: A binary file-like object with a `write(bytes)` method
- `multiline_strings`: Same as dumps
- `indent`: Same as dumps

**Returns**: None (writes to file)

**Raises**: Same as dumps

**Behavior**: Identical to dumps(), but writes encoded UTF-8 bytes directly to the file object instead of returning a string.

**Example**:
```python
import tomli_w

doc = {"name": "config", "version": 1}
with open("config.toml", "wb") as f:
    tomli_w.dump(doc, f)
```

#### Attribute: __version__

**Type**: str

The version string of the library (e.g., "1.2.0").

#### Attribute: __all__

**Type**: tuple of str

Exported names: `("dumps", "dump")`

## Implementation Notes

### String Formatting

- Basic strings are enclosed in double quotes
- Characters outside the printable ASCII range (except tab) must be escaped
- Control characters use compact escapes when available: `\b`, `\n`, `\f`, `\r`, `\"`, `\\`
- Other characters use Unicode escapes: `\uXXXX`
- Bare keys (table/inline-table keys) can only contain `[a-zA-Z0-9_-]`
- Empty strings and strings with special characters must be quoted

### Multi-line String Handling

When `multiline_strings=False` (default):
- All newlines are escaped as `\n` or `\r\n` as appropriate
- The output can be parsed back to the exact same bytes

When `multiline_strings=True`:
- Strings containing `\n` are written as triple-quoted multi-line strings
- `\r\n` sequences are normalized to `\n`
- This is lossy for `\r\n` vs `\n` but more readable

### Table and Array Formatting

- Top-level literal values are written first
- Tables and array-of-tables follow
- Nested tables use dotted notation: `[parent.child]`
- Array-of-tables use double brackets: `[[array_name]]`
- Inline tables use single-line format: `{ key = value, key2 = value2 }`
- Arrays use multi-line format with configurable indentation:
  ```toml
  array = [
      "item1",
      "item2",
  ]
  ```
- Trailing comma is included after the last array element

### Type Mapping

Python to TOML type conversion:
- `bool` → TOML boolean (`true`, `false`)
- `int` → TOML integer
- `float` → TOML float (including `nan`, `inf`, `-inf`)
- `str` → TOML string (basic or multi-line)
- `datetime.datetime` → TOML datetime
- `datetime.date` → TOML date
- `datetime.time` → TOML time (must not have tzinfo)
- `list`, `tuple` → TOML array
- `dict`, any Mapping → TOML table or inline table
- `decimal.Decimal` → TOML float

### Inline Table Heuristics

A table is rendered inline if:
- Its inline representation (with indent) is ≤ 100 characters
- It contains no newlines
- It's a value within an array or another inline table

Otherwise, it's rendered as a separate `[table]` section.

### Error Handling

The library raises `TypeError` for:
- Non-serializable object types
- Non-string mapping keys
- Keys that are string-like but not actual str instances

The library raises `ValueError` for:
- Negative indent values
- `datetime.time` objects with timezone information (TOML doesn't support offset times)

### Determinism

- The output order matches the input dict order (insertion order in Python 3.7+)
- No sorting is performed
- Inline tables are cached by object id for efficiency

## Examples

### Basic Usage

```python
import tomli_w

# Simple dictionary
doc = {"name": "MyApp", "version": "1.0", "debug": False}
toml_str = tomli_w.dumps(doc)
print(toml_str)
# Output:
# name = "MyApp"
# version = "1.0"
# debug = false
```

### Nested Tables

```python
import tomli_w

doc = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "username": "admin"
        }
    }
}
toml_str = tomli_w.dumps(doc)
# Output:
# [database]
# host = "localhost"
# port = 5432
#
# [database.credentials]
# username = "admin"
```

### Arrays

```python
import tomli_w

doc = {
    "colors": ["red", "green", "blue"],
    "matrix": [[1, 2], [3, 4]]
}
toml_str = tomli_w.dumps(doc, indent=2)
# Output:
# colors = [
#   "red",
#   "green",
#   "blue",
# ]
# matrix = [
#   [
#     1,
#     2,
#   ],
#   [
#     3,
#     4,
#   ],
# ]
```

### Array of Tables

```python
import tomli_w

doc = {
    "products": [
        {"name": "Hammer", "sku": 738594937},
        {"name": "Nail", "sku": 284758393}
    ]
}
toml_str = tomli_w.dumps(doc)
# Output:
# [[products]]
# name = "Hammer"
# sku = 738594937
#
# [[products]]
# name = "Nail"
# sku = 284758393
```

## Error Handling and Boundary Conditions

### Empty Inputs

```python
import tomli_w

# Empty dict
assert tomli_w.dumps({}) == ""

# Empty array
doc = {"items": []}
assert tomli_w.dumps(doc) == 'items = []\n'

# Empty string
doc = {"value": ""}
assert tomli_w.dumps(doc) == 'value = ""\n'
```

### Special Characters

```python
import tomli_w

# Quotes and backslashes
doc = {"path": 'C:\\Users\\John"s'}
result = tomli_w.dumps(doc)
assert result == 'path = "C:\\\\Users\\\\John\\"s"\n'

# Unicode
doc = {"greeting": "Hello, 世界"}
result = tomli_w.dumps(doc)
assert "世界" in result  # Unicode preserved

# Newlines without multiline
doc = {"text": "line1\nline2"}
result = tomli_w.dumps(doc, multiline_strings=False)
assert result == 'text = "line1\\nline2"\n'

# Newlines with multiline
doc = {"text": "line1\nline2"}
result = tomli_w.dumps(doc, multiline_strings=True)
assert '"""' in result
```

### Invalid Inputs

```python
import tomli_w
import datetime

# Non-string keys raise TypeError
try:
    tomli_w.dumps({1: "value"})
except TypeError:
    pass  # Expected

# Negative indent raises ValueError
try:
    tomli_w.dumps({}, indent=-1)
except ValueError:
    pass  # Expected

# Time with timezone raises ValueError
try:
    import datetime
    t = datetime.time(12, 0, tzinfo=datetime.timezone.utc)
    tomli_w.dumps({"time": t})
except ValueError:
    pass  # Expected

# Unsupported type raises TypeError
try:
    tomli_w.dumps({"obj": object()})
except TypeError:
    pass  # Expected
```

### Special Float Values

```python
import tomli_w
from decimal import Decimal

# NaN and infinity
doc = {
    "nan_val": float("nan"),
    "pos_inf": float("inf"),
    "neg_inf": float("-inf")
}
result = tomli_w.dumps(doc)
assert "nan" in result
assert "inf" in result
assert "-inf" in result

# Decimal support
doc = {"precise": Decimal("3.14159265358979323846")}
result = tomli_w.dumps(doc)
assert "3.14159265358979323846" in result
```

### Bare Keys vs Quoted Keys

```python
import tomli_w

# Bare keys (alphanumeric, dash, underscore)
doc = {"simple-key_123": "value"}
result = tomli_w.dumps(doc)
assert result == 'simple-key_123 = "value"\n'

# Quoted keys (spaces, special chars)
doc = {"key with spaces": "value", "key.with.dots": "value"}
result = tomli_w.dumps(doc)
assert '"key with spaces"' in result
assert '"key.with.dots"' in result
```

### File Writing

```python
import tomli_w
import tempfile

# Write to binary file
doc = {"config": "value"}
with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
    tomli_w.dump(doc, f)
    filepath = f.name

# File must be opened in binary mode
with tempfile.NamedTemporaryFile(mode='w') as f:
    try:
        tomli_w.dump(doc, f)  # Will fail
    except (TypeError, AttributeError):
        pass  # Text mode not supported
```
