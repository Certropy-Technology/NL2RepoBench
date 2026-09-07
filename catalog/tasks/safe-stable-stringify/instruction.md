# Project Description

Build a complete installable npm package named `safe-stable-stringify`, version
`2.5.0`, from an empty workspace. It must provide deterministic JSON
serialization that is safe for circular object graphs and BigInt values while
remaining compatible with the useful behavior of `JSON.stringify`.

## Natural Language Instruction

Create `safe-stable-stringify` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name and package-root import: `safe-stable-stringify`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: no declared third-party runtime packages. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `node:test`. A fixed collection
  contains `52` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── esm/
    └── wrapper.js
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### Default export `stringify(value, replacer?, space?)`

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

### `stringify.configure(options)` and named `configure`

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

## Implementation Notes

Keep the public surface behind the documented package exports. Preserve native
JSON escaping and number formatting, enumerable-property semantics,
`toJSON`/replacer callback keys and parent binding, stable sorting, typed-array
object output, and active-path cycle detection. Keep the implementation
independent of process-global state and external services.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
const stringify = require('safe-stable-stringify');
stringify({ c: 8, b: [{ z: 6, x: 4 }], a: 3 });
// '{"a":3,"b":[{"x":4,"z":6}],"c":8}'

const value = {}; value.self = value;
stringify(value); // '{"self":"[Circular]"}'
```

```javascript
const api = require('safe-stable-stringify');
console.log(typeof api);
```

```javascript
import api from 'safe-stable-stringify';
console.log(typeof api);
```

```javascript
const api = require('safe-stable-stringify');
console.log(typeof api);
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
