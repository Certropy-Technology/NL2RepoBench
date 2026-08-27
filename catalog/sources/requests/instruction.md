# Build `requests`

Create a complete, installable Python project named `requests` from an empty
workspace. Reproduce the deterministic, offline HTTP-client behavior described
below for CPython 3.12. The evaluator never contacts a live service: request
transport is supplied by a local adapter, so the implementation must not need
network access after installation.

## Project Description

`requests` is a synchronous HTTP client with a small public surface for
building requests, preparing headers and bodies, managing sessions and cookies,
authenticating requests, and consuming responses. The package and import name
are both `requests` and its version must be `2.34.2`.

## Supports

- Support CPython 3.10+ and provide a standard PEP 517 build using
  `pyproject.toml` (or an equivalent supported build configuration).
- Use a package layout that installs the importable `requests` package.
- Declare the four runtime dependencies with compatible exact behavior:
  `charset-normalizer` (2 <= version < 4), `idna` (2.5 <= version < 4),
  `urllib3` (1.26 <= version < 3), and `certifi` (>= 2023.5.7).
- Include the Apache-2.0 license text and a short README with installation and
  ordinary `Session`/`Response` examples.
- The installed package must import without the private evaluator files being
  present and must not use subprocesses, filesystem state, or environment
  services for ordinary request construction and response handling.

## Public API

The following import paths and names are required.

### `requests`

Expose `request`, `get`, `options`, `head`, `post`, `put`, `patch`, `delete`,
`Session`, `Request`, `PreparedRequest`, `Response`, `HTTPError`,
`ConnectionError`, `Timeout`, `TooManyRedirects`, `RequestException`,
`JSONDecodeError`, `CaseInsensitiveDict`, `RequestsCookieJar`, `cookiejar_from_dict`,
`merge_cookies`, `SessionRedirectMixin`, `codes`, and `__version__`.

`request(method, url, **kwargs)` and the verb helpers accept standard Requests
arguments including `params`, `data`, `json`, `headers`, `cookies`, `files`,
`auth`, `timeout`, `allow_redirects`, `proxies`, `hooks`, `stream`, `verify`,
`cert`, and `context`. The verb helpers must route through a fresh `Session`.

### `requests.models`

`Request(method=None, url=None, headers=None, files=None, data=None, params=None,
json=None, hooks=None, **kwargs)` stores the user-level request. `prepare()`
returns a `PreparedRequest` containing normalized method, URL, headers, body,
hooks, and the original request state. `PreparedRequest` supports `prepare`,
`prepare_method`, `prepare_url`, `prepare_headers`, `prepare_body`,
`prepare_auth`, `prepare_cookies`, `prepare_hooks`, `copy`, and `path_url`.

`Response` exposes `status_code`, `headers`, `url`, `reason`, `encoding`,
`apparent_encoding`, `request`, `connection`, `history`, `cookies`, and
`_content`. Its public methods/properties include `content`, `text`, `json`,
`iter_content`, `iter_lines`, `raise_for_status`, `close`, `ok`,
`is_redirect`, `is_permanent_redirect`, `next`, and context-manager support.

### `requests.sessions`

`Session` is a context manager. It owns default headers, cookies, auth, hooks,
proxies, trust-environment settings, redirect limits, and mounted adapters.
Implement `prepare_request`, `request`, all verb helpers, `send`,
`merge_environment_settings`, `get_adapter`, `mount`, and `close`.

The evaluator injects a local `BaseAdapter` subclass into a session. `send()`
must pass a fully prepared request to that adapter and return its `Response`.
The adapter can return redirect responses; follow redirects deterministically,
preserve `Response.history`, and stop at the configured maximum with
`TooManyRedirects`. No real socket or DNS access is needed by the evaluated
path.

### `requests.structures`

`CaseInsensitiveDict` is a mutable mapping whose lookup, replacement, deletion,
equality, iteration, and `lower_items()` operations are case-insensitive while
preserving the last spelling used for display. `LookupDict` supports mapping
fallback lookup (unknown keys return `None`) and attribute-style access for
known status names.

### `requests.cookies`

