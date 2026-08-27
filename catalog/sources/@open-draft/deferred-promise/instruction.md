# Project Description

Create a complete installable npm package named `@open-draft/deferred-promise`.
It must be an ESM package whose public root export is available after
`npm pack` and installation. The package provides two ways to control a native
Promise from a different scope:

- `createDeferredExecutor()` returns a Promise executor function with attached
  settlement controls.
- `DeferredPromise` is a Promise-compatible class that exposes those controls
  directly on the Promise instance.

Implement the package from an empty workspace. Do not depend on network access
at runtime. Keep the public package small and do not expose test-only helpers.

# Supports

- Node.js 24 ESM and npm package installation.
- A package root described by `package.json` with `type: "module"` and an
  `exports` entry for the built runtime.
- The package may be authored in TypeScript or JavaScript, but the packed
  package must contain runnable JavaScript and useful declaration files.
- The package must be installable with `npm ci --offline --ignore-scripts` when
  its lockfile and dependencies are present. It has no required runtime
  dependency; build tools are development-only.

# API Usage Guide

## `createDeferredExecutor`

Import `{ createDeferredExecutor }` from `@open-draft/deferred-promise`.

Signature: `createDeferredExecutor<Input = never, Output = Input>(): DeferredPromiseExecutor<Input, Output>`.

The returned callable has the normal Promise executor shape
`(resolve?, reject?) => void` and is passed to `new Promise(executor)`. Before
the Promise settles, its attached properties are:

- `state`: exactly `"pending"`, `"fulfilled"`, or `"rejected"`; it starts as
  `"pending"`.
- `resolve(value?)`: requests fulfillment. Calling it more than once, or after
  rejection, has no effect. A value is assimilated using normal Promise
  resolution, including native Promises and thenables.
- `reject(reason?)`: requests rejection. Calling it after settlement has no
  effect. The first reason is retained by `rejectionReason`.
- `result`: the first value supplied to `resolve`, when one was supplied.
- `rejectionReason`: the first rejection reason, including `undefined` when
  rejection had no argument.

Calling `resolve` or `reject` does not synchronously change `state`; the state
reflects the native Promise settlement timing. The returned Promise can be
awaited repeatedly and retains its settled value or reason.

## `DeferredPromise`

Import `{ DeferredPromise }` from `@open-draft/deferred-promise`.

Signature: `new DeferredPromise<Input, Output = Input>(executor?: Executor<Input> | null)`.

With no executor, construct a pending Promise and settle it later with
`promise.resolve(value?)` or `promise.reject(reason?)`. A non-null optional
executor receives the same deferred `resolve` and `reject` functions and may
settle the instance during construction. Exceptions thrown by that executor
reject the instance.

The instance is Promise-compatible: `await` works, and `.then`, `.catch`, and
`.finally` return ordinary Promise-compatible derived values. Chained
`then`/`catch` callbacks may return values, native Promises, or another
`DeferredPromise`; returned thenables are assimilated and rejection propagates
according to native Promise rules. A callback is invoked asynchronously after
settlement. The original Promise keeps its identity and value when a derived
chain is created.

`state` and `rejectionReason` have the same meaning as on the executor. The
`resolve` and `reject` controls remain available on derived promises and
continue to control the original deferred settlement source.

# Implementation Notes

Preserve native Promise semantics for one-shot settlement, microtask ordering,
thenable assimilation, callback exceptions, rejection recovery, and `finally`
cleanup. Keep the candidate boundary JSON-serializable: tests exercise values,
errors, and deterministic event traces rather than relying on in-process test
framework globals. The package root must expose both named exports and must not
require consumers to import internal source paths.
