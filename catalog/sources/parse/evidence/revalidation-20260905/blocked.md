# parse instruction revalidation checkpoint

- task: `parse`
- queue source digest: `sha256:cdd52c2c408b49d4ba077503d7b7224f2c888f361b20eefcb238e08e8cbbe070`
- frozen upstream revision: `8059e320eccf40d750843006dd2ef25197bbff74`
- declared source archive: `133120` bytes, SHA-256 `sha256:eb48010aafcc5a9699285f59fbe5abce50bacba1e6da175072163a7ed3c38176`
- locally verified source archive: `133120` bytes, SHA-256 `sha256:eb48010aafcc5a9699285f59fbe5abce50bacba1e6da175072163a7ed3c38176`; archive contains the frozen `LICENSE` whose SHA-256 is `sha256:2cc9942fe3f52a669c1fbb4e0bae9a27300d56564a382e954845c3256c4cabe2`.
- declared dependency lock: `204` bytes, SHA-256 `sha256:24713a5496e38f6da905cbc7944c15efd8863916e5da6825b835f66aa99068f7`; the exact bytes are present in the local artifact store.
- declared verifier artifact: `71680` bytes, SHA-256 `sha256:34c5369de94a0a17da612822ce17cf5619777ca43b4e6287f238932926845755`; not present in the currently available local CAS/handoff search scope.
- declared Oracle artifact: `143360` bytes, SHA-256 `sha256:2725090f72efa86930fd19c6abf806b68f0c03373696e27b44c376891b85365d`; not present in the currently available local CAS/handoff search scope.

## Commands and results

1. `uv run nl2repo task validate-source catalog/sources/parse` — exit `0`; reported source digest `sha256:cdd52c2c408b49d4ba077503d7b7224f2c888f361b20eefcb238e08e8cbbe070`.
2. Bounded local recovery search over trusted local generated projections, CAS, historical handoffs, archives, and caches — command exceeded the `1200` second bound and was terminated by timeout; no verifier or Oracle artifact with either declared digest was established before termination.

## Classification

`artifact-or-verifier-blocked`: the frozen source payload and dependency lock are hash-verified, but the declared private verifier and Oracle artifacts required for a fresh post-migration compile/Harbor matrix are unavailable. The prior `production-evidence.json` receipts are explicitly stale for this instruction digest and are not reused.

## Parent next step

Parent should register or recover exact private artifacts by the declared size and SHA-256, then compile twice with the locked toolchain and run a fresh NoNetwork Harbor Oracle plus the complete supported control matrix. Until then, leave lifecycle, production evidence, generated projection, CAS, and reports unchanged.
