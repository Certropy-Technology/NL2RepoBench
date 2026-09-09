# Build pydash Package

## Natural Language Instruction

Build the **pydash** library from scratch — a Python utility library inspired by Lo-Dash (lodash) and Underscore.js. This library provides functional programming helpers and utilities for working with collections, arrays, objects, strings, and functions in a pythonic way.

Implement a comprehensive set of utility functions covering:
- **Array operations**: chunking, compacting, flattening, taking, union, unique values, filtering
- **Object path operations**: deep get/set/unset with dot notation and array indexing
- **Collection operations**: map, filter, reduce, group_by, key_by, find operations
- **Predicate functions**: is_empty, is_equal for deep comparisons
- **Object manipulation**: merge, pick, omit, keys, values, invert, defaults
- **Function utilities**: negate, times, identity, constant
- **String transformations**: camelCase, snake_case, kebab-case, capitalize, truncate
- **Set operations**: intersection, difference, zip/unzip

The package should be installable via pip and expose all utilities through the top-level `pydash` module.

## Project Description

pydash is a comprehensive utility library that brings the power of functional programming to Python. It provides over 200 utility functions for manipulating and working with Python data structures in a clean, chainable, and functional style.

Key features:
- **Collection utilities**: Transform, filter, and aggregate data with functional operators
- **Deep object path access**: Navigate nested dictionaries and lists using string paths like `'a.b[0].c'`
- **Functional composition**: Combine functions with negate, times, and other higher-order utilities
- **String manipulation**: Convert between naming conventions and format strings
- **Type-safe operations**: Leverages type hints and returns predictable results
- **No side effects**: Most operations are pure functions that don't modify input data

## Supports

- **Language**: Python 3.10+
- **Dependencies**: typing-extensions (>3.10, !=4.6.0)
- **Build system**: setuptools with pyproject.toml
- **Package structure**: Multi-module library with top-level `pydash` package

## API Usage Guide

### Array Operations

```python
import pydash

# Chunk array into smaller arrays
pydash.chunk([1, 2, 3, 4, 5], 2)
# => [[1, 2], [3, 4], [5]]

# Remove falsey values
pydash.compact([0, 1, False, 2, '', 3, None])
# => [1, 2, 3]

# Get first and last elements
pydash.first([1, 2, 3])  # => 1
pydash.last([1, 2, 3])   # => 3

# Flatten arrays
pydash.flatten([1, [2, 3], [[4]]])
# => [1, 2, 3, [4]]

pydash.flatten_deep([1, [2, [3, [4]]]])
# => [1, 2, 3, 4]

# Take elements from start or end
pydash.take([1, 2, 3, 4, 5], 3)
# => [1, 2, 3]

pydash.take_right([1, 2, 3, 4, 5], 2)
# => [4, 5]

# Set operations
pydash.union([1, 2], [2, 3], [3, 4])
# => [1, 2, 3, 4]

pydash.uniq([1, 2, 2, 3, 3, 3])
# => [1, 2, 3]

pydash.intersection([1, 2, 3], [2, 3, 4])
# => [2, 3]

pydash.difference([1, 2, 3], [2, 4])
# => [1, 3]

# Exclude specific values
pydash.without([1, 2, 3, 4], 2, 4)
# => [1, 3]

# Zip and unzip
pydash.zip_([1, 2], ['a', 'b'], [True, False])
# => [[1, 'a', True], [2, 'b', False]]

pydash.unzip([[1, 'a'], [2, 'b']])
# => [[1, 2], ['a', 'b']]
```

### Object Path Operations

```python
import pydash

# Deep get with dot notation and array indexing
pydash.get({'a': {'b': {'c': 3}}}, 'a.b.c')
# => 3

pydash.get({'a': [{'b': 1}]}, 'a[0].b')
# => 1

# Default value when path doesn't exist
pydash.get({'x': 1}, 'y', default=10)
# => 10

# Check if path exists
pydash.has({'a': {'b': 2}}, 'a.b')
# => True

# Deep set (modifies object in place)
obj = {}
pydash.set_(obj, 'a.b.c', 5)
# obj is now {'a': {'b': {'c': 5}}}

# Remove nested property
obj = {'a': {'b': {'c': 3}}, 'd': 4}
pydash.unset(obj, 'a.b.c')
# obj is now {'a': {'b': {}}, 'd': 4}
```

### Collection Operations

```python
import pydash

# Map over collections
pydash.map_([1, 2, 3], lambda x: x * 2)
# => [2, 4, 6]

# Property extraction shorthand
pydash.map_([{'a': 1}, {'a': 2}], 'a')
# => [1, 2]

# Filter collections
pydash.filter_([1, 2, 3, 4], lambda x: x % 2 == 0)
# => [2, 4]

# Reduce/aggregate
pydash.reduce_([1, 2, 3, 4], lambda acc, x: acc + x, 0)
# => 10

# Group by a criterion
pydash.group_by([1.3, 2.1, 2.4], lambda x: int(x))
# => {'1': [1.3], '2': [2.1, 2.4]}

# Create lookup dictionary
pydash.key_by([{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}], 'id')
# => {'1': {'id': 1, 'name': 'a'}, '2': {'id': 2, 'name': 'b'}}

# Find elements
pydash.find([1, 2, 3, 4], lambda x: x > 2)
# => 3

pydash.find_index([1, 2, 3, 4], lambda x: x == 3)
# => 2

# Test predicates
pydash.every([2, 4, 6], lambda x: x % 2 == 0)
# => True

pydash.some([1, 2, 3], lambda x: x > 2)
# => True

pydash.includes([1, 2, 3], 2)
# => True
```

