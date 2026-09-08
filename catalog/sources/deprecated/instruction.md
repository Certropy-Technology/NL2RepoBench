# Project Description

The `deprecated` library provides Python decorators to mark functions, methods, and classes as deprecated. When deprecated code is called, it emits a `DeprecationWarning` to alert developers that the feature will be removed in a future version. The library supports both simple deprecation warnings and Sphinx-compatible documentation directives.

Target users are library maintainers who need to signal API changes to their users while maintaining backward compatibility during transition periods. The library handles function deprecation, class deprecation, method deprecation (instance, static, and class methods), and parameter deprecation.

This project excludes runtime enforcement (deprecated code still executes), automated code migration, and compile-time checking.

# Natural Language Instruction

Build the `deprecated` Python package from an empty workspace with the following capabilities:

1. **Classic deprecation decorator** (`@deprecated`) that emits `DeprecationWarning` when decorated functions, classes, or methods are called
2. **Sphinx integration decorators** (`@deprecated`, `@versionadded`, `@versionchanged`) that modify docstrings with Sphinx directives
3. **Parameter deprecation decorator** (`@deprecated_params`) that warns when specific function parameters are used
4. **Configurable warning behavior** through `reason`, `version`, `action`, and `category` parameters

The package name is `Deprecated` (PyPI) with import name `deprecated`. It must be installable via pip and support Python 3.6+. The implementation must use the `wrapt` library for proper decorator wrapping. All deprecation warnings must include the deprecated item's name in the message and respect Python's warning filter system.

# Supports (Environment Configuration)

- **Language**: Python 3.12
- **Package Manager**: pip
- **Installation**: `pip install -e .` (editable install from workspace root)
- **Runtime Dependencies**: 
  - `wrapt>=1.10,<3` (required for decorator implementation)
- **Build System**: setuptools via `setup.py` or declarative `pyproject.toml`
- **Network**: No network access during runtime (agent, candidate, verifier, and controls run offline)

# Project Directory Structure

```
workspace/
├── deprecated/
│   ├── __init__.py           # Package root, exports deprecated and deprecated_params
│   ├── classic.py            # Classic @deprecated decorator and ClassicAdapter
│   ├── sphinx.py             # Sphinx integration: deprecated, versionadded, versionchanged
│   └── params.py             # Parameter deprecation: DeprecatedParams class
├── setup.py                  # setuptools configuration with install_requires
└── pyproject.toml            # Optional: build system configuration
```

# API Usage Guide

## Module: `deprecated` (root exports)

### Function: `deprecated`
```python
from deprecated import deprecated

@deprecated
def old_function():
    pass

@deprecated(reason="use new_function instead")
def old_function2():
    pass

@deprecated(reason="obsolete", version="1.2.0")
def old_function3():
    pass

@deprecated(reason="unsafe", version="2.0.0", category=FutureWarning, action="always")
def old_function4():
    pass
```

**Import Path**: `from deprecated import deprecated` or `from deprecated.classic import deprecated`

**Signature**: 
```python
deprecated(
    *args, 
    reason: str = "",
    version: str = "",
    action: Literal["default", "error", "ignore", "always", "module", "once"] = None,
    category: Type[Warning] = DeprecationWarning,
    adapter_cls: Type[ClassicAdapter] = ClassicAdapter,
    extra_stacklevel: int = 0
) -> Callable
```

**Parameters**:
- `reason` (str, optional): Human-readable explanation of why the item is deprecated and what to use instead
- `version` (str, optional): Version number when deprecation started (e.g., "1.2.0")
- `action` (str, optional): Warning filter action - one of "default", "error", "ignore", "always", "module", "once". If `None`, uses global filter
- `category` (Type[Warning], optional): Warning class to use (default: `DeprecationWarning`)
- `adapter_cls` (Type, optional): Advanced - custom adapter class for message formatting
- `extra_stacklevel` (int, optional): Additional stack levels to attribute warning to caller
- First positional argument can be a string (shorthand for `reason`) or the decorated callable

**Returns**: Decorated function, method, or class that emits a deprecation warning when called/instantiated

