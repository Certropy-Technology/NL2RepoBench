# Project Description

Build `typing_extensions` 4.14.1 as an installable Python package. The package
provides runtime implementations and backports for selected public objects from
Python's `typing` module, plus experimental typing objects that are not in
Python 3.12.

This task is deliberately scoped to behavior observable at runtime on CPython
3.12. It does not require, test, or claim parity with mypy, pyright, pyre, or
any other static type checker. Stubs, checker plugins, and behavior that exists
only during static analysis are outside the contract.

# Supports

- Python: CPython 3.12 on Linux.
- Distribution name and version: `typing_extensions==4.14.1`.
- Import module: `typing_extensions`.
- The repository must contain `pyproject.toml` and install successfully with
  `pip` from the repository root.
- Use `flit_core >=3.11,<4` as the build backend dependency. The package has no
  third-party runtime dependencies.
- The installed module may be provided as `src/typing_extensions.py` or an
  equivalent package layout, as long as the public imports and behavior below
  are preserved.

# API Usage Guide

## Export surface and standard-library interoperation

Define a duplicate-free `typing_extensions.__all__`. The following names must
exist and be present in `__all__`:

```text
Annotated Concatenate Doc Literal LiteralString Never NoDefault NotRequired
ParamSpec Protocol ReadOnly Required Self Sentinel TypeAliasType TypeGuard TypeIs
TypeVarTuple TypedDict Unpack assert_never assert_type clear_overloads
dataclass_transform deprecated evaluate_forward_ref final get_annotations
get_args get_origin get_original_bases get_overloads get_protocol_members
get_type_hints is_protocol is_typeddict overload override reveal_type
runtime_checkable
```

On Python 3.12, re-export `Any`, `Callable`, `ClassVar`, `Final`, `Generic`,
`NewType`, `Optional`, `Union`, `get_args`, `get_origin`, and `no_type_check`
as the identical objects from `typing`. `NamedTuple`, `TypeVar`, and
`get_type_hints` are extension implementations and are not identical to their
`typing` counterparts.

## Runtime type forms and introspection

`get_origin()` and `get_args()` must understand standard and extension forms.
Representative Python 3.12 results include:

```python
repr(Literal[1, "x", None]) == "typing.Literal[1, 'x', None]"
get_args(Literal[1, "x", None]) == (1, "x", None)

repr(ReadOnly[bytes]) == "typing_extensions.ReadOnly[bytes]"
get_origin(ReadOnly[bytes]) is ReadOnly
get_args(ReadOnly[bytes]) == (bytes,)

repr(TypeIs[tuple[int, ...]]) == "typing_extensions.TypeIs[tuple[int, ...]]"
get_origin(TypeIs[tuple[int, ...]]) is TypeIs
get_args(TypeIs[tuple[int, ...]]) == (tuple[int, ...],)
```

The corresponding `Literal`, `Final`, `ClassVar`, `Required`, `NotRequired`,
`TypeGuard`, `Unpack`, and `Concatenate` forms use normal `typing`-style repr,
origin, and argument behavior. `LiteralString`, `Never`, and `Self` have the
Python 3.12 reprs `typing.LiteralString`, `typing.Never`, and `typing.Self`.
`ParamSpec.args` and `ParamSpec.kwargs` both report that `ParamSpec` as their
origin.

Nested `Annotated` forms flatten their metadata in inner-to-outer order:

```python
value = Annotated[Annotated[int, "first"], {"level": 2}, 3]
value.__origin__ is int
value.__metadata__ == ("first", {"level": 2}, 3)
get_origin(value) is Annotated
get_args(value) == (int, "first", {"level": 2}, 3)
```

Such a form is unhashable when any metadata item is unhashable.

`TypeAliasType(name, value, *, type_params=())` exposes `__name__`, `__module__`,
`__value__`, and `__type_params__`. For this example:

```python
Item = TypeVar("Item")
Pair = TypeAliasType("Pair", tuple[Item, Item], type_params=(Item,))
```

`repr(Pair)` is `Pair`; `repr(Pair[int])` is `Pair[int]`; the specialized form
has `Pair` as its origin and `(int,)` as its arguments. Calling `Pair()` raises
`TypeError`.

`TypeVar`, `ParamSpec`, and `TypeVarTuple` accept a `default=` argument. Their
`__default__` attributes retain the supplied object and `has_default()` returns
true. Without a default, `__default__ is NoDefault`, `has_default()` returns
false, and `repr(NoDefault)` is `typing_extensions.NoDefault`.

`Doc(text)` stores the text as `.documentation`, has repr `Doc(<text repr>)`,
and can be used as `Annotated` metadata.

## Typed dictionaries

Support both class and functional `TypedDict` syntax, `total=`, inheritance,
`Required`, `NotRequired`, and `ReadOnly`. A typed dictionary class exposes
`__annotations__`, `__total__`, `__required_keys__`, `__optional_keys__`,
`__readonly_keys__`, and `__mutable_keys__`. For example:

```python
Payload = TypedDict(
    "Payload",
    {
        "identifier": int,
        "nickname": NotRequired[str],
        "checksum": ReadOnly[bytes],
    },
)
```

