# Build `requests-cache`

## Project Description

Implement an installable Python distribution named `requests-cache` whose import package is
`requests_cache`. It adds persistent and in-memory caching behavior to the `requests` HTTP client.
The task targets the deterministic local behavior of requests-cache 1.3.4 at the pinned upstream
revision. The implementation must be usable from an empty workspace and must not require a live
HTTP server for its core behavior.

## Natural Language Instruction

Create an installable `requests-cache` distribution from an empty
`workspace/`. Implement deterministic request normalization and cache-key
generation, expiration and cache-control policy, in-memory response storage,
serialized response models, cached sessions, and temporary `requests` patching.
Preserve the import paths, method signatures, copy semantics, ordering,
time-zone handling, and error contracts specified below. The scored project
uses local request adapters and must not turn a cache miss into a live request.

Provide the `requests_cache` package and its root re-exports. Keep cache keys,
policy, backends, models, serializers, session behavior, and patcher behavior
separate so settings and caller-owned requests are not mutated by another
operation.

## Supports

- CPython 3.12 on Linux.
- A Hatchling-based build that produces the `requests-cache` distribution and importable
  `requests_cache` package, including `py.typed`.
- The required runtime dependencies are `requests`, `urllib3`, `attrs`, `cattrs`, `platformdirs`,
  and `url-normalize`. The verifier provides the locked closure during image construction.
- Deterministic local operation without databases, Redis, MongoDB, DynamoDB, browser automation,
  external HTTP services, wall-clock assertions, or access to the upstream repository.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── requests_cache/
