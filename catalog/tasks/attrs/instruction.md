# Build `attrs`

Create a complete, installable Python project named `attrs` from an empty
workspace. The project is a pure-Python class-building library. It must expose
both the modern `attrs` import package and the compatibility `attr` import
package, with the public behavior described below. Do not depend on a
preinstalled copy of `attrs` or on network access at runtime.

## Project Description

The library turns ordinary Python classes and declared fields into concise data
model classes. It generates initialization, representation, equality,
ordering, hashing, slots, weak-reference, pattern-matching, and pickling
behavior while allowing applications to supply defaults, factories, converters,
validators, comparison keys, field transformers, and assignment hooks.

The distribution is named `attrs`. The two import packages are `attrs` and
`attr`; they share the same implementation and exception objects. The frozen
candidate report identifies release metadata as `26.1.0`. The installed
distribution version and the lazy `attr.__version__` and `attrs.__version__`
values must agree, and `__version_info__` must be a comparable
`attr.VersionInfo` object.

## Supports

- Support CPython 3.10 and newer Python 3.x versions in the supported source
  range. Keep version-dependent behavior explicit and do not require PyPy or a
  non-CPython implementation for ordinary use.
- Provide an installable `src/` layout containing both `attr/` and `attrs/`.
- Declare no third-party runtime dependencies. Build and test tools are not
  runtime imports of the installed library.
- Include `py.typed` markers and useful stubs for the public modules. Runtime
  behavior must not depend on type checkers.
- Install and import without the verifier tests being present in the workspace.
- Keep runtime behavior local: no network, subprocess, filesystem, or service
  calls are required by normal field creation, class decoration, conversion,
  validation, introspection, or serialization operations.
- Preserve the public module names, aliases, exception identity, warning
  behavior, generated method metadata, and ordinary Python data-model protocol.

## Public API Inventory

The following names are required. Names beginning with an underscore are not
part of the required application-facing API, even if upstream tests inspect
some of them internally.

### `attr` package

`attr.__all__` contains:

```text
NOTHING, Attribute, AttrsInstance, Converter, Factory, NothingType,
asdict, assoc, astuple, attr, attrib, attributes, attrs, cmp_using,
converters, define, evolve, exceptions, field, fields, fields_dict, filters,
frozen, get_run_validators, has, ib, make_class, mutable, resolve_types, s,
set_run_validators, setters, validate, validators
```

The compatibility aliases have these identities and meanings:

- `attr.s`, `attr.attributes`, and `attr.attrs` are the classic class decorator.
- `attr.ib`, `attr.attr`, and `attr.attrib` are the classic field maker.
- `attr.define`, `attr.field`, `attr.mutable`, and `attr.frozen` are the modern
  APIs re-exported through the compatibility namespace.
- `attr.dataclass` is a compatibility alias for the classic decorator with
  `auto_attribs=True`.
- `attr.VersionInfo` is the version comparison class even though it is not in
  the `__all__` list.

### `attrs` package

`attrs.__all__` contains:

```text
NOTHING, Attribute, AttrsInstance, ClassProps, Converter, Factory,
NothingType, __author__, __copyright__, __description__, __doc__, __email__,
__license__, __title__, __url__, __version__, __version_info__, asdict, assoc,
astuple, cmp_using, converters, define, evolve, exceptions, field, fields,
fields_dict, filters, frozen, has, inspect, make_class, mutable, resolve_types,
setters, validate, validators
```

`attrs` does not need to re-export all classic aliases. It must expose the
listed modules and objects, and all corresponding `attr.*` and `attrs.*`
exception, converter, filter, setter, and validator imports must refer to the
same objects.

### Submodules

The following submodule functions and values are public from both namespaces:

- `attrs.converters` / `attr.converters`: `pipe`, `optional`,
  `default_if_none`, and `to_bool`.
