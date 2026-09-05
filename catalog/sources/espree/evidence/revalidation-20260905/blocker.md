# Espree instruction-migration revalidation blocker

- Task: `espree`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:44b5f6b7eda793b8eb4a76ebe80d6cff1095317af40d61b308082f82b4c0e41a`
- Frozen upstream revision: `8173ecfeb7473bff90d1da11b1347082f47e262e`
- Frozen upstream archive digest: `sha256:bc2f79fda450ef344b0696f374d492f95fee28b74254abbc1584440fd9739ac4`
- Current instruction bytes: `sha256:d777730f89820568b4c6090958d14c6f75cc2dfb7f96249fc7a41c43cb52982b`
- Lifecycle: unchanged at `controls-passed`; this is not a lifecycle transition.
- Historical `production-evidence.json`: unchanged because its receipt paths point to an old authoring worktree and its instruction digest is stale.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/espree` passed and reported the expected current catalog source digest. Harbor `0.21.0`, Node `24.19.0`, npm `11.17.0`, and `toolchain.node.lock.toml` were used. All four declared private CAS artifacts were present with matching size and SHA-256 values; see `artifact-check.json`.

`uv run python scripts/validate_instruction_quality.py` passed. `uv run nl2repo task lint-network --tasks-root catalog/sources` reported zero errors and zero espree findings.

## Deterministic production compiles

Both commands used the current source, the locked Node toolchain, the private artifact root, `--allow-private`, and no runtime network authorization:

```text
uv run nl2repo harbor compile catalog/sources/espree --output .nl2repo/revalidate-espree-20260905-compile-a --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
uv run nl2repo harbor compile catalog/sources/espree --output .nl2repo/revalidate-espree-20260905-compile-b --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
diff -rq .nl2repo/revalidate-espree-20260905-compile-a/espree .nl2repo/revalidate-espree-20260905-compile-b/espree
```

Both compiles exited `0`; the 102-file trees were byte-identical. Both manifests have SHA-256 `sha256:3163ec40c61b95578fa65c9b2394919ae5cd50c757f5fe7717380cc70baef42e` and canonical manifest digest `sha256:101826bb580f2c1b755a69bc3aa129eae8fec1e065eac9f68ca8e685e98acb32`. The compact records are `compile-a-summary.json` and `compile-b-summary.json`.

## NoNetwork blocker

The hash-bound Oracle artifact is present and valid, but its only member, `solve.sh`, initializes a Git repository and executes `git fetch --depth=1 origin <revision>` against `github.com` at runtime before checking the archive digest and materializing `/workspace`; see `oracle-bundle-inspection.json`.

This violates the revalidation NoNetwork contract. Harbor Oracle and all controls were not run, no host authorization was granted, and no Oracle, grading, network, collection, result, or failure-set receipt is claimed. The blocker is an artifact/verifier runtime-source-fetch issue, not evidence that espree is unsupported.

## Remediation

Register a replacement private Oracle bundle containing a local, revision- and archive-digest-verified payload, or replace the materializer with a source-local immutable payload. Recompile twice against that replacement and run the complete Harbor `0.21.0` Oracle, empty, stub, forgery, and offline matrix with no external network authorization. Persist every receipt under this evidence directory before replacing production evidence. Do not authorize `github.com`, reuse stale receipts, change the frozen denominator, or alter lifecycle state solely because of this blocker.
