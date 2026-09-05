# p-queue

## Project Description

Build an installable `p-queue` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `p-queue`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `PQueue`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Adding work`: preserve the documented object or module behavior, including state and side effects.
3. `Flow control and waiters`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Priority and state`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `p-queue`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- Declared build/runtime packages are supplied by the frozen evaluation image: `eventemitter3`, `p-timeout`
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

### `PQueue`

**Import and constructor:**

```js
import PQueue, {TimeoutError} from 'p-queue';
const queue = new PQueue(options);
```

`options` is optional. The scored fields are:

- `concurrency`: number of simultaneously running tasks; default `Infinity`;
  values below `1` throw `TypeError`.
- `timeout`: default positive finite timeout in milliseconds. It begins when a
  task starts, not while queued. Omit it for no timeout.
- `autoStart`: `false` starts paused; otherwise tasks start when possible.
- `intervalCap`: positive number of starts permitted per interval; default
  `Infinity`.
- `interval`: finite non-negative interval length in milliseconds; default `0`.
- `carryoverIntervalCount`: when true, unfinished tasks count toward the next
  fixed interval; default false.
- `strict`: when true, use a sliding-window rate limit. Strict mode requires a
  non-zero `interval` and finite `intervalCap` or throws `TypeError`.

#### Adding work

```ts
queue.add<T>(task: (options: {signal?: AbortSignal}) => T | PromiseLike<T>,
  options?: {id?: string; priority?: number; timeout?: number; signal?: AbortSignal}): Promise<T>

queue.addAll<T>(tasks: ReadonlyArray<(options: {signal?: AbortSignal}) => T | PromiseLike<T>>,
  options?: {priority?: number; timeout?: number; signal?: AbortSignal}): Promise<T[]>
```

`add` always returns a promise and adopts synchronous values, asynchronous
values, thrown errors, and rejected promises. `addAll` resolves values in input
order. Per-task timeout overrides the queue default. Invalid non-positive or
non-finite timeouts throw `TypeError`. Timed-out tasks reject with the named
`TimeoutError`; its message includes the configured milliseconds and current
running/waiting counts.

Priorities are finite numbers. Higher values run first among queued tasks;
equal priorities retain insertion order. `id` identifies queued tasks for
priority changes. The task receives the same `AbortSignal` supplied in its
options. Aborting queued work removes it immediately and rejects its promise
with `signal.reason`; aborting running work rejects it but does not start more
than the configured concurrency.

#### Flow control and waiters

```ts
queue.start(): this
queue.pause(): void
queue.clear(): void
queue.onEmpty(): Promise<void>
queue.onIdle(): Promise<void>
queue.onPendingZero(): Promise<void>
queue.onSizeLessThan(limit: number): Promise<void>
queue.onRateLimit(): Promise<void>
queue.onRateLimitCleared(): Promise<void>
queue.onError(): Promise<never>
```

`start` resumes a paused queue and returns that queue. `pause` prevents new
starts without interrupting running tasks. `clear` discards queued tasks but
does not cancel running tasks or reset strict rate-limit history.

`onEmpty` resolves when no tasks remain queued, even if tasks are still
running. `onIdle` resolves only when both `size` and `pending` are zero.
`onPendingZero` resolves whenever no tasks are currently running and ignores
queued work. `onSizeLessThan(limit)` resolves when `size < limit`.
Rate-limit waiters resolve at the corresponding state transition. `onError`
rejects on the first task error; each `add` rejection must still be handled.

#### Priority and state

```ts
queue.setPriority(id: string, priority: number): void
queue.sizeBy(options: {priority?: number}): number
```

`setPriority` reorders the live queued task with `id`. A non-finite priority
throws `TypeError`; an unknown id throws `ReferenceError`. `sizeBy` counts live
queued tasks matching the supplied priority.

The following properties are observable:

- writable `concurrency` and `timeout`;
- read-only `size`, `pending`, `isPaused`, `isRateLimited`, and `isSaturated`;
- read-only `runningTasks`, a fresh array of fresh objects containing `id`,
  `priority`, `startTime`, optional `timeout`, and optional non-negative
  `timeoutRemaining`.

Changing `concurrency` immediately processes available work. `isSaturated` is
true when every concurrency slot is occupied with queued backlog, or when the
queue is rate-limited with backlog. `runningTasks` mutation must not change
internal queue state.

#### Events

`PQueue` is an EventEmitter. It emits `add`, `active`, `completed`, `error`,
`next`, `empty`, `idle`, `pendingZero`, `rateLimit`, and `rateLimitCleared` at
their corresponding lifecycle transitions. `completed` receives the task
result and `error` receives the task error.

### Interval behavior

When `intervalCap` and `interval` enable rate limiting, no more than the cap
may start in one fixed window. Fixed-window work is released in batches at
window boundaries. With `strict: true`, starts use a sliding window: a new slot
opens only after the oldest counted start ages out. `isRateLimited` and the
rate-limit events reflect backlog blocked by this cap and clear when idle.

### `PriorityQueue`

```js
import {PriorityQueue} from 'p-queue';
const queue = new PriorityQueue();
```

The exported queue class supports:

```ts
queue.enqueue(run, {priority?: number, id?: string}): void
queue.dequeue(): (() => Promise<unknown>) | undefined
queue.filter({priority?: number}): Array<() => Promise<unknown>>
queue.setPriority(id: string, priority: number): void
queue.remove(id: string): void
queue.remove(run: () => Promise<unknown>): void
readonly queue.size: number
```

It orders higher priority first, preserves insertion order for ties, filters
only live entries, ignores already dequeued entries, and removes the matching
live id or function. Dequeuing an empty queue returns `undefined`.

### Validation errors

Constructor and setter validation uses `TypeError` messages that identify the
invalid option (`concurrency`, `intervalCap`, `interval`, `timeout`, or
`priority`). Strict-mode errors identify the required non-zero interval or
finite interval cap. Missing `PriorityQueue` ids use `ReferenceError` with the
unknown id in the message.


Preserve deterministic queue ordering and ordinary ESM package loading. The
frozen verifier has 46 `node:test` leaves derived from the core behavior of the
pinned 206-leaf upstream suite. It excludes long stress cases, custom queue
classes, TypeScript-only assertions, benchmark tooling, exact nanosecond
timing, and internal data structures. Those omissions define the public task
boundary and must not be interpreted as upstream parity.

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
  npm pack --ignore-scripts
```

### Example 2: ordinary usage
```text
import PQueue, {TimeoutError} from 'p-queue';
const queue = new PQueue(options);
```

### Example 3: boundary or error behavior
```text
queue.add<T>(task: (options: {signal?: AbortSignal}) => T | PromiseLike<T>,
  options?: {id?: string; priority?: number; timeout?: number; signal?: AbortSignal}): Promise<T>

queue.addAll<T>(tasks: ReadonlyArray<(options: {signal?: AbortSignal}) => T | PromiseLike<T>>,
  options?: {priority?: number; timeout?: number; signal?: AbortSignal}): Promise<T[]>
```

### Example 4: boundary or error behavior
```text
queue.start(): this
queue.pause(): void
queue.clear(): void
queue.onEmpty(): Promise<void>
queue.onIdle(): Promise<void>
queue.onPendingZero(): Promise<void>
queue.onSizeLessThan(limit: number): Promise<void>
queue.onRateLimit(): Promise<void>
queue.onRateLimitCleared(): Promise<void>
queue.onError(): Promise<never>
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
