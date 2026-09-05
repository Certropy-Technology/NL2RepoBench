# pyrsistent

## Project Description

Build an installable `pyrsistent` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pyrsistent`; public import package begins at `pyrsistent`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Persistent vectors`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Persistent maps`: preserve the documented object or module behavior, including state and side effects.
3. `Persistent sets`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Persistent bags`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `pyrsistent`; public import package begins at `pyrsistent`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `iniconfig==2.3.0`, `packaging==26.3`, `pluggy==1.6.0`, `pygments==2.21.0`, `pytest==9.1.1`, `setuptools==80.10.2`, `wheel==0.45.1`
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

### Persistent vectors

```python
pvector(iterable=()) -> PVector
v(*elements) -> PVector
```

`PVector` implements immutable sequence behavior. It supports integer indexing,
negative indexes, slicing (which returns a `PVector`), iteration, length,
membership, `count`, `index`, equality, hashing, addition with another vector,
and repetition by an integer.

The following methods return new vectors and do not mutate the receiver:

- `append(value)` appends one value.
- `extend(iterable)` appends every value from an iterable.
- `set(index, value)` replaces an existing position. Index `len(vector)` is
  accepted as an append; larger indexes raise `IndexError`.
- `mset(index1, value1, index2, value2, ...)` performs multiple replacements.
- `delete(index, stop=None)` removes one position or the slice `[index:stop]`.
- `remove(value)` removes the first equal value or raises `ValueError`.
- `transform(*transformations)` applies the transformation contract below.
- `evolver()` returns a mutable transaction view. Its `append`, `extend`, item
  assignment, and deletion update only the evolver. `is_dirty()` reports
  whether it differs from the last persistent snapshot, and `persistent()`
  returns a `PVector` and clears the dirty flag.

### Persistent maps

```python
pmap(initial={}, pre_size=0) -> PMap
m(**kwargs) -> PMap
```

`pmap` accepts a mapping or an iterable of key/value pairs. `PMap` implements
immutable mapping behavior, including item access, iteration, length,
membership, `get`, `keys`, `values`, `items`, their `iter*` spellings, equality,
and hashing. String keys may also be read as attributes; a missing attribute
raises `AttributeError`.

Map update methods return new maps:

- `set(key, value)` inserts or replaces one item.
- `remove(key)` removes an item or raises `KeyError` when absent.
- `discard(key)` removes an item when present and otherwise returns the same
  map object.
- `update(*mappings)` merges mappings from left to right; later values win.
- `update_with(update_fn, *mappings)` calls `update_fn(old, new)` for keys that
  already exist and inserts new keys unchanged.
- `left + right` is a merge in which values from `right` win.
- `transform(*transformations)` applies the transformation contract below.
- `evolver()` supports mapping-style item assignment/removal, `is_dirty()`,
  and `persistent()` without changing the source map.

### Persistent sets

```python
pset(iterable=(), pre_size=8) -> PSet
s(*elements) -> PSet
```

`PSet` implements immutable set behavior and removes duplicates. It supports
membership, iteration, length, equality, hashing, subset/superset comparisons,
the `|`, `&`, `-`, and `^` operators, and the named `union`, `intersection`,
`difference`, `symmetric_difference`, `issubset`, `issuperset`, and
`isdisjoint` operations.

`add(value)`, `remove(value)`, and `discard(value)` return new sets. `remove`
raises `KeyError` for a missing value; `discard` returns the same set object
when the value is absent. `evolver()` supports `add`, `remove`, `is_dirty`, and
`persistent` transaction semantics.

### Persistent bags

```python
pbag(elements) -> PBag
b(*elements) -> PBag
```

`PBag` is an unordered, hashable multiset. Iteration repeats each value by its
multiplicity, membership tests whether its count is nonzero, and `len` counts
duplicates. `count(value)` returns zero for absent values. `add(value)`,
`update(iterable)`, and `remove(value)` return new bags; removing an absent
value raises `KeyError`.

Bag arithmetic follows `collections.Counter`-style positive multiplicities:

- `left + right` adds counts.
- `left - right` subtracts counts and omits zero or negative results.
- `left | right` keeps the maximum count per value.
- `left & right` keeps the minimum positive count per value.

Bags compare and hash by value and multiplicity, regardless of insertion
order. Comparing equality to a non-`PBag`, or ordering two bags, raises
`TypeError`.

