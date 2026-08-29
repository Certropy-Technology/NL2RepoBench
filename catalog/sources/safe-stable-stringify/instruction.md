# Project Description

Build a complete installable npm package named `safe-stable-stringify`, version
`2.5.0`, from an empty workspace. It must provide deterministic JSON
serialization that is safe for circular object graphs and BigInt values while
remaining compatible with the useful behavior of `JSON.stringify`.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and both CommonJS and ESM
  package entry points.
- The package root must support `require('safe-stable-stringify')` and
  `import stringify, {configure} from 'safe-stable-stringify'`.
- Commit `package.json`, `package-lock.json` with `lockfileVersion: 3`,
  `index.js`, `index.d.ts`, and the ESM wrapper needed by the package exports.
- The package has no runtime dependencies, npm workspaces, native addons,
  lifecycle hooks, custom loaders, or network behavior. A clean verifier runs
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Runtime behavior is synchronous, deterministic, and local. Do not read
  files, use the clock or randomness, spawn processes, access a TTY, or access
  the network. User callbacks and `toJSON` methods are the only intentional
  user-code callbacks.

# API Usage Guide

## Default export `stringify(value, replacer?, space?)`

The package root's CommonJS value and ESM default export are the same callable
function. It returns JSON text or `undefined` when the root value cannot be
represented. Primitive values follow native JSON behavior, except that BigInt
is serialized as a decimal JSON number by default. Object enumerable string
keys are sorted lexicographically by default, recursively; array order is
preserved. Repeated references are serialized normally, while a reference to
an object on the active traversal path becomes the string `"[Circular]"`.

`replacer` may be a JSON-style function `(key, value)` or an array of string and
number property names. A function receives the parent as `this`, may replace a
value, and may return `undefined`; an array selects unique property names and
preserves that selection order. `space` accepts a number or string and is
bounded to ten spaces/characters like native JSON formatting.

Examples:

```js
const stringify = require('safe-stable-stringify');
stringify({ c: 8, b: [{ z: 6, x: 4 }], a: 3 });
// '{"a":3,"b":[{"x":4,"z":6}],"c":8}'

const value = {}; value.self = value;
stringify(value); // '{"self":"[Circular]"}'
```

## `stringify.configure(options)` and named `configure`

Both names create an independent serializer with these options:

- `bigint`: `true` (default) emits BigInts as decimal JSON numbers, `false`
  omits them, and `'string'` emits them as JSON strings.
- `circularValue`: a string, `null`, `undefined`, `Error`, or `TypeError`.
  The default is `"[Circular]"`; `undefined` omits circular object properties,
  `null` emits JSON null, and either error constructor throws `TypeError`.
- `deterministic`: `true` (default) sorts keys; `false` retains insertion
  order; a comparator `(a, b) => number` orders keys.
- `maximumDepth` and `maximumBreadth`: positive integers limiting traversal.
  Truncated objects/arrays are represented by `[Object]`/`[Array]` or a final
  `"..."`/`"... N items not stringified"` marker as appropriate.
- `strict`: when true, unsupported functions, symbols, non-finite numbers,
  BigInts, and circular values throw instead of being handled safely. Explicit
  `bigint` and `circularValue` options can change those two behaviors.
- `safe`: when true, errors from getters, `toJSON`, and replacers are encoded
  as bounded error strings instead of escaping the serialization call.

Invalid option types throw `TypeError`; positive integer options below one also
throw `RangeError`. `configure` does not mutate its options or share mutable
serializer state with another configured function.

# Implementation Notes

Keep the public surface behind the documented package exports. Preserve native
JSON escaping and number formatting, enumerable-property semantics,
`toJSON`/replacer callback keys and parent binding, stable sorting, typed-array
object output, and active-path cycle detection. The evaluator invokes the
package through an isolated JSON child process; private tests and the Oracle
implementation are not part of the package to implement.
