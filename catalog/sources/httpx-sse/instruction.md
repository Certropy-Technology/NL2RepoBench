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