- `attrs.validators` / `attr.validators`: `set_disabled`, `get_disabled`,
  `disabled`, `instance_of`, `optional`, `in_`, `and_`, `matches_re`,
  `deep_iterable`, `deep_mapping`, `is_callable`, `lt`, `le`, `ge`, `gt`,
  `ne`, `max_len`, `min_len`, `not_`, and `or_`.
- `attrs.setters` / `attr.setters`: `frozen`, `pipe`, `validate`, `convert`,
  and the `NO_OP` sentinel.
- `attrs.filters` / `attr.filters`: `include` and `exclude`.
- `attrs.exceptions` / `attr.exceptions`: `FrozenError`,
  `FrozenInstanceError`, `FrozenAttributeError`,
  `AttrsAttributeNotFoundError`, `NotAnAttrsClassError`,
  `DefaultAlreadySetError`, `UnannotatedAttributeError`, `PythonTooOldError`,
  and `NotCallableError`.

## Core Signatures

Implement these signatures. A bare decorator form such as `@define` and a
factory form such as `@define(...)` are both supported where `maybe_cls` is
present.

```python
attrs.field(
    *, default=attrs.NOTHING, validator=None, repr=True, hash=None,
    init=True, metadata=None, type=None, converter=None, factory=None,
    kw_only=None, eq=None, order=None, on_setattr=None, alias=None,
)

attr.attrib(
    default=attr.NOTHING, validator=None, repr=True, cmp=None, hash=None,
    init=True, metadata=None, type=None, converter=None, factory=None,
    kw_only=None, eq=None, order=None, on_setattr=None, alias=None,
)

attrs.define(
    maybe_cls=None, *, these=None, repr=None, unsafe_hash=None, hash=None,
    init=None, slots=True, frozen=False, weakref_slot=True, str=False,
    auto_attribs=None, kw_only=False, cache_hash=False, auto_exc=True,
    eq=None, order=False, auto_detect=True, getstate_setstate=None,
    on_setattr=None, field_transformer=None, match_args=True,
    force_kw_only=False,
)

attr.attrs(
    maybe_cls=None, these=None, repr_ns=None, repr=None, cmp=None, hash=None,
    init=None, slots=False, frozen=False, weakref_slot=True, str=False,
    auto_attribs=False, kw_only=False, cache_hash=False, auto_exc=False,
    eq=None, order=None, auto_detect=False, collect_by_mro=False,
    getstate_setstate=None, on_setattr=None, field_transformer=None,
    match_args=True, unsafe_hash=None, force_kw_only=True,
)

attrs.asdict(inst, *, recurse=True, filter=None, value_serializer=None)
attrs.astuple(inst, *, recurse=True, filter=None)
attr.asdict(
    inst, recurse=True, filter=None, dict_factory=dict,
    retain_collection_types=False, value_serializer=None,
)
attr.astuple(
    inst, recurse=True, filter=None, tuple_factory=tuple,
    retain_collection_types=False,
)

attrs.fields(cls_or_instance)
attrs.fields_dict(cls)
attrs.has(cls)
attrs.resolve_types(
    cls, globalns=None, localns=None, attribs=None, include_extras=True,
)
attrs.evolve(inst, **changes)
attr.assoc(inst, **changes)
attrs.validate(inst)
attrs.make_class(name, attrs, bases=(object,), class_body=None, **attributes_arguments)
attrs.cmp_using(
    eq=None, lt=None, le=None, gt=None, ge=None,
    require_same_type=True, class_name="Comparable",
)
attrs.inspect(cls)
```

`attrs.mutable` is an alias of `attrs.define`. `attrs.frozen` has the
`attrs.define` options while fixing `frozen=True` and `on_setattr=None`.
`attr.s` and `attr.attrs` are the same classic decorator; `attr.ib` and
`attr.attrib` are the same classic field maker. `attr.make_class` and all
other root re-exports retain the same behavior as their `attrs` counterparts.

## Fields, Defaults, and Metadata

`field()` and `attrib()` return a field marker that is inert until the class is
decorated. A field has these observable properties after decoration:

