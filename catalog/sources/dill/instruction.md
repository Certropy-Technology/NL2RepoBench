# Build the dill Package

## Project Description

`dill` extends Python's `pickle` module for serializing and de-serializing Python objects to the majority of the built-in Python types. It provides the user the same interface as the `pickle` module, with additional features for serializing more "exotic" types.

**Key Capabilities:**
- Serialize lambdas, nested functions, and closures
- Pickle Python classes, instances, and metaclasses  
- Handle functions with yields, generators, and code objects
- Serialize built-in types, dataclasses, and custom iterators
- Save and restore the state of an interpreter session
- Interactively diagnose pickling errors

`dill` is designed as a drop-in replacement for `pickle`, allowing existing code to be updated simply by importing `dill` instead of `pickle`.

## Supports

- **Language**: Python 3.9+
- **Package Manager**: pip
- **License**: BSD-3-Clause
- **No runtime dependencies**

## Natural Language Instruction

Your task is to implement the `dill` package that extends Python's pickle capabilities to serialize a much wider variety of Python objects, including lambdas, nested functions, closures, classes, and instances.

The package should be installable via `pip install -e .` and provide the following core functionality:

1. **Basic Serialization API** compatible with pickle:
   - `dill.dumps(obj, protocol=None, byref=None, fmode=None, recurse=None)` - serialize object to bytes
   - `dill.loads(str)` - deserialize bytes back to object
   - `dill.dump(obj, file, ...)` - serialize object to file
   - `dill.load(file)` - deserialize object from file

2. **Extended Serialization** beyond standard pickle:
   - Lambda functions (e.g., `lambda x: x * 2`)
   - Nested functions and closures
   - Functions with default arguments, *args, **kwargs
   - Classes and class instances
   - Dataclasses and instances
   - Class methods, static methods, properties
   - Partial functions from functools
   - Custom iterators and generators

3. **Additional Options**:
   - `recurse` parameter: when True, recursively trace and pickle objects referred to in global dictionary
   - Protocol levels compatible with pickle
   - Settings via `dill.settings` dictionary

4. **Round-trip Correctness**:
   - For simple objects: `dill.loads(dill.dumps(obj)) == obj`
   - For functions: `dill.loads(dill.dumps(func))(args)` produces same output as `func(args)`
   - For classes: restored instances have same attributes and methods

## Environment Configuration

**Python Version**: 3.12

**Base Image**: `python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`

**Installation**: The package uses setuptools and can be installed with:
```bash
python -m pip install --no-build-isolation --no-deps --no-index -e .
```

**Network**: No network access during candidate installation or verification.

## Project Directory Structure

```
workspace/
├── dill/
│   ├── __init__.py          # Main API exports: dumps, loads, dump, load, Pickler, Unpickler
│   ├── _dill.py             # Core serialization implementation
│   ├── settings.py          # Global settings dictionary
│   ├── detect.py            # Diagnostic tools for pickling issues
│   ├── logger.py            # Logging and tracing utilities
│   ├── session.py           # Session save/restore functionality
│   ├── source.py            # Source code inspection
│   ├── temp.py              # Temporary file utilities
│   ├── _objects.py          # Object type registry
│   ├── _shims.py            # Compatibility shims
│   ├── objtypes.py          # Type definitions
│   ├── pointers.py          # Pointer and reference handling
│   ├── __diff.py            # Diff utilities
│   └── __info__.py          # Package metadata
├── setup.py                  # Setuptools configuration
├── pyproject.toml           # Build system requirements
├── LICENSE                   # BSD-3-Clause license
└── README.md                 # Documentation
```

## API Usage Guide

### Core Serialization Functions

#### `dill.dumps(obj, protocol=None, byref=None, fmode=None, recurse=None)`

Serialize an object to a byte string.

**Parameters:**
- `obj`: Any Python object to serialize
- `protocol` (int, optional): Pickle protocol version (default: pickle.DEFAULT_PROTOCOL)
- `byref` (bool, optional): If True, pickle certain objects by reference (like modules)
- `fmode` (int, optional): File mode for file handles (HANDLE_FMODE, CONTENTS_FMODE, or FILE_FMODE)
- `recurse` (bool, optional): If True, recursively pickle objects in global dictionary