### Persistent lists

```python
plist(iterable=(), reverse=False) -> PList
l(*elements) -> PList
```

`PList` is a hashable persistent singly linked sequence. A non-empty list has
public `first` and `rest` values. The empty list is false, has length zero,
returns itself from `rest`, and raises `AttributeError` for `first`.

It supports indexing, negative indexes, slicing to another `PList`, iteration,
length, `count`, `index`, equality, ordering against another persistent list,
and hashing. Invalid indexes raise `IndexError`.

- `cons(value)` prepends one value.
- `mcons(iterable)` repeatedly prepends, so iterable order is reversed.
- `reverse()` and `reversed(value)` return a persistent list.
- `split(index)` returns `(left, right)` persistent lists.
- `remove(value)` removes the first match or raises `ValueError`.

With `reverse=True`, `plist` constructs its result in reverse iterable order.

### Persistent deques

```python
pdeque(iterable=(), maxlen=None) -> PDeque
dq(*elements) -> PDeque
```

`PDeque` is a hashable persistent double-ended sequence. It supports indexing,
negative indexes, slicing to a `PDeque`, iteration, length, `count`, `index`,
equality, ordering against another `PDeque`, and hashing. Public `left` and
`right` properties return the end values and raise `IndexError` on an empty
deque.

- `append(value)` and `appendleft(value)` add one value at the corresponding
  end.
- `extend(iterable)` appends to the right. `extendleft(iterable)` repeatedly
  prepends and therefore reverses the iterable order.
- `pop(count=1)` and `popleft(count=1)` return a deque with up to `count`
  values removed. Removing from an empty deque returns an empty deque. A
  negative count delegates to the opposite end.
- `remove(value)` removes the first match from the left or raises `ValueError`.
- `reverse()` and `reversed(value)` return the reversed deque.
- `rotate(steps)` rotates right for positive steps and left for negative steps.

`maxlen` must be `None` or a non-negative integer. Construction keeps the last
`maxlen` values. Appending to a full bounded deque discards from the opposite
end. Invalid `maxlen` values raise `TypeError` or `ValueError`.

### Conversion and helper functions

```python
freeze(value, strict=True)
thaw(value, strict=True)
mutant(function)
get_in(keys, collection, default=None, no_default=False)
```

`freeze` recursively converts exact built-in lists to `PVector`, dictionaries
and `defaultdict` values to `PMap`, sets to `PSet`, and tuple members while
preserving the tuple. Dictionary keys and set elements are not recursively
converted. In strict mode, values inside existing `PVector` and `PMap` objects
are also traversed; `strict=False` leaves their existing nested values alone.

`thaw` is the inverse: vectors become lists, maps become dictionaries, sets
become sets, and tuple shape is preserved. In strict mode it also traverses
native lists and dictionaries; `strict=False` leaves persistent values nested
inside native containers untouched.

`mutant` decorates a function by freezing positional and keyword arguments
before the call and freezing the return value afterward. It preserves function
metadata.

`get_in` applies each key/index in order to nested persistent or built-in
collections. It returns `default` when a `KeyError`, `IndexError`, or
`TypeError` prevents traversal. With `no_default=True`, it re-raises the
original exception.

### Named-tuple immutable type

```python
immutable(members="", name="Immutable", verbose=False) -> type
```

Create a named-tuple-like immutable type from a comma/space-separated string
or iterable of member names. Instances have named attributes and `_fields`.
`instance.set(**changes)` returns a new instance of the same class. With no
changes it returns the same object. Unknown names raise `AttributeError`.
Member names ending in `_` are frozen and cannot be changed with `set`.

### Transformations

`PVector`, `PMap`, `PRecord`, `PClass`, and checked collections provide:

```python
value.transform(path1, command1, path2, command2, ...)
```

Each path is a sequence of keys/indexes. A callable path component is a
matcher; it is invoked with a key/index, or with `(key_or_index, value)` when it
accepts two arguments, and every match is transformed. A callable command is
applied to the selected value; a non-callable command replaces it. Multiple
path/command pairs are processed left to right. A matcher that selects nothing
returns the original persistent object by identity.

Helper commands and matchers:

- `inc(value)` returns `value + 1`.
- `discard(evolver, key)` is the special command that removes a selected item.
- `rex(expression)` returns a matcher using `re.match` against keys.
- `ny(value)` always returns `True` and matches every key or index.

