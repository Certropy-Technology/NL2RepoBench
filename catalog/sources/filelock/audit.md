# `filelock` Authoring Audit

Status: **blocked for production authoring**. This task-local directory contains
public provenance, behavioral inventory, and source-only validation evidence. It
contains no upstream test bytes, hidden assertions, Oracle solution,
content-addressed dependency bundle, verifier code, Docker/Harbor assets,
credentials, or shared catalog/dataset edits.

The source and public specification are strong enough for a future pilot, but
this candidate is not publishable from the present lane. The project is a
large, process- and filesystem-sensitive library whose upstream suite directly
constructs rich Python objects, patches implementation modules, creates threads
and child processes, forks, runs async tasks, and inspects platform capability.
A generic one-call JSON candidate boundary cannot preserve those semantics.

## Decision

Keep `filelock` at `lifecycle.status = "blocked"` until all of the following are
separately approved and recorded:

1. an immutable final verifier image and explicit OS/Python/platform policy;
2. a hash-locked, offline build/runtime/test dependency artifact, including the
   PEP 517 backend and the Python 3.10 conditional `exceptiongroup` path;
3. a private test bundle and allowlisted command-plan artifact;
4. a task-specific child-side adapter that can run reviewed filesystem,
   process, thread, fork, async, descriptor, and rich-exception scenarios while
   keeping expected assertions in the trusted private verifier; and
5. three valid Oracle runs followed by empty, stub, forgery, and offline
   controls.

The local Linux baseline below is source evidence only. It is not a Harbor
Oracle reward, does not establish a frozen production denominator, and must not
be reported as a published benchmark score.

## Candidate Identity and Exact Source

The candidate was the `filelock` entry in
`reports/python-package-candidates.v1.json` and
`reports/python-package-candidates.v1.md`.

- Repository: `https://github.com/tox-dev/filelock`
- Selected source release: `3.32.3`
- Release tag: `3.32.3`
- Detached revision:
  `4aa742ca0992135fe21df290c8e9023f6981bb6f`
- Commit tree: `29c4c67ee4f5ab803b3348e88c284cd0a06ab28a`
- Parent: `fb5ab3eee603f352772d33c01a3a319f10c54959`
- Commit author/committer: `gaborbernat <gaborbernat@users.noreply.github.com>`
- Commit timestamp: `2026-08-13T15:59:20Z`
- Subject: `Release 3.32.3`
- Git submodules: none
- Detached checkout: clean before the probes and clean afterward, apart from
  ignored build-generated `src/filelock/version.py` and Python caches, which
  were not part of the source revision.

The source lock is the unprefixed Git archive from the detached release:

```text
command:       git archive --format=tar HEAD
archive bytes: 1,546,240
archive members: 117
archive sha256: sha256:1717a58d7ef0983c84bda07efb11fe46f98accaf4ab2581961f32d5e84f7b7f1
```

Two independent archive commands produced the same byte count and digest. The
archive is not prefixed or repacked. The source digest in `task.toml` is this
Git archive digest, not a mutable branch or a GitHub-generated tarball URL.

The published PyPI artifacts were also fetched by their immutable URLs and
matched the metadata API hashes:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `filelock-3.32.3.tar.gz` | 218,135 | `0ffa185a3540854c95caa7fa76b76cb219d907415e2c5dc9af25fd970563487f` |
| `filelock-3.32.3-py3-none-any.whl` | 98,901 | `7f0ca4bcc0e181c60dbbd8aa9ab5b120ebb99e4e064e83636340056f833a1f09` |

A local `uv build --wheel` from the detached checkout produced the same wheel
size and SHA-256 as PyPI. The sdist's `src/filelock`, `tasks`, and `tests` files
are byte-identical to the Git tree; its only additional source file is the
Hatch-VCS-generated `src/filelock/version.py`. This cross-check ties the chosen
Git revision to the released package without copying source or license bytes
into this catalog.

## License and Package Provenance

- License path: `LICENSE`
- License bytes: `1,088`
- License Git blob: `291919c0b6f41d014767f6c877af9f7595fcff99`
- License SHA-256:
  `608c89d5060ae9921adccf3236695bc654a9946e12323ef6c021dfa04e294d48`