`Payload` is recognized by `is_typeddict()`. Its required keys are
`identifier` and `checksum`, its optional key is `nickname`, its read-only key
is `checksum`, and its mutable keys are `identifier` and `nickname`. Calling it
constructs an ordinary dictionary. `isinstance(value, Payload)` raises
`TypeError`.

Inheritance combines key metadata. A `total=False` base field is optional
unless wrapped in `Required`; fields declared by a total child are required.
`get_original_bases()` on the child returns its original typed-dictionary base.
Combining `closed=True` with `extra_items=` raises `TypeError`; passing a
non-iterable/non-mapping field specification raises `TypeError`.

`get_type_hints(obj)` strips `Required`, `NotRequired`, `ReadOnly`, and
`Annotated` extras by default. With `include_extras=True`, it preserves them.

## Protocols

`Protocol` supports class syntax and `runtime_checkable`. `is_protocol(cls)`
identifies protocol classes, and `get_protocol_members(cls)` returns a frozen
set of member names, including annotated data attributes and methods.

For a runtime protocol containing only methods, `isinstance()` and
`issubclass()` perform structural checks. A missing method produces false. For
a runtime protocol containing a data member, `isinstance()` can succeed but
`issubclass()` raises `TypeError`. Runtime checks against an undecorated
protocol raise `TypeError`. Applying `runtime_checkable` or
`get_protocol_members` to a non-protocol class also raises `TypeError`.

## Overloads and decorators

`overload` registers overload definitions by implementation module and
qualified name. `get_overloads(implementation)` returns the registered
definitions in declaration order with their signatures and annotations.
`clear_overloads()` empties the registry without changing the implementation.

`final` sets `__final__ = True` on decorated classes and methods while leaving
them callable. `override` sets `__override__ = True` on a method while leaving
it callable.

`deprecated(message, *, category=DeprecationWarning, stacklevel=1)` works on
functions and classes. It preserves normal calls, sets `__deprecated__` to the
message, and emits one warning of the configured category on each decorated
function call or class construction.

`dataclass_transform()` marks the decorated object with
`__dataclass_transform__`. The mapping retains `eq_default`, `order_default`,
`kw_only_default`, `frozen_default`, `field_specifiers`, and extra keyword
arguments under `kwargs`.

`no_type_check` sets `__no_type_check__ = True`. On a class it also marks its
methods. `get_type_hints()` returns an empty mapping for a marked callable,
without evaluating unresolved annotations.

## Runtime helpers

`assert_type(value, typ)` returns `value` unchanged. `reveal_type(value)`
returns `value` unchanged and writes `Runtime type is '<runtime name>'` to
standard error. `assert_never(value)` raises `AssertionError` with:

```text
Expected code to be unreachable, but got: <value repr>
```

The value repr is limited to 100 characters followed by `...` when needed.

`NewType("UserId", int)` exposes `__name__`, `__qualname__`, and
`__supertype__`; calling it returns its argument unchanged. The NewType object
is not a class, so using it as the second argument to `isinstance()` raises
`TypeError`.

`NamedTuple` class syntax supports annotations and rightmost field defaults.
Instances are tuple subclasses with `_fields`, `_field_defaults`, `_asdict()`,
and `_replace()` behavior matching `collections.namedtuple`.

`get_original_bases(cls)` returns `__orig_bases__` when present. It reports a
specialized generic base such as `Box[int]`, retains a built-in generic base
such as `list[int]`, and returns an empty tuple for `object`.

`get_annotations(obj, *, globals=None, locals=None, eval_str=False, format=...)`
returns a fresh annotations dictionary. With `eval_str=False`, strings remain
strings. With `eval_str=True`, evaluate strings using the supplied namespaces.

`evaluate_forward_ref(forward_ref, *, owner=None, globals=None, locals=None,
type_params=None, format=Format.VALUE)` recursively evaluates a
`typing.ForwardRef`. For globals containing `Item = int`, `ForwardRef("list[Item]")`
evaluates to `list[int]`. An unresolved name raises `NameError`.

`Buffer` is the runtime-checkable `collections.abc.Buffer` on Python 3.12.
`bytes`, `bytearray`, and `memoryview` are instances and subclasses; `str` is
not.

## Sentinel

`Sentinel(name, repr=None)` creates a fresh object every call. The default repr
is `<name>` and an explicit `repr=` string is used verbatim. The object retains
its name as `_name`, is truthy, compares only by identity, is not callable, and
cannot be pickled. Both `SomeType | sentinel` and `sentinel | SomeType` create
`typing.Union` forms containing that exact sentinel object.

## Error behavior for special forms

Subscripted `Literal` and `Annotated` forms cannot be used for runtime
`isinstance` checks and raise `TypeError`. `TypeGuard`, `Required`, and `Unpack`
accept exactly one subscription argument and raise `TypeError` when passed a
tuple of multiple arguments.

# Implementation Notes

- Keep all state, overload registries, warnings, reprs, metadata attributes,
  and exception behavior deterministic within one Python process.
- Runtime objects must interoperate with Python 3.12's `typing`, `inspect`,
  `warnings`, `pickle`, `collections.abc`, and `importlib.metadata` modules.
- Do not add network calls, environment-specific paths, or remote services.
- Examples in this specification define runtime behavior only; they are not a
  promise about acceptance or rejection by any static type checker.
