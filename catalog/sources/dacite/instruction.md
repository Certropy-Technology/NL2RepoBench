# Project Description

```text
workspace/
├── pyproject.toml
├── README.md
└── dacite/
    ├── __init__.py
    ├── core.py
    └── py.typed
```

Create a complete, installable Python distribution named `dacite` from an
empty workspace. The package converts dictionaries into instances of
standard-library dataclasses while respecting their declared type hints,
defaults, nested structure, collection shapes, and a small explicit
configuration object.

`dacite` is a construction helper, not a schema-validation framework. It may
perform basic runtime type checks and conversions described below, but it does
not need to implement general coercion, arbitrary validation rules, JSON
parsing, or serialization back to dictionaries.

# Supports

- Support Python 3.10 and newer, including Python 3.12.
- The project must install from its repository root with
  `python -m pip install .` without network access once build requirements are
  available.
- Use the distribution name `dacite`, version `1.9.2`, and an import package
  named `dacite` containing a `py.typed` marker.
- Declare no third-party runtime dependency on supported Python versions.
  Compatibility metadata may retain the conditional
  `dataclasses; python_version < "3.7"` requirement.
- Normal operation is pure Python and local. It must not require files outside
  the installed package, subprocesses, services, or network access.

# API Usage Guide

## Root exports

`dacite.__all__` contains these names in this order:

```text
set_cache_size, get_cache_size, clear_cache, Config, from_dict,
DaciteError, DaciteFieldError, WrongTypeError, MissingValueError,
UnionMatchError, StrictUnionMatchError, ForwardReferenceError,
UnexpectedDataError
```

`from_dict` is implemented in `dacite.core`; all listed names are importable
from the package root.

## `from_dict`

```python
from_dict(
    data_class: type[T],
    data: dict[str, object],
    config: Config | None = None,
) -> T
```

The function creates and returns one instance of `data_class`. It examines
dataclass fields in declaration/inheritance order and obtains their resolved
type hints. For each field it reads `data[config.convert_key(field.name)]`.
When a key is absent, use the dataclass default, call its default factory, or
use `None` for an `Optional` field. A missing required `init=True` field raises
`MissingValueError`.

Construction supports:

- primitive values and `typing.Any`;
- nested dataclasses represented by nested mappings;
- `Optional`, `Union`, `Literal`, `NewType`, `InitVar`, and `Type` hints;
- parameterized lists, sets, tuples, mappings, and other ordinary collection
  hints, recursively converting their members;
- fixed-length tuples, variadic tuples, and mixed tuple member types;
- generic dataclasses and concrete generic specializations;
- forward references resolved from the class/module namespace or the explicit
  `Config.forward_references` mapping;
- dataclass inheritance, frozen dataclasses, `init=False` fields, defaults,
  default factories, and `__post_init__` behavior.

Nested errors prepend the containing field name to their `field_path`, using
dots between levels. The original input mapping is not a required output and
need not be mutated.

With default configuration, basic runtime type checking is enabled. Integers
are accepted for fields typed as `float` or `complex`, following Python's
numeric tower. Container members and mapping keys/values are checked against
their parameterized types. A mismatch raises `WrongTypeError`.

For a `Union`, candidates are attempted in declared order and the first
matching result is returned. If no member matches, raise `UnionMatchError`.
For an optional two-member union, `None` remains `None` and a non-null value is
processed as the non-`None` member.

## `Config`

```python
@dataclass
class Config:
    type_hooks: dict[type, Callable[[object], object]] = ...
    cast: list[type] = ...
    forward_references: dict[str, object] | None = None
    check_types: bool = True
    strict: bool = False
    strict_unions_match: bool = False
    convert_key: Callable[[str], str] = identity
```

Every `Config` instance receives fresh empty `type_hooks` and `cast`
containers.

- `type_hooks` maps an exact declared type to a one-argument transformation.
  Apply a hook before optional/union/collection/dataclass processing. Hooks for
  member types therefore apply recursively inside collections and nested
  values. Hook exceptions propagate.
