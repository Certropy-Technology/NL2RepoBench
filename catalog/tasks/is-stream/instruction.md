# Build `is-stream`

## Project Description

Create an installable ESM npm package named `is-stream`, version `4.0.1`,
from an empty workspace. The package identifies Node.js stream-like values and
distinguishes writable, readable, duplex, and transform streams.

This repository-generation task scores the five public predicates plus a
bounded JSON adapter named `run`. The adapter exists because native Node stream
objects and functions cannot cross the separate verifier process boundary.
Implement the behavior with your own source files. Do not retrieve the
reference repository or hidden tests.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, ESM, `linux/amd64`, and glibc.
- `package.json` must use `name: "is-stream"`, `version: "4.0.1"`,
  `type: "module"`, and a safe in-package root entry. It must expose the five
  predicates and the task adapter as named exports. A `main` entry pointing to
  the root ESM module is required by the bounded verifier loader.
- Commit a compatible npm v3 `package-lock.json`. A clean verifier installs and
  packs the candidate without network access using:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  npm pack --ignore-scripts
  ```

- The package has no runtime dependencies. Do not add workspaces, native
  addons, lifecycle hooks, custom loaders, registry overrides, subprocess
  helpers, generated downloads, or network access.

## API Usage Guide

All five predicates are synchronous, deterministic, side-effect free, and
return a boolean. They accept any JavaScript value without throwing.

```ts
export type Options = {
  checkOpen?: boolean;
};

export function isStream(stream: unknown, options?: Options): boolean;
export function isWritableStream(stream: unknown, options?: Options): boolean;
export function isReadableStream(stream: unknown, options?: Options): boolean;
export function isDuplexStream(stream: unknown, options?: Options): boolean;
export function isTransformStream(stream: unknown, options?: Options): boolean;
```

`checkOpen` defaults to `true`. With the default, a destroyed or closed stream
whose readable/writable state is false does not satisfy the corresponding
predicate. With `checkOpen: false`, classification uses the stream's structural
capabilities even after close.

### `isStream(stream, options?)`

Return `true` when `stream` is a non-null object with a callable `pipe` method
and it is readable, writable, or has no explicit readable/writable state. When
`checkOpen` is false, an object with callable `pipe` is accepted regardless of
its current readable/writable booleans.

```js
import {Readable} from 'node:stream';
import {isStream} from 'is-stream';

isStream(new Readable({read() {}})); // true
isStream({}); // false
```

### `isWritableStream(stream, options?)`

Return `true` only when `isStream` is true, writable is open unless
`checkOpen` is false, `write`, `end`, and `destroy` are callable, and
`writable`, `writableObjectMode`, and `destroyed` are booleans. Readable-only
streams return false.

### `isReadableStream(stream, options?)`

Return `true` only when `isStream` is true, readable is open unless
`checkOpen` is false, `read` and `destroy` are callable, and `readable`,
`readableObjectMode`, and `destroyed` are booleans. Writable-only streams
return false.

### `isDuplexStream(stream, options?)`

Return `true` exactly when the value satisfies both `isWritableStream` and
`isReadableStream` using the same options.

### `isTransformStream(stream, options?)`

Return `true` exactly when the value is duplex and also has a callable
`_transform` method. A plain duplex stream without `_transform` returns false.

## Bounded Adapter

The root module also exports:

```ts
export type StreamPredicate =
  | 'stream'
  | 'writable'
  | 'readable'
  | 'duplex'
  | 'transform';

export type StreamDescriptor =
  | {kind: 'native'; type: 'stream' | 'readable' | 'writable' | 'duplex' | 'transform' | 'passThrough'; destroyed?: boolean}
  | {kind: 'primitive'; value: null | boolean | number | string}
  | {kind: 'shape'; readable?: boolean; writable?: boolean; readableObjectMode?: boolean; writableObjectMode?: boolean; destroyed?: boolean; methods?: Array<'pipe' | 'read' | 'write' | 'end' | 'destroy' | '_transform'>};

export function run(request: unknown): Promise<unknown>;
```

`run` accepts one plain JSON object and supports two operations:

- `{op: 'version'}` resolves to `{version: '4.0.1'}`.
- `{op: 'check', predicate, value, checkOpen?}` constructs the allowlisted
  descriptor in the candidate child process, calls the corresponding public
  predicate, and resolves to its boolean result.

For a native descriptor, `destroyed: true` means call `destroy()` before the
predicate. A shape descriptor copies only the listed boolean fields and adds
no-op functions for its listed methods. Omitted fields remain absent. Reject
malformed requests, unknown operations, predicates, descriptor kinds, native
types, methods, or non-boolean `checkOpen` values with an `Error`.

The adapter must delegate classification to the five public predicates. It may
use only `node:stream` to construct the allowlisted native values. It must not
accept source text, module names, environment values, executable strings, file
paths, URLs, or arbitrary property names.

## Implementation Notes

The verifier installs the packed package, then invokes only the root `run`
export in bounded UID-isolated child processes. Requests are at most 64 KiB,
responses at most 256 KiB, and each call has a fixed timeout. Candidate code is
never imported into the trusted test process. The verifier owns collection,
network probes, grading, and reward files.

Runtime `instanceof` checks alone are insufficient: the public contract is
structural and includes stream-like plain objects. Do not mutate caller-owned
values in the predicates. File streams, HTTP messages, sockets, browser
streams, TypeScript compiler execution, and exact error wording are outside
the fixed denominator.
