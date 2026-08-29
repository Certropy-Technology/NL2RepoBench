# Project Description

Recreate `own-keys` version `1.0.2` as a CommonJS npm package. The package
exports one function that returns all own property keys of an object, including
non-enumerable string keys and symbol keys, in JavaScript property-key order.

# Supports

- Run on Node.js `24.19.0` with npm `11.17.0` on Linux x86-64.
- Create the package in the workspace root. `package.json` must declare:
  - `"name": "own-keys"` and `"version": "1.0.2"`;
  - `"main": "index.js"` and no `"type"` field that makes the root ESM;
  - root exports `{".": "./index.js", "./package.json": "./package.json"}`;
  - `"sideEffects": false` and `"license": "MIT"`;
  - exact runtime dependencies `call-bound@1.0.4`,
    `get-intrinsic@1.3.0`, `object-keys@1.1.1`, and
    `safe-push-apply@1.0.0`.
- Commit a v3 `package-lock.json` matching `package.json`. A clean environment
  must support `npm ci --offline --ignore-scripts --no-audit --no-fund` using
  the frozen npm cache supplied by the evaluator.
- Do not add development dependencies, lifecycle scripts, workspaces, native
  addons, registry configuration, loaders, or a build step. Runtime JavaScript
  must already be present in `index.js`.
- Runtime network access is unavailable. The implementation must not depend on
  filesystem input, network services, current time, random state, or mutable
  process-global configuration.

# API Usage Guide

## `ownKeys(source) => Array<string | symbol>`

Import path: the callable CommonJS package root.

`source` must be a JavaScript object. This includes ordinary objects, arrays,
functions, null-prototype objects, and proxies. On the pinned runtime, passing
`null`, `undefined`, or any primitive value throws `TypeError`.

Return a new array containing every own property key of `source`:

1. own integer-index string keys in ascending numeric order;
2. all other own string keys in property creation order;
3. own symbol keys in property creation order.

Both enumerable and non-enumerable keys are included. Inherited keys are not
included. Accessor values are not read, so getters must not run. The function
does not mutate `source`, its descriptors, or its prototype.

For proxies, observe the proxy's `[[OwnPropertyKeys]]` behavior. Preserve a
valid trap result's order and propagate the runtime `TypeError` for invalid
results such as duplicate keys or omission of a non-configurable own key.

Examples:

```js
const ownKeys = require("own-keys");

const hidden = Symbol("hidden");
const value = {visible: 1};
Object.defineProperty(value, "internal", {value: 2, enumerable: false});
value[hidden] = 3;

ownKeys(value); // ["visible", "internal", hidden]
ownKeys(["a", "b"]); // ["0", "1", "length"]
```

# Implementation Notes

The exported function has arity `1`. Results contain the original symbol
values, not symbol descriptions or string conversions, and each invocation
returns a fresh array.

The contract is the package root on the pinned modern Node runtime. Historical
fallback behavior on pre-ES2015 engines, browser bundling, CLI behavior, and
source retrieval are outside the task. Do not copy or fetch the upstream
implementation; implement the documented behavior locally.
