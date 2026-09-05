# Project Description

Build an installable CommonJS Node.js package named `nock` from an empty workspace. The package mocks outgoing Node HTTP requests in process: callers define an expected origin, method, path, request data, and reply, then use ordinary `node:http` requests or native `fetch()` without contacting an external server.

The package must work on Node.js 24.19.0. Each evaluation scenario starts a fresh process and uses only loopback-free, synthetic origins. No request in the required behavior may need DNS, public networking, a browser, a database, a native addon, or an external service.

# Natural Language Instruction

Build `nock` as a complete CommonJS package from an empty workspace. Implement
the callable root, scope and interceptor matching, asynchronous HTTP and native
fetch interception, replies, lifecycle state, definitions, and network controls
described below. Preserve registration order and cardinality deterministically
without opening a listening socket or contacting an external service.

# Supports or Environment Configuration

- Package metadata with name `nock`, version `0.0.0-development`, license `MIT`, `main = "./index.js"`, and a CommonJS package-root export callable as `require('nock')(basePath, options?)`.
- npm 11.17.0 with a v3 `package-lock.json`. The repository must install using `npm ci --offline --ignore-scripts`, then pack and install as a regular npm tarball. Runtime dependencies are optional; a self-contained implementation with no dependencies is valid.
- JSON-compatible request bodies and replies, strings, regular expressions created by the caller, asynchronous reply functions, and Node `Error` objects where described below.
- Deterministic interception of `node:http` and native `fetch()` calls. HTTPS pass-through, proxying, recording, filesystem fixtures, and real network access are outside this task.

# Project Directory Structure

```text
workspace/
├── package.json       # CommonJS metadata and root export
├── package-lock.json  # npm lockfile version 3
├── index.js           # callable root and package-level methods
└── lib/
    ├── scope.js       # Scope chain and lifecycle methods
    ├── interceptor.js # request matching and replies
    └── intercept.js   # in-process request hooks
```

`main` must resolve `index.js`; `lib/` contains package-owned runtime modules.
Recorder/back fixtures, evaluation files, verifier assets, and restricted cache files
must not be placed in this project tree.

# API Usage Guide

Import path: the callable CommonJS package root.

```js
const nock = require('nock');
```

## Package root

```js
const nock = require('nock')
const scope = nock(basePath, options?)
```

`basePath` accepts an `http://` origin string or a regular expression. The returned `Scope` is isolated from unrelated origins and exposes the chainable methods below. Importing the package activates interception by default.

The package root also exposes `activate`, `isActive`, `isDone`, `pendingMocks`, `activeMocks`, `removeInterceptor`, `disableNetConnect`, `enableNetConnect`, `cleanAll`, `abortPendingRequests`, `load`, `loadDefs`, `define`, `emitter`, `recorder`, `restore`, and `back`. `recorder`, `back`, `load`, and `loadDefs` must be present with their ordinary public shapes, but recording and filesystem fixture behavior are not exercised. `define(definitions)` is exercised with JSON-compatible definitions and returns the created scopes.

## Defining interceptors

A scope exposes these method shorthands:

```js
scope.get(path, body?)
scope.post(path, body?)
scope.put(path, body?)
scope.head(path, body?)
scope.patch(path, body?)
scope.merge(path, body?)
scope.delete(path, body?)
scope.options(path, body?)
scope.intercept(path, method, body?, options?)
```

Each returns an `Interceptor`. Paths accept strings or regular expressions. A plain-object request body matches structurally after JSON decoding, independent of object key order. An unmatched request must not consume a different interceptor.

An interceptor supports:

```js
interceptor.query(matcher)
interceptor.matchHeader(name, matcher)
interceptor.basicAuth({ user, pass? })
interceptor.reply(statusCode?, body?, headers?)
interceptor.reply(replyFunction)
interceptor.reply(statusCode, bodyFunction, headers?)
interceptor.replyWithError(error)
interceptor.times(count)
interceptor.once()
interceptor.twice()
interceptor.thrice()
interceptor.optionally(flag = true)
```

