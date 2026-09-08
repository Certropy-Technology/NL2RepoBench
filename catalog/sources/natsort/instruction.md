# Project Description

**natsort** is a Python library that provides simple yet flexible natural sorting functionality. Natural sorting orders strings containing numbers in a human-intuitive way, so that "file2.txt" comes before "file10.txt" (not lexicographically as "file10.txt", "file2.txt").

The library is designed for developers who need to sort file names, version strings, mixed alphanumeric data, and other human-readable sequences. It supports various sorting modes including locale-aware sorting, path sorting, real number sorting, and case-insensitive sorting.

## Target Users
- Python developers sorting file listings, version numbers, or mixed text-numeric data
- Applications requiring natural ordering of strings with embedded numbers
- Systems that need locale-dependent or path-aware sorting

## Key Capabilities
- Natural sorting of strings with embedded integers or floats
- Support for sorting paths with filesystem-specific separators and extensions
- Locale-aware sorting for international text
- Flexible algorithm options via bitwise-combinable flags
- Key generation for in-place sorting with `list.sort()`
- Convenience functions for common use cases

# Natural Language Instruction

Build a Python package named `natsort` that provides natural sorting functionality. The package must:

1. **Implement `natsorted()` function**: A drop-in replacement for Python's built-in `sorted()` that performs natural sorting, handling numbers within strings intelligently.

2. **Provide `natsort_keygen()` for custom sorting keys**: Generate reusable sorting keys that can be passed to `sorted()` or `list.sort()` for in-place natural sorting.

3. **Support algorithm customization via `ns` enum**: Provide a flags enum allowing users to control sorting behavior through bitwise OR operations, including:
   - `ns.IGNORECASE` / `ns.IC`: Case-insensitive sorting
   - `ns.FLOAT` / `ns.F`: Parse numbers as floats
   - `ns.SIGNED` / `ns.S`: Respect signs (+ or -)
   - `ns.REAL` / `ns.R`: Shortcut for `FLOAT | SIGNED`
   - `ns.PATH` / `ns.P`: Filesystem path-aware sorting
   - `ns.LOCALE` / `ns.L`: Locale-aware sorting
   - `ns.LOWERCASEFIRST` / `ns.LF`: Sort lowercase before uppercase
   - `ns.GROUPLETTERS` / `ns.G`: Group uppercase and lowercase together
   - `ns.NUMAFTER` / `ns.NA`: Sort numbers after non-numbers
   - `ns.NOEXP` / `ns.N`: Don't parse scientific notation
   - `ns.NANLAST` / `ns.NL`: Treat NaN as +Infinity
   - `ns.PRESORT` / `ns.PS`: Pre-sort input as strings

4. **Provide convenience functions**: `realsorted()`, `humansorted()`, and `os_sorted()` as shortcuts for common algorithm combinations.

5. **Implement `index_natsorted()`**: Return indices that would sort the input naturally.

6. **Provide helper functions**: `order_by_index()`, `as_utf8()`, `as_ascii()`, and `natsort_key()`.

The package must be installable via `pip install -e .` and expose all public APIs through the `natsort` top-level import. The implementation must handle mixed types (strings, integers, floats), Unicode strings, empty inputs, and preserve sort stability.

# Environment Configuration (Supports)

- **Language**: Python 3.7+
- **Package Manager**: pip
- **Installation**: `pip install -e .` from the package root
- **Build Backend**: Standard setuptools or modern PEP 517 backend
- **Runtime Dependencies**: None required (all dependencies are optional)
- **Network Mode**: No network access required after installation
- **Entry Points**: Package import only (no CLI required for core functionality)

The package must work in offline environments once installed, with no external API calls or network dependencies during normal operation.

# Project Directory Structure

```text
workspace/
├── natsort/
│   ├── __init__.py          # Main exports and version
│   ├── natsort.py           # Core sorting functions
│   ├── ns_enum.py           # ns enum and algorithm flags
│   └── utils.py             # Helper utilities and key generation
├── pyproject.toml           # Or setup.py/setup.cfg for package metadata
└── README.md                # Package documentation
```