- Declared SPDX/license expression: `MIT`
- The file is the standard MIT permission, warranty, and liability notice, and
  the PyPI wheel metadata independently reports `License-Expression: MIT` and
  includes the license file.
- `pyproject.toml` SHA-256:
  `c0fc9b643ca82a797267044866378ac45329b5e1bc6dac0003c29ddd73b30a3c`
- `tox.toml` SHA-256:
  `f1d05e889baa14f089c36f1e7e08622a76b9f6245e161bf3ad6d66c0da903542`

The project metadata read from the exact revision is:

```text
distribution/import name: filelock
version:                 dynamic VCS version, 3.32.3 at the release tag
requires-python:         >=3.10
runtime dependencies:    none
package layout:          src/filelock/
package data:            py.typed
build backend:           hatchling.build
build requirements:      hatch-vcs>=0.5, hatchling>=1.29
console entry points:     none
sdist payload:            src, tasks, tests, tox.toml
```

The package imports only the standard library on the ordinary path. Python
3.10's grouped-error path lazily imports `exceptiongroup`; `sqlite3` is a
standard-library capability used by `ReadWriteLock`; `fcntl` and Windows
`ctypes`/CRT APIs are selected by platform. The absence of a runtime
`Requires-Dist` entry is therefore correct, but it does not remove build/test
closure requirements.

## LOC and API Inventory

Physical-line metrics were computed over tracked Python files in the exact
release checkout. Comment-only lines are excluded from the noncomment column;
`src/filelock/version.py` is generated and excluded from the Git-source count.

| tree | Python files | physical | nonblank | nonblank/noncomment |
| --- | ---: | ---: | ---: | ---: |
| `src/filelock/` implementation | 20 | 7,865 | 6,650 | 6,229 |
| `tests/` and `tests/soft_rw/` | 46 | 18,378 | 14,874 | 14,542 |
| implementation + tests | 66 | 26,243 | 21,524 | 20,771 |

Under the original NL2RepoBench LOC bands, 7,865 implementation lines are in
the **hard** band (`>= 4,000`). This is materially larger than a simple
single-file lock wrapper: the package includes native backends, marker and
lease protocols, strict claim publication, SQLite and soft reader/writer
locks, async cancellation/rollback handling, fork registries, and platform
fallbacks.

The root `filelock.__all__` contains 37 names. The source also exposes
capability and compatibility seams such as `has_fcntl`, marker encoding and
parsing, owner/process identity helpers, descriptor helpers, and the sync/async
reader-writer modules. The package's own tests contain 121 root import aliases (32 unique root
names) and 63 unique module/name import pairs, and directly import several
underscored compatibility modules;
that is an important candidate-boundary risk, not permission to expose
arbitrary implementation helpers in a future public contract.

## Public Behavior and Cross-Module Surface

The public `instruction.md` records the implementable contract. The reviewed
behavioral seams are:

- `BaseFileLock` construction, timeout/blocking/polling, reentrancy, singleton
  identity, thread-local context, deadlock detection, context decorators,
  descriptor ownership, close-error policy, grouped cleanup errors, lifetime,
  preservation, and acquisition hooks;
- `FileLock`, `UnixFileLock`, `WindowsFileLock`, and `SoftFileLock` backend
  selection and cleanup;
- `MarkerSoftFileLock`, `OwnerRecord`, `encode_marker`, `parse_marker`, PID/
  hostname/start-token inspection, and explicit marker breaking;
- `StrictSoftFileLock`, `StrictSoftFileClaim`, intent/held claim publication,
  hard-link capability checks, fail-closed malformed-state handling, doorway
  rescans, force-break behavior, and identity-safe cleanup;
- `SoftFileLease`, heartbeat refresh, lease-duration agreement,
  `LeaseCompromise`, compromise callbacks, and the non-fencing/overlap warning;
- `ReadWriteLock`'s SQLite-backed shared-reader/exclusive-writer protocol,
  singleton cache, thread-pinned writes, fork invalidation, and close;
- `SoftReadWriteLock`'s sidecar marker protocol, writer preference, heartbeats,
  stale reader recovery, cross-host assumptions, and network-filesystem use;
- all async backends and reader/writer wrappers, executor selection, async
  context managers, cancellation drain/rollback, and event-loop progress; and
- `lock_descriptor`/`unlock_descriptor`, public exception attributes and
  pickling, package version, re-exports, and `py.typed` packaging.

