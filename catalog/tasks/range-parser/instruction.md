# Project Description

Implement the npm package `range-parser` version 1.2.1 as a CommonJS package in an empty workspace. The package parses an HTTP `Range`-style header into inclusive integer intervals relative to a representation size. The evaluator installs the package with npm in an isolated, offline environment and calls its public export through a separate subprocess.

# Supports

- Node.js 24.x and npm 11.x on Linux amd64.
- A package root with `package.json` naming the package `range-parser`, version `1.2.1`, and a CommonJS-compatible entry that resolves to `index.js` (an explicit `main: "index.js"` is acceptable, but Node's default entry is also valid).
- The package must be installable by `npm pack` with lifecycle scripts disabled and must not require runtime dependencies.
- The public module export is the range parser function described below. Do not add a CLI, network access, native extension, or lifecycle hook.

# API Usage Guide

Import the CommonJS export with `const parseRange = require('range-parser')`.

`parseRange(size, str, options)`

- `size`: a non-negative representation length used to cap the inclusive end position and to calculate suffix ranges. Return values for unusual non-numeric sizes are outside the contract.
- `str`: a string containing a range unit, `=`, and one or more comma-separated ranges. A range is `start-end`, `start-`, or `-suffix-length`; surrounding whitespace around positions is ignored.
- `options`: optional object. When `options.combine` is truthy, overlapping and adjacent intervals are merged while the resulting array keeps the original order of the first interval in each merged group.
- Return an array of objects shaped `{start: number, end: number}`. The returned array also has a `type` property containing the text before the first `=`. A malformed header returns `-2`; a syntactically valid header with no satisfiable interval returns `-1`.
- Throw `TypeError` with message `argument str must be a string` when `str` is not a string.
- End positions larger than `size - 1` are capped. A suffix larger than the representation covers the whole representation. Invalid comma-separated members are ignored when another valid satisfiable member remains.

Example:

```js
const parseRange = require('range-parser')
const ranges = parseRange(150, 'bytes=0-4,90-99,5-75,100-199', {combine: true})
// ranges.type === 'bytes'
// ranges is [{start: 0, end: 75}, {start: 90, end: 149}]
```

# Implementation Notes

Keep the implementation deterministic and self-contained. Preserve the distinction between malformed (`-2`) and unsatisfiable (`-1`) headers, including headers containing both invalid members and unsatisfiable members. Preserve input order for ordinary results. The evaluator checks CommonJS loading, numeric boundaries, whitespace, custom range units, invalid members, suffixes, and range combination behavior through a fixed private test collection.
