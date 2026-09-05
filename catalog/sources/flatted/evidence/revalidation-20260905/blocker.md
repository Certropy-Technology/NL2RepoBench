# flatted instruction-migration revalidation blocker

- Task: `flatted`
- Revalidation date: `2026-09-05`
- Expected catalog source digest: `sha256:6a8082a284bdcd8f4d7aa6bc12136f2483c3599ec0b62bf4b9c35de85537dcf6` (validated by `validate-source`)
- Lifecycle: unchanged at `controls-passed`; historical `production-evidence.json` is unchanged.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/flatted` passed with the expected source digest. The four declared private artifacts were present in the parent CAS and their sizes and SHA-256 values matched `task.toml`. Harbor `0.21.0`, Node `24.19.0`, npm `11.17.0`, and `toolchain.node.lock.toml` were used. All seven source controls passed shell syntax checks.

## Deterministic production compiles

Both production compiles exited `0` with `--allow-private`, the locked Node toolchain, and the parent CAS. The 75-entry bundles were byte-identical. Both manifests have raw SHA-256 `sha256:725e9dc5e0fc0d576d3900cc156bfa9e33cf095404d9aace0081cbba18487196` and canonical digest `sha256:0bb703a96a60bf65b4facde732b2340bd1fcd0e8aff5026e95fc8a1c423619ef`.

## NoNetwork blocker

The pinned Oracle artifact is present and internally contains only `solve.sh`. Its SHA-256 is recorded in `oracle-bundle-inspection.json`. The script invokes `git clone` and `git fetch` against `https://github.com/WebReflection/flatted` at runtime before verifying the pinned revision and source archive digest. This violates the revalidation NoNetwork contract. No GitHub authorization was granted. Oracle, empty, stub, forgery, install-script, loader-hook, hang, and offline Harbor runs were therefore not executed.

## Remediation

Register a replacement private Oracle bundle containing a local, revision- and archive-digest-verified payload, or replace the Oracle script with a source-local immutable payload. Recompile twice against that replacement and run the complete Harbor Oracle/control matrix, persisting repository-relative receipts and hashes before updating `production-evidence.json`. Do not grant GitHub access, reuse historical receipts, change the frozen denominator, or change lifecycle solely because of this infrastructure/verifier blocker.
