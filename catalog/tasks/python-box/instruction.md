# Project Description

`python-box` is an advanced Python library that extends the built-in dictionary with dot notation access, automatic nested structure conversion, and flexible configuration management. It addresses the common need for more intuitive and flexible dictionary-like objects in Python, particularly for configuration files, API responses, and data structures where dot notation provides cleaner syntax than bracket notation.

The library provides several Box variants: `Box` (the main class), `BoxList` (for lists containing dictionaries), `DDBox` (default dictionary behavior), and specialized options for frozen boxes, camel case conversion, and attribute name transformation. It supports JSON serialization/deserialization and maintains compatibility with standard dict operations while adding powerful new features.

# Natural Language Instruction

Implement a Python package named `python-box` (import name `box`) that provides advanced dictionary types with dot notation access and automatic nested structure conversion. The package must:

1. Provide a `Box` class that extends `dict` with attribute-style access (e.g., `box.key` equivalent to `box['key']`)
2. Automatically convert nested dictionaries to Box instances and lists to BoxList instances
3. Support multiple configuration options: `default_box` (auto-create missing keys), `frozen_box` (immutable), `camel_killer_box` (convert CamelCase to snake_case), and `conversion_box` (transform invalid attribute names)
4. Provide `BoxList` class for lists that automatically convert dict elements to Box instances
5. Support JSON serialization with `to_json()` and `from_json()` methods
6. Provide `DDBox` (DefaultDictBox) for default dictionary behavior without key errors
7. Include utility function `box_from_string()` for parsing string data
8. Support all standard dict methods (get, update, merge_update, pop, clear, copy, keys, values, items, etc.)
9. Handle special keys with invalid Python identifier characters through automatic transformation
10. Support tuple keys and other hashable types as dictionary keys

The package name is `python-box`, the import name is `box`, and it must be installable via pip with setuptools backend.

# Supports (Environment Configuration)

- Python: 3.9+
- Package Manager: pip
- Build System: `setuptools` (backend: `setuptools.build_meta`)
- Runtime Dependencies: None (core functionality uses only Python standard library)
- Optional Dependencies: PyYAML (for YAML support), toml (for TOML support), msgpack (for MessagePack support)
- Installation: `pip install .`
- Testing: pytest
- No network access required during runtime

# Project Directory Structure

```
workspace/
├── pyproject.toml
└── box/
    ├── __init__.py
    └── [implementation modules]
```

# API Usage Guide

## Module: `box`

The root module exports the main classes and utility functions.

### Class: `Box`

The primary class that extends `dict` with dot notation access and automatic nested conversion.

#### `__init__(*args, default_box=False, default_box_attr=None, frozen_box=False, camel_killer_box=False, conversion_box=True, **kwargs)`

Create a new Box instance.

- **Parameters:**
  - `*args`: Positional arguments passed to dict (dict, iterable of pairs, etc.)
  - `default_box` (bool): If True, accessing missing keys creates nested Box automatically
  - `default_box_attr`: Value to use for missing keys when `default_box=True` (default: Box())
  - `frozen_box` (bool): If True, the Box cannot be modified after creation
  - `camel_killer_box` (bool): If True, converts CamelCase attribute names to snake_case
  - `conversion_box` (bool): If True, transforms keys with special characters to valid Python identifiers
  - `**kwargs`: Keyword arguments become key-value pairs in the Box
- **Returns:** Box instance
- **Example:**
  ```python
  from box import Box
  
  # Empty box
  b = Box()
  
  # From dict
  b = Box({'a': 1, 'b': 2})
  
  # From kwargs
  b = Box(x=10, y=20)
  
  # From tuples
  b = Box([('a', 1), ('b', 2)])
  
  # With options
  b = Box(default_box=True)  # Auto-create missing keys
  b = Box({'a': 1}, frozen_box=True)  # Immutable
  b = Box(camel_killer_box=True)  # CamelCase -> snake_case
  ```

#### Attribute Access

Access dictionary values using dot notation.

- **Get:** `box.key` retrieves `box['key']`
- **Set:** `box.key = value` sets `box['key'] = value`
- **Delete:** `del box.key` deletes `box['key']`
- **Behavior:**
  - Nested dicts are automatically converted to Box
  - Lists containing dicts are converted to BoxList
  - Missing keys raise `BoxKeyError` (subclass of KeyError) unless `default_box=True`
- **Example:**
  ```python
  b = Box({'key': 'value'})
  print(b.key)  # 'value'
  
  b.new_key = 'new_value'
  print(b['new_key'])  # 'new_value'
  
  # Nested access
  b = Box({'outer': {'inner': 'value'}})
  print(b.outer.inner)  # 'value'
  ```

