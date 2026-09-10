# Build `wrap-ansi`

## Project Description

Create a complete installable npm package named `wrap-ansi`, version `10.0.1`,
from an empty workspace. It wraps terminal text to a requested column width
while treating supported ANSI escape sequences and Unicode grapheme clusters as
zero-width or measured visible content. The package is a repository-generation
task: implement the contract with your own package files and do not copy the
reference repository or its tests.

## Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64`.
- ESM package semantics with `package.json` containing `"type": "module"` and
  an `exports` map exposing runtime `./index.js` and types `./index.d.ts`.
- Distribution metadata must identify `wrap-ansi` version `10.0.1`.
- Include a v3 `package-lock.json` with exact integrity-locked runtime closure.
  Installation must work without network access:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The direct runtime dependencies are exact `ansi-styles@6.2.3` and
  `string-width@8.2.0`. Their exact transitive closure is
  `get-east-asian-width@1.6.0`, `strip-ansi@7.2.0`, and
  `ansi-regex@6.3.0`. Do not add lifecycle scripts, workspaces, native addons,
  registry overrides, custom loaders, or runtime downloads.
- The public entry point is the default ESM export:

  ```js
  import wrapAnsi from 'wrap-ansi';
  ```

## API Usage Guide

### `wrapAnsi(string, columns, options?)`

```ts
export type Options = {
  readonly hard?: boolean;
  readonly wordWrap?: boolean;
  readonly trim?: boolean;
};

export default function wrapAnsi(
  string: string,
  columns: number,
  options?: Options,
): string;
```

The declared input is a string, but runtime calls apply JavaScript `String()`
conversion to JSON-compatible values before processing. `columns` is a finite,
non-negative integer target width. A width of zero is valid; hard wrapping then
places each positive-width grapheme on its own row. The return value is a
string. Calls using this input domain and the option types below do not throw.
Other column values and malformed option objects are outside this contract.
Normal operation is deterministic and has no filesystem, subprocess, clock,
randomness, service, or network behavior.

The optional options object has these boolean fields:

- `hard` defaults to `false`. When true, a word longer than the available
  columns is split across rows; when false, an overlong word may remain wider
  than the column limit.
- `wordWrap` defaults to `true`. When false, every row is filled by splitting
  words as necessary instead of preferring spaces.
- `trim` defaults to `true`. When true, leading and trailing spaces on rows
  created by wrapping are removed. When false, spaces are preserved.

Words are separated by ASCII spaces. Wrapping preserves word order and visible
content. Empty input and whitespace-only input follow the trimming option. A
trailing newline remains a trailing newline; blank rows are not populated with
style reopen sequences.

```js
wrapAnsi('The quick brown fox', 10); // 'The quick\nbrown fox'
wrapAnsi('abcdef', 3, {hard: true}); // 'abc\ndef'
wrapAnsi('   ', 2, {trim: false}); // '  \n '
```

### ANSI and Unicode behavior

ANSI SGR sequences and OSC 8 hyperlinks are zero-width and must never be split.
Supported SGR includes basic modifiers/colors, semicolon-delimited 256-color and
RGB forms, colon-delimited 256-color/RGB forms, and C1 CSI equivalents. Other
complete CSI/OSC sequences remain intact as opaque zero-width units. Unterminated
or unsupported control strings are treated as ordinary text according to the
documented parser boundary.

Active SGR styles and hyperlinks are closed before a generated newline and
reopened on the next non-empty row. Reset sequences at a row start affect what
is reopened. Nested foreground/background/modifier styles retain their family
and close in reverse order. Original complete BEL- or ST-terminated hyperlink
sequences remain intact. Hyperlink controls inserted at a generated row break
use OSC 8 with BEL for the close and reopen, even when the original opener used
ST. Hyperlink parameters and URI bytes are retained, and adjacent URLs are not
mixed.

Visible width uses Unicode grapheme clusters and terminal width: fullwidth
characters and emoji consume their measured width, combining marks do not
split their grapheme cluster, and tabs expand to spaces at 8-column tab stops.
CRLF input is normalized to LF, while ordinary CR characters are retained as
content and can participate in wrapping.

## Implementation Notes

Keep the implementation ESM-compatible and package-local. Do not implement
wrapping by stripping ANSI and rebuilding the string: escape sequences,
parameterized hyperlinks, nested styles, resets, grapheme clusters, tab stops,
and malformed sequences must retain their observable placement. Preserve the
default option values, line normalization, exact escape bytes, package export
shape, type declaration, and offline npm lock/cache contract. The verifier calls
the candidate through a UID-separated child process and only checks the
deterministic API described above.
