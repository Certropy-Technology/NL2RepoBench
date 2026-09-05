# Figures instruction-migration revalidation blocker

- Task: `figures`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:c0893a6cfd5482159f6f576df9f3f0250d18132c799ce75c40c8dc8a91435dad`
- Frozen upstream revision: `3da3d1713e9a09dbfcfc99eac86af8f4377597b6`
- Frozen upstream archive digest: `sha256:c1b1db9dd7ff5771b6301e85ade19184e7bf46990b95008240729c39287b3258`
- Lifecycle and historical `production-evidence.json`: unchanged.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/figures` exited `0` and
reported the expected catalog digest. The four declared private artifacts were
present in the parent CAS and matched their declared sizes and SHA-256 values;
details are in `artifact-closure-summary.json`.

The current source was compiled twice with Harbor `0.21.0`,
`toolchain.node.lock.toml`, the parent private CAS, and `--allow-private`.
Both compiles exited `0`, produced 86 manifest files, and were byte-identical.
Both raw manifests have SHA-256
`sha256:4ec7e2e9d3ad5ab6297438c484248f9f643d5a1a61ab2c2ab6a2d8a6341e60bb` and
canonical digest
`sha256:84a91c6da5290bd1958a6edc820894ac900c14c0059a11d0db3b336dccf1c809`.

## NoNetwork blocker

The hash-valid Oracle artifact is
`sha256:c9fb351b1c4c85e576f4acae322aa7b66f5db1a3f33a6aa39f116ed8168f3ee4`.
Its `solve.sh` has SHA-256
`sha256:77ca3a4e1bf9a194397f9403d86471b8ae6a77ab0297138b45596b04ef9aaa0f`
and executes `git fetch` from `https://github.com/sindresorhus/figures` before
checking out the pinned revision and archive digest. This violates the required
NoNetwork contract. No Harbor Oracle or control run was started, no host was
authorized, and no grading, network, collection, result, or failure receipt is
claimed. The explicit not-run summaries are tracked beside this file.

## Remediation

Register a replacement private Oracle bundle containing a local source payload
verified against the frozen revision and archive digest, or provide an equivalent
source-local immutable payload. Recompile twice, inspect the replacement for
runtime network access, and then run the complete Oracle, empty, stub, forgery,
and offline matrix under NoNetwork. Persist all fresh receipts under this
evidence directory before updating production evidence or lifecycle.
