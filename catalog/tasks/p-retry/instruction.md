# p-retry

## Project Description

Build an installable `p-retry` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `p-retry`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `pRetry`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `AbortError`: preserve the documented object or module behavior, including state and side effects.
3. `makeRetriable`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Bounded Execution Contract`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `p-retry`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- Declared build/runtime packages are supplied by the frozen evaluation image: `is-network-error==1.3.2`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

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


You may organize internal modules freely, but keep all exports inside the
package and preserve ordinary ESM loading. The frozen verifier has 46
deterministic `node:test` leaves derived from the core behavior of the pinned
70-leaf upstream suite. It replaces long real-time waits with controlled timer
tokens and excludes lint configuration, exact stack formatting, broad
platform timing tolerances, benchmark tooling, and TypeScript inference checks
beyond the declared public signatures. These omissions define the benchmark
boundary and do not imply full upstream parity.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

### Example 2: ordinary usage
```text
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

### Example 3: boundary or error behavior
```text
round((randomize ? Math.random() + 1 : 1)
      * minTimeout
      * factor ** retriesConsumed)
```

### Example 4: boundary or error behavior
```text
import pRetry from 'p-retry';

let remainingFailures = 2;
const value = await pRetry(attemptNumber => {
  if (remainingFailures-- > 0) {
    throw new Error(`attempt ${attemptNumber}`);
  }

  return 'ready';
}, {retries: 2, minTimeout: 0});
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
