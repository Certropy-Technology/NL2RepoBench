# `parse-npm-tarball-url` Repair Provenance

This source authority supersedes the earlier static blocked audit in
`blocked.md`. The audit remains as historical evidence of the initial package
shape and dependency review.

## Frozen source

- upstream: `https://github.com/pnpm/parse-npm-tarball-url`
- revision: `1cf57de3b5451ba2efd42fe8ed4eb8ede6f0f706`
- license: MIT, declared by the frozen `package.json` and present in `LICENSE`
- `git archive --format=tar <revision>` SHA-256:
  `cd10dd7f52286e08ac646447dab6312bc072f89b5deca56122bb9405f429ccf2`
- runtime dependency from the frozen manifest: `semver ^7.6.3`
- authored runtime closure: exact `semver 7.7.4`, npm lockfile v3, npm `11.17.0`

## Packaging adaptation

The frozen checkout contains TypeScript source but no `lib/` output and uses
pnpm/TypeScript development scripts. The published task contract therefore
requires the observable built ESM package shape (`lib/index.js` and
`lib/index.d.ts`) and removes development/lifecycle metadata from the runtime
package. The Oracle runtime was compiled from the exact frozen source under
the locked Node 24 toolchain; candidate agents must implement the public
contract from the instruction and do not receive this runtime or source.

## Test traceability

The private 14-leaf slice is boundary-driven rather than an execution of the
upstream TypeScript test file. It covers the five valid source examples,
host/URL semantics, loose SemVer preservation, five invalid/null cases, and
the two assertion/error cases. The verifier-owned adapter returns only JSON
values and bounded exception metadata.

## Missing test-bundle remediation evidence

The originally referenced test bundle digest
`sha256:b5f00cb69c10fb8e6019abd8fbdf46016e0cc0e67c165964ff704d323116daa7`
was present in the local private artifact store as a 3,426-byte gzip-tar at the
legacy flat path `artifacts/private/sha256/<full-digest>`, not at the resolver's
prefix path. Its three members were the task-local `contract.test.mjs`,
`test_client.mjs`, and `candidate_adapter.mjs`; their contents match the
private boundary source and the 14-leaf contract. It was not treated as a
publishable runtime artifact.

A task-local, content-addressed rebuild renamed only the helper to
`candidate_adapter.txt` and changed `test_client.mjs`'s private helper path.
This preserves the adapter protocol and all assertions while preventing the
Node test collector from counting the helper as a test file. The rebuilt bundle
is `sha256:6c08d505abd0581f533082cba7abb65edac25522abdd09867056cb36c23c8824`,
3,430 bytes, with members `candidate_adapter.txt`, `contract.test.mjs`, and
`test_client.mjs`.

The first compile's Oracle run collected 15 and was invalid against the frozen
14 denominator; the corrected bounded retry collected exactly 14, was valid,
and passed 13/14 for reward `0.9285714285714286`. These authoring runs were
temporary and are summarized in `blocked.md`; private bundles remain in the
content-addressed artifact store rather than under the public source catalog.
The task remains blocked and no generated runtime is retained because empty,
stub, forgery, and offline controls were not completed.
