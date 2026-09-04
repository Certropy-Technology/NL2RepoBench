# Build `multidict`

Create an installable pure-Python package named `multidict` from an empty workspace. Reproduce the pinned upstream package's public mapping behavior on CPython 3.12 without fetching source code or dependencies during evaluation.

## Project Description

`multidict` provides mappings that can retain multiple values for one key. It includes case-sensitive and case-insensitive mutable mappings, read-only live proxies, specialized views, and an `istr` string subtype for case-insensitive keys. A pure-Python implementation is sufficient; a C accelerator is optional.

## Supports

- Provide an installable distribution named `multidict`, version `6.7.2.dev0`, requiring Python 3.10 or newer.
- Export exactly `CIMultiDict`, `CIMultiDictProxy`, `MultiDict`, `MultiDictProxy`, `MultiMapping`, `MutableMultiMapping`, `getversion`, `istr`, and `upstr` in `multidict.__all__`.
- Include a `multidict/py.typed` marker and expose the documented classes from the package root.
- Preserve insertion order and duplicate values for `MultiDict`; `CIMultiDict` compares keys case-insensitively while retaining the spelling of stored keys.

## API Usage Guide

### `MultiDict` and `CIMultiDict`

Import with `from multidict import MultiDict, CIMultiDict`. Construct with `MultiDict(iterable=None, **kwargs)` where the iterable is a mapping or an iterable of two-item `(key, value)` pairs. Keys must be strings. Duplicate pairs are retained in order. `CIMultiDict` uses case-folded key identity while preserving the spelling from each stored pair.

`len()` counts stored pairs. `items()`, `keys()`, and `values()` return live specialized views; iteration follows pair insertion order. `obj[key]` and `getone(key)` return the first value, while `getall(key)` returns all values in order. `get()` and the `getone`/`getall` default arguments return the supplied default for a missing key. Missing keys without defaults raise `KeyError`; invalid key types raise `TypeError`.

`add(key, value)` appends one pair. Assignment replaces all existing values for a key with one pair. `extend()` appends all supplied pairs. `update()` replaces each key using the values in the update input, and `merge()` adds only keys that do not already exist. `setdefault()` returns an existing first value or adds the default. `del`, `popone`, and `popall` remove one or all values as specified; `popitem()` removes the last stored pair and raises `KeyError` when empty. `clear()` removes all pairs. Mutating methods return `None`.

### `MultiDictProxy` and `CIMultiDictProxy`

Construct a proxy only from the matching mutable mapping type. A proxy is read-only but live: later changes to its source are visible. It supports mapping reads, `getone`, `getall`, views, containment, equality, and `copy()`. `copy()` returns a mutable `MultiDict` or `CIMultiDict` of the matching kind. Attempts to mutate a proxy are unavailable or fail.

### `istr`, `upstr`, and abstract interfaces

`istr(value)` is a string subtype whose equality and hash use case-insensitive identity while its string and repr forms preserve the original text. `upstr` is the same public class. `MultiMapping` and `MutableMultiMapping` are the abstract mapping interfaces, and concrete mappings satisfy the corresponding ABC relationships. Generic aliases such as `MultiDict[int]` are valid at runtime.

### `getversion`

`getversion(mapping_or_proxy) -> int` returns an integer mutation version. A mutation increases the version; a proxy reports its source's version. Passing another object raises `TypeError`.

## Implementation Notes

Keep candidate code self-contained and deterministic. Preserve duplicate-pair ordering, first-value lookup, case-insensitive identity, live proxy behavior, and mutation errors. Do not rely on network services, filesystem state outside the package, process-global randomness, or external processes. The verifier calls the public API through a child-process JSON adapter, so return values and errors must be ordinary JSON-observable Python behavior.
