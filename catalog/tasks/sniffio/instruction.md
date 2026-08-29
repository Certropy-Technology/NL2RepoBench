# Build `sniffio`

Create a complete, installable Python distribution named `sniffio` from an empty workspace. The package detects which supported asynchronous library is currently executing generic library code. Keep the implementation local and deterministic: it must not download code, inspect a service, or depend on the reference package being preinstalled.

## Project Description

The import package is `sniffio`. It is a small compatibility library for code that supports multiple async runtimes. Its public implementation uses a `ContextVar`, a thread-local override, and runtime inspection for asyncio. The frozen distribution version is `1.3.1+dev` for this source revision. Use a normal PEP 517 build configured by `pyproject.toml`; the evaluator runs CPython 3.12 on Linux and installs the project from the workspace without Git metadata.

The upstream project is dual-licensed under MIT or Apache-2.0. Include a clear package license declaration and a `sniffio/py.typed` marker. Do not add third-party runtime dependencies: `contextvars`, `threading`, and `sys` are standard-library modules.

## Supports

- Python 3.10 and newer, with the evaluator using CPython 3.12.
- `pip install .` and editable-style source layouts are not required, but the ordinary PEP 517 wheel build must work from a source tree with no `.git` directory.
- The root package exports exactly `current_async_library`, `AsyncLibraryNotFoundError`, `current_async_library_cvar`, and `thread_local` through `__all__`, plus `__version__` with value `"1.3.1+dev"`.
- Runtime detection for asyncio tasks and explicit overrides for generic async libraries.
- Deterministic behavior outside an async context: raise `AsyncLibraryNotFoundError` rather than guessing.

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

The verifier invokes candidate code only in an unprivileged child process. Implement the package and build metadata in the workspace; do not copy the upstream source, tests, or a preinstalled implementation at runtime. Avoid adding extra public APIs solely to satisfy undocumented behavior.
