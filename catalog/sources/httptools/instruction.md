# Build `httptools`

Create a complete, installable Python project named `httptools` from an empty
workspace. The project is a native HTTP/1.x parser and URL parser compatible
with the frozen `httptools` 0.8.0 contract. It must build its Cython extension
from the repository sources; replacing the parser with regular-expression-only
or in-memory placeholder behavior is not sufficient.

## Project Description

`httptools` exposes bindings to a low-level HTTP parser. It parses request and
response byte streams incrementally and reports message events to a protocol
object. It also parses URLs into an immutable structured value. The parser is
local and deterministic: it does not open sockets, access the filesystem, or
contact a service.

The distribution and import package are both named `httptools`, and the package
version is `0.8.0`. The supported implementation target is CPython 3.12 on
Linux amd64. Preserve the package and submodule import paths, root exports,
exception classes, native extension behavior, and `py.typed` package data.

## Supports

- Provide an installable project with a `pyproject.toml` using the setuptools
  build backend and a `httptools/` package containing the parser modules.
- Build the request parser, response parser, and URL parser extensions from
  Cython/C sources. The package must work after `pip install` into a target
  directory with no network access at runtime. Both
  `httptools.parser.parser` and `httptools.parser.url_parser` must load as
  native CPython extension modules, not as Python source substitutes.
- The only build-time third-party requirements are Cython 3.1.x, setuptools,
  and wheel. Do not add runtime dependencies. The standard library types
  `bytearray`, `memoryview`, and `array.array` must be accepted as documented.
- Export from `httptools`: `HTTPProtocol`, `HttpRequestParser`,
  `HttpResponseParser`, `HttpParserError`, `HttpParserCallbackError`,
  `HttpParserInvalidStatusError`, `HttpParserInvalidMethodError`,
  `HttpParserInvalidURLError`, `HttpParserUpgrade`, `parse_url`, `parser`, and
  `__version__`.
- Keep `httptools.parser`, `httptools.parser.protocol`,
  `httptools.parser.errors`, `httptools.parser.parser`, and
  `httptools.parser.url_parser` importable.

## API Usage Guide

### `httptools.HttpRequestParser`

Constructor: `HttpRequestParser(protocol: HTTPProtocol | object)`.

`protocol` may be `None` or any object. For each available callback method,
the parser calls `on_message_begin()`, `on_url(url: bytes)`,
`on_header(name: bytes, value: bytes)`, `on_headers_complete()`,
`on_body(body: bytes)`, `on_message_complete()`,
`on_chunk_header()`, and `on_chunk_complete()`. A request also exposes
`get_method() -> bytes`, inherited `get_http_version() -> str`,
`should_keep_alive() -> bool`, and `should_upgrade() -> bool`.

`feed_data(data: bytes | bytearray | memoryview | array[int]) -> None` consumes
an increment of an HTTP stream. It is incremental: callers may feed one byte at
a time, and callbacks may be emitted before a complete message is available.
The parser keeps state across calls. Each URL fragment is forwarded as it is
observed; one-byte feeds can include an empty `on_url(b"")` boundary fragment.
Chunked requests produce `on_chunk_header()` and `on_chunk_complete()` for
every chunk, including the terminating zero-size chunk, and `on_body()` only
for non-empty body fragments. A valid Upgrade request raises
`HttpParserUpgrade` after the HTTP portion, with the offset of the non-HTTP
tail in the current input buffer as its sole argument; `should_upgrade()` is
true after headers complete.

The state getters reflect the parser's current state. After a message-complete
callback, HTTP/1.1 request parsing is ready for the next message and
`should_keep_alive()` is `True`, even when the completed request carried
`Connection: close`; a completed HTTP/1.0 request without an explicit
keep-alive remains `False`.

`set_dangerous_leniencies(`
`lenient_headers=None, lenient_chunked_length=None, lenient_keep_alive=None,`
`lenient_transfer_encoding=None, lenient_version=None,`
`lenient_data_after_close=None, lenient_optional_lf_after_cr=None,`
`lenient_optional_cr_before_lf=None, lenient_optional_crlf_after_chunk=None,`
`lenient_spaces_after_chunk_size=None) -> None` changes the named parser
leniency flags. The misspelling `leniencies` is part of the public API.

Malformed request methods raise `HttpParserInvalidMethodError`, malformed
request URLs raise `HttpParserInvalidURLError`, and non-bytes-like input raises
`TypeError`. Exceptions raised by callbacks are wrapped in
`HttpParserCallbackError` while retaining the callback exception as the Python
exception context.

### `httptools.HttpResponseParser`

Constructor and inherited methods are the same as for the request parser.
`get_status_code() -> int` returns the parsed response status. A response emits
`on_status(status: bytes)` in addition to the common callbacks. A response
with status 101 and `Connection: upgrade` raises `HttpParserUpgrade` with the
offset of the non-HTTP tail. Invalid status lines raise
`HttpParserInvalidStatusError`; other malformed response data raises
`HttpParserError`.

### `httptools.parse_url`

`parse_url(url: bytes | bytearray | memoryview | array[int]) -> URL` returns an
immutable `URL` object from `httptools.parser.url_parser`. Its attributes are
`schema: bytes | None`, `host: bytes | None`, `port: int | None`,
`path: bytes | None`, `query: bytes | None`, `fragment: bytes | None`, and
`userinfo: bytes | None`. For example,
`parse_url(b"https://user:pass@example.test:8443/a?x=1#f")` has schema
`b"https"`, host `b"example.test"`, port `8443`, path `b"/a"`, query
`b"x=1"`, fragment `b"f"`, and userinfo `b"user:pass"`.

Relative paths preserve their bytes and leave authority fields as `None`.
Bracketed IPv6 authorities expose the host bytes without brackets and parse an
explicit decimal port. Empty, whitespace-only, malformed-authority,
NUL-containing, and URLs longer than 65,535 bytes raise
`HttpParserInvalidURLError`. A URL object does not allow assignment to its
parsed attributes; assigning `port` raises `AttributeError` with the normal
native-extension message that the attribute is not writable. Non-bytes-like
input raises `TypeError`.

## Implementation Notes

- Keep request and response parsing incremental and callback-driven. Header
  names and values are bytes and callback order is observable.
- Preserve the native parser's exception class hierarchy and upgrade offsets.
  Do not catch parser errors and turn them into generic `ValueError` instances.
- Build from an empty workspace with no access to the frozen upstream checkout,
  PyPI, GitHub, or any other network service during evaluation. Include all
  required C/Cython inputs and a deterministic version in the project itself.
- The verifier focuses on the documented Linux/amd64 JSON-safe behavior. It
  does not require private implementation names, test files, or network access.
