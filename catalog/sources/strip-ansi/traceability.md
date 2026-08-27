# `strip-ansi` traceability

Frozen source revision: `38ff9f2282540422031ed523f0060c7bb575e20f`
(`v7.2.0`). The source project exposes one default function and eight upstream
AVA behavior tests. The production verifier adapts those assertions to a
separate `node:test` verifier and expands only behaviors that are explicitly
documented in `instruction.md`.

| Leaf range | Public contract | Source/test basis |
| --- | --- | --- |
| 1 | npm name/version, ESM root export, declaration, default callable | `package.json`, `index.d.ts` |
| 2-5 | empty/plain/Unicode/whitespace text is preserved | upstream empty/plain tests and function fast path |
| 6-8 | SGR colors and modifiers are removed | upstream color and combined-style tests |
| 9-11 | 256-color and semicolon/colon truecolor CSI parameters are removed | frozen `ansi-regex@6.3.0` CSI contract |
| 12-14 | cursor, private-mode, and 8-bit CSI sequences are removed | upstream OSC/CSI fixture and 8-bit CSI test |
| 15-18 | OSC title and hyperlink strings terminated by BEL, ESC-ST, or C1-ST are removed | upstream BEL tests plus frozen dependency terminator contract |
| 19-20 | mixed and repeated sequences are removed globally while surrounding text is preserved | default function's documented all-match behavior |
| 21-23 | non-string values raise the specified `TypeError` using JavaScript `typeof` | source input guard |
| 24 | repeated calls are deterministic and do not leak regex state | source replace/global-regex behavior |

Every verifier leaf maps to the public instruction. The verifier does not test
an unadvertised CLI, ambient TTY detection, browser behavior, malformed
unterminated control strings, callbacks, symbols, BigInt, or custom prototypes.
