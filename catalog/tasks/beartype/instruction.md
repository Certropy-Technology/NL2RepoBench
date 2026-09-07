# Project Description

Build a clean-room, installable Python package named `beartype` that reproduces
the documented observable behavior of the frozen `beartype` 0.22.9 release.
The package is a runtime type-checking toolkit. It applies Python annotations to
callables, provides black-box checks for objects against type hints, exposes
objects for inspecting hints, and supplies reusable value validators.

The implementation starts in an empty `workspace/` directory. Do not assume
that any package source, generated wrapper, configuration, test, or metadata
file already exists. The final project must be installable with the package name
`beartype`, and `import beartype` must resolve to your implementation rather
than to a globally installed copy.

The public behavior includes:

1. The root `beartype.beartype` decorator and its configuration argument.
2. The `beartype.door` object-oriented and predicate-based hint API.
3. The `beartype.vale` subscription factories for value constraints.
4. The `beartype.roar` exception and warning families used by these APIs.
5. The `beartype.typing` compatibility namespace used in annotations.
6. Root configuration types, enums, version metadata, and stable exports.

The public behavior does not require optional development integrations such as
NumPy, Pandera, JAX, Celery, documentation builders, or static type checker
plugins. Do not download the upstream repository or copy its implementation.
Do not expose private `_check`, `_decor`, `_util`, or generated-code modules as
part of the requested public contract.

# Natural Language Instruction

Create a production-quality pure-Python package for the frozen `beartype` 0.22.9
API. Implement the following capabilities as one coherent package:

- Implement `beartype.beartype` as a decorator that accepts a callable or class
  and performs runtime checks from its supported annotations. A valid call must
  preserve the wrapped callable's result; an invalid parameter or return value
  must raise the documented public violation family.
- Implement the `beartype.BeartypeConf` configuration object and the public
  `BeartypeStrategy`, `BeartypeViolationVerbosity`, and `BeartypeDecorPlace`
  enums. Configuration objects are immutable in normal use and repeated creation
  with identical public settings is stable and reusable.
- Implement `beartype.door.is_bearable`, `die_if_unbearable`, and `is_subhint`
  for supported standard-library and PEP typing hints. They must return the
  documented boolean/None shape or raise a public DOOR violation/exception when
  the input cannot be handled.
- Implement `beartype.door.TypeHint` and its public methods and properties for
  inspecting a hint, checking an object, and comparing hint relationships.
- Implement `beartype.vale.Is`, `IsAttr`, `IsEqual`, `IsInstance`, and
  `IsSubclass` as public subscription factories that can be embedded in an
  annotation and checked by the decorator or DOOR functions.
- Implement the public exception and warning hierarchy in `beartype.roar`.
  Preserve family relationships and let callers catch documented base classes;
  do not rely on exact message strings or private leaf implementation names.
- Implement the `beartype.typing` compatibility namespace. Its public typing
  names must be importable and usable in annotations on Python 3.10+.
- Provide package metadata for the exact project name and version `0.22.9`.
  Include `py.typed` and make root exports match the public API described below.

Use only the Python standard library at runtime. The build backend may use the
preinstalled packaging tools described in `task.toml`, but no runtime feature
may require a third-party package. Keep all behavior deterministic for the same
inputs. Do not make network requests, spawn an external service, or read a
reference implementation at runtime.

# Supports

- Runtime: CPython 3.12 on Linux, with source compatibility for Python 3.10+.
- Package manager: pip or uv can install the local project from `workspace/`.
- Build metadata: PEP 517/518/621-compatible `pyproject.toml` with project name
  `beartype`, version `0.22.9`, and no mandatory runtime dependencies.
- Install entry: `python -m pip install .` from the workspace, or the equivalent
  offline uv installation used by the harness.
- Runtime network policy: no network. Agent, candidate, verifier, Oracle, and
  controls must not access GitHub, PyPI, DNS, package registries, or any external
  service during their execution.
