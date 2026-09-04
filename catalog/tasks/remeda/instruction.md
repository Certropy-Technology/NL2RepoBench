# Build `remeda`

## Project Description

Create a complete installable npm package named `remeda`, version `2.0.0`, from
an empty workspace. Remeda is a functional utility library for JavaScript and
TypeScript. This task evaluates a deterministic JSON-safe slice of its public
runtime API. The package must expose the named exports described below from its
package root.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The root package must be importable with `import * as R from "remeda"`.
- `package.json` must identify `remeda` version `2.0.0`, use ESM-compatible
  exports for `./dist/index.js`, and include a lockfile with `lockfileVersion: 3`.
- The package has no runtime dependencies. A clean verifier installs it with
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Do not use network access, native addons, lifecycle hooks, custom loaders,
  subprocesses, environment state, clocks, randomness, or filesystem reads at
  runtime. Return ordinary JSON-compatible values for the operations below.
- This is a repository-generation task: implement the package from this
  specification rather than copying a reference repository or hidden tests.

## API Usage Guide

All listed functions support Remeda's data-first form and, where shown, a
data-last form. Data-first calls place the data first. Data-last calls return a
function that accepts the data last.

### Array operations

- `map(data, callback)` and `map(callback)(data)` return a new array containing
  callback results. The callback receives `(value, index, data)`.
- `filter(data, predicate)` and `filter(predicate)(data)` preserve items for
  which the predicate is truthy.
- `take(data, n)` / `take(n)(data)` return the first `n` items. Negative `n`
  returns an empty array.
- `drop(data, n)` / `drop(n)(data)` remove the first `n` items. Negative `n`
  returns a shallow copy of the input.
- `chunk(data, size)` / `chunk(size)(data)` split an array into consecutive
  chunks. `size <= 0` raises `RangeError`.
- `unique(data)` / `unique()(data)` preserve the first occurrence of each value,
  using JavaScript `Set` equality.
- `difference(data, other)` / `difference(other)(data)` remove matching values
  from `data` as a multiset while preserving order.
- `partition(data, predicate)` / `partition(predicate)(data)` return
  `[matching, nonMatching]`, preserving order in both arrays.
- `groupBy(data, callback)` / `groupBy(callback)(data)` return an object whose
  keys are callback results; callback results of `undefined` exclude an item.
- `indexBy(data, callback)` / `indexBy(callback)(data)` return an object keyed by
  callback results; a later item replaces an earlier item with the same key.
- `zip(first, second)` / `zip(second)(first)` pair equal-position items up to
  the shorter input.
- `range(start, end)` and `range(start, {end, step})`, or `range(end)(start)`
  and `range({end, step})(start)`, return an end-exclusive numeric sequence.
  `step` defaults to `1` and zero raises `RangeError`.
- `reverse(data)` / `reverse()(data)` return a reversed shallow copy.
- `sortBy(data, rules...)` / `sortBy(rules...)(data)` return a stable sorted
  shallow copy. Each rule is a callback or `[callback, "desc"]`; earlier rules
  have precedence.

### Numeric and object operations

- `add(value, addend)` / `add(addend)(value)` and `multiply(value, factor)` /
  `multiply(factor)(value)` return arithmetic results.
- `sum(data)` / `sum()(data)` return the numeric sum, or `0` for an empty array.
- `mean(data)` / `mean()(data)` return the arithmetic mean, or `undefined` for
  an empty array.
- `clamp(value, {min, max})` / `clamp({min, max})(value)` constrain a number
  inclusively; either bound may be omitted.
- `pick(data, keys)` / `pick(keys)(data)` return a new object containing the
  requested existing properties in key order.
- `omit(data, keys)` / `omit(keys)(data)` return a shallow copy without keys.
- `merge(destination, source)` / `merge(source)(destination)` shallow-merge
  enumerable own properties, with source values taking precedence.
- `mergeDeep(destination, source)` / `mergeDeep(source)(destination)` recurse
  only when both overlapping values are plain objects.
- `pipe(data, ...functions)` applies functions from left to right and returns
  the final value. `identity(value)` returns its input unchanged.

### Predicates and strings

- `isDeepEqual(data, other)` / `isDeepEqual(other)(data)` compare JSON-like
  primitives, arrays, and plain objects structurally and recursively.
- `isNullish(value)`, `isString(value)`, and `isNumber(value)` return booleans.
- `capitalize(text)` uppercases the first character and leaves the remainder;
  `uncapitalize(text)` lowercases the first character.
- `toCamelCase(text)`, `toKebabCase(text)`, and `toSnakeCase(text)` normalize
  word separators and case as named.
- `truncate(text, length, options?)` returns the original text when within the
  limit; otherwise it uses `options.omission` (default `"..."`) and keeps the
  result at most `length` UTF-16 code units.

Callbacks in the hidden tests use only ordinary JSON data and deterministic
callback descriptors (identity, property lookup, numeric remainder, and
string length). Implementations must still pass the callback's `(value, index,
data)` arguments through correctly.

## Implementation Notes

Keep the package root and named export behavior compatible with ESM consumers.
Data-last calls must not mutate the input and must preserve callback order.
Array-returning operations must return fresh arrays. Object operations must not
mutate their inputs. Property keys are ordinary JSON strings in the scored
contract. Unsupported values such as functions, symbols, maps, sets, dates,
and typed arrays are outside this task's JSON adapter boundary.
