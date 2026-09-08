# jsonpath-ng: JSONPath Query Library Implementation

## Natural Language Instruction

You are asked to implement the `jsonpath-ng` library from scratch. This library provides a robust JSONPath implementation for Python that allows querying and manipulating nested JSON/dictionary structures using a powerful path expression language.

JSONPath is to JSON what XPath is to XML - it provides a standardized way to query and extract data from complex nested structures. Your implementation should support:

1. **Basic path expressions**: Access fields using dot notation (`$.name`, `$.user.email`)
2. **Array operations**: Index access (`[0]`, `[-1]`), slicing (`[1:3]`, `[:2]`, `[2:]`), wildcards (`[*]`)
3. **Field wildcards**: Match all fields at a level (`$.*`, `$.user.*`)
4. **Root access**: Query from the root (`$`)
5. **Path tracking**: Each match should know its full path in the original data structure
6. **Update operations**: Modify values at matched paths
7. **Extended features**: Filters (`[?(@.price > 10)]`), arithmetic (`$.a + $.b`), special operators (`` `len` ``, `` `keys` ``, `` `parent` ``)
8. **Error handling**: Invalid JSONPath syntax should raise appropriate exceptions

The library must parse JSONPath expressions into an internal representation, execute queries against JSON data structures, return matches with their values and paths, and support in-place updates.

## Project Description

`jsonpath-ng` is a final implementation of JSONPath for Python that aims to be standard compliant, including arithmetic and binary comparison operators. It provides a full language implementation where JSONPath expressions are first-class objects that can be analyzed, transformed, parsed, printed, and extended.

**Key Features:**
- Robust parser (not just regex-based)
- Returns match objects with both value and full path information
- Support for updating and filtering matched values
- Extended parser with arithmetic, filters, and special operators
- Clean AST (Abstract Syntax Tree) for metaprogramming

**Package Information:**
- PyPI Package: `jsonpath-ng`
- Version: 1.8.0
- License: Apache-2.0
- Python: 3.10+

## Supports

- Python 3.10, 3.11, 3.12, 3.13, 3.14
- No external runtime dependencies
- Works with standard Python dictionaries and lists

## Environment Configuration

### Python Version
Python 3.12

### Dependencies
No runtime dependencies required. The library is self-contained.

### Installation
```bash
pip install -e .
```

## API Usage Guide

### Core Module: `jsonpath_ng`

#### `jsonpath_ng.parse(path_string)`

Parse a JSONPath expression string into an executable path object.

**Parameters:**
- `path_string` (str): JSONPath expression (e.g., `'$.users[*].name'`)

**Returns:**
- JSONPath object that can be used to find or update matches

**Raises:**
- `JsonPathParserError`: If the path syntax is invalid
- `JsonPathLexerError`: If lexical analysis fails

**Example:**
```python
from jsonpath_ng import parse

# Parse a simple path
expr = parse('$.user.name')

# Parse array wildcard path
expr = parse('$.items[*].price')

# Parse with slicing
expr = parse('$.data[1:5]')
```

#### `JSONPath.find(data)`

Find all matches of the path in the given data structure.

**Parameters:**
- `data` (dict/list): The JSON-like data structure to query

**Returns:**
- List of `DatumInContext` objects, each containing:
  - `.value`: The matched value
  - `.full_path`: The complete path to this value

**Example:**
```python
data = {'users': [{'name': 'alice', 'age': 30}, {'name': 'bob', 'age': 25}]}
expr = parse('$.users[*].name')
matches = expr.find(data)

# Extract values
values = [m.value for m in matches]  # ['alice', 'bob']

# Get full paths as strings
paths = [str(m.full_path) for m in matches]  # ['((users.[0]).name)', '((users.[1]).name)']
```

#### `JSONPath.update(data, new_value)`

Update all matched paths with a new value.

**Parameters:**
- `data` (dict/list): The data structure to update
- `new_value` (any): The value to set at all matched locations

**Returns:**
- Updated data structure (dict/list) with modifications applied

**Example:**
```python
data = {'items': [1, 2, 3]}
expr = parse('$.items[*]')
result = expr.update(data, 0)
# result: {'items': [0, 0, 0]}
```

### Extended Module: `jsonpath_ng.ext`

#### `jsonpath_ng.ext.parse(path_string)`

Parse a JSONPath expression with extended syntax support including filters and arithmetic.

**Example:**
```python
from jsonpath_ng.ext import parse as ext_parse

# Filter: select items where price > 10
expr = ext_parse('$.items[?(@.price > 10)]')
matches = expr.find({'items': [{'price': 5}, {'price': 15}]})
# Returns: [{'price': 15}]

# Arithmetic: add two fields
expr = ext_parse('$.a + $.b')
matches = expr.find({'a': 10, 'b': 20})
# Returns: [30]

# Special operators
expr = ext_parse('$.items.`len`')
matches = expr.find({'items': [1, 2, 3]})
# Returns: [3]
```

**Supported Filters:**
- Comparison: `>`, `>=`, `<`, `<=`, `=`, `!=`
- String matching: `=~` (regex)
- Combine with `&`

**Arithmetic Operators:**
- `+`, `-`, `*`, `/`

**Special Operators:**
- `` `len` ``: Get length of array/string
- `` `keys` ``: Get dictionary keys
- `` `parent` ``: Navigate to parent object

### Exceptions Module: `jsonpath_ng.exceptions`

#### `JsonPathParserError`

Raised when JSONPath syntax is invalid during parsing.