`RequestsCookieJar` behaves as a mutable mapping and a `CookieJar`. Support
`set`, `get`, `keys`, `values`, `items`, `get_dict`, `copy`, `clear`, and normal
cookie-domain/path handling. `cookiejar_from_dict` creates a jar, and
`merge_cookies` merges dictionaries or jars without losing existing cookies.
Cookie headers must be attached when a prepared request is sent through a
session.

### `requests.auth`

`AuthBase`, `HTTPBasicAuth`, `HTTPProxyAuth`, and `HTTPDigestAuth` are importable.
For the evaluated path, basic auth must add an RFC 7617 `Authorization: Basic`
header to the prepared request and accept string or bytes credentials. Preserve
the normal equality behavior of basic-auth objects. Digest auth must remain
constructible and callable without breaking request preparation.

### `requests.utils` and `requests.status_codes`

Provide the normal utility behavior for `to_key_val_list`, `from_key_val_list`,
`parse_list_header`, `parse_dict_header`, `parse_header_links`, `iter_slices`,
`super_len`, `requote_uri`, `prepend_scheme_if_needed`, `urldefragauth`,
`get_auth_from_url`, `default_headers`, `default_user_agent`, and
`check_header_validity`. `requests.codes` must expose standard aliases such as
`ok`, `not_found`, `found`, and `too_many_requests` with their numeric values.

## API Usage Guide

### Request preparation

`Request("POST", "https://example.test/items", params={"q": "a b"},
json={"n": 2}, headers={"X-Trace": "yes"}).prepare()` must produce a URL with
encoded query parameters, a JSON body encoded as UTF-8, a suitable
`Content-Type`, and case-insensitive headers. Form data uses URL encoding; a
sequence of pairs preserves pair order and repeated keys. Fragments remain at
the end of the URL after query parameters. Invalid schemes, malformed URLs,
invalid header names/values, or conflicting body arguments raise the documented
Requests exception/value errors rather than silently producing a bad request.

### Responses

A response with byte content can be read repeatedly through `.content`; `.text`
uses the declared charset when present and otherwise a sensible encoding;
`.json()` decodes JSON and raises `JSONDecodeError` for invalid JSON.
`iter_content(chunk_size)` yields byte chunks and `iter_lines()` joins chunks
without losing line boundaries. `bool(response)` is equivalent to `.ok`.
`raise_for_status()` raises `HTTPError` for 4xx/5xx statuses and includes the
status and URL in its message.

### Sessions and local transports

Session-level headers, cookies, auth, and hooks merge with per-request values.
When a custom adapter returns a response, the response references the prepared
request and receives the session cookie jar. Response hooks run after sending
and may return a replacement response. `stream=False` eagerly consumes content;
`stream=True` leaves the response iterable until the caller closes it.
`Session.close()` closes all mounted adapters and later sends fail with the
normal closed-session behavior.

### Redirects

For a redirect response with a `Location` header, `Session` resolves relative
locations, records the prior response in `.history`, and follows GET/HEAD
redirects. For 301/302/303 redirects from POST, the follow-up request becomes
GET and its body/content headers are removed; 307/308 preserve method and body.
Fragments are not sent to the adapter. Redirects exceeding the configured
maximum raise `TooManyRedirects`.

## Implementation Notes

- The evaluator uses deterministic child-side adapters and never relies on
  wall-clock time, DNS, proxies, a live HTTP service, or external files.
- Keep trusted evaluator assets separate from the candidate package. Do not
  hard-code expected evaluator outputs or add a test-only import path.
- Preserve `functools.wraps`-style metadata for public callables where the
  upstream API exposes it, and preserve normal exception types and attributes.
- The fixed evaluator covers packaging/version, request and body preparation,
  case-insensitive headers, response decoding/iteration/status handling,
  sessions with local adapters, cookies, basic auth, hooks, redirects, and
  utility/status-code helpers. Implement the public contracts rather than a
  one-off mock that only handles the examples above.

Example:

```python
import requests

session = requests.Session()
request = requests.Request("GET", "https://example.test/items", params={"page": 2})
prepared = session.prepare_request(request)
assert prepared.path_url == "/items?page=2"
```