The `natsort/` directory contains the library source code. The `__init__.py` exports all public APIs. Package metadata (name, version, author, license) must be defined in `pyproject.toml`, `setup.py`, or `setup.cfg`.

# API Usage Guide

## Core Sorting Function

### `natsorted(seq, key=None, reverse=False, alg=ns.INT, **kwargs)`

Import: `from natsort import natsorted`

**Purpose**: Sort a sequence using natural sorting algorithm.

**Parameters**:
- `seq` (iterable): The sequence to sort
- `key` (callable, optional): Custom key function applied before natural sorting
- `reverse` (bool, default False): Sort in descending order if True
- `alg` (ns enum, default ns.INT): Algorithm flags (can be combined with `|`)
- Additional keyword arguments passed to underlying sort

**Returns**: List containing sorted elements

**Behavior**: 
- Parses embedded numbers and sorts them numerically
- Preserves Python's stable sort behavior
- Does not modify input sequence (returns new list)
- Handles mixed types: strings, integers, floats
- None values sorted first by default (last with ns.NANLAST)

**Example**:
```python
from natsort import natsorted
result = natsorted(['file10.txt', 'file2.txt', 'file1.txt'])
# Returns: ['file1.txt', 'file2.txt', 'file10.txt']
```

## Key Generation

### `natsort_keygen(key=None, alg=ns.INT, **kwargs)`

Import: `from natsort import natsort_keygen`

**Purpose**: Generate a reusable key function for natural sorting.

**Parameters**:
- `key` (callable, optional): Pre-processing function
- `alg` (ns enum, default ns.INT): Algorithm flags
- Additional keyword arguments for key generation

**Returns**: Callable that can be passed to `sorted()` or `list.sort()`

**Example**:
```python
from natsort import natsort_keygen
key_func = natsort_keygen()
data = ['a10', 'a2', 'a1']
data.sort(key=key_func)  # In-place sort
# data is now ['a1', 'a2', 'a10']
```

### `natsort_key(val, key=None, alg=ns.INT)`

Import: `from natsort import natsort_key`

**Purpose**: Transform a single value using the natural sorting key.

**Parameters**:
- `val`: The value to transform
- `key` (callable, optional): Pre-processing function
- `alg` (ns enum, default ns.INT): Algorithm flags

**Returns**: Tuple representing the natural sorting key for the value

**Example**:
```python
from natsort import natsort_key
result = natsort_key('file10.txt')
# Returns: ('file', 10, '.txt')
```

## Algorithm Flags (ns enum)

### `ns` - Natural Sort Algorithm Enum

Import: `from natsort import ns`

**Purpose**: Control natural sorting behavior through bitwise-combinable flags.

**Common Flags**:
- `ns.INT` or `ns.I`: Parse numbers as integers (default)
- `ns.FLOAT` or `ns.F`: Parse numbers as floats
- `ns.SIGNED` or `ns.S`: Respect +/- signs
- `ns.REAL` or `ns.R`: Equivalent to `ns.FLOAT | ns.SIGNED`
- `ns.IGNORECASE` or `ns.IC`: Case-insensitive sorting
- `ns.LOWERCASEFIRST` or `ns.LF`: Sort lowercase before uppercase
- `ns.PATH` or `ns.P`: Path-aware sorting (respects separators and extensions)
- `ns.LOCALE` or `ns.L`: Locale-aware sorting
- `ns.NUMAFTER` or `ns.NA`: Sort numbers after letters
- `ns.GROUPLETTERS` or `ns.G`: Group upper and lower case together
- `ns.NOEXP` or `ns.N`: Don't parse scientific notation (e.g., "5E10")
- `ns.NANLAST` or `ns.NL`: Sort NaN/None values last
- `ns.PRESORT` or `ns.PS`: Pre-sort strings before natural sort

**Usage**: Combine flags with bitwise OR (`|`)

