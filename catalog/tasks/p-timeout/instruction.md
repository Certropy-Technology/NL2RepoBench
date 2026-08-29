# Build `p-timeout`

## Project Description

Create an installable npm package named `p-timeout`, version `7.0.1`, from an
empty workspace. The package decorates a promise-like input with a configurable
timeout while preserving input fulfillment and rejection, providing fallback
and cancellation behavior, and supporting `AbortSignal`.

The task scores the complete public runtime API with deterministic custom
timers and controlled promises. It does not require the upstream AVA suite,
lint configuration, TypeScript test runner, benchmark tooling, or development
dependencies. Do not copy upstream source or tests into the generated package.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must name version `7.0.1`, use `"type": "module"`, and expose
  a safe in-package ESM root entry with `index.js` as the default runtime entry
  and `index.d.ts` as its declaration entry.
- The root entry has a default export named `pTimeout` and a named class export
  `TimeoutError`.
- Include only `index.js` and `index.d.ts` in the package `files` list. Declare
  no runtime dependencies, development dependencies, npm scripts, lifecycle
  hooks, workspaces, native addons, custom loaders, or registry configuration.
- Include a version 3 `package-lock.json` consistent with the zero-dependency
  package. A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not use network access, browser globals, random values, or wall-clock
  polling to determine timeout outcomes.

## Bounded Execution Contract

The verifier never imports candidate code into its trusted test process. It
starts an unprivileged, resource-bounded child that imports the installed
package and constructs allowlisted promise, timer, cancellation, fallback, and
abort scenarios inside that child. Requests and responses are bounded JSON.

No source text, executable strings, user functions, native timer handles,
`AbortSignal` objects, errors, symbols, BigInts, cyclic values, custom
prototypes, or accessors cross this boundary. JSON values are recursively
composed of null, booleans, finite numbers, strings, arrays, and ordinary
objects. Native objects and callbacks are created only by the child-side
adapter.

## API Usage Guide

### `TimeoutError`

```ts
export class TimeoutError extends Error {
  readonly name: 'TimeoutError';
  constructor(message?: string, options?: ErrorOptions);
}
```

`TimeoutError` is an `Error` subclass whose `name` is always
`"TimeoutError"`. Its constructor preserves the normal `Error` message and
`options.cause` behavior.

### `pTimeout`

```ts
export type ClearablePromise<T> = Promise<T> & {
  clear(): void;
};

export type Options<ReturnType> = {
  milliseconds: number;
  fallback?: () => ReturnType | Promise<ReturnType>;
  message?: string | Error | false;
  customTimers?: {
    setTimeout: typeof globalThis.setTimeout;
    clearTimeout: typeof globalThis.clearTimeout;
  };
  signal?: AbortSignal;
};

export default function pTimeout<ValueType, ReturnType = ValueType>(
  input: PromiseLike<ValueType>,
  options: Options<ReturnType>,
): ClearablePromise<ValueType | ReturnType>;
```

The `message: false` overload also allows `undefined` in the fulfillment type.

`milliseconds` must be a positive number. Positive fractional values and
`Number.POSITIVE_INFINITY` are accepted; zero, negative values, `NaN`, other
infinities, non-numbers, and a missing value reject with `TypeError`.
`Number.POSITIVE_INFINITY` disables the timeout but still observes the input
and an optional abort signal.

If `input` settles first, adopt its fulfillment value or preserve its rejection.
The returned value is a real Promise with an idempotent `clear()` method.
Clearing disables the timeout without canceling or settling the input, so the
decorated promise later follows the input. Clear the timer after every terminal
path. Invoke supplied timer functions with an undefined receiver and pass the
configured millisecond value to `setTimeout`.

If the timeout wins:

- with no `fallback`, call `input.cancel()` once when that method exists;
- with no custom `message`, reject `TimeoutError` with
  `Promise timed out after {milliseconds} milliseconds`;
- with a string `message`, reject `TimeoutError` using that exact string,
  including an empty string;
- with an `Error` object, reject that same object;
- with `message: false`, fulfill with `undefined`;
- with `fallback`, call it once instead of canceling the input and adopt its
  returned value, returned promise, thrown error, or rejection.

An already-aborted signal rejects immediately using `signal.reason`; if that
reason is nullish, reject a `DOMException` named `AbortError`. Otherwise add one
abort listener with `{once: true}`. Remove the listener after input resolution,
input rejection, timeout, fallback settlement, or abort. Abort remains active
when `milliseconds` is `Number.POSITIVE_INFINITY`.

Example:

```js
import pTimeout, {TimeoutError} from 'p-timeout';

const input = new Promise(resolve => setTimeout(resolve, 100, 'done'));

try {
  await pTimeout(input, {milliseconds: 25});
} catch (error) {
  if (error instanceof TimeoutError) {
    console.log(error.message);
  }
}
```

## Implementation Notes

Settlement and cleanup must be single-shot. Late input settlement, late abort,
or a stale timer callback must not change an already settled result. Preserve
input and fallback error identity inside the process, do not swallow promise
rejections, and do not leave abort listeners or active timers after settlement.
The frozen verifier has 35 `node:test` leaves adapted from the pinned upstream
AVA and tsd suites; it replaces elapsed-time assertions with explicit custom
timer callbacks and controlled promises.
