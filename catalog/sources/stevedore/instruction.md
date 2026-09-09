# Project Description

`stevedore` is a Python library for managing dynamic plugins using setuptools entry points. It provides a consistent interface for discovering and loading extensions at runtime, eliminating the need for applications to implement their own plugin loading mechanisms. The library builds on setuptools entry points to provide manager classes that implement common patterns for using dynamically loaded extensions, including single driver selection, named extension loading, and hook-based extension invocation.

The library is widely used in the OpenStack ecosystem and provides type-annotated interfaces for ExtensionManager, DriverManager, NamedExtensionManager, EnabledExtensionManager, and HookManager patterns.

# Natural Language Instruction

Implement a Python package named `stevedore` that provides plugin management capabilities using setuptools entry points. The package must:

1. Provide an `ExtensionManager` class that discovers and loads all extensions in a given namespace
2. Provide a `DriverManager` class that loads a single named driver from a namespace
3. Provide a `NamedExtensionManager` class that loads specific named extensions from a namespace
4. Provide an `EnabledExtensionManager` class that filters extensions based on a check function
5. Provide a `HookManager` class for hook-based extension invocation
6. Define exception classes: `NoUniqueMatch`, `NoMatches`, and `MultipleMatches` for error handling
7. Support extension metadata access (name, module_name, attr, entry_point_target, plugin, obj)
8. Provide map(), names(), and iteration interfaces for all managers
9. Handle missing entry points gracefully with configurable callbacks
10. Support lazy loading (invoke_on_load=False) and eager loading
11. Include example formatter plugins and test plugins as entry points for testing

The package name is `stevedore`, the import name is `stevedore`, and it must be installable via pip with no runtime dependencies.

# Supports (Environment Configuration)

- Python: 3.11+
- Package Manager: pip
- Build System: `pbr` (Python Build Reasonableness)
- Runtime Dependencies: None (uses only Python standard library: importlib.metadata, collections.abc, logging)
- Installation: `pip install .` or `pip install -e .`
- Entry Points: Includes stevedore.example.formatter and stevedore.test.extension namespaces
- No network access required during runtime

# Project Directory Structure

```
workspace/
├── pyproject.toml
├── setup.cfg
├── setup.py
├── LICENSE
├── README.rst
├── stevedore/
│   ├── __init__.py
│   ├── extension.py          # ExtensionManager and Extension classes
│   ├── driver.py              # DriverManager class
│   ├── named.py               # NamedExtensionManager class
│   ├── enabled.py             # EnabledExtensionManager class
│   ├── hook.py                # HookManager class
│   ├── exception.py           # Exception classes
│   ├── _cache.py              # Internal caching utilities
│   ├── dispatch.py            # Dispatch utilities
│   ├── sphinxext.py           # Sphinx extension
│   ├── py.typed               # PEP 561 marker
│   ├── example/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── simple.py          # Simple formatter class
│   │   ├── load_as_driver.py
│   │   └── load_as_extension.py
│   ├── example2/
│   │   ├── __init__.py
│   │   └── fields.py          # FieldList formatter class
│   └── tests/
│       ├── __init__.py
│       └── test_extension.py  # FauxExtension and BrokenExtension classes
```

# API Usage Guide

## Module: `stevedore`

The root module exports the primary manager classes:

```python
from stevedore import (
    ExtensionManager,
    DriverManager,
    NamedExtensionManager,
    EnabledExtensionManager,
    HookManager,
)
```

## Module: `stevedore.exception`

Exception hierarchy for plugin loading errors:

### `class NoUniqueMatch(RuntimeError)`

Base exception indicating no unique match was found (zero or multiple matches).

### `class NoMatches(NoUniqueMatch)`

Raised when no extensions with the specified name are found.

### `class MultipleMatches(NoUniqueMatch)`

Raised when multiple extensions match a query expecting a single result.

