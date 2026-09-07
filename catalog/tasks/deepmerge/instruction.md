# Project Description

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

Build an installable CommonJS npm package named `deepmerge`, version `4.3.1`,
from an empty workspace. It deeply merges enumerable own properties of objects
and provides a convenience operation for merging a list of objects. The
package must be self-contained at runtime; the published entry point must not
need a registry package or a build step.

# Supports

- Node.js `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- A CommonJS package whose `package.json` has `name: "deepmerge"`,
  `version: "4.3.1"`, and `main: "index.js"`. Do not make the package ESM.
- The root export is a callable merge function. It must also expose the
  callable convenience method `merge.all`.
- Commit an npm lockfile with `lockfileVersion: 3` matching the package
  metadata. A clean environment must support:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The runtime package has no dependencies, lifecycle hooks, workspaces, native
  addons, loaders, registry configuration, or runtime network access. Build
  tooling and the upstream development-only dependencies are outside the
  published package.

# API Usage Guide

## `merge(target, source, options?)`

The callable package root accepts two values and an optional options object and
returns a new merged value. It does not mutate either input. Plain objects are
merged recursively; properties from `source` take precedence when a property
cannot be recursively merged.

The supported JSON-facing values are plain objects, arrays, strings, finite
numbers, booleans, and `null`. Object keys are enumerable own string keys.
Arrays preserve their order and, by default, are concatenated. A target and
source of different top-level kinds are replaced by a cloned source value.

The default options are:

- `clone: true`: recursively copy mergeable objects and array elements.
- `arrayMerge(target, source, options)`: concatenate the arrays and clone
  mergeable elements. A custom function may return any replacement array.
- `isMergeableObject(value)`: values that are non-null objects other than
  `Date`, `RegExp`, and React elements are recursively copied by default.
- `customMerge(key, options)`: for an overlapping property, may return a
  two-argument merge function for that property; any non-function result uses
  the default merge behavior.

The evaluator exercises these option hooks through deterministic local
scenarios. Implementations must pass the `options` object to custom array and
property merge functions and must add the internal
`cloneUnlessOtherwiseSpecified(value, options)` helper to that object for
array merge functions to use.

Prototype-sensitive keys must be handled defensively. Do not merge a key that
would write through an inherited or non-enumerable property on the target.
An own enumerable JSON key named `__proto__` is data, not permission to alter
the result object's prototype. Preserve enumerable symbol keys when the API is
used with ordinary JavaScript values, although symbols are outside the JSON
adapter.

## `merge.all(objects, options?)`

`merge.all` accepts an array of values and reduces it from left to right using
the same merge semantics, starting with `{}`. It returns a new object. An
argument that is not an array throws an `Error` whose message explains that
the first argument should be an array. An empty array returns `{}`.

# Implementation Notes

Keep the implementation deterministic and CommonJS-compatible. Use only
local JavaScript behavior. Preserve input objects, recursive cloning,
array-concatenation order, custom merge hooks, and prototype-poisoning
protections. The private evaluator invokes the package in a separate child
process through a bounded JSON protocol; callbacks, symbols, dates, regular
expressions, class instances, and object identity remain inside that child.

Do not copy the reference repository or its tests. Do not implement only the
README example: boundary cases include empty arrays, nested arrays of objects,
type replacement, `clone: false`, custom array and property merges, invalid
`merge.all` input, key order, and an own `__proto__` key.

## Natural Language Instruction

Create `deepmerge` from an empty workspace. Implement recursive object and
array merging, `merge.all`, clone behavior, custom merge hooks, and
prototype-sensitive key handling exactly as specified. Keep the callable root
export compatible with `require('deepmerge')`.

```js
import merge from 'deepmerge';
```

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

`package.json` declares CommonJS metadata and `index.js` is both the callable
root export and the home of `merge.all`. No hidden verifier or test file is an
agent-owned project file.

## Examples

```js
const merge = require('deepmerge');
const result = merge({user: {name: 'A'}}, {user: {active: true}});
```

```js
const merge = require('deepmerge');
merge.all([{a: 1}, {b: 2}]);
```

## Error Handling and Boundary Conditions

Neither input is mutated. Arrays concatenate by default, top-level kind
mismatches replace with a clone, and `merge.all` rejects a non-array argument.
Own enumerable `__proto__` data must not change the result prototype. Custom
hooks receive the options object and remain local JavaScript calls.
