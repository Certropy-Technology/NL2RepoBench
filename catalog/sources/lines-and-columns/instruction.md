# Build `lines-and-columns`

## Project Description

Create an installable npm package named `lines-and-columns`, version
`0.0.0-dev`, from an empty workspace. The package maps JavaScript string
character offsets to zero-based source line and column locations and maps
locations back to offsets. Implement the documented public behavior with your
own source; do not retrieve a reference repository or hidden tests.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc, and ESM-first package
  semantics with a CommonJS compatibility export.
- `package.json` must set `name` to `lines-and-columns`, `version` to
  `0.0.0-dev`, and `type` to `module`.
- The package root must export the named class `LinesAndColumns` from both ESM
  and CommonJS entry points. The package must also expose a safe `types` entry.
- Declare no runtime dependencies, development dependencies, workspaces, or
  lifecycle scripts. Include the committed npm v3 lockfile and every file
  needed by the declared root exports.
- A clean verifier must be able to run the package through:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  npm pack --ignore-scripts
  ```

- Do not use network access, native addons, browser globals, current time, or
  random state.

## API Usage Guide

### `LinesAndColumns`

Import path: the package root.

Signature:

```js
new LinesAndColumns(string)
```

The constructor accepts a JavaScript string and records its line starts. String
offsets and columns are JavaScript UTF-16 code-unit offsets, the same units
used by `string.length` and bracket indexing. The input is not mutated.

### `locationForIndex`

Signature:

```js
locationForIndex(index) // {line: number, column: number} | null
```

Lines and columns are zero-based. `index` is valid when it is between `0` and
the string length inclusive; an index before the start or after the end
returns `null`. Index `string.length` maps to the end of the final line. The
returned object has exactly `line` and `column` properties.

Every `\n` starts a new line. A `\r` also starts a new line; when a `\r` is
immediately followed by `\n`, the pair starts one new line. The newline code
units remain part of the preceding line's addressable span, so for `"a\r\nb"`
indices `0`, `1`, and `2` are on line `0`, while index `3` is line `1`, column
`0`. A trailing newline creates an empty final line.

### `indexForLocation`

Signature:

```js
indexForLocation(location) // number | null
```

`location` contains zero-based numeric `line` and `column` properties. A line
outside the recorded lines, a negative column, or a column beyond that line's
length returns `null`. Otherwise the result is the UTF-16 code-unit offset.
Newline code units count toward the preceding line's length, including both
code units of a CRLF pair. The method is deterministic and does not mutate the
location object.

### Examples

```js
import {LinesAndColumns} from "lines-and-columns";

const map = new LinesAndColumns("ab\ncd");
map.locationForIndex(3); // {line: 1, column: 0}
map.indexForLocation({line: 1, column: 2}); // 5
```

For a string containing `"😀"`, the emoji occupies two columns because it is
two UTF-16 code units in JavaScript.

## Implementation Notes

- Keep the public class available from the package root in both module
  systems. ESM and CommonJS calls must produce the same results.
- Use a deterministic line-start representation so repeated queries return
  stable plain objects or `null`.
- The scored contract is the behavior above. Browser APIs, locale-sensitive
  behavior, asynchronous APIs, CLI entry points, and undocumented internals
  are outside the contract.
