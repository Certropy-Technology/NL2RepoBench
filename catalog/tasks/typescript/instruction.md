# Build `@typescript/typescript`

## Project Description

Build an installable npm package named `@typescript/typescript`, version
`0.0.0`, from an empty workspace. The pinned upstream revision is the native
TypeScript preview package. This task scores a bounded, JSON-safe slice of its
lexical scanner utilities and bidirectional `SpanMap` API.

## Supports

- Node `24.19.0` and npm `11.17.0` on `linux/amd64`.
- ESM package semantics with an importable scoped package named
  `@typescript/typescript`.
- A package root export exposing `version` and `versionMajorMinor`, plus these
  subpath exports:
  `@typescript/typescript/package.json`,
  `@typescript/typescript/unstable/ast`, and
  `@typescript/typescript/unstable/ast/scanner`.
- A committed npm lockfile using lockfile version 3. The package has no runtime
  dependencies and must install offline with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- No lifecycle scripts, workspaces, native addons, registry configuration,
  runtime downloads, or network access.

The candidate must submit built JavaScript and the package metadata needed by
the exports above. Do not submit the upstream repository, hidden tests,
grader, reward files, npm cache, or Oracle material.

## API Usage Guide

### Package metadata and root export

The package manifest has name `@typescript/typescript`, version `0.0.0`, type
`module`, no `scripts`, `dependencies`, or `devDependencies` fields, and an
Apache-2.0 license. The root import returns `version === "0.0.0"` and
`versionMajorMinor === "7.1"`.

### Scanner

**Import path:** `@typescript/typescript/unstable/ast/scanner`.

Implement the exported `createScanner(skipTrivia, languageVariant, text,
start?, length?)` factory and its scanner object. The JSON adapter exercises
tokenization of declarations, punctuation, comments, whitespace, numeric and
string literals, Unicode identifiers, operators, keywords, templates, and
unterminated strings. Each token result includes the canonical `SyntaxKind`
name, original token text and value, UTF-16 `fullStart`, `start`, and `end`
positions, and the scanner flags `precedingLineBreak`, `unicodeEscape`, and
`unterminated`.

The scanner must honor `skipTrivia`, `LanguageVariant.Standard`, explicit
start/length bounds, and JavaScript UTF-16 indexing. `EndOfFile` is included as
the final token. Do not execute input text.

### Scanner utilities

**Import path:** `@typescript/typescript/unstable/ast/scanner`.

The following JSON-safe utilities are scored:

- `tokenToString(SyntaxKind)` and `stringToToken(text)` map token spellings
  and canonical names, returning `null` for an unknown spelling.
- `computeLineStarts(text)` returns zero-based line-start offsets for LF, CRLF,
  and Unicode line separators.
- `skipTrivia(text, position, stopAfterLineBreak?, stopAtComments?, inJSDoc?)`
  returns the next non-trivia position under the supplied flags.
- `getShebang(text)` returns a leading hashbang line without its line ending,
  or `null` when none is present.
- `isIdentifierText(text, languageVersion?, languageVariant?)` validates an
  identifier spelling under the selected script target and language variant.
- `getLeadingCommentRanges(text, position)` and
  `getTrailingCommentRanges(text, position)` return comment kind, `pos`, `end`,
  and `hasTrailingNewLine` fields.

### SpanMap

**Import path:** `@typescript/typescript/unstable/ast`.

`new SpanMap(segments)` receives at most 128 JSON segment objects. Each segment
has non-negative `virtualStart`, `virtualEnd`, `originalStart`,
`originalEnd`, a `SpanMapKind` of `Verbatim`, `Atom`, or `Alias`, and optional
`SpanMapFeature` flags. Omitted features mean `All`.

The scored methods return JSON-safe positions/ranges and canonical fidelity
names:

- `virtualToOriginalPosition(position)` and
  `virtualToOriginalSpan({pos,end})` map virtual text to original text.
- `virtualToOriginalPositionForFeature(position, feature)` and
  `virtualToOriginalSpanForFeature(range, feature)` return `None` fidelity when
  the selected feature is disabled.
- `originalToVirtualPositions(position, feature)` returns every matching
  projection, including duplicate groups and atom fidelity.
- `originalToVirtualSpans(range, feature)` returns exact, atom, or approximate
  projections for contained and cross-segment ranges.
- `SpanMap.isExact`, `SpanMap.isSingleSegment`, and `SpanMap.isNone` classify
  `SpanMapFidelity` values.

Gaps map to deterministic insertion points with `None` fidelity. Verbatim
segments preserve offsets; atom segments map to their complete target range;
cross-segment ranges are `Approximate`. Segment ordering and feature filtering
must be deterministic.

## JSON Boundary

The verifier owns the subprocess adapter. Requests contain only bounded JSON
objects, strings, finite integers, booleans, arrays, and null. No JavaScript
source, callbacks, functions, object identity, native handles, or custom
classes cross the boundary. The adapter imports the fixed package name and
normalizes enum values and range objects to JSON. The candidate must implement
the package API, not a custom grader-facing server.

## Implementation Notes

Reproduce the observable behavior of the pinned native-preview revision rather
than a generic JavaScript lexer or one-directional range mapper. Preserve
UTF-16 offsets, canonical enum behavior, comments, escape flags, gap handling,
duplicate original projections, atom ranges, and feature-aware fidelity.

Do not rely on the current directory, network, environment variables, a global
TypeScript installation, or nondeterministic state to change scored results.
