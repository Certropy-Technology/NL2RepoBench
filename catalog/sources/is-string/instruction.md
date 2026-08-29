# Project Description

Build an installable CommonJS npm package named `is-string`, version `1.1.1`,
from an empty workspace. The package exports one synchronous predicate that
recognizes string primitives and genuine boxed String objects.

# Supports

- Node.js `24.19.0` with npm `11.17.0` on Linux x86-64.
- CommonJS package metadata: `package.json` must use `name: "is-string"`,
  `version: "1.1.1"`, `main: "index.js"`, and `types: "index.d.ts"`.
- A v3 `package-lock.json` matching the package metadata. The package must
  install with `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- No runtime dependencies, native addons, workspaces, lifecycle scripts,
  registry configuration, generated downloads, or build step.
- The package root is callable and must also be usable through
  `require("is-string")` from another CommonJS module.

# API Usage Guide

## `isString(value) => boolean`

Import path: `require("is-string")`.

TypeScript declaration:

```ts
declare function isString(value: unknown): value is string | String;
```

Return `true` for a primitive JavaScript string, including the empty string and
Unicode strings. Return `true` for an object created by the String constructor,
including an empty boxed string. Return `false` for `undefined`, `null`,
booleans, numbers, BigInts, Symbols, functions, arrays, regular expressions,
dates, boxed non-string primitives, and ordinary objects.

An object that merely sets `Symbol.toStringTag` to `"String"` is not a boxed
String and must return `false`. An object with string-returning `toString` or
`valueOf` methods is also not a boxed String. The predicate must not invoke
user-defined conversion methods to decide this. A genuine boxed String must be
recognized even when its `Symbol.toStringTag` property is changed.

The result is synchronous, deterministic, and always a boolean. It must not
read files, inspect the environment, use the clock or randomness, spawn
processes, or access the network.

Example:

```js
const isString = require('is-string');

isString('hello');          // true
isString(new String('hi')); // true
isString({ toString() { return 'hi'; } }); // false
```

# Implementation Notes

Check primitive strings before object handling. For objects, distinguish the
internal String data slot from lookalikes; do not implement the predicate by
coercing with `String(value)`, by comparing `Object.prototype.toString` alone,
or by trusting a user-controlled `Symbol.toStringTag`. Preserve the callable
CommonJS root export and keep the declaration compatible with `export =`.
