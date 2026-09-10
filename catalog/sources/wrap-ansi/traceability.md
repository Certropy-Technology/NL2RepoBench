# Traceability

Frozen source revision:
`c6b6259a58843e491e8703c5010a2a517b5f5738` (`10.0.1`). The verifier
collects 44 unique `node:test` leaves.

| Leaf range | Public contract | Source and test basis |
| --- | --- | --- |
| 1 | package name/version, ESM root export, declaration, callable name and three-parameter signature | upstream package metadata and `index.d.ts` |
| 2-7 | soft and hard wrapping, first-word handling, long words, and `wordWrap` filling | upstream wrapping modes and API options |
| 8-16 | trim defaults, preserved spaces, empty/whitespace input, zero columns, CRLF, trailing newline, and independent input rows | upstream whitespace and line-boundary behavior |
| 17-25 | zero-width SGR, style close/reopen, nested foreground/background/modifiers, resets, 256-color, RGB, and colon color syntax | upstream ANSI parser and style-state tests |
| 26-31 | BEL/ST OSC 8 wrapping, adjacent URL identity, complete CSI/C1 preservation, and unsupported control-string text | upstream hyperlink and control-sequence boundary |
| 32-34 | 8-column tab stops, repeated tabs, and ANSI-independent tab width | upstream tab expansion behavior |
| 35-40 | fullwidth text, surrogate-pair emoji, ZWJ/flag/combining graphemes, and ANSI around grapheme clusters | upstream Unicode width and segmentation behavior |
| 41-44 | trim inside styled spans, untrimmed styled spaces, trailing empty rows, and runtime `String()` coercion | upstream style/trim boundaries and exported implementation behavior |
| Runtime boundary | offline pack/install, bounded workspace, UID-separated child calls, report ownership, timeout, and no egress | compiler-generated Node verifier plus `test_client.mjs` |

The Oracle bundle is private and contains only a solve script that fetches and
verifies the frozen upstream commit during the trusted Oracle run. It is never
available to the model candidate.
