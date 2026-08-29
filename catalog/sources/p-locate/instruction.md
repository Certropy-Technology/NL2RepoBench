# Build `p-locate`

## Project Description

Create an installable npm package named `p-locate`, version `7.0.0`, from an
empty workspace. The package is an asynchronous counterpart to `Array#find`:
it receives a synchronous or asynchronous iterable, tests resolved values, and
returns the first value whose tester result is exactly `true`.

This task covers the complete public runtime export and its TypeScript
declaration. It does not require the upstream AVA, XO, tsd, GitHub workflow, or
development dependencies. Do not copy upstream source or tests into the
generated repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must name version `7.0.0`, use `"type": "module"`, and expose
  a safe in-package ESM root entry plus its TypeScript declaration entry.
- The package root has exactly one runtime export: a default function named
  `pLocate`.
- Declare `p-limit` as the sole direct runtime dependency, pinned to `7.3.1`.
  The v3 `package-lock.json` must resolve its transitive `yocto-queue`
  dependency to `1.2.2`.
- Declare no npm scripts or development dependencies. A clean verifier must be
  able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not use lifecycle hooks, workspaces, native addons, custom loaders,
  registry configuration, network access, browser globals, random state, or
  wall-clock timing to determine the result.

## Bounded Execution Contract

The trusted verifier never imports candidate code into its own process. It
starts a bounded unprivileged child that imports the installed package and
constructs allowlisted iterable and tester scenarios in that child. Requests
and responses are bounded JSON objects; callbacks, promises, iterators, and
errors are created only inside the child process.

Scored values are recursively composed of JSON null, booleans, finite numbers,
strings, arrays, and ordinary objects. No source text, executable strings,
functions, symbols, BigInts, cyclic objects, accessors, or custom prototypes
cross the verifier boundary. Each scenario uses at most six input values and
finite event-loop turns.

## API Usage Guide

### `pLocate`

```ts
export type Options = {
  readonly concurrency?: number;
  readonly preserveOrder?: boolean;
};

export default function pLocate<ValueType>(
  input: Iterable<PromiseLike<ValueType> | ValueType>,
  tester: (element: ValueType) => PromiseLike<boolean> | boolean,
  options?: Options,
): Promise<ValueType | undefined>;

export default function pLocate<ValueType>(
  input: AsyncIterable<PromiseLike<ValueType> | ValueType>,
  tester: (element: ValueType) => PromiseLike<boolean> | boolean,
): Promise<ValueType | undefined>;
```

For a synchronous iterable, resolve every input value before passing it as the
sole argument to `tester`. Adopt both synchronous and PromiseLike tester
results. A value matches only when the fulfilled tester result is the boolean
`true`; other truthy values do not match. Fulfill with the matching resolved
input value, or with `undefined` when the iterable ends without a match.

`options.concurrency` bounds the number of pending tester calls. It defaults
to `Number.POSITIVE_INFINITY` and accepts positive integers or positive
infinity. Invalid values, including zero, negative numbers, fractions, and
`NaN`, reject with the `TypeError` produced by the limiter.

`options.preserveOrder` defaults to `true`. In that mode, testers may execute
concurrently, but matching is resolved in input order: a later value that
finishes first does not overtake an earlier matching value. With
`preserveOrder: false`, return the first matching value by tester completion.
The first observed terminal outcome ends the search; a tester or input
rejection observed before a match rejects the returned promise.

When `input` implements `Symbol.asyncIterator`, consume it serially with
`for await`. Await each yielded value and its tester result before requesting
the next value, stop requesting values after a match, and ignore the
synchronous-iterable `concurrency` and `preserveOrder` options. If an object
implements both iterator protocols, use its asynchronous iterator.

Preserve exception constructor names and messages from rejected input values,
tester throws or rejections, and iterator failures. The package has no global
mutable state and does not mutate input values.

Example:

```js
import pLocate from 'p-locate';

const result = await pLocate(
  [Promise.resolve('alpha'), 'beta', 'gamma'],
  async value => value.startsWith('b'),
  {concurrency: 2},
);

// result is 'beta'
```

Completion-order example:

```js
const result = await pLocate(jobs, runCheck, {preserveOrder: false});
```

Here the first job whose `runCheck` promise fulfills to `true` wins, even when
it appears later in `jobs`.

## Implementation Notes

Keep synchronous-iterable scheduling deterministic under bounded concurrency,
and keep asynchronous-iterable consumption serial. Do not coerce tester
results to booleans. Do not swallow input, tester, or iterator failures merely
to continue searching. The generated repository should contain the package
metadata, implementation, declarations, license, and any original tests you
choose to write, but it must not contain the hidden verifier or forged grading
files.
