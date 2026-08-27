# Build `p-queue`

## Project Description

Create an installable npm package named `p-queue`, version `9.3.3`, from an
empty workspace. It is an ESM promise queue that controls task concurrency,
priority, pausing, timeouts, cancellation, and interval-based rate limits.

The root module has a default `PQueue` class and named `PriorityQueue` and
`TimeoutError` exports. Type-only `Queue`, `QueueAddOptions`, and `Options`
exports must be present in the declaration entry. This task scores a bounded,
deterministic subset of the pinned public API. It does not claim complete
upstream test parity.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must use `"type": "module"`, version `9.3.3`, and a safe
  in-package root export with both JavaScript and TypeScript declaration files.
- Declare exactly `eventemitter3` version `5.0.4` and `p-timeout` version
  `7.0.1` as runtime dependencies. Declare no scripts, workspaces, optional
  dependencies, peer dependencies, native addons, or other runtime packages.
- Include a v3 `package-lock.json` agreeing with `package.json`. A clean
  verifier must be able to install and pack the project with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  npm pack --ignore-scripts
  ```

  The offline verifier cache is keyed by these immutable lock records; include
  them in `package-lock.json` without trying to contact the registry:

  | Package | Resolved archive | Integrity |
  | --- | --- | --- |
  | `eventemitter3@5.0.4` | `https://registry.npmjs.org/eventemitter3/-/eventemitter3-5.0.4.tgz` | `sha512-mlsTRyGaPBjPedk6Bvw+aqbsXDtoAyAzm5MO7JgU+yVRyMQ5O8bD4Kcci7BS85f93veegeCPkL8R4GLClnjLFw==` |
  | `p-timeout@7.0.1` | `https://registry.npmjs.org/p-timeout/-/p-timeout-7.0.1.tgz` | `sha512-AxTM2wDGORHGEkPCt8yqxOTMgpfbEHqF51f/5fJCmwFC3C/zNcGT63SymH2ttOAaiIws2zVg4+izQCjrakcwHg==` |

- Do not require lifecycle hooks, a custom loader, registry configuration,
  network access, browser globals, or native code.

## Bounded Verification Boundary

Candidate code runs only in an unprivileged, time- and resource-bounded child
process. The trusted test process does not import it. Requests describe one
allowlisted queue scenario with JSON data; responses contain JSON results.
Requests and responses are limited to 64 KiB and 256 KiB. No source text,
functions, callbacks, executable strings, modules, file handles, symbols,
BigInts, custom prototypes, or cyclic objects cross this boundary.

The verifier creates ordinary internal task functions from bounded descriptors
containing identifiers, finite priorities, delays of at most 500 milliseconds,
JSON result values, error flags, and positive finite timeouts. It observes task
start/completion order, settled values, queue properties, documented events,
and timing with tolerance. Filesystem behavior, custom queue classes, huge
queues, benchmarks, and compile-time generic variance are outside the scored
contract.

## API Usage Guide

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

## Implementation Notes

Preserve deterministic queue ordering and ordinary ESM package loading. The
frozen verifier has 46 `node:test` leaves derived from the core behavior of the
pinned 206-leaf upstream suite. It excludes long stress cases, custom queue
classes, TypeScript-only assertions, benchmark tooling, exact nanosecond
timing, and internal data structures. Those omissions define the public task
boundary and must not be interpreted as upstream parity.
