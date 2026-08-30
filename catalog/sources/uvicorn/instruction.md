# Build `uvicorn`

Create an installable Python package named `uvicorn`, version `0.52.4`, from
an empty workspace. Reproduce the deterministic public behavior below from the
frozen Uvicorn API. Evaluation uses CPython 3.12 on Debian 13 amd64 with no
runtime network access. Do not fetch the upstream project or install packages
during evaluation.

## Project Description

Uvicorn is an ASGI server implementation. This task covers its deterministic
configuration, import, logging, middleware, protocol-helper, WSGI-adaptation,
flow-control, and server-state behavior. The scored contract uses in-memory
ASGI scopes and transport doubles. It does not start listening sockets or
process supervisors.

## Supports

- A normal installable project with `pyproject.toml` or `setup.py`, a
  `uvicorn/` package, distribution metadata version `0.52.4`, and a `uvicorn`
  console entry point.
- CPython 3.12 with the preinstalled `click` and `h11` runtime dependencies.
- ASGI 2 and ASGI 3 callables, JSON-safe in-memory scopes and messages, and
  WSGI environment construction.
- Deterministic behavior only. No source checkout, package download, external
  network request, real listener, signal delivery, subprocess supervision,
  TLS file access, or reload watcher is part of the scored contract.

## API Usage Guide

### Package exports and command line

`uvicorn.__version__` is `"0.52.4"`. The package exports `main`, `run`,
`Config`, and `Server`, with `__all__` in that order. The installed `uvicorn`
console command is the Click command from `uvicorn.main:main`. It accepts an
`APP` argument and normal Uvicorn options including `--host`, `--port`,
`--workers`, `--help`, and `--version`. Help exits successfully, and version
output identifies Uvicorn 0.52.4, CPython, the interpreter version, and the
platform.

