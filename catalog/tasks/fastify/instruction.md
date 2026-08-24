# Project Description

Build an installable Node.js package named `fastify` from an empty workspace. It is a CommonJS HTTP application framework: callers create an isolated application, register routes and hooks, and exercise it without binding a network port through an injection API.

The package must expose the framework factory from the package root (`require('fastify')`) and must work with Node.js 24.19.0. The evaluator starts a fresh candidate process for every scenario and communicates only with JSON-serializable values. Do not require a network connection, native addon, browser, database, or external service.

# Supports

- Node.js 24.19.0 and npm 11.17.0.
- CommonJS package metadata with package name `fastify`, version `6.0.0-alpha.2`, and a root entry that exports the callable factory.
- Runtime dependencies may be declared in `package.json`, but the package must install with `npm ci --offline --ignore-scripts` from a v3 `package-lock.json`. Do not use lifecycle scripts, workspaces, git dependencies, file dependencies, or native addons.
- All request bodies, route options, handler results, and responses used by this task are JSON-compatible values. A handler may be synchronous or return a Promise.

# API Usage Guide

## `require('fastify')(options?)`

Return a new application object. Each application starts with no user routes. The `logger: false` option is supported by the scenarios. The returned object must expose the methods below and preserve chainability where stated.

## Route registration

Support the shorthand methods `get(path, [options], handler)`, `post(path, [options], handler)`, `put(path, [options], handler)`, `delete(path, [options], handler)`, and the generic `route({ method, url, handler, schema?, preHandler? })`. Paths may contain named parameters such as `/users/:id`, a terminal wildcard such as `/files/*`, and a static prefix supplied by plugin registration. Route registration returns the same application object.

Handlers receive `(request, reply)`. `request.params`, `request.query`, `request.body`, and `request.headers` are JSON-readable objects. A handler may return a JSON value, call `reply.send(value)`, set a status with `reply.code(statusCode)`, or set a response header with `reply.header(name, value)`. `reply.code` and `reply.header` return the reply object.

## `inject(request)`

Execute a request without opening a listening socket. The request object includes `method`, `url` or `path`, optional `payload`, and optional `headers`. Return a Promise resolving to a response object exposing JSON-readable `statusCode`, `headers`, and `body`, plus a `json()` method whose result is the parsed JSON body when the body is JSON. Injection must wait for registered routes and hooks to be ready.

## Hooks

Support `addHook(name, fn)` for `onRequest`, `preParsing`, `preValidation`, `preHandler`, `onSend`, and `onResponse`. Hooks may use callback style `(request, reply, done)` or return a Promise. They run in registration order for the request lifecycle. A hook can set a reply status/header or call `done(error)`; an error enters the configured error handler.

## JSON schema validation

Route options may contain `schema: { querystring?, params?, body?, response? }`. Validate the request against the JSON Schema subset needed by ordinary object/string/integer/number/boolean/null values, including `type`, `required`, `properties`, `additionalProperties`, `items`, `minimum`, `maximum`, `minLength`, `maxLength`, `pattern`, and `enum`. Invalid input returns status `400` with a JSON error body. A response schema may serialize or validate the handler result; valid response values remain JSON-readable.

## Errors and not-found handling

`setErrorHandler(handler)` installs the application error handler and returns the application. The handler receives `(error, request, reply)` and may return a JSON value or use `reply.code`/`reply.send`. `setNotFoundHandler(handler)` installs the handler for unmatched routes and returns the application. Without a custom handler, unmatched routes return status `404`.

## Plugins and encapsulation

`register(plugin, options?)` accepts a plugin function `(instance, options, done)` or an async plugin. The plugin may register routes, hooks, and decorators on its instance. `prefix` in the registration options prefixes routes declared by that plugin. Plugin-local hooks and decorators affect the plugin scope and its descendants without unexpectedly changing sibling scopes. Registration returns the application object.

## Introspection and lifecycle

`hasRoute({ method, url })` returns a boolean for a registered route. `ready()` returns a Promise that resolves after registration completes. `close()` returns a Promise and releases application resources. These calls must be safe for the in-memory injection scenarios.

# Implementation Notes

Keep the implementation modular and installable from the empty workspace. Route matching must be deterministic: static paths take precedence over parameters, parameters over wildcards, and registration order breaks ties. Preserve HTTP method semantics and normalize JSON response bodies consistently. The evaluator does not require `listen()` or real sockets, so those may be implemented minimally, but `inject()` must not depend on external networking.

Do not copy the upstream source or tests. Recreate the documented behavior from the contract, including error paths, empty and Unicode JSON values, hook ordering, route prefixes, and package installation metadata.
