# `openai` instruction revalidation blocker

This is a revalidation blocker after the instruction migration. The existing
`task.toml`, lifecycle, generated projection, and historical
`production-evidence.json` are intentionally unchanged.

## Frozen input

- Queue source digest: `sha256:d51d1fbb6f05f0c35b5a46eb0b25c7d6532c9693f799bc1bf75003f350d1e451`
- Validated source digest: `sha256:d51d1fbb6f05f0c35b5a46eb0b25c7d6532c9693f799bc1bf75003f350d1e451`
- Frozen upstream revision: `555ac487f450f24928d859478ea2f41b58906206`
- Frozen source archive: `sha256:3fee3c1832ceafd565161d3a0c42555823c7bdb7ca20dc2f217e8f7437365720` (`14653440` bytes)
- Network policy: `no-network`; no source-host, registry, DNS, or external-service authorization was used.

## Artifact and Oracle assessment

`uv run nl2repo task validate-source catalog/sources/openai` exited `0` before
any mutation. The dependency-lock, verifier, and Oracle outer bundles were
each present in the parent private CAS and matched their declared sizes and
SHA-256 values. The Oracle tar contains only `solve.sh`; it has no
`source.tar`, `oracle-package/`, or other installable source payload.

The script performs a runtime `git fetch` from
`https://github.com/openai/openai-python` for the frozen revision. That source
fetch is forbidden for this revalidation, so no compile or Harbor execution
was started. Detailed artifact and script inventories are in
`artifact-check.json` and `oracle-inspection.json`.

## Local recovery

The bounded search checked the generated `openai` projection, all task-local
source/evidence, parent private CAS, retained authoring state and logs, local
Git object stores, and available package/archive caches. The installed package
tree found in an authoring environment is newer and has no frozen-commit proof;
it is not accepted as a replacement for the declared Git archive. The frozen
commit is absent from the checked local repositories. A broad historical
filesystem candidate scan exceeded its bound and is explicitly not treated as
proof of absence. No replacement bundle was constructed.

See `local-recovery-search.json` for the exact search scopes and outcomes.
The commands run for this revalidation, including the two repository-wide
pre-existing wrapper failures, are recorded in `validation-summary.json`.

## Decision and unblock action

Failure class: `artifact-or-verifier`.

This worker does not claim current Oracle, controls, compile, or receipt
results. Historical production evidence remains visible but stale after the
instruction migration; it was not rewritten into a fabricated success or
terminal blocked lifecycle state.

Recover the exact archive matching the frozen revision and SHA-256, then have
the parent register an offline Oracle bundle, compile twice with the locked
toolchain, and rerun the current-manifest Oracle plus empty, stub, forgery,
and offline/no-egress controls. Do not authorize GitHub, package registries,
DNS, or external services to bypass this blocker.
