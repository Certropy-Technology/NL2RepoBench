# Build `websocket-client`

Create an installable Python package named `websocket-client` from an empty
workspace. The import package is `websocket`; it must run on CPython 3.12 on
Debian 12 amd64 and must not contact any network service during evaluation.

## Project Description

`websocket-client` is a low-level and callback-oriented WebSocket client. This
task evaluates its deterministic RFC 6455 frame representation and the utility
code used to prepare a connection. Live sockets, TLS handshakes, proxies, and
threads are deliberately outside the scored surface.

## Supports

- `pip install .` from a clean workspace using the traditional `setup.py`
  build backend and the `wsdump` console entry point.
- The import modules `websocket`, `websocket._abnf`, `websocket._url`,
  `websocket._cookiejar`, `websocket._handshake`, `websocket._socket`,
  `websocket._core`, `websocket._app`, `websocket._logging`,
  `websocket._utils`, and `websocket._exceptions`.
- Standard-library-only runtime behavior. Do not add network clients,
  subprocesses, generated endpoint code, or mandatory optional dependencies.

## API Usage Guide

### Package exports and state

`websocket.__version__` is the package version. `websocket.ABNF` exposes the
opcode constants `OPCODE_CONT`, `OPCODE_TEXT`, `OPCODE_BINARY`, `OPCODE_CLOSE`,
`OPCODE_PING`, and `OPCODE_PONG`, plus the close status constants. The package
exports `WebSocket`, `WebSocketApp`, `create_connection`,
`setdefaulttimeout`, `getdefaulttimeout`, and `enableTrace`.

Construct `WebSocket(get_mask_key=None, sockopt=None, sslopt=None,
fire_cont_frame=False, enable_multithread=True, skip_utf8_validation=False,
dispatcher=None, **options)`. `gettimeout`/`settimeout` and the `timeout`
property use seconds and accept `None`, integers, or floats. `set_mask_key`
replaces the callable used for frame masks. `fileno()` raises
`WebSocketException("Connection not established")` before a connection.

Construct `WebSocketApp(url, header=None, on_open=None, on_reconnect=None,
on_message=None, on_error=None, on_close=None, on_ping=None, on_pong=None,
on_cont_message=None, keep_running=True, get_mask_key=None, cookie=None,
subprotocols=None, on_data=None, socket=None)`. Construction stores the
configuration without opening a socket. `close()` is safe on an inactive app.

### URLs, proxies, and cookies

`websocket._url.parse_url(url)` returns `(hostname, port, resource, secure)`
for `ws://` and `wss://` URLs, applying ports 80 and 443 and retaining the
query string. It raises `ValueError` for an invalid scheme or hostname.

`get_proxy_info(hostname, is_secure, proxy_host=None, proxy_port=0,
proxy_auth=None, no_proxy=None, proxy_type="http")` returns
`(proxy_host, proxy_port, proxy_auth)`. Explicit proxies require a nonzero
port; `no_proxy` supports `*`, exact domains, subdomains, and IP networks.
Environment lookup is deterministic when the relevant proxy environment
variable is set by the caller.

`SimpleCookieJar.add(set_cookie)`, `.set(set_cookie)`, and `.get(host)` store
domain-scoped cookies and return a sorted `name=value; ...` string for a host.

### Frames and protocol validation

`ABNF(fin=0, rsv1=0, rsv2=0, rsv3=0, opcode=1, mask_value=1, data="")`
represents one frame. `ABNF.mask(mask_key, data)` applies the four-byte XOR
mask. `format()` serializes short, 16-bit, and 64-bit payload lengths; set
`get_mask_key` to a deterministic callable when checking masked output.
`validate(skip_utf8_validation=False)` rejects reserved bits, illegal opcodes,
fragmented ping frames, invalid close statuses, and invalid UTF-8 close
reasons.

`frame_buffer(recv_fn, skip_utf8_validation)` incrementally reads and validates
one frame. `continuous_frame(fire_cont_frame, skip_utf8_validation)` validates,
joins, and extracts fragmented data frames.

### Handshake and logging helpers

`websocket._handshake._get_handshake_headers(resource, url, host, port,
options)` returns deterministic request header lines and a key. Explicit
`Sec-WebSocket-Key`, headers, cookies, subprotocols, host, origin, and
suppression options are honored. `_validate(headers, key, subprotocols)` checks
the Upgrade/Connection/Accept contract and returns `(valid, subprotocol)`.

`enableTrace(True, handler=None, level="DEBUG")` toggles trace logging;
`isEnabledForTrace()` reports the state. The exception classes in
`websocket._exceptions` preserve their documented inheritance and the
`WebSocketBadStatusException` status fields.

## Implementation Notes

Keep frame ordering, masking, URL parsing, cookie sorting, exception messages,
and object state deterministic. The verifier calls the candidate through a
separate UID-isolated subprocess with JSON-compatible scenarios. Do not open a
socket or use the network to satisfy this task, and do not read hidden files or
write trusted reports. The full upstream suite is recorded as provenance; the
scored denominator is the independent 30-leaf offline contract above.
