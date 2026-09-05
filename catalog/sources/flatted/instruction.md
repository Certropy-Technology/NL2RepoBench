# Project Description

Build an installable npm package named `flatted` from an empty workspace. The
package provides JSON-compatible serialization and parsing while preserving
circular references and repeated object identity. Its wire format is a JSON
array whose first element represents the root value and whose later elements
hold referenced strings, arrays, and objects.

# Natural Language Instruction

Build `flatted` from an empty workspace. Implement the dual ESM/CommonJS root
exports, TypeScript declaration entry, table-based graph encoding, graph
reconstruction, replacer/reviver behavior, and helper round trips described
below. Preserve JavaScript property order, object identity, circular links,
native JSON error behavior, and input immutability. Do not substitute ordinary
`JSON.stringify` because it cannot represent the required graph semantics.

# Supports

- Node.js 24.19.0 and npm 11.17.0 on Linux amd64 with glibc.
- Package name `flatted`, version `3.4.4`, and a committed npm lockfile with
  `lockfileVersion: 3`.
- Named exports `parse`, `stringify`, `toJSON`, and `fromJSON` from both ESM
  import and CommonJS `require('flatted')` at the package root.
- TypeScript declarations at `types/index.d.ts` through the package root
  `types` condition.
- No runtime dependencies, lifecycle scripts, workspaces, native addons,
  custom loaders, registry configuration, or runtime network access.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── esm/index.js
├── cjs/index.js
└── types/index.d.ts
```

The package root must expose the same four public operations from both module
systems. `package.json` maps ESM and CommonJS consumers to the corresponding
entries and exposes `types/index.d.ts`. Keep implementation files local to this
tree; no generated cache, verifier code, fixture, or runtime download belongs
in the candidate workspace.
- JSON-compatible primitive values, plain objects, arrays, repeated object
  references, and circular object graphs. Functions, symbols, sockets, and
  class-specific internal state are outside the serialization contract, just
  as they are for ordinary JSON.

# API Usage Guide

## `stringify`

Import path: `flatted`.

Signature:

```ts
stringify(
  value: any,
  replacer?: ((this: any, key: string, value: any) => any) |
    (string | number)[] | null,
  space?: string | number,
): string
```

Return a primitive string containing the flatted wire representation. Traverse
arrays in index order and objects in `Object.keys` order. The first encountered
root, object, array, or string receives the next zero-based table index.
References to table values are encoded as decimal index strings; actual string
values are themselves stored once in the table, so strings that look like
indices remain unambiguous. Numbers, booleans, and `null` remain inline.

For example:

```js
const value = {};
value.self = value;
stringify(value); // '[{"self":"0"}]'

const array = [];
array.push(array);
stringify(array); // '[["0"]]'

stringify({name: 'Ada'}); // '[{"name":"1"},"Ada"]'
```

Repeated references must reuse one index and recover as the same object after
parsing. Do not mutate the input graph. Honor `toJSON` methods in the same
places as `JSON.stringify`.

The optional arguments follow `JSON.stringify` semantics:

- A function replacer is called with the owning value as `this`, first for the
  root key `""`, then for properties and array positions. Its return value is
  what gets serialized; returning `undefined` omits object properties.
- An array replacer is a property allowlist. String and number entries select
  matching object keys at every object level; array positions still serialize
  normally.
- Numeric indentation is clamped to ten spaces. String indentation is
  truncated to ten UTF-16 code units. Formatting is applied to every table
  entry consistently with `JSON.stringify`.

Primitive roots are supported. Representative results are `stringify(null) ===
'[null]'`, `stringify(1) === '[1]'`, and `stringify('x') === '["x"]'`.

## `parse`

Import path: `flatted`.

Signature:

```ts
parse(
  text: string,
  reviver?: (this: any, key: string, value: any) => any,
): any
```

Parse only the flatted wire format produced by `stringify`, rebuild circular
and repeated references, and return the root value. Invalid JSON or malformed
input follows the native parsing failure behavior, including `SyntaxError` for
invalid JSON text. Never evaluate strings as code.

When supplied, invoke the reviver bottom-up with the containing object as
`this`, including a final call for root key `""`, following `JSON.parse`
reviver behavior. A returned replacement becomes the property value; returning
`undefined` deletes an object property. References visible to the reviver must
already resolve to the reconstructed graph where required.

For example:

```js
const value = parse('[{"self":"0"}]');
value.self === value; // true

parse('[{"count":1}]', (key, value) =>
  key === 'count' ? value + 1 : value
); // {count: 2}
```

## `toJSON`

Import path: `flatted`.

Signature: `toJSON(value: any): any`.

Return the JSON-compatible table value represented by `JSON.parse(stringify(value))`.
The result itself is acyclic and can be passed to native `JSON.stringify`.
For a self-referencing object, `toJSON(value)` is the array
`[{"self":"0"}]`. Do not mutate the input.

## `fromJSON`

Import path: `flatted`.

Signature: `fromJSON(value: any): any`.

Interpret a previously produced `toJSON` table as flatted data and reconstruct
its circular and repeated references. This is equivalent in observable result
to `parse(JSON.stringify(value))`. Do not mutate the table input.

# Implementation Notes

Keep the implementation deterministic and free of ambient state. The package
must work entirely offline after installation. Preserve JavaScript property
ordering and native JSON handling of unsupported property values, sparse array
positions, non-finite numbers, escaping, and indentation.

Evaluation installs a packed copy with lifecycle scripts disabled. Candidate
code runs as an unprivileged process behind a bounded task-specific JSON
adapter. The adapter constructs circular fixtures inside that child and returns
only graph observations; the trusted verifier never imports candidate code.
Private tests, the Oracle implementation, and verifier internals are not part
of the package to implement.

# Examples

```js
import {stringify, parse} from 'flatted';
const node = {name: 'root'};
node.self = node;
const restored = parse(stringify(node));
restored.self === restored; // true
```

```js
import {toJSON, fromJSON} from 'flatted';
const table = toJSON({items: ['a', 'a']});
const value = fromJSON(table);
value.items[0] === value.items[1]; // true for the shared table entry
```

```js
const flatted = require('flatted');
flatted.stringify({ok: true});
```

# Error Handling and Boundary Conditions

Malformed wire text must fail with a native parsing error and must never be
evaluated as JavaScript. Repeated references must resolve to the same object,
while primitive roots remain primitive after a round trip. Replacer and
reviver callbacks follow the documented `JSON.stringify`/`JSON.parse` order;
returning `undefined` from a replacer or reviver has its documented omission or
deletion effect. Do not mutate input graphs or tables. Agent, candidate,
verifier, Oracle, controls, and runtime use NoNetwork and cannot fetch package
metadata or source code during execution.
