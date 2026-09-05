# Project Description

Implement the npm package `range-parser` version 1.2.1 as a CommonJS package in an empty workspace. The package parses an HTTP `Range`-style header into inclusive integer intervals relative to a representation size. The evaluator installs the package with npm in an isolated, offline environment and calls its public export through a separate subprocess.

# Natural Language Instruction

Create the self-contained CommonJS package and export one callable parser.
Implement explicit, open, suffix, malformed, unsatisfiable, whitespace,
custom-unit, multiple-range, and combined-range behavior exactly as specified.
Do not add a CLI, runtime dependency, network path, or native extension.

# Supports or Environment Configuration

- Node.js 24.x and npm 11.x on Linux amd64.
- A package root with `package.json` naming the package `range-parser`, version `1.2.1`, and a CommonJS-compatible entry that resolves to `index.js` (an explicit `main: "index.js"` is acceptable, but Node's default entry is also valid).
- The package must be installable by `npm pack` with lifecycle scripts disabled and must not require runtime dependencies.
- The public module export is the range parser function described below. Do not add a CLI, network access, native extension, or lifecycle hook.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── README.md
└── LICENSE
```

`index.js` is resolved by `require("range-parser")` and contains the public
callable export.

# API Usage Guide

**Import path:** the package root `range-parser`, loaded with
`const parseRange = require('range-parser')`.

**Signature:** `parseRange(size: number, str: string, options?: {combine?: unknown}): Array<{start: number, end: number}> | -1 | -2`.

`parseRange(size, str, options)`

- `size`: a non-negative representation length used to cap the inclusive end position and to calculate suffix ranges. Return values for unusual non-numeric sizes are outside the contract.
- `str`: a string containing a range unit, `=`, and one or more comma-separated ranges. A range is `start-end`, `start-`, or `-suffix-length`; surrounding whitespace around positions is ignored.
- `options`: optional object. When `options.combine` is truthy, overlapping and adjacent intervals are merged while the resulting array keeps the original order of the first interval in each merged group.
- Return an array of objects shaped `{start: number, end: number}`. The returned array also has a `type` property containing the text before the first `=`. A malformed header returns `-2`; a syntactically valid header with no satisfiable interval returns `-1`.
- Throw `TypeError` with message `argument str must be a string` when `str` is not a string.
- End positions larger than `size - 1` are capped. A suffix larger than the representation covers the whole representation. Invalid comma-separated members are ignored when another valid satisfiable member remains.

The parser must preserve the numeric `start` and `end` values as inclusive
positions. For `start-end`, both endpoints are present and the end is capped;
for `start-`, the end is the final representation position. For `-N`, the
range starts at `size - N` when that is non-negative and otherwise starts at
zero. A zero-size representation has no satisfiable positions and therefore
returns `-1` for otherwise well-formed range members.

The unit is the text before the first equals sign and may be a custom token;
the parser does not restrict it to `bytes`. Whitespace around the unit,
equals sign, commas, hyphens, and decimal positions follows the documented
header grammar. Decimal positions must be finite non-negative integers. An
empty member or a member with missing required digits is invalid, while a
valid member after an invalid member can still produce an ordinary result.

When `combine` is truthy, merge intervals that overlap or touch at adjacent
positions. The merged interval uses the lowest start and highest end from its
group, and the output order is the order of the first interval in each group.
When `combine` is absent or falsy, retain every satisfiable interval in input
order, including overlapping intervals. The custom `type` property remains
the exact unit text on every ordinary result array.

Example:

```js
const parseRange = require('range-parser')
const ranges = parseRange(150, 'bytes=0-4,90-99,5-75,100-199', {combine: true})
// ranges.type === 'bytes'
// ranges is [{start: 0, end: 75}, {start: 90, end: 149}]
```

# Implementation Notes

Keep the implementation deterministic and self-contained. Preserve the distinction between malformed (`-2`) and unsatisfiable (`-1`) headers, including headers containing both invalid members and unsatisfiable members. Preserve input order for ordinary results. The evaluator checks CommonJS loading, numeric boundaries, whitespace, custom range units, invalid members, suffixes, and range combination behavior through a fixed collection.

# Examples

```js
const parseRange = require("range-parser");
parseRange(150, "bytes=0-4,90-99", {combine: true});
```

```js
parseRange(100, "bytes=-20");
```

```js
parseRange(100, "items=5-9");
```

# Error Handling and Boundary Conditions

Return `-2` for malformed headers and `-1` for valid headers with no
satisfiable interval. Cap ends at `size - 1`, preserve input order, and throw
`TypeError("argument str must be a string")` for a non-string header.

The public call is synchronous and has no side effects: it does not read files,
write files, mutate global state, access the network, or start a subprocess.
Its only observable state is the returned array and its `type` property. The
array objects contain own numeric `start` and `end` fields; sentinel returns
are the numeric values `-1` and `-2`, not strings or thrown errors. Values are
safe to serialize as ordinary JSON for the bounded adapter.

The module example is `import range_parser` only as a language-level alias in
documentation; the actual Node entry is CommonJS and must be loaded with
`require("range-parser")`. Do not expose an ESM-only replacement or change the
callable default shape. The parser has no asynchronous API and returns before
the caller's next statement.

Callers may reuse the returned value or serialize it immediately; no hidden
iterator, promise, stream, or callback contract exists. The parser should not
coerce a non-string header into text, and it should not coerce a non-numeric
size into a valid representation length. Keep negative and fractional bounds
outside the documented numeric domain deterministic rather than relying on
locale rules. Preserve the ordinary result's `Array.isArray` behavior and its
stable own-property ordering when inspected by a JSON bridge.
