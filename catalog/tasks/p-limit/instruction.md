# Build `p-limit`

## Project Description

Create an installable npm package named `p-limit`, version `7.3.1`, from an
empty workspace. The package limits the number of concurrently executing
promise-returning or synchronous functions while preserving each call's
result, rejection, arguments, and asynchronous execution context.

This task scores the complete public runtime API through deterministic,
bounded concurrency scenarios. It does not require the upstream benchmark,
lint configuration, AVA tests, or development dependencies. Do not copy
upstream source or tests into the generated repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must name version `7.3.1`, use `"type": "module"`, and expose
  a safe in-package ESM root entry plus its TypeScript declaration entry.
- The root entry has a default export named `pLimit` and a named export
  `limitFunction`.
- Declare `yocto-queue` as the sole runtime dependency, pinned to `1.2.1` in a
  v3 `package-lock.json`. Declare no npm scripts or development dependencies.
- A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not use lifecycle hooks, workspaces, native addons, custom loaders,
  registry configuration, network access, browser globals, random state, or
  wall-clock timing to determine queue behavior.

## Bounded Execution Contract

The verifier never imports candidate code into its trusted test process. It
starts a bounded child process that imports the installed package and constructs
allowlisted task scenarios inside that child. Requests are JSON objects of at
most 64 KiB, use at most 16 tasks, and use finite concurrency from 1 through 8
except for the explicit positive-infinity case. Responses are JSON objects of
at most 256 KiB.

No source text, executable strings, user callbacks, functions, symbols,
BigInts, cyclic objects, custom prototypes, or accessors cross this boundary.
Task values and forwarded arguments are recursively composed of JSON null,
booleans, finite numbers, strings, arrays, and ordinary objects. The child
constructs only identity/result functions, controlled promises, synchronous or
asynchronous failures, arithmetic mappers, and async-context checks described
below.

## API Usage Guide

### `pLimit`

```ts
type Options = {
  readonly concurrency: number;
  readonly rejectOnClear?: boolean;
};

export default function pLimit(concurrency: number | Options): LimitFunction;
```

`concurrency` must be a positive integer or `Number.POSITIVE_INFINITY`.
Anything else throws `TypeError`. The object form applies the same validation
to `options.concurrency`; `rejectOnClear`, when present, must be boolean and
defaults to `false`.

The returned limiter is callable:

```ts
limit(function_, ...arguments_): Promise<ReturnType>
```

Each call begins asynchronously and invokes `function_(...arguments_)` only
when fewer than `concurrency` earlier calls are active. Adopt synchronous
values and promises into the returned promise. Preserve thrown errors and
promise rejections for that call, then continue processing later queued work.
Results from `Promise.all` remain in call order even when tasks complete in a
different order. AsyncLocalStorage context present when a limited call is
submitted must be visible inside that call.

The limiter has these properties:

```ts
readonly activeCount: number;
readonly pendingCount: number;
concurrency: number;
clearQueue(): void;
map<Input, ReturnType>(
  iterable: Iterable<Input>,
  mapperFunction: (input: Input, index: number) => PromiseLike<ReturnType> | ReturnType
): Promise<ReturnType[]>;
```

- `activeCount` is the number of functions currently executing.
- `pendingCount` is the number waiting to start. Both begin at zero and return
  to zero after all submitted work settles.
- Assigning `concurrency` validates the new value. Raising it schedules more
  queued work asynchronously. Lowering it does not cancel active work; later
  work starts only as capacity becomes available under the new limit.
- `clearQueue()` removes every pending call but does not cancel active calls.
  With `rejectOnClear: false`, removed calls remain unresolved. With
  `rejectOnClear: true`, each removed call rejects with an error whose name is
  `AbortError`.
- `map` accepts any synchronous iterable, passes each value and zero-based
  index to the mapper, enforces the same limiter, and returns results in input
  order. It remains callable after destructuring from the limiter.

Example:

```js
import pLimit from 'p-limit';

const limit = pLimit(2);
const results = await Promise.all([
  limit(async value => value * 2, 2),
  limit(async value => value * 2, 3),
]);

// results is [4, 6]
```

### `limitFunction`

```ts
export function limitFunction<Arguments extends unknown[], ReturnType>(
  function_: (...arguments_: Arguments) => PromiseLike<ReturnType>,
  options: Options
): (...arguments_: Arguments) => Promise<ReturnType>;
```

Return a new function that forwards every argument to `function_` and limits
concurrent executions according to `options`. Calls made through one returned
function share its limiter; separate returned functions do not share state.
Apply the same option validation, result, rejection, and async-context behavior
as `pLimit`.

## Implementation Notes

Queue transitions and output ordering must be deterministic. Releasing,
rejecting, clearing, or changing the limit must never make `activeCount`
negative or start more work than the effective concurrency. The frozen
verifier contains 24 `node:test` leaves adapted from the pinned upstream AVA
suite. It replaces timing and randomness with controlled promises while
retaining constructor validation, queue state, ordering, errors, mapping,
dynamic concurrency, clear behavior, argument forwarding, `limitFunction`,
and AsyncLocalStorage coverage.
