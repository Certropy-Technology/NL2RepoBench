# Authoring Provenance

- Upstream: `https://github.com/chalk/wrap-ansi`
- Frozen revision: `c6b6259a58843e491e8703c5010a2a517b5f5738`
- Frozen package version: `10.0.1`
- Commit timestamp: `2026-08-18T00:40:33+02:00`
- Source archive: 92,160 bytes, SHA-256
  `dccdb394d6c59a10e8f50aba2b8ebbbbf4f27a3a2d822e73a8fa9190934ccec6`
- License: MIT, from upstream `license`; SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Source files at the revision: `index.js`, `index.d.ts`, `package.json`,
  `test.js`, and repository metadata. The scored public API is the default
  `wrapAnsi(string, columns, options?)` export.
- The upstream `npm test` command passed in the pinned Node 24.19.0/npm 11.17.0
  image: 80 runtime leaves passed, none failed, and the XO and declaration
  checks exited successfully. The task-local baseline log SHA-256 is
  `ba755ec031f8c42e4b3ee61e1d3301601d8f154c00a48713b7b193b234a66719`.
- Exact runtime closure: direct `ansi-styles@6.2.3` and
  `string-width@8.2.0`; transitive `get-east-asian-width@1.6.0`,
  `strip-ansi@7.2.0`, and `ansi-regex@6.3.0`.
- The private npm v3 lock/cache artifact is 348,160 bytes with SHA-256
  `e2afe0fb68b4a534011a110eee20317c0ff56001d792ae19373e45987af83487`.
- The private tests are independently authored deterministic contract tests;
  upstream test bytes are not placed in the candidate or verifier bundle. The
  verifier freezes 44 `node:test` leaves behind a UID-separated JSON child.

The raw source archive and npm cache are task-local private artifacts. The
model agent receives only the public instruction and an empty workspace.
