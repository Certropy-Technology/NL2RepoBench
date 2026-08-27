# Project Description

Build an installable CommonJS npm package named `ramda` from an empty
workspace. The package is a deterministic, dependency-free functional utility
library. This task scores a JSON-safe bounded slice of the upstream Ramda
package, not its complete higher-order or fantasy-land surface.

# Supports

- Node.js `24.19.0` and npm `11.17.0`.
- Package name `ramda`, version `0.32.0`, and a CommonJS root entry point.
- A committed `package-lock.json` with `lockfileVersion: 3`.
- No runtime dependencies, lifecycle scripts, workspaces, native addons,
  custom loaders, registry configuration, or network access.
- The root module must expose the named functions below through
  `require('ramda')`.

Calls are made through a JSON request/response boundary. Arguments and results
are JSON values: null, booleans, finite numbers, strings, arrays, and plain
objects. Functions, callbacks, symbols, BigInts, regular expressions, dates,
custom prototypes, sparse arrays, cyclic values, transducers, placeholders,
partial application, and browser/ESM subpath builds are outside this task.
Each listed function is called directly with all of its arguments.

# API Usage Guide

## Numeric functions

- `add(a, b)`, `subtract(a, b)`, `multiply(a, b)`, `divide(a, b)`, and
  `modulo(a, b)` use JavaScript numeric operation order.
- `mathMod(a, b)` returns the non-negative modulus for a positive divisor.
- `clamp(min, max, value)` constrains a comparable value to inclusive bounds.
- `inc(value)`, `dec(value)`, and `negate(value)` return numeric transforms.
- `sum(values)`, `product(values)`, `mean(values)`, and `median(values)` reduce
  numeric arrays without mutating them. `median` sorts values numerically.

## Sequence functions

- `append(value, list)` and `prepend(value, list)` return new arrays.
- `concat(left, right)` joins compatible arrays.
- `insert(index, value, list)` and `insertAll(index, values, list)` insert
  before the supplied index.
- `remove(start, count, list)`, `update(index, value, list)`, and
  `slice(from, to, list)` return non-mutating array changes. `slice` accepts
  negative indexes with JavaScript slice semantics.
- `take(count, list)`, `drop(count, list)`, `takeLast(count, list)`, and
  `dropLast(count, list)` work on array prefixes or suffixes.
- `reverse(list)`, `range(from, to)`, `flatten(value)`, and `uniq(list)` are
  non-mutating. `range` includes `from` and excludes `to`; `flatten` is
  recursive; `uniq` keeps first occurrences.
- `difference(left, right)`, `union(left, right)`, and `without(values, list)`
  use structural equality and preserve the observable order from their left
  input. `intersection(left, right)` uses structural equality and follows the
  observable order from its right input.
- `zip(left, right)` stops at the shorter array. `zipObj(keys, values)` maps
  keys to values until either input is exhausted.
- `head(list)`, `last(list)`, `tail(list)`, `init(list)`, `nth(index, list)`,
  and `length(value)` return normal sequence observations. Negative `nth`
  indexes count from the end.

## Object functions

- `assoc(key, value, object)` and `assocPath(path, value, object)` return
  copies with an updated direct or nested value, creating plain nested objects
  when needed.
- `dissoc(key, object)` and `dissocPath(path, object)` return copies without
  the requested direct or nested property.
- `path(path, object)`, `paths(paths, object)`, `prop(key, object)`, and
  `props(keys, object)` read direct or nested values. A missing value is
  observed as JSON `null` through this boundary.
- `pick(keys, object)` retains existing requested properties. `pickAll(keys,
  object)` may include missing properties internally, but JSON serialization
  omits their undefined object values. `omit(keys, object)` removes keys.
- `mergeLeft(left, right)`, `mergeRight(left, right)`, `mergeAll(objects)`, and
  `mergeDeepRight(left, right)` merge plain objects without mutating inputs.
  Left/right functions choose the indicated side for conflicts; deep merge
  recurses only through plain nested objects.
- `keys(object)` and `values(object)` use JavaScript enumerable-own-property
  enumeration order. `has(key, object)` and `hasPath(path, object)` check own
  property presence. `isEmpty(value)` recognizes empty JSON arrays and plain
  objects.

## Equality and string functions

- `equals(left, right)` performs structural equality for JSON values.
- `includes(value, list)`, `indexOf(value, list)`, and `lastIndexOf(value,
  list)` perform structural membership/search and return `-1` when absent.
- `toLower(text)`, `toUpper(text)`, and `trim(text)` follow JavaScript string
  behavior.
- `split(separator, text)` accepts a string separator and returns an array.
  `join(separator, values)` returns a string.

# Implementation Notes

Preserve input arrays and objects. The package must be installable with an
offline npm lock and must not execute scripts at install. Do not add a build
step, generated download, or dependency that requires network access. The
task's JSON boundary deliberately does not require currying or callback-based
collection functions, even though the full upstream project offers them.
