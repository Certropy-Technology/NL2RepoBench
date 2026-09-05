# `editables` instruction revalidation blocker

- Revalidation date: 2026-09-05
- Expected current catalog source digest: `sha256:27b73d301a347e2aff0cafa08e9124bb8091773293f7c54ca0d89dab4a63c232`
- Source validation: passed with `uv run nl2repo task validate-source catalog/sources/editables`.
- Prior lifecycle: `controls-passed`; lifecycle changed: no.
- Historical `production-evidence.json` changed: no.

## Compile evidence

The current source was compiled twice with Harbor `0.21.0`,
`toolchain.lock.toml`, the parent private CAS, and `--allow-private`. Both
commands exited `0`; `diff -rq` reported byte-identical output trees. The
compact receipts are:

- `compile-a-summary.json`
- `compile-b-summary.json`

Both outputs contain 57 files, bundle-manifest SHA-256
`sha256:3e70d585851d33dc1e1aa5118771608b36c5c138d91a4e1f7e30651667dfee0a`,
and canonical manifest digest
`sha256:c95504502c58e52b7b6844401e7666b9a35a0cf1e1ad374987b80e8139a0ed9d`.

## Blocker

The hash-verified private Oracle bundle is recorded in
`oracle-bundle-summary.json`. Its `solve.sh` performs a runtime `git fetch`
from the upstream GitHub repository before copying the frozen source into
`/workspace`. Agent, candidate, verifier, Oracle, and controls must remain
NoNetwork for this revalidation, so no Oracle or control run was authorized.

The source also has no standalone task-local `empty` or `offline` control
script. Existing `stub.sh` and `forgery.sh` are source assets, but they cannot
produce a complete changed-bundle matrix without the missing controls and a
new Oracle run.

This is an artifact/verifier revalidation blocker, not evidence that the task
is unsupported. The existing lifecycle and historical production evidence are
preserved.

## Remediation

Provide a private Oracle payload containing the exact frozen source locally,
with revision and archive digest verification but no runtime source fetch.
Add standalone NoNetwork `empty` and `offline` control assets, compile the
new source twice, inspect the replacement Oracle before execution, and run a
fresh Oracle, empty, stub, forgery, and offline matrix. Persist all grading,
network, collection/result, failure-set, and manifest summaries under this
directory before updating `production-evidence.json`.
