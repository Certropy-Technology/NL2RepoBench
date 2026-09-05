# Project Description

Build an installable Node.js package named `fast-deep-equal`, version `3.1.3`,
from an empty workspace. It is a zero-runtime-dependency CommonJS library for
comparing bounded JSON values. The scored task is intentionally narrower than
the upstream package: it preserves the root equality behavior for JSON values,
but does not expose the React or ES6-specific entry points.

# Natural Language Instruction

Create the CommonJS `fast-deep-equal` package from an empty workspace. Export
the callable root equality function and preserve the documented comparison
semantics, supported JSON values, and deterministic result behavior.

# Supports or Environment Configuration

- Use Node.js 24.19.0 and npm 11.17.0 with the exact package metadata in
  `task.toml`; this package has no runtime dependencies.
- Agent, candidate, verifier, Oracle, and controls run with no network access.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

# API Usage Guide

The API Usage Guide below is authoritative for the root callable export, input
domains, equality rules, and return type.

# Implementation Notes

Keep comparisons deterministic and side-effect free for the documented JSON
values. Do not expose unrequested React or ES6 entry points.

# Examples

```js
const equal = require('fast-deep-equal');
equal({a: 1}, {a: 1});
```

```js
equal([1, 2], [1, 2]);
```

# Error Handling and Boundary Conditions

```js
equal({a: 1}, {a: 2});
```

```js
equal(null, null);
```

# Supports

- Run on Node.js `24.19.0` with npm `11.17.0` on Linux x86-64.
- `package.json` must declare `"name": "fast-deep-equal"`,
  `"version": "3.1.3"`, and `"main": "index.js"`. Do not declare a
  `"type"` field that makes the package ESM.
- The CommonJS root remains callable:

  ```js
  const equal = require("fast-deep-equal");
  equal({ answer: 42 }, { answer: 42 }); // true
  ```

  It must also expose `require("fast-deep-equal").equal` as the same callable
  function. This non-conflicting alias is required by the fixed JSON child
  adapter; it does not replace the root callable API.
- Commit a v3 `package-lock.json` that matches `package.json`. A clean
  environment must support `npm ci --offline --ignore-scripts --no-audit
  --no-fund`.
- Declare no runtime dependencies, development dependencies, lifecycle hooks,
  native addons, workspaces, loaders, registry configuration, or build step.
  The runtime JavaScript must already be present in `index.js`.
- Runtime network access is unavailable. Do not depend on a network service,
  filesystem input, current time, random state, or a custom test runner.

# API Usage Guide

## `equal(left, right) => boolean`

Import path: the callable package root, with the same function available as
its `.equal` property.

`left` and `right` are independently decoded JSON values. The adapter accepts
one bounded JSON request and returns one JSON boolean, so every comparison must
be deterministic and must not require callbacks, source strings, functions, or
other executable values.

For values in the supported domain, return `true` exactly when the values are
equal under these rules:

- JSON primitives (`null`, booleans, strings, and finite numbers) use strict
  value equality.
- Arrays have the same length and recursively equal elements in the same
  order.
- Plain objects have the same own enumerable string keys and recursively equal
  values. Object key insertion order does not affect equality.
- A JSON key named `"__proto__"` is an ordinary own key and is compared
  recursively; it must not mutate a prototype.
- A matching own `"constructor"` key whose value is `null`, a boolean, a
  number, or a string compares as part of the object. Matching structured
  `"constructor"` values (arrays or objects independently decoded from JSON)
  compare `false`, even when their JSON contents match. Different constructor
  values compare `false`.

Examples:

```js
const equal = require("fast-deep-equal");

equal([1, { tag: "ok" }], [1, { tag: "ok" }]); // true
equal({ b: 2, a: 1 }, { a: 1, b: 2 });          // true
equal([1, 2], [2, 1]);                          // false
```

# Implementation Notes

The task boundary is JSON only. Cycles, shared references, `undefined`,
`NaN`, infinities, `BigInt`, symbols, functions, sparse arrays, dates,
regular expressions, maps, sets, typed arrays, buffers, class instances,
custom prototypes, accessors, and custom `valueOf`, `toString`, or `toJSON`
behavior are outside the contract. JSON objects with an own `"valueOf"` or
`"toString"` key are also outside the supported input domain.

The `/react`, `/es6`, and `/es6/react` entry points, TypeScript declarations,
benchmarks, source-template build tooling, CLI behavior, and browser behavior
are deliberately out of scope. This is a bounded JSON-safe projection of the
pinned CommonJS root API, not a claim of complete JavaScript-value parity.
