# Project Description

Build a complete installable npm package named `widest-line`, version `6.0.0`,
from an empty workspace. Its default export returns the maximum terminal display
width of any line in a string.

This is a repository-generation task. Create the package files yourself; do not
fetch or copy the reference repository.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, glibc, and ESM package semantics.
- `package.json` must identify the package as `widest-line` version `6.0.0`, use
  `"type": "module"`, and export `index.js` as the default root export and
  `index.d.ts` as its type declaration.
- The runtime dependency is `string-width` with the range `^8.1.0`. Do not add
  development dependencies, npm workspaces, native addons, custom loaders,
  registry configuration, or lifecycle scripts.
- Commit a lockfile with `lockfileVersion: 3`. A clean verifier runs
  `npm ci --offline --ignore-scripts --no-audit --no-fund` without network access.
- The function is synchronous, deterministic, stateless, and has no CLI, file,
  clock, randomness, subprocess, or network behavior.

# API Usage Guide

Export one default function from the package root:

```ts
export default function widestLine(string: string): number;
```

The input is a string. Split it at each line-feed character (`\n`), measure
each resulting line with `string-width@8`, and return the largest measured
display width. The return value is a non-negative integer.

The measured width follows the dependency's default terminal rules: ordinary
printable characters count as one column, CJK/full-width characters and emoji
clusters count as two columns, combining marks and control characters count as
zero, and ANSI escape sequences do not contribute columns. Tabs are ignored by
the dependency's default rules. A carriage return is a zero-width control
character, so the other characters on its line still contribute their widths.

Newline characters are separators, not part of any measured line. Empty input,
an input containing only line feeds, and an empty line have width zero. A
trailing line feed contributes an empty final line but does not change the
maximum. If several lines tie, return the common width; no line content is
returned.

The function must reject non-string input using the normal JavaScript type
error caused by the documented string contract. It must not mutate input and
must return the same result for repeated calls with the same string.

Examples:

```js
import widestLine from 'widest-line';

widestLine('a\nbe'); // 2
widestLine('古\n\u001B[1m@\u001B[22m'); // 2
widestLine('😀\né'); // 2
```

# Implementation Notes

Keep the package surface to the one default synchronous export. Preserve ESM
root exports and the declaration signature. Do not bundle a replacement for
`string-width`; use the declared dependency and keep runtime installation
offline-compatible. Do not expose tests, verifier code, or the Oracle solution
in the generated package.