**Example**:
```python
from natsort import natsorted, ns
result = natsorted(['A10', 'a2', 'A1'], alg=ns.IGNORECASE | ns.REAL)
```

## Convenience Functions

### `realsorted(seq, key=None, reverse=False, alg=ns.REAL, **kwargs)`

Import: `from natsort import realsorted`

**Purpose**: Sort sequence treating numbers as signed floats.

**Behavior**: Shortcut for `natsorted(seq, alg=ns.REAL | alg)`

**Example**:
```python
from natsort import realsorted
result = realsorted(['val5.10', 'val-3', 'val2'])
# Returns: ['val-3', 'val2', 'val5.10']
```

### `humansorted(seq, key=None, reverse=False, alg=ns.LOCALE, **kwargs)`

Import: `from natsort import humansorted`

**Purpose**: Sort with locale-aware comparison.

**Behavior**: Shortcut for `natsorted(seq, alg=ns.LOCALE | alg)`. Respects locale-specific alphabetical order and decimal separators.

**Note**: Requires proper locale configuration via `locale.setlocale()`.

**Example**:
```python
import locale
from natsort import humansorted
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
result = humansorted(['apple10', 'Apple5', 'banana2'])
```

### `os_sorted(seq, key=None, reverse=False, **kwargs)`

Import: `from natsort import os_sorted`

**Purpose**: Sort paths like the operating system's file browser.

**Behavior**: Applies OS-specific sorting rules (case-insensitive on Windows, locale-aware on Linux/Mac).

**Example**:
```python
from natsort import os_sorted
result = os_sorted(['File10', 'file2', 'File1'])
```

## Index and Order Functions

### `index_natsorted(seq, key=None, reverse=False, alg=ns.INT, **kwargs)`

Import: `from natsort import index_natsorted`

**Purpose**: Return the indices that would naturally sort the sequence.

**Returns**: List of integer indices

**Example**:
```python
from natsort import index_natsorted
indices = index_natsorted(['a10', 'a2', 'a1'])
# Returns: [2, 1, 0]  (meaning seq[2], seq[1], seq[0] is the sorted order)
```

### `order_by_index(seq, index, iter=False)`

Import: `from natsort import order_by_index`

**Purpose**: Reorder a sequence using provided indices.

**Parameters**:
- `seq` (sequence): The sequence to reorder
- `index` (list of int): Indices defining the new order
- `iter` (bool, default False): Return iterator instead of list if True

**Returns**: Reordered sequence

**Example**:
```python
from natsort import order_by_index
result = order_by_index(['a', 'b', 'c'], [2, 0, 1])
# Returns: ['c', 'a', 'b']
```

## Helper Functions

### `as_utf8(val)`

Import: `from natsort import as_utf8`

**Purpose**: Decode bytes to UTF-8 string for sorting.

**Use Case**: Sorting sequences containing bytes objects

**Example**:
```python
from natsort import natsorted, as_utf8
result = natsorted([b'a10', b'a2', b'a1'], key=as_utf8)
# Returns: [b'a1', b'a2', b'a10']
```

### `as_ascii(val)`

Import: `from natsort import as_ascii`

**Purpose**: Decode bytes to ASCII string for sorting.

**Behavior**: Similar to `as_utf8` but uses ASCII encoding.

# Implementation Notes

## Number Parsing
- By default, parse consecutive digits as unsigned integers
- With `ns.FLOAT`, parse numbers as floating-point including decimals
- With `ns.SIGNED`, recognize +/- immediately before numbers
- With `ns.NOEXP`, disable scientific notation parsing
- Leading zeros create distinct values ('01' ≠ '1')

## String Transformation
- Split strings into alternating text and number components
- Text components compared lexicographically
- Number components compared numerically
- The transformation is tuple-based for proper comparison

## Mixed Type Handling
- Integers, floats, and strings can be sorted together
- Type stability: same types maintain relative order
- None values sort first (or last with `ns.NANLAST`)

## Path Sorting
- With `ns.PATH`, split on filesystem separators ('/' or '\\')
- Also split on file extensions (e.g., '.txt')
- Ensures directories sort correctly relative to files

