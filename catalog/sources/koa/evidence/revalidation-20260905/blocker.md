# Koa instruction revalidation blocker (2026-09-05)

The queue requires current source digest
`sha256:64012f706a24ff01cc8c11126c74ece05ab4c41473ac25e27fc9c34739958538`
and `validate-source` confirmed that digest before any source edit. The frozen
upstream archive digest is
`sha256:069a16c6ea48c4d9e9f34fa31746c238c081fbce1f67cc99c85b75057faf5245`
at revision `9c202e0077f4e314795222aff1be0da0bf9b2493`.

All four declared private artifacts were verified offline by exact byte size and
SHA-256. The Oracle artifact is not an offline Oracle payload: its top level only
contains an npm cache, `runtime-package-lock.json`, and `solve.sh`; no
`source.tar` is present. Its `solve.sh` performs a GitHub `git fetch` before
creating the source archive. The local-recovery search covered the current
generated runtime/evidence, parent CAS, retained runs, historical handoffs,
authoring archives, retained worktrees, and local caches. No exact frozen source
archive or hash-verifiable replacement was found.

The source compiled successfully twice with the locked Node toolchain and parent
CAS. Both manifests are byte-identical with file SHA-256
`sha256:b363f9244383f1e27c49e89c7a9af7048ba9aa415dd5c3e5c5099eaf012f54b9`,
canonical digest
`sha256:340f983c3e6e4fa46a2e4494f7dfc10edb7e69ef20fd6a704a95cc839ee6fdc3`,
and 478 files. No Harbor Oracle or controls were run because the only Oracle
source path would violate the mandatory NoNetwork policy. No Oracle/control
receipt was inferred or replaced.

This is an artifact/verifier blocker, not a model, source, or infrastructure
failure. Existing `task.toml` lifecycle and `production-evidence.json` were
preserved unchanged. Parent must register a source-digest-verified offline
Oracle bundle, recompile, then run the full Oracle/empty/stub/forgery/offline
matrix before replacing production evidence.

Tracked evidence:

- `artifact-check.json` — exact CAS checks and Oracle payload inspection.
- `local-recovery-search.json` — bounded local recovery results.
- `compile-a.log`, `compile-b.log`, `compile-diff.log` — deterministic compile evidence.
