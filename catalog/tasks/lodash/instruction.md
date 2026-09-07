# Project Description

Build an installable npm package named `lodash`, version `4.18.1`, from an
empty workspace. It is a CommonJS utility library for deterministic array,
object, collection, string, number, and JSON-value operations. This task is a
bounded JSON-compatible slice of the frozen Lodash root API, not the complete
upstream distribution.

# Natural Language Instruction

Create the `lodash` project from an empty `workspace/`. Provide a CommonJS
root object that exposes `VERSION` and every callable listed in the API guide.
Implement the array, object/path, collection, string, number/aggregate, and
JSON predicate families for the stated JSON input domain. Preserve order and
determinism wherever the contract says so, and keep the documented root API
usable through `const _ = require('lodash')`.

Do not retrieve or embed the upstream implementation or tests. Do not add
callbacks, executable iteratees, browser or CLI behavior, wrapper chains,
templates, mixins, FP entry points, or other excluded surfaces. The generated
package must be self-contained and runtime-offline.

# Supports

- Use Node.js `24.19.0` and npm `11.17.0` on Linux amd64.
- `package.json` must declare `name: "lodash"`, `version: "4.18.1"`,
  `main: "lodash.js"`, and license `MIT`. The root is CommonJS and must not
  use a `type` field that makes `lodash.js` an ES module.
- The root object exposes `VERSION === "4.18.1"` and the 71 selected
  functions in the API guide. Inputs are bounded JSON values; callbacks and
  non-JSON JavaScript values are outside scope.
- Commit a matching npm v3 `package-lock.json`. Offline installation must
  succeed with `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declare no scripts, runtime or development dependencies, workspaces, native
  addons, loaders, registry configuration, lifecycle hooks, or network access.
  Runtime behavior must not depend on files outside the package, time,
  randomness, locale settings, or environment variables.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── lodash.js
└── LICENSE
```

`package.json` owns package identity, CommonJS entry metadata, and the empty
dependency policy. `lodash.js` is the installed root implementation and must
export the documented callable properties plus `VERSION`. `LICENSE` records
the declared MIT license. No build script, test directory, browser bundle,
per-method module, or private evaluator file is needed by the public project.

The public package import is the root CommonJS `lodash` entry; consumers use
the `_` root object rather than an internal module path.

# API Usage Guide

All listed functions are properties of the CommonJS root object. Return values
are observed as JSON values. Property paths are strings using dot/bracket
notation or arrays of string/integer segments. Iteratee arguments use only the
documented property-name/path or partial-object shorthands.

## Array utilities

- `chunk(array, size = 1) => Array<Array>` splits from the start into chunks of
  at most `size`, preserving order and the final remainder.
- `compact(array) => Array` removes JSON falsey values `false`, `null`, `0`,
  and `""`; `concat(array, ...values) => Array` returns a new array and
  flattens each array argument by one level.
- `difference(array, values) => Array` removes values occurring in `values`
  under SameValueZero equality, preserving first-array order and retained
  duplicates. `drop`, `dropRight`, `take`, and `takeRight` use their default
  `n = 1` and remove/retain up to `n` values from the named side.
- `flatten(array) => Array` removes one nesting level; `flattenDeep(array) =>
  Array` recursively removes all array nesting.
- `head(array)`, `last(array)`, `initial(array)`, and `nth(array, n = 0)`
  select the first, final, all-but-final, or indexed value; negative `nth`
  indexes count from the end. `uniq(array)` removes SameValueZero duplicates
  while retaining first occurrence order. `zip(...arrays)` groups values by
  index.

## Object and path utilities

- `get(object, path, defaultValue?)` returns the path value or the default when
  the resolved value is `undefined`; `has(object, path) => boolean` requires
  every segment to be an own property; `at(object, paths) => Array` returns
  values in path-list order.
- `assign(object, ...sources)`, `defaults(object, ...sources)`, and
  `merge(object, ...sources)` return the destination after left-to-right own
  property copying, absent/undefined filling, or recursive plain-object and
  index-wise array merging. Later scalar values replace earlier values for
  `merge`.
- `pick(object, paths)` and `omit(object, paths)` preserve nested shape while
  selecting or removing own deep paths. `keys`, `values`, and `toPairs` return
  own enumerable string keys, values, or pairs in JavaScript enumeration
  order. `invert(object)` converts each value to a key; a collision is won by
  the later source key.

