# Build `get-east-asian-width`

## Project Description

Create an installable npm package named `get-east-asian-width`, version
`1.6.0`, from an empty workspace. It classifies a Unicode code point using
the Unicode East Asian Width property and reports the display width used by
East Asian typography.

This is a repository-generation task. Implement the documented behavior with
your own source files; do not retrieve a reference implementation or hidden
tests.

## Natural Language Instruction

Create the package from an empty `workspace/`. Implement both named root
exports, the Unicode width table, safe-integer validation, and the option that
selects whether ambiguous characters count as wide. Keep the result a pure
number or category string: no CLI, generated Unicode download, filesystem
state, current locale, clock, randomness, or network fallback is part of the
package.

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

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

The root ESM entry point must export `eastAsianWidth` and
`eastAsianWidthType`; the declaration file describes their signatures and the
`WidthType` union. No build-time Unicode fetcher or test-only entrypoint is
required.

## API Usage Guide

### `eastAsianWidth(codePoint, options?)`

Import path: `import * as eastAsianWidthApi from 'get-east-asian-width'`.
The named export is `eastAsianWidthApi.eastAsianWidth`.
Its signature is
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

Import path: `import * as eastAsianWidthApi from 'get-east-asian-width'`.
The named export is `eastAsianWidthApi.eastAsianWidthType`.
Its signature is
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

## Examples

```js
import {eastAsianWidth, eastAsianWidthType} from 'get-east-asian-width';

const width = eastAsianWidth('界'.codePointAt(0)); // 2
const kind = eastAsianWidthType('A'.codePointAt(0)); // 'narrow'
```

```js
import {eastAsianWidth} from 'get-east-asian-width';

eastAsianWidth(0x00b7, {ambiguousAsWide: false}); // 1
eastAsianWidth(0x00b7, {ambiguousAsWide: true}); // 2
```

## Error Handling and Boundary Conditions

- Inputs must be safe integer numbers. A string, fractional number, `NaN`,
  infinity, `bigint`, or symbol is outside the contract and must raise the
  documented `TypeError` rather than being coerced.
- Code points absent from the frozen local table return `neutral` from
  `eastAsianWidthType` and width `1` from `eastAsianWidth`.
- Repeated calls with the same number and options return the same primitive
  result and do not mutate the options object.
