# `anyio` authoring record

Status: **blocked**. This directory freezes and audits the requested upstream
revision. It is not a runnable Harbor task. It contains no generated runtime,
private source/test/dependency bundle, Oracle solution, control receipt, or
reward.

## Project Description

AnyIO 4.15.0 is a high-level asynchronous concurrency and networking library
that exposes one public API over both asyncio and Trio. The frozen source spans
event-loop selection, cancellation, task groups, futures, synchronization,
typed attributes, memory/file/TLS streams, sockets, subprocesses, worker
threads, worker processes, subinterpreters, signal receivers, temporary files,
and a pytest plugin.

The source authority is known:

- upstream: `https://github.com/agronholm/anyio`;
- revision: `928366259543412a2deb1e2ba09ea45ffa92ef4f`;
- exact tag: `4.15.0`;
- Git tree: `50b1e8f311c883eb9a26c36dffae06e5bfc056aa`;
- unprefixed Git archive: 1,413,120 bytes, SHA-256
  `688c88c5af84b9d9e2eb4efa17227bc9073210d71da09754bfe954779f4e0542`;
- license: MIT, `LICENSE` SHA-256
  `5361ac9dc58f2ef5fd2e9b09c68297c17f04950909bbc8023bdb82eacf22c2b0`;
- submodules: none.

## Supports

Upstream declares Python `>=3.10` and classifiers through Python 3.15. The
repository's current Python Harbor lane is pinned to CPython 3.12.14 on the
digest-addressed Debian 13 image recorded in `task.toml`. Any runnable task
must preinstall a complete hash-locked closure during image build and then run
the Agent, candidate, verifier, Oracle, and every control with
`network_mode=no-network`.

That closure is not available here. Runtime requirements include `idna` and,
on Python before 3.15, `typing_extensions`; backend-complete behavior also
requires Trio and its transitive closure. The upstream test group additionally
requires pytest plugins, Hypothesis, TLS fixtures, process inspection, loop
implementations, and build backends. The checkout contains no lock file. A
local Python 3.14.6 source-path probe reached the lazy package root but failed
while loading socket/typed-attribute APIs because `typing_extensions` was not
installed; neither backend could be imported in that environment. This is an
environment observation, not an Oracle result.

## API Usage Guide

The frozen root package exposes roughly 96 non-private attributes and the
source contains 46 Python modules. A top-level AST inventory found 300 public
definitions: 153 classes, 69 async functions, and 78 synchronous functions.
The backend abstraction alone defines 47 methods covering event-loop state,
cancellation checkpoints/scopes, task groups, synchronization, worker
threads, subprocesses, TCP/UDP/UNIX sockets, address resolution, signals, task
inspection, and test runners.

These objects are not plain JSON values. Their observable behavior depends on
live coroutine objects, cancellation exception identity, exception groups,
context variables, scheduler checkpoints, task ancestry, deadlines and clocks,
file descriptors, socket addresses, process groups, OS signals, threads,
interpreter availability, and backend-specific options. Callbacks and coroutine
functions supplied by users must execute inside the selected backend and
preserve context and cancellation semantics.

The upstream suite has 29 `test_*.py` modules and 304 top-level test functions,
257 of them async. This is not the frozen denominator because pytest expands
backend and parameter matrices dynamically. The suite includes 153 textual
backend fixture/parameter references and extensive socket, subprocess,
thread/process, interpreter, signal, timing, and pytest-plugin coverage.

## Implementation Notes

The production verifier must remain a separate trusted process and cannot
import candidate code directly. The current generic Python child protocol is
appropriate for bounded serializable calls, but it does not define a way to
transport a live task group, cancel scope, stream, socket, listener, process,
portal, event-loop token, callback, or coroutine while preserving asyncio and
Trio scheduling semantics. Running upstream pytest in the trusted verifier
with candidate code on `sys.path` would violate the isolation contract.

Restricting the task to stateless helpers, one backend, or memory streams would
be a new scope decision and would not establish fidelity for AnyIO 4.15.0.
Likewise, replacing real local socket/process/signal behavior with JSON mocks
would change the public contract. The task therefore remains blocked pending:

1. an approved public API scope that explicitly states whether both asyncio
   and Trio are required;
2. a private, hash-locked Python 3.12 dependency/test closure;
3. a reviewed child-side scenario protocol for callbacks, cancellation,
   clocks, tasks, streams, local sockets, subprocesses, threads/processes,
   interpreters, signals, and pytest plugin behavior;
4. a source-only NoNetwork collection that records the expanded fixed
   denominator and backend/platform skips;
5. successful compile, Oracle, empty, stub, forgery, and offline controls
   against one final manifest.

Until those items exist, `catalog/tasks/anyio/` must remain absent and no
Oracle/control result may be inferred from this audit.
