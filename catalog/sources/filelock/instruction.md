# Project Description

Build the pinned `filelock` Python project from an empty `workspace/`. Implement
the synchronous, asynchronous, reader/writer, strict-claim, and lease APIs in
the existing task-specific contract.

# Natural Language Instruction

Create an installable `filelock` package. Preserve lock acquisition/release,
timeouts, reentrancy, platform selection, marker records, ownership claims,
and cleanup exactly as documented below.

# Supports or Environment Configuration

- Use CPython 3.12 with the exact package/build closure in `task.toml`.
- Behavior is local filesystem coordination; do not use services or network.
- Agent, candidate, verifier, Oracle, and controls run with no network access.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── filelock/
    ├── __init__.py
    ├── _api.py
    ├── _windows.py
    ├── _unix.py
    ├── asyncio.py
    └── py.typed
```

# API Usage Guide

The detailed API inventory and guide below are authoritative for all classes,
methods, signatures, state, and exceptions.

# Implementation Notes

Lock state must be deterministic and safely released on errors. Respect caller
paths and platform capabilities without hidden global coordination.

# Examples

```python
from filelock import FileLock
with FileLock('/tmp/example.lock'):
    pass
```

```python
lock = FileLock('/tmp/example.lock', timeout=1)
lock.acquire(); lock.release()
```

# Error Handling and Boundary Conditions

```python
FileLock('/tmp/example.lock', timeout=0).acquire()
```

```python
lock.release()  # preserve documented release behavior
```

# Build `filelock`

Create a complete, installable Python project named `filelock` from an empty
workspace. The project is a platform-independent file-locking library. It must
provide the synchronous, asynchronous, reader/writer, strict-claim, and
lease-based APIs described below, with behavior compatible with the frozen
`filelock` 3.32.3 source contract. The implementation must be self-contained:
do not depend on a preinstalled copy of `filelock`, on the upstream checkout,
or on network access at runtime.

## Project Description

`filelock` coordinates cooperating threads and processes that use a shared
filesystem path. It exposes native OS locks where the platform provides them,
cooperative marker locks where it does not, and higher-level reader/writer and
lease protocols for workloads that need shared reads, a single writer, stale
claim recovery, or fail-closed ownership. It is an advisory coordination
library: callers still need an atomic publication strategy for the protected
resource, and a lock does not stop code that ignores the lock.

The distribution and import package are both named `filelock`. The package
version is `3.32.3`, exposed as `filelock.__version__`. Preserve the root
package/module names, exception classes, aliases, protocol records, context
manager behavior, and Python data-model behavior described here.

## Supports

- Support CPython 3.10 and newer Python 3.x versions in the source's supported
  range. On Python 3.10, grouped cleanup errors may use the `exceptiongroup`
  backport lazily; on Python 3.11 and newer use the built-in exception-group
  types. Do not require third-party runtime packages on the ordinary path.
- Provide an installable `src/filelock/` package, a `py.typed` marker, project
  metadata for distribution `filelock`, and version metadata that resolves to
  `3.32.3` without requiring a Git checkout at runtime.
- Declare no third-party runtime dependency. PEP 517 build tools and test
  tools are development/build dependencies, not imports required by normal
  lock use. `sqlite3`, `fcntl`, and Windows APIs are platform capabilities,
  not PyPI runtime dependencies.
- Keep normal operations local and deterministic: no network, service account, or
  external service is required merely to construct or use a lock. Configured
  expiry and polling intentionally use local clocks; filesystem, process,
  thread, and event-loop effects are intentional parts of the contract.
- Preserve the public root exports below and keep the corresponding documented
  submodules importable. Do not replace the library with a single in-memory
  mutex; separate processes and separate Python interpreters must coordinate
  through the filesystem or native OS primitive.

## Root API Inventory

`filelock.__all__` contains these names and they must be importable from the
root package:

```text
AcquireReturnProxy
AsyncAcquireReadWriteReturnProxy
AsyncAcquireReturnProxy
AsyncAcquireSoftReadWriteReturnProxy
AsyncFileLock
AsyncReadWriteLock
AsyncSoftFileLease
AsyncSoftFileLock
AsyncSoftReadWriteLock
AsyncStrictSoftFileLock
AsyncUnixFileLock
AsyncWindowsFileLock
BaseAsyncFileLock
BaseFileLock
CloseErrorPolicy
ContextErrorPolicy
FileLock
LeaseCompromise
LeaseSettingsMismatch
LockOptions
MarkerSoftFileLock
OwnerRecord
ReadWriteLock
SoftFileLease
SoftFileLock
SoftFileLockLifetimeWarning
SoftFileLockProtocolError
SoftReadWriteLock
StrictSoftFileClaim
StrictSoftFileClaimState
StrictSoftFileLock
Timeout
UnixFileLock
WindowsFileLock
__version__
lock_descriptor
unlock_descriptor
```

`filelock.has_fcntl` is also available as the capability flag used by the
platform selection. The compatibility modules used by the package's public
behavior must remain importable, including `filelock.asyncio`,
`filelock._api`, `filelock._descriptor`, `filelock._error`,
`filelock._identity`, `filelock._lease`, `filelock._marker`,
`filelock._read_write`, `filelock._soft`, `filelock._soft_rw`,
`filelock._strict`, and `filelock._util`.

## Synchronous Base Lock API

The common constructor is:

```python
BaseFileLock(
    lock_file, timeout=-1, mode=-1, thread_local=True, *,
    blocking=True, is_singleton=False, poll_interval=0.05,
    lifetime=None, context_error_policy="chain",
    close_error_policy="default", fallback_to_soft=True,
    preserve_lock_file=False, on_acquired=None,
)
```

The concrete classes accept the same options unless a section below says
otherwise. `lock_file` accepts `str` and `os.PathLike` and is stored as a
string. `timeout < 0` waits without a deadline, `timeout == 0` makes one
attempt, and a positive timeout measures elapsed monotonic time. `blocking`
overrides the timeout and makes a contended acquisition return immediately.
`poll_interval` is the positive finite delay between attempts. The deprecated
keyword `poll_intervall` remains accepted by `acquire()` and emits a
`DeprecationWarning` while taking precedence over `poll_interval`.

The lock exposes these properties, with setters where shown:

```python
lock_file                # str
is_thread_local()        # bool
is_singleton             # bool
context_error_policy     # "chain" or "group"
close_error_policy       # "default", "raise", or "suppress"
fallback_to_soft         # bool
preserve_lock_file       # bool
on_acquired              # callable or None
timeout                  # float; writable
blocking                 # bool; writable
poll_interval            # float; writable
lifetime                 # float or None; writable
mode                     # effective permission mode
has_explicit_mode        # bool
is_locked                # bool
lock_counter             # nested-acquisition depth
```

A newly constructed lock is not held. A missing parent
directory is created when an acquisition needs it. When `mode` is omitted,
open the new marker with `0o666` so the process umask/default ACL determines the
result; an explicit mode is applied to a newly created lock file. Invalid
negative/non-finite lifetime and non-positive/non-finite polling values raise
clear `ValueError`/`TypeError` exceptions.

`acquire()` has this contract:

```python
lock.acquire(
    timeout=None, poll_interval=None, *,
    poll_intervall=None, blocking=None, cancel_check=None,
) -> AcquireReturnProxy
```

`None` uses the corresponding instance default. On success it increments the
reentrant counter and returns a proxy, not the lock itself. The proxy's
`__enter__` returns the lock and its `__exit__` releases one level. The lock
itself is a `ContextDecorator`, so both `with lock:` and decorating a function
are supported. `release(force=False)` decrements one nested level and releases
the physical lock at zero; `force=True` releases all levels. Releasing an
unheld lock is a no-op for the ordinary base lock. A dropped lock makes a
best-effort forced release without raising from its finalizer.

Two distinct lock objects in the same thread that block forever on the same
canonical path must fail fast with `RuntimeError` rather than self-deadlock.
Finite-timeout and non-blocking attempts use the ordinary `Timeout` path.
Equivalent relative/absolute spellings share the deadlock identity while a
final symlink is not silently followed as the lock target. `is_singleton=True`
returns one weakly cached instance per concrete class and canonical path; a
singleton constructed later with different timeout/blocking settings raises a
configuration error instead of silently changing the existing instance.

`context_error_policy="chain"` preserves the normal exception context when a
body and release both fail. `"group"` raises an exception group containing the
body failure and release failure without hiding either. `close_error_policy`
controls only a post-unlock `os.close` failure according to the documented
`default`, `raise`, and `suppress` choices; an unlock failure keeps the lock
held so callers can retry.

For native backends, `on_acquired(fd)` runs once per physical acquisition after
the OS lock is held and initialization is complete. The callback receives the
borrowed descriptor, must not close/unlock it, and may raise; a raised callback
must roll the acquisition back and preserve both callback and rollback errors
when both fail. Recursive acquisitions do not invoke it again. Existence-based
backends reject `on_acquired` and `preserve_lock_file=True`; native backends
honor the latter according to their platform cleanup rules.

## Concrete Backends and Platform Selection

`FileLock` is the platform-aware alias. On Windows it is
`WindowsFileLock`; on a Unix-like runtime with usable `fcntl.flock` it is
`UnixFileLock`; when `fcntl` is unavailable it is `SoftFileLock` and emits a
warning. Explicit `UnixFileLock`, `WindowsFileLock`, and `SoftFileLock` remain
constructible even when the current platform cannot execute their native
primitive; unsupported operations fail clearly rather than silently pretending
that a kernel lock exists.

### `UnixFileLock` and `WindowsFileLock`

On Unix, use an open lock-file descriptor and exclusive non-blocking
`fcntl.flock`; retain the pathname after release so contenders do not split
across different inodes. If the filesystem reports `ENOSYS`,
`fallback_to_soft=True` may switch to `SoftFileLock`; with it false, propagate
the native error. Do not truncate or chmod a file until the native lock has
been won. Refuse a final symlink when the platform exposes `O_NOFOLLOW`.

On Windows, use a one-byte exclusive `LockFileEx` range at offset zero and
open the actual handle without following a final reparse point. Treat sharing
violation/delete-pending states as retryable contention, but surface permanent
access failures. Release unlocks before closing and normally attempts to delete
the lock file; `preserve_lock_file=True` keeps the pathname. A lock file may
remain after release when another Windows thread still has an open handle, and
that persistence must not be mistaken for held state.

### `SoftFileLock`

`SoftFileLock` uses exclusive creation (`O_CREAT|O_EXCL`) of a marker path.
The marker contains the holder PID, hostname, and, where available, a process
start token. A contender may reclaim a malformed marker after its short grace
period or a marker whose exact same-host owner is provably dead. A foreign
hostname, a live matching PID, an unreadable owner token, or an ambiguous
filesystem error is treated as held (fail closed). `pid`,
`is_lock_held_by_us`, and `break_lock()` expose marker inspection and explicit
operator override. `break_lock()` voids mutual exclusion and must not be used
as ordinary release logic.

The legacy `lifetime` option permits age-based marker expiry even while a
holder is alive; it can overlap protected work and therefore does not promise
strict mutual exclusion. Native locks warn and ignore this option. Do not
share a mutable marker protocol with a native lock at the same path unless the
caller accepts the documented interoperability limits.

### Marker records and strict claims

`MarkerSoftFileLock` publishes protocol-2 `OwnerRecord` values. Keep these
module-level helpers compatible:

```python
OwnerRecord(pid, hostname, mode, token=None, lease_duration=None, start=None)
encode_marker(record: OwnerRecord) -> bytes
parse_marker(content: str | None) -> OwnerRecord | None
```

Unknown future owner modes must not be aged out as malformed live records.

`StrictSoftFileLock` is a fail-closed cooperative backend. It uses the
permanent `<lock>.filelock` coordination directory and a `claims` directory;
each contender publishes a private record, an `intent` claim, and then a
`held` claim through atomic no-replace hard links. The lowest stable claim wins,
all contenders rescan the doorway before entering, and release removes only
that owner's claim paths. Its `claims` property returns immutable
`StrictSoftFileClaim` records, sorted by claim name:

```python
StrictSoftFileClaim(name, state, token, pid, hostname, start=None)
# state is "intent" or "held"
```

Malformed, unreadable, unknown-version, symlinked, or otherwise ambiguous
strict state raises `SoftFileLockProtocolError` and blocks rather than guessing
that an owner is dead. `force_break(claim_name)` is an explicit operator action
that removes one named claim; strict claims never expire merely by age.
`preserve_lock_file=True` is supported, while `lifetime` and `on_acquired` are
not. Filesystems without coherent hard links must report an unsupported
protocol instead of claiming strict safety.

### `SoftFileLease`

`SoftFileLease` adds an expiring protocol-2 marker to `MarkerSoftFileLock`:

```python
SoftFileLease(
    lock_file, *, lease_duration=30.0,
    heartbeat_interval=None, on_compromise=None, **lock_options,
)
```

`lease_duration` must be positive and all contenders for a path must agree on
it. The default heartbeat is one third of the duration and must be positive and
shorter than the duration. While held, `token` identifies the current claim
and a daemon heartbeat refreshes the marker. If the marker disappears, is
replaced, or cannot be refreshed long enough for another owner to take it,
`compromise` becomes a `LeaseCompromise(lock_file, token, reason, error)` and
`on_compromise` is called from the heartbeat thread. Reasons are
`"marker-missing"`, `"owner-changed"`, and `"refresh-failed"`. A lease is not a
fencing token: an expired holder may overlap a successor, so use
`StrictSoftFileLock` when overlap is unacceptable. A contender using a
conflicting duration raises `LeaseSettingsMismatch`.

## Reader/Writer Locks

`ReadWriteLock` is a cross-process reader/writer lock backed by SQLite:

```python
ReadWriteLock(lock_file, timeout=-1, *, blocking=True, is_singleton=True)
ReadWriteLock.get_lock(lock_file, timeout=-1, *, blocking=True)
```

It permits multiple shared readers or one exclusive writer. Acquisition is
reentrant within the same mode; upgrading read-to-write and downgrading
write-to-read raise `RuntimeError`, and write ownership is pinned to its
acquiring thread. `acquire_read()` and `acquire_write()` return
`AcquireReturnProxy`; `read_lock()` and `write_lock()` are synchronous context
managers with optional `timeout`/`blocking` overrides. `release(force=False)`
releases one level, and `close()` releases held state and closes the SQLite
connection. The default singleton is keyed by resolved path and rejects
inconsistent timeout/blocking settings. A database actively used across
`fork()` is invalidated in the child; construct a new lock after the fork.
The SQLite database path must be usable by the active SQLite VFS; marker
backends create their parent directories, while SQLite follows its normal
database-path errors. SQLite-backed locking is for local filesystems, not NFS.

`SoftReadWriteLock` provides the same reader/writer shape without SQLite and
is intended for shared/network filesystems:

```python
SoftReadWriteLock(
    lock_file, timeout=-1, *, blocking=True, is_singleton=True,
    heartbeat_interval=30.0, stale_threshold=None, poll_interval=0.25,
)
SoftReadWriteLock.get_lock(lock_file, timeout=-1, *, blocking=True)
```

It uses sidecars `<lock>.state`, `<lock>.write`, and
`<lock>.readers/<host>.<pid>.<uuid>`. Reader markers have heartbeats and are
reclaimed only after `stale_threshold` (default three heartbeat intervals).
Writer acquisition first blocks new readers, then waits for existing readers,
so writers are not starved. Reentrancy, upgrade/downgrade restrictions,
thread-pinned writes, singleton behavior, fork invalidation, stale-marker
handling, and `close()` mirror the documented synchronous class.
`heartbeat_interval` and `poll_interval` must be positive, and
`stale_threshold` must be strictly greater than the heartbeat interval.

## Async API

The asynchronous lock classes mirror their synchronous counterparts and use
`asyncio` context managers and proxies:

```python
BaseAsyncFileLock(
    lock_file, timeout=-1, mode=-1, thread_local=False, *,
    blocking=True, is_singleton=False, poll_interval=0.05,
    lifetime=None, context_error_policy="chain",
    close_error_policy="default", fallback_to_soft=True,
    preserve_lock_file=False, on_acquired=None,
    loop=None, run_in_executor=True, executor=None,
)