#### Bracket Access

Standard dictionary bracket notation works alongside dot notation.

- **Get:** `box['key']`
- **Set:** `box['key'] = value`
- **Contains:** `'key' in box`
- **Delete:** `del box['key']`
- **Example:**
  ```python
  b = Box()
  b['key'] = 'value'
  print(b.key)  # 'value'
  
  if 'key' in b:
      del b['key']
  ```

#### `get(key, default=None)`

Get value for key with optional default.

- **Parameters:**
  - `key`: Dictionary key
  - `default`: Value to return if key is missing (default: None)
- **Returns:** Value if key exists, otherwise default
- **Example:**
  ```python
  b = Box({'a': 1})
  print(b.get('a'))  # 1
  print(b.get('missing'))  # None
  print(b.get('missing', 'default'))  # 'default'
  ```

#### `to_dict()`

Convert Box and nested Boxes back to standard Python dicts.

- **Returns:** dict with all nested Box/BoxList converted to dict/list
- **Behavior:** Recursively converts all Box instances to dicts and BoxList instances to lists
- **Example:**
  ```python
  b = Box({'a': 1, 'nested': {'b': 2}})
  d = b.to_dict()
  print(type(d))  # <class 'dict'>
  print(type(d['nested']))  # <class 'dict'>
  ```

#### `to_json(**kwargs)`

Convert Box to JSON string.

- **Parameters:** `**kwargs` passed to `json.dumps()` (e.g., `indent`, `sort_keys`)
- **Returns:** JSON string representation
- **Example:**
  ```python
  b = Box({'a': 1, 'b': 2})
  json_str = b.to_json()
  print(json_str)  # '{"a": 1, "b": 2}'
  
  # With formatting
  json_str = b.to_json(indent=2, sort_keys=True)
  ```

#### `from_json(json_string, **kwargs)` (classmethod)

Create Box from JSON string.

- **Parameters:**
  - `json_string` (str): Valid JSON string
  - `**kwargs`: Additional Box constructor options
- **Returns:** Box instance
- **Example:**
  ```python
  b = Box.from_json('{"a": 1, "b": 2}')
  print(b.a)  # 1
  
  # Nested structures
  b = Box.from_json('{"outer": {"inner": "value"}}')
  print(b.outer.inner)  # 'value'
  ```

#### `update(*args, **kwargs)`

Update Box with key-value pairs from dict or kwargs.

- **Parameters:**
  - `*args`: Dict or iterable of pairs
  - `**kwargs`: Keyword arguments
- **Returns:** None (modifies Box in place)
- **Behavior:** Nested dicts are converted to Box
- **Example:**
  ```python
  b = Box({'a': 1})
  b.update({'b': 2, 'c': 3})
  print(dict(b))  # {'a': 1, 'b': 2, 'c': 3}
  
  b.update(d=4, e=5)
  ```

#### `merge_update(*args, **kwargs)`

Recursively merge nested dictionaries.

- **Parameters:** Same as `update()`
- **Returns:** None (modifies Box in place)
- **Behavior:** For nested dicts, merges keys instead of replacing entire dict
- **Example:**
  ```python
  b = Box({'a': {'x': 1, 'y': 2}})
  b.merge_update({'a': {'y': 3, 'z': 4}})
  # Result: {'a': {'x': 1, 'y': 3, 'z': 4}}
  ```

#### `setdefault(key, default=None)`

Get value for key, setting it to default if missing.

- **Parameters:**
  - `key`: Dictionary key
  - `default`: Value to set and return if key is missing
- **Returns:** Existing value or newly set default
- **Example:**
  ```python
  b = Box()
  val = b.setdefault('key', 'default')
  print(val)  # 'default'
  print(b.key)  # 'default'
  
  val = b.setdefault('key', 'other')
  print(val)  # 'default' (existing value)
  ```

#### `pop(key, *args)`

Remove key and return its value.

- **Parameters:**
  - `key`: Dictionary key
  - `*args`: Optional default value if key is missing
- **Returns:** Value for key
- **Raises:** `KeyError` if key is missing and no default provided
- **Example:**
  ```python
  b = Box({'a': 1, 'b': 2})
  val = b.pop('a')
  print(val)  # 1
  print('a' in b)  # False
  
  val = b.pop('missing', 'default')
  print(val)  # 'default'
  ```

#### `popitem()`

Remove and return an arbitrary (key, value) pair.

- **Returns:** Tuple of (key, value)
- **Raises:** `KeyError` if Box is empty
- **Example:**
  ```python
  b = Box({'a': 1})
  k, v = b.popitem()
  print(k, v)  # 'a' 1
  print(len(b))  # 0
  ```

#### `clear()`

Remove all items from the Box.

