# Build `quick-lru`

## Project Description

Create an installable npm package named `quick-lru`, version `7.3.0`, from an empty workspace.
It is a small `Map` subclass implementing a Least Recently Used cache with a dual-cache design.
The implementation must preserve JavaScript key and value identity while providing bounded
recency operations, optional lazy time-to-live expiration, and explicit eviction controls.

## Supports

- Node.js `24.19.0` with npm `11.17.0` on Linux amd64 with glibc.
- An ESM package with `package.json` containing `name`, `version`, `type: "module"`, and an
  export map that exposes `index.js` and `index.d.ts` from the package root.
- The default export `QuickLRU` and no runtime or development dependency in the submitted
  package. Include a committed npm v3 `package-lock.json` so `npm ci --offline --ignore-scripts
  --no-audit --no-fund` succeeds in a clean verifier.
- A self-contained implementation. Do not use network services, native addons, workspaces,
  install hooks, custom loaders, or a globally installed copy of the package.

## API Usage Guide

### `QuickLRU` and `Options`

`import QuickLRU from 'quick-lru'` returns a class extending `Map`.
Construct it with `new QuickLRU({maxSize, maxAge?, onEviction?})`. `maxSize` is required and in
normal typed usage is a number greater than zero; the runtime accepts any truthy value that
compares greater than zero. `maxAge` defaults to `Infinity`; an explicit numeric zero is invalid.
`onEviction(key, value)` is optional and is called immediately before automatic LRU
eviction, TTL expiration, or `evict()` removal, but not for `delete()` or `clear()`.

The cache may temporarily contain up to twice `maxSize` entries because it keeps a recent and an
old `Map`; the observable `size` is capped at `maxSize` and counts each logical key once.

### Entry operations

- `set(key, value, options?)` stores any JavaScript key/value and returns the same cache. An
  optional `{maxAge}` overrides the constructor TTL for that entry. Non-numeric per-entry values
  are ignored. Re-setting a recent key updates its value and refreshes its expiry while retaining its
  current insertion position; setting an old key creates a current entry.
- `get(key)` returns the value or `undefined`. Reading an old live entry promotes it to recent;
  an expired entry is lazily removed and invokes `onEviction`.
- `has(key)` returns a boolean and lazily removes expired entries. `peek(key)` returns a value
  without changing recency and also lazily removes expired entries.
- `delete(key)` removes one key and returns whether it existed. `clear()` removes all entries
  without eviction callbacks.
- `expiresIn(key)` returns the exact remaining milliseconds, `Infinity` for an entry without expiry,
  or `undefined` for a missing entry. It does not evict or change recency, so an expired entry may
  return a negative value until another lazy-expiration operation observes it.

### Iteration and capacity

- `entriesAscending()` and `entries()` yield live `[key, value]` pairs oldest first. During a
  dual-cache rotation, iteration can expose more live entries than the capped `size` getter.
- `entriesDescending()` yields live pairs newest first. `keys()`, `values()`, and the default
  iterator follow ascending order and omit expired entries.
- `forEach(callback, thisArg?)` calls the callback as `callback(value, key, cache)` in ascending
  order and uses `thisArg` as its `this` value.
- `size`, `maxSize`, and `maxAge` are read-only getters. `toString()` returns
  `QuickLRU(<size>/<maxSize>)`, and `cache[Symbol.toStringTag]` is `QuickLRU`.
- `resize(newSize)` requires a positive number, changes the capacity, keeps the newest entries
  when shrinking, and invokes `onEviction` for entries discarded during the resize. Increasing
  capacity preserves live entries.
- `evict(count = 1)` removes the least-recently-used live entries, coercing `count` with
  `Number()` and truncating fractional values. Non-positive, `NaN`, and empty-cache requests are
  no-ops; at least one live entry remains. It invokes `onEviction` for removed entries.

### Example

```js
import QuickLRU from 'quick-lru';

const cache = new QuickLRU({maxSize: 2});
cache.set('user:1', {name: 'Ada'});
cache.set('user:2', {name: 'Lin'});
cache.get('user:1');
cache.set('user:3', {name: 'Sam'});
// The oldest live entry is evicted; user:1 was promoted by get().
```

## Implementation Notes

Keep the package root and declaration file compatible with Node ESM resolution. Preserve Map
identity semantics for object and symbol keys, insertion/recency order, `undefined` values, and
the distinction between `Infinity`, an expired entry, and a missing entry. Expiration is lazy and
uses the runtime clock; do not introduce polling timers. Eviction callbacks must observe the
entry before it disappears, and user values must not be stringified or mutated. The frozen
verifier exercises constructor validation, all public methods, iteration order, callback timing,
TTL behavior, resize/evict boundaries, and package metadata through a bounded child-process
boundary.
