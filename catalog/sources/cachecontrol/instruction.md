# Build `CacheControl`

Create a complete, installable Python project for the distribution
`CacheControl` and import package `cachecontrol`. Start from the empty workspace.
The implementation must run on CPython 3.12, preserve CacheControl 0.14.4's
public behavior described below, and make no network connection during
evaluation.

## Project Description

CacheControl adds RFC-aware HTTP caching to `requests`. It stores serialized
`urllib3.HTTPResponse` objects, decides whether a cached response is fresh,
adds conditional request headers for stale ETag entries, updates cached content
after a 304 response, and provides in-memory and filesystem cache backends.
This task covers those behaviors with prepared requests and in-memory response
bodies. It does not require a live web server, DNS, TLS, Redis, or outbound HTTP.

## Supports

- Python 3.10 or newer; evaluation uses CPython 3.12 on Debian 12 amd64.
- A PEP 517 `pyproject.toml` that supports `pip install .` without build
  isolation or network access during evaluation.
- Distribution version `0.14.4`, import package `cachecontrol`, and console
  script `doesitcache` mapped to `cachecontrol._cmd:main`.
- Runtime dependencies compatible with `requests >= 2.16.0` and
  `msgpack >= 0.5.2, < 2.0.0`. The `filecache` extra declares
  `filelock >= 3.8.0`; the Redis extra may remain optional.
- The modules `cachecontrol`, `cachecontrol.adapter`, `cachecontrol.cache`,
  `cachecontrol.controller`, `cachecontrol.filewrapper`,
  `cachecontrol.heuristics`, `cachecontrol.serialize`, `cachecontrol.wrapper`,
  `cachecontrol.caches`, and `cachecontrol.caches.file_cache`.
- Local deterministic operation. Do not contact a server, launch a subprocess,
  inspect hidden verifier paths, or write trusted reports.

## API Usage Guide

### Package exports and session wrapper

The package root exports `CacheControlAdapter`, `CacheController`, and
`CacheControl`, plus `__author__`, `__email__`, and `__version__`. The version
is the installed distribution version string `"0.14.4"`.

```python
def CacheControl(
    sess: requests.Session,
    cache: BaseCache | None = None,
    cache_etags: bool = True,
    serializer: Serializer | None = None,
    heuristic: BaseHeuristic | None = None,
) -> requests.Session
```

`CacheControl` mounts one `CacheControlAdapter` for `http://` and one for
`https://`, then returns the same session object. The adapter constructor is:

```python
CacheControlAdapter(
    cache: BaseCache | None = None,
    cache_etags: bool = True,
    controller_class: type[CacheController] | None = None,
    serializer: Serializer | None = None,
    heuristic: BaseHeuristic | None = None,
    cacheable_methods: Collection[str] | None = None,
    *args,
    **kwargs,
)
```

It is a `requests.adapters.HTTPAdapter`. `close()` closes both the HTTP adapter
and its cache. Real transport through `send()` is outside the evaluation
contract; constructing, mounting, and closing adapters must remain local.

### Cache backend contract

`cachecontrol.cache.BaseCache` defines this interface:

```python
get(key: str) -> bytes | None
set(key: str, value: bytes, expires: int | datetime | None = None) -> None
delete(key: str) -> None
close() -> None
```

The base `get`, `set`, and `delete` methods raise `NotImplementedError`.
`close()` is a no-op by default. `DictCache(init_dict=None)` implements this
contract with a mutable mapping and thread-safe writes/deletes. Missing keys
return `None`; deleting a missing key is harmless; `expires` is accepted but
does not expire in-memory values.

`SeparateBodyBaseCache` adds:

```python
set_body(key: str, body: bytes) -> None
get_body(key: str) -> IO[bytes] | None
```

Its base methods raise `NotImplementedError`.

### Filesystem caches

```python
FileCache(
    directory: str | PathLike[str],
    forever: bool = False,
    filemode: int = 0o0600,
    dirmode: int = 0o0700,
    use_dir_lock: bool | type[filelock.BaseFileLock] | None = None,
)

SeparateBodyFileCache(...same arguments...)
url_to_file_path(url: str, filecache: FileCache) -> str
```

Both classes use SHA-224 cache keys, nested prefix directories, atomic writes,
and the configured file/directory modes. `FileCache` stores metadata and body
together. `SeparateBodyFileCache` stores metadata and body separately;
`get_body` returns an open binary file or `None`. `delete` removes all files
for the key and ignores absent files. Expiration accepts integer seconds or a
`datetime`. `forever=True` disables expiration cleanup.

`url_to_file_path` first normalizes an absolute URL with
`CacheController.cache_url`, then returns the corresponding metadata path. A
relative URL raises the same absolute-URI error as `cache_url`.

### URI and cache-control parsing

```python
parse_uri(uri: str) -> tuple[str | None, str | None, str, str | None, str | None]
CacheController.cache_url(uri: str) -> str
CacheController.parse_cache_control(headers: Mapping[str, str]) -> dict[str, int | None]
```

`parse_uri` returns `(scheme, authority, path, query, fragment)` using RFC 3986
component boundaries without changing spelling. `cache_url` requires an
absolute URI, lowercases scheme and authority, supplies `/` for an empty path,
keeps the query, and removes the fragment.

