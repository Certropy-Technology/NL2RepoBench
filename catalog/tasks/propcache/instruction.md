# Build `propcache`

Create a complete, installable Python project named `propcache` from an empty
workspace. It is a small descriptor library that provides a fast property cache
for ordinary Python classes. The package must work on CPython 3.12 without
network access at runtime and must not require the hidden verifier files.

## Project Description

The distribution exposes two descriptors. `cached_property` stores the first
computed value in the instance's `__dict__`, matching the useful behavior of
`functools.cached_property`. `under_cached_property` stores values in a
caller-owned `_cache` mapping, which is useful for objects that control their
cache layout. Both descriptors preserve the wrapped callable and docstring,
support class-level introspection, and are usable as generic aliases at runtime.

The frozen upstream release reports `propcache.__version__ == "0.5.2"`.

## Supports

- Support CPython 3.10 and newer Python 3.x versions, with CPython 3.12 as the
  evaluation runtime.
- Provide a PEP 517 installable project, preferably using the upstream-style
  `src/propcache/` layout, and include `propcache/py.typed`.
- Provide the public `propcache` package and the public submodule
  `propcache.api`. There are no third-party runtime dependencies.
- A pure-Python implementation is required and must be the fallback when
  `PROPCACHE_NO_EXTENSIONS` is set or an optional native extension cannot be
  imported. A Cython extension may be supplied, but it must not be necessary
  for ordinary installation or behavior.
- Normal descriptor use performs no network, subprocess, filesystem, or
  service operation. Runtime dependency installation is a build-time concern.

## API Usage Guide

### `propcache.cached_property`

Import path: `propcache.cached_property` and `propcache.api.cached_property`.

Signature: `cached_property(func)` where `func` is a callable accepting the
instance and returning any value. The decorator returns a descriptor.

On first access through an instance, call `func(instance)`, store the returned
value under the descriptor's attribute name in `instance.__dict__`, and return
it. Later reads return the exact cached object without calling `func` again.
Deleting that instance dictionary entry makes the next read compute a fresh
value. Assignment to the attribute is allowed using normal non-data-descriptor
behavior and can replace the cached value. Access through the class returns the
descriptor itself.

The descriptor exposes the wrapped callable as `.func` and its `__doc__` is the
wrapped function's docstring. Python invokes `__set_name__(owner, name)` during
class creation; an instance manually attached under a different second name
must raise `TypeError`. Accessing an instance without a `__dict__` must raise
the normal `TypeError` or `AttributeError` from the cache operation.

Example:

```python
from propcache import cached_property

class Report:
    @cached_property
    def total(self):
        return sum(range(4))

report = Report()
assert report.total == 6
assert report.__dict__["total"] == 6
```

### `propcache.under_cached_property`

Import path: `propcache.under_cached_property` and
`propcache.api.under_cached_property`.

Signature: `under_cached_property(wrapped)` where `wrapped` accepts the
instance. The descriptor uses `instance._cache[self.name]` as its storage.
If that key exists, return the stored value. Otherwise call the wrapped
function, store its result under the key, and return it. The mapping is owned by
the instance and may be a dict-like `Mapping` that supports assignment.

This is a data descriptor: assigning to the property raises
`AttributeError("cached property is read-only")`. Reading an instance without
`_cache`, or with a cache that cannot be indexed, propagates the resulting
`AttributeError`, `KeyError`, or mapping error. Class access returns the
descriptor. The pure-Python descriptor exposes `.wrapped`, and the wrapped
docstring is available through `__doc__`; the cache key is the declared
attribute name even when the native implementation keeps that name private.

Example:

```python
from propcache import under_cached_property

class User:
    def __init__(self):
        self._cache = {}

    @under_cached_property
    def label(self):
        return "user"

assert User().label == "user"
```

### Module facade and aliases

`propcache.api.__all__` contains exactly `("cached_property",
"under_cached_property")`. The same two objects are available from
`propcache._helpers`, while the top-level package lazily exposes them through
`__getattr__`. `propcache.__all__` is empty, so wildcard import does not expose
the facade API. `dir(propcache)` nevertheless includes both public names.

The top-level and API objects must be identical, and invalid attributes must
raise `AttributeError` with the usual module-style message. The package must
also expose `propcache.__version__` with value `"0.5.2"`.

### Typing and fallback behavior

`cached_property[int]` and `under_cached_property[int]` must be valid runtime
subscription expressions (a `types.GenericAlias` or equivalent is acceptable).
`propcache._helpers_py` must expose the pure-Python implementations and its
objects must have the same descriptor behavior as the public fallback. Setting
`PROPCACHE_NO_EXTENSIONS` must select that fallback without changing the public
API contract.

## Implementation Notes

- Keep descriptor names stable through `__set_name__`; do not compute a cache
  key from a mutable or non-deterministic value.
- Preserve object identity for cache hits and do not share cache state between
  instances.
- The optional native implementation may use Cython, but the source tree must
  remain installable on a CPython image with the declared build dependencies.
- Keep the implementation modular enough that imports from `propcache.api`,
  `propcache._helpers`, and `propcache._helpers_py` agree on behavior.
- Do not copy hidden tests or rely on a preinstalled `propcache` package.
