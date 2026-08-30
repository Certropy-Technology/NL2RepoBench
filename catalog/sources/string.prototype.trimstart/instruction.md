# Build `string.prototype.trimstart`

Create an installable npm package named `string.prototype.trimstart` from an
empty workspace. It must provide the CommonJS ES2019 `String.prototype.trimStart`
shim described below without copying the upstream implementation or tests.

## Project Description

The package root is a callable function named `trim`. It trims ECMAScript
whitespace from the beginning of a value after ordinary JavaScript object
coercion. The function is deterministic and must not read the filesystem, use
the network, inspect a terminal, or depend on time or randomness.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` with glibc.
- `package.json` must declare name `string.prototype.trimstart`, version
  `1.0.8`, main `index.js`, and license `MIT`.
- Commit a v3 `package-lock.json` matching the manifest. The only runtime
  dependencies permitted are `call-bind`, `define-properties`, and
  `es-object-atoms`; do not add development dependencies, workspaces, native
  addons, registry overrides, or lifecycle hooks.
- `npm ci --offline --ignore-scripts --no-audit --no-fund` must succeed from a
  clean checkout using the package lock.
- The root module must be a callable CommonJS export named `trim`. It must
  expose non-enumerable callable properties `implementation`, `getPolyfill`,
  and `shim`.

## API Usage Guide

### `trim(value) => string`

Import the root export with CommonJS:

```js
const trim = require('string.prototype.trimstart');
trim(' \t\nhello'); // 'hello'
```

`value` is any non-nullish JavaScript value. The function applies ordinary
JavaScript string coercion, then removes whitespace from the beginning only.
Trailing and internal whitespace remain. The ECMAScript whitespace set is
ASCII tabs/control whitespace, space, no-break space, U+1680, U+2000 through
U+200A, U+2028, U+2029, U+202F, U+205F, U+3000, and BOM U+FEFF. Zero-width
space U+200B, Mongolian vowel separator U+180E on Node 24, U+0085, and U+FFFE
remain in the result. The operation returns a string and does not mutate
caller-owned values.

### Helper properties

- `trim.implementation`: a callable implementation of the trimming behavior.
- `trim.getPolyfill()`: returns a callable native `trimStart`/`trimLeft` method
  when the host method is conforming, otherwise the package implementation.
- `trim.shim()`: installs the selected polyfill as `String.prototype.trimStart`
  when required and returns the selected callable.

The three helper properties are non-enumerable. The root callable has name
`trim` and a one-argument function length.

## Errors and boundary

Calling the root function with `null` or with no argument throws a `TypeError`
because the receiver must be object-coercible. Other JSON values such as
numbers, booleans, arrays, and plain objects follow ordinary JavaScript
ToString behavior. Do not add validation for those values.

## Implementation Notes

- Keep the package root importable without a build step after npm installation.
- The scored verifier uses a fresh bounded unprivileged Node child for each
  request and passes JSON values only.
- The frozen denominator is 31 deterministic `node:test` leaves covering
  package identity, helper shape, leading whitespace boundaries, Unicode
  exclusions, coercion, nullish errors, shim behavior, large inputs,
  non-mutation, and determinism.
- Upstream Tape/NYC/ESLint development tooling, browser compatibility, and
  audit/network post-test behavior are outside this production boundary.
