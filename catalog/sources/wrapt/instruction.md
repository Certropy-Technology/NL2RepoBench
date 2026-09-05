# Project Description

Create an installable Python package named `wrapt` from an empty workspace. It
is a decorator and object-proxy library whose public behavior must remain
transparent to callers: wrapped objects keep their normal operations,
introspection, attribute semantics, and binding behavior.

# Natural Language Instruction

Create the `wrapt` project from an empty workspace. Implement transparent
object proxies, callable and lazy proxies, function wrappers and decorators,
signature overlays, reversible patching and wrapper chains, caching and
synchronization, coroutine conversion, lazy imports, and post-import hooks.
Preserve special-method dispatch, descriptor binding, object identity,
exception identity, and the separation between proxy-only and wrapped state.
The pure-Python implementation must remain correct when optional acceleration
is disabled.

# Supports

- CPython 3.12 on Linux amd64, installed with `python -m pip install .`.
- Distribution version `2.4.0rc5`, import package `wrapt`, and the public names
  exported by `wrapt.__all__`.
- A pure-Python implementation is required. The optional C extension
  `wrapt._wrappers` may be built when a compiler is available, but behavior
  must remain correct when it is disabled with `WRAPT_INSTALL_EXTENSIONS=false`
  or `WRAPT_DISABLE_EXTENSIONS=1`.
- Deterministic local operation only. Do not require a network, service,
  database, subprocess, or files outside the package and the caller's objects.
- Agent, candidate, verifier, Oracle, and controls are NoNetwork. They must
  not access GitHub, package indexes, DNS, external services, or downloads.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── setup.py
├── src/
│   └── wrapt/
│       ├── __init__.py
│       ├── decorators.py
│       ├── wrappers.py
│       ├── patch.py
│       ├── import_hooks.py
│       ├── exceptions.py
│       └── py.typed
└── README.md
```

The source layout may use an equivalent build configuration, but the installed
distribution must expose every documented `wrapt` import path. Evaluator files,
reference source, private reports, and dependency caches are not project files.

# API Usage Guide

## Object proxies

`wrapt.ObjectProxy(wrapped)` returns a transparent proxy for `wrapped`.
Attribute reads and writes, `str`, equality, hashing, containment, iteration,
arithmetic, `len`, and context-manager operations are delegated to the wrapped
object. `repr(proxy)` identifies the proxy rather than pretending to be the
wrapped object's repr; `os.fspath(proxy)` is intentionally rejected by the
upstream contract. The underlying object is available as the
read-only `__wrapped__` attribute. Proxy-only state may be stored with
`_self_`-prefixed attributes and must not leak into the wrapped object's
attributes. `CallableObjectProxy` additionally forwards calls, and
`PartialCallableObjectProxy` provides partial application.

`AutoObjectProxy(factory)` and `LazyObjectProxy(factory)` defer construction
until the wrapped value is first needed. `lazy_import(name, attribute=None,
*, interface=...)` creates a lazy proxy for an importable module or attribute.

## Function wrappers and decorators

`FunctionWrapper(wrapped, wrapper, enabled=None)` calls `wrapper(wrapped,
instance, args, kwargs)` around each invocation. It preserves the wrapped
function's observable name, module, docstring, annotations, and binding to
instances, class methods, and static methods. `BoundFunctionWrapper` is the
bound view and `partial` creates a callable proxy with pre-applied arguments.

`@wrapt.decorator` turns a wrapper function with the same four-argument
contract into a reusable decorator. Its `enabled` option can be a boolean or a
callable predicate. `adapter` may provide a prototype whose signature is
exposed through `inspect.signature` while calls still reach the wrapped
function. `with_signature(wrapped, *, prototype=None, signature=None,
factory=None)` supplies the same signature overlay explicitly.

## Patching and wrapper chains

`wrap_function_wrapper(target, name, wrapper)` and
`wrap_object(target, name, factory, args=(), kwargs=None)` install wrappers and
return a handle. `transient_function_wrapper(target, name)` applies a wrapper
for the duration of a `with` block. `unwrap_object(target, name, handle,
*, missing_ok=False)` removes a matching wrapper and restores the prior
attribute. `wrapper_chain(obj, *, limit=64)` returns the ordered wrapt chain;
`unwrapped(obj, *, limit=64)` returns the terminal wrapped object;
`find_wrapper` and `is_wrapped_by` inspect a chain without relying on equality.
`resolve_path` and `resolve_owner` resolve dotted module/class attributes.

## Caching, synchronization, and import hooks

`lru_cache(func=None, /, **kwargs)` behaves like a transparent cached function
wrapper and supports the standard cache methods. `synchronized(wrapped)`
serializes calls using a per-instance or shared lock and works for synchronous
functions, context-manager use, and asynchronous functions. `mark_as_sync`,
`mark_as_async`, `sync_to_async`, and `async_to_sync` control coroutine
classification and conversion. `register_post_import_hook(hook, name)`,
`when_imported(name)`, `notify_module_loaded(module)`, and
`discover_post_import_hooks(group)` provide deterministic post-import hooks.

`MISSING` is the patching sentinel. Public exception classes in
`wrapt.exceptions` must be raised for invalid paths, missing wrappers, and
invalid wrapper-chain operations rather than generic replacements.

# Implementation Notes

Keep package and submodule imports compatible with the public API and preserve
insertion order and normal Python exception identity. The verifier exercises
the listed behavior through an unprivileged JSON subprocess; do not depend on
trusted verifier imports or writable verifier paths. Native acceleration is an
optional implementation detail, not a license to change observable behavior.
The upstream suite's mypy snapshots, probabilistic stress programs, platform
specific cases, and extension-only error propagation are inventoried but are
outside this fixed deterministic score.

# Examples

```python
from wrapt import ObjectProxy, CallableObjectProxy

value = ObjectProxy({"key": 3})
assert value["key"] == 3
callable_value = CallableObjectProxy(lambda x: x + 1)
assert callable_value(2) == 3
```

```python
from wrapt import decorator

@decorator
def around(wrapped, instance, args, kwargs):
    return wrapped(*args, **kwargs)

@around
def add(a, b):
    return a + b

assert add(2, 3) == 5
```

# Error Handling and Boundary Conditions

- Proxy-only `_self_` attributes must not be written to the wrapped object;
  `__wrapped__` remains read-only and `repr` identifies the proxy.
- Wrapper methods that are not callable are skipped only where the contract
  permits it; exceptions raised by user functions propagate unchanged.
- Unwrapping a missing or mismatched handle raises the documented public
  exception unless `missing_ok=True` applies.
- Limits on wrapper-chain traversal are bounded and deterministic. Repeated
  hook, cache, synchronization, and lazy-resolution calls must preserve order,
  state transitions, and return values without external services.