- Optional extras must not be required for the core package. A missing optional
  integration should not prevent `import beartype`, `beartype.door`,
  `beartype.vale`, `beartype.roar`, or `beartype.typing` from loading.
- The requested package is pure Python. Do not require a C compiler, native
  extension, database, daemon, filesystem fixture, locale, or environment
  variable for the core API.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── beartype/
    ├── __init__.py
    ├── py.typed
    ├── typing/
    │   └── __init__.py
    ├── door/
    │   ├── __init__.py
    │   ├── _cls/                  # private implementation may be nested here
    │   └── _func/
    ├── vale/
    │   └── __init__.py
    ├── roar/
    │   └── __init__.py
    ├── cave/
    │   └── __init__.py
    └── claw/
        └── __init__.py
```

The public import paths in this tree are `beartype`, `beartype.typing`,
`beartype.door`, `beartype.vale`, `beartype.roar`, `beartype.cave`, and
`beartype.claw`. Private helper modules may be organized below those packages,
but callers and tests must not need to import private paths.

# API Usage Guide

## Root decorator and metadata: `beartype`

Import the decorator as `from beartype import beartype`. Its public callable
shape is:

```python
beartype(obj=None, *, conf=BeartypeConf()) -> object
```

When used as `@beartype`, it accepts a supported Python callable or class and
returns a callable/class that preserves the original public calling convention
as far as runtime wrapping permits. When used as `@beartype(conf=my_conf)`, it
returns a decorator. A correctly typed call returns the wrapped function's own
value. A parameter mismatch raises a public parameter-violation family from
`beartype.roar`; a return mismatch raises a public return-violation family.

The decorator must support ordinary annotations such as `int`, `str`,
`list[int]`, `dict[str, int]`, `tuple[int, ...]`, `typing.Union`,
`typing.Optional`, `typing.Literal`, and `typing.Annotated` to the extent
supported by Python 3.12. Unsupported hints must fail through a public
beartype exception rather than silently claiming a false positive.

The root module also exports `__version__` as the string `"0.22.9"`,
`__version_info__` as its corresponding integer tuple, `BeartypeConf`,
`BeartypeStrategy`, `BeartypeViolationVerbosity`, `BeartypeDecorPlace`, and
`FrozenDict`. These names are imported from `beartype`, not from private modules.

## Configuration: `beartype.BeartypeConf`

Construct it with keyword-only options from the frozen public signature:

```python
BeartypeConf(
    *,
    claw_decor_place_func=BeartypeDecorPlace.LAST_BEFORE_DECOR_HOSTILE,
    claw_decor_place_type=BeartypeDecorPlace.LAST,
    claw_is_pep526=True,
    claw_skip_package_names=(),
    hint_overrides=FROZENDICT_EMPTY,
    is_color=ARG_VALUE_UNPASSED,
    is_debug=False,
    is_pep484_tower=False,
    is_pep557_fields=False,
    strategy=BeartypeStrategy.O1,
    violation_door_type=None,
    violation_param_type=None,
    violation_return_type=None,
    violation_type=None,
    violation_verbosity=BeartypeViolationVerbosity.DEFAULT,
    warning_cls_on_decorator_exception=default,
    claw_decoration_position_funcs=None,
    claw_decoration_position_types=None,
    is_check_pep557=None,
) -> BeartypeConf
```

The exact default sentinel representation is an implementation detail; preserve
the observable defaults and accept the documented keyword names. Expose
read-only properties `kwargs`, `hint_overrides`, `strategy`,
`warning_cls_on_decorator_exception`, `is_color`, `is_debug`,
`is_pep484_tower`, `is_pep557_fields`, `claw_decor_place_func`,
`claw_decor_place_type`, `claw_is_pep526`, `claw_skip_package_names`,
`violation_door_type`, `violation_param_type`, `violation_return_type`,
`violation_type`, and `violation_verbosity`. Equality, hashing, and repr must be
stable for equivalent public configurations.

`BeartypeStrategy` is imported from `beartype` and includes `O0`, `O1`, `Ologn`,
and `On`. `BeartypeViolationVerbosity` includes `MINIMAL`, `DEFAULT`, and
`MAXIMAL`. `BeartypeDecorPlace` includes the documented decorator-position
members such as `FIRST` and `LAST`. Enum members are selected through the
public enum objects, never by depending on their integer values.

## DOOR predicate API: `beartype.door`

Import `is_bearable`, `die_if_unbearable`, `is_subhint`, and `TypeHint` from
`beartype.door`.

```python
is_bearable(obj: object, hint: Hint, *, conf=BeartypeConf()) -> bool

