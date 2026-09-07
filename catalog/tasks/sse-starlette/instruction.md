# Project Description

The package turns event values into SSE wire bytes and exposes an ASGI
`EventSourceResponse` that streams those bytes. It must preserve the async and
synchronous iterable boundary, response headers, ping serialization, bounded
send timeouts, client disconnect callbacks, cooperative shutdown, and safe
websocket denial message adaptation described below.

Operation is local and has no network access. Do not contact a server, download
source, invoke a subprocess, or depend on files outside the package.

## Natural Language Instruction

Create `sse-starlette` from an empty workspace as a complete installable python project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `sse-starlette`. Primary import or package entry: `sse_starlette`.
- CPython 3.12.14 on debian-12-amd64 with pip.
- Install from `workspace/` using `python -m pip install .`.
- Declared dependency closure: anyio==4.14.2, idna==3.19, iniconfig==2.3.0, packaging==26.3, pluggy==1.6.0, pygments==2.20.0, pytest==9.1.1, pytest-asyncio==1.4.0, setuptools==80.9.0, starlette==0.49.3, typing-extensions==4.16.0, wheel==0.45.1. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `pytest`. A fixed collection
  contains `28` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── sse_starlette/
│   ├── __init__.py
│   ├── event.py
│   ├── sse.py
│   └── py.typed
└── README.md
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### `ServerSentEvent`

Import with `from sse_starlette.event import ServerSentEvent`. The complete
signature is:

```python
ServerSentEvent(data=None, *, event=None, id=None, retry=None,
                comment=None, sep=None)
```

`encode()` returns UTF-8 `bytes`. The default line separator is `"\\r\\n"`;
`sep` may be exactly `"\\r\\n"`, `"\\r"`, or `"\\n"`. A comment is emitted
first as one `: ` line per logical line. Then `id`, `event`, each logical
`data` line, and `retry` are emitted in that order, followed by one additional
separator. `None` fields are omitted. Values are converted with `str`, while
`retry` must be an `int` when encoding or `TypeError("retry argument must be
int")` is raised. Newlines are removed from `id` and `event`, and data/comment
newlines are split into separate lines.

### `JSONServerSentEvent`

`JSONServerSentEvent(data=None, *args, **kwargs)` JSON-serializes non-`None`
data with compact separators, UTF-8 characters preserved, and NaN/Infinity
rejected. It then follows the exact `ServerSentEvent` encoding rules. JSON
serialization errors propagate.

### `ensure_bytes`

`ensure_bytes(data, sep)` returns an SSE byte payload. `bytes` and
`memoryview` values are passed through as bytes. A `ServerSentEvent` is
encoded with `sep`; a dictionary is interpreted as keyword arguments to
`ServerSentEvent` and encoded with `sep`; every other value becomes the string
form of a data-only event. The function is deterministic and local.

### `EventSourceResponse`

Import with `from sse_starlette.sse import EventSourceResponse`. The constructor
is:

```python
EventSourceResponse(
    content, status_code=200, headers=None,
    media_type="text/event-stream", background=None, ping=None, sep=None,
    ping_message_factory=None, data_sender_callable=None, send_timeout=None,
    client_close_handler_callable=None, shutdown_event=None,
    shutdown_grace_period=0,
)
```

`content` is an async iterable or synchronous iterable of values accepted by
`ensure_bytes`. The response sends an `http.response.start` message followed by
one `http.response.body` message per item with `more_body=True`, then an empty
final body with `more_body=False`. It uses a thread-pool adapter for sync
iterables. Each response has `Cache-Control: no-store` unless supplied by the
caller, and always forces `Connection: keep-alive` and
`X-Accel-Buffering: no`; its default content type is
`text/event-stream; charset=utf-8`.

`ping` defaults to 15 seconds and 0 disables the practical wait in controlled
tests. `ping` must be an `int` or `float` and cannot be negative; invalid
values raise `TypeError("ping interval must be int")` or
`ValueError("ping interval must be greater than 0")`. Pings are comment events
or the result of `ping_message_factory`, and are serialized under the send
lock. `enable_compression()` always raises `NotImplementedError`.

`send_timeout`, when not `None`, bounds each send. A timed-out send closes an
async iterator when possible and raises `SendTimeoutError`. A
`client_close_handler_callable` receives the `http.disconnect` message exactly
when the response observes client disconnect. A supplied AnyIO
`shutdown_event` is set when shutdown is detected; with a positive
`shutdown_grace_period`, the content stream may finish cooperatively before
being cancelled. Negative grace periods raise
`ValueError("shutdown_grace_period must be >= 0")`.

When called with a websocket scope, HTTP response message types are adapted to
`websocket.http.response.start` and `websocket.http.response.body` before being
sent. A background task runs after the response completes.

### `AppStatus` and `SendTimeoutError`

`AppStatus.should_exit` is the process-local shutdown flag used by the response;
the static methods `disable_automatic_graceful_drain()` and
`enable_automatic_graceful_drain_mode()` toggle the automatic mode.
`SendTimeoutError` subclasses `TimeoutError`. These names are available from
`sse_starlette.sse`, with the deterministic behavior above forming the task contract.

## Implementation Notes

Keep package imports safe when uvicorn is absent. Preserve event order and
header precedence exactly. Do not solve this task with a fake response that
only returns precomputed strings: async generators, sync iterables, callbacks,
locking, timeout cancellation, shutdown, and ASGI message transformation are
all part of the documented behavior.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```python
ServerSentEvent(data=None, *, event=None, id=None, retry=None,
                comment=None, sep=None)
```

```python
EventSourceResponse(
    content, status_code=200, headers=None,
    media_type="text/event-stream", background=None, ping=None, sep=None,
    ping_message_factory=None, data_sender_callable=None, send_timeout=None,
    client_close_handler_callable=None, shutdown_event=None,
    shutdown_grace_period=0,
)
```

```python
import sse_starlette
print(sse_starlette)
```

```python
import sse_starlette
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
