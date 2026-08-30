# `strip-final-newline` traceability

Frozen source revision: `a1bfe78e3a3de2f73ed3a7600932d7cc952732b4`.
The private adapter is required because candidate objects and byte-view
identity cannot be transported safely into the trusted verifier process.

| Leaves | Public contract | Frozen source basis |
| --- | --- | --- |
| 1 | npm metadata, ESM root export, declaration entry, callable default | package metadata and `index.d.ts` |
| 2-10 | empty/no-op strings, LF, CRLF, repeated LF, mixed line endings, Unicode, and preservation of other trailing characters | `index.js`, README examples, and upstream string assertions |
| 11-20 | empty/LF/CRLF byte arrays, repeated LF, arbitrary bytes, result type, shared storage, and no-op identity | `index.js`, README performance note, and upstream Uint8Array assertions |
| 21-25 | boolean, null, plain object, DataView, and multi-byte typed array rejection with the documented error contract | `index.js` invalid-input branch and upstream invalid-type assertions |
| 26-29 | stable repeated calls, empty input repeatability, CRLF view offsets, and non-mutation of input bytes | factory behavior, README examples, and binary subarray semantics |

Every assertion in the private 29-leaf adapter is stated in `instruction.md`.
The task does not test CLI behavior, filesystem/network access, callbacks,
TypeScript compilation, or unbounded adversarial inputs.
