# js-yaml instruction revalidation blocker

## Source freeze

- Queue source digest: `sha256:720d3329e8c32390b99c8588f6828f408a1dcc601e719c65fa54523dc08d6c03`
- Upstream revision: `6b4ff5e92474186b0c0381021ba4120f883c1995`
- Frozen source archive digest: `sha256:2f0874ea3403323297f422b9a8f91fd28e506ec80b124a0ee6a90175ee368096`
- Recovery log: `catalog/sources/js-yaml/evidence/revalidation-20260905/recovery-commands.log`
  (`sha256:c2e8b68e5438473a52b473c5479100152b4d9acecdcc14e54164f956a1d0e88e`)
- Recovery search: `catalog/sources/js-yaml/evidence/revalidation-20260905/recovery-search.json`
  (`sha256:e81fba5e3c0e702ecec79d78a393562de800d526241b538f83810907ecc6caea`)

## Failure class

`artifact/verifier`: the declared Oracle bundle is present and hash-valid, but
its `solve.sh` obtains the frozen source with `git clone
https://github.com/nodeca/js-yaml`. The bundle has no source archive or other
installable payload. No exact archive matching the frozen source digest was
found in the bounded trusted-local recovery search, and the pinned commit is
not present in local Git objects.

## Gate decision

The current instruction digest was validated before this decision. Two
production compiles completed and were byte-identical, with raw manifest
SHA-256 `d9337b41dd4b1738ed05ece740b5821578aeb56f3ee2a8c7cd95cbb269cb08b3`
and canonical manifest digest
`sha256:96a67f7ddd9d1016c0f4e89eb3ddfbf0db8c3c325b2aeca2b8be6314e86e591d`.
Oracle and controls were not run: running the existing Oracle would require
forbidden source-host access, and no exact replacement payload can be proposed
without unverifiable bytes. Prior
`production-evidence.json` and lifecycle metadata are preserved unchanged;
their old ignored run paths are not treated as current receipts.

## Next unblock action

Parent must supply or recover an independently hash-verified local source
archive or replacement private Oracle bundle containing revision
`6b4ff5e92474186b0c0381021ba4120f883c1995` and archive digest
`sha256:2f0874ea3403323297f422b9a8f91fd28e506ec80b124a0ee6a90175ee368096`.
After parent CAS registration, recompile twice with the locked Node toolchain,
then run the Oracle and all supported controls against the new manifest. Do
not authorize GitHub, npm, DNS, or another external service to bypass this
blocker.
