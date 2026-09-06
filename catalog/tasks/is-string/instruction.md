# Project Description

Build an installable CommonJS npm package named `is-string`, version `1.1.1`,
from an empty workspace. The package exports one synchronous predicate that
recognizes string primitives and genuine boxed String objects.

# Natural Language Instruction

Create the `is-string` package from an empty workspace. Implement the callable
CommonJS root export, its TypeScript declaration, and the complete primitive
and boxed-string predicate described in the API guide. The implementation must
distinguish genuine String internal data from objects that only look like
strings, remain synchronous and deterministic, and expose no unrelated API.
Keep package metadata, the lockfile, the root export, and the declaration
consistent with one another. Do not add a CLI, service, filesystem behavior,
or a dependency merely to perform type detection.

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

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

`index.js` is the CommonJS package entry and must export the predicate itself,
not an object wrapper. `index.d.ts` describes the same `export =` shape. No
runtime source, generated download, test fixture, or configuration file is
required beyond this minimal installable layout.

# API Usage Guide

Import path and package shape:

```js
const isString = require('is-string');
// TypeScript declaration form: import isString = require('is-string');
```

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

## API examples

Example:

```js
const isString = require('is-string');

isString('hello');          // true
isString(new String('hi')); // true
isString({ toString() { return 'hi'; } }); // false
```

Additional ordinary and boundary examples:

```js
isString('');                 // true
isString(new String(''));     // true
isString(Object(42));         // false
```

```js
const tagged = { [Symbol.toStringTag]: 'String' };
isString(tagged);              // false
```

# Error Handling and Boundary Conditions

The supported input domain is `unknown`; every input must produce a boolean
without throwing solely because it is `null`, a Symbol, or a hostile object.
Do not call user-defined `toString`, `valueOf`, getters, proxies, or coercion
hooks as part of the decision. A genuine boxed String remains true after its
own `Symbol.toStringTag` is changed, while a tag-only impostor remains false.
The function must not retain references, mutate an object, inspect the clock,
read process state, or perform any I/O. Agent, candidate, verifier, Oracle,
controls, and runtime all operate with no network access.

## Observable contract checklist

- The result is always the primitive boolean `true` or `false`.
- Primitive strings include empty strings and strings containing Unicode code
  units; their contents are not normalized or decoded.
- `new String(value)` is true when it is an actual boxed string, regardless of
  whether the wrapped value is empty.
- Numbers, booleans, BigInts, Symbols, functions, arrays, dates, regular
  expressions, and ordinary objects are false.
- `Object.create(String.prototype)` is not a genuine boxed string and is false.
- An object with `valueOf`, `toString`, or a string-looking tag is not coerced.
- The predicate has no asynchronous form and never returns a Promise.
- Repeated calls with the same input do not change the input or global state.

# Implementation Notes

Check primitive strings before object handling. For objects, distinguish the
internal String data slot from lookalikes; do not implement the predicate by
coercing with `String(value)`, by comparing `Object.prototype.toString` alone,
or by trusting a user-controlled `Symbol.toStringTag`. Preserve the callable
CommonJS root export and keep the declaration compatible with `export =`.

## Packaging requirements

`package.json` must identify the package as CommonJS and point its `main` field
at `index.js`. The lockfile must be valid for the declared npm version and must
not introduce a runtime dependency. A clean offline `npm ci` followed by a
regular `require('is-string')` must work from outside the project directory.
Do not depend on the evaluator's current working directory, a globally
installed copy, environment variables, or a network registry.

## Non-goals

This package is not a string coercion utility, schema validator, Unicode
normalizer, text encoder, or replacement for `typeof`. It does not expose
methods such as `isPrimitive`, `isObject`, or `toString`. Do not add a CLI,
browser-only global, telemetry hook, cache, or mutable configuration object.

# Examples

## Additional examples

```js
const isString = require('is-string');
for (const value of ['', 'cafe\u0301', new String('x')]) {
  if (!isString(value)) throw new Error('expected a string value');
}
```

```js
const isString = require('is-string');
const fake = Object.create(String.prototype);
fake.valueOf = () => 'not a boxed string';
isString(fake); // false, without calling valueOf
```

The implementation should be small, but the public behavior above is the full
contract. Keep all examples runnable with the declared package entry and keep
the implementation free of external I/O.
