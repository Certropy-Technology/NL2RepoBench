# Project Description

## Project Description

Create an installable npm package named `async`, version `3.2.6`, from an
empty workspace. It is a CommonJS callback/control-flow library. The task
scores a deterministic subset of the public collection and control-flow API
through `async/adapter`, a JSON-compatible task adapter required because
JavaScript callbacks cannot cross the verifier process boundary directly.

This is a repository-generation task. Implement the described behavior with
your own source files. Do not retrieve the reference repository or hidden
tests.

# Natural Language Instruction

Create the `async` project from an empty `workspace/`. Build an installable implementation, not a loose demonstration script. The public API guide below is the complete source of the task contract; preserve its import paths, signatures, return shapes, ordering, state changes, and exceptions.

Required capabilities:
- callback collection helpers: implement the documented public behavior and preserve its input/output and error contract.
- ordered and limited concurrency: implement the documented public behavior and preserve its input/output and error contract.
- series and waterfall control flow: implement the documented public behavior and preserve its input/output and error contract.
- retry, timeout, and JSON adapter operations: implement the documented public behavior and preserve its input/output and error contract.

Do not copy an upstream checkout or tests. Keep behavior deterministic and local, and make the package usable from the installation layout described below. The principal public entry points include: `require('async')`, `require('async/adapter').run(request)`, `times(n, iteratee)`, `retry(times, task)`.

# Supports

- Node `24.19.0`, npm `11.17.0`, CommonJS, and `linux/amd64` with glibc.
- `require('async')` must expose the documented public functions. Set `main`
  to the implementation entry point; the conventional `dist/async.js` path is
  supported. Package metadata must identify version `3.2.6`.
- `require('async/adapter').run(request)` must be an async callable export.
  This adapter is part of this task's public contract, not an upstream async
  API. It translates the bounded JSON operations below into calls to the
  package's callback APIs.
- Commit a compatible npm v3 `package-lock.json`. A clean verifier runs
  `npm ci --offline --ignore-scripts --no-audit --no-fund` and
  `npm pack --ignore-scripts`.
- The scored package has no runtime dependency roots. Do not add network,
  native-addon, git, file, workspace, custom-loader, or lifecycle-hook
  dependencies.


## NoNetwork boundary

Agent, candidate, verifier, Oracle, controls, and normal runtime execution are network-isolated. Do not access GitHub, package registries, Go proxies, DNS, or external services during execution; use only the frozen local build inputs.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── dist/async.js
├── adapter.js
└── lib/
    ├── map.js
    ├── mapLimit.js
    ├── parallel.js
    ├── series.js
    ├── waterfall.js
    ├── retry.js
    └── timeout.js
```

# API Usage Guide

### Root package

The package root is CommonJS:

```js
const async = require('async');
await async.map([1, 2, 3], (value, done) => done(null, value * 2));
```

Implement these public functions and their Promise form when the final
callback is omitted: `map`, `mapLimit`, `mapSeries`, `filter`, `reject`,
`detect`, `some`, `every`, `reduce`, `groupBy`, `sortBy`, `parallel`,
`parallelLimit`, `series`, `waterfall`, `times`, `timesLimit`, `retry`, and
`timeout`.

Collection mappers, predicates, and tasks receive a Node-style callback.
`map` and `parallel` may start work concurrently but preserve array result
order. Limit variants never exceed their positive concurrency limit.
`mapSeries`, `series`, `reduce`, and `waterfall` preserve sequential data
flow. `filter` and `reject` preserve source order. `detect` returns the first
matching value or `undefined`; `some` and `every` return booleans.

`reduce` begins with its supplied memo. `groupBy` creates arrays keyed by the
computed grouping key. `sortBy` sorts by a computed key while retaining a
deterministic result for equal keys. `times(n, iteratee)` calls the iteratee
for indexes `0` through `n - 1`.

`retry(times, task)` attempts a task until it succeeds or exhausts its budget.
`timeout(task, milliseconds, info)` fails with an error whose `code` is
`'ETIMEDOUT'` when the callback does not arrive in time, preserving `info`
when provided.

### `async/adapter`

`run(request)` accepts one plain JSON object and resolves to a JSON value.
Reject malformed requests and unsupported operation names with an `Error`.
The adapter supports these operation names:

- `version`: return `{ version }`.
- `map`, `mapLimit`, and `mapSeries`: accept `values`, a `transform` of
  `identity`, `double`, `square`, or `uppercase`, and optional `delays` in
  milliseconds. Limit variants also return observed `maxActive` and `events`.
- `filter`, `reject`, `detect`, `some`, and `every`: accept `values` and a
  `predicate` of `even`, `odd`, `truthy`, or `nonempty`.
- `reduce`: accepts `values`, `memo`, and a `reducer` of `sum`, `product`, or
  `concat`. `groupBy` accepts `parity`, `firstLetter`, or `type`; `sortBy`
  accepts `number` or `length`.
- `parallel`, `parallelLimit`, and `series`: accept `tasks`, an array of
  `{ value, delay }` objects. Return ordered `result`, observed `maxActive`,
  and start/finish `events` where applicable.
- `waterfall`: accepts `value` and `steps`, whose `op` is `add`, `multiply`,
  or `append` and whose `value` is the operand.
- `times` and `timesLimit`: accept `n`, optional `limit`, and optional
  `delay`; return `{ result, maxActive }`.
- `retry`: accepts positive `times`, nonnegative `failures`, and `value`.
  Return `{ ok: true, value, attempts }` after success, or
  `{ ok: false, error, attempts }` after exhaustion.
- `timeout`: accepts `delay`, positive `milliseconds`, `value`, and optional
  JSON-compatible `info`. Return `{ ok: true, value }` on time, otherwise
  `{ ok: false, code: 'ETIMEDOUT', info }`.

The adapter must delegate these operations to the root package functions, not
to a network service or external process. Keep timing deterministic: `delay`
and members of `delays` are nonnegative milliseconds.

# Implementation Notes

The verifier invokes only `require('async/adapter').run` through a bounded,
non-root subprocess with JSON input/output. It cannot pass callbacks, source
code, arbitrary module names, shell commands, or environment configuration.
Do not rely on verifier files, global npm packages, browser APIs, native
addons, lifecycle hooks, or network access.

Preserve JSON values and input array order. A task may schedule callback work
with timers, but should not depend on wall-clock precision beyond the supplied
relative delays. Async iterables, queues, cargo workers, auto dependency
graphs, filesystem/network helpers, browser builds, and callback cancellation
are outside this fixed denominator.

# Examples

## Ordinary ordered map

```javascript
const async = require('async')
async.map([1, 2, 3], (value, done) => done(null, value * 2), (error, values) => {
  if (error) throw error
  console.log(values)
})
```

## Ordinary adapter operation

```javascript
const {run} = require('async/adapter')
const result = await run({op: 'reduce', values: [1, 2, 3], memo: 0, reducer: 'sum'})
```

## Boundary: timeout result

```javascript
await run({op: 'timeout', delay: 20, milliseconds: 1, value: 'late'})
```

## Boundary: unknown operation

```javascript
await run({op: 'unknown'}) // rejects with the documented request error
```

# Error Handling and Boundary Conditions

Reject invalid inputs using the documented exception or error result. Preserve empty-input behavior, ordering, Unicode/encoding behavior, cancellation or timeout semantics, and local filesystem boundaries where the API specifies them. Never turn a failed local operation into a network request, subprocess, or silent success.
