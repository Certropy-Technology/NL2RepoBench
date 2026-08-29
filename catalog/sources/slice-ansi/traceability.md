# `slice-ansi` traceability

Frozen source revision: `50fc7781f5dd4d1421dbe061822d815708831af4` (`9.0.0`).

The upstream checkout contains `index.js`, `tokenize-ansi.js`, a TypeScript
declaration, package metadata, and one AVA test file. The production verifier
uses only a private deterministic adapter and does not expose the upstream
test file.

| Leaves | Public behavior covered | Source basis |
| --- | --- | --- |
| 1 | Package name/version, ESM root, and callable default export | package metadata and declaration |
| 2-3 | Plain visible slicing, omitted end, and empty/out-of-range boundaries | upstream `main` and empty-slice assertions |
| 4-5 | ANSI SGR styles and style state across a slice | upstream colored, modifier, multi-style, and reset assertions |
| 6-7 | Non-visible CSI/control strings and malformed prefixes | upstream non-canonical CSI, generic OSC, DCS, SOS, PM, APC, and truncated-tail assertions |
| 8-10 | ANSI color variants, unknown codes, and visible-text preservation | upstream truecolor, colon SGR, and unknown-color assertions |
| 11-14 | Fullwidth, surrogate pairs, combining marks, ZWJ sequences, and CRLF | upstream Unicode boundary assertions |
| 15-16 | Regional indicators, keycaps, emoji presentation, and text-presentation symbols | upstream grapheme and emoji-width assertions |
| 17-20 | Wide-character boundary exclusion, start-inside-wide behavior, and styled wide text | upstream wide-character and style boundary assertions |
| 21-23 | OSC-8 hyperlinks with BEL, ESC-ST, C1-ST, parameters, and partial slices | upstream hyperlink tests |
| 24 | Stateless mixed calls and deterministic repeatability | upstream randomized invariant and pure-function behavior |

Every scored leaf is an independent `node:test` leaf with a unique ID after
collection. The frozen denominator is 24. Collection errors or a different
leaf count invalidate the verifier result rather than changing the denominator.

The verifier boundary excludes callbacks, filesystem handles, TTY state,
non-JSON values, package subpath exports, and the upstream AVA/XO development
toolchain. These are scope boundaries, not hidden requirements.