## Collection utilities

- `map(collection, path) => Array` reads a property path from each array or
  object element. `filter(collection, source) => Array` and
  `find(collection, source)` use recursive partial JSON-object matching;
  `find` returns the first match.
- `groupBy(collection, path)` groups by the string form of the path result,
  preserving encounter order. `keyBy(collection, path)` indexes similarly and
  lets later entries replace earlier values.
- `orderBy(collection, paths, orders)` performs stable multi-key ordering;
  each order is `"asc"` or `"desc"`. `sortBy(collection, paths)` performs
  stable ascending multi-key ordering.
- `includes(collection, value, fromIndex = 0)` uses SameValueZero for arrays
  and object values and substring search for strings; negative indexes count
  from the end. `size(collection)` returns array length, JavaScript string
  length, or own enumerable object-key count.

## String utilities

`camelCase`, `kebabCase`, `snakeCase`, and `startCase` split words at
punctuation, whitespace, and case boundaries and normalize case before joining
with lower camel case, `-`, `_`, or spaces. `capitalize` uppercases the first
character and lowercases the rest; `upperFirst` and `lowerFirst` change only
that character. `pad`, `padStart`, and `padEnd` repeat/truncate `chars` to
reach the requested length; `pad` centers and puts an odd extra character on
the right. `repeat(string, n = 1)` concatenates copies. `escape` and
`unescape` handle Lodash HTML entities for `&`, `<`, `>`, `"`, and `'`.
`truncate(string, options = {})` honors length 30, omission `"..."`, and an
optional separator in the retained prefix.

## Number and aggregate utilities

`clamp(number, lower, upper)` limits to inclusive bounds;
`inRange(number, start, end)` checks a half-open interval and swaps reversed
bounds. `add` sums two numbers. `ceil`, `floor`, and `round` apply their
named decimal-precision mode. `max`, `min`, `sum`, and `mean` operate on
finite-number arrays. `maxBy`, `minBy`, `sumBy`, and `meanBy` use a property
path and return/select or aggregate finite values.

## JSON predicates

`isEqual` recursively compares JSON primitives, arrays in order, and plain
objects independent of key insertion order. `isEmpty` recognizes empty
arrays, strings, and plain objects. `isPlainObject`, `isArray`, `isNumber`,
and `isString` distinguish JSON object, array, number, and string kinds without
coercion.

# Implementation Notes

- Keep every result JSON-serializable and deterministic for the stated input
  domain. Do not sort object keys unless the selected API explicitly orders a
  result; preserve stable collection order.
- Do not mutate caller inputs for the documented operations. Destination
  mutation by `assign`, `defaults`, and `merge` is not observed across the
  process boundary, but their returned values must be correct.
- JavaScript callbacks, regular expressions, symbols, `BigInt`, `undefined`,
  `NaN`, infinities, sparse arrays, typed arrays, buffers, dates, maps, sets,
  custom prototypes, accessors, class instances, cycles, wrapper chains, lazy
  sequences, templates, mixins, FP modules, per-method modules, browser
  globals, and CLI behavior are outside this contract.
- Property-name/path and partial-object shorthand behavior is required;
  general executable callback iteratees are not.

# Examples

```js
const _ = require('lodash');

_.chunk([1, 2, 3, 4, 5], 2); // [[1, 2], [3, 4], [5]]
_.map([{id: 1}, {id: 2}], 'id'); // [1, 2]
```

```js
const source = {user: {name: 'Ada'}, active: true};
_.get(source, 'user.name'); // 'Ada'
_.filter([source, {active: false}], {active: true}); // [source]
```

# Error Handling and Boundary Conditions

- Empty arrays and strings produce their documented empty selections or
  aggregate results; `find`, `head`, `last`, `max`, and `min` retain the
  stated `undefined`/non-empty input domain behavior.
- Path helpers accept dotted/bracket strings and segment arrays. Missing paths
  resolve to defaults or false without reading inherited properties.
- Stable ties preserve encounter order in `orderBy`, `sortBy`, `groupBy`, and
  `keyBy`; `zip` represents missing JSON values as the bounded contract
  requires. String operations use JavaScript string semantics.
- Do not coerce unsupported non-JSON values into scored results. Do not read
  files or services, execute supplied code, or allow network, current time,
  random state, locale, or environment variables to influence output.
