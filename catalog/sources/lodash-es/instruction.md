# Project Description

Build an installable npm package named `lodash-es`, version `4.18.1`, from an
empty workspace. The package is an ESM utility library derived from the pinned
Lodash behavior contract. This task evaluates a deterministic, JSON-safe slice
of the package rather than browser builds, the FP build, or every internal
Lodash helper.

# Supports

- Run on Node.js `24.19.0` with npm `11.17.0` on Linux x86-64.
- `package.json` must declare `name: "lodash-es"`, `version: "4.18.1"`,
  `type: "module"`, and an ESM entry point at `index.js`.
- The package must be installable with
  `npm ci --offline --ignore-scripts --no-audit --no-fund` using a v3
  `package-lock.json` and no runtime or development dependencies.
- Runtime execution is offline and must not depend on current time, random
  state, environment variables, files outside the package, or network services.
- The root entry point must expose each listed function as a named ESM export.
  A default export containing the same named functions is also required.

# API Usage Guide

Arguments and ordinary results in the scored contract are JSON-compatible
values. The documented `undefined` results are represented by an absent JSON
`value` field at the verifier boundary. Functions must be deterministic and
must not mutate an input supplied by the caller; none of the functions below
are mutating in this task.

- `chunk(array, size = 1) => any[][]`: split an array into consecutive chunks.
  Omitting `size` uses `1`; a non-positive size returns an empty array.
- `compact(array) => any[]`: remove falsey values while preserving order.
- `concat(value, ...values) => any[]`: concatenate values, flattening one level
  for array arguments.
- `difference(array, ...values) => any[]`: return values from the first array
  that do not occur in the other arrays, preserving first-array order.
- `drop(array, n = 1) => any[]` and `dropRight(array, n = 1) => any[]`: remove
  up to `n` items from the corresponding side.
- `flatten(array) => any[]` and `flattenDeep(array) => any[]`: flatten one
  level or all nested array levels respectively.
- `head(array) => any` and `last(array) => any`: return the first or last item;
  JSON test inputs are non-empty.
- `map(collection, iteratee) => any[]`: support property-name iteratees such
  as `"name"` and iteratee pairs such as `["active", true]`.
- `filter(collection, predicate) => any[]` and
  `find(collection, predicate) => object|undefined`: support object-match
  predicates such as `{ active: true }`.
- `groupBy(collection, iteratee) => object` and
  `keyBy(collection, iteratee) => object`: support property-name iteratees and
  string `length` values, using Lodash key coercion.
- `get(object, path, defaultValue) => any` and `has(object, path) => boolean`:
  support dotted paths and array paths for JSON objects.
- `isEqual(left, right) => boolean`: recursively compare JSON arrays and
  objects without depending on key insertion order.
- `cloneDeep(value) => any`: deep-copy JSON arrays and objects.
- `sumBy(collection, iteratee) => number` and
  `maxBy(collection, iteratee) => object|undefined`: support property-name
  iteratees.
- `orderBy(collection, iteratees, orders) => any[]`: support property-name
  iteratees and `"asc"`/`"desc"` order strings.
- `uniq(array) => any[]`: remove duplicate JSON-compatible primitive values and
  preserve first occurrence order.
- `zip(...arrays) => any[][]`: create rows by index, using `null` for missing
  JSON values in the scored domain.
- `camelCase(string) => string`, `kebabCase(string) => string`, and
  `startCase(string) => string`: normalize word boundaries and case according
  to Lodash behavior for ordinary ASCII and Unicode-letter input.
- `toString(value) => string`: use Lodash string coercion for JSON-compatible
  values; in particular, finite numbers use their ordinary decimal spelling.
- `toNumber(value) => number`: convert JSON-compatible numeric strings and
  numbers using Lodash numeric coercion.

# Implementation Notes

Only the root named exports and their default-export aliases are scored. The
package may expose additional files, but it must not require CommonJS loaders,
bundlers, TypeScript, native addons, lifecycle scripts, or registry access.
The upstream browser/UMD distributions, FP conversion helpers, CLI, docs, and
performance harness are outside this bounded contract. Do not copy the private
tests or reference implementation into the candidate workspace.
