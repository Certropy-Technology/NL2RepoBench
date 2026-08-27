# Build `p-map`

## Project Description

Create an installable npm package named `p-map`, version `7.0.6`, from an
empty workspace. The package maps synchronous or asynchronous iterables with
bounded concurrency. It exposes the default `pMap` function, the named
`pMapIterable` function, and the named `pMapSkip` symbol from its ESM root.

The scored contract is a deterministic, JSON-compatible subset of the pinned
public API. It covers mapping, ordering, concurrency limits, asynchronous
input, skipping, error aggregation, abort signals, streaming, and
backpressure. It does not expose the reference source or tests. Do not copy
upstream source or tests into the generated repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must use `"type": "module"`, identify `p-map` version
  `7.0.6`, and expose a safe in-package ESM root. The root default export is
  `pMap`; named exports are `pMapIterable` and `pMapSkip`.
- Declare no runtime dependencies, npm scripts, lifecycle hooks, workspaces,
  native addons, custom loaders, or registry configuration. Include a v3
  `package-lock.json` that agrees with `package.json`.
- A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Runtime behavior must not require network access, browser globals, files
  outside the installed package, current wall-clock time, or random state.
  Internal timers used to await mapper promises are ordinary JavaScript
  behavior; output must not depend on scheduling accidents.

## JSON Boundary

The verifier invokes the installed package only in bounded child processes as
an unprivileged user. Requests are JSON objects no larger than 64 KiB and
responses are JSON objects no larger than 256 KiB. Candidate code is never
imported into the trusted test process.

The scored value domain is recursively composed of JSON null, booleans,
finite numbers, strings, arrays, and objects. The fixed adapter constructs
ordinary mapper callbacks, promises, iterables, async iterables,
`AbortController` instances, and `pMapSkip` values inside the candidate child.
It never transports or evaluates source text, executable strings, functions,
symbols, BigInts, regular expressions, custom prototypes, accessors, or
cyclic objects.

Mapper callback identity and arbitrary user side effects cannot cross this
boundary. They are observed only through returned JSON values and bounded
trace facts such as invocation indexes and maximum simultaneous mapper calls.
Exact elapsed milliseconds are not part of the scored result.

## API Usage Guide

### Default export: `pMap`

**Import and signature:**

```js
import pMap, {pMapSkip} from 'p-map';

await pMap(input, mapper, options?);
```

`input` must be an `Iterable` or `AsyncIterable`. Each yielded value may be a
promise; await it before invoking `mapper`. A string is an ordinary iterable
of its code points. `mapper(element, index)` receives the awaited element and
a zero-based index assigned in source order. It may return a value, a promise,
or `pMapSkip`.

Return a promise for an array of mapper results in input order, regardless of
completion order. Omit every result equal to the exported `pMapSkip` symbol
without disturbing the relative order of retained results. Empty input and
input for which every result is skipped produce `[]`.

```js
const values = await pMap([1, 2, 3, 4], async (value, index) => {
  if (value % 2 === 0) {
    return pMapSkip;
  }

  return {value: value * 10, index};
}, {concurrency: 2});

// [{value: 10, index: 0}, {value: 30, index: 2}]
```

#### `pMap` options

- `concurrency`: maximum number of mapper promises pending at once. The
  default is `Infinity`. Accept `Infinity` or a safe integer greater than or
  equal to `1`. Reject zero, negative, fractional, string, and non-finite
  values other than positive `Infinity` with `TypeError`.
- `stopOnError`: defaults to `true`. With `true`, reject with the first mapper
  or source error observed. Mappers already started are not cancelled merely
  because another mapper rejected. A finite concurrency limit prevents later
  input from starting after rejection when it has not already been pulled.
  With `false`, continue mapping and then reject with an `AggregateError`
  containing all mapper errors in observation order. A source iterator error
  still rejects directly because the source cannot safely continue.
- `signal`: an optional `AbortSignal`. If already aborted, reject immediately
  with `signal.reason` and do not invoke the mapper. If it aborts while mapping,
  reject with `signal.reason`. Remove the abort listener when the returned
  promise settles. Aborting does not retroactively cancel mapper promises that
  have already started.

Invalid input rejects with `TypeError` and a message identifying that an
`Iterable` or `AsyncIterable` was expected. A non-function mapper rejects with
`TypeError` and a message containing `Mapper function is required`.

### Named export: `pMapIterable`

**Import and signature:**

```js
import {pMapIterable, pMapSkip} from 'p-map';

for await (const value of pMapIterable(input, mapper, options?)) {
  // Consume values in input order.
}
```

Return an `AsyncIterable` that maps the same synchronous or asynchronous input
domain. Await promised input values and mapper results, pass stable zero-based
indexes, preserve input order, and omit `pMapSkip` results. Mapper or source
errors are thrown to the consumer. Values successfully yielded before a later
error remain consumed.

`concurrency` has the same domain and default as `pMap`.

`backpressure` is the maximum number of resolved mapper promises waiting to be
collected by the consumer. It defaults to `concurrency`. Accept `Infinity` or
a safe integer greater than or equal to `concurrency`. Reject a smaller,
zero, negative, fractional, string, or otherwise invalid value with
`TypeError`. While a consumer pauses, do not keep pulling and mapping beyond
the configured concurrency and backpressure bounds.

```js
const stream = pMapIterable([1, 2, 3], async value => value * 2, {
  concurrency: 2,
  backpressure: 2
});

const output = [];
for await (const value of stream) {
  output.push(value);
}

// [2, 4, 6]
```

### Named export: `pMapSkip`

`pMapSkip` is one stable symbol exported from the package root. Returning that
exact symbol from either mapper omits the corresponding result. Ordinary JSON
values, including the string `"skip"`, are not treated as the sentinel.

## Implementation Notes

- Preserve deterministic result and error ordering while allowing mapper work
  to settle concurrently. Concurrency is about pending mapper work, not output
  order.
- Handle synchronous iterator failures, asynchronous iterator failures,
  promised input values, mapper rejections, and abort signals without emitting
  unhandled promise rejections.
- The frozen production verifier has 54 `node:test` leaves. They are adapted
  from the 51-leaf upstream AVA suite plus packaging and boundary checks. The
  upstream lint, TypeScript declaration tests, randomized timing windows, and
  algorithmic performance benchmark were validated during source authoring but
  are not executed by the production verifier.
- Do not include hidden tests, verifier code, private artifacts, reward files,
  the reference implementation, or generated Harbor files in the candidate
  package.
