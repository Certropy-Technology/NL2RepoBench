# Build `requests-cache`

## Project Description

Implement an installable Python distribution named `requests-cache` whose import package is
`requests_cache`. It adds persistent and in-memory caching behavior to the `requests` HTTP client.
The task targets the deterministic local behavior of requests-cache 1.3.4 at the pinned upstream
revision. The implementation must be usable from an empty workspace and must not require a live
HTTP server for its core behavior.

## Supports

- CPython 3.12 on Linux.
- A Hatchling-based build that produces the `requests-cache` distribution and importable
  `requests_cache` package, including `py.typed`.
- The required runtime dependencies are `requests`, `urllib3`, `attrs`, `cattrs`, `platformdirs`,
  and `url-normalize`. The verifier provides the locked closure during image construction.
- Deterministic local operation without databases, Redis, MongoDB, DynamoDB, browser automation,
  external HTTP services, wall-clock assertions, or access to the upstream repository.

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