`query()` accepts `true` to allow any query or an object whose decoded keys and values must match. Header names match case-insensitively. `basicAuth()` matches the corresponding Basic Authorization header.

## Replies

`reply()` returns the parent `Scope`. String replies remain strings. Plain objects are JSON encoded and receive an `application/json` content type unless explicitly overridden. Explicit headers are returned using case-insensitive HTTP semantics.

A body reply function receives `(uri, parsedBody)` and may return a body synchronously or through a Promise. A full reply function passed as the only argument to `reply()` may return `[statusCode, body, headers]`, synchronously or through a Promise. `replyWithError(error)` makes the request emit the supplied `Error`, preserving its message and custom `code`.

The following scope-level modifiers are chainable:

```js
scope.defaultReplyHeaders(headers)
scope.replyContentLength()
scope.replyDate(date?)
scope.persist(flag = true)
scope.matchHeader(name, matcher)
scope.filteringPath(regexp, replacement)
scope.filteringPath(function)
scope.filteringRequestBody(regexp, replacement)
scope.filteringRequestBody(function)
```

Default and interceptor-specific reply headers merge, with interceptor values taking precedence. `replyContentLength()` adds the byte length for ordinary string or Buffer replies. `replyDate(date)` emits the supplied date in HTTP-date form. Filtering transforms the observed path or request body before matcher comparison.

## Cardinality and state

An interceptor is required once by default. `times(n)`, `twice()`, and `thrice()` require the corresponding count. A persistent interceptor continues matching after its first use and remains active; once matched, it is considered done. An optional interceptor is considered done even when unused but remains active until removed.

Each `Scope` exposes:

```js
scope.done()
scope.isDone()
scope.pendingMocks()
scope.activeMocks()
```

`done()` throws an `AssertionError` when required mocks remain. `pendingMocks()` returns required unsatisfied mock keys; `activeMocks()` also includes optional and persistent active mocks. The package-root variants aggregate across scopes. `removeInterceptor(interceptorOrOptions)` returns whether one interceptor was removed, and `cleanAll()` removes every registered interceptor.

## Activation and network control

`isActive()` reports whether interception is installed. `restore()` deactivates it, and `activate()` reactivates it; activating an already active interceptor may throw rather than duplicating hooks. `disableNetConnect()` rejects unmatched requests with an `ENETUNREACH` error containing `Disallowed net connect`. `enableNetConnect()` restores unmatched-request pass-through, though the evaluator does not perform a real pass-through request.

## Definitions and transports

`define(definitions)` accepts objects containing `scope`, `method`, `path`, `status`, `response`, `rawHeaders`, and `options`, creates corresponding scopes, and returns them in input order. Definitions used here contain only JSON-compatible values.

Matching mocks must work for ordinary `node:http` requests and native `fetch()` calls. Request and reply completion must be asynchronous-safe and must not open a listening socket.

# Implementation Notes

Keep global interception state deterministic and cleanly removable. Match origin, method, path, query, headers, and body before consuming an interceptor. Preserve registration order when multiple active interceptors are candidates. Avoid external requests even for unmatched scenarios when network connections are disabled.

Streams, delays, `replyWithFile`, Unix sockets, TLS certificate behavior, live `allowUnmocked` pass-through, recorder output, and `nock.back` fixture modes are intentionally outside the evaluated contract. Do not copy the upstream source or tests; recreate the documented behavior from this specification.

# Examples

```js
const nock = require('nock');
const scope = nock('http://service.test').get('/health').reply(200, {ok: true});
scope.done();
```

```js
const scope = nock('http://service.test')
  .post('/items', {name: 'one'})
  .reply(201, 'created', {'x-result': 'ok'});
```

```js
nock.disableNetConnect();
nock.enableNetConnect();
```

# Error Handling and Boundary Conditions

- Required unused mocks make `done()` throw `AssertionError`.
- Header names match case-insensitively; mismatched origin, method, path,
  query, or body must not consume another interceptor.
- `activate()` must not duplicate hooks, and `cleanAll()` removes all mocks.
- Disabled unmatched connections fail locally with the documented network error
  and never fall through to DNS, loopback, proxy, or public network access.
