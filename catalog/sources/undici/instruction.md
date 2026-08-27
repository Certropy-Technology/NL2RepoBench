# Build `undici`

## Project Description

Create an installable npm package named `undici`, version `8.10.0`, from an
empty workspace. It is a CommonJS HTTP client for Node.js. The scored contract
is a deterministic, subprocess-safe slice of the public API. Implement the
behavior yourself; do not copy the pinned upstream repository or its tests.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` with glibc.
- The package root must be named `undici`, version `8.10.0`, and use the
  CommonJS entry `index.js`. The root must include `index.d.ts` and expose the
  runtime API from `require('undici')`.
- Include a committed npm v3 `package-lock.json`. A clean verifier runs
  `npm ci --offline --ignore-scripts --no-audit --no-fund` and then packs the
  package. Do not declare runtime dependencies.
- Do not use native addons, workspaces, registry configuration, lifecycle
  scripts, external services, clocks, random values, or environment-dependent
  output in the scored API.
- HTTP tests use a server bound to `127.0.0.1` inside the verifier process.
  External network access is unavailable and must not be required.

## API Usage Guide

### Package exports

`require('undici')` returns an object containing these value exports:

```text
Agent BalancedPool Client CloseEvent DecoratorHandler Dispatcher
Dispatcher1Wrapper EnvHttpProxyAgent ErrorEvent EventSource FormData
H2CClient Headers MessageEvent MockAgent MockCallHistory MockCallHistoryLog
MockClient MockPool Pool ProxyAgent RedirectHandler Request Response RetryAgent
RetryHandler RoundRobinPool SnapshotAgent Socks5ProxyAgent WebSocket
WebSocketError WebSocketStream buildConnector cacheStores caches connect
deleteCookie errors fetch getCookies getGlobalDispatcher getGlobalOrigin
getSetCookies install interceptors mockErrors parseCookie parseMIMEType ping
pipeline request serializeAMimeType setCookie setGlobalDispatcher
setGlobalOrigin stream upgrade util
```

The package must also expose the documented CommonJS default-style surface:
`require('undici').fetch`, `.request`, `.Headers`, `.Request`, `.Response`,
`.MockAgent`, `.Agent`, `.Dispatcher`, `.Pool`, `.setGlobalDispatcher`, and
`.getGlobalDispatcher` are callable or constructible values of the expected
kind. Type declarations must be present at `index.d.ts` and describe the
public exports sufficiently for consumers to import the above core values.

### `fetch`

`fetch(input, init?)` returns a Promise of a Response. `input` is an HTTP URL
string or URL object. `init` may contain `method`, `headers`, `body`, and
`dispatcher`. The method defaults to `GET`; a string body is sent unchanged.
The response exposes `status`, `ok`, `url`, `headers`, `text()`, `json()`, and
`clone()`. Redirect responses are followed by default. A response body can be
consumed once; a second consumption rejects with a TypeError-like error.

The scored behavior includes JSON response decoding, request headers and
method/body forwarding, status handling, relative redirects, and an
AbortController cancellation before a delayed response completes.

### `request`

`request(url, options?)` returns a Promise with `statusCode`, `headers`,
`trailers`, and a readable `body`. The body supports the async methods
`text()` and `json()` used by the contract. `options.method`, `options.headers`,
and `options.body` are supported. A URL query string is preserved in the
server request path. Invalid URLs reject with an Undici invalid-argument error
or another ordinary Error rather than silently making a request.

### Web API classes

`new Headers(init)` accepts a record or sequence of name/value pairs. Header
names are case-insensitive, names are lowercased for iteration, surrounding
HTTP whitespace is trimmed, `append` combines values with `, `, `set` replaces
the value, `delete` removes it, and `has`/`get` report the current state.

`new Request(url, init?)` stores the URL, method, headers, and optional body.
`new Response(body?, init?)` stores status, headers, and a readable body;
`ok` is true for 2xx statuses. `clone()` creates an independently readable
copy. The JSON boundary only uses string bodies and JSON-compatible results.

### Dispatchers

`new Dispatcher()` is an abstract base: calling its unimplemented `dispatch`,
`close`, or `destroy` methods raises an Error. `compose` returns a dispatcher
with the dispatcher methods. `new Agent()` and `new Pool(origin)` are usable
dispatchers for the local HTTP server. `setGlobalDispatcher` changes the
dispatcher used by later `fetch` calls and `getGlobalDispatcher` returns it.

### `MockAgent`

`new MockAgent()` creates a deterministic dispatcher without network access.
`disableNetConnect()` rejects unmatched requests. `mockAgent.get(origin)`
returns a mock pool; `.intercept({path, method}).reply(status, body, headers?)`
registers a response. A fetch using `{dispatcher: mockAgent}` receives that
response. `pendingInterceptors()` reports registered-but-unused interceptors,
and `assertNoPendingInterceptors()` succeeds after all expected calls.

### Utility exports

`parseCookie` parses a simple `name=value` cookie and attributes; `setCookie`
adds a cookie to a Headers object and `getCookies` reads request cookies.
`parseMIMEType` parses a type and parameters and
`serializeAMimeType` serializes that parsed representation. `util.headerNameToString`
returns a string header name and `util.parseHeaders` parses a CRLF header block.
The functions must return JSON-safe values for the inputs used by the tests.

### `install`

`install()` installs the package's `fetch`, `Headers`, `Request`, `Response`,
`FormData`, and WebSocket-related constructors onto `globalThis`. The scored
check only verifies the fetch and core Web API globals and their identity with
the exported implementations.

## Implementation Notes

- Preserve HTTP status codes, URL paths, header semantics, and response body
  text exactly. JSON output from the verifier is only a transport boundary;
  it is not an additional CLI requirement for the package.
- Keep candidate code in the package itself. The verifier imports the packed
  package in an unprivileged child process and never imports candidate modules
  into trusted test code.
- The private tests use fixed local ports selected at runtime, so do not hard
  code a port. Handle ordinary connection cleanup so a completed call does not
  keep the process alive.
- Unsupported advanced protocols such as HTTP/2, WebSocket, EventSource,
  proxy agents, SQLite cache storage, TLS certificates, and native parsers are
  outside this deterministic slice. Their names remain part of the export
  inventory where practical, but no external service or native implementation
  is required.