```text
name, default, validator, repr, eq, eq_key, order, order_key, hash, init,
metadata, type, converter, kw_only, inherited, on_setattr, alias,
alias_is_default
```

`Attribute` instances are read-only, slot-based descriptors. Their metadata is
a shallow copied, read-only mapping. `Attribute.evolve(**changes)` returns a
new field definition and updates an automatically generated alias when its
name changes; an explicit alias remains explicit. Fields are comparable,
hashable where their values allow it, and pickle-compatible.

The default is `NOTHING`, a sentinel distinct from `None`. A missing required
field must make the generated initializer raise `TypeError`. `factory=f` is
equivalent to a `Factory(f)` default and creates a fresh value per instance.
`Factory(factory, takes_self=False)` stores a callable; with `takes_self=True`
the partially initialized instance is passed as its argument. Do not share a
mutable default merely because it is convenient.

The classic and modern field makers accept the same field concepts but differ
in call syntax and in the classic `cmp` compatibility argument. `converter`
and `validator` may be a callable or a list/tuple; a sequence is composed in
order. `metadata` is arbitrary application data. `type` is stored metadata and
is not runtime type checking by itself. `eq`, `order`, `repr`, and `hash` may
be booleans or supported key/format callables as documented by their
signatures. `init=False` excludes a field from the generated initializer.

Leading underscores are stripped from generated initializer argument names.
`alias` overrides this behavior. A field with `kw_only=True` must be passed by
keyword. Class-level `kw_only` applies according to the decorator's modern or
classic defaults, while an explicit field setting wins. Mandatory fields cannot
follow a defaulted positional field unless they are keyword-only.

The field marker also supports decorator notation for a field's default,
validator, and converter. The decorated helper must not overwrite the field
name itself. Defaults and factories run while the instance is being built, so
they may observe only the initialization state available at their position.

## Class Decoration

The decorator discovers fields from type annotations and field markers. With
the modern APIs, `auto_attribs=None` detects whether annotations or explicit
field markers are the intended mode; `ClassVar` values are ignored. In
annotation mode, every attrs field marker must have an annotation and a mixed
unannotated marker raises `UnannotatedAttributeError`. In explicit field mode,
unrelated annotations are not silently promoted to fields. `these={name:
field}` provides an explicit field mapping and can decorate a class that was
not authored with attrs fields.

Inherited fields follow declaration order. `collect_by_mro=True` uses proper
method-resolution-order collection; the classic default preserves its legacy
behavior. Generic attrs classes and their specialized forms are supported by
introspection.

The generated initializer accepts positional and keyword arguments according
to field order, aliases, defaults, and keyword-only settings. Its operation
order is:

1. Run `__attrs_pre_init__` when present.
2. For each field, obtain its default or factory and run its converter.
3. Run all field validators.
4. Run `__attrs_post_init__` when present.

Converters run before validators. `init=False` fields are initialized from
their default/factory but are not accepted by the generated initializer. When
`init=False` or an existing initializer prevents replacement, provide the
generated initializer as `__attrs_init__` for a custom initializer to call.

Decorated classes expose `__attrs_attrs__` as their tuple of `Attribute`
objects. `attrs.fields()` accepts an attrs class or an attrs instance and
returns that tuple; the tuple supports both integer indexing and attribute-name
lookup. `attrs.fields_dict()` accepts a class and returns an insertion-ordered
mapping from field names to the same `Attribute` objects. Invalid inputs raise
the documented `TypeError` or `NotAnAttrsClassError` rather than returning an
empty result.

Decorators add or preserve these protocols according to their options:

- `repr=True` creates a readable class-qualified `__repr__`; a field formatter
  callable supplies its string directly. `str=True` adds a matching `__str__`.
- `eq=True` creates `__eq__` and `__ne__` that compare only identical class
  types. `order=True` creates all four ordering methods and also requires
  equality. Different types return `NotImplemented` where Python expects it.
  Field-level key callables transform values before comparison.
