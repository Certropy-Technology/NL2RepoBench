# Build `universalify`

## Project Description

Create a complete installable CommonJS npm package named `universalify`,
version `2.0.1`, from an empty workspace. The package converts a callback-based
function or a Promise-based function into one callable in either style while
preserving its receiver, arguments, result, and failure reason.

This is a repository-generation task. Implement the behavior described here
with your own package files. Do not fetch or copy a reference repository or
its tests.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and CommonJS semantics.
- `require('universalify')` must return an object whose public enumerable
  exports are exactly `fromCallback` and `fromPromise`.
- `package.json` must name `universalify` version `2.0.1`, use `index.js` as
  its package-root CommonJS entry, require Node `>=10.0.0`, and include only
  package files needed at runtime.
- Commit an npm v3 `package-lock.json` agreeing with `package.json`. A clean
  verifier installs the package with:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The runtime dependency closure is empty. Do not declare dependencies,
  optional dependencies, peer dependencies, development dependencies,
  workspaces, native addons, custom loaders, registry settings, lifecycle
  scripts, generated downloads, or network access. The package has no CLI.
- Runtime behavior is local and deterministic. The wrapper factories may use
  native `Promise`; they must not inspect files, environment variables, the
  clock, randomness, subprocesses, a TTY, or the network.

## API Usage Guide

Both factories require a callable source function and return a new function.
The returned function has the same `.name` value as the source function and
forwards the dynamic `this` receiver. Supplying a non-callable value is outside
the valid input domain; ordinary JavaScript `TypeError` behavior may result.

### `fromCallback(function_)`

**Import path:** package root named export.

**Signature:**

```ts
type NodeCallback<Result> = (error: unknown, result?: Result) => void;

function fromCallback<Arguments extends unknown[], Result>(
  function_: (...arguments_: [...Arguments, NodeCallback<Result>]) => void,
): {
  (...arguments_: [...Arguments, NodeCallback<Result>]): void;
  (...arguments_: Arguments): Promise<Result>;
};
```

The source function follows the Node callback convention: its final argument
is called as `(error, result)`. The returned wrapper selects its mode solely by
checking whether the wrapper call's final argument is a function.

- With a final callback, call the source immediately with the same receiver
  and all original arguments. Return `undefined`; do not wrap or intercept the
  callback. A synchronous exception from the source or user callback therefore
  propagates synchronously.
- Without a final callback, return a native Promise. Invoke the source with the
  same receiver and a newly appended callback, without modifying an array used
  by the caller for `.apply`.
- Resolve with the callback's first result value only when `error == null`, so
  both `null` and `undefined` mean success. Reject with the exact first argument
  for every other value, including falsey values such as `0`, `false`, or an
  empty string.
- Extra callback result arguments are ignored. The source may settle its
  callback synchronously or asynchronously. The factory does not add
  once-only enforcement if a source calls its callback repeatedly.

```js
const {fromCallback} = require('universalify');

const readValue = fromCallback(function (value, callback) {
  callback(null, {receiver: this.label, value});
});

await readValue.call({label: 'promise'}, 3);
readValue.call({label: 'callback'}, 4, (error, result) => {
  // error is null; result is {receiver: 'callback', value: 4}
});
```

### `fromPromise(function_)`

**Import path:** package root named export.

**Signature:**

```ts
function fromPromise<Arguments extends unknown[], Result>(
  function_: (...arguments_: Arguments) => PromiseLike<Result>,
): {
  (...arguments_: Arguments): PromiseLike<Result>;
  (...arguments_: [...Arguments, NodeCallback<Result>]): void;
};
```

The source function must return a valid Promise or thenable.

- Without a final callback, call the source with the same receiver and all
  arguments and return its result unchanged. Do not replace it with a new
  Promise.
- With a final callback, remove that callback before invoking the source, call
  the source with the same receiver and remaining arguments, attach handlers
  to its returned Promise/thenable, and return `undefined`.
- On fulfillment, invoke the callback exactly as `(null, result)`. On
  rejection, invoke it with the exact rejection reason as its sole argument,
  including a falsey reason.
- Do not catch exceptions thrown by the user callback and do not invoke that
  callback a second time. A throw from a callback reached through a fulfilled
  Promise consequently becomes an unhandled rejection of the ignored chained
  Promise under normal JavaScript semantics.

```js
const {fromPromise} = require('universalify');

const double = fromPromise(async function (value) {
  return {receiver: this.label, value: value * 2};
});

await double.call({label: 'promise'}, 3);
double.call({label: 'callback'}, 4, (error, result) => {
  // error is null; result is {receiver: 'callback', value: 8}
});
```

## Implementation Notes

- Detect only a function in the final wrapper argument as a callback. A
  function in any earlier position is ordinary source input.
- Preserve source function names through the returned wrapper rather than
  exposing generic factory names.
- Do not serialize, clone, or otherwise transform values passed inside the
  process. Promise resolution and callback delivery use the original values
  and rejection reasons.
- The verifier constructs callback and Promise scenarios in a bounded,
  UID-isolated child process and returns only JSON-safe observations to the
  trusted test process. Candidate code is never imported by the trusted
  verifier process.
