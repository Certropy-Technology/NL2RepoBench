# Build `frozenlist`

Create an installable Python package named `frozenlist` from an empty workspace.
Reproduce the pinned upstream package's public list-like API on CPython 3.12,
including its optional Cython accelerator and pure-Python fallback. Evaluation is
local and deterministic; do not fetch source code or dependencies during the
evaluation run.

## Project Description

`FrozenList` is a mutable sequence that can be permanently frozen. It starts as
an independent copy of an optional iterable, supports ordinary sequence
operations while unfrozen, and rejects all mutations after `freeze()`. The
package also exposes the pure-Python implementation as `PyFrozenList` and may
replace the default implementation with the compiled `_frozenlist` accelerator.

## Supports

- Provide an installable distribution named `frozenlist` with package version
  `1.8.1.dev0` and Python requirement `>=3.10`.
- Provide `frozenlist/__init__.py`, `frozenlist/__init__.pyi`, and the
  `frozenlist/py.typed` marker. A Cython implementation may be used, but the
  package must remain usable through its pure-Python implementation.
- Expose exactly `FrozenList` and `PyFrozenList` through `frozenlist.__all__`.
- Preserve `FrozenList` as a `collections.abc.MutableSequence`, support the
  generic spelling `FrozenList[int]`, and accept `None`, lists, tuples, and
  other iterables in the constructor without aliasing the input container.
- Preserve indexing, slicing, iteration, reverse iteration, containment,
  equality/order comparisons, `insert`, `append`, `extend`, `+=`, `remove`,
  `clear`, `reverse`, `pop`, `count`, and `index` semantics.
- Expose a boolean `frozen` property. `freeze()` is idempotent and makes every
  mutating operation raise `RuntimeError("Cannot modify frozen list.")` without
  changing the stored items.
- Preserve `repr`, hash behavior, shallow `copy`, deep copy, circular-reference
  handling, and the public aliases across both implementations.
- Honor `FROZENLIST_NO_EXTENSIONS=1` at import time by selecting the pure-Python
  implementation. The package itself must have no network, service,
  filesystem, or subprocess behavior at runtime.

## API Usage Guide

### `frozenlist.FrozenList`

Import path: `from frozenlist import FrozenList`

Signature: `FrozenList(items: Iterable[T] | None = None) -> FrozenList[T]`.
The constructor consumes `items` once and stores a new list. With no argument or
with `None`, the result is empty and unfrozen. `FrozenList[T]` is valid normal
Python generic syntax.

`frozen` is a read-only boolean property. `freeze() -> None` permanently changes
it to `True`; calling it again has no further effect. `__getitem__` supports an
integer index or slice, and the normal `MutableSequence` methods are available.
All mutations, including slice assignment, deletion, `insert`, `append`,
`extend`, in-place addition, `remove`, `clear`, `reverse`, and `pop`, must fail
with `RuntimeError` once frozen.

`__hash__() -> int` raises `RuntimeError` while unfrozen and equals the hash of
the corresponding tuple after freezing. `copy.copy()` makes an independent
container with shared item objects and preserves frozen state. `copy.deepcopy()`
makes recursive copies, preserves aliases and cycles, and preserves frozen
state. `repr()` has the form `<FrozenList(frozen=False, [...])>` or the same
form with `True`.

### `frozenlist.PyFrozenList`

Import path: `from frozenlist import PyFrozenList`

`PyFrozenList` exposes the same constructor, properties, methods, comparison,
copy, and freeze contracts as `FrozenList`. When extensions are disabled it is
the implementation used by `FrozenList`; when extensions are available it
remains the pure-Python class for compatibility testing.

## Implementation Notes

Use a real `MutableSequence` implementation with private frozen state and item
storage rather than a plain list alias. Preserve the exact public names and
generic behavior, make mutation checks happen before changing storage, and
ensure failed mutations leave the sequence unchanged. A standard setuptools
build backend is sufficient; a Cython extension is optional as long as the
fallback and import switch work. Keep package metadata and typing files inside
the distribution.
