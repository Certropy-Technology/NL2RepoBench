# Project Description

Create a complete, installable Python distribution named `httpcore` from an empty
workspace. It is a low-level HTTP transport library used by higher-level clients.
The implementation must reproduce the deterministic public behavior of the pinned
revision `10a658221deb38a4c5b16db55ab554b0bf731707` without copying the source or
upstream tests.

## Supports

- Support CPython 3.12 on Linux and provide a PEP 517 build using `pyproject.toml`.
- Install the package from the repository root with no network during candidate
  installation once the declared build/runtime dependencies are present in the
  image. Runtime dependencies are `certifi` and `h11`; optional HTTP/2 support
  uses `h2`, `hpack`, and `hyperframe`.
- Keep the scored behavior deterministic and local. The evaluator injects
  `MockStream` or `AsyncMockStream` data and never requires DNS, a socket,
  `httpbin`, a proxy service, or a live HTTP server.
- Expose `httpcore.__version__ == "1.0.9"` and keep all public imports below
  available from the package root or their documented submodules.

## API Usage Guide

### Models and exports

The root package exports `request`, `stream`, `URL`, `Origin`, `Proxy`, `Request`,
`Response`, the synchronous and asynchronous connection/pool/proxy classes,
`MockStream`, `AsyncMockStream`, `MockBackend`, `AsyncMockBackend`, the network
stream/backend base classes, `default_ssl_context`, `SOCKET_OPTION`, and the
exception hierarchy (`ConnectionNotAvailable`, `ProxyError`, `ProtocolError`,
`LocalProtocolError`, `RemoteProtocolError`, `UnsupportedProtocol`,
`TimeoutException`, `PoolTimeout`, `ConnectTimeout`, `ReadTimeout`, `WriteTimeout`,
`NetworkError`, `ConnectError`, `ReadError`, `WriteError`).

`URL(url=b"", *, scheme=b"", host=b"", port=None, target=b"")` accepts an ASCII
string or bytes URL, or explicit byte components. Its `scheme`, `host`, `port`,
and `target` fields are stable; `bytes(url)` reconstructs the request URL and
`.origin` supplies the default port for HTTP, HTTPS, WebSocket, and SOCKS5
schemes. Unicode in the convenience string form is rejected; callers can use
explicit bytes for non-ASCII request targets.

`Origin(scheme, host, port)` stores byte components, compares by value, and has a
stable `scheme://host:port` string form. `Proxy(url, auth=None, headers=None,
ssl_context=None)` parses a proxy URL, retains optional credentials as bytes, and
adds a correctly encoded `Proxy-Authorization` header when `auth` is supplied.

`Request(method, url, *, headers=None, content=None, extensions=None)` normalizes
the method, URL, and headers to bytes and wraps bytes or byte iterables in a
request stream. An extension named `target` replaces only the URL request target.
`Response(status, *, headers=None, content=None, extensions=None)` stores status,
headers, a sync or async byte stream, and extensions. `repr` uses
`<Request [b'GET']>` and `<Response [200]>` forms.

### Response streams

`Response.read()` and `Response.aread()` consume the matching sync or async stream
once and cache the complete bytes in `.content`. `iter_stream()` and
`aiter_stream()` expose one-shot chunk iteration; accessing `.content` before
reading a streaming response, or iterating a consumed stream again, raises
`RuntimeError`. `close()` and `aclose()` close a stream when it supplies the
corresponding close operation.

### Mock backends and HTTP connections

`MockStream(buffer, http2=False)` and `AsyncMockStream(buffer, http2=False)` read
the supplied byte chunks in order, return `b""` at EOF, accept writes, expose
`get_extra_info`, and have a stable representation. `MockBackend(buffer, http2=False)`
and `AsyncMockBackend` create those streams for TCP or Unix-socket requests.

`HTTP11Connection(origin, stream=None, ssl_context=None, keepalive_expiry=None,
local_address=None, uds=None, proxy=None, socket_options=None)` and its async
counterpart implement `request(method, url, *, headers=None, content=None,
extensions=None)` and `stream(...)`. They serialize an HTTP/1.1 request through
the injected mock stream, parse status/headers/body, ignore interim 1xx responses,
and support 101 protocol upgrades through `response.extensions["network_stream"]`.
An unread response closes the connection; a completed response can become idle.
Requests to a different origin, concurrent requests on a single HTTP/1.1
connection, malformed/incomplete responses, and illegal header values raise the
documented runtime or protocol exceptions.

`ConnectionPool(...)` and `AsyncConnectionPool(...)` implement the same request
and stream signatures, route by origin, reuse eligible idle connections, enforce
`max_connections` and `max_keepalive_connections`, and discard responses with a
`Connection: close` header. `connections`, `close()`/`aclose()`, and the state
inspection methods (`can_handle_request`, `is_available`, `is_idle`,
`is_closed`, `has_expired`, `info`) are public observable behavior.

`HTTP2Connection` and `AsyncHTTP2Connection` consume deterministic HTTP/2 frames
from `MockBackend(..., http2=True)` when `h2` is installed. They preserve response
status, headers, body, stream lifecycle, and connection reuse. `HTTPProxy`,
`AsyncHTTPProxy`, `SOCKSProxy`, and `AsyncSOCKSProxy` retain their public
constructors and proxy routing behavior; live proxy I/O is outside the scored
contract.

`RequestInterface` and `AsyncRequestInterface` define the request/stream contract;
`ConnectionInterface` and `AsyncConnectionInterface` expose lifecycle and
origin/state methods. The synchronous and asynchronous methods must remain
separate and must not return coroutine objects from synchronous calls.

### Exceptions and top-level helpers

Preserve exception identity and inheritance: `ConnectError` is a `NetworkError`,
`RemoteProtocolError` is a `ProtocolError`, and timeout subclasses derive from
`TimeoutException`. `request(...)` performs one request through a temporary
connection pool and `stream(...)` is its context-managed streaming equivalent.

## Implementation Notes

Keep model, exception, backend, HTTP/1.1, HTTP/2, proxy, pool, and sync/async
interfaces modular. Preserve insertion order of headers and body chunks. Do not
contact a network or execute an external program for scored operations. The
verifier invokes candidate code through one child subprocess per fixed scenario;
all callbacks and mock objects therefore remain inside the child process.

The original project supports optional Trio/AnyIO backends and live integration
tests. Those are outside this bounded deterministic contract, but importing the
root package must remain safe when optional packages are absent. Do not use a
VCS-derived version or require a `.git` directory for installation.