die_if_unbearable(
    obj: object,
    hint: Hint,
    *,
    conf=BeartypeConf(),
    exception_prefix="die_if_unbearable() ",
) -> None

is_subhint(subhint: Hint, superhint: Hint) -> bool
```

`is_bearable` returns a boolean result for supported hints and ordinary Python
objects. It must not mutate the object. `die_if_unbearable` returns `None` when
the object satisfies the hint, and raises a public `BeartypeDoorHintViolation`
or compatible public DOOR exception otherwise. `exception_prefix` changes only
public diagnostic context; callers must not depend on exact wording.

`is_subhint` returns a boolean relation for supported hint pairs. Invalid or
unsupported relations may raise a public `BeartypeDoorException` family. Keep
comparison deterministic and do not use object identity as the relation.

`TypeHint` is constructed as `TypeHint(hint)` and exposes:

```python
TypeHint(hint: T_Hint) -> TypeHint[T_Hint]
TypeHint.hint -> T_Hint
TypeHint.args -> tuple
TypeHint.is_ignorable() -> bool
TypeHint.is_bearable(obj: object, *, conf=BeartypeConf()) -> bool
TypeHint.die_if_unbearable(obj: object, *, conf=BeartypeConf(), exception_prefix="die_if_unbearable() ") -> None
TypeHint.is_subhint(other: TypeHint) -> bool
TypeHint.is_superhint(other: TypeHint) -> bool
```

The `hint` property returns the original public hint object and `args` exposes
its public type arguments as a tuple. The methods have the same success and
exception behavior as the module-level DOOR functions. `TypeHint` subclasses
such as `UnionTypeHint`, `LiteralTypeHint`, `AnnotatedTypeHint`,
`AnyTypeHint`, `ClassTypeHint`, `CallableTypeHint`, `GenericTypeHint`,
`SubscriptedTypeHint`, `TupleFixedTypeHint`, and `TupleVariableTypeHint` are
publicly importable from `beartype.door` when present in the frozen release.
Do not require callers to know private subclass implementation names.

## Validator factories: `beartype.vale`

Import `Is`, `IsAttr`, `IsEqual`, `IsInstance`, and `IsSubclass` from
`beartype.vale`. These are subscription-style public factories used inside
annotations:

```python
from beartype.vale import Is, IsAttr, IsEqual, IsInstance, IsSubclass