`parse_cache_control` treats directive names case-insensitively. It recognizes
`max-age`, `max-stale`, `min-fresh`, `no-cache`, `no-store`, `no-transform`,
`only-if-cached`, `must-revalidate`, `public`, `private`, `proxy-revalidate`,
and `s-maxage`. Numeric directives have integer values. Flag directives and
`max-stale` without a value map to `None`. Unknown directives, malformed
numeric values, and required numeric directives without values are ignored.

### CacheController decisions

```python
CacheController(
    cache: BaseCache | None = None,
    cache_etags: bool = True,
    serializer: Serializer | None = None,
    status_codes: Collection[int] | None = None,
)
cached_request(request: requests.PreparedRequest) -> urllib3.HTTPResponse | False
conditional_headers(request: requests.PreparedRequest) -> dict[str, str]
cache_response(
    request: requests.PreparedRequest,
    response_or_ref: urllib3.HTTPResponse | weakref.ReferenceType[urllib3.HTTPResponse],
    body: bytes | None = None,
    status_codes: Collection[int] | None = None,
) -> None
update_cached_response(
    request: requests.PreparedRequest,
    response: urllib3.HTTPResponse,
) -> urllib3.HTTPResponse
```

The default cache is `DictCache`; default cacheable statuses are 200, 203, 300,
301, and 308. A range request does not use a cached full response. Request
`no-cache` and `max-age=0` bypass cache lookup. Freshness uses response `Date`,
`Cache-Control: max-age`, `Expires`, and request `max-age`/`min-fresh`.
Permanent 301 and 308 responses remain cacheable when no explicit freshness
lifetime exists. Stale responses without an ETag are deleted. Missing or bad
dates do not produce fresh cached responses.

`conditional_headers` returns `If-None-Match` and/or `If-Modified-Since` from a
stored response. `cache_response` rejects unsupported statuses, partial or
wrong-length bodies, `no-store`, `Vary: *`, and responses that arrived stale.
An ETag response is retained for at least 14 days when ETag caching is enabled.
Positive `max-age`, future `Expires`, and permanent redirects are cached.

`update_cached_response` merges headers from a 304 response into the cached
response except `Content-Length`, changes its status to 200, stores it again,
and returns it. If no cached response exists, it returns the supplied response.

### Serialization

```python
Serializer.dumps(
    request: requests.PreparedRequest,
    response: urllib3.HTTPResponse,
    body: bytes | None = None,
) -> bytes
Serializer.loads(
    request: requests.PreparedRequest,
    data: bytes,
    body_file: IO[bytes] | None = None,
) -> urllib3.HTTPResponse | None
Serializer.serialize(data: dict[str, Any]) -> bytes
Serializer.prepare_response(request, cached, body_file=None) -> urllib3.HTTPResponse | None
```

The current format starts with `b"cc=4,"` and uses MessagePack. It preserves
body bytes, headers, status, version, reason, and `decode_content`. When
`dumps` receives no body, it reads the response without content decoding and
restores a readable in-memory body on that response. `Vary` request headers are
recorded. `loads` returns `None` for empty data, other format versions, invalid
MessagePack, `Vary: *`, or a Vary mismatch. A supplied `body_file` replaces the
inline body. A serialized chunked transfer header is removed on load.

### Heuristics

```python
expire_after(delta: datetime.timedelta, date: datetime | None = None) -> datetime
datetime_to_header(dt: datetime) -> str
BaseHeuristic.warning(response) -> str | None
BaseHeuristic.update_headers(response) -> dict[str, str]
BaseHeuristic.apply(response) -> response
OneDayCache()
ExpiresAfter(**timedelta_kwargs)
LastModified()
```

`BaseHeuristic.apply` merges `update_headers` into the response and adds the
warning returned by `warning` only when headers changed. `OneDayCache` adds a
one-day `Expires` and `Cache-Control: public` when `Expires` is absent.
`ExpiresAfter` applies the configured `timedelta` from the current UTC time and
emits its explanatory 110 warning. `LastModified` uses ten percent of the
`Date` minus `Last-Modified` interval, capped at 24 hours, only for statuses
cacheable by default and only when existing cache headers permit it. It does
not add a warning.

## Implementation Notes

Preserve case-insensitive HTTP header behavior by using the public
`requests`/`urllib3` types where appropriate. Keep raw body bytes unchanged,
and keep cache storage, expiration, serialization, and adapter ownership in
separate modules. Time-dependent methods must permit controlled clocks through
ordinary module patching; evaluation does not sleep or depend on the current
wall clock. Filesystem checks use a bounded temporary directory.

The separate verifier installs the candidate into an isolated site directory
and runs every observation as an unprivileged child process. It collects 27
fixed leaves. The task does not expose hidden assertions, reference source, or
trusted report paths.

Example:

```python
import io

from requests import Request
from urllib3 import HTTPResponse

from cachecontrol.cache import DictCache
from cachecontrol.controller import CacheController

request = Request("GET", "https://example.com/data").prepare()
response = HTTPResponse(
    body=io.BytesIO(b"value"),
    headers={"Date": "Wed, 21 Oct 2015 07:28:00 GMT", "Cache-Control": "max-age=60"},
    status=200,
    preload_content=False,
)

cache = DictCache()
controller = CacheController(cache=cache)
controller.cache_response(request, response, body=b"value")
assert request.url in cache.data
```