- `unsafe_hash`, the legacy `hash` option, `frozen`, `eq`, and `cache_hash`
  determine hash generation. Equal objects must hash equally. A frozen,
  equality-based class is hashable by default; an equality-based mutable class
  is normally unhashable; `cache_hash=True` caches a generated hash and is only
  valid when attrs generates a hash method. Field-level `hash` selects values.
- `slots=True` creates a slotted class, with `weakref_slot` controlling the
  weak-reference slot. Generated slotted classes remain pickle-compatible and
  must not accidentally retain a `__dict__` when slots prohibit one.
- `match_args=True` creates `__match_args__` for positional structural pattern
  matching. On Python versions that support it, attrs-generated classes also
  expose the expected replacement protocol.
- `getstate_setstate` controls generated pickling helpers for slotted classes.
- `auto_detect=True` preserves a method implemented directly on the class for
  `__init__`, `__repr__`, equality, hash, or ordering instead of blindly
  replacing it. Explicit flags override detection.
- `auto_exc=True` gives attrs exception subclasses appropriate `args` behavior
  and leaves exception identity comparison semantics intact.

`attrs.define` defaults to modern slotted classes, equality, converters and
validators on assignment, automatic method detection, and no ordering.
`attr.attrs`/`attr.s` retain classic defaults: dict classes, classic typing
discovery, no automatic assignment hook when `on_setattr` is omitted, and
classic equality/order defaults. These default differences are part of the
contract; aliases must not collapse them accidentally.

`frozen` classes reject assignment and deletion with `FrozenInstanceError` and
the message `can't set attribute`. `attrs.setters.frozen` rejects assignment
of one field with `FrozenAttributeError`. A frozen class can initialize
derived fields in `__attrs_post_init__` only through the same explicit
`object.__setattr__` technique available to ordinary Python classes.

## Assignment Hooks

`on_setattr` receives `(instance, attribute, new_value)`. Its return value is
stored as the new field value. A list/tuple is composed with
`attrs.setters.pipe`. The built-in setters are:

- `convert`: apply the field converter, if any;
- `validate`: apply the field validator unless validators are globally
  disabled;
- `frozen`: raise `FrozenAttributeError`;
- `pipe(*setters)`: pass the value through each setter in order;
- `NO_OP`: disable assignment hooks for one field even when the class has a
  default hook.

Modern `define` uses conversion and validation on ordinary assignment by
default; classic `attr.s` does not add that hook unless requested. Assignment
hooks are not a replacement for initializer conversion and validation.

A generator hook may yield exactly once. Code before the yield runs before the
assignment, code after it runs afterward, and the yielded value is assigned.
Exceptions propagate. A hook yielding zero or multiple times is invalid.

## Introspection and Copying

`has(cls)` returns whether a class is attrs-decorated, including supported
generic specializations, and raises `TypeError` for non-class inputs. It must
not claim ordinary classes are attrs classes.

`resolve_types(cls, globalns=None, localns=None, attribs=None,
include_extras=True)` resolves forward and string annotations into the
`Attribute.type` values and returns the same class, so it can be used as a
decorator. Missing names raise `NameError`; a non-attrs class without an
explicit `attribs` list raises `NotAnAttrsClassError`.

`evolve(inst, **changes)` creates a new instance by calling the generated
initializer. The instance must be positional, private field names are written
using their initializer aliases, `init=False` fields cannot be changed, and
normal converters and validators run. Unknown initializer names raise
`TypeError`. `assoc(inst, **changes)` is the older compatibility operation: it
copies the instance and assigns fields directly, raises
`AttrsAttributeNotFoundError` for unknown attrs fields, and remains available
with its deprecation semantics.

`attrs.validate(inst)` runs all validators for the instance and lets their
exceptions propagate. If validators are globally disabled it is a no-op.