## Case Sensitivity
- Default sorting is case-sensitive (uppercase before lowercase)
- `ns.IGNORECASE`: Ignore case differences
- `ns.LOWERCASEFIRST`: Lowercase before uppercase
- `ns.GROUPLETTERS`: Group same letters regardless of case

## Locale Awareness
- `ns.LOCALE` enables locale-dependent string comparison
- Requires `locale.setlocale()` to be called first
- Affects alphabetical order and number formatting
- Optional PyICU library improves locale handling

## Performance
- Key generation (`natsort_keygen`) is efficient for repeated sorting
- Optional `fastnumbers` library can improve performance
- Stable sort preserves original order for equal elements

## Determinism
- Sorting is deterministic for the same input and flags
- With `ns.PRESORT`, pre-sort to eliminate input-order dependency

# Examples

## Basic Natural Sorting
```python
from natsort import natsorted

# Simple list
data = ['item10', 'item2', 'item1']
result = natsorted(data)
# Result: ['item1', 'item2', 'item10']

# Version strings
versions = ['v1.10', 'v1.2', 'v1.1']
sorted_versions = natsorted(versions)
# Result: ['v1.1', 'v1.2', 'v1.10']
```

## Using Algorithm Flags
```python
from natsort import natsorted, ns

# Case-insensitive
data = ['Apple', 'banana', 'apple']
result = natsorted(data, alg=ns.IGNORECASE)
# Result: ['Apple', 'apple', 'banana']

# Real numbers (signed floats)
data = ['val5.3', 'val-10', 'val2']
result = natsorted(data, alg=ns.REAL)
# Result: ['val-10', 'val2', 'val5.3']

# Combined flags
data = ['File10', 'file2', 'File1']
result = natsorted(data, alg=ns.IGNORECASE | ns.PATH)
# Result: ['File1', 'file2', 'File10']
```

## In-Place Sorting
```python
from natsort import natsort_keygen

data = ['file10.txt', 'file2.txt', 'file1.txt']
data.sort(key=natsort_keygen())
# data is now ['file1.txt', 'file2.txt', 'file10.txt']
```

## Working with Indices
```python
from natsort import index_natsorted, order_by_index

original = ['z10', 'z2', 'z1']
indices = index_natsorted(original)
# indices: [2, 1, 0]

# Apply to another list
labels = ['third', 'second', 'first']
reordered = order_by_index(labels, indices)
# reordered: ['first', 'second', 'third']
```

# Error Handling and Boundary Conditions

## Empty Sequences
```python
from natsort import natsorted
result = natsorted([])
# Returns: []
```

## None Values
```python
from natsort import natsorted, ns

# Default: None sorted first
result = natsorted(['a', None, 'b'])
# Returns: [None, 'a', 'b']

# With NANLAST: None sorted last (intended behavior may vary)
result = natsorted(['a', None, 'b'], alg=ns.NANLAST)
```

## Mixed Types
```python
from natsort import natsorted

# Integers, floats, and strings
result = natsorted([3, '10', 2.5, '1'])
# Returns: ['1', 2.5, 3, '10']
```

## Invalid Algorithm Flags
- Flags are combined with bitwise OR
- Invalid flag values are treated as integers
- Prefer using named `ns` enum values for clarity

## Unicode Handling
```python
from natsort import natsorted

# Unicode strings work correctly
result = natsorted(['café10', 'café2', 'café1'])
# Returns: ['café1', 'café2', 'café10']
```

## Bytes Sorting
```python
from natsort import natsorted, as_utf8

# Requires explicit key function
data = [b'file10', b'file2', b'file1']
result = natsorted(data, key=as_utf8)
# Returns: [b'file1', b'file2', b'file10']
```

## Large Numbers
```python
from natsort import natsorted

# Handles arbitrarily large integers
result = natsorted(['item1000000', 'item999', 'item100'])
# Returns: ['item100', 'item999', 'item1000000']
```
