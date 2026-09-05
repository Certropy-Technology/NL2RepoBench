# Project Description

Build the installable CommonJS npm package `json-stable-stringify` from an
empty workspace. It serializes JSON-compatible values to deterministic JSON
text, sorting object keys while preserving array order.

The task id is `json-stable-stringify` and its package name is
`json-stable-stringify`.

# Natural Language Instruction

Implement the package root `require('json-stable-stringify')` with stable
recursive serialization, replacers, custom comparators, spacing, empty-collapse,
`toJSON`, and active-path cycle handling. Preserve native JSON omission and
number semantics and the documented TypeError contracts. Keep the package
self-contained and offline.

# Supports or Environment Configuration

- Node.js 24.19.0 on Linux amd64 with CommonJS `index.js` as the package entry.
- Use `package.json` and a v3 `package-lock.json`; installation uses
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declare only dependencies supported by the frozen local lockfile; no runtime
  download, lifecycle hook, native addon, or external service is allowed.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── README.md
└── index.js
```

# API Usage Guide

Import path: `require('json-stable-stringify')`; an equivalent module example
is `import stringify from 'json-stable-stringify'`.

```js
const stringify = require('json-stable-stringify')
stringify(obj, opts?) // string | undefined
```

Primitive values follow `JSON.stringify`; object keys are sorted
lexicographically by default and arrays retain order. `opts` may be an options
object or comparator function. `space` accepts a string or number. `cmp`
receives `{key, value}` records and may receive `{get(key)}` for the current
object. `replacer(key, value)` runs with the parent as `this`; returning
`undefined` omits object properties. `cycles: true` emits `"__cycle__"` for
active-path cycles; otherwise cycles throw `TypeError`. `collapseEmpty: true`
keeps empty collections compact in pretty output, and non-boolean values throw.

# Implementation Notes

Keep native JSON escaping and number handling, recursive key ordering,
comparator/replacer context, and active-path cleanup stable. Do not use network
access, current time, random state, or the reference repository.

# Examples

```js
const stringify = require('json-stable-stringify')
stringify({ c: 8, b: [{ z: 6, x: 4 }], a: 3 })
stringify({ b: 1, a: 2 }, { space: 2 })
```

```js
const stringify = require('json-stable-stringify')
const value = {}; value.self = value
stringify(value, { cycles: true })
```

# Error Handling and Boundary Conditions

- Undefined root values return `undefined`; undefined object properties are
  omitted and undefined array values become `null`.
- Active-path cycles throw `TypeError` unless `cycles: true`; repeated values
  on separate branches are serialized normally.
- Invalid `collapseEmpty` and unsupported options fail deterministically.

The implementation must not read external files, contact a network, or depend
on the current clock or random state.
