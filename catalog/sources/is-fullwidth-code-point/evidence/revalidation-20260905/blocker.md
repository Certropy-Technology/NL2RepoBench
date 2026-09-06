# is-fullwidth-code-point instruction revalidation blocker

- Task: `is-fullwidth-code-point` version `2.0.0`
- Queue source digest: `sha256:257dd9f165bb2faa80c6fda8a4b925db0cde977ad53f2bf9048cb7b3bbf7e179`
- Frozen upstream revision: `2696d873463fde9f6b09b49c98380bd49c67b00a`
- Frozen source archive digest: `sha256:fdc4bd52b082a3ac5654f92c8b6b1d50d4c105cb48b65930e2e40a7673a7fdd0`
- Failure class: `artifact`
- Status: revalidation blocked before Oracle and controls; existing lifecycle and production evidence preserved.

## Verified artifacts

All four declared private artifacts were found in the parent CAS and matched their declared size and SHA-256. The exact records are in `artifact-check.json`. The Oracle bundle inventory is only `solve.sh`; it does not contain `source.tar`, `oracle-package/`, or another installable payload. Its script performs a GitHub fetch for the frozen revision, which is forbidden for this NoNetwork revalidation.

## Local recovery

The required bounded local search checked task-local source/evidence and generated runtime, retained authoring handoffs/worktrees/runs/session logs, repository objects, and local caches. It searched by the exact source archive digest and immutable revision. No matching source archive or payload was found, and no replacement bundle was constructed. Details are in `local-recovery-search.json`.

## Safe compile

Two offline production compiles completed with `--allow-private`, `toolchain.node.lock.toml`, and the parent CAS. Both produced byte-identical 84-file bundles with canonical manifest digest `sha256:649a39e06c9f9c28cee1b4257380974fa2cb7b1424aec51f2bcacf0eeffa458e` and raw manifest SHA-256 `sha256:dc8943d2be7ba34c349569ba0150efb954846cbe7fe548a8635728d5607fd74e`. The compact records are `compile-a-summary.json` and `compile-b-summary.json`.

## Commands and results

```text
uv run nl2repo task validate-source catalog/sources/is-fullwidth-code-point
exit 0; queue and validated source digest matched sha256:257dd9f165bb2faa80c6fda8a4b925db0cde977ad53f2bf9048cb7b3bbf7e179

uv run nl2repo harbor compile catalog/sources/is-fullwidth-code-point --output .nl2repo/revalidation-is-fullwidth-code-point-a --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
exit 0; 84 files; canonical manifest sha256:649a39e06c9f9c28cee1b4257380974fa2cb7b1424aec51f2bcacf0eeffa458e

uv run nl2repo harbor compile catalog/sources/is-fullwidth-code-point --output .nl2repo/revalidation-is-fullwidth-code-point-b --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
exit 0; byte-identical to compile A
```

No Harbor Oracle or control command was run because the only Oracle source acquisition path requires forbidden network access and no exact local replacement exists. No host authorization, registry access, DNS, Docker cleanup, or generated projection change was performed.

## Next step

The parent integrator must recover an exact source payload matching the frozen archive digest and revision, register it in the shared CAS, then rerun double compile and the complete current-manifest Oracle/control matrix under NoNetwork. Do not reuse the prior GitHub-authorized receipts or replace `production-evidence.json` until fresh durable receipts exist.
