# Build `annotated-types`

Create a complete, installable Python project named `annotated-types` from an
empty workspace.  It provides reusable metadata objects for
`typing.Annotated`; the package itself does not validate application values or
perform network, filesystem, subprocess, or service operations.

## Project Description

The library supplies immutable, typed metadata for bounds, lengths, units,
time zones, and arbitrary predicates.  It also supplies grouped metadata that
downstream annotation consumers can unpack by iteration, plus convenient
generic aliases for common string and floating-point predicates.  The public
distribution is imported as `annotated_types` and reports version `0.8.0`.

## Supports

- Support CPython 3.10 and newer Python 3.x versions in the source's supported
  range; the evaluation runtime is CPython 3.12.
- Produce an installable project with an `annotated_types/` package and a
  `py.typed` marker.  A standard PEP 517 build using Hatchling is acceptable;
  do not require a third-party runtime dependency.
- Expose the documented names from `annotated_types` without requiring the
  upstream tests or README to be installed.
- Use only deterministic standard-library behavior.  Metadata construction,
  equality, hashing, iteration, and representation must not access the
  network or depend on the current time.

## API Usage Guide

### Root exports and metadata classes

The root module exports these names through `__all__` in this order:

```text
BaseMetadata, GroupedMetadata, Gt, Ge, Lt, Le, Interval, MultipleOf,
MinLen, MaxLen, Len, Timezone, Predicate, LowerCase, UpperCase, IsDigits,
IsFinite, IsNotFinite, IsNan, IsNotNan, IsInfinite, IsNotInfinite, doc,
DocInfo, __version__
```

It also makes `Unit`, `IsDigit`, and `IsAscii` available as attributes for
backwards-compatible direct imports, even though those three are not in the
`__all__` tuple.  `__version__` is the string `"0.8.0"`.

`BaseMetadata` is an empty base class with no instance dictionary.  The
following are frozen, slotted dataclasses inheriting from it; their constructor
argument is positional unless stated otherwise, their field is readable, and
instances compare by value:

```python
Gt(gt)
Ge(ge)
Lt(lt)
Le(le)
MultipleOf(multiple_of)
MinLen(min_length)
MaxLen(max_length)
Timezone(tz)
Unit(unit)
Predicate(func)
```

`Gt`, `Ge`, `Lt`, and `Le` represent strict or inclusive comparisons.  The
stored boundary may be any object that can be compared with the eventual
value.  `MultipleOf` stores a divisor for consumers to interpret, and
`MinLen`/`MaxLen` store inclusive length bounds.  `Unit` stores its string
unchanged and performs no parsing or validation.

`Predicate(func)` stores a callable without invoking it during construction.
Its `func` field is public.  Its representation names ordinary functions and
built-in methods in an introspectable form (for example,
`Predicate(str.isascii)`), names a method descriptor by its qualified name,
and still produces a useful representation for lambdas.  The object itself is
not required to be callable.

### Grouped metadata

`GroupedMetadata` is a runtime-checkable protocol.  It exposes the property
`__is_annotated_types_grouped_metadata__`, whose value is exactly `True`, and
requires an `__iter__()` method yielding metadata objects.  A concrete
subclass that does not override `__iter__` must fail at class definition with
`TypeError`; the base implementation raises `NotImplementedError` if reached.
Structural implementers that provide the marker property and iterator are
accepted by `isinstance` checks.

```python
Interval(*, gt=None, ge=None, lt=None, le=None)
Len(min_length=0, max_length=None)
```

Both are frozen, slotted grouped metadata dataclasses.  `Interval` yields, in
order, `Gt`, `Ge`, `Lt`, and `Le` objects for each non-`None` bound.  `Len`
yields `MinLen(min_length)` only when the lower bound is positive, followed by
`MaxLen(max_length)` when an upper bound is not `None`.  Thus `Len()` yields
nothing, `Len(3)` yields one `MinLen`, and `Len(0, 4)` yields one `MaxLen`.

### Generic aliases and documentation metadata

These are `typing.Annotated` aliases and must retain their metadata when
subscripted with a concrete type:

- `LowerCase` uses `Predicate(str.islower)`.
- `UpperCase` uses `Predicate(str.isupper)`.
- `IsDigit` and its compatibility alias `IsDigits` use `Predicate(str.isdigit)`.
- `IsAscii` uses `Predicate(str.isascii)`.
- `IsFinite`, `IsNotFinite`, `IsNan`, `IsNotNan`, `IsInfinite`, and
  `IsNotInfinite` use `math.isfinite`, `math.isnan`, or `math.isinf`, with
  `Not(...)` for the negative forms.

`Not(func)` is a small dataclass-like wrapper with a public `func` attribute and
`__call__(value)` returning the boolean negation of `func(value)`.  It is used
inside the negative numeric aliases so consumers can introspect the wrapped
callable.

`doc(value)` is an alias for the documentation metadata class `Doc`; the
backwards-compatible `DocInfo` name is the same class.  A constructed object
has a `documentation` attribute containing the supplied value.  Prefer the
standard library where possible, but if `typing_extensions.Doc` is available
it may be reused; the aliases and attribute behavior must remain consistent.

## Implementation Notes

- Preserve dataclass value semantics, frozen assignment errors, slots, and
  useful `repr` output for the metadata classes.  Type annotations on fields
  are part of the public typing surface but are not runtime validators.
- Keep `GroupedMetadata` compatible with both nominal subclasses and
  structural implementers.  Iteration order is observable and deterministic.
- `Annotated` aliases must be built from the metadata objects above rather than
  from eagerly evaluated values.  Stacking an additional `Annotated` metadata
  item must preserve the original metadata order according to Python's typing
  semantics.
- Do not copy the upstream source or tests into the workspace.  The hidden
  verifier exercises the public behavior through an isolated child process.
- A minimal package layout is sufficient; documentation and development-only
  lint configuration are not required, but installation must work from the
  project root without network access during evaluation.
