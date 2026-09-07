# Project Description

The import package is `sniffio`. It is a small compatibility library for code that supports multiple async runtimes. Its public implementation uses a `ContextVar`, a thread-local override, and runtime inspection for asyncio. The frozen distribution version is `1.3.1+dev` for this source revision. Use a normal PEP 517 build configured by `pyproject.toml`; the evaluator runs CPython 3.12 on Linux and installs the project from the workspace without Git metadata.

The upstream project is dual-licensed under MIT or Apache-2.0. Include a clear package license declaration and a `sniffio/py.typed` marker. Do not add third-party runtime dependencies: `contextvars`, `threading`, and `sys` are standard-library modules.

## Natural Language Instruction

Create `sniffio` from an empty workspace as a complete installable python project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `sniffio`. Primary import or package entry: `sniffio`.
- CPython 3.12.11 on debian-12-amd64 with pip.
- Install from `workspace/` using `python -m pip install .`.
- Declared dependency closure: packaging==26.3, setuptools==80.9.0, setuptools-scm==8.3.1. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `pytest`. A fixed collection
  contains `21` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── sniffio/
│   ├── __init__.py
│   ├── _impl.py
│   ├── _version.py
│   └── py.typed
└── README.md
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### `sniffio.current_async_library() -> str`

Import path: `from sniffio import current_async_library`. It takes no arguments and returns one of the runtime labels currently known by the implementation: `"asyncio"`, `"curio"`, or an explicitly supplied context/thread-local label. The function first honors `sniffio.thread_local.name`, then `sniffio.current_async_library_cvar`, then detects an active asyncio task, then probes Curio only when Curio is already imported. It must not import or start an async runtime merely to answer the query. If no recognized runtime is active, raise `AsyncLibraryNotFoundError` with a useful message.

Calling it twice in the same active asyncio task must return the same string. Calling it after leaving the task must again raise `AsyncLibraryNotFoundError` unless an override remains set. A value stored in the ContextVar is scoped to the current context and is reset with the token returned by `set()`.

### `sniffio.current_async_library_cvar`

Import path: `from sniffio import current_async_library_cvar`. This is a `contextvars.ContextVar` whose default is `None`. Setting a non-`None` string makes `current_async_library()` return that string in the current context. It must not leak into a copied or independently executed context after reset.

### `sniffio.thread_local`

Import path: `from sniffio import thread_local`. This is a `threading.local` instance whose `name` attribute defaults to `None`. Setting `thread_local.name` to a string makes it the highest-priority result of `current_async_library()` in that thread. A fresh worker thread has its own default `None` and does not inherit the caller's thread-local value.

### `sniffio.AsyncLibraryNotFoundError`

Import path: `from sniffio import AsyncLibraryNotFoundError`. It is a subclass of `RuntimeError` used when the active library is unknown or no async library is running. Do not replace it with a generic exception.

### Compatibility modules and package metadata

The modules `sniffio._impl` and `sniffio._version` remain importable. The distribution metadata must report name `sniffio` and version `1.3.1+dev`; the package must include `sniffio/py.typed`. Preserve the public root names and their importability.

## Implementation Notes

Keep the two override mechanisms distinct: thread-local state has priority over ContextVar state, and both have priority over runtime sniffing. Do not cache a runtime result globally, because asyncio task detection and context state are dynamic. Detect asyncio through its current-task API and handle the no-running-loop case by continuing to the next probe. Curio support is conditional and must not become a mandatory dependency.

Implement the package and build metadata in the workspace; do not copy the upstream source, tests, or a preinstalled implementation at runtime. Avoid adding extra public APIs solely to satisfy undocumented behavior.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```python
import sniffio
print(sniffio)
```

```python
import sniffio
# Invoke a documented API using an empty or boundary input.
```

```python
import sniffio
print(sniffio)
```

```python
import sniffio
# Invoke a documented API using an empty or boundary input.
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.

An override must be scoped to the current execution context and restored after use.
Unknown async-library names follow the documented exception contract rather than guessing a runtime.
Package metadata and the `py.typed` marker are part of the installable public project.
