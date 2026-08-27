# Project Description

Build an installable npm package named `lodash`, version `4.18.1`, from an
empty workspace. The package is a CommonJS utility library for deterministic
array, object, collection, string, number, and JSON-value operations.

This task is a bounded JSON-compatible slice of the frozen Lodash root API.
Implement the documented behavior with your own code. The package must not
download, clone, or embed the upstream implementation or its tests.

# Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64`.
- `package.json` must declare `"name": "lodash"`, `"version": "4.18.1"`,
  `"main": "lodash.js"`, and `"license": "MIT"`.
- The package root is CommonJS: `const _ = require("lodash")`. Do not set a
  `type` field that makes `lodash.js` an ES module.
- The root object must expose `VERSION === "4.18.1"` and every callable named
  below.
- Commit a matching npm v3 `package-lock.json`. The package must install using
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Do not declare `scripts`, runtime dependencies, development dependencies,
  workspaces, native addons, loaders, registry configuration, or lifecycle
  hooks. Runtime JavaScript must already be present in `lodash.js`.
- Runtime network access is unavailable. Behavior must not depend on files,
  services, the clock, random state, locale settings, or environment variables.

All scored inputs are bounded JSON values. Property paths are strings using
dot/bracket notation or arrays of string/integer path segments. Iteratee
arguments use only the documented property-name/path or partial-object
shorthands; JavaScript callbacks never cross the verifier boundary.

# API Usage Guide

All functions below are properties of the CommonJS package root.

## Array utilities

- `chunk(array, size = 1) => Array<Array>` splits from the start into arrays of
  at most `size`, preserving order and a final remainder.
- `compact(array) => Array` removes falsey JSON values: `false`, `null`, `0`,
  and `""`.
- `concat(array, ...values) => Array` returns a new array, appending scalar
  arguments and flattening each array argument by one level.
- `difference(array, values) => Array` keeps values from the first array that
  do not occur in the second under SameValueZero equality. Preserve the first
  array's order and duplicates that are not excluded.
- `drop(array, n = 1)` and `dropRight(array, n = 1)` return the remaining slice
  after removing up to `n` values from the respective end.
- `flatten(array)` removes one nesting level; `flattenDeep(array)` recursively
  removes all array nesting.
- `head(array)` and `last(array)` return the first and final values.
- `initial(array) => Array` returns all but the final value.
- `nth(array, n = 0)` selects index `n`; negative indexes count from the end.
- `take(array, n = 1)` and `takeRight(array, n = 1)` return up to `n` values
  from the respective end.
- `uniq(array) => Array` removes SameValueZero duplicates while retaining the
  first occurrence order.
- `zip(...arrays) => Array<Array>` groups values that have the same index.

Example:

```js
_.chunk([1, 2, 3, 4, 5], 2); // [[1, 2], [3, 4], [5]]
_.flatten([1, [2, [3]]]);     // [1, 2, [3]]
_.uniq([2, 1, 2]);            // [2, 1]
```

## Object and path utilities

- `get(object, path, defaultValue?)` returns the value at `path`, or
  `defaultValue` when the resolved value is `undefined`.
- `has(object, path) => boolean` reports whether every path segment is an own
  property.
- `at(object, paths) => Array` returns path values in the same order as
  `paths`.
- `assign(object, ...sources) => object` copies own enumerable source
  properties from left to right; later sources overwrite earlier values.
- `defaults(object, ...sources) => object` fills only absent or `undefined`
  destination properties, scanning sources from left to right.
- `merge(object, ...sources) => object` recursively merges plain objects and
  merges arrays by index. Later scalar values replace earlier values.
- `pick(object, paths) => object` returns the selected own deep paths while
  preserving their nested shape.
- `omit(object, paths) => object` returns the remaining own data after removing
  the selected deep paths.
- `keys(object)`, `values(object)`, and `toPairs(object)` return own enumerable
  string keys, their values, or `[key, value]` pairs in JavaScript enumeration
  order.
- `invert(object) => object` converts each value to a property key whose value
  is the original key. If values collide, the later key wins.

Only the returned JSON value is observed. In-place mutation of the first
argument by `assign`, `defaults`, or `merge` does not cross the subprocess
boundary, but their returned result must have the behavior above.

## Collection utilities

The supported collections are arrays, strings, and plain JSON objects as noted.

- `map(collection, path) => Array` returns the value at the property path from
  each array/object element.
- `filter(collection, source) => Array` returns elements that recursively
  contain the enumerable properties and values of the partial JSON object
  `source`.
