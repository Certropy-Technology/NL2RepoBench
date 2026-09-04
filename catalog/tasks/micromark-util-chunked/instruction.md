# Build `micromark-util-chunked`

## Project Description

Create an installable npm package named `micromark-util-chunked`, version
`2.0.1`, from an empty workspace. The package provides ESM utilities for
mutating arrays safely when insertion lists can be very large.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The package root must expose the named exports `push` and `splice`.
- A clean verifier runs `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Runtime behavior is deterministic and local. Do not use filesystem, clock,
  randomness, subprocesses, browser globals, or network access.

## API Usage Guide

### `splice(list, start, remove, items)`

Import the named function from the package root:

```js
import {splice} from 'micromark-util-chunked'
```

Signature:

```ts
export function splice<T>(list: T[], start: number, remove: number, items: T[]): void
```

Mutate `list` like `Array.prototype.splice`: normalize a negative `start` from
the end, clamp a positive start to the list length, remove up to `remove`
items, and insert every item from `items` at that position. Negative remove
counts behave as zero. The function returns `undefined` and does not return
removed items. Large insertion arrays must work without argument-spread stack
overflows.

### `push(list, items)`

Signature:

```ts
export function push<T>(list: T[], items: T[]): T[]
```

Append all `items` to `list`. When `list` is non-empty, mutate and return the
same `list` object. When `list` is empty, return `items` directly without
copying it. The result preserves item order and supports large arrays.

## Implementation Notes

Keep the package ESM-only with package version `2.0.1` and the exact two named
exports. The runtime dependency closure includes the frozen
`micromark-util-symbol` package only for its public chunk-size constant. Do not
expose additional exports, retain mutable module-global state, or fetch source
or dependencies at runtime.
