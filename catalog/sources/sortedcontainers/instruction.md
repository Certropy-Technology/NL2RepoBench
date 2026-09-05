# Project Description

Build an installable pure-Python distribution named `sortedcontainers`, version
`2.4.0`, from an empty workspace. The package provides sorted sequence, set,
and mapping types through the top-level `sortedcontainers` import. Containers
must remain ordered after mutation and must expose the sequence, range, set,
mapping, and live-view behavior described below.

This task uses a bounded **sorted-container scenario contract v1**. The public
container behavior is evaluated with deterministic local values and JSON-safe
scenario inputs.

## Natural Language Instruction

Create `sortedcontainers` from an empty workspace as a complete installable python project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `sortedcontainers`. Primary import or package entry: `sortedcontainers`.
- CPython 3.12.14 on debian-12-amd64 with pip.
- Install from `workspace/` using `python -m pip install .`.
- Declared dependency closure: setuptools==84.0.0. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `pytest`. A fixed collection
  contains `30` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── sortedcontainers/
│   ├── __init__.py
│   ├── sortedlist.py
│   ├── sortedset.py
│   └── sorteddict.py
└── README.md
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### `SortedList` and `SortedKeyList`

```python
SortedList(iterable=None, key=None)
SortedKeyList(iterable=None, key=identity)
```

`SortedList` is a mutable sequence that sorts values in ascending comparison
order and retains duplicates. Supplying a non-`None` key to `SortedList`
constructs a `SortedKeyList`. Equal-key values retain their insertion order.
The read-only `key` property is `None` for an ordinary `SortedList` and is the
callable supplied to `SortedKeyList`.

Implement sequence behavior for `len`, membership, iteration, reversed
iteration, integer indexing (including negative indexes), slicing (including
negative steps), item and slice deletion, equality and lexicographic ordering.
Implement these mutation and query methods:

```python
add(value)
update(iterable)
clear()
discard(value)
remove(value)
pop(index=-1)
count(value)
index(value, start=None, stop=None)
bisect_left(value)
bisect_right(value)
bisect(value)                 # alias of bisect_right
islice(start=None, stop=None, reverse=False)
irange(minimum=None, maximum=None, inclusive=(True, True), reverse=False)
copy()
```

`discard` is a no-op when absent; `remove` and `index` raise `ValueError` when
the value is absent. An invalid or empty `pop` raises `IndexError`. A slice
step of zero raises `ValueError`. `islice` uses positional slice bounds.
`irange` uses value bounds and honors the two inclusive flags. `+`, `+=`, `*`,
and `*=` return or mutate sorted lists while retaining duplicates.

`SortedKeyList` additionally implements:

```python
irange_key(min_key=None, max_key=None, inclusive=(True, True), reverse=False)
bisect_key_left(key)
bisect_key_right(key)
bisect_key(key)               # alias of bisect_key_right
```

Value-based membership, removal, count, and index distinguish values even when
their computed keys are equal. The inherited value-bisect methods compute the
argument's key and delimit its complete equal-key group; the explicit key-range
and key-bisect methods operate directly on keys. Both include every equal-key
value in stable order.

### `SortedSet`

```python
SortedSet(iterable=None, key=None)
```

`SortedSet` stores unique hashable values while exposing them in sorted order.
It implements ordinary mutable-set comparisons and membership plus sequence
indexing, slicing, item and slice deletion, iteration, and reversed iteration.
With a key function, sequence order follows the computed key and equal-key
values remain stable.

Implement `add`, `update`, `clear`, `discard`, `remove`, `pop(index=-1)`,
`count`, `index`, `copy`, `islice`, `irange`, `irange_key`, the value and key
bisect methods listed for sorted lists, and the standard methods
`difference`, `difference_update`, `intersection`, `intersection_update`,
`symmetric_difference`, `symmetric_difference_update`, `union`,
`isdisjoint`, `issubset`, and `issuperset`. Operators `-`, `&`, `^`, `|` and
their in-place forms have the corresponding set meanings and preserve the
receiver's sort key.

Adding an existing value has no effect. `discard` ignores an absent value;
`remove` raises `KeyError`. `pop` removes and returns the value at the sorted
position and raises `IndexError` for an empty or invalid position.

### `SortedDict` and views

```python
SortedDict(*args, **kwargs)
```

When the first positional argument is callable it is the key function used to
sort dictionary keys; remaining arguments initialize the mapping. Otherwise
construction follows `dict`. Mapping equality and key lookup follow ordinary
dictionary behavior, while iteration and `reversed` yield sorted keys.

Implement normal mapping assignment, deletion, membership, `len`, `get`,
`clear`, `copy`, `fromkeys`, `update`, `setdefault`, `pop`, and:

```python
popitem(index=-1)
peekitem(index=-1)
index(key, start=None, stop=None)
bisect_left(key)
bisect_right(key)
bisect(key)
islice(start=None, stop=None, reverse=False)
irange(minimum=None, maximum=None, inclusive=(True, True), reverse=False)
irange_key(min_key=None, max_key=None, inclusive=(True, True), reverse=False)
bisect_key_left(key)
bisect_key_right(key)
bisect_key(key)
keys()
items()
values()
```

`peekitem` returns the key/value pair at a sorted position without mutation;
`popitem` removes that pair. Both default to the final pair. `popitem` on an
empty mapping raises `KeyError`; invalid non-empty positions for `peekitem`
raise `IndexError`. Mapping `|`, reflected `|`, and `|=` use normal dictionary
merge precedence while returning or preserving a `SortedDict` where the
sorted dictionary is the implementing operand.

`keys()`, `items()`, and `values()` return `SortedKeysView`,
`SortedItemsView`, and `SortedValuesView`. They are live views: later mapping
updates are reflected in their length, membership, order, indexing, slicing,
and reversed iteration. Keys and items views also implement the ordinary
set-view comparisons and `&`, `|`, `-`, and `^` operations.

## Implementation Notes

Preserve all public return shapes, ordering, state transitions, and exception contracts described above. Keep installation metadata and public imports consistent and deterministic.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```python
SortedList(iterable=None, key=None)
SortedKeyList(iterable=None, key=identity)
```

```python
add(value)
update(iterable)
clear()
discard(value)
remove(value)
pop(index=-1)
count(value)
index(value, start=None, stop=None)
bisect_left(value)
bisect_right(value)
bisect(value)                 # alias of bisect_right
islice(start=None, stop=None, reverse=False)
irange(minimum=None, maximum=None, inclusive=(True, True), reverse=False)
copy()
```

```python
irange_key(min_key=None, max_key=None, inclusive=(True, True), reverse=False)
bisect_key_left(key)
bisect_key_right(key)
bisect_key(key)               # alias of bisect_key_right
```

```python
SortedSet(iterable=None, key=None)
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