**Example:**
```python
from stevedore.exception import NoMatches, NoUniqueMatch
try:
    raise NoMatches("No driver found")
except NoUniqueMatch:
    print("Caught as NoUniqueMatch")
```

## Class: `stevedore.extension.Extension`

Represents a single loaded extension with metadata.

### Attributes

- `name` (str): The entry point name
- `entry_point` (importlib.metadata.EntryPoint): The entry point object
- `plugin` (type[T]): The loaded class or callable
- `obj` (T | None): The instantiated object if invoke_on_load=True, otherwise None

### Properties

- `module_name` (str): The module name (e.g., "stevedore.example.simple")
- `attr` (str): The attribute name (e.g., "Simple")
- `entry_point_target` (str): The full target string (e.g., "stevedore.example.simple:Simple")

**Example:**
```python
from stevedore import ExtensionManager
mgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)
ext = mgr.extensions[0]
print(ext.name)               # 'simple'
print(ext.module_name)        # 'stevedore.example.simple'
print(ext.attr)               # 'Simple'
print(ext.entry_point_target) # 'stevedore.example.simple:Simple'
print(ext.plugin)             # <class 'stevedore.example.simple.Simple'>
print(ext.obj)                # None (invoke_on_load=False)
```

## Class: `stevedore.ExtensionManager`

Discovers and loads all extensions in a namespace.

### `__init__(namespace, invoke_on_load=False, invoke_args=None, invoke_kwds=None, on_load_failure_callback=None, verify_requirements=None, warn_on_missing_entrypoint=None, conflict_resolver=None)`

Initialize the extension manager.

- **Parameters:**
  - `namespace` (str): Entry point namespace to query
  - `invoke_on_load` (bool): Whether to instantiate plugins on load (default: False)
  - `invoke_args` (tuple | None): Positional arguments for plugin instantiation
  - `invoke_kwds` (dict | None): Keyword arguments for plugin instantiation
  - `on_load_failure_callback` (Callable | None): Callback for load failures
  - `verify_requirements` (bool | None): **DEPRECATED** No-op parameter
  - `warn_on_missing_entrypoint` (bool | None): **DEPRECATED** Control missing entry point warnings
  - `conflict_resolver` (Callable | None): Handler for duplicate entry point names

- **Attributes:**
  - `extensions` (list[Extension]): List of loaded Extension objects

### `names() -> list[str]`

Return a list of extension names.

**Returns:** List of entry point names as strings

**Example:**
```python
from stevedore import ExtensionManager
mgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)
print(mgr.names())  # ['field', 'plain', 'simple']
```

### `map(func) -> list`

Apply a function to all extensions and return results.

- **Parameters:**
  - `func` (Callable[[Extension], T]): Function to apply to each extension
- **Returns:** List of results

**Example:**
```python
from stevedore import ExtensionManager
mgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)
plugins = mgr.map(lambda ext: ext.plugin.__name__)
print(sorted(plugins))  # ['FieldList', 'Simple', 'Simple']
```

### `__iter__() -> Iterator[Extension]`

Iterate over all extensions.

**Example:**
```python
from stevedore import ExtensionManager
mgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)
for ext in mgr:
    print(ext.name, ext.plugin.__name__)
```

## Class: `stevedore.DriverManager`

Loads a single named driver from a namespace. Inherits from NamedExtensionManager.

### `__init__(namespace, name, invoke_on_load=False, invoke_args=None, invoke_kwds=None, on_load_failure_callback=None, on_missing_entrypoints_callback=None, verify_requirements=None, warn_on_missing_entrypoint=None, conflict_resolver=None)`

Initialize the driver manager.

