# Project Description

Build an installable pure-Python distribution named `sortedcontainers`, version
`2.4.0`, from an empty workspace. The package provides sorted sequence, set,
and mapping types through the top-level `sortedcontainers` import. Containers
must remain ordered after mutation and must expose the sequence, range, set,
mapping, and live-view behavior described below.

This task uses a bounded **sorted-container scenario contract v1**. The private
verifier starts a fresh unprivileged candidate subprocess for every scenario.
All containers, key functions, and mutations are constructed inside that child;
the trusted verifier never imports candidate code and receives only a JSON
verdict.

# Supports

- CPython 3.12; the frozen environment is CPython 3.12.14 on Debian 12
  `linux/amd64`.
- Distribution and import package name `sortedcontainers`, version `2.4.0`.
- A complete installable project using `setup.py`, `pyproject.toml`, or another
  standards-compliant local Python build configuration.
- No third-party runtime dependencies and no runtime network, service,
  subprocess, database, or native-extension requirement.
- Apache-2.0 package metadata.
- The package root exports `SortedList`, `SortedKeyList`,
  `SortedListWithKey`, `SortedSet`, `SortedDict`, `SortedKeysView`,
  `SortedItemsView`, and `SortedValuesView`. `SortedListWithKey` is an alias
  of `SortedKeyList`. The metadata values are `__title__ ==
  "sortedcontainers"`, `__version__ == "2.4.0"`, and `__license__ ==
  "Apache 2.0"`.

# API Usage Guide

## `SortedList` and `SortedKeyList`

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

## `SortedSet`

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

## `SortedDict` and views

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

# Frozen Scenario Leaves

The fixed denominator is exactly 30 leaves:

```text
api-surface
sorted-list-init-order
sorted-list-mutations
sorted-list-sequence
sorted-list-delete-pop
sorted-list-bisect-count-index
sorted-list-islice
sorted-list-irange
sorted-list-operators-copy
sorted-key-list-init-stability
sorted-key-list-mutations
sorted-key-list-key-range
sorted-key-list-value-queries
sorted-set-init-sequence
sorted-set-mutations
sorted-set-delete-pop
sorted-set-range-bisect
sorted-set-algebra
sorted-set-inplace-operations
sorted-set-key-order
sorted-dict-init-order
sorted-dict-mutations
sorted-dict-pop-peek
sorted-dict-range-bisect
sorted-dict-key-order
sorted-dict-live-views
sorted-dict-view-set-operations
sorted-dict-union
copy-independence
error-contracts
```

The slice adapts deterministic assertions from the frozen upstream collection
for list/set/dict ordering, mutation, range, bisect, operators, keyed ordering,
and views. It deliberately excludes stress loops, timing and memory claims,
pickle internals, private load/index-tree methods, recursive `repr`, CPython
reference counts, Python 2 compatibility, docs, and benchmarks. Those excluded
areas are not hidden requirements.
