# Project Description

Create an installable npm package named `lines-and-columns`, version
`0.0.0-dev`, from an empty workspace. The package maps JavaScript string
character offsets to zero-based source line and column locations and maps
locations back to offsets. It provides one public class and has no I/O,
network, clock, random, browser, or locale-dependent behavior.

# Natural Language Instruction

Create the `lines-and-columns` project from an empty `workspace/`. Implement
the public `LinesAndColumns` class at the package root. The class must index a
JavaScript string and provide deterministic conversion in both directions
between UTF-16 code-unit offsets and zero-based line/column locations.

Support LF, CR, and combined CRLF line endings, empty lines, trailing
newlines, and non-BMP characters. Keep the class available to both ESM and
CommonJS consumers and include a safe declaration entry. Build the package
with your own implementation; do not retrieve another repository or depend on
runtime compilation.

# Supports

- Use Node.js `24.19.0`, npm `11.17.0`, Linux amd64 with glibc, and ESM-first
  package semantics with a CommonJS compatibility export.
- `package.json` must set `name` to `lines-and-columns`, `version` to
  `0.0.0-dev`, and `type` to `module`.
- The package root must export the named class `LinesAndColumns` from both ESM
  and CommonJS entry points and expose a safe `types` entry.
- Declare no runtime dependencies, development dependencies, workspaces, or
  lifecycle scripts. Commit an npm v3 `package-lock.json` describing that
  zero-dependency package.
- A clean installation must succeed with
  `npm ci --offline --ignore-scripts --no-audit --no-fund`; packaging must
  succeed with `npm pack --ignore-scripts`.
- Agent, candidate, verifier, Oracle, and control execution is NoNetwork.
  Do not access registries, source hosts, DNS, or external services.
- Do not use native addons, browser globals, current time, random state, or a
  CLI. All declared runtime entries must already exist in the package.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.cjs
├── index.d.ts
└── src/
    └── index.ts
```

The root export map must expose ESM `index.js`, CommonJS `index.cjs`, and the
`index.d.ts` types entry. `src/index.ts` is the public source layout recorded
for the project; the installable root entries may be authored from it, but the
package cannot depend on a build lifecycle script. Do not add test, fixture,
loader, CLI, or generated-report files to the public package contract.

# API Usage Guide

## Root import and constructor

Import the named class from the package root:

```js
import {LinesAndColumns} from 'lines-and-columns';
const map = new LinesAndColumns('ab\ncd');
```

The CommonJS root exposes the same named class. Its constructor signature is:

```ts
new LinesAndColumns(string: string)
```

The constructor accepts a JavaScript string and records its line starts.
Offsets and columns use JavaScript UTF-16 code units, matching `.length` and
string indexing. It does not mutate the input, perform I/O, or expose mutable
index state.

## `locationForIndex`

```ts
locationForIndex(index: number): {line: number; column: number} | null
```

Lines and columns are zero-based. An integer index from `0` through the input
string length, inclusive, maps to a plain object with exactly `line` and
`column`. An index before the start or after the end returns `null`. The index
equal to `string.length` maps to the end of the final line.

Every `\n` starts a new line. A `\r` also starts a new line, but immediately
adjacent `\r\n` starts only one new line. Newline code units remain in the
preceding line's addressable span. For `"a\r\nb"`, indices `0`, `1`, and `2`
are on line `0`, and index `3` is line `1`, column `0`. A trailing newline
creates an empty final line.

## `indexForLocation`

```ts
indexForLocation(location: {line: number; column: number}): number | null
```

The location contains zero-based numeric `line` and `column` properties. A
line outside the indexed lines, a negative column, or a column beyond that
line's addressable length returns `null`. A valid location returns its UTF-16
code-unit offset. Newline code units count toward the preceding line's length,
including both units of CRLF. The method does not mutate the location object.

For every valid addressable location, converting to an index and back must be
stable. Repeated calls with the same constructor input and arguments produce
equivalent results.

# Implementation Notes

- Keep the public class available from the package root in both module
  systems. ESM and CommonJS construction must produce equivalent behavior.
- Use a deterministic line-start representation. Query methods return a new
  plain location object or `null`; callers do not receive internal state.
- Preserve UTF-16 code-unit semantics rather than Unicode code points or
  grapheme clusters. A character such as `"😀"` occupies two columns.
- Treat a CRLF pair as one line break while keeping both code units
  addressable on the previous line.
- Browser APIs, asynchronous behavior, CLI entry points, locale-sensitive
  behavior, filesystem access, and undocumented internals are outside scope.

# Examples

```js
import {LinesAndColumns} from 'lines-and-columns';

const map = new LinesAndColumns('ab\ncd');
map.locationForIndex(3); // {line: 1, column: 0}
map.indexForLocation({line: 1, column: 2}); // 5
```

```js
const windows = new LinesAndColumns('a\r\nb');
windows.locationForIndex(2); // {line: 0, column: 2}
windows.locationForIndex(3); // {line: 1, column: 0}

const unicode = new LinesAndColumns('😀x');
unicode.locationForIndex(2); // {line: 0, column: 2}
```

# Error Handling and Boundary Conditions

- `new LinesAndColumns('')` still has line zero; index zero maps to line zero,
  column zero. Negative indices and indices greater than zero return `null`.
- A final LF, CR, or CRLF creates an empty final line at the end index.
- `locationForIndex(-1)` and an index beyond `.length` return `null`.
  `indexForLocation` returns `null` for negative columns, missing lines, and
  columns beyond the selected line.
- Newline boundaries are deterministic: adjacent CRLF is one break, while
  independent CR or LF units each start a line.
- Methods must not mutate caller-owned values and must not consult files,
  environment variables, time, randomness, browser globals, DNS, registries,
  source hosts, or network services.
