# Project Description

Create an installable Python package named `jaraco.functools` with an importable
package `jaraco.functools`. It provides small, deterministic function helpers
that complement the standard library `functools` module.

# Supports

- Python 3.10 or newer and a root `pyproject.toml` using a setuptools build backend.
- Runtime dependency declaration for `more-itertools`.
- Installation with `python -m pip install -e .` without network access.
- If using setuptools-scm with a source archive, provide a deterministic
  `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_JARACO_FUNCTOOLS` build value.
- The public functions and class listed in the API guide below.
- Preservation of wrapped function metadata where the guide says a decorator
  preserves it.

# API Usage Guide

All names below are imported from `jaraco.functools`.

`compose(*funcs)` returns a callable that applies the functions from right to
left. The innermost function may receive arbitrary positional and keyword
arguments. An empty call follows `functools.reduce` and raises `TypeError`.

`once(func)` returns a `functools.wraps`-like wrapper that calls `func` only on
its first invocation and reuses the saved result afterwards. The wrapper exposes
`saved_result` after the first call and a `reset()` method; deleting
`saved_result` also resets it.

`method_cache(method, cache_wrapper=functools.lru_cache())` installs a per-
instance cache on the first normal method call. The cached method exposes
`cache_clear()`. The decorator also supports `__getitem__` and `__getattr__`,
which are special methods and therefore use an internal per-instance cache.

`apply(transform)` decorates a function and applies `transform` to its return
value. `result_invoke(action)` decorates a function, calls `action(result)` for
side effect, and returns the original result. `invoke(func, /, *args, **kwargs)`
calls `func` immediately and returns the same function object. `passthrough(func)`
calls `func` with the first argument and returns that first argument unchanged.

`Throttler(func, max_rate=float('Inf'))` is a callable rate limiter. It exposes
`func`, `max_rate`, `last_called`, and `reset()`, forwards calls to `func`, and
can be used as a descriptor. Wrapping another `Throttler` unwraps its original
function. Tests should use an infinite rate for deterministic behavior.

`first_invoke(func1, func2)` returns a callable that invokes `func1()` first,
then invokes `func2` with the received arguments and returns its result.
`method_caller(name, /, *args, **kwargs)` is the deprecated wrapper around
`operator.methodcaller`: each construction emits `DeprecationWarning` and
returns the constructed method caller.

`retry_call(func, cleanup=lambda: None, retries=0, trap=())` retries a callable
for the requested number of trapped failures, calling `cleanup()` after each
trapped failure. The final call propagates its exception. `retries=float('inf')`
means retry until success. `retry(*args, **kwargs)` is the decorator form.

`print_yielded(func)` decorates a generator function and consumes it, printing
each yielded value on its own line. `pass_none(func)` skips `func` and returns
`None` when its first positional argument is `None`. `signed(func)` adds `+` to
positive formatted values, leaves negative values as formatted, and leaves zero
unsigned. `none_as(value, replacement=None)` returns `replacement` only for
`None`.

`assign_params(func, namespace)` returns a partial that supplies the entries in
`namespace` whose names occur in `func`'s signature. Normal Python missing- and
unexpected-argument errors remain observable. `save_method_args(method)` stores
the most recent positional and keyword arguments on the instance as
`_saved_<method name>.args` and `.kwargs` before calling the method.

`except_(*exceptions, replace=None, use=None)` decorates a function and catches
only the listed exception types. It returns `replace`, or evaluates the
provided `use` expression in the wrapper call context when supplied.
`identity(x)` returns `x`. `bypass_when(check, *, _op=identity)` returns a
decorator that returns its first argument when `_op(check)` is truthy, otherwise
calls the wrapped unary function. `bypass_unless(check)` is the inverse.

`splat(func)` adapts a function so a tuple/list is expanded as positional
arguments and a mapping is expanded as keyword arguments. `chainable(method)`
requires the wrapped method to return `None` and then returns `self`.
`noop(*args, **kwargs)` accepts anything and returns `None`.

# Implementation Notes

Keep behavior local, deterministic, and compatible with ordinary Python call
semantics. Do not add network access, external services, generated vendored
dependencies, or hard-coded verifier-specific hooks. The private verifier runs
the public API through a separate child process, so the implementation must be
installable into a candidate-owned site and importable there.
