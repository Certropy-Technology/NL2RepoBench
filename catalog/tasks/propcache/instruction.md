# propcache

## Project Description

Build an installable `propcache` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `propcache`; public import package begins at `propcache`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `propcache.cached_property`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `propcache.under_cached_property`: preserve the documented object or module behavior, including state and side effects.
3. `Module facade and aliases`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Typing and fallback behavior`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `propcache`; public import package begins at `propcache`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `Cython==3.3.0`, `coverage==7.16.0`, `execnet==2.1.2`, `expandvars==1.0.0`, `iniconfig==2.3.0`, `packaging==26.3`, `pluggy==1.6.0`, `pygments==2.21.0`, `pytest==9.1.1`, `pytest-cov==7.1.0`, `pytest-xdist==3.8.0`, `setuptools==80.9.0`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── an/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

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


- Keep descriptor names stable through `__set_name__`; do not compute a cache
  key from a mutable or non-deterministic value.
- Preserve object identity for cache hits and do not share cache state between
  instances.
- The optional native implementation may use Cython, but the source tree must
  remain installable on a CPython image with the declared build dependencies.
- Keep the implementation modular enough that imports from `propcache.api`,
  `propcache._helpers`, and `propcache._helpers_py` agree on behavior.
- Do not copy evaluation tests or rely on a preinstalled `propcache` package.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
from propcache import cached_property

class Report:
    @cached_property
    def total(self):
        return sum(range(4))

report = Report()
assert report.total == 6
assert report.__dict__["total"] == 6
```

### Example 2: ordinary usage
```text
from propcache import under_cached_property

class User:
    def __init__(self):
        self._cache = {}

    @under_cached_property
    def label(self):
        return "user"

assert User().label == "user"
```

### Example 3: boundary or error behavior
```text
from propcache import cached_property

class Report:
    @cached_property
    def total(self):
        return sum(range(4))

report = Report()
assert report.total == 6
assert report.__dict__["total"] == 6
```

### Example 4: boundary or error behavior
```text
from propcache import under_cached_property

class User:
    def __init__(self):
        self._cache = {}

    @under_cached_property
    def label(self):
        return "user"

assert User().label == "user"
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
