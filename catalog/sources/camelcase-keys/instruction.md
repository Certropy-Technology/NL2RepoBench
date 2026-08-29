# Build `camelcase-keys`

## Project Description

Create an installable npm package named `camelcase-keys`, version `10.0.2`, from
an empty workspace. The package converts object keys to camel case and supports
recursive conversion for JSON-shaped objects and arrays.

# Supports

- Node `24.19.0`, npm `11.17.0`, `linux/amd64`, and glibc.
- ESM package semantics: `package.json` must contain `"type": "module"`.
- The package root must export one default function through an export map:
  `types: "./index.d.ts"` and `default: "./index.js"`.
- `package.json` must identify the package as `camelcase-keys` version `10.0.2`
  and use the MIT license. Runtime dependencies must be exact pins for
  `camelcase@9.0.0`, `map-obj@6.0.0`, `quick-lru@7.3.0`, and `type-fest@5.8.0`.
- Include a v3 `package-lock.json` agreeing with the package manifest. A clean
  verifier must run `npm ci --offline --ignore-scripts --no-audit --no-fund` and
  `npm pack --ignore-scripts`.
- Do not use workspaces, native addons, custom loaders, runtime network access,
  lifecycle hooks, or a build step. Do not include hidden tests, verifier code,
  Oracle material, or npm cache bytes in the candidate package.

# API Usage Guide

Import the default ESM export from the package root:

```js
import camelcaseKeys from 'camelcase-keys';

camelcaseKeys({'foo-bar': true});
// {fooBar: true}
```

The runtime signature is:

```ts
camelcaseKeys(input: unknown, options?: Options): unknown
```

The declaration file should expose the corresponding generic object/array
types so callers retain transformed key information. For a supported
non-built-in object, the function returns a new object with string keys
converted using camelcase word boundaries. A top-level array returns a new
array whose object elements are converted even when `deep` is false. Primitive
values are returned unchanged.

`options` accepts:

- `deep` (boolean, default `false`): recursively convert objects inside object
  properties and arrays. With `deep: false`, nested values are preserved.
- `pascalCase` (boolean, default `false`): capitalize the first converted word.
- `preserveConsecutiveUppercase` (boolean, default `false`): retain runs such
  as `FOO` rather than normalizing them.
- `exclude` (array of strings or regular expressions): leave matching keys
  unchanged while still processing their values according to the other rules.
- `stopPaths` (array of dot-notation strings): when `deep` is true, do not
  recurse into a matching child path. Paths use the original input keys, and
  array indices are omitted.

The function is synchronous and stateless from the caller's perspective. It
does not mutate the input. On the public JavaScript API, arrays, nested arrays,
ordinary custom objects, numeric-looking string keys, leading `_`/`$`, symbols,
and built-in values such as Date, RegExp, Map, Set, Promise, typed arrays, and
Error have defined preservation behavior. Circular references remain circular
when deep conversion is enabled. Supported JSON inputs and well-formed options
do not intentionally throw; malformed option values may produce ordinary
JavaScript `TypeError` failures.

# Implementation Notes

The scored boundary sends bounded JSON-compatible values and options through a
UID-separated child process. In that boundary, `exclude` uses string entries;
regular-expression entries remain part of the public JavaScript API but cannot
be represented in JSON. Implement the package as a normal importable library,
not as a CLI. Preserve property order and values, use locale-independent
conversion, and keep repeated calls deterministic. Filesystem descriptors,
callbacks, custom prototypes, symbols, built-in instances, and cyclic graphs
are outside the scored JSON boundary even though the public function should not
corrupt them.
