# detect-indent

## Project Description

Build an installable npm package named `detect-indent` that identifies the
indentation style most strongly supported by a source string. The package is a
small ESM library with a single default export and no runtime dependencies.

## Supports

- Node.js 24 on Linux x86-64 with npm 11.
- ESM package metadata: `package.json` must declare `type: "module"`,
  `name: "detect-indent"`, version `7.0.2`, and export `./index.js` as the
  package root. Provide the public type declaration in `index.d.ts`.
- Commit a `package-lock.json` using lockfile version 3. Installation must
  work with `npm ci --offline --ignore-scripts`; do not add runtime or build
  dependencies.
- The package must be usable immediately after installation. Do not require a
  lifecycle hook, transpiler, generated directory, native addon, or network
  access.

## API Usage Guide

### `import detectIndent from 'detect-indent'`

#### `detectIndent(string: string): {amount: number, type: 'space' | 'tab' | undefined, indent: string}`

Accept any text string and inspect line-leading spaces or tabs. Return the
most strongly supported indentation transition:

- `type` is `"space"` or `"tab"` when indentation is detected, otherwise
  `undefined`.
- `amount` is the positive count of spaces or tabs in that transition, or `0`
  when no indentation is detected.
- `indent` is the corresponding repeated character string, or `""` when no
  indentation is detected.

The result is a fresh plain object. A non-string input throws `TypeError` with
the message `Expected a string`.

## Implementation Notes

- Analyze each line independently, including text with LF or CRLF endings;
  empty lines do not contribute evidence. Leading indentation is made only of
  spaces or only of tabs for a given line. Mixed space-plus-tab prefixes are
  not required to become one indentation unit.
- Compare changes in indentation between neighboring non-empty lines. Count
  repeated uses of a transition and use repeated lines as a tie-breaker. When
  space and tab evidence is exactly tied, the earliest strongest evidence wins.
- Ignore one-space changes during the first pass so alignment in comments and
  documentation does not overpower a real indentation level. If no other
  evidence exists, reconsider one-space indentation so a file indented by one
  space is still detected.
- A document with no indentation, an empty string, or only unindented text
  returns `{amount: 0, type: undefined, indent: ''}`. Whitespace-only lines
  can provide indentation evidence.
- Preserve the package root's default export and declaration shape. Do not
  expose test fixtures or test-only exports as part of the public API.