`uvicorn._ansi.style(text: str, fg: str | None = None, bold: bool = False) ->
str` wraps text with ANSI foreground and bold codes, in that order, and always
appends the ANSI reset sequence. Supported foreground names are `black`,
`red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, and their
`bright_` variants.

### Import resolution

`uvicorn.importer.import_from_string(import_str: Any) -> Any` returns a
non-string input unchanged. A string must have the form
`"module:attribute.nested"`; the function imports the module and traverses each
attribute component. Invalid syntax, a missing top-level module, or a missing
attribute raises `ImportFromStringError` with a descriptive message. An import
error raised from inside an otherwise found module is propagated unchanged.

### Configuration

`uvicorn.config.Config` has this constructor:

```python
Config(
    app,
    host="127.0.0.1",
    port=8000,
    uds=None,
    fd=None,
    loop="auto",
    http="auto",
    ws="auto",
    ws_max_size=16 * 1024 * 1024,
    ws_max_queue=32,
    ws_ping_interval=20.0,
    ws_ping_timeout=20.0,
    ws_per_message_deflate=True,
    lifespan="auto",
    env_file=None,
    log_config=LOGGING_CONFIG,
    log_level=None,
    access_log=True,
    use_colors=None,
    interface="auto",
    reload=False,
    reload_dirs=None,
    reload_delay=0.25,
    reload_includes=None,
    reload_excludes=None,
    workers=None,
    proxy_headers=True,
    server_header=True,
    date_header=True,
    forwarded_allow_ips=None,
    root_path="",
    limit_concurrency=None,
    limit_max_requests=None,
    limit_max_requests_jitter=0,
    backlog=2048,
    timeout_keep_alive=5,
    timeout_notify=30,
    timeout_graceful_shutdown=None,
    timeout_worker_healthcheck=5,
    callback_notify=None,
    ssl_keyfile=None,
    ssl_certfile=None,
    ssl_keyfile_password=None,
    ssl_version=SSL_PROTOCOL_VERSION,
    ssl_cert_reqs=ssl.CERT_NONE,
    ssl_ca_certs=None,
    ssl_ciphers=None,
    ssl_context_factory=None,
    headers=None,
    factory=False,
    h11_max_incomplete_event_size=None,
    reset_contextvars=False,
)
```

Constructor options are retained as public attributes. `workers` defaults to
one, or to `WEB_CONCURRENCY` when that environment variable is present and no
explicit value is supplied. `forwarded_allow_ips` defaults to
`FORWARDED_ALLOW_IPS`, then to `"127.0.0.1"`. `loaded` starts false.

`is_ssl` is true when a key file, certificate file, or SSL context factory is
configured. `use_subprocess` is true for reload mode or more than one worker.
`should_reload` is true only when `app` is an import string and reload mode is
enabled. `asgi_version` maps `asgi2` to `"2.0"` and `asgi3`/`wsgi` to `"3.0"`.

`load() -> None` resolves the selected HTTP, WebSocket, lifespan, and app
imports; rejects a second call; creates lower-case Latin-1 encoded headers;
adds `(b"server", b"uvicorn")` unless disabled or overridden; and detects
ASGI 3, ASGI 2, or explicitly selected WSGI interfaces. `ws="none"` disables
the WebSocket protocol. ASGI 2 apps are wrapped in `ASGI2Middleware`; WSGI apps
are wrapped in `WSGIMiddleware`; proxy-header wrapping follows configuration.
An app factory is called with no arguments. Import failure exits with
`STARTUP_FAILURE` (`3`).

`get_loop_factory() -> Callable[[], AbstractEventLoop] | None` returns `None`
for `loop="none"` and a loop factory for `"auto"`, `"asyncio"`, `"uvloop"`,
or a custom import string. `setup_event_loop()` is removed and raises
`AttributeError` explaining that `get_loop_factory` replaced it in Uvicorn
0.36.0.

`is_dir(path: pathlib.Path) -> bool` resolves relative paths and returns false
on filesystem errors. `resolve_reload_patterns(patterns_list: list[str],
directories_list: list[str]) -> tuple[list[str], list[pathlib.Path]]` expands
directory patterns, resolves existing directories, removes nested child
directories when their parent is already watched, removes duplicates, and
returns the normalized patterns and directories. Ordering is not guaranteed.

### Logging helpers

`ColourizedFormatter(fmt=None, datefmt=None, style="%", use_colors=None)` is a
`logging.Formatter`. `use_colors` defaults from terminal detection.
`color_level_name(level_name, level_no) -> str` applies level-specific colors,
and `formatMessage(record) -> str` adds a left-aligned eight-character
`levelprefix` ending in `:`. When colors are active, `color_message` in a log
record replaces the ordinary message.

`DefaultFormatter` uses stderr terminal detection. `AccessFormatter` adds
`get_status_code(status_code: int) -> str` and formats a record whose arguments
are `(client_addr, method, full_path, http_version, status_code)`. Known status
codes include their standard phrase; unknown codes include an empty phrase.

`message_with_placeholders(message: Any) -> Any` in
`uvicorn.middleware.message_logger` shallow-copies a mapping and replaces
`body`, `bytes`, `text`, and `headers` content with length or redaction
placeholders. It does not mutate the input.

### Proxy headers middleware

`ProxyHeadersMiddleware(app, trusted_hosts: list[str] | str = "127.0.0.1")`
is an ASGI 3 wrapper. Trusted hosts may be exact IPv4/IPv6 addresses, CIDR
networks, literal host names or Unix-socket strings, comma-separated text, or
`"*"`. Lifespan scopes pass through unchanged. Untrusted peers cannot alter the
scope.

For a trusted peer, valid `X-Forwarded-Proto` values update the scope scheme;
HTTP `http`/`https` values become WebSocket `ws`/`wss` for WebSocket scopes.
All `X-Forwarded-For` header occurrences are combined. The client is the first
untrusted hop when reading the combined chain from right to left. If every hop
is trusted, the leftmost hop is used. Bare addresses use port `0`; IPv4
`host:port` and bracketed IPv6 `[host]:port` are supported. Empty or malformed
values are handled conservatively.

### Protocol utilities

In `uvicorn.protocols.utils`:

- `get_remote_addr(transport) -> tuple[str, int] | None` prefers the transport
  socket's peer name, then a two-item `peername` extra.
- `get_local_addr(transport) -> tuple[str, int | None] | None` prefers the
  socket's local name, then `sockname`; Unix paths have a `None` port.
- `is_ssl(transport) -> bool` reflects whether `sslcontext` is present.
- `get_client_addr(scope) -> str` returns `"host:port"`, or `""` without a
  client.
- `get_path_with_query_string(scope) -> str` URL-quotes the Unicode path and
  appends a nonempty ASCII query string.
- `ClientDisconnected` is an `OSError` subclass.

`uvicorn.protocols.http.flow_control.FlowControl(transport)` exposes
`read_paused` and `write_paused`, idempotent `pause_reading()` /
`resume_reading()` and `pause_writing()` / `resume_writing()`, and async
`drain()`. Pausing writes blocks `drain` until resumed.

`service_unavailable(scope, receive, send) -> None` sends a 503 ASGI response
with body `b"Service Unavailable"`, content type `text/plain; charset=utf-8`,
content length `19`, and `connection: close`. `HIGH_WATER_LIMIT` is `65536`
and `CLOSE_HEADER` is `(b"connection", b"close")`.

When only the required dependencies are present, `AutoHTTPProtocol` resolves
to `H11Protocol`, `AutoWebSocketsProtocol` is `None`, and `auto_loop_factory`
uses the standard asyncio loop factory.

### ASGI and WSGI adaptation

`ASGI2Middleware(app)` stores an ASGI 2 application. Calling the middleware
creates `app(scope)` and awaits the returned instance with `(receive, send)`.

`build_environ(scope, message, body: io.BytesIO) -> dict` in
`uvicorn.middleware.wsgi` creates a PEP 3333 environment. It sets request,
script/path, query, protocol, scheme, WSGI, server and optional remote-address
keys. `content-type` and `content-length` become `CONTENT_TYPE` and
`CONTENT_LENGTH`; other headers become `HTTP_*`; duplicate values are joined
with commas. Unicode script and path components are converted through UTF-8
bytes and Latin-1 text as required by WSGI.

### Server and lifespan state

`ServerState()` starts with `total_requests == 0`, empty `connections` and
`tasks` sets, and an empty `default_headers` list.

`Server(config)` exposes `server_state`, `started`, `should_exit`, and
`force_exit`, all initially false where applicable. Its cached
`limit_max_requests` is `None` when disabled; otherwise it is the configured
limit plus a random integer from zero through `limit_max_requests_jitter`.

`LifespanOff(config)` has `should_exit == False`, a mutable empty `state`
dictionary, and async no-op `startup()` and `shutdown()` methods.

`LOG_LEVELS` maps `critical`, `error`, `warning`, `info`, `debug`, and `trace`
to standard logging levels plus trace level `5`. `INTERFACES` is
`["auto", "asgi3", "asgi2", "wsgi"]`; `TRACE_LOG_LEVEL` is `5`.

## Implementation Notes

Keep module paths and distribution metadata compatible with the imports above.
Preserve normal Python exception classes, message text, ASGI message shapes,
bytes-versus-text boundaries, and deterministic ordering where specified.
Include any package marker files needed by your build backend.

The verifier invokes the candidate only through UID-isolated subprocesses. The
trusted verifier does not import candidate modules. Live HTTP/WebSocket
protocol engines, real sockets, TLS certificates, signal capture, workers,
reload polling, native `httptools`/`uvloop`, optional WebSocket libraries, and
Gunicorn integration are intentionally outside the scored contract.
