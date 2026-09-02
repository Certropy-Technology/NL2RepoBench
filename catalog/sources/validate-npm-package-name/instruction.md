# Project Description

Build an installable CommonJS npm package named `validate-npm-package-name`,
version `8.0.0`, from an empty workspace. The package validates npm package
names and preserves the distinction between names accepted for new packages,
names accepted only for legacy packages, and names that were never valid.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, glibc, and CommonJS package
  semantics.
- `require('validate-npm-package-name')` must return the validation function.
- Commit a `package-lock.json` with `lockfileVersion: 3`. The package has no
  runtime dependencies and must install without network access using:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not add runtime dependencies, workspaces, native addons, registry
  overrides, lifecycle scripts, a CLI, or custom Node loaders.
- Runtime behavior is synchronous, deterministic, stateless, and offline. It
  must not read or write files, use the clock or randomness, spawn processes,
  access a TTY, or access the network.

# API Usage Guide

## CommonJS root export `validate(name)`

**Import path:** the package root.

**Signature:**

```ts
type ValidationResult = {
  validForNewPackages: boolean;
  validForOldPackages: boolean;
  warnings?: string[];
  errors?: string[];
};

declare function validate(name: unknown): ValidationResult;
export = validate;
```

The function never throws for ordinary JavaScript inputs and does not mutate
them. Every result always has the two boolean fields. Include `warnings` or
`errors` only when the corresponding array is non-empty.

```js
const validate = require('validate-npm-package-name');

validate('some-package');
// { validForNewPackages: true, validForOldPackages: true }

validate('http');
// {
//   validForNewPackages: false,
//   validForOldPackages: true,
//   warnings: ['http is a core module name']
// }

validate(' leading-space');
// {
//   validForNewPackages: false,
//   validForOldPackages: false,
//   errors: [
//     'name cannot contain leading or trailing spaces',
//     'name can only contain URL-friendly characters'
//   ]
// }
```

### Non-string inputs

Return immediately with one error:

| Input | Error text |
| --- | --- |
| `null` | `name cannot be null` |
| `undefined` | `name cannot be undefined` |
| every other non-string value | `name must be a string` |

The last row includes numbers (including `NaN` and infinities), booleans,
arrays, objects, bigint values, symbols, and functions.

### Errors for string inputs

Accumulate applicable errors in this order:

1. Empty: `name length must be greater than zero`.
2. Starts with `.`: `name cannot start with a period`.
3. Starts with `-`: `name cannot start with a hyphen`.
4. Starts with `_`: `name cannot start with an underscore`.
5. Leading or trailing JavaScript whitespace:
   `name cannot contain leading or trailing spaces`.
6. Case-insensitive whole-name exclusions:
   `node_modules is not a valid package name` or
   `favicon.ico is not a valid package name`.
7. Not URL-friendly: `name can only contain URL-friendly characters`.

An unscoped URL-friendly name uses only characters that JavaScript
`encodeURIComponent` leaves unchanged: ASCII letters, digits, `-`, `_`, `.`,
`!`, `~`, `*`, `'`, `(`, and `)`. Spaces, tabs, `%`, `:`, non-ASCII text, and
slashes are not URL-friendly in an unscoped name.

A scoped name has exactly `@scope/package`, with both segments non-empty and
individually URL-friendly by the same rule. The leading `@` and single `/` are
then allowed. For a syntactically scoped name, also reject a package segment
that starts with `.` using the period error above. A scoped package segment may
start with `-` or `_`, and names such as `@user/node_modules` and `@user/http`
are valid because exclusions and core-module checks apply to the whole name.

### Legacy warnings

After string errors, accumulate warnings in this order:

1. If the complete case-insensitive name is one of Node
   `require('node:module').builtinModules`, add
   `<original name> is a core module name`.
2. If JavaScript `name.length` is greater than 214 UTF-16 code units, add
   `name can no longer contain more than 214 characters`.
3. If `name.toLowerCase() !== name`, add
   `name can no longer contain capital letters`.
4. If the final package segment contains any of `~'!()*`, add
   `name can no longer contain special characters ("~'!()*")`.

The special-character warning checks only the final segment. For example,
`@scope!/package` has no special-character warning, while
`@scope/package!` does. Preserve duplicate-free warning and error arrays in the
order above.

### Validity booleans

- `validForOldPackages` is `true` exactly when there are no errors.
- `validForNewPackages` is `true` exactly when there are neither errors nor
  warnings.

# Implementation Notes

Keep the public surface to the single CommonJS function. The pinned Node
runtime's `builtinModules` list is the authoritative core-module inventory.
The evaluator invokes the root export through a bounded, UID-isolated child
process and verifies JSON-serializable result objects. Private tests, the
Oracle implementation, and grading reports are not part of the package to
implement.