`attrs.inspect(cls)` returns the experimental `ClassProps` record for a
decorated class and raises `NotAnAttrsClassError` otherwise. Its observable
properties include `is_exception`, `is_slotted`, `has_weakref_slot`,
`is_frozen`, `kw_only`, `collected_fields_by_mro`, `added_init`, `added_repr`,
`added_eq`, `added_ordering`, `hashability`, `added_match_args`, `added_str`,
`added_pickling`, `on_setattr_hook`, `field_transformer`, and the
`is_hashable` property.

## Collection Conversion

`attr.asdict(inst, recurse=True, filter=None, dict_factory=dict,
retain_collection_types=False, value_serializer=None)` converts attrs fields
to a dictionary. `attrs.asdict(inst, *, recurse=True, filter=None,
value_serializer=None)` is the modern convenience form that always uses
`dict` and retains collection types. Both recurse into attrs instances and
nested lists, tuples, sets, frozensets, and dictionaries when requested. The
classic form converts nested tuple/set-like collections to lists unless
`retain_collection_types=True`; dictionary keys are handled as tuple-like
collections when needed to remain usable as keys.

`attr.astuple(inst, recurse=True, filter=None, tuple_factory=tuple,
retain_collection_types=False)` and `attrs.astuple(inst, *, recurse=True,
filter=None)` provide the corresponding tuple conversion. The modern form
retains collection types and uses `tuple`. A custom factory may produce a list
or another collection in the classic form.

The `filter(attribute, value)` callback decides whether a field is included.
`filters.include(*what)` keeps values whose type, field name, or `Attribute`
object is listed; `filters.exclude(*what)` removes those values. Both helpers
accept types, strings, and `Attribute` instances. `value_serializer(instance,
attribute, value)` runs after filtering and can replace values, including
nested collection values where the conversion contract supplies no attrs
instance or field.

## Comparison Helper

`cmp_using(eq=None, lt=None, le=None, gt=None, ge=None,
require_same_type=True, class_name="Comparable")` returns a wrapper class whose
instances hold one `.value`. Supplied comparison callables receive the wrapped
values. When `require_same_type` is true, comparisons between different value
types return `NotImplemented`. At least equality and a complete enough set of
ordering operations must be supplied for total ordering; otherwise raise the
documented `ValueError`. The resulting type is intended for a field-level
`eq`/`order` key and should preserve normal Python comparison behavior.

## Validators

Validators are callables with `(instance, attribute, value)` arguments. They
return normally on success and raise on failure. Implement these semantics:

- `instance_of(type_or_tuple)` uses `isinstance` and raises `TypeError` with
  the attribute, expected type, and received value information.
- `optional(validator_or_sequence)` accepts `None` and delegates non-`None`
  values to the child validator(s).
- `in_(options)` checks membership. Lists, dictionaries, and sets may be
  normalized to tuples internally to keep the validator hashable, while error
  messages retain the original options.
- `and_(*validators)` runs every child. `or_(*validators)` succeeds at the
  first child that returns and otherwise raises `ValueError` after attempting
  every child.
- `matches_re(regex, flags=0, func=None)` accepts a string or compiled pattern
  and defaults to full matching. `func` may select `re.fullmatch`, `re.search`,
  or `re.match`; flags are only accepted with a string pattern.
- `deep_iterable(member_validator, iterable_validator=None)` optionally checks
  the iterable itself and then every member. `deep_mapping(key_validator=None,
  value_validator=None, mapping_validator=None)` checks the mapping and/or its
  keys and values; at least one key or value validator is required.
- `is_callable()` raises `NotCallableError` for non-callable values.
- `lt`, `le`, `ge`, `gt`, and `ne` compare against an inclusive or exclusive
  bound as named and raise `ValueError` on failure.
- `max_len` and `min_len` compare `len(value)` to the supplied bound.
- `not_(validator, *, msg=None, exc_types=(ValueError, TypeError))` inverts a
  validator by suppressing configured child exceptions and raising
  `ValueError` when the child succeeds. Other exception types propagate.

