# Build `p-map`

## Project Description

Create an installable npm package named `p-map`, version `7.0.7`, from an empty
workspace. It maps values from synchronous or asynchronous iterables through a
mapper while bounding the number of pending mapper promises. The package also
offers an async-iterable result form and a sentinel for omitting mapped values.

The implementation must be a normal reusable ESM library. It must not copy the
upstream implementation or tests.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` with glibc.
- `package.json` must name version `7.0.7`, declare `"type": "module"`, and
  expose the root through an export map with `types: "./index.d.ts"` and
  `default: "./index.js"`.
- Include `index.js`, `index.d.ts`, and a v3 `package-lock.json` consistent with
  the manifest. There are no runtime dependencies, workspaces, native addons,
  lifecycle scripts, or development dependencies required by the package.
- A clean verifier must be able to run
  `npm ci --offline --ignore-scripts --no-audit --no-fund` followed by
  `npm pack --ignore-scripts`.
- Do not use runtime network services, wall-clock timing, random state, or
  browser globals to determine scheduling behavior.

## API Usage Guide

### `pMap`

Import the default export from the package root:

```js
import pMap, {pMapSkip} from 'p-map';

const values = await pMap([1, 2, 3], async (value, index) => value + index, {
  concurrency: 2,
});
```

```ts
function pMap<Element, NewElement>(
  input: Iterable<Element | Promise<Element>> | AsyncIterable<Element | Promise<Element>>,
  mapper: (element: Element, index: number) => NewElement | Promise<NewElement | typeof pMapSkip>,
  options?: Options
): Promise<Array<Exclude<NewElement, typeof pMapSkip>>>;
```

`input` must be a synchronous or asynchronous iterable. Each input item is
awaited before the mapper receives it. The mapper receives the item and its
zero-based input index. Mapper results are returned in input order, regardless
of completion order. Synchronous mapper returns are accepted; thrown errors and
rejected promises reject the result.

`options.concurrency` defaults to `Infinity` and must be a safe integer at least
1 or positive infinity. With `stopOnError: true` (the default), the first
mapper error rejects the returned promise, while already-started work may still
settle. With `stopOnError: false`, all work is allowed to settle and mapper
errors are reported as an `AggregateError`. The `signal` option accepts an
`AbortSignal`; an already-aborted signal or a later abort rejects with its
reason, normally an `AbortError` DOMException.

Return the exported `pMapSkip` symbol from the mapper to omit that item from the
final array. Multiple skipped values are removed while the remaining values
retain their input order.

### `pMapIterable`

```ts
function pMapIterable<Element, NewElement>(
  input: Iterable<Element | Promise<Element>> | AsyncIterable<Element | Promise<Element>>,
  mapper: (element: Element, index: number) => NewElement | Promise<NewElement | typeof pMapSkip>,
  options?: IterableOptions
): AsyncIterable<Exclude<NewElement, typeof pMapSkip>>;
```

This validates the same iterable, mapper, and `concurrency` rules, then returns
an async iterable. Results are yielded in input order even when later mapper
promises settle first. `backpressure` defaults to `concurrency` and must be a
safe integer at least as large as `concurrency`, or positive infinity. It bounds
the number of produced-but-not-yet-collected results. Mapper and source errors
are raised when the consumer advances the result iterator.

### `pMapSkip`

`pMapSkip` is a named-export unique symbol. Returning it from either mapper
causes the corresponding item not to appear in the array or async iterable.

## Implementation Notes

Keep the package self-contained and deterministic. Do not expose private helper
modules through the export map. Preserve source iteration order and mapper
indices for promise-valued inputs and async iterables. Validation errors should
be `TypeError` and should happen before invoking an invalid mapper. The scored
verifier uses a bounded JSON scenario adapter: callbacks, symbols, custom
objects, and arbitrary executable strings do not cross the trusted boundary,
but the adapter constructs controlled promises, async generators, and errors in
the candidate child process.
