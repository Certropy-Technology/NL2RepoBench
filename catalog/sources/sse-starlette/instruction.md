# Build `sse-starlette`

Create an installable Python package named `sse-starlette`, version `3.4.8`,
from an empty workspace. It implements a local, deterministic subset of a
Server-Sent Events response library for Starlette and FastAPI.

## Project Description

The package turns event values into SSE wire bytes and exposes an ASGI
`EventSourceResponse` that streams those bytes. It must preserve the async and
synchronous iterable boundary, response headers, ping serialization, bounded
send timeouts, client disconnect callbacks, cooperative shutdown, and safe
websocket denial message adaptation described below.

Evaluation is local and has no network access. The verifier supplies only
JSON-safe scenarios to a separate child process; do not contact a server,
download source, invoke a subprocess, or depend on files outside the package.

## Supports

- CPython 3.12 on Debian 12 amd64.
- A PEP 517 installable package with import package `sse_starlette`.
- Runtime dependencies `starlette` and `anyio` from the supplied build-time
  closure. Do not add a runtime dependency on uvicorn, FastAPI, SQLAlchemy,
  Graphviz, or any external service.
- Root exports `EventSourceResponse`, `ServerSentEvent`, and
  `JSONServerSentEvent`; `sse_starlette.event` also exports `ensure_bytes`.
- Version `3.4.8` and a `py.typed` marker. Metadata must be deterministic and
  must not be obtained from the network.

The scored contract excludes live HTTP servers, database streaming, uvicorn
signal installation, real sockets, threads, and the upstream experimentation
and integration suites. ASGI scopes and messages are represented by ordinary
JSON-compatible dictionaries in the verifier.

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
`sse_starlette.sse`, but only the deterministic behavior above is scored.

## Implementation Notes

Keep package imports safe when uvicorn is absent. Preserve event order and
header precedence exactly. Do not solve this task with a fake response that
only returns precomputed strings: the verifier exercises async generators,
sync iterables, callbacks, locking, timeout cancellation, shutdown, and ASGI
message transformation through a child-side adapter. Keep the candidate and
trusted verifier processes separate; hidden test files and expected values are
not available in the workspace.