- **Returns:** None
- **Example:**
  ```python
  b = Box({'a': 1, 'b': 2})
  b.clear()
  print(len(b))  # 0
  ```

#### `copy()`

Create a shallow copy of the Box.

- **Returns:** New Box instance
- **Behavior:** Creates new Box but nested Box instances are independent copies (deep copy behavior for nested Boxes)
- **Example:**
  ```python
  b1 = Box({'a': 1})
  b2 = b1.copy()
  b2.a = 2
  print(b1.a)  # 1 (unchanged)
  
  # Nested boxes are independent
  b1 = Box({'a': {'b': 1}})
  b2 = b1.copy()
  b2.a.b = 2
  print(b1.a.b)  # 1 (nested Box is independent)
  ```

#### `keys()`

Return a view of the Box's keys.

- **Returns:** dict_keys view
- **Example:**
  ```python
  b = Box({'a': 1, 'b': 2})
  print(list(b.keys()))  # ['a', 'b']
  ```

#### `values()`

Return a view of the Box's values.

- **Returns:** dict_values view
- **Example:**
  ```python
  b = Box({'a': 1, 'b': 2})
  print(list(b.values()))  # [1, 2]
  ```

#### `items()`

Return a view of the Box's (key, value) pairs.

- **Returns:** dict_items view
- **Example:**
  ```python
  b = Box({'a': 1, 'b': 2})
  for k, v in b.items():
      print(k, v)  # 'a' 1, 'b' 2
  ```

#### `fromkeys(keys, value=None)` (classmethod)

Create a new Box with keys from iterable and values set to value.

- **Parameters:**
  - `keys`: Iterable of keys
  - `value`: Value to set for all keys (default: None)
- **Returns:** New Box instance
- **Example:**
  ```python
  b = Box.fromkeys(['a', 'b', 'c'], 0)
  print(dict(b))  # {'a': 0, 'b': 0, 'c': 0}
  ```

#### Special Behaviors

**default_box Mode:**
When `default_box=True`, accessing missing keys automatically creates nested Box structures.

```python
b = Box(default_box=True)
b.missing.nested.key = 'value'
print(b.missing.nested.key)  # 'value'
```

**default_box_attr Option:**
Controls what type of object is created for missing keys in `default_box` mode.

```python
# Default creates nested Box
b = Box(default_box=True)
print(type(b.missing).__name__)  # 'Box'

# Custom default creates specified type
b = Box(default_box=True, default_box_attr={})
print(type(b.missing).__name__)  # 'Box' (even {} becomes Box)

b = Box(default_box=True, default_box_attr=None)
print(b.missing is None)  # True
```

**frozen_box Mode:**
When `frozen_box=True`, the Box cannot be modified.

```python
from box import Box, BoxError

b = Box({'a': 1}, frozen_box=True)
print(b.a)  # 1 (reading allowed)

try:
    b.a = 2  # Raises BoxError
except BoxError:
    print("Cannot modify frozen box")

try:
    b.new = 2  # Raises BoxError
except BoxError:
    print("Cannot add to frozen box")

try:
    del b.a  # Raises BoxError
except BoxError:
    print("Cannot delete from frozen box")
```

**camel_killer_box Mode:**
When `camel_killer_box=True`, CamelCase attribute names are automatically converted to snake_case.

```python
b = Box(camel_killer_box=True)
b.CamelCase = 'value'
print(b.camel_case)  # 'value'

b['BigKey'] = 'value'
print(b.big_key)  # 'value'
```

**Automatic Key Transformation:**
Keys with spaces, special characters, or numeric prefixes are automatically transformed to valid Python identifiers.

```python
b = Box({'key with spaces': 'value'})
print(b.key_with_spaces)  # 'value'

b = Box({'123': 'value'})
print(b.x123)  # 'value'

b = Box({'key!@#': 'value'})
print(b.key)  # 'value'
```

#### Standard dict Operations

Box supports all standard dictionary operations:

```python
b = Box({'a': 1, 'b': 2})

# Length
print(len(b))  # 2

# Iteration
for key in b:
    print(key)  # 'a', 'b'

# Boolean conversion
print(bool(Box()))  # False
print(bool(Box({'a': 1})))  # True

# Equality
b1 = Box({'a': 1})
b2 = Box({'a': 1})
print(b1 == b2)  # True

b3 = Box({'a': 2})
print(b1 != b3)  # True

# String representation
b = Box({'a': 1})
print('Box' in repr(b))  # True
print('a' in str(b))  # True
```

### Class: `BoxList`

A list subclass that automatically converts dict elements to Box instances.

#### `__init__(iterable=None, **kwargs)`

Create a new BoxList.

