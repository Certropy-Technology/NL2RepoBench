# Build `httpx`

Recreate the public behavior of the pinned `httpx` HTTP client library from an
empty workspace. The implementation must be an installable Python package with
both synchronous and asynchronous clients and the public request, response,
headers, cookies, query parameter, authentication, timeout, streaming, and
transport APIs exposed by the pinned revision.

## Supports

Use CPython 3.12 on Linux. Provide a standard PEP 517 build (`pyproject.toml` or
an equivalent supported build configuration) and keep runtime imports limited
to the package's declared dependencies. The evaluator installs the candidate
without network access and protects its test and verifier directories.

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
