# Build `koa`

## Project Description

Create a complete installable npm package named `koa`, compatible with Node
24.19.0 and npm 11.17.0. Koa is a small HTTP application framework: an
application owns an ordered async middleware stack, creates a request context
for each HTTP request, and turns the context into a native Node HTTP server
callback.

This is a repository-generation task. Start from an empty workspace and write
your own implementation. Do not copy the pinned upstream repository or its
tests. The evaluator runs deterministic in-process HTTP requests only; no
external service, browser, database, clock, or random value is required.

## Natural Language Instruction

Create `koa` from an empty workspace as a CommonJS package. Implement the
application class, ordered asynchronous middleware composition, request and
response context wrappers, HTTP response behavior, and root HTTP-error
exports described below. The implementation must be usable through
`require('koa')` without a build step.

The required capability groups are:

1. Application construction, configuration defaults, introspection, and
   middleware registration.
2. Promise-based middleware ordering, error propagation, double-`next()`
   protection, and native server callback creation.
3. Context, request, proxy, query, hostname, IP, subdomain, and state
   behavior for deterministic local HTTP requests.
4. Response headers, body serialization, status coupling, redirects,
   attachments, caching metadata, and HTTP errors.
5. Offline CommonJS packaging with the documented dependency closure and
   package root entry point.

Do not add an unrelated CLI, persistent server, browser integration, database,
or external network behavior. Preserve native Node HTTP semantics where the
API guide refers to them.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64/glibc.
- CommonJS package semantics. The package root must be importable with
  `require('koa')` and return the application class. `package.json` must have
  `name: "koa"`, a semver version, `main: "lib/application.js"`, and a valid
  lockfile with `lockfileVersion: 3`.
- The package must have no lifecycle hooks that execute candidate code during
  installation. The verifier runs `npm ci --offline --ignore-scripts` and
  packages the project with `npm pack --ignore-scripts`.
- Runtime dependencies must be declared in `package.json` and resolved by the
  committed lockfile. Do not use git/file/workspace dependencies, native
  addons, workspaces, registry overrides, or network access.
- Keep implementation files under the package exports and include all source
  needed by `require('koa')`. A build-only ESM wrapper is optional and is not
  part of the scored contract.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── lib/
