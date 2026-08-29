# Build `p-retry`

## Project Description

Recreate the `p-retry` npm package at version `8.0.0`. The package repeatedly
invokes a synchronous, promise-returning, or async operation under a bounded
retry policy. It supports callback-controlled retry consumption, exponential
backoff, elapsed-time limits, cancellation, explicit abort errors, and wrappers
that make ordinary functions retriable.

Work in `/workspace`. Produce a complete, installable npm package; do not fetch
the reference implementation or any dependency. The evaluation environment is
offline and provides only the declared locked dependency through a private npm
cache.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must name `p-retry` version `8.0.0`, use `"type": "module"`,
  set `"sideEffects": false`, require Node `>=22`, and expose a safe
  in-package ESM root entry plus its TypeScript declaration entry.
- The root entry exports default `pRetry`, named `AbortError`, and named
  `makeRetriable`.
- Declare `is-network-error` as the sole runtime dependency, pinned to `1.3.2`
  in a v3 `package-lock.json`. Declare no npm scripts, development
  dependencies, workspaces, lifecycle hooks, native addons, or custom loaders.
- A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not use network access, registry configuration, random global state, or
  source-host access to implement or install the package. Runtime calls may
  classify a supplied network-shaped `TypeError`; they do not need live
  network access.

## API Usage Guide

### `pRetry`

```ts
export type RetryContext = {
  readonly error: Error;
  readonly attemptNumber: number;
  readonly retriesLeft: number;
  readonly retriesConsumed: number;
  readonly retryDelay: number;
};

export type Options = {
  readonly onFailedAttempt?: (context: RetryContext) => void | Promise<void>;
  readonly shouldRetry?: (context: RetryContext) => boolean | Promise<boolean>;
  readonly shouldConsumeRetry?: (context: RetryContext) => boolean | Promise<boolean>;
  readonly retries?: number;
  readonly factor?: number;
  readonly minTimeout?: number;
  readonly maxTimeout?: number;
  readonly randomize?: boolean;
  readonly maxRetryTime?: number;
  readonly signal?: AbortSignal;
  readonly unref?: boolean;
};

export default function pRetry<T>(
  input: (attemptNumber: number) => PromiseLike<T> | T,
  options?: Options
): Promise<T>;
```

Invoke `input` immediately with one-based attempt numbers. Adopt synchronous
values and promises into the returned promise. The defaults are `retries: 10`,
`factor: 2`, `minTimeout: 1000`, `maxTimeout: Infinity`,
`maxRetryTime: Infinity`, and `randomize: false`. Callback defaults accept and
consume each eligible retry.

`retries` is a non-negative number or positive infinity; it counts retries
after the first attempt. Reject negative values, non-numbers, and `NaN` with
`TypeError`. The removed `forever` option must reject with an explanatory
error. Callback options must be functions when supplied.

Normalize a non-`Error` throw or rejection to a descriptive `TypeError`.
Ordinary `TypeError` instances are treated as programming errors and are not
retried. A `TypeError` recognized by `is-network-error` remains eligible for
retry. Preserve the final eligible error when the budget or policy stops.

For an eligible failure, compute a frozen context. `attemptNumber` starts at
one, `retriesConsumed` starts at zero, and finite `retriesLeft` never becomes
negative. Callback order is:

1. `shouldConsumeRetry(context)`;
2. `onFailedAttempt(context)` with the effective delay;
3. terminal budget, type, and elapsed-time checks;
4. `shouldRetry(context)`.

If `shouldConsumeRetry` returns false, do not decrement the retry budget, do
not advance the backoff, and report `retryDelay: 0`; `shouldRetry` may still
allow the next attempt. `onFailedAttempt` runs for the final ordinary failure,
with `retryDelay: 0`, but `shouldRetry` does not run after a terminal budget or
non-network `TypeError` check. Await every callback. A callback error aborts
with that callback error.

The uncapped delay for a consumed retry is:

```text
round((randomize ? Math.random() + 1 : 1)
      * minTimeout
      * factor ** retriesConsumed)
```

Cap it at `maxTimeout`. Treat a non-positive finite `factor` as `1`.
`minTimeout` and `factor` must be non-negative finite numbers;
`maxTimeout` and `maxRetryTime` may also be positive infinity. The total
`maxRetryTime` starts when `pRetry` is called, uses a monotonic clock, includes
operation and callback time, and can shorten or eliminate the next delay.

When `signal` is already aborted, reject with its reason before invoking
`input`. When it aborts during input or delay, reject with its reason and stop
further attempts. With `unref: true`, call `unref()` on timeout tokens when the
runtime supplies that method.

Example:

```js
import pRetry from 'p-retry';

let remainingFailures = 2;
const value = await pRetry(attemptNumber => {
  if (remainingFailures-- > 0) {
    throw new Error(`attempt ${attemptNumber}`);
  }

  return 'ready';
}, {retries: 2, minTimeout: 0});
```

### `AbortError`

```ts
export class AbortError extends Error {
  readonly name: 'AbortError';
  readonly originalError: Error;
  constructor(message: string | Error);
}
```

Constructing from a string creates an `Error` with that message as
`originalError`; constructing from an `Error` preserves the same object.
Throwing `AbortError` from `input` stops immediately, skips all failure
callbacks, and rejects `pRetry` with `originalError`, not the wrapper.

### `makeRetriable`

```ts
export function makeRetriable<Arguments extends readonly unknown[], Result>(
  function_: (...arguments_: Arguments) => PromiseLike<Result> | Result,
  options?: Options
): (...arguments_: Arguments) => Promise<Result>;
```

Return a function that applies the same retry semantics independently on every
call. Forward all arguments unchanged and preserve the dynamic `this` value.

## Bounded Execution Contract

The verifier never imports candidate code into its trusted process. It starts
an unprivileged, resource-bounded child that imports the installed package and
constructs allowlisted retry scenarios inside that child. Requests and
responses are bounded JSON objects. No source text, executable strings,
callbacks, functions, symbols, cyclic values, accessors, or custom prototypes
cross the process boundary.

The child creates only controlled synchronous/async results, ordinary and
network-shaped errors, named callback policies, deterministic timer tokens,
bounded abort signals, and JSON-safe argument lists described by this public
contract.

## Implementation Notes

You may organize internal modules freely, but keep all exports inside the
package and preserve ordinary ESM loading. The frozen verifier has 46
deterministic `node:test` leaves derived from the core behavior of the pinned
70-leaf upstream suite. It replaces long real-time waits with controlled timer
tokens and excludes lint configuration, exact stack formatting, broad
platform timing tolerances, benchmark tooling, and TypeScript inference checks
beyond the declared public signatures. These omissions define the benchmark
boundary and do not imply full upstream parity.