**Example:**
```python
from jsonpath_ng import parse
from jsonpath_ng.exceptions import JsonPathParserError

try:
    parse('$..invalid[]]')
except JsonPathParserError as e:
    print(f"Parse error: {e}")
```

#### `JsonPathLexerError`

Raised when lexical analysis fails (e.g., unclosed quotes).

## JSONPath Syntax Reference

### Basic Syntax

| Syntax | Description | Example |
|--------|-------------|---------|
| `$` | Root object | `$` matches the entire data |
| `.field` | Access named field | `$.name` |
| `['field']` | Bracket notation | `$['user-name']` |
| `[n]` | Array index (0-based) | `$.items[0]` |
| `[-n]` | Negative index | `$.items[-1]` (last) |
| `[start:end]` | Array slice | `$.items[1:3]` |
| `[*]` | All array elements | `$.items[*]` |
| `.*` | All object fields | `$.*` |

### Path Examples

```python
# Root access
parse('$')  # Returns the entire data structure

# Simple field
parse('$.name')  # Access 'name' field at root

# Nested fields
parse('$.user.email')  # Traverse nested objects

# Array indexing
parse('$.items[0]')   # First element
parse('$.items[-1]')  # Last element

# Array slicing
parse('$.items[1:3]')  # Elements 1 and 2
parse('$.items[:2]')   # First 2 elements
parse('$.items[2:]')   # From index 2 to end

# Wildcards
parse('$.items[*]')          # All array elements
parse('$.*')                 # All fields in root object
parse('$.users[*].name')     # All names from users array

# Complex paths
parse('$.data.users[*].profile.email')
```

## Implementation Notes

### Core Components

1. **Lexer** (`lexer.py`): Tokenizes JSONPath expression strings
2. **Parser** (`parser.py`): Builds AST from tokens using PLY (Python Lex-Yacc)
3. **JSONPath Classes** (`jsonpath.py`): AST node types (Fields, Index, Slice, Child, etc.)
4. **Extended Parser** (`ext/`): Additional operators and filters
5. **Exceptions** (`exceptions.py`): Error types for invalid syntax

### Key Classes

- `Root`: Represents `$`
- `Fields`: Named field access
- `Index`: Array index access
- `Slice`: Array slicing
- `Child`: Combines two path segments (e.g., `$.a.b`)
- `DatumInContext`: Match result with value and path

### Match Objects

When you call `.find()`, you get `DatumInContext` objects:
- `.value`: The actual matched value
- `.full_path`: A path object representing where this value was found
- `str(match.full_path)`: String representation of the path

### Update Behavior

The `.update()` method creates a modified copy of the data structure with all matched paths set to the new value. It preserves unmatched parts of the structure unchanged.

### Extended Syntax Details

**Filters** use `@` to refer to the current item being tested:
- `$.items[?(@.price > 10)]`: Items with price greater than 10
- `$.items[?(@.name = "alice")]`: Items where name equals "alice"

**Arithmetic** evaluates operations between matched values:
- `$.a + $.b`: Add two fields
- `$.price * $.quantity`: Multiply fields

**Special operators** are enclosed in backticks:
- `` $.items.`len` ``: Length of items array
- `` $.data.`keys` ``: Keys of data dictionary
- `` $.a.b.`parent` ``: Get parent of field b (returns the object containing b)

### Error Handling

Parse errors occur when:
- Unclosed brackets: `$.arr[0`
- Invalid syntax: `$..invalid[]]`
- Unclosed quotes: `$."field`
- Empty expressions: `parse('')`
- Malformed filters: `$.arr[?(@.bad`

All parse errors raise either `JsonPathParserError` or `JsonPathLexerError` from `jsonpath_ng.exceptions`.

### Testing Considerations

- Test basic field access (nested, missing fields)
- Test array operations (indexing, negative indices, slicing, wildcards)
- Test path string representations
- Test update operations with different value types
- Test filter expressions with various comparison operators
- Test arithmetic operations
- Test special operators (len, keys, parent)
- Test edge cases (empty arrays/dicts, null values, unicode)
- Test exception handling for invalid syntax

## Project Directory Structure

```
workspace/
├── jsonpath_ng/
│   ├── __init__.py           # Package initialization, exports parse()
│   ├── jsonpath.py           # Core JSONPath AST classes
│   ├── parser.py             # Main parser implementation
│   ├── lexer.py              # Lexical analyzer
│   ├── exceptions.py         # Exception classes
│   ├── ext/
│   │   ├── __init__.py       # Extended parser exports
│   │   ├── filter.py         # Filter expression support
│   │   ├── arithmetic.py     # Arithmetic operators
│   │   └── iterable.py       # Iteration utilities
│   ├── bin/
│   │   ├── __init__.py
│   │   └── jsonpath.py       # CLI tool (optional)
│   └── _ply/                 # Vendored PLY parser library
│       ├── __init__.py
│       ├── lex.py            # PLY lexer
│       └── yacc.py           # PLY parser
├── setup.py                  # Package setup
└── pyproject.toml            # Build configuration (optional)
```

**Key Files:**
- `jsonpath_ng/__init__.py`: Must export `parse` function and version
- `jsonpath_ng/parser.py`: Must provide `parse()` function
- `jsonpath_ng/jsonpath.py`: Core path classes with `find()` and `update()` methods
- `jsonpath_ng/exceptions.py`: Must define `JsonPathParserError` and `JsonPathLexerError`
- `jsonpath_ng/ext/__init__.py`: Must export extended `parse` function

The `_ply` subdirectory contains the PLY (Python Lex-Yacc) parser generator library, which you should vendor or reimplement to avoid external dependencies.
