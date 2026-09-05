# Build `urllib3`

Create an installable Python package named `urllib3` from an empty workspace. The
implementation must run on CPython 3.12 on Debian 12 amd64, use only the Python
standard library at runtime, and must not contact any network service during
evaluation.

## Project Description

`urllib3` is a reusable HTTP client library. This task covers its deterministic
local library behavior: URL decomposition, HTTP header collections, request
metadata, timeout and retry policy objects, multipart field encoding, response
body decoding, warning helpers, and the package's public re-exports. Socket
connections, TLS handshakes, proxy servers, HTTP/2 transports, browser APIs,
and external network I/O are outside this bounded contract.

## Natural Language Instruction

Create the installable `urllib3` package from an empty workspace. Implement
the deterministic URL, header, multipart, retry, timeout, response, warning,
and public re-export behavior below. Keep all transport and external I/O out of
the local contract.

## Supports

- `pip install .` from a clean workspace and normal imports of `urllib3`.
- Python 3.10+ compatible code; the evaluation runtime is CPython 3.12.
- The public package imports and modules `urllib3`, `urllib3._collections`,
  `urllib3.exceptions`, `urllib3.fields`, `urllib3.filepost`,
  `urllib3.response`, `urllib3.util`, `urllib3.util.request`,
  `urllib3.util.retry`, `urllib3.util.timeout`, and `urllib3.util.url`.
- JSON-compatible inputs and deterministic return values for the APIs below.
  Do not add a network client, subprocess dependency, generated endpoint, or
  task-specific test hook.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── urllib3/
    ├── __init__.py
    ├── _collections.py
    ├── exceptions.py
    ├── fields.py
    ├── filepost.py
    ├── response.py
    └── util/
        ├── __init__.py
        ├── retry.py
        ├── timeout.py
        └── url.py
```

## API Usage Guide

### Package exports

`urllib3.__version__` is a string version. The package root re-exports
`HTTPConnectionPool`, `HTTPSConnectionPool`, `HTTPHeaderDict`, `PoolManager`,
`ProxyManager`, `HTTPResponse`, `Retry`, `Timeout`, `BaseHTTPResponse`,
`connection_from_url`, `proxy_from_url`, `encode_multipart_formdata`,
`make_headers`, `request`, `add_stderr_logger`, and `disable_warnings`.

### URL parsing

`urllib3.util.parse_url(url: str) -> Url` decomposes an HTTP URL into the
named fields `scheme`, `auth`, `host`, `port`, `path`, `query`, and `fragment`.
It normalizes the scheme and host as specified by the URL grammar, preserves
path/query text, handles userinfo and IPv6 bracket notation, and raises the
documented URL exception for malformed ports or invalid URLs. `Url` is
immutable and its `url` property reconstructs a canonical URL.

### Header collections

`urllib3._collections.HTTPHeaderDict(headers=None, **kwargs)` is a
case-insensitive, insertion-ordered mapping of HTTP header names to values.
`add(key, value, combine=False)` preserves repeated values; with `combine=True`
it joins compatible values using ``, ``. `getlist(key)` returns all values,
`items()` exposes merged pairs, `iteritems()` exposes each pair, `copy()`
returns an independent collection, and normal mapping operations are
case-insensitive.

### Request metadata and multipart fields

`urllib3.util.make_headers(...) -> dict[str, str]` builds deterministic request
headers for keep-alive, accepted encodings, user agent, basic authentication,
proxy authentication, and cache disabling. Authentication values are encoded
with the requested encoding and represented using HTTP Basic authentication.

`urllib3.fields.guess_content_type(filename, default=...) -> str` returns a
standard MIME type based on a filename, or the supplied default when unknown.
`RequestField(name, data, filename=None, headers=None)` models one multipart
field. `make_multipart(content_disposition=None, content_type=None,
content_location=None)` sets its multipart headers and `render_headers()`
returns deterministic CRLF-terminated header text.

`urllib3.filepost.encode_multipart_formdata(fields, boundary=None)` returns
`(body: bytes, content_type: str)`. It encodes scalar and file fields with a
deterministic boundary when one is supplied and includes the required closing
delimiter.

### Retry and timeout policy

`urllib3.util.retry.Retry(...)` is an immutable retry policy. `Retry.from_int`
normalizes booleans and integers, `new(**changes)` returns a modified policy,
`is_retry(method, status_code, has_retry_after=False)` applies method and status
rules, `get_backoff_time()` computes exponential backoff from history, and
`increment(...)` returns the next policy or raises the documented max-retry
exception. Retry history is preserved in order.

`urllib3.util.timeout.Timeout(total=None, connect=_TYPE_DEFAULT, read=_TYPE_DEFAULT)`
stores total/connect/read budgets. `Timeout.from_float(value)` creates equal
connect and read budgets, `clone()` makes an independent policy, and
`start_connect()` / `get_connect_duration()` expose bounded elapsed-connect
behavior. Invalid negative or non-numeric values raise the documented error.

### Response decoding

`urllib3.response.HTTPResponse` accepts a file-like body and metadata. Its
`data`/`read()` behavior, `stream()`, `read_chunked()`, `decode_content`,
`getheaders()`, `getheader()`, `json()`, `drain_conn()`, and `close()` methods
must preserve deterministic body, header, and state behavior for in-memory
responses. Content decoding must honor the declared content encoding and must
not silently change bytes when decoding is disabled.

### Exceptions and warning helpers

The exception classes in `urllib3.exceptions` retain their documented
inheritance relationships and useful string representations. `disable_warnings`
changes the standard warning filter for urllib3 warning classes without
performing I/O.

## Examples

```python
from urllib3.util import parse_url

assert parse_url("https://example.test/a?q=1").host == "example.test"
```

```python
from urllib3._collections import HTTPHeaderDict

headers = HTTPHeaderDict()
headers.add("X-Test", "one")
assert headers.getlist("x-test") == ["one"]
```

## Error Handling and Boundary Conditions

Malformed URLs and invalid retry or timeout values raise the documented
exceptions. Header lookup is case-insensitive while preserving insertion
order. Response decoding never changes bytes when disabled, and no helper may
open sockets or contact a network service.

## Implementation Notes

Keep public imports and signatures compatible with the described API. Preserve
ordering, immutability/copy semantics, exact bytes and CRLF framing, exception
types, and deterministic version/export behavior. Optional compression,
SOCKS, HTTP/2, TLS, socket transport, and real-server integration are not
required by this task and should not be used to justify network access.

The verifier uses a separate UID-isolated subprocess for every candidate API
observation. The hidden contract contains 32 deterministic leaf scenarios; it
does not expose unpublished tests, the reference implementation, or scoring
files. Do not read hidden paths or write verifier-owned reports.
