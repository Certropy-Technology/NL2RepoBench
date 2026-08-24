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
