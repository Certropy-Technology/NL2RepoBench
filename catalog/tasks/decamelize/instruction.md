# Build `decamelize`

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

Create a complete, installable npm package named `decamelize` from an empty
workspace. It converts camelized text into lowercased text with a configurable
separator while handling acronym boundaries and Unicode letters.

## Project Description

The package is an ESM-only, zero-runtime-dependency string utility. Its package
root must export a default function named `decamelize`. The function is
deterministic, does not mutate inputs, access the filesystem, inspect a
terminal, use a clock, use randomness, or access the network.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must declare `name: "decamelize"`, version `"6.0.1"`,
  `type: "module"`, and a safe root `exports` entry pointing to an ESM
  JavaScript file. A TypeScript declaration file may be included.
- Commit a v3 `package-lock.json` consistent with the package and declare no
  runtime or development dependencies, workspaces, native addons, loaders, or
  registry configuration.
- `npm ci --offline --ignore-scripts --no-audit --no-fund` must succeed from a
  clean checkout. No lifecycle hook may be needed to make the package run.
- Do not copy the pinned upstream implementation or its tests. Implement the
  behavior from this specification in your own source.

## API Usage Guide

### `decamelize(text, options?) => string`

Import the default export from the package root:

```js
import decamelize from 'decamelize';

decamelize('unicornRainbow');
// 'unicorn_rainbow'

decamelize('unicornRainbow', {separator: '-'});
// 'unicorn-rainbow'
```

`text` must be a JavaScript string. The function returns a new string and
preserves existing punctuation, whitespace, digits, and separators except for
the case conversion and inserted separators described below.

`options` may be omitted or be an object with:

- `separator?: string`, defaulting to `_`. It may be empty or contain multiple
  characters.
- `preserveConsecutiveUppercase?: boolean`, defaulting to `false`. When false,
  all resulting letters are lowercased. When true, consecutive uppercase runs
  are preserved, while a one-letter uppercase boundary and the final lowercase
  portion of an acronym are handled as described by the examples below.

The function inserts a separator between a lowercase letter or digit and a
following uppercase letter. It also separates an uppercase acronym run from a
following uppercase letter plus lowercase run. With the default option, the
result is lowercased after these boundaries are inserted.

Examples:

```js
decamelize('thisIsATest');
// 'this_is_a_test'
decamelize('myURLString');
// 'my_url_string'
decamelize('myURLString', {preserveConsecutiveUppercase: true});
// 'my_URL_string'
decamelize('oxygenO2Level', {preserveConsecutiveUppercase: true});
// 'oxygen_O2_level'
decamelize('testGUILabel', {separator: '!', preserveConsecutiveUppercase: true});
// 'test!GUI!label'
```

Unicode uppercase/lowercase letters are recognized, including characters such
as `Č` and `Š`. Digits participate in boundary detection. Empty and one-code-
unit strings are valid and follow the case-preservation option.

### Errors and boundary

If `text` is not a string, or `options.separator` is present and not a string,
throw a `TypeError` with the message
`The \`text\` and \`separator\` arguments should be of type \`string\``.
Other option fields are treated as ordinary JavaScript values and do not cause
additional validation errors. JSON values only are used by the verifier.

## Implementation Notes

- Keep the package root importable without a build step after npm installation.
- The scored verifier calls the default export in a fresh unprivileged Node
  child for each request. It passes JSON strings and plain option objects only.
- The frozen denominator is 24 deterministic `node:test` leaves. It covers
  package identity/import, empty and short inputs, ordinary camel boundaries,
  digits, punctuation, acronyms, Unicode, custom and empty separators,
  uppercase preservation, invalid text/separator types, and non-mutation of
  the input/options values.
- The upstream AVA and tsd development toolchains, performance timing
  thresholds, declaration checking, and unsupported non-JSON values are outside
  the production boundary. This is an explicit deterministic scope, not a
  claim of complete upstream test parity.

## Natural Language Instruction

Build `decamelize` from an empty workspace. Provide the default ESM root export
with configurable separators, acronym handling, Unicode case boundaries, and
the exact type-error behavior below. Preserve punctuation, whitespace, and
caller-owned input values.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

`package.json` is the install metadata and `index.js` is the root ESM entry.
The declaration file describes the same default export and no test-only entry
points are public.

## Examples

```js
import decamelize from 'decamelize';
decamelize('helloWorld', {separator: '-'});
```

```js
decamelize('myURLString', {preserveConsecutiveUppercase: true});
```

## Error Handling and Boundary Conditions

Non-string text and a non-string separator throw the specified `TypeError`.
Empty strings, digits, punctuation, acronym runs, and Unicode uppercase
letters remain deterministic. The package performs no I/O, network access, or
mutation of options.
