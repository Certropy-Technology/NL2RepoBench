# p-limit

## Project Description

Build an installable `p-limit` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `p-limit`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `pLimit`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `limitFunction`: preserve the documented object or module behavior, including state and side effects.
3. `p-limit`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `root exports`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `p-limit`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- Declared build/runtime packages are supplied by the frozen evaluation image: `yocto-queue==1.2.1`
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


Queue transitions and output ordering must be deterministic. Releasing,
rejecting, clearing, or changing the limit must never make `activeCount`
negative or start more work than the effective concurrency. The frozen
verifier contains 24 `node:test` leaves adapted from the pinned upstream AVA
suite. It replaces timing and randomness with controlled promises while
retaining constructor validation, queue state, ordering, errors, mapping,
dynamic concurrency, clear behavior, argument forwarding, `limitFunction`,
and AsyncLocalStorage coverage.

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
type Options = {
  readonly concurrency: number;
  readonly rejectOnClear?: boolean;
};

export default function pLimit(concurrency: number | Options): LimitFunction;
```

### Example 3: boundary or error behavior
```text
limit(function_, ...arguments_): Promise<ReturnType>
```

### Example 4: boundary or error behavior
```text
readonly activeCount: number;
readonly pendingCount: number;
concurrency: number;
clearQueue(): void;
map<Input, ReturnType>(
  iterable: Iterable<Input>,
  mapperFunction: (input: Input, index: number) => PromiseLike<ReturnType> | ReturnType
): Promise<ReturnType[]>;
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
