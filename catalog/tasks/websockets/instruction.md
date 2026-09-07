# Build `websockets`

```text
workspace/
├── pyproject.toml
└── websockets/__init__.py
```

Create an installable Python distribution named `websockets`, version `17.1`,
from an empty workspace. Implement the deterministic local protocol library
described below. The evaluator does not provide the reference source and the
evaluation process has no network access.

## Project Description

`websockets` provides WebSocket protocol building blocks for synchronous and
asynchronous applications. The scored contract focuses on the pure local data
structures and RFC 6455 wire handling that do not require a live server, DNS,
TLS, a proxy, or an external service.

## Natural Language Instruction

Create the `websockets` package from an empty `workspace/`. Implement the
documented headers, URI value object, frame and close codecs, protocol state,
and asyncio message assembly contracts. Keep live services, DNS, TLS, and
optional native acceleration outside the task.

## Supports

- CPython 3.12 on Linux and a standard setuptools/PEP 517 installation.
- `python -m pip install .` from the repository root with no dependency fetch
  during evaluation. The package has no third-party runtime dependencies.
- The import package `websockets` and its `py.typed` marker.
- Root exports and modules used by the API guide: `websockets.datastructures`,
  `websockets.uri`, `websockets.frames`, `websockets.protocol`, and
  `websockets.asyncio.messages`.
- Deterministic behavior for the local APIs below. Live networking, servers,
  clients, TLS, proxies, Trio integration, legacy compatibility, and the
optional C speedups are outside the scored subset.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── websockets/
    ├── __init__.py
    ├── py.typed
    ├── datastructures.py
    ├── uri.py
    ├── frames.py
    ├── protocol.py
    └── asyncio/messages.py
```

The root re-exports the documented public names and each module remains
importable after installation.


## API Usage Guide

### Package exports

`import websockets` must expose `__version__ == "17.1"` and a declared
`__all__` containing the documented public names, including `Headers`,
`MultipleValuesError`, `Frame`, `Close`, `CloseCode`, `Opcode`, `Protocol`,
`Side`, `State`, `InvalidURI`, `InvalidHeaderValue`, `ProtocolError`, and
`ConcurrencyError`. Root exports may be lazy, but importing each exported name
must resolve to the corresponding public object.

### `Headers`

Use `from websockets.datastructures import Headers, MultipleValuesError`.
`Headers(*args: HeadersLike, **kwargs: str) -> None` accepts another `Headers`,
a mapping, an iterable of `(name, value)` pairs, or keyword values. Header
lookup is case-insensitive. `headers[name: str] -> str` returns the only value,
raises `KeyError` when absent, and raises `MultipleValuesError` when a name has
multiple values. `headers[name] = value` appends a string value; deletion
removes all values for that name. `get_all(name: str) -> list[str]` returns all
values in insertion order, `raw_items() -> Iterator[tuple[str, str]]` preserves
original spelling and order, and `copy() -> Headers` is independent. Equality
compares the case-insensitive values. `str(headers)` and `serialize() -> bytes`
use CRLF and end with an extra blank line. Values containing CR or LF raise
`InvalidHeaderValue`; `set_insecure(key: str, value: str) -> None` deliberately
bypasses that validation.

### `parse_uri` and `WebSocketURI`

`from websockets.uri import parse_uri, WebSocketURI`.
`parse_uri(uri: str) -> WebSocketURI` accepts only `ws://` and `wss://`,
lower-cases the hostname, applies default ports 80 and 443, and returns a
`WebSocketURI(secure: bool, host: str, port: int, path: str, query: str,
username: str | None = None, password: str | None = None)` dataclass.
`resource_name` returns the path or `/`, with `?query` appended when present.
`user_info` returns a `(username, password)` tuple or `None`. Fragments,
missing hosts, a username without a password, and other schemes raise
`InvalidURI`. Non-ASCII IRI input is normalized to IDNA host text and
percent-encoded path/query text.

### Frames and close codes

`from websockets.frames import Frame, Close, Opcode, CloseCode`.
`Frame(opcode: Opcode, data: BytesLike, fin: bool = True, rsv1: bool = False,
rsv2: bool = False, rsv3: bool = False)` stores a frame. `serialize(*, mask:
bool, extensions: Sequence[Extension] | None = None) -> bytes` produces RFC
6455 bytes. Text and binary frames, masking, payload lengths beyond the short
form, and `check() -> None` validation must be deterministic. `Frame.parse(
read_exact, *, mask: bool, max_size: int | None = None, extensions=None)` is a
generator returning one `Frame` from a bounded byte reader. `Close(code:
CloseCode | int, reason: str)` round-trips valid close payloads through
`serialize() -> bytes` and `Close.parse(data: BytesLike) -> Close`, and rejects
invalid status codes or invalid UTF-8 reasons with the documented
protocol/Unicode errors.

### Protocol state machine

`Protocol(side: Side, *, state: State = State.OPEN, max_size: int | tuple[int |
None, int | None] | None = 2**20, logger=None)` accepts `Side.CLIENT` or
`Side.SERVER`. `send_text(data: BytesLike, fin: bool = True) -> None` and
`send_binary(data: BytesLike, fin: bool = True) -> None` enqueue frames in
`data_to_send() -> list[bytes]`. `receive_data(data: bytes | bytearray) -> None`
parses complete frames and makes them available through `events_received() ->
list[Event]`. A correctly masked client text frame received by a server
produces a `Frame` event with the original bytes. `send_close(code: CloseCode |
int | None = None, reason: str = "") -> None` emits a close frame and
transitions to closing.

### Asyncio `Assembler`

`from websockets.asyncio.messages import Assembler`. Construct it as
`Assembler(high: int | None = None, low: int | None = None, pause: Callable =
lambda: None, resume: Callable = lambda: None)`. Put `Frame` objects into its
`frames` queue and await `get(decode: bool | None = None) -> str | bytes` to
assemble one complete message, or iterate `get_iter(decode: bool | None = None)
-> AsyncIterator[str | bytes]` for fragments. Text defaults to `str`, binary
defaults to `bytes`, and an explicit `decode` converts the opposite way.
Concurrent reads raise `ConcurrencyError`; an ended queue raises `EOFError`.

## Examples

```python
from websockets.frames import Frame, Opcode
from websockets.uri import parse_uri

parse_uri('ws://localhost:8765/chat')
Frame(Opcode.TEXT, b'hello')
```

Encode and parse local frames, close values, headers, and URI objects using
the documented return types.

## Error Handling and Boundary Conditions

Reject malformed headers and URIs, invalid opcodes, bad masking, fragmented
control frames, oversized control payloads, and invalid close codes according
to the public protocol exceptions.

## Implementation Notes

Keep the implementation local and deterministic. Preserve insertion order and
case-insensitive lookup semantics in headers, validate frame RSV/opcode and
payload constraints, apply WebSocket masking correctly, and keep protocol
state transitions consistent. Do not call `pip install` at runtime, clone the
upstream project, contact a live endpoint, start an unbounded process, or rely
on wall-clock timing. A pure-Python implementation is acceptable even though
the upstream distribution contains an optional C extension.
