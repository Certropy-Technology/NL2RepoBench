# Build `starlette`

Create an installable Python package named `starlette`, version `1.6.0`, from
an empty workspace. Implement the deterministic local and ASGI behavior below
from the frozen Starlette API. Evaluation runs on CPython 3.12 on Debian 12
amd64 with no runtime network access. Do not fetch the upstream project or
install packages during evaluation.

## Project Description

Starlette is a lightweight ASGI toolkit for building HTTP and WebSocket
applications. This task evaluates its core request/response primitives,
datastructures, routing helpers, and deterministic middleware behavior. The
contract intentionally excludes external services, browser clients, template
engines, multipart parsers, and telemetry integrations.

## Supports

- A normal installable project with `pyproject.toml` and a `starlette/` package.
- `starlette.__version__ == "1.6.0"` and safe imports of the documented modules.
- CPython 3.12, AnyIO-backed asynchronous helpers, and the standard library.
- ASGI 3 callables using scope dictionaries, async receive callables, and async
  send callables. Messages must use bytes for HTTP bodies and header names/values.
- Deterministic behavior only. No source checkout, package download, network
  request, subprocess, browser, credential, or environment discovery is part
  of the contract.

## API Usage Guide

### URL and datastructures

`starlette.datastructures.URL(url: str = "", scope: Scope | None = None,
**components) -> URL` stores and exposes URL components (`scheme`, `netloc`,
`path`, `query`, `fragment`, `username`, `password`, `hostname`, `port`) and
`is_secure`. It accepts either a URL string, an ASGI HTTP scope, or replacement
components, but not conflicting forms. `replace`, `include_query_params`,
`replace_query_params`, and `remove_query_params` return new URLs and preserve
the original. Query values are URL-encoded deterministically.

`URLPath(path: str, protocol: "http" | "websocket" | "" = "", host: str = "")`
is a string subclass. `make_absolute_url(base_url: str | URL) -> URL` combines
the path with a base URL; HTTP and WebSocket protocols select `http`/`https`
and `ws`/`wss` respectively.

`Headers(headers: Mapping[str, str] | None = None, raw: list[tuple[bytes,
bytes]] | None = None, scope: MutableMapping[str, Any] | None = None)` is an
immutable, case-insensitive mapping. `get`, indexing, `items`, `keys`,
`values`, `getlist`, `raw`, and `mutablecopy` are supported. `MutableHeaders`
adds case-insensitive assignment/deletion, `append`, `setdefault`, `update`,
`add_vary_header`, and mapping union (`|` and `|=`); duplicate values remain
only when explicitly appended.

`ImmutableMultiDict` preserves duplicate pairs through `multi_items()` and
returns the last value for a key. `MultiDict` additionally supports mutation,
`setlist`, `append`, `poplist`, `popitem`, `update`, and `clear`. `QueryParams`
accepts a query string, bytes, mapping, or pairs, converts keys and values to
strings, and renders URL-encoded pairs in order. `FormData` is the immutable
form container and exposes async `close()` for contained upload files.

`Secret(value: str)` returns the value only through `str()` and redacts it in
`repr`; its truth value follows the underlying string. `CommaSeparatedStrings`
parses comma-separated text with shell-style quoting, behaves as a sequence,
and renders items with quoted representations. `State` stores arbitrary values
through attributes or mapping operations and raises `AttributeError` for an
unknown attribute. `Address` is a `(host, port)` named tuple.

### Convertors and routing

`starlette.convertors` provides `StringConvertor`, `PathConvertor`,
`IntegerConvertor`, `FloatConvertor`, and `UUIDConvertor`. Each has a `regex`,
`convert(value)`, and `to_string(value)`. String values cannot be empty or
contain `/`; integer and float output rejects negative values, and float output
rejects NaN and infinity. `register_url_convertor(key, convertor)` adds a
custom convertor to `CONVERTOR_TYPES`.