**Returns:** bytes - serialized representation

**Example:**
```python
import dill

# Serialize a lambda
f = lambda x: x ** 2
serialized = dill.dumps(f)
```

#### `dill.loads(str)`

Deserialize a byte string back to a Python object.

**Parameters:**
- `str` (bytes): Serialized byte string from `dill.dumps()`

**Returns:** object - the deserialized Python object

**Raises:**
- `UnpicklingError`: If deserialization fails

**Example:**
```python
import dill

f = lambda x: x ** 2
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(5)  # Returns 25
```

#### `dill.dump(obj, file, protocol=None, byref=None, fmode=None, recurse=None)`

Serialize an object to a file-like object.

**Parameters:**
- `obj`: Object to serialize
- `file`: File-like object with `write()` method (e.g., io.BytesIO, open file)
- Other parameters same as `dumps()`

**Returns:** None

**Example:**
```python
import dill
import io

data = {'key': 'value', 'number': 42}
buffer = io.BytesIO()
dill.dump(data, buffer)
```

#### `dill.load(file)`

Deserialize an object from a file-like object.

**Parameters:**
- `file`: File-like object with `read()` method

**Returns:** object - the deserialized Python object

**Example:**
```python
import dill
import io

buffer = io.BytesIO()
dill.dump([1, 2, 3], buffer)
buffer.seek(0)
restored = dill.load(buffer)  # Returns [1, 2, 3]
```

### Serializing Functions

#### Lambda Functions

```python
import dill

# Basic lambda
f = lambda x, y: x + y
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(3, 4)  # Returns 7
```

#### Functions with Closures

```python
import dill

def make_multiplier(n):
    return lambda x: x * n

multiplier = make_multiplier(5)
serialized = dill.dumps(multiplier)
restored = dill.loads(serialized)
result = restored(3)  # Returns 15
```

#### Nested Functions

```python
import dill

def outer(a):
    def inner(b):
        return a + b
    return inner

f = outer(10)
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(5)  # Returns 15
```

#### Recursive Functions with recurse=True

For functions that reference themselves by name, use `recurse=True`:

```python
import dill

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

serialized = dill.dumps(factorial, recurse=True)
restored = dill.loads(serialized)
result = restored(5)  # Returns 120
```

### Serializing Classes and Instances

#### Simple Classes

```python
import dill

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self):
        return (self.x**2 + self.y**2)**0.5

p = Point(3, 4)
serialized = dill.dumps(p)
restored = dill.loads(serialized)
result = restored.distance()  # Returns 5.0
```

#### Dataclasses

```python
import dill
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int

p = Person('Alice', 30)
serialized = dill.dumps(p)
restored = dill.loads(serialized)
# restored.name == 'Alice', restored.age == 30
```

#### Classes with Methods

```python
import dill

class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

calc = Calculator()
serialized = dill.dumps(calc)
restored = dill.loads(serialized)
# Can call restored.add(2, 3), restored.multiply(2, 3)
```

### Serializing Collections

All standard Python collections are supported:

```python
import dill

# Lists
data = [1, 2, [3, 4]]
assert dill.loads(dill.dumps(data)) == data

# Dictionaries
data = {'a': 1, 'nested': {'b': 2}}
assert dill.loads(dill.dumps(data)) == data

# Sets (note: restored as sorted list for comparison)
data = {1, 2, 3, 4, 5}
restored = dill.loads(dill.dumps(data))
assert sorted(list(restored)) == [1, 2, 3, 4, 5]

# Tuples
data = (1, 'two', 3.0)
assert dill.loads(dill.dumps(data)) == data
```

### Advanced Features

#### Partial Functions

```python
import dill
from functools import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
serialized = dill.dumps(square)
restored = dill.loads(serialized)
result = restored(5)  # Returns 25
```

#### Custom Iterators

```python
import dill

class Counter:
    def __init__(self, max):
        self.max = max
        self.current = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current < self.max:
            self.current += 1
            return self.current
        raise StopIteration

c = Counter(3)
serialized = dill.dumps(c)
restored = dill.loads(serialized)
result = list(restored)  # Returns [1, 2, 3]
```

#### Class Inheritance