AsyncReadWriteLock(
    lock_file, timeout=-1, *, blocking=True, is_singleton=True,
    loop=None, executor=None,
)

AsyncSoftReadWriteLock(
    lock_file, timeout=-1, *, blocking=True, is_singleton=True,
    heartbeat_interval=30.0, stale_threshold=None, poll_interval=0.25,
    loop=None, executor=None,
)
```

`AsyncFileLock`, `AsyncUnixFileLock`, `AsyncWindowsFileLock`,
`AsyncSoftFileLock`, `AsyncStrictSoftFileLock`, and `AsyncSoftFileLease` are
the corresponding backends. `AsyncSoftFileLease` accepts the lease-specific
`lease_duration`, `heartbeat_interval`, and `on_compromise` options in
addition to the common async options.

`await lock.acquire(timeout=None, poll_interval=None, *, blocking=None,
cancel_check=None)` returns `AsyncAcquireReturnProxy`; `await lock.release(force=False)`
releases one level. `async with lock:` and `async with lock.acquire():` must
release reliably. Blocking filesystem/native/SQLite work runs in the selected
executor when `run_in_executor=True`, so other tasks on the loop continue to
run. A caller-supplied executor is never shut down by the lock; an internally
owned executor is shut down by `close()` where applicable. `thread_local=True`
with executor-based async operation is invalid because the worker thread would
not preserve the caller's context. Cancellation must drain an already-running
backend operation and complete rollback before another transition can claim the
same descriptor or marker; cancellation and rollback failures remain
observable.

## Descriptor Helpers and Errors

`lock_descriptor(fd, *, blocking=True, poll_interval=0.05) -> bool` takes the
same native one-byte/exclusive OS lock used by `FileLock` on an already-open
caller-owned descriptor. It never opens, closes, truncates, unlinks,
canonicalizes, or falls back; the caller retains ownership of `fd`. A
non-blocking contention returns `False`, a successful call returns `True`, and
permanent native failures propagate. `unlock_descriptor(fd) -> None` unlocks
without closing the descriptor. There is no async wrapper for these helpers.

Provide these exception contracts:

- `Timeout(lock_file)` is a `TimeoutError` subclass with `lock_file`, stable
  string/repr forms, and pickle round-tripping.
- `SoftFileLockLifetimeWarning` is a `DeprecationWarning` for the overlapping
  legacy expiry mode.
- `LeaseSettingsMismatch` is a `ValueError` for disagreeing lease durations.
- `SoftFileLockProtocolError(lock_file, claim_name, reason)` is an `OSError`
  carrying the three inspection properties and a stable message; it is used
  whenever strict state cannot be interpreted safely.
- `LeaseCompromise` is an immutable record with `lock_file`, `token`,
  `reason`, and optional `error`.

## Filesystem, Process, and Packaging Constraints

- Use process-safe filesystem or OS primitives, not only Python locks. Separate
  interpreters must contend on the same path. Preserve atomic create/link,
  descriptor identity checks, symlink/reparse-point refusal, stale-owner
  handling, and cleanup behavior.
- Preserve thread-local versus shared context exactly: when `thread_local=True`,
  configuration and lock state are per-thread; when false, reentrancy and
  transitions are shared as documented. Preserve fork safety by resetting or
  invalidating inherited contexts rather than letting a child release the
  parent's ownership.
- Keep Unix, Windows, no-`fcntl`, no-`sqlite3`, symlink-disabled,
  hard-link-disabled, and network-filesystem behavior capability-driven. Do
  not emulate Windows by checking only `sys.platform`; the real backend must
  refuse unsupported native operations and use the documented fallback or
  fail-closed error.
- Do not treat the existence of a lock pathname as proof that a native lock is
  held. Unix keeps its inode after release; Windows may retain a pathname while
  handles close; soft and strict backends have different marker protocols.
- Include a usable `pyproject.toml`, MIT license notice, README, package data,
  and import-compatible module tree. Do not include verifier tests or hidden
  test data in the generated candidate repository.
- Preserve ordering, exception identity, warning categories, async cancellation
  behavior, and filesystem side effects. Avoid network, random external state,
  and host-specific absolute paths outside the lock paths supplied by callers.

The goal is a complete repository, not a minimal happy-path lock. A correct
implementation must be able to pass the upstream behavioral surface while
remaining installable and usable when the verifier tests are absent from the
candidate workspace.
## Frozen Linux Verification Scope

The production verifier runs on Linux/amd64 with CPython 3.12 in separate
no-network agent and verifier containers. Its fixed denominator contains 17
deterministic leaves drawn from the public contracts above: root imports and
packaging, native and soft lock lifecycle, strict claims, leases, SQLite and
soft reader/writer modes, caller-owned descriptors, asynchronous lifecycle,
marker records, singleton configuration, and timeout/error behavior.

Every probe creates a unique temporary path. Cross-process contention never
infers ordering from a sleep or scheduler race: a holder emits a readiness
signal only after acquisition, waits for an explicit release signal, and each
contender uses a finite timeout or a single non-blocking attempt. The verifier
uses bounded deadlines solely to fail infrastructure or incomplete candidates;
the required behavior is the documented held/timeout/release transition.

The Linux lane intentionally verifies local filesystem semantics only. It does
not claim Windows, network-filesystem, or cross-host certification beyond the
capability-driven behavior specified above.