- **Parameters:**
  - `namespace` (str): Entry point namespace
  - `name` (str): The driver name to load
  - `invoke_on_load` (bool): Whether to instantiate the driver on load
  - `invoke_args` (tuple | None): Positional arguments for instantiation
  - `invoke_kwds` (dict | None): Keyword arguments for instantiation
  - `on_load_failure_callback` (Callable | None): Callback for load failures (default raises)
  - `on_missing_entrypoints_callback` (Callable | None): Callback for missing drivers
  - `verify_requirements` (bool | None): **DEPRECATED**
  - `warn_on_missing_entrypoint` (bool | None): **DEPRECATED**
  - `conflict_resolver` (Callable | None): Handler for duplicate names

- **Attributes:**
  - `driver` (type[T]): The loaded driver class
  - `extensions` (list[Extension]): List with single Extension

- **Raises:**
  - `NoMatches`: If the specified driver name is not found

**Example:**
```python
from stevedore import DriverManager
from stevedore.exception import NoMatches

dm = DriverManager(namespace='stevedore.example.formatter', name='simple', invoke_on_load=False)
print(dm.driver.__name__)  # 'Simple'
print(dm.extensions[0].name)  # 'simple'

try:
    dm = DriverManager(namespace='stevedore.example.formatter', name='nonexistent', invoke_on_load=False)
except NoMatches as e:
    print(f"Driver not found: {e}")
```

## Class: `stevedore.NamedExtensionManager`

Loads specific named extensions from a namespace. Inherits from ExtensionManager.

### `__init__(namespace, names, invoke_on_load=False, invoke_args=None, invoke_kwds=None, on_load_failure_callback=None, on_missing_entrypoints_callback=None, verify_requirements=None, warn_on_missing_entrypoint=None, name_order=None, conflict_resolver=None)`

Initialize the named extension manager.

- **Parameters:**
  - `namespace` (str): Entry point namespace
  - `names` (list[str]): List of extension names to load
  - `invoke_on_load` (bool): Whether to instantiate plugins on load
  - `invoke_args` (tuple | None): Positional arguments for instantiation
  - `invoke_kwds` (dict | None): Keyword arguments for instantiation
  - `on_load_failure_callback` (Callable | None): Callback for load failures
  - `on_missing_entrypoints_callback` (Callable | None): Callback for missing names (default warns)
  - `verify_requirements` (bool | None): **DEPRECATED**
  - `warn_on_missing_entrypoint` (bool | None): **DEPRECATED**
  - `name_order` (bool | None): Whether to preserve name order
  - `conflict_resolver` (Callable | None): Handler for duplicate names

- **Behavior:**
  - Silently skips names not found in the namespace (unless callback raises)
  - Deduplicates requested names (requests for same name multiple times load once)

**Example:**
```python
from stevedore import NamedExtensionManager

nm = NamedExtensionManager(
    namespace='stevedore.example.formatter',
    names=['simple', 'field'],
    invoke_on_load=False
)
print(sorted([e.name for e in nm.extensions]))  # ['field', 'simple']

nm = NamedExtensionManager(
    namespace='stevedore.example.formatter',
    names=['simple', 'nonexistent'],
    invoke_on_load=False,
    warn_on_missing_entrypoint=False
)
print([e.name for e in nm.extensions])  # ['simple'] - missing name skipped
```

## Class: `stevedore.EnabledExtensionManager`

Loads extensions filtered by a check function. Inherits from ExtensionManager.

### `__init__(namespace, check_func, invoke_on_load=False, invoke_args=None, invoke_kwds=None, on_load_failure_callback=None, verify_requirements=None, warn_on_missing_entrypoint=None, conflict_resolver=None)`

Initialize the enabled extension manager.

- **Parameters:**
  - `namespace` (str): Entry point namespace
  - `check_func` (Callable[[Extension], bool]): Function to filter extensions (return True to include)
  - `invoke_on_load` (bool): Whether to instantiate plugins on load
  - `invoke_args` (tuple | None): Positional arguments for instantiation
  - `invoke_kwds` (dict | None): Keyword arguments for instantiation
  - `on_load_failure_callback` (Callable | None): Callback for load failures
  - `verify_requirements` (bool | None): **DEPRECATED**
  - `warn_on_missing_entrypoint` (bool | None): **DEPRECATED**
  - `conflict_resolver` (Callable | None): Handler for duplicate names