The instruction intentionally describes observable behavior rather than copying
function bodies, private helpers, or upstream assertion text.

## Test Inventory and Frozen-Collection Probe

The release's `pyproject.toml` configures pytest with `tests` as the test path,
`[".", "tasks"]` on `pythonpath`, strict error warnings, the
`requires_hard_links` marker, asyncio session fixture scope, and a 20-second
per-test timeout. The test tree contains 46 Python files, including six shared
helpers/conftest files and 40 modules with collected tests. A nested AST scan
found 773 statically named `test*` definitions; parametrization expands this
substantially.

The reproducible source collection command was:

```bash
cd /tmp/nl2repo-candidates/filelock
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /tmp/filelock-venv/bin/python -m pytest --collect-only -q \
  -p no:cacheprovider -p pytest_asyncio.plugin -p pytest_timeout -p pytest_mock tests
```

The explicit plugins are necessary for a clean probe: the project config names
`asyncio_default_fixture_loop_scope` and `timeout`, so disabling all plugin
autoload without loading `pytest-asyncio` and `pytest-timeout` produces
configuration errors rather than a valid collection. `pytest-randomly` was not
loaded for the normalized node-list check because it deliberately randomizes
collection order.

Four independent collection runs against the detached test tree and the
locally built release wheel used CPython 3.10.20, 3.12.11, 3.13.14, and
3.14.6 with pytest 9.0.3 and the same selected test tools. Each run had:

```text
collected:          1,306 nodes
collection errors:  0
normalized node SHA: 28702f17d1c19711be35642e725470bb3982505dd3baa3e5205d6ef455d3fb35
```

Two repeated 3.14 runs also produced the same normalized node hash. The
provisional per-module collection shape under the 3.14 run was:

| module | nodes | skips in full baseline |
| --- | ---: | ---: |
| `tests.soft_rw.test_soft_rw_async` | 15 | 0 |
| `tests.soft_rw.test_soft_rw_sync` | 79 | 0 |
| `tests.test_async_filelock` | 133 | 0 |
| `tests.test_async_filelock_acquire_cancellation` | 17 | 0 |
| `tests.test_async_filelock_release_cancellation` | 7 | 0 |
| `tests.test_async_filelock_rollback_agnostic` | 8 | 0 |
| `tests.test_async_filelock_runner_shutdown` | 3 | 0 |
| `tests.test_async_filelock_transition_admission` | 4 | 0 |
| `tests.test_async_read_write` | 30 | 0 |
| `tests.test_async_read_write_cancellation` | 16 | 0 |
| `tests.test_async_soft_contracts` | 4 | 0 |
| `tests.test_async_transition_gate` | 3 | 0 |
| `tests.test_default_mode` | 21 | 0 |
| `tests.test_error` | 5 | 0 |
| `tests.test_filelock` | 276 | 31 |
| `tests.test_fork_backends` | 16 | 0 |
| `tests.test_fork_coordination` | 22 | 2 |
| `tests.test_fork_ownership` | 25 | 0 |
| `tests.test_fork_registries` | 3 | 0 |
| `tests.test_lifetime_validation` | 119 | 0 |
| `tests.test_lock_expiry` | 29 | 0 |
| `tests.test_marker_records` | 28 | 0 |
| `tests.test_process_identity` | 14 | 1 |
| `tests.test_read_write` | 26 | 0 |
| `tests.test_read_write_fork` | 29 | 6 |
| `tests.test_read_write_unit` | 66 | 0 |
| `tests.test_soft_lease` | 34 | 0 |
| `tests.test_soft_lifetime_warning` | 26 | 4 |
| `tests.test_soft_stale` | 69 | 7 |
| `tests.test_strict_soft` | 42 | 1 |
| `tests.test_strict_soft_compat` | 2 | 2 |
| `tests.test_strict_soft_failures` | 70 | 0 |
| `tests.test_strict_soft_paths` | 6 | 0 |
| `tests.test_strict_soft_races` | 7 | 0 |
| `tests.test_strict_soft_recovery` | 3 | 0 |
| `tests.test_strict_soft_stress` | 1 | 0 |
| `tests.test_subclass_options` | 25 | 0 |
| `tests.test_unix_fallback` | 9 | 0 |
| `tests.test_util` | 13 | 0 |
| `tests.test_virtualenv` | 1 | 0 |
| **total** | **1,306** | **54** |

