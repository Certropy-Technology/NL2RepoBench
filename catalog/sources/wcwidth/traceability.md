# wcwidth contract traceability

The 36 private leaf IDs map to the public contract in `instruction.md` as follows:

| Contract area | Leaf IDs |
| --- | --- |
| Package exports and compatibility | `metadata`, `legacy-module`, `public-types` |
| Codepoint/string width and Unicode edge cases | `wcwidth-basic`, `wcswidth-basic`, `ambiguous`, `virama-and-emoji`, `n-argument` |
| Grapheme navigation | `graphemes`, `reverse-boundary` |
| Terminal parsing and controls | `iter-sequences`, `width-sgr`, `width-controls`, `width-ignore`, `width-kitty`, `clip-controls` |
| Display-aware layout | `alignment`, `wrap-ascii`, `wrap-cjk`, `wrap-sgr`, `clip-cjk`, `clip-sgr`, `sgr-propagation` |
| Terminal correction and stable tables | `terminal-override`, `determinism-4` |
| OSC 8 and Kitty records | `hyperlink-params`, `hyperlink-unit`, `text-sizing-params`, `text-sizing-unit`, `text-sizing-parse` |
| Determinism | `determinism-1`, `determinism-2`, `determinism-3` |

Every leaf observes only explicit JSON-safe projections or exception data. No private test file,
implementation helper, generated table name, source archive, or candidate-owned report is read by
the trusted verifier.
