# Crypto-random-string instruction revalidation blocker

- The migrated instruction validates at source digest
  `sha256:f23624d39f95ab92d8ff4f8360f55e2d27c2e137d11da9c5870258a7b7514ba4`.
- Two production compiles using Harbor `0.21.0`, `toolchain.node.lock.toml`,
  and the private artifact store were byte-identical. The compact manifest is
  `bundle-manifest.json` and binds canonical digest
  `sha256:131e052a9c684385042ca3c911301827edef16bcc367642b677106938157d965`.
- All four private task artifacts in `task.toml` were present and matched their
  declared byte sizes and SHA-256 digests.
- The inspected Oracle payload is not compatible with the required NoNetwork
  contract. Its `solve.sh` performs `git fetch` from GitHub at runtime before
  producing the local reference implementation. The payload details and script
  hash are recorded in `oracle-payload.json`.
- Oracle, controls, grading, network, collection, result, and failure-set
  receipts were not generated. `matrix-status.json` records each as
  `not-run`; no result or reward is fabricated.
- Historical `production-evidence.json` was deliberately not replaced because
  its old run paths are not durable in this worktree.

## Remediation

Provide a hash-verified local source archive or an equivalent offline Oracle
payload that preserves the pinned revision and source digest. Recompile the
current source and rerun Oracle, empty, stub, forgery, hang, install-script,
loader-hook, and offline controls, persisting every receipt under this
directory before updating `production-evidence.json`.
