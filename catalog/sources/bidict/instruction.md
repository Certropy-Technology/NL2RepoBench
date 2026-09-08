# Build bidict Package

## Project Description

bidict is the bidirectional mapping library for Python. It provides a `bidict` class that maintains a bidirectional mapping between keys and values, allowing efficient lookups in both directions through its `inverse` property.

Version: 0.24.1
License: MPL-2.0 (Mozilla Public License 2.0)
Repository: https://github.com/jab/bidict

## Supports

- Python 3.12
- Pure Python implementation with no external runtime dependencies
- Typed with py.typed marker for type checkers

## Natural Language Instruction

Implement the bidict package in the `/workspace` directory. The package should provide a `bidict` class that maintains bidirectional mappings between keys and values.

Your implementation must:

1. Create a `bidict` module that can be imported with `from bidict import bidict`
2. Implement the `bidict` class that extends dictionary functionality
3. Support construction from dictionaries, keyword arguments, or key-value pairs
4. Provide an `inverse` property that returns the inverse mapping (values→keys)
5. Maintain bidirectionality: prevent duplicate values (raise `ValueDuplicationError`)
6. Support standard dict operations: get, setdefault, update, pop, popitem, clear, copy
7. Support dict views: keys(), values(), items()
8. Support equality comparison with other bidicts and regular dicts
9. The inverse should also be a fully functional bidirectional mapping

## Environment Configuration

Build System: setuptools with pyproject.toml (uses uv_build backend)
Python Version: 3.12
Base OS: Debian 12 (bookworm)

The package uses `pyproject.toml` with uv_build as the build backend. No external runtime dependencies are required for Python 3.12+.

## API Usage Guide

### Basic Construction and Access

```python
from bidict import bidict

# Create a bidict
element_by_symbol = bidict({'H': 'hydrogen', 'He': 'helium', 'Li': 'lithium'})

# Forward mapping access
element_by_symbol['H']  # 'hydrogen'

# Inverse mapping access
element_by_symbol.inverse['hydrogen']  # 'H'
```

### Import Path

```python
from bidict import bidict, ValueDuplicationError
```

### Class Signature

```python
class bidict(dict):
    """Bidirectional mapping."""
    
    def __init__(self, *args, **kwargs):
        """Initialize from dict, pairs, or kwargs."""
    
    @property
    def inverse(self) -> bidict:
        """Return inverse mapping (values to keys)."""
    
    def __setitem__(self, key, value) -> None:
        """Set item, raising ValueDuplicationError if value exists."""
    
    def __getitem__(self, key):
        """Get value for key."""
    
    def get(self, key, default=None):
        """Get value for key with optional default."""
    
    def setdefault(self, key, default=None):
        """Set key to default if not present."""
    
    def update(self, *args, **kwargs) -> None:
        """Update with new mappings."""
    
    def pop(self, key, *default):
        """Remove and return value for key."""
    
    def popitem(self) -> tuple:
        """Remove and return (key, value) pair."""
    
    def clear(self) -> None:
        """Remove all items."""
    
    def copy(self) -> bidict:
        """Return shallow copy."""
    
    def keys(self):
        """Return keys view."""
    
    def values(self):
        """Return values view."""
    
    def items(self):
        """Return items view."""
```

### Exception

```python
class ValueDuplicationError(ValueError):
    """Raised when attempting to insert a duplicate value."""
```

### Construction Examples

```python
# From dictionary
b = bidict({'a': 1, 'b': 2})

# From keyword arguments
b = bidict(x=10, y=20)

# From key-value pairs
b = bidict([('k1', 'v1'), ('k2', 'v2')])

# Mixed
b = bidict({'a': 1}, b=2)

# Empty
b = bidict()
```

### Bidirectional Access

```python
b = bidict({'a': 1, 'b': 2})

# Forward direction
b['a']  # 1

# Inverse direction  
b.inverse[1]  # 'a'

# Inverse of inverse
b.inverse.inverse['a']  # 1

# Both directions support dict operations
list(b.keys())  # ['a', 'b']
list(b.inverse.keys())  # [1, 2]
```