`starlette.routing.compile_path(path: str) -> tuple[Pattern, str,
dict[str, Convertor]]` compiles `{name}` and `{name:type}` parameters for a URL
path or host. It returns the compiled regex, normalized format string, and
convertor mapping; duplicate names and unknown convertor types raise.
`replace_params(path, param_convertors, path_params) -> tuple[str, dict]`
serializes parameters present in the format and returns any remaining values.

`Route(path, endpoint, *, methods=None, name=None, include_in_schema=True,
middleware=None, max_body_size=None)` matches HTTP scopes as `(Match, child_scope)`
and supports `url_path_for(name, **params)`. GET routes also match HEAD;
nonmatching methods are `Match.PARTIAL`. `Match` contains `NONE`, `PARTIAL`, and
`FULL`. `NoMatchFound` is raised for unknown reverse routes.

### Requests and responses

`starlette.requests.cookie_parser(cookie_string: str) -> dict[str, str]`
leniently parses semicolon-separated cookies. `Request(scope, receive,
send)` exposes `method`, `url`, `base_url`, `headers`, `query_params`,
`path_params`, `cookies`, `client`, and `state`. Its async `body()` joins HTTP
request chunks and caches the result, `json()` parses the cached body, and
`stream()` yields chunks then an empty terminator. Re-consuming an already
consumed stream raises `RuntimeError`; `is_disconnected()` observes an HTTP
disconnect without network access.

`Response(content=None, status_code=200, headers=None, media_type=None,
background=None)` renders strings as UTF-8 bytes and bytes/memoryviews as-is.
It creates content-length and media-type headers when appropriate. `headers`
is a mutable case-insensitive view, and `set_cookie`/`delete_cookie` append
standard Set-Cookie values. `PlainTextResponse`, `HTMLResponse`, and
`JSONResponse` select their media types; JSON uses compact UTF-8 JSON and
rejects non-finite values. `RedirectResponse(url, status_code=307, ...)`
sets a quoted Location header.

Calling a response as `await response(scope, receive, send)` sends an
`http.response.start` message followed by one or more `http.response.body`
messages. `StreamingResponse(content, ...)` accepts a sync iterable or async
iterable and emits chunks with `more_body=True` followed by an empty final
body. `FileResponse._parse_range_header(header, file_size)` parses bounded
byte ranges and raises `MalformedRangeHeader` or `RangeNotSatisfiable` for
invalid requests; filesystem delivery itself is outside the scored contract.

### Middleware, background work, and concurrency

`CORSMiddleware(app, allow_origins=(), allow_methods=("GET",),
allow_headers=(), allow_credentials=False, allow_origin_regex=None,
allow_private_network=False, expose_headers=(), max_age=600)` handles CORS
preflight requests locally through `preflight_response(Headers)` and adds the
configured headers to simple responses. Disallowed origins, methods, headers,
and private-network requests produce a 400 response.

`BackgroundTask(func, *args, **kwargs)` runs a sync function in the AnyIO
threadpool or awaits an async function. `BackgroundTasks` runs added tasks in
insertion order. `run_in_threadpool(func, *args, **kwargs)` awaits a sync
function, and `iterate_in_threadpool(iterator)` asynchronously yields values
from a sync iterator.

`HTTPException(status_code, detail=None, headers=None)` and
`WebSocketException(code=1000, reason=None)` preserve their public attributes.
`starlette.status` exposes the standard HTTP status constants.

## Implementation Notes

Keep the package layout compatible with the imports above and include
`starlette/py.typed`. Preserve deterministic ordering, normal Python exception
types, and ASGI message shapes. The verifier invokes the candidate only through
a UID-isolated subprocess and supplies JSON-compatible scenarios; the trusted
verifier never imports candidate modules. Optional integrations such as
`httpx`, `jinja2`, `python-multipart`, `pyyaml`, OpenTelemetry, real sockets,
and browser-facing TestClient behavior are intentionally out of scope.
