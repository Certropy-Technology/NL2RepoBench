# Project Description

Create a Python package named `pandarallel` that adds convenient parallel
operations to pandas objects. A user should be able to initialize the package
once and then call parallel counterparts of common pandas operations while
receiving results with the same values, labels, ordering, and exception
semantics as the corresponding sequential operation.

The project is a repository-generation task: start from an empty workspace and
provide the complete installable package, not a patch for an existing checkout.

## Supports

- Support Python 3.7 or newer and the pandas ecosystem.
- Include a conventional `setup.py` entry point and package metadata so that
  `pip install -e .` works from the repository root. Runtime dependencies must
  include pandas, `dill` (at least 0.3.1), and `psutil`; test/development
  dependencies may include NumPy and pytest.
- Provide the `pandarallel/` package, its data-type adapters, progress-bar
  support, and a package version. Do not require a network service or a
  project-local copy of the verifier's tests at runtime.
- Keep the implementation usable on POSIX systems and Windows. Select a
  multiprocessing context appropriate for the platform and make user-defined
  callables, including lambdas and closures, transferable to workers.

## API Usage Guide

### Package entry point and initialization

Expose the class `pandarallel` and `__version__` from the package root so the
following import works:

```python
from pandarallel import pandarallel
```

Implement:

```python
pandarallel.initialize(
    shm_size_mb=None,
    nb_workers=NB_PHYSICAL_CORES,
    progress_bar=False,
    verbose=2,
    use_memory_fs=None,
) -> None
```

Initialization must install the parallel methods described below on the
corresponding pandas classes. `nb_workers` controls the requested worker
process count. When it is omitted, use the number of available physical CPU
cores (or a safe positive fallback when that information is unavailable).
`verbose` controls informational messages; `progress_bar` controls progress
output without changing the computed result.

Data transfer strategy is selected by `use_memory_fs`:

- `None` automatically uses the configured memory filesystem when it exists,
  and otherwise uses ordinary multiprocessing pipes.
- `True` requires the memory filesystem and raises `SystemError` when it is
  unavailable.
- `False` always uses pipe-based transfer.

The memory-filesystem root defaults to `/dev/shm` and may be overridden by the
`MEMORY_FS_ROOT` environment variable. Initialization must not require a
Jupyter environment; when a notebook environment is present, a notebook-style
progress display may be used.

### DataFrame operations

After initialization, add these methods to `pandas.DataFrame`:

- `parallel_apply(func, *args, **kwargs)` — parallel equivalent of
  `DataFrame.apply`, including `axis=0`/`axis=1`, positional arguments, and
  keyword arguments. Preserve pandas-compatible indexes, columns, result
  shapes, and ordering. Reject an invalid axis with `ValueError`.
- `parallel_applymap(func, **kwargs)` — parallel element-wise equivalent of
  `DataFrame.applymap` (or the compatible pandas element-wise API). Preserve
  the frame's shape, labels, and values, including empty frames.

The methods must support both named functions and anonymous/lambda callables.

### Series operations

After initialization, add these methods to `pandas.Series`:

- `parallel_apply(func, *args, **kwargs)` — equivalent in observable behavior
  to `Series.apply`.
- `parallel_map(arg, na_action=None)` (and compatible positional/keyword
  arguments accepted by the pandas `map` operation) — equivalent to
  `Series.map`.

Preserve the original index and order, pass function arguments correctly, and
handle empty Series without creating an invalid worker partition.

### GroupBy operations

Add `parallel_apply` to pandas DataFrame group-by objects. It must support
single-column and multi-column grouping and return the same kind of result,
index structure, and group ordering as the corresponding `GroupBy.apply` call.
Functions that return scalars, Series, or DataFrames must be handled without
silently dropping group results.

### Rolling and expanding operations

Add `parallel_apply` to:

- `Series.rolling(...)` objects;
- grouped rolling objects such as `DataFrame.groupby(...).column.rolling(...)`;
- grouped expanding objects such as `DataFrame.groupby(...).column.expanding(...)`.

Window parameters, `raw`, function arguments, missing values, MultiIndex
labels, and the alignment of the sequential pandas result must be preserved.
Small and empty inputs should remain well-defined rather than producing a
zero-worker failure.

### Progress reporting and errors

When `progress_bar=True`, provide a useful terminal progress display and a
notebook-compatible display when running inside a supported notebook shell.
When it is false, computations must remain usable in non-interactive logs.
Worker failures and exceptions raised by a user function must be propagated to
the caller rather than being converted into a successful or partial result.
Temporary files, pools, managers, and queues must be cleaned up on both success
and failure.

## Implementation Notes

- Parallel methods should be behaviorally comparable with their sequential
  pandas counterparts; concatenate or otherwise reduce worker results in the
  original logical order.
- Use a bounded number of worker processes and avoid assuming that `/dev/shm`
  exists. Memory-filesystem transfers and pipe transfers are both supported
  modes, not two different result contracts.
- Serialize user callables and their arguments in a way that supports the
  named and anonymous functions used by normal Python callers.
- Keep public imports stable from `pandarallel`, and keep platform-specific
  multiprocessing choices explicit.
- The repository may contain documentation and examples, but implementation
  behavior must not depend on hidden tests, test-only fixtures, or network
  access.