### Value Duplication Prevention

```python
b = bidict({'a': 1})

# This raises ValueDuplicationError because value 1 already exists
b['b'] = 1  # Raises bidict.ValueDuplicationError

# Same for inverse direction
b2 = bidict({1: 'a'})
b2.inverse['a'] = 2  # Raises bidict.ValueDuplicationError
```

### Dictionary Methods

```python
b = bidict({'a': 1, 'b': 2})

# Get with default
b.get('a')  # 1
b.get('z', -1)  # -1

# Setdefault
b.setdefault('c', 3)  # 3, and b now contains 'c': 3
b.setdefault('a', 99)  # 1 (returns existing value)

# Update
b.update({'d': 4})
b.update(e=5)

# Pop
v = b.pop('a')  # Returns 1, removes 'a'
v = b.pop('z', 'default')  # Returns 'default'

# Popitem
key, value = b.popitem()

# Clear
b.clear()  # b is now empty

# Copy
c = b.copy()  # Shallow copy
```

### Views and Iteration

```python
b = bidict({'a': 1, 'b': 2})

# Keys
list(b.keys())  # ['a', 'b']

# Values
list(b.values())  # [1, 2]

# Items
list(b.items())  # [('a', 1), ('b', 2)]

# Membership
'a' in b  # True
1 in b.inverse  # True
```

### Equality

```python
b1 = bidict({'a': 1})
b2 = bidict({'a': 1})
b1 == b2  # True

# Also compares equal to regular dicts with same items
b1 == {'a': 1}  # True
```

## Implementation Notes

### Core Requirements

1. **Module Structure**: The package must be importable as `from bidict import bidict, ValueDuplicationError`

2. **Bidirectional Invariant**: At all times, both the forward and inverse mappings must be consistent. If `b[k] = v`, then `b.inverse[v] = k`.

3. **Value Uniqueness**: Unlike regular dicts where multiple keys can map to the same value, bidict enforces value uniqueness. Attempting to add a key-value pair where the value already exists for a different key raises `ValueDuplicationError`.

4. **Inverse Property**: The `inverse` property returns a view of the bidirectional mapping in the opposite direction. Operations on the inverse affect the original bidict.

5. **Double Inverse**: The inverse of the inverse returns the original mapping: `b.inverse.inverse` is equivalent to `b`.

### Build System

The package uses pyproject.toml with uv_build as the build backend:

```toml
[build-system]
requires = ["uv_build>=0.8.13,<0.12"]
build-backend = "uv_build"
```

Install in development/editable mode:
```bash
python -m pip install --no-build-isolation --no-deps --no-index -e .
```

### Type Information

The package includes a `py.typed` marker file to indicate that it includes type information for type checkers.

### Exception Module Path

The `ValueDuplicationError` exception should have the module path `bidict.ValueDuplicationError`.

## Project Directory Structure

```
workspace/
├── bidict/
│   ├── __init__.py          # Public API exports
│   ├── _bidict.py           # Main bidict class
│   ├── _exc.py              # Exception classes
│   ├── py.typed             # Type marker
│   └── [other implementation files]
├── pyproject.toml           # Build configuration
└── [other project files]
```

The exact internal structure is flexible, but the public API must be importable from the top-level `bidict` module.

## Common Edge Cases

1. **Empty bidict**: `bidict()` creates an empty bidirectional mapping
2. **Single element**: Works correctly with just one key-value pair
3. **Integer keys**: Keys and values can be of any hashable type
4. **None values**: `None` is a valid value
5. **Pop from empty**: `popitem()` on empty bidict raises `KeyError`
6. **Get missing key**: `get('missing')` returns `None` by default
7. **Update with duplicate value**: Raises `ValueDuplicationError`
8. **Overwrite existing key**: `update({'a': 99})` overwrites key 'a' with new value

## Test Coverage

Your implementation will be tested on:
- Construction from various input types
- Forward and inverse access patterns
- Bidirectional consistency
- Value duplication detection
- All standard dict methods
- View operations
- Equality semantics
- Edge cases and error conditions