│   ├── __init__.py
│   ├── cache_keys.py
│   ├── session.py
│   ├── patcher.py
│   ├── policy/
│   │   ├── __init__.py
│   │   └── expiration.py
│   ├── backends/
│   │   ├── __init__.py
│   │   └── base.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py
│   │   └── response.py
│   └── serializers/
│       └── __init__.py
└── README.md
```

The root package and modules named in the API guide are public import paths.
Service backends, live HTTP fixtures, browser integrations, and test or
verifier files are outside the generated project.

## API Usage Guide

### Cache keys and normalization

Import these functions from `requests_cache.cache_keys` or the package root:

- `normalize_params(value, ignored_parameters=None) -> str` decodes query/form data, sorts pairs,
  preserves duplicate values, redacts named keys as `REDACTED`, and preserves key-only parameters.
- `normalize_url(url, ignored_parameters=None) -> str` normalizes a URL and applies the same query
  filtering. Scheme, host, port, path, and query normalization must be deterministic.
- `normalize_headers(headers, ignored_parameters=None) -> CaseInsensitiveDict` returns a
  case-insensitive mapping with filtered keys and normalized comma-separated values.
- `normalize_request(request, ignored_parameters=None, content_root_key=None)` returns a copy of a
  `requests.Request` or prepared request with method, URL, headers, and supported JSON/form bodies
  normalized. It must not mutate the caller's original request.
- `create_key(request, ignored_parameters=None, match_headers=False, serializer=None,
  content_root_key=None, **request_kwargs) -> str` returns a deterministic hexadecimal cache key.
  Equivalent normalized requests must produce equal keys; the request method, normalized content,
  TLS verification flag, selected headers, and serializer identity are part of the key.
- `filter_sort_dict`, `filter_sort_multidict`, `filter_sort_list`, `filter_url`, and
  `get_matched_headers` provide the corresponding deterministic filtering operations.

### Expiration policy

Import `get_expiration_datetime`, `get_expiration_seconds`, `get_url_expiration`, `add_tzinfo`,
and `utcnow` from `requests_cache.policy.expiration`. Expiration accepts `None` or `-1` for no
expiration, `0` for immediate expiration, a numeric number of seconds, a `timedelta`, a timezone-aware
`datetime`, or an RFC HTTP-date string. Relative values are added to `start_time` when supplied and
results are UTC-aware. Invalid HTTP dates raise `ValueError` unless the ignore option is enabled.
`get_url_expiration(url, patterns)` returns the first matching pattern's value and supports glob or
compiled regular-expression patterns.

### Cache settings and actions

`requests_cache.policy.CacheSettings` is an attrs-based settings object. It records expiration,
allowed status codes/methods, ignored parameters, header matching, read-only mode, stale-if-error,
and cache-control options. `CacheActions.from_request(cache_key, request, settings)` computes the
read/send/write decision for a prepared request. `set_request_headers(headers, expire_after,
only_if_cached, refresh, force_refresh)` returns a copy containing requests-cache directives.

### In-memory cache and response models

`requests_cache.backends.BaseCache`, `BaseStorage`, and `DictStorage` implement cache operations
without a remote service. `BaseCache` supports `get_response`, `save_response`, `contains`, `delete`,
`filter`, `clear`, `reset_expiration`, `update`, and `urls`; its `responses` and `redirects` mappings
are dict-like. `CachedResponse.from_response(response, expires=None)` wraps a `requests.Response`
and preserves status, URL, headers, body, request, cache key, and expiration metadata. Cached and
original responses expose `from_cache` appropriately. `format_datetime` and `format_file_size`
return stable display strings.

### Serialization

`requests_cache.serializers.init_serializer(serializer, decode_content)` accepts a named serializer
or a `Stage`/`SerializerPipeline` instance. The built-in `pickle`, `json`, `yaml`, `ujson`, and
`orjson` names must be exposed; optional serializers may fail at initialization when their optional
library is absent. A pipeline must provide `dumps` and `loads`, preserve response metadata, and
respect the `decode_content` setting.

### Cached sessions and patching

`requests_cache.CachedSession` extends `requests.Session`. Its `get`, `post`, `put`, `patch`,
`delete`, `head`, `options`, `request`, and `send` methods apply cache policy. With an adapter that
returns local `requests.Response` objects, the first request is an origin response and a repeated
equivalent request is returned from the cache. `only_if_cached` returns a 504 response on a miss;
`cache_disabled()` temporarily bypasses cache reads/writes. `close()` closes the configured backend.

`install_cache`, `uninstall_cache`, `enabled`, `disabled`, `get_cache`, `is_installed`, `clear`, and
`delete` from `requests_cache.patcher` temporarily or permanently patch the `requests.Session`
factory. Context managers restore the previous factory even when their body raises.

## Implementation Notes

Keep the package's public import paths and re-exports compatible with the documented modules.
Separate the request normalization, policy, backend, model, serializer, session, and patcher layers
so that changing one does not mutate shared settings or caller-owned request objects. Treat cache
keys and serialized response content as deterministic data. Optional database backends may be
present as importable placeholder classes, but they are outside the scored contract and must not
be required to import the core package. Do not contact the network from library code during the
local scenarios.

## Examples

```python
from requests_cache import CachedSession

session = CachedSession(backend="memory")
# A local adapter supplies the origin response for this URL in scored use.
response = session.get("https://example.invalid/data")
```

A repeated equivalent request uses the cached response and exposes
`response.from_cache` without changing the response body or request method.

```python
from requests_cache.cache_keys import normalize_url, create_key

normalized = normalize_url("https://example.test/items?b=2&a=1")
key = create_key(request)
```

Equivalent query pairs normalize deterministically, while a changed method or
selected header produces a different key when header matching is enabled.

## Error Handling and Boundary Conditions

- `None` and `-1` expiration mean no expiry; `0` expires immediately, and
  invalid HTTP-date strings raise `ValueError` unless the documented ignore
  option is enabled.
- Normalization preserves duplicate query values and key-only parameters,
  redacts configured keys, and never mutates a caller's request.
- A cache miss with `only_if_cached` returns a local 504 response. Optional
  Redis, MongoDB, DynamoDB, and GridFS integrations are not required for the
  in-memory core and must not be imported to use it.
- Context managers restore patched session factories even when their body
  raises; `close()` releases the configured local backend.
