# Project Description

Create an installable Python package named `jaraco.functools`. It supplies
small deterministic helpers for composition, memoization, decorators, retries,
throttling, argument binding, and no-op/pass-through functions. The package
complements rather than replaces the standard `functools` module.

# Natural Language Instruction

From an empty workspace, implement the documented public functions and
`Throttler` class under `jaraco.functools`. Preserve wrapped function metadata,
Python call semantics, per-instance caches, retry cleanup, descriptor behavior,
and deterministic output. Provide packaging metadata and the `more_itertools`
runtime dependency. Do not copy reference source, tests, or verifier files.

# Supports or Environment Configuration

- Python 3.10 or newer; evaluation uses Python 3.12 on Linux.
- Distribution/import package: `jaraco.functools`. Use a root `pyproject.toml`
  and a deterministic build version; if using setuptools-scm, honor the
  supplied `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_JARACO_FUNCTOOLS` value.
- Runtime dependency: `more_itertools`; build tools are build-only.
- Installation and all agent, candidate, verifier, Oracle, and control runs
  are offline after dependencies are prepared. No network, clock, or external
  service may affect behavior.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
├── LICENSE
└── jaraco/
    ├── __init__.py
    └── functools/
        ├── __init__.py
        └── py.typed
```

# API Usage Guide

All APIs below are imported from `jaraco.functools`.

```python
compose(*funcs)
once(func)
method_cache(method, cache_wrapper=functools.lru_cache())
apply(transform)
result_invoke(action)
invoke(func, /, *args, **kwargs)
passthrough(func)
Throttler(func, max_rate=float("Inf"))
first_invoke(func1, func2)
method_caller(name, /, *args, **kwargs)
retry_call(func, cleanup=lambda: None, retries=0, trap=())
retry(*args, **kwargs)
```

`compose` applies functions right-to-left; the innermost accepts the original
arguments. An empty composition follows `functools.reduce` and raises
`TypeError`. `once` calls once, exposes `saved_result`, and resets via
`reset()` or deleting that attribute. `method_cache` installs a per-instance
cache and exposes `cache_clear`; special methods use an internal cache.

`apply` transforms a return value; `result_invoke` performs a side effect and
returns the original result; `invoke` calls immediately and returns the same
function object; `passthrough` calls a function and returns its first argument.
`Throttler` forwards calls while exposing `func`, `max_rate`, `last_called`, and
`reset`; it also works as a descriptor and unwraps another `Throttler`.

`first_invoke` calls its first function and passes the result arguments to the
second. `method_caller` wraps `operator.methodcaller` and emits
`DeprecationWarning`. `retry_call` retries trapped failures, runs `cleanup`
after each, and propagates the final exception; infinite retries continue until
success. `retry` is its decorator form.

```python
print_yielded(func)
pass_none(func)
signed(func)
none_as(value, replacement=None)
assign_params(func, namespace)
save_method_args(method)
except_(*exceptions, replace=None, use=None)
identity(x)
bypass_when(check, *, _op=identity)
bypass_unless(check)
splat(func)
chainable(method)
noop(*args, **kwargs)
```

`print_yielded` consumes a generator and prints each item on its own line.
`pass_none` bypasses its function for a first argument of `None`; `signed`
formats positive numbers with `+`; `none_as` replaces only `None`.
`assign_params` creates a partial from matching signature names, and
`save_method_args` records the latest call as `_saved_<name>.args` and
`.kwargs`. `except_` catches only listed exceptions and returns `replace` or
evaluates `use`. `identity`, bypass helpers, `splat`, `chainable`, and `noop`
retain the ordinary argument and return contracts stated by their signatures.

# Implementation Notes

Use `functools.wraps` where metadata preservation is promised. Cache state is
per instance, not a shared mutable default. Retry and throttling behavior must
be deterministic in tests; callers can use an infinite rate. Do not add
network, subprocess, generated dependency, or verifier-specific behavior.

# Examples

```python
from jaraco.functools import compose, once

double = lambda x: x * 2
inc_after_double = compose(lambda x: x + 1, double)
assert inc_after_double(3) == 7

f = once(lambda: "ready")
assert f() == f() == "ready"
f.reset()
```

```python
from jaraco.functools import retry_call, pass_none

assert pass_none(str)(None) is None
assert retry_call(lambda: 4, retries=2) == 4
```

# Error Handling and Boundary Conditions

The task id is `jaraco-functools`; the distribution is `jaraco.functools`.

- Empty `compose()` raises the normal reduction `TypeError`.
- `retry_call` runs cleanup only after trapped failures and propagates the
  final untrapped/final failure.
- `chainable` requires the wrapped method to return `None`; otherwise it must
  report the contract violation rather than silently return `self`.
- `except_` must not catch exception classes that were not requested.
- Avoid current time and unbounded retries in deterministic evaluation.