The final verifier must recollect after private test materialization and use a
structured report. `expected_total_source` remains `unknown` in `task.toml`;
the source probe is not a frozen denominator.

## Source Baseline and Filesystem Probes

A temporary wheel and test environment used CPython 3.14.6, pytest 9.0.3,
pytest-asyncio 1.3.0, pytest-cov 7.1.0, pytest-mock 3.15.1,
pytest-randomly 3.16.0, pytest-timeout 2.4.0, and virtualenv 21.2.0. The
selected environment resolved 16 installed package records:

```text
coverage==7.15.4
distlib==0.4.3
filelock==3.32.3
iniconfig==2.3.0
packaging==26.3
platformdirs==4.11.3
pluggy==1.6.0
Pygments==2.21.0
pytest==9.0.3
pytest-asyncio==1.3.0
pytest-cov==7.1.0
pytest-mock==3.15.1
pytest-randomly==3.16.0
pytest-timeout==2.4.0
python-discovery==1.5.2
virtualenv==21.2.0
```

The full run against the detached test tree and locally built release wheel
was executed as an unprivileged user so POSIX mode
and ownership behavior were real:

```bash
TMPDIR=/tmp/filelock-nobody-tmp PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
/tmp/filelock-venv/bin/python -m pytest -q -p no:cacheprovider \
  -p pytest_asyncio.plugin -p pytest_timeout -p pytest_mock \
  --junitxml=/tmp/filelock-audit-nobody/junit.xml tests
```

Observed result:

```text
1252 passed, 54 skipped in 187.20s (0:03:07)
JUnit: tests=1306, failures=0, errors=0, skipped=54
```

A root run reached 1,243 passed and one failure in the read-only-claim test,
with eight additional mode-related skips; root can bypass or alter POSIX mode
checks. That result was not treated as a source failure. The final verifier
must run with a deliberate non-root policy and record it as part of the
environment lock.

The task's local filesystem harness was run as the same unprivileged user:

```bash
TMPDIR=/tmp/filelock-verify-tmp \
  /tmp/filelock-venv/bin/python tasks/verify_filesystem.py
```

It completed successfully for four processes performing 100 holds each per
backend:

```text
FileLock             PASS  held=400/400 overlaps=0
SoftFileLock         PASS  held=400/400 overlaps=0
StrictSoftFileLock   PASS  held=400/400 overlaps=0
```

A focused smoke probe also passed synchronous native, strict, lease,
SQLite-reader/writer, soft-reader/writer, descriptor, and asynchronous lock
construction/acquire/release paths. No result from these source probes is an
Oracle reward.

Capability probes on this Linux host reported `fork`, `register_at_fork`,
`fcntl`, SQLite, hard links, symlinks, `O_NOFOLLOW`, directory-fd operations,
FIFO, AF_UNIX, audit events, and all tested finalization/cancellation
capabilities as available. `fork1` and the old-client compatibility path were
absent. Re-running the repository's capability shim with `fcntl` hidden engaged
the documented soft-lock fallback and completed the local filesystem probe;
hiding `sqlite3` made `ReadWriteLock` unavailable and the remaining filesystem
probe still completed. These are capability probes, not cross-platform proof.

## Filesystem and Platform Matrix

The source selects behavior from actual capabilities, not only version strings:

- Unix/macOS uses `fcntl.flock` for `UnixFileLock`; `ENOSYS` can fall back to a
  soft marker unless the caller requests fail-closed native behavior.
- Windows uses `LockFileEx` over a one-byte range, NT handles, and explicit
  reparse-point checks. Windows cleanup and symlink privilege affect skips and
  persistence of the pathname.
- Builds without `fcntl` select `SoftFileLock` with a warning.
- Builds without `sqlite3` omit the SQLite reader/writer aliases while keeping
  native/soft file locks available.
- Strict claims require coherent atomic no-replace hard links; Termux/Android
  and other filesystems without that capability must skip or fail closed.
- `ReadWriteLock` is local-filesystem SQLite and is not safe to certify on NFS.
  `SoftReadWriteLock` is the network-filesystem reader/writer option, subject
  to server cache/coherence and same-UID trust assumptions.