**Behavior**:
- For functions and methods: warning emitted each time the function is called
- For classes: warning emitted each time the class is instantiated (via `__new__`)
- Warning message format:
  - Functions: "Call to deprecated function (or staticmethod) {name}."
  - Methods: "Call to deprecated method {name}."
  - Class methods: "Call to deprecated class method {name}."
  - Classes: "Call to deprecated class {name}."
  - Appends " ({reason})" if reason provided
  - Appends " -- Deprecated since version {version}." if version provided
- Respects Python's warning filtering system via `warnings` module
- When `action` is set, temporarily overrides warning filter for that specific warning

**Example**:
```python
import warnings
from deprecated import deprecated

@deprecated(reason="use new_api() instead", version="1.5.0")
def old_api():
    return "data"

# Calling old_api() emits: DeprecationWarning: Call to deprecated function (or staticmethod) old_api. 
# (use new_api() instead) -- Deprecated since version 1.5.0.
warnings.simplefilter("always")
result = old_api()  # Returns "data" but warns
```

### Function: `deprecated_params`
```python
from deprecated import deprecated_params

@deprecated_params("old_param")
def function(old_param=None, new_param=None):
    pass

@deprecated_params("x", reason="use y instead")
def function2(x=None, y=None):
    pass

@deprecated_params({"a": "a is deprecated", "b": "use b_new"})
def function3(a=None, b=None):
    pass
```

**Import Path**: `from deprecated import deprecated_params` or `from deprecated.params import deprecated_params` or `from deprecated.params import DeprecatedParams`

**Signature**:
```python
deprecated_params(
    param: Union[str, Dict[str, str]],
    reason: str = "",
    category: Type[Warning] = DeprecationWarning
) -> Callable
```

**Parameters**:
- `param`: Either a string (parameter name) or dict mapping parameter names to custom deprecation messages
- `reason` (str, optional): Deprecation message when `param` is a string. Defaults to "'{param}' parameter is deprecated"
- `category` (Type[Warning], optional): Warning class (default: `DeprecationWarning`)

**Returns**: Decorated function that warns when deprecated parameters are used

**Behavior**:
- Inspects function signature to detect when deprecated parameters are bound (positional or keyword)
- Only emits warning if the deprecated parameter is actually provided in the call
- Multiple deprecated parameters each emit their own warning
- Uses `stacklevel=3` to point to the caller's location

**Example**:
```python
from deprecated import deprecated_params

@deprecated_params({"old_arg": "old_arg is obsolete, use new_arg"})
def process(old_arg=None, new_arg=None):
    return new_arg or old_arg

# Warns only when old_arg is provided
process(new_arg=5)     # No warning
process(old_arg=10)    # Warns: "old_arg is obsolete, use new_arg"
```

## Module: `deprecated.sphinx`

### Function: `deprecated` (Sphinx variant)
```python
from deprecated.sphinx import deprecated

@deprecated(version="1.0.0")
def old_function():
    '''Original docstring.'''
    pass
```

**Import Path**: `from deprecated.sphinx import deprecated`

**Signature**:
```python
deprecated(
    reason: str = "",
    version: str = "",  # REQUIRED
    line_length: int = 70,
    action: str = None,
    category: Type[Warning] = DeprecationWarning,
    extra_stacklevel: int = 0
) -> Callable
```

**Parameters**:
- `version` (str, **required**): Version when deprecated (e.g., "1.2.0"). Raises `ValueError` if empty
- `reason` (str, optional): Deprecation reason, inserted into Sphinx directive
- `line_length` (int, optional): Maximum line width for wrapping reason text in docstring (default: 70)
- `action`, `category`, `extra_stacklevel`: Same as classic `@deprecated`

**Returns**: Decorated function/class with modified docstring containing Sphinx `.. deprecated::` directive

**Behavior**:
- **Modifies `__doc__`**: Appends Sphinx directive to existing docstring
- **Emits warning**: Same runtime warning behavior as classic `@deprecated`
- **Directive format**:
  ```
  .. deprecated:: {version}
     {reason, wrapped to line_length}
  ```
- Reason text is dedented, split into paragraphs, and wrapped to `line_length - 3` characters
- Preserves existing docstring content, adding directive after blank line separator
- Strips Sphinx cross-reference syntax from warning messages (e.g., `:func:\`name\`` becomes `name`)

