# `ansi-regex` traceability

Frozen source revision: `7cf0228990eb38c27f9897f4fb17d42d39075a20`.
The private adapter is required because a JavaScript `RegExp` is not a JSON
value; all candidate imports happen in that child process.

| Leaves | Public contract | Frozen source basis |
| --- | --- | --- |
| 1 | npm metadata, ESM root export, declaration, callable default | package metadata and `index.d.ts` |
| 2-6 | empty/plain/Unicode/whitespace preservation and no cross-call state | README examples and function factory behavior |
| 7-12 | SGR, 256-color, colon truecolor, cursor, private-mode, and 8-bit CSI | CSI expression contract and ANSI test families |
| 13-17 | OSC BEL, ESC-ST, C1-ST, hyperlinks, and mixed payloads | README hyperlink example and OSC terminator contract |
| 18-21 | global versus `onlyFirst`, explicit false, and ordinary-text boundaries | documented option semantics |
| 22-24 | repeated construction, repeated matching, and source/flags stability | stateless factory contract |

Every assertion in the private 24-leaf adapter is stated in `instruction.md`.
The task does not test CLI behavior, file/network access, callbacks, arbitrary
objects, or unbounded adversarial regex inputs.

