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

# Supports

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

The serializer must distinguish an active recursive path from an object that
is merely shared by two independent branches. If the same child object is
referenced by `left` and `right` after `left` has been serialized, both
properties are serialized normally; only a reference encountered while that
object is still being serialized is a cycle. Comparator calls receive the
key/value records for one object and must not alter the source object.

The replacer is called for the root and then for each traversed property with
the containing object as `this`. A replacer result of `undefined` omits an
object property and becomes `null` in an array, matching native JSON behavior.
If a value has a callable `toJSON`, invoke it before ordinary serialization
and then apply the replacer to the resulting value. BigInt values remain an
unsupported JSON value and must raise the documented native-compatible error.

Object enumeration is limited to enumerable string keys. Prototype-inherited
properties are not added to the output, while an own `toJSON` method may
participate through the normal JSON conversion hook. Numeric formatting,
negative zero, escaping, and non-finite number handling follow the runtime's
JSON representation rather than a locale or custom formatter.

Pretty output uses the requested `space` indentation and keeps arrays in input
order. Empty arrays and objects are rendered compactly when `collapseEmpty`
is enabled, but their surrounding parent indentation remains deterministic.
The default comparator sorts keys lexicographically at every object depth;
custom comparators are applied independently at each depth and stable ties
retain the original enumerable-key order.

When `space` is a number, indentation is capped and derived from that many
spaces; when it is a string, the string is used as the indentation unit.
Unsupported option types must be rejected before producing partial output.
The returned text is a primitive string and serialization must not mutate
enumerable keys, arrays, comparator state, or replacer-owned objects. A
comparator may inspect the current object through its documented getter, but
the getter must not expose inherited keys as enumerable own properties. Empty
objects and arrays remain valid JSON values even when they are collapsed.