### Predicate Functions

```python
import pydash

# Check if empty
pydash.is_empty([])    # => True
pydash.is_empty({})    # => True
pydash.is_empty([1])   # => False

# Deep equality comparison
pydash.is_equal([1, 2, 3], [1, 2, 3])
# => True

pydash.is_equal({'a': 1}, {'a': 1})
# => True

pydash.is_equal([1, 2], [2, 1])
# => False
```

### Object Manipulation

```python
import pydash

# Merge objects
pydash.merge({'a': 1}, {'b': 2})
# => {'a': 1, 'b': 2}

pydash.merge({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
# => {'a': 1, 'b': 3, 'c': 4}

# Pick specific properties
pydash.pick({'a': 1, 'b': 2, 'c': 3}, 'a', 'c')
# => {'a': 1, 'c': 3}

# Omit properties
pydash.omit({'a': 1, 'b': 2, 'c': 3}, 'b')
# => {'a': 1, 'c': 3}

# Get keys and values
pydash.keys({'a': 1, 'b': 2})
# => ['a', 'b']

pydash.values({'a': 1, 'b': 2, 'c': 3})
# => [1, 2, 3]

# Invert keys and values
pydash.invert({'a': 1, 'b': 2})
# => {'1': 'a', '2': 'b'}

# Fill in defaults
pydash.defaults({'a': 1}, {'a': 2, 'b': 2})
# => {'a': 1, 'b': 2}
```

### Function Utilities

```python
import pydash

# Negate a predicate
is_even = lambda x: x % 2 == 0
is_odd = pydash.negate(is_even)
is_odd(3)  # => True

# Invoke function n times
pydash.times(3, lambda i: i * 2)
# => [0, 2, 4]

# Identity function
pydash.identity(42)
# => 42

# Constant function
const_func = pydash.constant(42)
const_func()  # => 42

# Generate ranges
list(pydash.range_(5))
# => [0, 1, 2, 3, 4]

list(pydash.range_(1, 6))
# => [1, 2, 3, 4, 5]

list(pydash.range_(0, 10, 2))
# => [0, 2, 4, 6, 8]
```

### String Transformations

```python
import pydash

# Case conversions
pydash.camel_case('hello world')
# => 'helloWorld'

pydash.snake_case('helloWorld')
# => 'hello_world'

pydash.kebab_case('helloWorld')
# => 'hello-world'

# Capitalization
pydash.capitalize('hello world')
# => 'Hello world'

pydash.upper_first('hello')
# => 'Hello'

pydash.lower_first('Hello')
# => 'hello'

# Truncate strings
pydash.truncate('hello world', 8)
# => 'hello...'
```

## Implementation Notes

### Module Structure

The library is organized into several submodules:
- `arrays.py` - Array manipulation functions
- `collections.py` - Collection iteration and transformation
- `objects.py` - Object/dictionary utilities
- `strings.py` - String manipulation
- `functions.py` - Function composition and utilities
- `predicates.py` - Type checking and comparison
- `utilities.py` - Miscellaneous utilities

All public functions must be re-exported through `__init__.py` for top-level access.

### Key Implementation Considerations

1. **Immutability**: Most functions should not modify input arguments. Return new data structures instead. Exceptions are functions with `_` suffix like `set_` that explicitly modify in place.

2. **Path notation**: Functions like `get`, `set_`, `has`, `unset` support:
   - Dot notation: `'a.b.c'`
   - Array indexing: `'a[0].b'`
   - Mixed: `'users[0].profile.name'`

3. **Iteratee support**: Functions like `map_`, `filter_`, `group_by` support multiple iteratee types:
   - Functions: `lambda x: x * 2`
   - Property names: `'id'` (extracts the 'id' property)
   - Dictionaries: `{'a': 1}` (matches objects with that property)

4. **Type conversions**: When keys are converted to strings (e.g., in `group_by`, `key_by`, `invert`), integer keys become string keys: `{1: 'a'}` becomes `{'1': 'a'}`

5. **Generator functions**: Some functions like `range_` return generators. Wrap in `list()` to get concrete results.

6. **Naming conflicts**: Functions that conflict with Python builtins have `_` suffix: `map_`, `filter_`, `reduce_`, `set_`, `zip_`, `range_`

### Testing Strategy

The library must pass comprehensive test scenarios covering:
- Empty inputs and edge cases
- Nested data structures
- Different iteratee types
- Type conversions (especially dict integer keys to strings)
- Generator consumption
- Deep equality comparisons
- Path notation variants

### Version Information

The library must expose `__version__ = "8.1.0"` at the top level.

## Project Directory Structure

```
workspace/
├── pyproject.toml           # Build configuration
├── setup.py                 # Optional legacy setup
├── README.rst              # Documentation
├── LICENSE.rst             # MIT license
└── src/
    └── pydash/
        ├── __init__.py     # Main exports with __version__
        ├── arrays.py       # Array utilities
        ├── collections.py  # Collection operations
        ├── objects.py      # Object/dict utilities
        ├── strings.py      # String transformations
        ├── functions.py    # Function utilities
        ├── predicates.py   # Type checking
        ├── utilities.py    # Miscellaneous
        ├── helpers.py      # Internal helpers
        ├── types.py        # Type definitions
        ├── exceptions.py   # Custom exceptions
        ├── chaining/       # Method chaining support
        └── py.typed        # PEP 561 marker
```

## Environment Configuration

- Python version: 3.10+
- Required dependencies: `typing-extensions>3.10,!=4.6.0`
- Build backend: setuptools with pyproject.toml
- Install command: `pip install -e .`
