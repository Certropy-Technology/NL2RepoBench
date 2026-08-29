# Build `@eslint/object-schema`

## Project Description

Create an installable npm package named `@eslint/object-schema` at version `3.0.5` from an
empty workspace. It is an ESM-first utility for validating objects against per-key definitions
and merging several objects with a strategy selected for each key. The package is used by
configuration tooling, so deterministic ordering, clear validation errors, and non-mutating
merge results are important.

## Supports

- Node.js `24.19.0` on Linux amd64 with glibc and npm `11.17.0`.
- Both ESM and CommonJS consumers. The package root must support `import` and `require` and
  expose `dist/esm/index.js`, `dist/cjs/index.cjs`, and declaration files under `dist`.
- A package manifest with name `@eslint/object-schema`, version `3.0.5`, `type: "module"`, and
  an exports map for both `import` and `require`.
- A committed npm v3 `package-lock.json`. The runtime dependency closure is empty; installation
  must succeed with `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Do not use network services, native addons, workspace dependencies, install hooks, or a
  globally installed copy of this package.

## API Usage Guide

### Package exports

The package root must export the classes `ObjectSchema`, `MergeStrategy`, and
`ValidationStrategy`. These are named exports in ESM and properties of the object returned by
CommonJS `require("@eslint/object-schema")`.

### `MergeStrategy`

`MergeStrategy.overwrite(first, second)` returns `second`, including when it is `undefined`.
`MergeStrategy.replace(first, second)` returns `second` when it is defined and otherwise returns
`first`. `MergeStrategy.assign(first, second)` returns a new object containing enumerable own
properties from both inputs, with properties from `second` taking precedence. It must not mutate
either input.

### `ValidationStrategy`

The static validators `array`, `boolean`, `number`, `object`, `object?`, `string`, and `string!`
return `undefined` for valid values and throw `TypeError` for invalid values. `object` accepts
non-null objects including arrays and class instances; `object?` also accepts `null`.
`string!` accepts only non-empty strings. Error messages identify the expected kind, such as
`Expected an array.` or `Expected a non-empty string.`.

### `ObjectSchema`

`new ObjectSchema(definitions)` accepts a non-empty object whose keys are schema keys. Each
definition may contain:

- `merge`: a function or one of `"assign"`, `"overwrite"`, and `"replace"`;
- `validate`: a function or one of the named validators above;
- `required: true` to require the key in every validated object;
- `requires: [key, ...]` to require other keys whenever this key is present; or
- `schema: { ... }` for a nested `ObjectSchema`, in which case the nested value is validated and
  merged recursively.

Definitions using `schema` do not need to provide `merge` or `validate`. Invalid or incomplete
definitions throw `TypeError` during construction. Unknown named strategies also throw.

`schema.hasKey(key)` returns whether a definition exists. `schema.validate(object)` returns
`undefined` for a valid object. It throws when `object` has an unknown key, a value fails its
validator, a required key is absent, or a present key is missing one of its dependencies. Errors
identify the key, for example `Unexpected key "x" found.`, `Missing required key "x".`, or
`Key "child" requires keys "parent".`. Errors raised by a key validator are wrapped as
`Key "key": <original message>` and preserve the original error as `cause`.

`schema.merge(first, second, ...rest)` requires at least two non-null objects. It validates each
input, then returns a new object. Only defined schema keys are considered, and a key is merged
only when it appears in at least one input. The selected strategy receives the accumulated value
and the next value in input order. A returned `undefined` does not assign a new value; therefore
an already accumulated value remains present, while a key with no prior value is absent. Input
objects and nested values must not be mutated by the schema implementation.

### Example

```js
import { MergeStrategy, ObjectSchema, ValidationStrategy } from "@eslint/object-schema";

const schema = new ObjectSchema({
  count: { required: true, merge: (a = 0, b = 0) => a + b, validate: "number" },
  options: { merge: MergeStrategy.assign, validate: ValidationStrategy["object?"] },
});

schema.validate({ count: 1 });
const result = schema.merge({ count: 1 }, { count: 2, options: { mode: "fast" } });
// { count: 3, options: { mode: "fast" } }
```

## Implementation Notes

Keep the public entry point and package metadata compatible with both module systems. Preserve
strategy call order, object-key insertion order, wrapped error causes, and the distinction between
`undefined`, `null`, and missing keys. Avoid prototype-pollution behavior when validating or
merging ordinary object input. Build output must be self-contained and must not require the
monorepo, TypeScript at runtime, a network connection, or any package other than this package.