Positive = Is[lambda value: value > 0]
Named = IsAttr["name", IsInstance[str]]
Expected = IsEqual["ready"]
InstanceOf = IsInstance[dict]
SubclassOf = IsSubclass[BaseException]
```

A validator created through a supported public subscription can be passed as an
annotation to `@beartype`, `is_bearable`, or `die_if_unbearable`. It accepts a
value when its documented predicate is true and rejects it otherwise. Callable
validators must be deterministic and side-effect free for the same value.
`IsAttr` names a public attribute and composes with another validator or hint;
missing attributes are rejected through normal validation rather than crashing
with an internal traceback. `IsEqual` compares the candidate with the supplied
expected value. `IsInstance` and `IsSubclass` use the corresponding public
Python class relationships and reject invalid class specifications publicly.

## Exception and warning families: `beartype.roar`

Import exception classes from `beartype.roar`, for example:

```python
from beartype.roar import (
    BeartypeException,
    BeartypeDoorException,
    BeartypeDoorHintViolation,
    BeartypeCallHintViolation,
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
    BeartypeWarning,
)
```

`BeartypeException` is the root public exception family. DOOR errors derive
from `BeartypeDoorException`; call-time annotation violations derive from the
call/violation families. Catch a documented base class when possible. The
specific exception type should distinguish an invalid parameter from an invalid
return and a DOOR validation failure. Error messages may include context but
are not part of this task's exact-value contract. Warning classes under
`beartype.roar`, including `BeartypeWarning`, are public categories and should
be usable with Python's `warnings` machinery.

## Compatibility typing: `beartype.typing`

The module `beartype.typing` re-exports typing constructs for use in public
annotations. At minimum support `Any`, `Annotated`, `Callable`, `Literal`,
`Optional`, `TypeVar`, `TypedDict`, `Union`, `cast`, `get_args`, `get_origin`,
`get_type_hints`, `no_type_check`, `no_type_check_decorator`, `overload`,
`NamedTuple`, `NewType`, `Final`, `ClassVar`, `Generic`, `IO`, `TextIO`,
`BinaryIO`, `TypeAlias`, `TypeGuard`, `ParamSpec`, `ParamSpecArgs`, and
`ParamSpecKwargs` where provided by the supported interpreter. Imports must be
usable in function and class annotations without network access.

## Optional public namespaces: `beartype.cave` and `beartype.claw`

The frozen release exposes public aliases under `beartype.cave` and import-hook
entry points under `beartype.claw`. Implement stable, harmless imports for the
public names that can be supported without optional services. `beartype.cave`
may expose common runtime types such as `AnyType`, `BoolType`, `IntType`,
`StrType`, `SequenceType`, `MappingType`, and callable type tuples. `beartype.claw`
may expose `beartype_all`, `beartype_package`, `beartype_packages`,
`beartype_this_package`, and `beartyping` with documented callable signatures.
Import-hook behavior is not required to depend on a network or an external
package; unsupported hook configurations must fail with a public exception.

# Implementation Notes

Keep the implementation modular: the root exports should be thin public aliases,
while hint normalization, runtime checks, validator handling, configuration,
and exception definitions can live in private modules. The public behavior is
black-box behavior, not generated source text. You may choose any internal
algorithm that satisfies the observable API.

Use standard Python introspection and typing protocols. Preserve wrapped
function return values, class construction behavior, positional/keyword calls,
and ordinary metadata when practical. A decorator must not change a successful
function's semantic result merely because checking is enabled.

Check parameters before entering the wrapped callable and check its return after
it completes. Exceptions raised by the wrapped callable itself should propagate
rather than being replaced with a type violation. A type violation must identify
whether the parameter or return contract was violated through the public
exception family; exact wording, generated function names, source fragments,
and stack-frame layout are not required.

For container hints, implement the supported public element checks and preserve
normal empty-container behavior. Empty containers should satisfy element hints
when there is no observed element contradicting the hint. `Any` and compatible
unconstrained hints should not reject ordinary values. Union/optional, literal,
annotated, tuple, mapping, sequence, callable, and class hints should follow
normal Python typing semantics at the public behavior level.

Configuration and enum values must not depend on environment variables, current
time, process identity, network state, or random seeds. `BeartypeConf` values
should be hashable when their public inputs are hashable, and equivalent
configurations should compare equal. Do not expose mutable internal dictionaries
through read-only properties.

Validators should compose with regular type hints and other validators. Their
public failure behavior should be a normal validation failure from the caller's
API, not an implementation traceback. Avoid evaluating arbitrary validator code
at package import time; evaluate it only when the public validator is used.

The `beartype.typing` compatibility layer must remain importable even when
optional packages are absent. Use only standard-library typing objects for the
core task. Keep `py.typed` present and make the project metadata discoverable by
pip/uv.

# Examples

## Normal example: a typed function

```python
from beartype import beartype

