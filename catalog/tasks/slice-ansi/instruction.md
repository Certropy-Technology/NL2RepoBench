# Project Description

Build an installable npm package named `slice-ansi`, version `9.0.0`, from an
empty workspace. The package provides one ESM default export that slices a
terminal string by visible display columns while preserving ANSI styles,
OSC-8 hyperlinks, Unicode width, and grapheme-cluster boundaries.

This is a repository-generation task. Implement the documented behavior with
your own source and package files. Do not download, clone, or copy the pinned
upstream implementation or its tests.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The package root must be importable with:

  ```js
  import sliceAnsi from 'slice-ansi';
  ```

- `package.json` must declare name `slice-ansi`, version `9.0.0`, `type` as
  `module`, and a safe root export for `index.js` plus `index.d.ts`.
- Commit an npm lockfile with `lockfileVersion: 3`. A clean verifier runs:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The exact runtime dependencies are `ansi-styles@6.2.3` and
  `is-fullwidth-code-point@5.1.0`; the latter resolves to
  `get-east-asian-width@1.6.0`. Do not add other dependencies, workspaces,
  native addons, registry overrides, custom loaders, or lifecycle hooks.
- Runtime behavior is synchronous, deterministic, and local. Do not read
  files, inspect the environment, use the clock or randomness, spawn
  processes, access a TTY, or access the network.

# API Usage Guide

## Default export `sliceAnsi`

**Import path:** the package root.

**Signature:**

```ts
export default function sliceAnsi(
  string: string,
  startSlice: number,
  endSlice?: number,
): string;
```

`string` is a JavaScript string that may contain ordinary text, ANSI/VT
control sequences, or OSC-8 hyperlinks. `startSlice` and `endSlice` are
zero-based visible-column boundaries. The returned value contains the
selected text and only the control sequences needed to preserve the active
formatting of that selection.

The function is synchronous, does not mutate its arguments, and returns a new
string. The documented JSON boundary supplies finite numeric indexes and
strings. Values outside that domain, including symbols, BigInt, cyclic data,
custom objects, and non-finite numbers, are not scored.

## Visible columns and boundaries

- Ordinary narrow graphemes count as one visible column.
- East Asian Fullwidth/Wide characters count as two columns.
- Emoji-style graphemes, regional-indicator flags, keycaps, skin-tone
  sequences, combining-mark sequences, Hangul Jamo sequences, and ZWJ emoji
  sequences remain intact and are not split.
- A grapheme whose full width would cross `endSlice` is excluded. If the
  boundary falls inside a two-column grapheme, neither part is returned.
- When `endSlice` is omitted, slicing continues to the end after applying the
  same grapheme-safe start rule. A `startSlice` inside a wide grapheme skips
  that grapheme.
- CRLF is one grapheme cluster and is preserved as both characters.
- Empty or out-of-range selections return the empty string. A selection with
  no visible text must not contain style or hyperlink control codes.

Examples:

```js
sliceAnsi('abcdef', 1, 4); // 'bcd'
sliceAnsi('A\u3042B', 0, 2); // 'A'
sliceAnsi('A\u3042B', 1, 3); // '\u3042'
sliceAnsi('Ae\u0301B', 1, 2); // 'e\u0301'
```

## ANSI and VT controls

Recognize and exclude from visible-column counting:

- 7-bit CSI sequences beginning with `ESC [` and 8-bit CSI (`U+009B`),
  including SGR parameters separated by semicolons or colons.
- SGR style starts and ends, including modifier, foreground, background, and
  truecolor forms. Active styles are reopened at the start of a non-empty
  slice and closed in reverse order at its end.
- SGR reset and style replacement. A later style in the same family replaces
  the previous active style; closing one family preserves other active
  families.
- Non-SGR CSI sequences, malformed/truncated CSI prefixes, and generic OSC,
  DCS, SOS, PM, APC, and standalone ST control strings as non-visible control
  text. Do not swallow ordinary visible text after an incomplete prefix.

Known or unknown SGR codes must remain in the returned control text when they
are part of the selected range. Unknown active codes are closed with a reset
when required to avoid leaking formatting.

## OSC-8 hyperlinks

Recognize hyperlinks introduced by either `ESC ]8;` or 8-bit OSC (`U+009D`
followed by `8;`). Accept BEL, `ESC \\`, and 8-bit ST (`U+009C`) terminators,
including URI parameters. Hyperlink control text is not visible. A non-empty
slice inside a hyperlink preserves its opening form and emits a matching
closing form. A slice containing only a hyperlink opening or closing emits no
empty hyperlink. Mixed opening and closing terminators are preserved when
possible, and a generated close uses the opening prefix and its terminator.

## Packaging

Keep the implementation self-contained behind the package root. Include a
matching TypeScript declaration for the default export. Do not expose a CLI or
copy upstream tests. The verifier calls the default export through an
isolated child process; private tests and the reference implementation are not
part of the package to implement.

# Implementation Notes

The frozen source's original AVA suite exercises 94 assertions and includes
randomized checks. The production contract is a deterministic 24-leaf
`node:test` slice covering package shape, ordinary and wide text, grapheme
boundaries, ANSI/SGR state, OSC-8 links, malformed controls, and stateless
repeatability. This is a documented boundary adaptation, not a claim of full
upstream test parity.

Use a bounded parser or tokenizer for control sequences and a deterministic
Unicode grapheme/width strategy. The evaluator observes only JSON-compatible
strings and numbers through the default export. Candidate code must not be
imported into the trusted test process, and must not write verifier reports.