│   ├── application.js
│   ├── context.js
│   ├── request.js
│   ├── response.js
│   └── http-errors.js
└── README.md
```

`package.json` must set `main` to `lib/application.js` and list the frozen
runtime dependencies. The CommonJS root export is the Koa application class;
its HTTP error helpers are properties of that export. The module split above
is a concrete minimum: request and response wrappers must remain separately
testable, while context and application coordinate their state. Do not place
tests, verifier code, generated bundles, or network configuration in the
published workspace.

## API Usage Guide

### Application class

`const Koa = require('koa')` returns the application class. It extends
`EventEmitter` and supports:

The public import path is `require('koa')`. For type-oriented documentation,
the equivalent notation is `import Koa from 'koa'`; the runtime package must
remain CommonJS and must not require an ESM loader.

```js
const app = new Koa({
  env: 'test',
  proxy: false,
  subdomainOffset: 2,
  proxyIpHeader: 'X-Forwarded-For',
  maxIpsCount: 0,
  keys: ['secret'],
  asyncLocalStorage: true,
})
```

The options are optional. `env` defaults to `NODE_ENV` or `development`;
`proxy` defaults to false; `subdomainOffset` defaults to 2;
`proxyIpHeader` defaults to `X-Forwarded-For`; and `maxIpsCount` defaults to
0, meaning all forwarded addresses. `keys` configures signed cookies.
`asyncLocalStorage: true` enables `app.currentContext` during a request.

The instance exposes `middleware` (an array), `context`, `request`, and
`response` prototypes. `toJSON()` and `inspect()` return an object containing
`subdomainOffset`, `proxy`, and `env`. The static `default` getter returns the
application class.

### Middleware and server callback

`app.use(fn)` requires a function, appends it to the middleware stack, and
returns the same application instance. Non-functions raise `TypeError`.

`app.callback()` returns a native Node HTTP request handler. Middleware has the
signature `async (ctx, next) => {}`. The composed stack runs in registration
order before the downstream middleware and in reverse order after it. The
handler creates a fresh context, runs middleware, and responds from `ctx.body`,
`ctx.status`, and response headers. A request with no body defaults to status
404; a string or Buffer is sent as-is; plain objects are JSON encoded.

`app.listen(...args)` is shorthand for creating an HTTP server from
`app.callback()` and calling `server.listen(...args)`.

### Context and request behavior

Each request receives `ctx`, with `ctx.app`, `ctx.request`, `ctx.response`,
`ctx.req`, `ctx.res`, `ctx.state` (a new object), and `ctx.originalUrl`.
`ctx.request` and `ctx.response` are wrappers around the native request and
response. The context delegates the documented request/response methods and
properties, including `ctx.method`, `ctx.url`, `ctx.path`, `ctx.querystring`,
`ctx.query`, `ctx.host`, `ctx.hostname`, `ctx.protocol`, `ctx.secure`,
`ctx.ip`, `ctx.ips`, `ctx.subdomains`, `ctx.get(field)`, `ctx.accepts(...)`,
`ctx.is(...)`, `ctx.status`, `ctx.message`, `ctx.body`, `ctx.type`,
`ctx.length`, `ctx.header`, `ctx.headers`, and `ctx.state`.

When `proxy` is false, protocol/host/IP use the direct socket and Host header.
When true, `X-Forwarded-Proto`, `X-Forwarded-Host`, and the configured IP
header are trusted. `maxIpsCount` limits the forwarded IP list from the right.
Subdomains are returned from the hostname before the final
`subdomainOffset` components, in nearest-to-furthest order.

### Response behavior

The response wrapper supports `set`, `append`, `get`, `has`, `remove`,
`redirect`, `attachment`, `vary`, `flushHeaders`, and the `status`, `message`,
`body`, `length`, `type`, `lastModified`, and `etag` accessors.

Setting a string body selects `text/plain; charset=utf-8` unless a type is
already present. Objects select JSON and are serialized by the application
when the response is sent. Buffers and streams are sent as binary data. A
null body produces an empty response (normally status 204); status codes in
the empty-status set remove the body. `ctx.redirect(url)` sets a 302 status
when needed, a Location header, and an HTML or plain-text body according to
the request's accepted types.

`ctx.throw(...)` creates and throws an HTTP error. The default error handler
emits the app `error` event, removes existing response headers, chooses the
error status, and exposes the error message only when the error is marked
exposable.

### Re-exported HTTP errors

The package root also exposes `createHttpError`, `HttpError`, and
`isHttpError` as properties of the exported application class. They must
remain usable without requiring consumers to import `http-errors` directly.

## Implementation Notes

- Use Node's native `http`, `stream`, `events`, and `async_hooks` APIs where
  appropriate. Middleware composition must correctly reject invalid entries
  and must not call `next()` twice.
- Keep request handling deterministic and local. Do not bind a fixed port;
  callers may use `app.listen(0)` or create a server from `callback()`.
- Preserve header case-insensitive behavior, query parsing, content-type
  detection, status/body coupling, and async context semantics.
- A clean checkout must install and package offline with the commands used by
  the verifier. Do not rely on a globally installed copy of Koa.

## Examples

```js
const Koa = require('koa');
const app = new Koa({env: 'test'});
app.use(async ctx => { ctx.body = 'ok'; });
const server = app.listen(0);
```

```js
const Koa = require('koa');
const app = new Koa();
app.use(async (ctx, next) => {
  ctx.state.started = true;
  await next();
  ctx.set('X-Order', 'outer');
});
app.use(async ctx => { ctx.body = {ready: ctx.state.started}; });
const handler = app.callback();
```

```js
const Koa = require('koa');
const app = new Koa({proxy: true});
app.use(async ctx => {
  ctx.status = 201;
  ctx.type = 'json';
  ctx.body = {host: ctx.hostname, secure: ctx.secure};
});
```

## Error Handling and Boundary Conditions

- `app.use` rejects non-functions with `TypeError`, and middleware that calls
  `next()` more than once must reject deterministically.
- Middleware runs before downstream code in registration order and resumes in
  reverse order. A rejected middleware promise reaches the application error
  handler and emits the `error` event once.
- Requests with no body default to 404. Null bodies and empty status codes
  suppress content; strings, buffers, streams, and plain objects use their
  documented response handling and headers.
- Proxy-derived protocol, host, and IP values are used only when `proxy` is
  enabled. Forwarded IP limits and subdomain ordering remain deterministic.
- Redirect and HTTP-error responses must remove unsafe prior headers and
  expose error text only when the error is marked exposable.
- Agent, candidate, verifier, Oracle, and controls run with NoNetwork. The
  package cannot resolve dependencies or contact services during installation
  or request handling.

