# Build `multidict`

## Project Description

Create the `multidict` project from an empty workspace. This is a repository-generation task for the frozen `python` package contract, task specification version `1.0.0`, at source revision `86351873dcc36edb11ba1a27035f2ce2e9ff8f4e`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is python, mapping, duplicate-keys, case-insensitive, proxy, separate-verifier.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `multidict` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `multidict` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `python` on `3.12.14`; target environment metadata declares `debian-12-amd64`.
- Distribution/package: `multidict`; import/root name: `multidict`. Package manager: `pip`.
- Install from the repository root with `python -m pip install . --no-deps`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── multidict/
│   └── __init__.py
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: `MultiDict` and `CIMultiDict`, `MultiDictProxy` and `CIMultiDictProxy`, `istr`, `upstr`, and abstract interfaces, `getversion`, Mapping examples.

For each listed family, the detailed contract below defines the import path or CLI entry, signature, accepted inputs, return type/shape, ordering and determinism, state or I/O side effects, errors, and examples. Implement the complete public surface, including root re-exports and aliases where the specification names them. If an API is stateful, preserve mutation and repeated-call behavior; if it is pure, do not introduce global state.

## Implementation Notes

Keep the implementation self-contained and deterministic under the declared runtime. The candidate repository must install from the workspace root, import through the documented public path, and run without external services. Preserve package metadata, module semantics (ESM/CommonJS or Python import behavior), serialization formats, resource cleanup, and boundary behavior described below. publicly unavailable evaluator adapters and non-public evaluation details are not part of the implementation.

## Examples

Ordinary project examples:

```bash
cd workspace
python -m pip install . --no-deps
```

```python
# Import the public package and use the task-specific APIs documented below.
from multidict import *
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

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

### Mapping examples

```python
from multidict import MultiDict

headers = MultiDict([("Accept", "text/plain"), ("Accept", "text/html")])
assert headers["Accept"] == "text/plain"
assert headers.getall("Accept") == ["text/plain", "text/html"]
headers.add("Accept", "application/json")
```

```python
from multidict import CIMultiDict, CIMultiDictProxy

source = CIMultiDict([("Content-Type", "text/plain")])
proxy = CIMultiDictProxy(source)
source["content-type"] = "application/json"
assert proxy["CONTENT-TYPE"] == "application/json"
```

Constructing from malformed pairs or non-string keys raises the documented
`TypeError`; looking up a missing key without a default raises `KeyError`.
Calling `popitem()` on an empty mapping also raises `KeyError`. A proxy remains
read-only, but it must reflect later source mutations and report the same
mutation version through `getversion`.
