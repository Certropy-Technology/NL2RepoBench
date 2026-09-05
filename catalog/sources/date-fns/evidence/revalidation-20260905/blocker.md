# date-fns instruction revalidation blocker

- Revalidation source digest: `sha256:36b24b55587f07a9bb5b635df0fd1e3b1c4df897733e7392644b84ad3c38d9cc`.
- Immutable upstream revision: `a0a39220522ed1228445792c768ed887709aea5f`.
- Source validation completed with exit code `0`.
- Two production compiles completed with `toolchain.node.lock.toml`, Harbor
  `0.21.0`, `--allow-private`, and the parent private artifact store. The full
  compiled trees and bundle manifests were byte-identical. Their compact
  summaries are `compile-a-summary.json` and `compile-b-summary.json`; the
  canonical manifest digest is
  `sha256:e3b35fb75ff36e4bb19e20bb1750deaad31429974898ffe384bbd76043126bd5`.
- The private Oracle bundle is
  `sha256:addcaac3664c5db6ea8d205b2feb5d30e4dff6808dd404025c369a971d9c956e`.
  Payload inspection found only `build.mjs` and `solve.sh`. `solve.sh` runs
  `git fetch` from `github.com` at runtime, then creates the source archive.
  No local source archive is present in the Oracle payload.
- No Oracle, empty, stub, forgery, offline, or timeout Harbor run was started;
  running them would violate the required NoNetwork contract. No fresh
  production evidence was substituted for the historical evidence.

## Remediation

Replace the Oracle payload with a hash-bound local source archive (or otherwise
provide a trusted local source materialization) and a solve script that verifies
the declared revision and archive digest without runtime network access. Then
compile the replacement bundle twice, inspect it again, and run the complete
Oracle/control matrix under NoNetwork. Persist all resulting collection,
grading, network, result, and failed/skipped-set summaries before updating
`production-evidence.json` or lifecycle status.