**Example**:
```python
from deprecated.sphinx import deprecated

@deprecated(reason="Use new_function() for better performance.", version="2.0.0")
def old_function():
    '''Processes data.'''
    return 42

# Docstring becomes:
# '''Processes data.
#
# .. deprecated:: 2.0.0
#    Use new_function() for better performance.
# '''

# Runtime: emits DeprecationWarning when called
```

### Function: `versionadded`
```python
from deprecated.sphinx import versionadded

@versionadded(version="1.0.0")
def new_function():
    '''New feature.'''
    pass
```

**Import Path**: `from deprecated.sphinx import versionadded`

**Signature**:
```python
versionadded(
    reason: str = "",
    version: str = "",  # REQUIRED
    line_length: int = 70
) -> Callable
```

**Parameters**:
- `version` (str, **required**): Version when feature was added
- `reason` (str, optional): Description of what was added
- `line_length` (int): Maximum line width for text wrapping

**Returns**: Decorated function/class with Sphinx `.. versionadded::` directive in docstring

**Behavior**:
- **Modifies `__doc__` only** - does NOT emit runtime warnings
- Appends Sphinx directive similar to `deprecated()` but using `versionadded`
- Raises `ValueError` if `version` is missing

**Example**:
```python
@versionadded(reason="Initial implementation", version="1.0.0")
def new_feature():
    return "result"

# No warning emitted, only docstring modified
```

### Function: `versionchanged`
```python
from deprecated.sphinx import versionchanged

@versionchanged(version="2.0.0")
def modified_function():
    '''Changed behavior.'''
    pass
```

**Import Path**: `from deprecated.sphinx import versionchanged`

**Signature**: Same as `versionadded`

**Returns**: Decorated function/class with Sphinx `.. versionchanged::` directive in docstring

**Behavior**:
- **Modifies `__doc__` only** - does NOT emit runtime warnings
- Appends `.. versionchanged:: {version}` directive
- Raises `ValueError` if `version` is missing

## Module: `deprecated.classic`

### Class: `ClassicAdapter`

**Import Path**: `from deprecated.classic import ClassicAdapter`

Advanced usage only. Base adapter class that formats deprecation messages and applies warnings. Can be subclassed to customize message formatting.

**Methods**:
- `__init__(reason, version, action, category, extra_stacklevel)`: Initialize adapter
- `get_deprecated_msg(wrapped, instance)`: Generate warning message text
- `__call__(wrapped)`: Apply deprecation to wrapped object

Users typically do not instantiate this directly; it's used internally by `@deprecated`.

# Implementation Notes

## Core Decorator Requirements

1. **Decorator stacking**: Must work with `@staticmethod`, `@classmethod`, and custom decorators
2. **Signature preservation**: Use `wrapt.decorator` to preserve function signatures and metadata
3. **Warning attribution**: Set correct `stacklevel` so warnings point to caller, not decorator
   - Functions/methods: typically `stacklevel=2` (pure Python `wrapt`)
   - Classes: `stacklevel=2` or `3` depending on `wrapt` C extension availability
4. **`wrapt` detection**: Check for `wrapt._wrappers` module to determine if C extension is loaded

## Class Deprecation Implementation

Deprecated classes must override `__new__` to emit the warning before instance creation:
```python
old_new = wrapped.__new__
def wrapped_new(cls, *args, **kwargs):
    warnings.warn(msg, category=category, stacklevel=stacklevel)
    if old_new is object.__new__:
        return old_new(cls)  # Don't pass args to object.__new__
    return old_new(cls, *args, **kwargs)
wrapped.__new__ = staticmethod(wrapped_new)
```

## Sphinx Directive Format

Sphinx directives must follow strict formatting:
- Directive line: `.. {directive}:: {version}` or `.. {directive}::` (no version)
- Reason indented with 3 spaces
- Empty line separates original docstring from directive block
- If original docstring is empty, insert one newline before directive to avoid Sphinx "explicit markup ends without a blank line" error

## Parameter Deprecation

Use `inspect.signature(f).bind(*args, **kwargs)` to detect which parameters were provided. Only warn when a deprecated parameter is actually bound in the call.

## Warning Filter Interaction

When `action` is set (e.g., "always", "error", "ignore"):
```python
with warnings.catch_warnings():
    warnings.simplefilter(action, category)
    warnings.warn(msg, category=category, stacklevel=stacklevel)
```

When `action` is `None` or empty, call `warnings.warn()` directly to use global filter.

## Deterministic Behavior

