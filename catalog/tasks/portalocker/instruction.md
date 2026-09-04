# Project Description

Build an installable Python package named `portalocker` from an empty workspace.
It provides advisory file locks and small coordination utilities for Linux/POSIX.
Implement the public behavior described here for CPython 3.12 on Linux. The
package must not require a runtime third-party dependency.

# Supports

- Python 3.12 on Linux/POSIX.
- A PEP 517 `pyproject.toml` package named `portalocker`, version `4.3.0`.
- No runtime network, Redis server, database, TTY, or external service.
- The `redis` extra and Windows-only `msvcrt`/`pywin32` behavior are outside this
  task. POSIX locking must use the platform's advisory file-lock facilities.
- The package must install with the standard build frontend and be importable
  from its installed target under `python -I`.

# API Usage Guide

## Package exports and flags

The `portalocker` package exports `Lock`, `RLock`, `TemporaryFileLock`,
`PidFileLock`, `BoundedSemaphore`, `NamedBoundedSemaphore`, `open_atomic`,
`lock`, `unlock`, `LockFlags`, `LOCK_EX`, `LOCK_SH`, `LOCK_NB`, `LOCK_UN`,
`AlreadyLocked`, `LockException`, and `LockLostError`. `__version__` and the
installed distribution version are `4.3.0`. `LockFlags` is an `IntFlag` with
`EXCLUSIVE`, `SHARED`, `NON_BLOCKING`, and `UNBLOCK`; combine flags with `|`.
`lock(file, flags)` acquires a POSIX advisory lock and `unlock(file)` releases
it. Passing contradictory flags or no lock type to `lock` raises `RuntimeError`.

## `Lock`

`portalocker.Lock(filename, mode='a', timeout=None, check_interval=0.25,
fail_when_locked=False, flags=LockFlags.EXCLUSIVE | LockFlags.NON_BLOCKING,
*, raise_on_release_error=False, **file_open_kwargs)` is a context manager and
file-like lock owner. It opens `filename` with the requested built-in `open`
mode, acquires the lock, yields the open handle, and releases/ closes it on
exit. `timeout=None` means use the normal blocking behavior; a finite timeout
retries contention at `check_interval`. With `fail_when_locked=True`, initial
contention raises `AlreadyLocked` immediately. The lock file remains on disk
after release because it is an ordinary file.

## `RLock`

`portalocker.RLock(filename, mode='a', timeout=None, check_interval=0.25,
fail_when_locked=False, flags=LockFlags.EXCLUSIVE | LockFlags.NON_BLOCKING)`
allows the same instance and thread to acquire a lock repeatedly. Each
successful `acquire()` increments an internal count; matching `release()` calls
decrement it and only the final release unlocks/closes the file. Releasing more
times than acquired raises `LockException`.

## Temporary and PID locks

`TemporaryFileLock(filename='.lock', timeout=None, check_interval=0.25,
fail_when_locked=True, flags=...)` is a lock whose file is removed when the
lock is released. It yields its file handle in a `with` block. `PidFileLock`
has the same lifecycle with default filename `.pid`; while held it writes the
decimal current process ID, `read_pid()` returns that integer (or `None` when
there is no readable PID), and release removes the file.

## Semaphores

`BoundedSemaphore(maximum, name='bounded_semaphore',
filename_pattern='{name}.{number:02d}.lock', directory=..., timeout=5,
check_interval=0.25, fail_when_locked=True)` represents `maximum` slots as
separate lock files. `get_filenames()` returns the deterministic slot paths;
`get_random_filenames()` returns the same paths in a randomized order;
`get_filename(number)` formats one slot. `acquire()` obtains one slot and
returns a `Lock` when a slot is acquired. With the default
`fail_when_locked=True`, an exhausted semaphore raises `AlreadyLocked`; with
`fail_when_locked=False`, it returns `None`. `release()` releases its acquired
slot.
`NamedBoundedSemaphore` derives its name from the supplied name when one is
not explicitly provided. This revision does not reject a non-positive maximum
during construction, but such a semaphore has no usable slots.

## `open_atomic`

`portalocker.open_atomic(filename, binary=True)` is a context manager yielding
a writable temporary handle. On normal exit it publishes the complete payload
at `filename` atomically and refuses to replace an existing destination with
`FileExistsError`. The temporary file is created beside the destination and
removed after successful publication; on a failed publication the payload may
be preserved for diagnosis. With `binary=False`, it yields a text handle.

# Implementation Notes

Keep the public module layout (`portalocker.constants`, `exceptions`,
`portalocker`, `types`, and `utils`) and re-export the documented names from
`portalocker.__init__`. Preserve deterministic exception classes and cleanup.
Use a separate subprocess boundary for file-lock contention tests: an
unprivileged candidate child receives JSON requests and returns JSON values;
the trusted verifier must never import candidate code into its own process.
Use bounded temporary paths and clean up every lock, child process, and file.
Do not implement Redis or Windows-only APIs by contacting a service.
