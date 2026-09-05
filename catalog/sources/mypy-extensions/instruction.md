# Build `mypy-extensions`

## Project Description

Create the `mypy_extensions` project from an empty workspace. This is a repository-generation task for the frozen `python` package contract, task specification version `1.0.0`, at source revision `9fc7fe08c8e638cdd9bbf1aa9bf188aef4fd24ef`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is python, typing, mypy, mypyc, decorators, separate-verifier.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `mypy_extensions` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `mypy_extensions` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `python` on `3.12.14`; target environment metadata declares `debian-12-amd64`.
- Distribution/package: `mypy_extensions`; import/root name: `mypy_extensions`. Package manager: `pip`.
- Install from the repository root with `python -m pip install . --no-deps`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── mypy_extensions/
│   └── __init__.py
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: Callable argument markers, `TypedDict`, `trait`, `mypyc_attr`, `FlexibleAlias`, Native integer shims, Deprecated `NoReturn`.

For each listed family, the detailed contract below defines the import path or CLI entry, signature, accepted inputs, return type/shape, ordering and determinism, state or I/O side effects, errors, and examples. Implement the complete public surface, including root re-exports and aliases where the specification names them. If an API is stateful, preserve mutation and repeated-call behavior; if it is pure, do not introduce global state.

## Implementation Notes

Keep the implementation self-contained and deterministic under the declared runtime. The candidate repository must install from the workspace root, import through the documented public path, and run without external services. Preserve package metadata, module semantics (ESM/CommonJS or Python import behavior), serialization formats, resource cleanup, and boundary behavior described below. publicly unavailable evaluator adapters and non-public evaluation details are not part of the implementation.

## Examples

Ordinary project examples:

```bash
cd workspace
python -m pip install . --no-deps
```

```python
# Import the public package and use the task-specific APIs documented below.
import_or_require = "mypy_extensions"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Project Description

Build an installable Python distribution named `mypy_extensions` from an empty
workspace. The distribution provides the runtime compatibility helpers from
the frozen `mypy-extensions` 1.2.0 development revision: callable argument
markers, deprecated `TypedDict` and `NoReturn` shims, mypyc decorators and
native-integer shims, and `FlexibleAlias`.

These APIs are intentionally lightweight at runtime. They preserve type
objects, classes, and normal `int` values while exposing metadata used by mypy
or mypyc. No static type checker, compiler plugin, command-line program, or
network service is required.

# Supports

- Python 3.12 and an installable distribution version normalized as
  `1.2.0.dev0`.
- A top-level module importable as `mypy_extensions`.
- No runtime third-party dependencies.
- Offline installation and use after build dependencies have been provisioned.
- The public names `TypedDict`, `Arg`, `DefaultArg`, `NamedArg`,
  `DefaultNamedArg`, `VarArg`, `KwArg`, `trait`, `mypyc_attr`,
  `FlexibleAlias`, `i64`, `i32`, `i16`, `u8`, and the deprecated dynamic name
  `NoReturn`.

# API Usage Guide

## Callable argument markers

Import these functions from `mypy_extensions`:

```python
Arg(type=typing.Any, name=None)
DefaultArg(type=typing.Any, name=None)
NamedArg(type=typing.Any, name=None)
DefaultNamedArg(type=typing.Any, name=None)
VarArg(type=typing.Any)
KwArg(type=typing.Any)
```

Each function returns the exact object supplied as `type`; when omitted, it
returns `typing.Any`. The optional `name` is accepted by the first four helpers
and does not change the runtime result. These markers do not validate values or
wrap callables.

Example:

```python
from mypy_extensions import Arg, NamedArg

assert Arg(int, "count") is int
assert NamedArg(str, "label") is str
```

## `TypedDict`

`TypedDict` supports all of these forms:

```python
TypedDict(typename, fields_mapping_or_iterable, *, total=True)
TypedDict(typename, *, total=True, **field_types)

