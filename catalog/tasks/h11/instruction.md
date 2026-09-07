# Build `h11`

Create an installable Python package named `h11` from an empty workspace. The
package must implement the bounded public HTTP/1.1 protocol surface described
below. It must run on CPython 3.12 on Debian 12 amd64 and must not contact any
network service during evaluation.

## Project Description

`h11` is a pure-Python, bring-your-own-I/O implementation of HTTP/1.1. It
models requests, responses, body data, connection closure, header rules,
wire serialization, wire parsing, and the coupled client/server state machine.
The package contains no socket or network implementation.

## Natural Language Instruction

Create `h11` from an empty `workspace/`. Implement the event model, normalized
headers, incremental HTTP/1.1 readers and writers, and the client/server state
machine described below. The result must be an installable package rather than
a single demonstration function. Preserve wire bytes, event order, sentinel
identity, and protocol error classes. Keep all I/O supplied by the caller; this
project does not open sockets or contact a service.

## Supports

- `pip install .` from a clean workspace and normal imports of `h11`.
- The package modules `h11.__init__`, `h11._events`, `h11._headers`,
  `h11._connection`, `h11._readers`, `h11._writers`, `h11._receivebuffer`,
  `h11._state`, `h11._util`, `h11._abnf`, and `h11.py.typed`.
- Standard-library-only runtime behavior. Do not add runtime dependencies,
  network clients, subprocesses, or generated endpoint code.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── h11/
│   ├── __init__.py
│   ├── _abnf.py
│   ├── _connection.py
│   ├── _events.py
│   ├── _headers.py
│   ├── _readers.py
│   ├── _receivebuffer.py
│   ├── _state.py
│   ├── _util.py
│   ├── _writers.py
│   └── py.typed
└── README.md
```

The metadata must map the package root to `h11`; private tests, verifier files,
Oracle files, and reports are not part of this tree.

## API Usage Guide

### Public constants and exceptions

Import `CLIENT`, `SERVER`, `IDLE`, `SEND_RESPONSE`, `SEND_BODY`, `DONE`,
`MUST_CLOSE`, `CLOSED`, `MIGHT_SWITCH_PROTOCOL`, `SWITCHED_PROTOCOL`, and
`ERROR` from `h11`. These are identity-based sentinel values and their `repr`
is the name. Import `NEED_DATA` and `PAUSED` from `h11`; they are sentinel
return values from parsing. `ProtocolError` is the abstract base exception;
`LocalProtocolError` describes an illegal local action and
`RemoteProtocolError` describes invalid peer data. Protocol errors expose an
`error_status_hint` integer, defaulting to 400.

### Event objects

Import `Request`, `InformationalResponse`, `Response`, `Data`, `EndOfMessage`,
and `ConnectionClosed` from `h11`. `Request` accepts keyword-only
`method`, `target`, and `headers`, with optional `http_version` defaulting to
`b"1.1"`. `Response` and `InformationalResponse` accept keyword-only
`status_code`, `headers`, optional `http_version`, and optional `reason`.
`Data(data, chunk_start=False, chunk_end=False)` stores body bytes and chunk
markers. `EndOfMessage(headers=None)` stores optional trailer headers.

Methods, targets, versions, header names, and header values accept ASCII
strings or bytes-like values where the API documents them. Requests on HTTP
1.1 require exactly one `Host` header. Response status codes must be integers
between 200 and 999; informational status codes must be between 100 and 199.
Event objects are immutable and unhashable.

### Headers

Headers are represented by an ordered list of `(name, value)` pairs. Construct
events with strings or bytes; names are lowercased for lookup and values are
validated and stripped according to HTTP field rules. `event.headers` is a
sequence of normalized byte pairs. Its `raw_items()` method returns original
header-name casing paired with normalized values. Repeated compatible headers
preserve order. `Content-Length` values must agree and contain only digits;
only `Transfer-Encoding: chunked` is supported.

### `Connection`

Construct `Connection(CLIENT)` for a client or `Connection(SERVER)` for a
server. `send(event)` returns serialized bytes for requests, responses, body
data, and end-of-message events, and returns `None` for `ConnectionClosed`.
`send_with_data_passthrough(event)` returns the individual byte writes and
preserves the exact data object for `Data` events. `receive_data(data)` queues
peer bytes; pass `b""` to signal EOF. `next_event()` returns an event,
`NEED_DATA`, or `PAUSED`. `our_state`, `their_state`, `states`,
`their_http_version`, `trailing_data`, and
`they_are_waiting_for_100_continue` expose connection state. Call
`start_next_cycle()` only when both sides are `DONE` and keep-alive is active.

Requests serialize as `METHOD TARGET HTTP/1.1`, with `Host` first. Responses
serialize as `HTTP/1.1 STATUS REASON`; body framing uses `Content-Length`,
chunked transfer encoding, or close-delimited HTTP/1.0 behavior. Unknown
length HTTP/1.1 responses receive `Transfer-Encoding: chunked` automatically.

### Internal modules used by the contract

The tests exercise the stable behavior of `_events`, `_headers`, `_connection`,
`_state`, `_util`, and the reader/writer path. Internal module names and class
signatures are part of this task's bounded contract even though the project
does not promise the complete generated API surface outside it.

## Implementation Notes

Keep ordering deterministic and preserve ordinary exception types and messages
for protocol errors. Do not implement networking, token handling, browser
behavior, or external I/O. The verifier invokes the candidate through a
separate UID-isolated subprocess and passes only JSON-compatible scenarios.
Do not read hidden files or write trusted reports. The full upstream test suite
is used as provenance; the scored denominator is the independent 24-leaf
contract covering the deterministic local protocol surface.

## Examples

```python
from h11 import CLIENT, Connection, Request

conn = Connection(CLIENT)
wire = conn.send(Request(method="GET", target="/", headers=[("Host", "example.test")]))
assert wire.startswith(b"GET / HTTP/1.1")
```

```python
from h11 import CLIENT, Connection, Data, EndOfMessage, Request

conn = Connection(CLIENT)
conn.send(Request(method="POST", target="/upload", headers=[("Host", "example.test")]))
conn.send(Data(data=b"payload"))
conn.send(EndOfMessage())
```

## Error Handling and Boundary Conditions

- Invalid local headers or illegal state transitions raise `LocalProtocolError`;
  malformed peer bytes raise `RemoteProtocolError`.
- Conflicting `Content-Length`, unsupported transfer framing, and an HTTP/1.1
  request without `Host` must not be silently accepted.
- `next_event()` may return `NEED_DATA` or `PAUSED`; EOF is supplied as
  `receive_data(b"")` and is represented by `ConnectionClosed`.
- Keep-alive cycles may restart only after both sides are complete. All agent,
  candidate, verifier, Oracle, and control execution is `network_mode=no-network`.
