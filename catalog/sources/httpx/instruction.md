# Build `httpx`

Recreate the public behavior of the pinned `httpx` HTTP client library from an
empty workspace. The implementation must be an installable Python package with
both synchronous and asynchronous clients and the public request, response,
headers, cookies, query parameter, authentication, timeout, streaming, and
transport APIs exposed by the pinned revision.

## Project Description

Build an installable Python distribution named `httpx` from an empty
`workspace/`. It is a synchronous and asynchronous HTTP client library whose
core behavior is exercised through injected local transports. Implement
request construction, response decoding, client lifecycle, authentication,
redirects, streaming, hooks, and transport routing without requiring a live
HTTP server. Expose the documented `httpx` package rather than a command-only
replacement.

## Natural Language Instruction

Create the `httpx` package and build metadata. Implement the public `Client`,
`AsyncClient`, `Request`, `Response`, `Headers`, `Cookies`, `QueryParams`,
`MockTransport`, timeout, authentication, stream, and mount interfaces below.
Preserve method signatures, request/response types, header and cookie
ordering, body encoding, redirect history, and deterministic exception
behavior. Both sync and async paths must use an injected transport for scored
scenarios; do not add a network fallback or a service process.

The package must support `import httpx` and imports such as
`from httpx import Client, Response`. Keep sync and async context managers
independent, close owned transports exactly once, and leave caller-owned
request data unmodified.

## Supports

Use CPython 3.12 on Linux. Provide a standard PEP 517 build (`pyproject.toml` or
an equivalent supported build configuration) and keep runtime imports limited
to the package's declared dependencies. The evaluator installs the candidate
without network access and protects its test and verifier directories.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── httpx/
│   ├── __init__.py
│   ├── _client.py
│   ├── _models.py
│   ├── _transports/
│   │   ├── __init__.py
│   │   └── mock.py
│   ├── _auth.py
│   ├── _config.py
│   ├── _content.py
│   ├── _exceptions.py
│   └── _urls.py
└── README.md
```

The root package exports the public classes and helpers used below. Additional
modules are allowed only for a documented import path or a private helper
needed by that path. Do not create test, verifier, report, source-archive, or
network-service files in the generated workspace.

## API Usage Guide

- `httpx.Client` and `httpx.AsyncClient` send requests through an injected
  transport and provide request helpers (`get`, `post`, `put`, `patch`, `delete`,
  `head`, `options`, and `request`). Context managers close their transports;
  closed clients reject later requests.
- `httpx.MockTransport` accepts a synchronous or asynchronous request handler and
  returns its `Response` without contacting the network. Mounts route selected
  schemes/hosts to another transport.
- `httpx.Request` and `httpx.Response` preserve method, URL, headers, cookies,
  body/content, status code, reason phrase, extensions, and streaming behavior.
  Responses provide `.json()`, `.text`, `.content`, iterators, and
  `.raise_for_status()` with HTTP status exceptions.
- Client and per-request headers, query parameters, cookies, basic
  authentication, redirects, event hooks, and stream context managers follow
  the normal `httpx` semantics. All behavior exercised by the evaluator must
  remain deterministic with `MockTransport`.

The frozen evaluator slice contains 24 JSON-safe behavior cases covering sync
and async requests, body encoding, headers, query parameters, cookies,
redirects, authentication, hooks, streaming, mounts, status errors, and client
lifecycle. It has a fixed denominator of 24; collection errors or a different
number of effective cases invalidate the grading result.

## Implementation Notes

Do not depend on a live HTTP service, wall clock, DNS, or external files for
normal operation. Preserve public import paths and re-exports expected by
callers. Candidate code is installed and exercised by a separate verifier
process; verifier output is a JSON object with per-case `passed`, `failed`, or
`skipped` statuses and a numeric fixed-test pass-rate reward.

## Examples

```python
import httpx

transport = httpx.MockTransport(lambda request: httpx.Response(200, text="ok"))
with httpx.Client(transport=transport) as client:
    response = client.get("https://example.test/")
```

```python
request = httpx.Request("POST", "https://example.test/items", json={"a": 1})
assert request.method == "POST"
```

```python
response = httpx.Response(200, json={"ok": True})
assert response.json() == {"ok": True}
```

```python
async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
    response = await client.get("https://example.test/")
```

## Error Handling and Boundary Conditions

Invalid URLs, unsupported content encodings, closed clients, and transport
failures raise the corresponding public `httpx` exception classes. A response
with a non-success status raises only when `raise_for_status()` is called.
Streaming responses must be closed or consumed before their client closes;
request and response bodies are bytes at the transport boundary. Redirects
remain deterministic and preserve response history, while no DNS lookup,
socket, wall-clock dependency, or external file is permitted in scored use.
