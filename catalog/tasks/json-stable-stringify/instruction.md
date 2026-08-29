# Project Description

Implement the npm package `json-stable-stringify` from an empty workspace. The package must expose the CommonJS entry point `require('json-stable-stringify')` and return deterministic JSON text: object keys are sorted lexicographically by default while array order is preserved.

# Supports

- Node.js 24.19.0 on Linux amd64 with CommonJS `index.js` as the package entry point.
- Runtime dependencies declared in `package.json` and installed by `npm ci --ignore-scripts`.
- JSON-compatible values, including nested objects, arrays, strings, numbers, booleans, `null`, `undefined`, `toJSON` methods, and circular references.

# API Usage Guide

`const stringify = require('json-stable-stringify')`

`stringify(obj, opts?) -> string | undefined`

The first argument is the value to serialize. Primitive values follow native `JSON.stringify` semantics. An object is emitted with its enumerable string keys in deterministic order, recursively. Arrays retain their original order; an undefined array element is represented as `null`; object properties whose serialized value is undefined are omitted. The result is a JSON string, or `undefined` when the root value is not JSON-representable.

`opts` may be an options object or a comparator function; passing `null` as the second argument is not supported and throws `TypeError`. `opts.space` accepts a string indentation unit or a number of spaces (bounded by the normal string repetition behavior). `opts.cmp` or a function supplied directly as `opts` compares `{ key, value }` records and determines object-key order. A comparator with a third argument receives `{ get(key) }` for the object currently being sorted. `opts.replacer`, when supplied, is invoked with `(key, value)` and with its `this` value set to the parent container; it may replace a value or return `undefined` to omit it. `opts.cycles: true` serializes repeated object references on the active path as the string `"__cycle__"`; otherwise circular input throws `TypeError`. `opts.collapseEmpty: true` keeps empty arrays and objects compact when pretty-printing. A provided non-boolean `collapseEmpty` throws `TypeError`.

Examples:

```js
const stringify = require('json-stable-stringify');
stringify({ c: 8, b: [{ z: 6, x: 4 }], a: 3 });
// '{"a":3,"b":[{"x":4,"z":6}],"c":8}'

stringify({ b: 1, a: { y: 2, x: 1 } }, { space: 2 });
// '{\n  "a": {\n    "x": 1,\n    "y": 2\n  },\n  "b": 1\n}'
```

# Implementation Notes

Keep the package self-contained behind the documented CommonJS entry point. Do not add network access, lifecycle installation hooks, generated build output, or a dependency on the reference repository. Preserve native JSON escaping and number handling, stable recursive ordering, comparator behavior, replacer behavior, cycle detection, and the exact `TypeError` contract for invalid `collapseEmpty` and circular values.
