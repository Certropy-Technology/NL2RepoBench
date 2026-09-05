# Furl instruction revalidation blocker

- The expected migrated instruction digest is `sha256:f5e2e3638f23791bfd3d8dac33493bcd9480a5f0ca4351fdbb2a8dcec8dd6404`.
- The frozen source digest is `sha256:11dfb073771de0ecf9117808aa37282afff150be2ba809f15e01f9802b21a197`.
- The dependency lock, verifier bundle, and Oracle bundle were present and verified by size and SHA-256.
- Two production compiles using the locked toolchain and local CAS were byte-identical; both produced canonical manifest `sha256:48fa9cf0a1c2dba0d5cb8c91e82d058cd5715c9c4c1b41f182fbe6592614e242`.
- The Oracle `solve.sh` performs runtime `git clone` and `git fetch` from `github.com`. The required NoNetwork policy forbids that fetch, so Harbor Oracle and controls were not run.
- Lifecycle, historical production evidence, generated runtime, and frozen denominator remain unchanged.

Remediation: replace the runtime-fetching Oracle payload with a local, digest-verified source payload or otherwise make the frozen source available through the approved private CAS before rerunning the full Oracle, empty, stub, forgery, and offline matrix.