- Lease expiry, process start tokens, symlink handling, unlink-open-file
  behavior, permissions, fork, and audit events vary by OS/runtime and are
  capability-gated.

The release workflow's declared test matrix is broader than this Linux probe:
CPython 3.10 through 3.15 and free-threaded 3.14t/3.15t across Ubuntu
24.04, Windows 2025, and macOS 15, plus unmeasured PyPy 3.11 and GraalPy 3.11
jobs. Additional jobs exercise loopback NFSv3/NFSv4 with independent client
caches, loopback SMB/CIFS, missing `fcntl`, missing `sqlite3`, Windows symlink
privilege granted/denied, and real Termux/Android. The workflow explicitly
gates different backends for NFS and SMB; passing the local Linux test does not
license a claim of universal filesystem safety.

## Test Behavior and Determinism Review

A static scan of the 46 test files found:

- 245 `pytest.mark.parametrize` occurrences;
- 64 `skipif` occurrences and capability-dependent hard-link markers;
- 34 timeout markers;
- 215 monkeypatch/mocker environment or module patch operations;
- 499 test functions accepting `tmp_path`;
- 192 accepting `mocker`, plus 8 accepting `monkeypatch`;
- 34 subprocess calls in 10 files;
- 32 explicit thread constructions in 10 files;
- 31 `os.fork` references in five files; and
- 59 asyncio task/gather/run operations in 11 files.

The core module groups are:

- synchronous path locks, modes, timeouts, cleanup, subclasses, errors, and
  descriptor helpers (`test_filelock.py`, `test_default_mode.py`,
  `test_error.py`, `test_subclass_options.py`, `test_util.py`);
- async acquire/release, executor transitions, cancellation, and rollback;
- SQLite and soft reader/writer concurrency, stale markers, heartbeats,
  thread pinning, and fork behavior;
- soft marker identity, PID/hostname/start-token and lifetime recovery;
- strict claim races, malformed records, private-record cleanup, hard-link
  failures, symlink defenses, and recovery; and
- old-client compatibility and virtualenv/package behavior.

The suite is not byte-deterministic under every environment: parametrized
ordering can be randomized by `pytest-randomly`, skip sets depend on OS and
capabilities, wall-clock contention tests have deadlines, and conditional
xfail/skip markers are present for runtimes without coroutine/fork or native
features. A production metric must freeze the interpreter, OS, user identity,
filesystem type, pytest/plugin versions, random-order policy, skip/xfail
semantics, and timeout budget.

## Dependency Closure and Offline Gaps

The exact `pyproject.toml` has no runtime dependencies and no `uv.lock` or
hash-bearing test requirements. Its direct build/test declarations are:

```text
build: hatch-vcs>=0.5, hatchling>=1.29
test: covdefaults>=2.3, diff-cover>=10.2,
      exceptiongroup>=1.2 on Python <3.11,
      pytest>=9.0.3, pytest-asyncio>=1.3, pytest-cov>=7.1,
      pytest-mock>=3.15.1, pytest-randomly>=3.16,
      pytest-timeout>=2.4, virtualenv>=21.2
```

The temporary source-probe environment resolved the test tree to the 16
records listed above. That is one network/cache-backed resolution, not a
content-addressed dependency bundle: versions are selected from lower bounds,
registry artifacts are not committed with hashes, the build backend is absent
from the test environment listing, and no immutable base image exists for this
task.

A clean-cache offline build probe intentionally failed closed:

```text
UV_CACHE_DIR=/tmp/filelock-empty-cache uv build --wheel --offline \
  --out-dir /tmp/filelock-offline-dist .
exit status: 2
error: hatch-vcs was not found in the cache while resolving build-system.requires
```

This confirms that the current checkout cannot claim an offline build closure.
Before packaging, provision and hash the build backend, selected interpreter,
all test/verifier wheels, and any system capabilities required by the chosen
platform policy. Do not convert a successful warm-cache install into a claim
of no-network reproducibility.

## Candidate Boundary Review

The current production Python boundary is
`src/nl2repobench/verification/candidate_client.py` plus
`candidate_runner.py`:

- `call()`/`get()` JSON-encode one module/attribute request, start a fresh
  unprivileged child, import candidate code only in that child, and require one
  JSON-serializable response;
