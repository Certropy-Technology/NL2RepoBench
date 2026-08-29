# Meow Authoring Provenance

## Immutable source and license

- Upstream: `https://github.com/sindresorhus/meow`
- Revision: `1f3ec6cfd29a2df43ad637023be57001db49c410` (`Meta tweaks`)
- Git archive: 768,000 bytes, SHA-256 `20135ee5f801dae4630dc1550e118a5bacd415768543e0073b01e60152895f69`
- License: MIT; license bytes SHA-256 `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- No submodules. The exact tree contains 59 tracked files and no committed npm lockfile.

## Baseline and remediation

The first clean build probe exited 127 because `rollup` was absent before dependency installation. With Node `v22.23.1`/npm `10.9.8`, `npm install --ignore-scripts --no-audit --no-fund` installed 675 locked packages, `npm run build` generated `build/index.js` and `build/index.d.ts`, and `npm test` passed 148 upstream tests. The production image is pinned to Node `24.19.0`/npm `11.17.0`; the generated build is repeated under that locked runtime when the private closure is packed.

The upstream suite uses AVA, TSD, child processes, and process-exit assertions. The Harbor task therefore uses a smaller fixed `node:test` contract over JSON-safe calls, covering the public parser behavior without importing candidate code into the trusted verifier. Process exit, callback predicates, TypeScript-only checks, and development lint are explicitly excluded from the scored slice.

## Network and artifacts

Candidate and verifier runs use `no-network`, a private npm v3 lock/cache closure, and `ignore-scripts`. Only the trusted Oracle receives a run-scoped authorization for the exact upstream source host. Private dependency, test, verifier, command, and Oracle bytes are content-addressed under `.nl2repo/artifacts` and are not copied into this public source directory.