`set_disabled(bool)` and `get_disabled()` control a process-global validator
switch. `disabled()` is a nestable context manager that restores the previous
state. This state is intentionally not thread-safe; do not substitute
thread-local behavior. The legacy `attr.set_run_validators` and
`attr.get_run_validators` expose the inverse configuration state.

## Converters

Converters receive a field's incoming value and return the stored value. They
run before validators. `Converter(converter, *, takes_self=False,
takes_field=False)` can additionally receive the partially initialized
instance and/or its `Attribute`, in that order. `converters.pipe(*converters)`
passes the result through each converter and is the identity when empty.
`converters.optional(converter)` leaves `None` unchanged and converts other
values. `converters.default_if_none(default=NOTHING, factory=None)` replaces
`None` with a fixed default or the result of a zero-argument factory; exactly
one of default/factory must be provided, and a `Factory(takes_self=True)` is
invalid for this helper. `converters.to_bool` accepts the true spellings
`True`, `"true"`, `"t"`, `"yes"`, `"y"`, `"on"`, `"1"`, and `1`, and the false
spellings `False`, `"false"`, `"f"`, `"no"`, `"n"`, `"off"`, `"0"`, and `0`.
Other values raise `ValueError`.

## Version and Exceptions

`VersionInfo(year, minor, micro, releaselevel)` is immutable, hashable, and
compares with another `VersionInfo` or a tuple of length 1 through 4. Invalid
comparison operands return `NotImplemented` through normal Python comparison
protocol. The installed metadata version is parsed into
`__version_info__`; a three-component version uses release level `final`.

All exception classes are importable from both namespaces and preserve these
base classes and purposes:

- `FrozenError(AttributeError)` is the common immutable-assignment error;
  `FrozenInstanceError` and `FrozenAttributeError` specialize it.
- `AttrsAttributeNotFoundError(ValueError)` reports an unknown attrs field.
- `NotAnAttrsClassError(ValueError)` reports an invalid class/instance target.
- `DefaultAlreadySetError(RuntimeError)` reports conflicting defaults.
- `UnannotatedAttributeError(RuntimeError)` reports a missing annotation in
  strict `auto_attribs` mode.
- `PythonTooOldError(RuntimeError)` reports an unavailable Python feature.
- `NotCallableError(TypeError)` reports a required callable that is not
  callable, retaining its message and offending value.

Unsupported package metadata attributes must raise `AttributeError` with the
normal module-qualified message. `attr.converters`, `attr.validators`, and
`attr.filters` may be loaded lazily, but direct imports must work.

## Determinism and Boundaries

Preserve declaration and MRO order wherever the API promises order. Do not
depend on hash iteration order for field discovery. Generated reprs and
signatures must be stable for the same module, class, field order, options, and
Python version. Python hash randomization and runtime-specific generated
function filenames are not observable ordering contracts. Validator global
state, metadata resolution, and generic-class caching are process state and
must not be silently made thread-local.

The library must not require native extensions, Rust, Cython, network access,
or subprocesses at runtime. Optional development paths are not part of the
runtime contract: cloudpickle compatibility is conditional on CPython,
pympler size checks are optional and unavailable on PyPy, and Pyright/Mypy/
Pyrefly/ty/docs/lint/xdist are separate tooling concerns. Keep Python-version
branches and deprecation warnings observable. Do not use wall-clock timing to
define library behavior.

The finished repository must be implementable from this document and ordinary
Python standard-library knowledge. Do not copy source bodies, upstream test
assertions, generated code, or private verifier details into the project.

## Deterministic Verification Scope

The production task uses a fixed denominator of 20 deterministic, offline
behavior scenarios. Their public behavior areas are: modern definition,
converter and validator ordering, fresh factories, keyword-only and aliased
fields, classic compatibility, frozen assignment errors, assignment hooks,
validator composition, validator disable state, converter helpers, recursive
collection conversion, field introspection and metadata, evolve, inherited
field order, make_class, ordering and hashing, forward type resolution,
value serialization, post-init derived fields, and package aliases/version
metadata. The verifier reconstructs classes and callback recipes from an