- `run_module()` can execute a candidate module with string arguments in a
  fresh child; and
- each operation has bounded input/output, CPU, memory, process, file, and
  cumulative-time limits, with no persistent object handles between calls.

The filelock suite cannot be passed faithfully by splitting upstream calls into
independent generic JSON requests:

1. Inputs include `Path` objects, open file descriptors, callbacks,
   `threading.Event`/`Thread`, executors, asyncio loops/tasks, exception
   instances, and live lock/proxy objects. These are not JSON values.
2. Successful results include lock objects, context proxies, immutable record
   objects, properties, and rich exception state. The generic runner calls
   `json.dumps` on a return value and cannot preserve identity or methods.
3. Reentrancy, singleton caches, deadlock registries, heartbeat threads,
   marker files, SQLite connections, fork registries, and async transition
   gates require state across multiple operations in one candidate process.
4. Upstream tests patch candidate internals and standard-library capability
   probes, reload modules, change directories/environment variables, inspect
   file modes and symlinks, and assert exact cleanup/error behavior. A fresh
   process per call changes those semantics.
5. Process/fork tests use the candidate's own source path and helper scripts;
   the generic module runner has no reviewed fixture protocol for child process
   creation, filesystem mounts, ownership, timing, or interval observations.
6. The package has no console entry point, so a generic console operation adds
   no substitute boundary.

A future filelock-specific adapter should accept only reviewed declarative
scenarios, construct the lock objects and callbacks inside the untrusted child,
control a temporary filesystem and environment, run bounded sync/thread/process
and async sequences, and return normalized JSON observations (state
transitions, intervals, marker/claim directory listings, public record fields,
exception type/message/properties, and cleanup results). Hidden expected values
and assertions must remain in the trusted private bundle. Directly importing
candidate code from trusted pytest, or copying the upstream test suite into a
trusted verifier, is not an acceptable fallback.

The public package name is common and available on PyPI. If agent networking is
enabled, downloading `filelock==3.32.3` is a contamination risk; the final
experiment must declare its network policy and ensure that a prebuilt upstream
solution is not silently accepted as a generated repository.

## Commands and Scope Controls

The following commands were run against a detached public checkout and
short-lived environments under `/tmp`; no command changed a tracked/shared
file outside this task directory in the repository checkout:

```text
GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none --no-checkout \
  https://github.com/tox-dev/filelock /tmp/nl2repo-candidates/filelock
git checkout --detach 4aa742ca0992135fe21df290c8e9023f6981bb6f
git show -s --format=... HEAD
git submodule status
git archive --format=tar HEAD                 # twice; identical digest
sha256sum LICENSE pyproject.toml tox.toml
uv build --wheel --out-dir /tmp/filelock-audit/dist .
uv pip install --python /tmp/filelock-venv/bin/python <wheel> <test pins>
pytest --collect-only -q ...                   # CPython 3.10, 3.12, 3.13, 3.14
pytest -q --junitxml=... tests                  # unprivileged CPython 3.14
python tasks/verify_filesystem.py               # local 4-process contention
FILELOCK_BLOCK_MODULE=fcntl ... assert_fallback.py
FILELOCK_BLOCK_MODULE=sqlite3 ... assert_fallback.py
UV_CACHE_DIR=/tmp/filelock-empty-cache uv build --wheel --offline ...
git status --short --untracked-files=all
```

No Docker build, Harbor execution, hidden-test/private-artifact materialization,
Oracle, negative control, dataset compilation, conversion-loop state update,
shared index edit, or secret use was performed. The only durable files created
for this candidate are the task-local `task.toml`, `instruction.md`, and this
`audit.md`.

## Reopen Conditions

Reopen this candidate only after:

1. selecting and recording a final platform/user/filesystem policy (at minimum,
   decide whether the production task is Linux-only or has real Windows and
   network-filesystem lanes);
2. materializing a hash-locked offline build/test/verifier closure and an
   immutable image digest;
3. recollecting the private suite in that final image with structured JUnit/JSON,
   explicit skip/xfail semantics, and a fixed denominator;
4. reviewing a child-side adapter for rich state, callbacks, descriptor and
   filesystem effects, fork/process behavior, and async cancellation; and
5. running Oracle x3, empty, stub, forgery, and offline controls before any
   lifecycle advance.