- Deprecation state is applied at decoration time (function/class definition)
- Each call/instantiation emits a warning according to current warning filter state
- No global mutable state; each decorator instance is independent
- Multiple decorators on same function stack correctly

# Examples

## Basic Function Deprecation
```python
from deprecated import deprecated

@deprecated
def old_function(x):
    return x * 2

# Emits: DeprecationWarning: Call to deprecated function (or staticmethod) old_function.
result = old_function(5)  # Returns 10
```

## Class Deprecation with Reason and Version
```python
from deprecated import deprecated

@deprecated(reason="Use NewClass instead", version="2.0.0")
class OldClass:
    def __init__(self, value):
        self.value = value

# Emits warning on instantiation
obj = OldClass(42)  # obj.value == 42
```

## Method Deprecation
```python
from deprecated import deprecated

class DataProcessor:
    @deprecated(reason="use process_v2()")
    def process(self, data):
        return data.upper()
    
    def process_v2(self, data):
        return data.lower()

dp = DataProcessor()
dp.process("Text")  # Warns and returns "TEXT"
```

## Parameter Deprecation
```python
from deprecated import deprecated_params

@deprecated_params({"old_format": "old_format is deprecated, use new_format"})
def format_data(data, old_format=False, new_format=True):
    if old_format:
        return data.upper()
    return data.lower()

format_data("Test", new_format=True)   # No warning
format_data("Test", old_format=True)    # Warns
```

## Sphinx Documentation
```python
from deprecated.sphinx import deprecated, versionadded, versionchanged

@versionadded(reason="New feature", version="1.0.0")
def new_feature():
    '''Implements new capability.'''
    return "result"

@versionchanged(reason="Improved algorithm", version="1.5.0")
def improved_feature():
    '''Existing feature.'''
    return "better"

@deprecated(reason="Use new_feature() instead", version="2.0.0")
def old_feature():
    '''Legacy implementation.'''
    return "legacy"

# Only old_feature() emits runtime warning
# All three have modified docstrings with Sphinx directives
```

## Custom Warning Category
```python
from deprecated import deprecated

class APIDeprecationWarning(DeprecationWarning):
    pass

@deprecated(category=APIDeprecationWarning, action="error")
def critical_deprecated():
    return "value"

# Raises APIDeprecationWarning exception (action="error")
```

# Error Handling and Boundary Conditions

## Required Parameters

- `deprecated.sphinx.deprecated()`, `versionadded()`, and `versionchanged()` **require** `version` parameter
- Calling without `version` raises `ValueError`

```python
from deprecated.sphinx import deprecated

try:
    @deprecated()  # Missing version
    def func():
        pass
except ValueError:
    print("version is required")
```

## Decorator Application

- `@deprecated` works on functions, classes, instance methods, static methods, class methods
- Raises `TypeError` if applied to non-callable or unsupported types
- Nested decorators work correctly (decorator stacking is supported)

## Warning Emission

- Warnings are emitted **every time** a deprecated item is called (unless filtered by `action` or global filter)
- `action="once"` emits warning only on first call per location
- `action="ignore"` suppresses all warnings for that decorator
- `action="error"` converts warning to exception

## Return Value and Exception Preservation

- Decorated functions/methods return original values unmodified
- Exceptions raised in decorated code propagate normally
- Warning emission happens before function execution

```python
@deprecated
def failing_function():
    raise ValueError("error")

# Emits deprecation warning, then raises ValueError
failing_function()
```

## Parameter Deprecation Edge Cases

- `deprecated_params` only warns if deprecated parameter is **actually provided**
- Works with positional and keyword arguments
- Multiple deprecated parameters each generate separate warnings
- Unknown parameters are ignored (no validation beyond signature binding)

## Docstring Handling

- Sphinx decorators handle `None` docstrings (create minimal valid docstring)
- Preserve existing docstring formatting and content
- Multiple Sphinx directives can be stacked on same function

# Security

This library uses the Python `warnings` module which is part of the standard library and does not introduce security risks. The library:
- Does not execute arbitrary code from strings
- Does not access filesystem or network
- Does not modify global interpreter state beyond standard warning filters
- Uses `wrapt` for safe decorator application without eval/exec

Warning messages may include function/class names and user-provided `reason` strings. These are included in warning output but not executed or interpreted.
