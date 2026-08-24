# lossless-json candidate audit

Status: `blocked` / audit-only. This record does not contain a task manifest,
Harbor bundle, hidden tests, Oracle bytes, or npm cache.

## Source candidate

- Repository: `https://github.com/josdejong/lossless-json`
- Candidate revision: `7e89e3b789617e97e370dc8d923a124d6407a463`
- License: MIT, to be re-hashed from the detached source archive during
  `freeze-source`.
- The selected revision has a committed npm lockfile and zero declared runtime
  dependencies according to the discovery audit. Archive and license byte
  digests remain unrecorded in this checkout.

## Public scope proposal

The first candidate boundary should use string/tagged JSON operations only:

- parse source and return a canonical textual round-trip;
- stringify JSON-compatible values;
- compare/inspect lossless numeric text through tagged values;
- explicitly represent `LosslessNumber`, `bigint`, and dates as tagged objects
  if they cross the subprocess boundary.

Exclude reviver/replacer callbacks, custom number parsers, direct class identity,
untagged Date/BigInt and any value that cannot be represented deterministically
over the JSON request/response protocol.

## Build/test risks

- Public `lib` entrypoints are generated from TypeScript/Babel/Rollup tooling;
  generated-output provenance and the exact offline build command are not frozen.
- Vitest source tests and built-library tests must be collected in the final
  Node 22 verifier; no frozen denominator is claimed here.
- `npm ci --offline --ignore-scripts` and the complete integrity/store closure
  have not been independently verified for the exact revision.
- No task-specific node:test adapter, candidate boundary tests, Oracle or
  empty/stub/forgery/hang/offline controls exist yet.

## Reopen requirements

1. Reproduce exact archive/license hashes and source-only LOC.
2. Verify npm lock and offline closure from an empty cache.
3. Freeze generated build outputs or an allowlisted offline build toolchain.
4. Adapt the JSON-safe scope to a private structured `node:test` bundle.
5. Freeze collection and run Oracle three times plus all negative controls.

Until these gates pass, this is evidence for candidate discovery only and must
not be counted as a published Harbor task.
