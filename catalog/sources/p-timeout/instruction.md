# p-timeout

## Project Description

Build an installable `p-timeout` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `p-timeout`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `TimeoutError`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `pTimeout`: preserve the documented object or module behavior, including state and side effects.
3. `p-timeout`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `root exports`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `p-timeout`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- No third-party runtime package is declared by the local task metadata; standard-library support is sufficient unless the API section says otherwise.
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


Settlement and cleanup must be single-shot. Late input settlement, late abort,
or a stale timer callback must not change an already settled result. Preserve
input and fallback error identity inside the process, do not swallow promise
rejections, and do not leave abort listeners or active timers after settlement.
The frozen verifier has 35 `node:test` leaves adapted from the pinned upstream
AVA and tsd suites; it replaces elapsed-time assertions with explicit custom
timer callbacks and controlled promises.

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
export class TimeoutError extends Error {
  readonly name: 'TimeoutError';
  constructor(message?: string, options?: ErrorOptions);
}
```

### Example 3: boundary or error behavior
```text
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

### Example 4: boundary or error behavior
```text
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


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