- `find(collection, source)` returns the first element matching that same
  partial-object shorthand.
- `groupBy(collection, path) => object` groups values by the string form of the
  property-path result, preserving encounter order within each group.
- `keyBy(collection, path) => object` indexes values by the string form of the
  property-path result; later entries replace earlier entries for one key.
- `orderBy(collection, paths, orders) => Array` performs stable multi-key
  ordering. Each order is `"asc"` or `"desc"` and corresponds to the path at
  the same index.
- `sortBy(collection, paths) => Array` performs stable ascending multi-key
  ordering.
- `includes(collection, value, fromIndex = 0) => boolean` uses SameValueZero
  for arrays/object values and substring search for strings. Negative indexes
  count from the end.
- `size(collection) => number` returns an array length, JavaScript string
  length, or own enumerable object-key count.

```js
_.map([{ id: 1 }, { id: 2 }], "id"); // [1, 2]
_.groupBy(["one", "two", "three"], "length");
// { "3": ["one", "two"], "5": ["three"] }
```

## String utilities

Inputs and outputs are JavaScript strings.

- `camelCase(string)`, `kebabCase(string)`, and `snakeCase(string)` split words
  at punctuation, whitespace, and case boundaries, normalize their case, and
  join with lower camel case, `-`, or `_` respectively.
- `startCase(string)` joins detected words with spaces and uppercases each
  word's first character while lowercasing the remainder.
- `capitalize(string)` uppercases the first character and lowercases the
  remainder. `upperFirst(string)` and `lowerFirst(string)` change only the
  first character.
- `pad(string, length, chars = " ")` centers a shorter string. An odd number
  of padding characters puts the extra character on the right.
- `padStart(string, length, chars = " ")` and `padEnd(...)` pad one side.
  Repeat and truncate `chars` as needed. Strings already at least `length`
  characters are unchanged.
- `repeat(string, n = 1)` concatenates `n` copies.
- `escape(string)` replaces `&`, `<`, `>`, `"`, and `'` with Lodash HTML
  entities. `unescape(string)` reverses those supported entities.
- `truncate(string, options = {})` limits the result to `options.length`
  (default 30), including `options.omission` (default `"..."`). If a string
  `options.separator` occurs in the retained prefix, cut back to its last
  occurrence before appending the omission. A string no longer than the limit
  is unchanged.

## Number and aggregate utilities

Inputs are finite JSON numbers and arrays/objects of finite numbers.

- `clamp(number, lower, upper)` limits to inclusive bounds.
- `inRange(number, start, end) => boolean` checks `start <= number < end`; if
  `start > end`, swap the bounds first.
- `add(augend, addend)` returns the numeric sum.
- `ceil(number, precision = 0)`, `floor(...)`, and `round(...)` apply the named
  rounding mode at decimal `precision`.
- `max(array)` and `min(array)` return the numeric extrema of a non-empty array.
- `sum(array)` and `mean(array)` return the arithmetic sum and mean.
- `maxBy(array, path)` and `minBy(array, path)` return the first element having
  the largest or smallest finite value at `path`.
- `sumBy(array, path)` and `meanBy(array, path)` aggregate finite values at
  `path`.

## JSON predicates

- `isEqual(left, right) => boolean` recursively compares JSON primitives,
  arrays in order, and plain objects independent of key insertion order.
- `isEmpty(value) => boolean` is true for empty arrays, strings, and plain
  objects, and false for non-empty collections.
- `isPlainObject(value) => boolean` is true for ordinary JSON objects and false
  for arrays, primitives, and `null`.
- `isArray(value)`, `isNumber(value)`, and `isString(value)` distinguish the
  corresponding JSON kinds without coercion.

# Implementation Notes

- Keep results deterministic and JSON-serializable for the documented input
  domain. Values and behaviors that JSON cannot represent are outside scope.
- JavaScript callbacks, function iteratees, regular expressions, symbols,
  `BigInt`, `undefined`, `NaN`, infinities, sparse arrays, typed arrays,
  buffers, dates, maps, sets, custom prototypes, accessors, class instances,
  cycles, wrapper chains, lazy sequences, templates, mixins, FP modules,
  per-method module entry points, browser globals, and CLI behavior are outside
  the scored contract.
- Property-name/path and partial-object shorthand behavior described above is
  required; general callback iteratees are not.
- Preserve stable ordering where specified. Do not sort object keys unless the
  selected API explicitly orders its result.
