# Zod authoring audit

- Frozen source: `colinhacks/zod` commit
  `e516c3baf22615e20934116abebfed6c000222c2`, tree
  `1f8fe962ebac8d3898be3f0eed07a2f2bba571e2`.
- Source archive SHA-256:
  `8d4a60e45991c6d3ca3884f0bc449a8b8229cb6af0eafcf095656037fdc81a5b`.
- License: MIT, verified from the frozen root `LICENSE` and package metadata.
- Runtime: digest-pinned Node 24.19.0 / npm 11.17.0 on Debian bookworm,
  `linux/amd64`.
- Upstream dependency lock: `pnpm-lock.yaml` SHA-256
  `03627f8232469285ad0ae0199f749bf5471f71e4d78f709cb74ad63bbf87bbc3`;
  the exact-revision build used pnpm 10.12.1.
- The package-local test script is not a valid baseline at this revision because
  its merged projects list resolves `vitest.compile.config.ts` relative to
  `packages/zod`. The bounded environment adaptation runs the same pinned
  Vitest from the repository root. Three offline runs each passed 264 test
  files and 4,181 tests.
- The registry's signed `zod@4.4.3` tarball predates the frozen revision and is
  not Oracle truth. The Oracle package was built from the exact frozen source;
  its tarball SHA-256 is
  `d9c8f500e05ab6d35d1efd0783eb1a4722416ac028924cf39d146c402a947d8c`.
- The production task is a 24-leaf JSON-safe Zod v4 classic slice. Candidate
  code runs only in an unprivileged subprocess in a separate no-network
  verifier. Hidden tests and reward output remain verifier-owned.
- Final Harbor 0.21.0 Oracle: valid `true`, `24/24`, reward `1.0`.
- Final controls: empty `0/24` with candidate-installation-failed; stub
  `1/24`; forgery `1/24` despite forged workspace reward files; call-hang
  completed in 201 seconds and failed closed as candidate-call-failed; offline
  control completed with reward `0` and all 24 calls failed. All final network
  receipts report `public_network_available=false`.
- The generic Node compiler now supports `stub`, `forgery`, `call-hang`, and
  `offline` controls. The generic Node runtime reports the declared
  `node-test-leaf-pass-rate-v1` contract. These shared changes are included in
  the worktree for integrator review and the pinned runtime digest is updated.
- Reviews, pilot Agent Runs, dataset integration, and publication remain the
  integrator's responsibility.
