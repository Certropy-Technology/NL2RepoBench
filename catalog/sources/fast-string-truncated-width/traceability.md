# `fast-string-truncated-width` traceability

Frozen source revision: `1d50ce0c1497c1399eed50f87926817587049358`.
The upstream package exposes one default function, three public type aliases,
and 18 executable offline test groups. The production verifier maps those
behaviors into 39 isolated leaves and expands only contract details documented
in `instruction.md`.

| Leaf range | Public contract | Frozen source/test basis |
| --- | --- | --- |
| 1 | package identity, ESM root, no runtime dependencies, declaration surface | `package.json`, `src/index.ts`, `src/types.ts` |
| 2-5 | empty/plain widths, ANSI source indices, documented truncation example | upstream raw-result and basic-width groups |
| 6-10 | SGR/OSC zero width, controls, tabs, combining marks | upstream ANSI, control, tab, combining, hyperlink groups |
| 11-20 | CJK/Hangul/full-width/ambiguous, emoji clusters, surrogate indices, half-width kana, ordinary Unicode | upstream basic, emoji, Unicode, half-width, and surrogate groups |
| 21-25 | ellipsis reservation, non-fitting ellipsis, zero/negative limits, ANSI truncation index | upstream Latin and ANSI truncation tables plus public result semantics |
| 26-31 | `controlWidth`, `tabWidth`, `emojiWidth`, `regularWidth`, `wideWidth`, `ellipsisWidth` overrides | public option types and width constants in the frozen source |
| 32-35 | CJK/emoji/hyperlink-safe truncation and mixed options | upstream CJK, emoji, hyperlink truncation groups |
| 36-39 | exact-fit behavior, repeat determinism, 1,000-code-point chunk boundaries, bounded long-tail truncation | public deterministic contract and frozen parser chunking behavior |

Every verifier leaf maps to public instruction text. The verifier does not test
the skipped mutable network emoji corpus, a CLI, browser APIs, native addons,
ambient terminal state, invalid TypeScript-only input types, or undocumented
malformed ANSI sequences.