class Name(TypedDict, total=True):
    field: FieldType
```

Creating a typed-dict class emits `DeprecationWarning` with text identifying
`mypy_extensions.TypedDict` as deprecated. The resulting class:

- is a subclass of `dict` whose direct base is `dict`;
- has the requested `__name__`, caller `__module__`, merged
  `__annotations__`, and boolean `__total__` metadata;
- constructs ordinary `dict` instances and performs no runtime key or value
  validation;
- merges inherited typed-dict annotations in base order;
- supports `total=False` in functional and class syntax;
- supports normal instance and class pickling when the class is module-bound;
- raises `TypeError` for invalid field type declarations, for mixing a field
  mapping with keyword fields, and for `isinstance` or `issubclass` checks
  against a typed-dict class.

The mapping/iterable and keyword field forms are alternatives. Supplying both
must fail. Field annotations are normalized with Python's typing type check,
and type metadata remains usable in expressions such as `typing.Optional[T]`.

## `trait`

```python
trait(cls)
```

Returns the exact class object unchanged. It does not create a subclass,
descriptor, or wrapper and does not modify class attributes.

## `mypyc_attr`

```python
mypyc_attr(*attrs, **kwattrs)
```

Returns a decorator. Applying that decorator to a function or class returns
the exact decorated object unchanged, regardless of the positional or keyword
metadata supplied. It does not attach runtime attributes.

## `FlexibleAlias`

`FlexibleAlias` is a two-stage subscription helper. Its first subscription
evaluates `subscription_arguments[-1]` and retains that value; any second
subscription returns the retained value unchanged:

```python
from mypy_extensions import FlexibleAlias

assert FlexibleAlias[str, int][float] is int
assert repr(FlexibleAlias[dict][str]) == "dict[-1]"
```

For a comma-separated first subscription, `subscription_arguments` is a tuple,
so its final member is retained. For a single first-stage argument, the helper
applies `[-1]` to that argument itself; the example above therefore retains the
generic alias `dict[-1]`, while a non-subscriptable object may raise
`TypeError`. The second subscription's argument does not affect the result.
Reusing an applied alias returns the same retained object each time.

## Native integer shims

The classes `i64`, `i32`, `i16`, and `u8` have the same runtime contract:

```python
i64(x=0, base=<not supplied>) -> int
i32(x=0, base=<not supplied>) -> int
i16(x=0, base=<not supplied>) -> int
u8(x=0, base=<not supplied>) -> int
```

Construction delegates to the built-in `int`. Omitting `base` supports normal
numeric conversion; explicitly supplying it supports string/bytes conversion
exactly as `int(x, base)`. Results are plain built-in `int` objects. No range
checking, signedness enforcement, wrapping, or overflow behavior is applied at
runtime.

For each shim, `isinstance(value, shim)` is equivalent to
`isinstance(value, int)`, so it accepts `bool` and rejects `float`. Each class
has a descriptive docstring naming the shim and its `int` behavior.

## Deprecated `NoReturn`

`NoReturn` is provided dynamically when first requested:

```python
from mypy_extensions import NoReturn
```

The first lookup returns the module's compatibility marker class and emits one
`DeprecationWarning` directing users to `typing.NoReturn` or
`typing_extensions.NoReturn`. The value is then cached in the module, so a
second lookup returns the identical object without another warning. An unknown
dynamic attribute raises `AttributeError` whose message names both the module
and missing attribute.

# Implementation Notes

Keep the implementation deterministic and free of network, filesystem,
subprocess, clock, locale, or random-number dependencies. Public behavior is
evaluated in isolated child Python processes through JSON-safe observations;
the runtime evaluator never imports candidate code. Complex type objects,
warnings, class metadata, pickling, and identity are reconstructed and observed
inside those child processes.

Do not require mypy, mypyc, `typing_extensions`, or any other runtime package.
Packaging metadata must identify the `mypy_extensions` distribution and must
not declare runtime requirements.
