# Build `get-east-asian-width`

## Project Description

Create an installable npm package named `get-east-asian-width`, version
`1.6.0`, from an empty workspace. It classifies a Unicode code point using
the Unicode East Asian Width property and reports the display width used by
East Asian typography.

This is a repository-generation task. Implement the documented behavior with
your own source files; do not retrieve a reference implementation or hidden
tests.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc, and ESM semantics.
- `package.json` must set `name` to `get-east-asian-width`, `version` to
  `1.6.0`, and `type` to `module`. The package root must expose the ESM
  entrypoint and the public type declaration.
- A committed npm lockfile version 3. A clean verifier runs
  `npm ci --offline --ignore-scripts --no-audit --no-fund` and then
  `npm pack --ignore-scripts` without network access.
- The package has no runtime dependencies. Do not use workspaces, native
  addons, lifecycle hooks, custom loaders, runtime downloads, or network
  access.

## API Usage Guide

### `eastAsianWidth(codePoint, options?)`

Import the named function from `get-east-asian-width`. Its signature is
`eastAsianWidth(codePoint: number, options?: {ambiguousAsWide?: boolean}): 1 | 2`.
`codePoint` must be a JavaScript safe integer. Non-integers, strings, and
other values throw `TypeError`. A safe integer outside the Unicode data table
is classified as neutral and has width `1`.

The default is `{ambiguousAsWide: false}`. Fullwidth and wide characters
return `2`; all other categories return `1`. When `ambiguousAsWide` is true,
ambiguous characters return `2` as well. The input is read-only and calls are
deterministic.

```js
import {eastAsianWidth} from 'get-east-asian-width';

eastAsianWidth('字'.codePointAt(0)); // 2
eastAsianWidth('⛣'.codePointAt(0)); // 1
eastAsianWidth('⛣'.codePointAt(0), {ambiguousAsWide: true}); // 2
```

### `eastAsianWidthType(codePoint)`

Import `eastAsianWidthType` from `get-east-asian-width`. Its signature is
`eastAsianWidthType(codePoint: number): WidthType`, where `WidthType` is the
union `'fullwidth' | 'halfwidth' | 'wide' | 'narrow' | 'neutral' | 'ambiguous'`.
It applies the same safe-integer validation and returns the Unicode category
for the code point. Values not present in the table return `'neutral'`.

```js
import {eastAsianWidthType} from 'get-east-asian-width';

eastAsianWidthType('字'.codePointAt(0)); // 'wide'
eastAsianWidthType('A'.codePointAt(0)); // 'narrow'
```

## Implementation Notes

Use a deterministic, local Unicode lookup representation. The scored
subprocess boundary passes JSON-compatible numbers and booleans only. The
contract does not require a CLI, filesystem API, Unicode-data build script,
network fetching, or private helper exports. Preserve supplementary Unicode
code points, exact category strings, and informative `TypeError` behavior.