**Example:**
```python
from stevedore import EnabledExtensionManager

def check_simple(ext):
    return 'simple' in ext.name.lower()

em = EnabledExtensionManager(
    namespace='stevedore.example.formatter',
    check_func=check_simple,
    invoke_on_load=False
)
print(sorted([e.name for e in em.extensions]))  # ['plain', 'simple']
```

## Class: `stevedore.HookManager`

Manages hooks for event-driven extension invocation. Inherits from NamedExtensionManager.

### `__init__(namespace, name, invoke_on_load=False, invoke_args=None, invoke_kwds=None, on_load_failure_callback=None, on_missing_entrypoints_callback=None, verify_requirements=None, warn_on_missing_entrypoint=None)`

Initialize the hook manager.

- **Parameters:**
  - `namespace` (str): Entry point namespace
  - `name` (str): Hook name
  - `invoke_on_load` (bool): Whether to instantiate plugins on load
  - `invoke_args` (tuple | None): Positional arguments for instantiation
  - `invoke_kwds` (dict | None): Keyword arguments for instantiation
  - `on_load_failure_callback` (Callable | None): Callback for load failures
  - `on_missing_entrypoints_callback` (Callable | None): Callback for missing hooks
  - `verify_requirements` (bool | None): **DEPRECATED**
  - `warn_on_missing_entrypoint` (bool | None): **DEPRECATED**

**Note:** HookManager requires both `namespace` and `name` parameters.

# Implementation Notes

## Entry Points

The package must define the following entry points in pyproject.toml or setup.cfg:

```toml
[project.entry-points."stevedore.example.formatter"]
simple = "stevedore.example.simple:Simple"
field = "stevedore.example2.fields:FieldList"
plain = "stevedore.example.simple:Simple"

[project.entry-points."stevedore.test.extension"]
t1 = "stevedore.tests.test_extension:FauxExtension"
t2 = "stevedore.tests.test_extension:FauxExtension"
e1 = "stevedore.tests.test_extension:BrokenExtension"
```

## Example Plugin Classes

The package includes example formatter classes:

- `stevedore.example.simple.Simple`: Basic formatter example
- `stevedore.example2.fields.FieldList`: Field-based formatter example

And test extension classes:

- `stevedore.tests.test_extension.FauxExtension`: Mock extension for testing
- `stevedore.tests.test_extension.BrokenExtension`: Extension that simulates load failures

These classes are minimal and serve as entry point targets. They do not need full implementations.

## Build Configuration

The package uses `pbr` (Python Build Reasonableness) as the build backend:

```toml
[build-system]
requires = ["pbr>=6.1.1"]
build-backend = "pbr.build"

[project]
name = "stevedore"
dynamic = ["version", "dependencies"]
requires-python = ">=3.11"
license = "Apache-2.0"
```

Version is managed by pbr and derived from git tags or setup.cfg.

## Type Annotations

The package uses modern Python type hints with:
- Generic types (Extension[T], ExtensionManager[T])
- ParamSpec for callback type hints
- TypeAlias for complex callback signatures
- A `py.typed` marker file for PEP 561 compliance

## Logging

The package uses the Python logging module with logger name 'stevedore' and adds a NullHandler to avoid logging errors when the application doesn't configure logging.

## Conflict Resolution

When multiple entry points have the same name in a namespace, the default behavior is to raise `MultipleMatches`. The `conflict_resolver` parameter allows customization.

## Legacy Parameters

The `verify_requirements` and `warn_on_missing_entrypoint` parameters are deprecated and have no effect. They are retained for backward compatibility.

## Empty Namespaces

Managers gracefully handle namespaces with no entry points, returning empty extension lists rather than raising exceptions.