- **Parameters:**
  - `iterable`: Initial items for the list
  - `**kwargs`: Box constructor options for dict elements
- **Returns:** BoxList instance
- **Example:**
  ```python
  from box import BoxList
  
  bl = BoxList([1, 2, 3])
  
  # Dicts are converted to Box
  bl = BoxList([{'a': 1}, {'b': 2}])
  print(bl[0].a)  # 1
  print(bl[1].b)  # 2
  ```

#### List Operations

BoxList supports all standard list operations with automatic Box conversion.

```python
from box import BoxList

bl = BoxList([1, 2])

# Append
bl.append({'c': 3})
print(bl[2].c)  # 3

# Extend
bl.extend([4, {'d': 5}])
print(bl[4].d)  # 5

# Insert
bl = BoxList([1, 3])
bl.insert(1, {'b': 2})
print(bl[1].b)  # 2

# Indexing
bl = BoxList([1, 2, 3, 4, 5])
print(bl[1:3])  # [2, 3]

# Remove
bl = BoxList([1, 2, 3])
bl.remove(2)
print(list(bl))  # [1, 3]

# Modification
bl = BoxList([{'a': 1}])
bl[0].a = 2
print(bl[0].a)  # 2
```

### Class: `DDBox` (DefaultDictBox)

A Box variant that automatically creates nested Box structures for missing keys (equivalent to `Box(default_box=True)`).

```python
from box import DDBox

db = DDBox()
db.missing.nested = 'value'
print(db.missing.nested)  # 'value'
```

### Function: `box_from_string(string, **kwargs)`

Parse a string and create a Box from it.

- **Parameters:**
  - `string` (str): String representation of data (JSON format)
  - `**kwargs`: Additional Box constructor options
- **Returns:** Box instance
- **Example:**
  ```python
  from box import box_from_string
  
  b = box_from_string('{"a": 1}')
  print(b.a)  # 1
  ```

### Exception: `BoxError`

Base exception class for Box-specific errors.

- **Inheritance:** Inherits from `Exception`
- **Usage:** Raised for Box-specific errors like frozen box modification

### Exception: `BoxKeyError`

Exception raised when accessing missing keys in a Box.

- **Inheritance:** Inherits from both `KeyError` and `BoxError`
- **Usage:** Raised when accessing missing keys (unless `default_box=True`)

```python
from box import Box, BoxKeyError

b = Box()
try:
    value = b.missing
except BoxKeyError:
    print("Key not found")
```

# Implementation Notes

## Core Requirements

1. **Box Class:**
   - Must extend `dict`
   - Override `__getattr__`, `__setattr__`, `__delattr__` for dot notation
   - Override `__getitem__`, `__setitem__` to convert nested dicts to Box
   - Implement all dict methods with proper Box/BoxList conversion

2. **BoxList Class:**
   - Must extend `list`
   - Override `__getitem__`, `__setitem__`, `append`, `extend`, `insert` to convert dicts to Box

3. **Automatic Conversion:**
   - When a dict is added to a Box (via any method), convert it to a Box
   - When a list is added to a Box and contains dicts, convert it to a BoxList
   - Conversion should be recursive for nested structures

4. **Key Transformation:**
   - Replace spaces with underscores
   - Add 'x' prefix to numeric keys
   - Remove special characters that aren't valid in Python identifiers
   - Apply camel_killer transformation when enabled

5. **Frozen Box:**
   - Raise `BoxError` on any modification attempt (`__setattr__`, `__setitem__`, `__delattr__`, `__delitem__`, `update`, `pop`, etc.)
   - Allow reading operations

6. **Default Box:**
   - When accessing missing key via attribute, create and return new Box (or `default_box_attr` value)
   - Store the created value in the dict

7. **JSON Support:**
   - `to_json()` must recursively convert to dict/list before JSON serialization
   - `from_json()` must parse JSON and convert to Box structure

8. **Error Handling:**
   - Raise `BoxKeyError` for missing keys (not `KeyError` directly)
   - Raise `BoxError` for frozen box modifications
   - Validate frozen_box, default_box, camel_killer_box options

## Testing Considerations

- Test all dict methods with Box instances
- Test nested structure conversion (dicts, lists, mixed)
- Test frozen box immutability
- Test default box auto-creation
- Test camel_killer transformation
- Test key transformation for special characters
- Test JSON serialization/deserialization
- Test BoxList operations
- Test that copy() creates independent nested structures

## Package Structure

The package must be installable via pip with:
- Package name: `python-box`
- Import name: `box`
- Build backend: `setuptools.build_meta`
- Minimum Python version: 3.9

The `pyproject.toml` should define:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "python-box"
version = "7.4.1"
requires-python = ">=3.9"
```