@beartype
def repeat(word: str, count: int) -> str:
    return word * count

assert repeat("ha", 3) == "hahaha"
```

The successful call returns the function's own string. A call such as
`repeat("ha", "3")` must raise a public parameter violation family rather than
silently coercing the string to an integer.

## Normal example: DOOR and a generic hint

```python
from beartype.door import is_bearable, die_if_unbearable

assert is_bearable({"count": 2}, dict[str, int]) is True
die_if_unbearable({"count": 2}, dict[str, int])
```

The predicate must not mutate the dictionary. A dictionary containing a value
that violates the declared element hint is rejected by `is_bearable` and by
`die_if_unbearable`.

## Normal example: a value validator

```python
from beartype import beartype
from beartype.vale import Is

Positive = Is[lambda value: value > 0]

@beartype
def square(value: Positive) -> int:
    return value * value

assert square(4) == 16
```

The validator accepts the positive input and the function returns its square.

## Normal example: inspecting a hint

```python
from beartype.door import TypeHint

hint = TypeHint(list[int])
assert hint.hint == list[int]
assert isinstance(hint.args, tuple)
assert hint.is_bearable([1, 2]) is True
```

The public properties describe the supplied hint without requiring a private
subclass import.

# Error Handling and Boundary Conditions

## Wrong parameter and wrong return

A decorated function receiving a value that does not satisfy a parameter hint
raises `beartype.roar.BeartypeCallHintParamViolation` or its documented public
base family. A decorated function returning a value that violates its return
hint raises `BeartypeCallHintReturnViolation` or its documented public base
family. Do not assert exact message text, line numbers, generated code, or
traceback frames.

## Empty and Unicode values

An empty list checked against `list[int]` is valid because it contains no
contradictory element. Unicode strings remain ordinary `str` values and must be
accepted by `str` annotations without ASCII-only assumptions. A non-ASCII value
must not cause an encoding-dependent internal failure.

## Invalid DOOR input

`die_if_unbearable("not-an-int", int)` raises a public DOOR violation and
returns no value. `is_bearable("not-an-int", int)` returns `False`. The APIs
must not mutate the input or print diagnostics to stdout/stderr during normal
use.

## Unsupported or malformed hints

If a hint is outside the supported public typing surface, use an appropriate
public `BeartypeDoorException`/`BeartypeDecorHintException` family rather than
silently accepting every object. Invalid validator subscriptions and invalid
class arguments likewise fail through documented public exception families.

## Configuration edge cases

Equivalent `BeartypeConf()` calls compare equal and have stable hashes/reprs.
Changing a public option such as `strategy` or `violation_verbosity` produces a
configuration with the corresponding observable property. The implementation
must not expose a mutable alias that lets callers silently change an existing
configuration.

## NoNetwork and isolation

The package and all examples above must run without network access. Never
attempt to download beartype, resolve a registry package, contact a provider,
or inspect a hidden test. Hidden verification may exercise public behavior with
subprocesses and fresh interpreters; do not assume process-global state from an
unrelated test.

## Normal example: configuration selection

```python
from beartype import BeartypeConf, BeartypeStrategy, beartype

conf = BeartypeConf(strategy=BeartypeStrategy.O1)
@beartype(conf=conf)
def as_text(value: str) -> str:
    return value

assert as_text("stable") == "stable"
```

The selected public configuration is passed through the decorator without
changing a successful result.

## Normal example: typing compatibility

```python
from beartype.typing import Optional
from beartype import beartype

@beartype
def label(value: Optional[str]) -> str:
    return "none" if value is None else value

assert label(None) == "none"
assert label("ok") == "ok"
```

Compatibility typing exports can be used directly in annotations.
