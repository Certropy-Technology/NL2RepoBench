# Project Description

The task id is `joblib`; build its public Python package from an empty workspace.

# Natural Language Instruction

Build joblib from an empty workspace as an installable Python distribution.
Implement the public parallel, persistence, hashing, compression, memory-cache,
disk, and utility contracts described below. Preserve deterministic ordering and
normal Python exceptions while keeping the implementation local and offline.

# Supports or Environment Configuration

Use Python 3.12 on Linux with the frozen local dependency closure and no network.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── joblib/
    ├── __init__.py
    ├── parallel.py
    ├── memory.py
    ├── numpy_pickle.py
    ├── hashing.py
    ├── compressor.py
    ├── disk.py
    └── testing.py
```

# API Usage Guide

The public API guide below is the contract for `joblib`.

# Build `joblib`

Create a complete, installable Python project named `joblib` from an empty
workspace. The project provides local utilities for parallel function calls,
deterministic disk caching, object persistence, hashing, compression, and
bounded filesystem helpers. Do not depend on a preinstalled copy of joblib or
on network access at runtime.

## Legacy Project Description

Implement the public package `joblib` for CPython 3.12. It must be usable as a
normal installed package and must keep candidate code separate from verifier
code. The scored contract is local and deterministic: no Dask cluster,
network service, interactive shell, or external command is required. Process
parallelism may be implemented, but the required scenarios must work with
sequential and thread backends as well.

The package should expose the usual top-level joblib names: `Memory`,
`MemorizedResult`, `expires_after`, `Parallel`, `delayed`, `cpu_count`,
`effective_n_jobs`, `parallel_config`, `parallel_backend`,
`register_parallel_backend`, `register_store_backend`, `register_compressor`,
`ParallelBackendBase`, `StoreBackendBase`, `wrap_non_picklable_objects`,
`dump`, `load`, `hash`, `Logger`, and `PrintTime`. Set a PEP 440-compatible
`__version__` string and make the package importable without NumPy.

## Supports

- Support Python 3.12 on a Debian-based amd64 environment.
- Use the standard library plus the declared runtime dependencies
  `cloudpickle`, `numpy`, and optional `lz4`. Build tooling may use pinned
  `setuptools` and `wheel`.
- Provide a normal setuptools project with package metadata and an installable
  `joblib/` package. Include the vendored process-management modules needed by
  the public parallel API; do not replace them with an unrelated third-party
  library.
- Runtime operations in this task are local and deterministic. Do not clone,
  download, contact a service, or rely on current time, random state, or a
  development checkout to implement the contract.

## API Usage Guide

### Parallel execution

`joblib.delayed(function)` returns a callable that records its positional and
keyword arguments. `joblib.Parallel(n_jobs=1, backend=None, verbose=0,
return_as="list", **config)` consumes an iterable of delayed calls and returns
their results in input order. `return_as="generator"` returns a generator
that yields results in input order. Exceptions raised by a task propagate to
the caller. An unknown backend name raises `ValueError`.

The `threading` and `sequential` backends are required. `parallel_backend(name,
n_jobs=None, **backend_params)` and `parallel_config(backend=None,
n_jobs=None, prefer=None, require=None, verbose=0, **backend_params)` are
nestable context managers that set defaults for code using `Parallel` without
explicit settings. Invalid `prefer` or `require` values raise `ValueError`.
`effective_n_jobs(n_jobs)` returns a positive effective worker count and
`cpu_count()` returns a positive integer. `register_parallel_backend(name,
factory, make_default=False)` validates and registers a backend factory.

### Persistence

`joblib.dump(value, filename, compress=0, protocol=None)` serializes an object
to a path or binary file object and returns a list containing the written path
for a path input, or `None` for a file object. Compression accepts zlib/gzip,
bz2, lzma/xz, and the optional lz4 backend where available. `joblib.load`
reconstructs the value from a path or file object. The functions preserve
ordinary Python containers and NumPy arrays. `load(path, mmap_mode="r")`
returns a NumPy memmap for an uncompressed persisted NumPy array; compressed
arrays are loaded as normal arrays and issue a warning when mmap is requested.
Invalid compression configuration raises a clear exception.

### Hashing

`joblib.hash(obj, hash_name="md5", coerce_mmap=False)` returns a deterministic
hex digest for pickleable objects. Equivalent dictionaries and sets hash
independently of insertion/iteration order. NumPy arrays are supported when
NumPy is installed. An unsupported hash algorithm raises `ValueError`.

### Disk cache

`Memory(location, backend="local", mmap_mode=None, compress=False,
verbose=1, bytes_limit=None, backend_options=None)` creates a cache rooted at
`location`, which may be a string or `pathlib.Path`. `memory.cache(function,
ignore=None, cache_validation_callback=None)` returns a callable wrapper.
The first call computes and stores the result; an equivalent later call loads
the cached value without recomputing it. Positional and keyword forms that
represent the same call share a cache entry. `ignore` excludes named arguments
from the cache key. `check_call_in_cache` reports whether an entry exists and
`clear(warn=False)` removes cached results. A failed computation is not cached
and is recomputed on the next call. `Memory.location` reflects the configured
path.

### Utilities and extension points

`joblib.disk.memstr_to_bytes(text)` accepts values such as `"1K"`, `"2M"`,
`"3G"`, and fractional values, returning an integer byte count; malformed
values raise `ValueError`. `wrap_non_picklable_objects(obj)` wraps a callable
so locally defined closures can participate in serialization. `register_compressor`
rejects invalid names or non-compressor objects with `ValueError`.

`joblib.testing.check_subprocess_call(cmd, timeout=5, stdout_regex=None,
stderr_regex=None)` runs a supplied local command for test utilities, checks
its exit status and optional regexes, and raises `ValueError` for a failed
check. This helper is not needed by normal application code.

## Implementation Notes

- Preserve the public import paths and top-level re-exports. Avoid importing
  NumPy eagerly from modules that should work without it.
- Cache keys must include function identity and normalized arguments. Cache
  writes should be atomic enough that a partially written result is not
  treated as a valid cache hit.
- Keep `Memory` and persistence behavior deterministic for fixed inputs and
  temporary directories. Do not share mutable defaults between calls.
- The verifier exercises behavior through a child process and a JSON protocol;
  it will not import candidate modules in the verifier process.

# Examples

```python
from joblib import Parallel, delayed
assert Parallel(n_jobs=2)(delayed(lambda x: x * 2)(x) for x in [1, 2]) == [2, 4]
```

```python
from joblib import Memory, dump, load
from pathlib import Path
path = Path("value.joblib")
dump({"answer": 42}, path)
assert load(path)["answer"] == 42
```

# Error Handling and Boundary Conditions

- Invalid backend, compressor, hash, cache, and persistence inputs raise the
  documented Python exception instead of silently changing behavior.
- Array order, object hashing, compression round trips, and cache keys are
  deterministic for fixed inputs.
- Dask, platform-specific branches, external services, timing benchmarks, and
  network access are outside this task.

The task id and import/distribution package are `joblib`. The API inventory
freezes 33 deterministic local scenarios across parallel, persistence,
hashing, memory, and utility behavior.
- The hidden contract intentionally excludes Dask integration, distributed
  services, benchmark timing thresholds, platform-specific Windows behavior,
  and private implementation helpers. Correctness on the documented local
  API matters more than reproducing an undocumented internal layout.