Transformations preserve untouched nested persistent objects when possible.

### Records, classes, and fields

Declare fixed-field types by subclassing `PRecord` or `PClass` and assigning
field descriptors:

```python
field(
    type=...,
    invariant=...,
    initial=...,
    mandatory=False,
    factory=...,
    serializer=...,
)
```

`PRecord` is also a `PMap`; fields are available by attribute and item access.
`PClass` is an immutable ordinary object rather than a mapping. Both support
value equality, readable class-name representations, `set`, `remove`,
`transform`, `evolver`, `create`, and `serialize`.

- A field `type` may be one type or an iterable of allowed types. A mismatch
  raises `PTypeError`.
- `mandatory=True` requires the field. Missing mandatory fields raise
  `InvariantException`, whose `missing_fields` names the qualified fields.
- `initial` supplies a default value.
- `factory` receives the supplied field value before type/invariant checks.
  When a field type is another `PRecord` and no factory is supplied, nested
  mappings are converted through that record's `create` method.
- A field invariant returns `(boolean, error)` or an iterable of such pairs.
  A class-level `__invariant__` validates the complete object after field
  invariants pass. Failures raise `InvariantException`; `invariant_errors`
  preserves the reported error objects.
- `serializer(format, value)` customizes field serialization. Without one,
  `serialize(format=None)` recursively serializes checked collections, records,
  and classes to built-in containers.
- `create(mapping, _factory_fields=None, ignore_extra=False)` constructs an
  instance and recursively uses factories. Unknown fields raise
  `AttributeError` unless `ignore_extra=True`.

Collection field helpers convert and check every element:

```python
pset_field(item_type, optional=False, initial=(), ...)
pvector_field(item_type, optional=False, initial=(), ...)
pmap_field(key_type, value_type, optional=False, invariant=..., ...)
```

`optional(type1, type2, ...)` returns the supplied allowed types with
`type(None)` appended.

### Checked collections

Subclass `CheckedPVector`, `CheckedPSet`, or `CheckedPMap` to enforce types and
invariants while retaining the corresponding persistent collection API:

- Vector/set subclasses declare `__type__`; map subclasses declare
  `__key_type__` and `__value_type__`.
- `__invariant__(value)` may return `(boolean, error)` for each value.
- `create(source_data, _factory_fields=None, ignore_extra=False)` recursively
  constructs checked values.
- Wrong vector/set values or map values raise `CheckedValueTypeError`; wrong
  map keys raise `CheckedKeyTypeError`; invariant failures raise
  `InvariantException`.
- All update paths, including direct methods, transformations, and evolvers,
  enforce the checks.
- `serialize()` returns built-in lists, sets, and dictionaries, recursively
  applying serializers of nested checked values.


- All apparent update operations must preserve the original object and return
  persistent values. Empty/no-op operations may return the original instance.
- Do not rely on iteration order for maps, sets, or bags. Preserve sequence
  order for vectors, lists, and deques.
- Exceptions described above are part of the public contract. Ordinary missing
  keys/indexes and failed invariants must not be silently ignored.
- Keep public imports in `pyrsistent`; callers should not need private module
  paths.
- Keep runtime behavior deterministic and offline. Tests and examples in the
  repository may be self-authored, but the evaluator supplies independent
  hidden checks.

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
(
    "pmap", "m", "PMap", "pvector", "v", "PVector",
    "pset", "s", "PSet", "pbag", "b", "PBag",
    "plist", "l", "PList", "pdeque", "dq", "PDeque",
    "CheckedPMap", "CheckedPVector", "CheckedPSet",
    "InvariantException", "CheckedKeyTypeError", "CheckedValueTypeError",
    "CheckedType", "optional", "PRecord", "field", "pset_field",
    "pmap_field", "pvector_field", "PClass", "PClassMeta",
    "immutable", "freeze", "thaw", "mutant", "get_in",
    "inc", "discard", "rex", "ny",
)
```

### Example 2: ordinary usage
```text
pvector(iterable=()) -> PVector
v(*elements) -> PVector
```

### Example 3: boundary or error behavior
```text
pmap(initial={}, pre_size=0) -> PMap
m(**kwargs) -> PMap
```

### Example 4: boundary or error behavior
```text
pset(iterable=(), pre_size=8) -> PSet
s(*elements) -> PSet
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