- `cast` lists base types whose matching field types should be constructed by
  calling the declared field type. A base class entry applies to subclasses;
  for example, listing `enum.Enum` enables enum construction. A collection
  cast changes the outer collection type after recursively building members.
- `forward_references` supplies additional names to type-hint resolution.
- `check_types=False` returns constructed values without the final basic type
  rejection. For an unmatched union, retain the original value.
- `strict=True` rejects input keys that do not correspond to dataclass field
  names by raising `UnexpectedDataError`. The default ignores extra input.
- `strict_unions_match=True` evaluates every union member. Exactly one match is
  returned; multiple matches raise `StrictUnionMatchError`.
- `convert_key(field_name)` maps a Python field name to the input key. This
  supports conventions such as snake_case dataclass fields backed by camelCase
  dictionaries.

`Config.hashable_forward_references` is a cached, hashable view used by type
resolution. It is `None` for a missing/empty mapping and otherwise behaves as
an immutable mapping of the configured names.

## Cache controls

```python
set_cache_size(size: int | None) -> None
get_cache_size() -> int | None
clear_cache() -> None
```

The default configured cache size is `2048`. `set_cache_size` changes the size
used when creating subsequent internal cached wrappers; `None` means
unbounded. `clear_cache` clears the library's cache of wrappers and returns
`None`. Cache behavior must not change conversion results.

## Exceptions

The public hierarchy is:

```text
DaciteError(Exception)
├── DaciteFieldError
│   ├── WrongTypeError
│   │   └── UnionMatchError
│   ├── MissingValueError
│   └── StrictUnionMatchError
├── ForwardReferenceError
└── UnexpectedDataError
```

`DaciteFieldError` stores `field_path` and provides
`update_path(parent_field_path)` to prepend nested paths.

- `WrongTypeError` stores `field_type`, `value`, and `field_path`; its message
  identifies the field, expected type, received value, and received type.
- `MissingValueError` reports `missing value for field "<path>"`.
- `UnionMatchError` reports that the received type cannot match any member of
  the field's union.
- `StrictUnionMatchError` stores a mapping of matching types to values and
  reports the conflicting type names.
- `ForwardReferenceError` stores the underlying resolution message and prefixes
  it with `can not resolve forward reference: `.
- `UnexpectedDataError` stores the unexpected key set and reports every key.

# Implementation Notes

Preserve dataclass declaration order and normal constructor/default semantics.
Do not eagerly coerce values unless a configured hook or cast requests it.
Type-hook processing precedes recursive construction, configured casting
follows recursive construction, and final type checking happens afterward.

The result must be an actual instance of the requested dataclass, including
nested and collection members, not a dictionary proxy. Keep exception objects
inspectable through the attributes described above. Implement the behavior
without retrieving the upstream repository or any reference implementation at
runtime.

# Natural Language Instruction

Create the `dacite` project from an empty workspace. Implement
dictionary-to-dataclass construction, nested type-aware conversion, explicit
`Config` customization, cache controls, and inspectable exceptions exactly as
specified below. Keep the package local and deterministic; do not wrap an
installed copy or fetch the upstream project.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── dacite/
    ├── __init__.py
    ├── core.py
    ├── config.py
    ├── dataclasses.py
    ├── types.py
    └── py.typed
```

The root package exports `from_dict`, `Config`, cache controls, and the public
exception classes. The exact internal split may vary, but the installed import
path and package metadata must agree with this project layout.

# Examples

```python
from dataclasses import dataclass
from dacite import from_dict

@dataclass
class User:
    name: str
    age: int

user = from_dict(User, {"name": "Ada", "age": 36})
```

```python
from dataclasses import dataclass
from dacite import Config, from_dict

@dataclass
class Item:
    item_id: int

item = from_dict(Item, {"item_id": "7"}, Config(cast=[int]))
```

# Error Handling and Boundary Conditions

Missing required fields raise `MissingValueError`; incompatible values raise
`WrongTypeError` or the documented union error. With `strict=True`, unknown
input keys raise `UnexpectedDataError`. Optional values may become `None`, but
arbitrary JSON parsing, serialization, and network access are outside scope.
