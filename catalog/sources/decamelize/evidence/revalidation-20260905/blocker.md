# Decamelize instruction-migration revalidation blocker

- Task: `decamelize`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:e63d8c7bb62c0c1c557042507d1dcd9512e34df4be99824470f2a2ebd795c77b`
- Frozen upstream archive digest: `sha256:4bc589382527a52de984f5768d6eece961d0a532439d894cdd4e2aef7a82696e`
- Lifecycle: unchanged at `controls-passed`; this is not a lifecycle transition.
- Historical `production-evidence.json`: unchanged because its receipt paths point to an old non-durable authoring run tree.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/decamelize` passed and reported the expected current catalog source digest. Harbor `0.21.0` and the locked Node/npm toolchain were inspected. The dependency, command, test, and Oracle private artifacts were found in the parent CAS with their declared sizes and SHA-256 values. All eight task-local control scripts were inspected.

## Deterministic production compiles

Both commands used the current source, `toolchain.node.lock.toml`, the private CAS, `--allow-private`, and no runtime network authorization:

```text
uv run nl2repo harbor compile catalog/sources/decamelize --output .nl2repo/decamelize-revalidation-compile-a --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
uv run nl2repo harbor compile catalog/sources/decamelize --output .nl2repo/decamelize-revalidation-compile-b --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
diff -rq .nl2repo/decamelize-revalidation-compile-a/decamelize .nl2repo/decamelize-revalidation-compile-b/decamelize
```

Both compiles exited `0`; `diff -rq` reported no differences. The generated bundle contains 76 files, has manifest SHA-256 `sha256:83ad1a8a7acbc055341bedd8749315b69b79f9650dc1274a165edac673a0da34`, and has canonical manifest digest `sha256:705cb32e1057ae20d21e34678f4e38d29f5875b10e61a6248f6c5e006d78ec86`.

## NoNetwork blocker

The hash-bound Oracle artifact is `sha256:bbd4f73308982c546ed72715ba772bdb5ef08d8686060c65b60b3e662c0d365b`. Its only member is `solve.sh`, whose SHA-256 is `sha256:ed45fb5fbe20b2eb0f058e3763fc2aae30f2dcf6d9c30e0cf5587f6fa3d8fda3`. The script executes `curl` against `codeload.github.com` to fetch revision `365e2e909c93c8a5e7c9398523290ba0b35a3a93` at runtime before checking the archive digest and creating `/workspace`.

This violates the revalidation NoNetwork contract. Harbor Oracle and all controls were not run; no Oracle, grading, network, collection, result, or failure receipt is claimed. No external host authorization was granted.

## Remediation

Register a replacement private Oracle bundle containing a local, revision- and archive-digest-verified payload, or replace `solve.sh` with a source-local immutable payload. Recompile twice against the replacement and run the complete Harbor `0.21.0` Oracle, empty, stub, forgery, and offline matrix. Persist every receipt under this evidence directory before replacing production evidence. Do not grant `codeload.github.com`, reuse stale receipts, change the frozen denominator, or alter lifecycle state solely due to this infrastructure/verifier blocker.
