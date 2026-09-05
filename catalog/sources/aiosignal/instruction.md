# Project Description

Create an installable Python package named `aiosignal` from an empty workspace.
It is a small, dependency-backed asynchronous callback signal. The package must
work on CPython 3.10 and newer, use the `frozenlist` dependency, and expose the
public API and lifecycle below. Runtime behavior must be local and deterministic;
do not fetch source code or dependencies during evaluation.

## Project Description

`Signal` is a mutable list of asynchronous receivers while it is being built.
After `freeze()` it becomes immutable and can dispatch events with `await
signal.send(...)`. A signal owns an arbitrary application object for debugging,
preserves callback registration order, and can also be used as a decorator.

# Natural Language Instruction

Create the `aiosignal` project from an empty `workspace/`. Build an installable implementation, not a loose demonstration script. The public API guide below is the complete source of the task contract; preserve its import paths, signatures, return shapes, ordering, state changes, and exceptions.

Required capabilities:
- ordered async callback registration: implement the documented public behavior and preserve its input/output and error contract.
- frozen-list mutation rules: implement the documented public behavior and preserve its input/output and error contract.
- decorator registration: implement the documented public behavior and preserve its input/output and error contract.
- frozen asynchronous dispatch: implement the documented public behavior and preserve its input/output and error contract.

Do not copy an upstream checkout or tests. Keep behavior deterministic and local, and make the package usable from the installation layout described below. The principal public entry points include: `freeze()`, `Signal(owner: object)`, `repr(signal)`, `an`.

# Supports

- Provide `aiosignal/__init__.py`, `aiosignal/py.typed`, package metadata, and
  an installable build using `pip install .` and editable installation.
- Declare `frozenlist` as the runtime dependency. Use no network, filesystem,
  subprocess, or service behavior in the library itself.
- Preserve the frozen-list operations inherited from `frozenlist`: append,
  item assignment, deletion, iteration, indexing, length, and `freeze()`.
- The package version for this task is `1.4.0` and `Signal` is the only name
  required in `aiosignal.__all__`.


## NoNetwork boundary

Agent, candidate, verifier, Oracle, controls, and normal runtime execution are network-isolated. Do not access GitHub, package registries, Go proxies, DNS, or external services during execution; use only the frozen local build inputs.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── aiosignal/
    ├── __init__.py
    └── py.typed
```

# API Usage Guide

### `aiosignal.Signal`

Import path: `from aiosignal import Signal`

Signature: `Signal(owner: object)`; the generic form `Signal[T](owner)` must
also be accepted by normal Python typing syntax. `owner` is stored for the
signal's representation and may be any object.

The instance starts unfrozen and empty. Before freezing, register async
callables with `append`, `extend`, or the decorator form `@signal`; replace or
delete entries with normal list operations. A callback is not invoked while it
is registered. Once `signal.freeze()` has been called, all mutations must raise
`RuntimeError` and leave the callbacks unchanged.

`async def send(self, *args, **kwargs) -> None` is valid only after freezing.
It awaits each registered callback in registration order, passes the exact
positional and keyword arguments through unchanged, and returns `None`. Calling
`send` before freezing raises `RuntimeError` without invoking a callback. A
non-callable entry or a callback that is not awaitable must surface the normal
`TypeError` from invocation/awaiting; do not silently skip it. If a callback
raises, stop dispatch and propagate that exception.

`repr(signal)` is deterministic and includes the concrete class name, owner
representation, frozen state, and a list representation of the registered
callbacks, in the form `<Signal owner=..., frozen=False, [...]>`.

# Implementation Notes

Keep the signal's owner as an instance attribute and use the upstream
`frozenlist.FrozenList` mutation and freeze semantics rather than replacing it
with a plain list. Preserve callback order, support arbitrary `**kwargs`, and
make the decorator return the decorated function. The verifier exercises both
synchronous list operations and asynchronous subprocess-isolated scenarios,
including empty signals, invalid entries, mutation attempts after freezing,
argument forwarding, and representation.

# Examples

## Ordinary ordered dispatch

```python
from aiosignal import Signal

events = []
signal = Signal(owner="worker")
signal.append(lambda value: record(events, value))
signal.freeze()
await signal.send("ready")
```

## Ordinary decorator registration

```python
signal = Signal(owner=None)
@signal
async def receiver(value):
    return None
signal.freeze()
```

## Boundary: send before freeze

```python
signal = Signal(owner=None)
await signal.send()  # raises RuntimeError
```

## Boundary: mutation after freeze

```python
signal.freeze()
signal.append(receiver)  # raises RuntimeError
```

# Error Handling and Boundary Conditions

Reject invalid inputs using the documented exception or error result. Preserve empty-input behavior, ordering, Unicode/encoding behavior, cancellation or timeout semantics, and local filesystem boundaries where the API specifies them. Never turn a failed local operation into a network request, subprocess, or silent success.
