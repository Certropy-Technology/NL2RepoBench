# `validate-npm-package-name` authoring provenance

Status: `controls-passed`; review, model Agent Run, integration, and publication
remain parent-loop stages.

## Source and license freeze

- Upstream: `https://github.com/npm/validate-npm-package-name`.
- Frozen revision: `f63469d58278635630681c2506f05176ff18a7cb`
  (`8.0.0`).
- No submodules.
- ISC license in root `LICENSE`.
- Deterministic `git archive --format=tar` SHA-256:
  `9661772a73903963953effd89a95902ce3b5b4b82106c839ed3d6e938f4e8a79`.
- License SHA-256:
  `f3e1645267f7dd77ee6545283cc1766e5883e8fb3b5088fe2cfb995defbb3dde`.

## API and tests

The only runtime export is the callable CommonJS package root. It accepts one
value and returns a deterministic validation object. The two upstream
`node:test` leaves pass under the pinned Node 24 image with networking disabled.
The production verifier freezes 44 leaves and invokes candidate code only in
UID 10001 child processes through the adapter summarized in
`candidate-boundary.json`.

## Environment and closure

- Node `24.19.0`, npm `11.17.0`, Debian bookworm amd64, glibc.
- Pinned image digest:
  `sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- No runtime dependencies. The private npm bundle contains a lockfile v3 and
  an empty, integrity-checked npm cache.
- Candidate and verifier phases are `no-network`; no registry, source, or
  provider hosts are stored in task metadata.

## Oracle boundary

The private Oracle bundle alone contains `solve.sh`. It fetches exactly the
frozen commit, asserts the resolved commit, creates a Git archive, verifies the
archive digest, and adapts only development metadata and the missing lockfile.
The model Agent never receives this bundle or the Oracle source-host override.

## Gate record

The finalized production bundle is compiled with `toolchain.node.lock.toml`
and the task-local private CAS. Harbor `0.21.0` Oracle and the empty, stub,
forgery, install-script, loader-hook, bounded-hang, and offline controls are
recorded under `.nl2repo/evidence/validate-npm-package-name/`. Exact receipts,
hashes, and summaries are bound in `production-evidence.json` after the final
compile and rerun.