```python
import dill

class Animal:
    def speak(self):
        return 'sound'

class Dog(Animal):
    def speak(self):
        return 'bark'

d = Dog()
serialized = dill.dumps(d)
restored = dill.loads(serialized)
result = restored.speak()  # Returns 'bark'
```

## Implementation Notes

### Required Modules

The package should provide these core modules in the `dill/` directory:
- `__init__.py` - exports main API functions
- `_dill.py` - core implementation
- `settings.py` - global settings
- Additional modules for extended functionality

### Serialization Protocol

- Must be compatible with Python's pickle protocol
- Should handle basic types: int, str, float, bool, None, bytes
- Should handle collections: list, tuple, dict, set, frozenset
- Should handle functions: lambda, nested, closures, recursive (with `recurse=True`)
- Should handle classes: instances, methods, properties, dataclasses

### Round-trip Testing

The implementation must satisfy these properties:

For **immutable basic types**:
```python
obj = <int, str, float, bool, None, tuple of immutable>
assert dill.loads(dill.dumps(obj)) == obj
```

For **collections**:
```python
# Lists and dicts
assert dill.loads(dill.dumps([1, 2, 3])) == [1, 2, 3]
assert dill.loads(dill.dumps({'a': 1})) == {'a': 1}

# Sets (order not guaranteed)
s = {1, 2, 3}
restored = dill.loads(dill.dumps(s))
assert sorted(list(restored)) == sorted(list(s))
```

For **functions**:
```python
f = lambda x: x * 2
restored = dill.loads(dill.dumps(f))
assert restored(5) == f(5)
```

For **classes**:
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
restored = dill.loads(dill.dumps(p))
assert restored.x == p.x and restored.y == p.y
```

### Special Handling

- **Bytes**: When serializing bytes, restored bytes should be identical
- **Recursive functions**: Use `recurse=True` parameter to include global scope
- **Dataclasses**: Must preserve field values and types after restoration
- **File-like objects**: `dump()` and `load()` work with any object having `write()` and `read()` methods

### Error Handling

The implementation should raise appropriate exceptions:
- `PicklingError` - when serialization fails
- `UnpicklingError` - when deserialization fails
- `PickleError` - base class for pickle-related errors

### Module Structure Requirements

The main `dill/__init__.py` must export at minimum:
```python
from ._dill import (
    dump, dumps, load, loads,
    Pickler, Unpickler,
    DEFAULT_PROTOCOL, HIGHEST_PROTOCOL,
    HANDLE_FMODE, CONTENTS_FMODE, FILE_FMODE,
    PickleError, PicklingError, UnpicklingError,
    PickleWarning, PicklingWarning, UnpicklingWarning,
)

from .settings import settings

__version__ = "0.4.1"
```

### Testing Approach

The verifier will test:
1. Basic types: int, float, str, bool, None, bytes
2. Collections: list, dict, tuple, set, frozenset
3. Lambda functions and closures
4. Nested functions
5. Classes and instances
6. Dataclasses
7. Functions with special parameters (*args, **kwargs, defaults)
8. Class methods, static methods, properties
9. Partial functions
10. Custom iterators and inheritance
11. File I/O with `dump()` and `load()`
12. Recursive functions with `recurse=True`

### Common Pitfalls

- **Recursive functions without recurse=True**: Functions that reference themselves by name need `recurse=True` to ensure the function definition is included in the serialized state
- **Module-level classes**: Classes defined at module level may need special handling to restore correctly
- **Mutable default arguments**: Be careful with functions that use mutable defaults
- **Circular references**: The implementation must handle circular references between objects

## Success Criteria

Your implementation will be considered correct if:

1. All basic serialization round-trips work correctly (`dumps`/`loads`, `dump`/`load`)
2. Lambda functions and closures can be serialized and restored with correct behavior
3. Classes and instances can be serialized and restored with preserved attributes and methods
4. Collections (list, dict, set, tuple) are correctly serialized and deserialized
5. Special Python objects (dataclasses, partial functions, iterators) work correctly
6. The `recurse` parameter enables serialization of recursive functions
7. File I/O operations work with BytesIO and file-like objects
8. The package can be installed and imported without errors

Focus on correctness and completeness of the core serialization functionality. The implementation should handle the wide variety of Python types that `dill` is known for supporting beyond standard pickle.
