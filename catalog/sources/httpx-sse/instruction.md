# Build `httpx-sse`

Create an installable Python package named `httpx-sse`, version `0.4.3`, from an
empty workspace. It consumes Server-Sent Event (SSE) messages from HTTPX
responses and must expose the documented synchronous and asynchronous helpers.

## Project Description

The package provides `EventSource`, `connect_sse`, `aconnect_sse`,
`ServerSentEvent`, and `SSEError`. It parses the SSE wire format incrementally
from HTTPX text streams while preserving event fields and deterministic parser
state.

## Supports

- CPython 3.12 on Linux and a standard PEP 517 installable package.
- `httpx` as the only runtime dependency. The evaluator supplies its pinned
  dependency closure during image build; evaluation itself has no network.
- Root imports from `httpx_sse` and the package marker `py.typed`.
- Version `0.4.3`, the MIT license, and an importable `__version__`.

## API Usage Guide

### `ServerSentEvent`

Import with `from httpx_sse import ServerSentEvent`. The constructor is
`ServerSentEvent(event=None, data=None, id=None, retry=None)`. Missing `event`
defaults to `"message"`; missing `data` and `id` default to empty strings;
`retry` remains `None`. The read-only properties `.event`, `.data`, `.id`, and
`.retry` return those values. `.json()` parses `.data` with `json.loads` and
propagates JSON decode errors. `repr()` is deterministic and includes only
non-empty optional fields.

### `EventSource`

Construct `EventSource(response)` with an `httpx.Response`. The `.response`
property returns the same response. `iter_sse()` validates that the response
content type contains `text/event-stream`, then yields `ServerSentEvent` values
in wire order from `response.iter_text()`. `aiter_sse()` provides the same
behavior asynchronously from `response.aiter_text()` and flushes a final
unterminated line.

SSE lines recognize only CRLF, CR, and LF as line endings. A blank line dispatches
the accumulated event. `data` lines join with `"\\n"`; one optional space after
the colon is removed. `event`, `id`, and integer `retry` fields are preserved.
Comment lines and unknown fields are ignored. An `id` containing NUL is ignored,
and an invalid `retry` value does not dispatch an event by itself. The last event
id persists across dispatches as required by the SSE format.

### Connection helpers

`connect_sse(client, method, url, **kwargs)` is a context manager for an
`httpx.Client`; `aconnect_sse(client, method, url, **kwargs)` is its async
counterpart for `httpx.AsyncClient`. Both use `client.stream`, set request
headers `Accept: text/event-stream` and `Cache-Control: no-store`, and yield an
`EventSource`. Caller-supplied request options are forwarded. The context closes
the HTTPX response/stream when it exits.

### Errors and exports

`SSEError` is an `httpx.TransportError` subclass and is raised when the response
content type is not an event stream. The package root must export
`__version__`, `EventSource`, `connect_sse`, `aconnect_sse`, `ServerSentEvent`,
and `SSEError` in its declared `__all__`.

## Implementation Notes

Keep parser state across arbitrary text chunks. Do not use live servers, DNS,
wall-clock delays, external files, or network access in normal operation. The
fixed evaluator uses HTTPX MockTransport and bounded custom byte streams, and
checks both sync and async paths, multiline data, CR/CRLF/LF boundaries,
comments, ids, retry values, content-type errors, request headers, and context
manager behavior. Upstream ASGI integration and live reconnection are outside
the deterministic scored subset.

## Natural Language Instruction

Create `httpx-sse` from an empty workspace. Implement the public event model,
incremental SSE decoder, synchronous and asynchronous event sources, and HTTPX
stream context managers described above. Preserve wire order, multiline data,
event identifiers, retry values, content-type errors, and final unterminated
lines. Keep the implementation compatible with HTTPX responses and bounded
mock streams, without starting a server or accessing a network endpoint.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── src/
    └── httpx_sse/
        ├── __init__.py
        ├── _api.py
        ├── _decoders.py
        ├── _exceptions.py
        ├── _models.py
        └── py.typed
```

The distribution metadata names `httpx-sse`, while the installed import
package is `httpx_sse`. Root exports come from `src/httpx_sse/__init__.py`;
the underscored modules hold API, decoder, exception, and model logic. Use the
declared HTTPX runtime dependency and preinstalled build closure. The generated
project must install from its root with no network access.

## Examples

```python
from httpx_sse import ServerSentEvent

event = ServerSentEvent(event="update", data='{"ok": true}', id="7")
event.event       # "update"
event.json()      # {"ok": True}
```

```python
from httpx_sse import EventSource

# `response` is supplied by a local HTTPX MockTransport in the test boundary.
source = EventSource(response)
events = list(source.iter_sse())
```

```python
from httpx_sse import connect_sse

with connect_sse(client, "GET", "https://example.test/events") as source:
    first = next(source.iter_sse())
```

## Error Handling and Boundary Conditions

- `EventSource` raises `SSEError` when the response content type does not
  contain `text/event-stream`; the response object remains observable.
- CRLF, CR, and LF delimiters are equivalent. A blank line dispatches the
  current event, while comments and unknown fields are ignored.
- Multiple `data:` fields join with one newline and remove only one optional
  space after the colon. An id containing NUL is ignored and invalid retry
  text does not create a retry value.
- The parser preserves the last event id across dispatches and flushes a final
  line when an iterator ends without a delimiter. Missing optional fields use
  their documented defaults.
- Connection helpers forward caller options, add the SSE request headers, and
  close the HTTPX stream when their context exits.
