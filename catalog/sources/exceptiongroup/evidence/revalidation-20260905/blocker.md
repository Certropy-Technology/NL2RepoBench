# Exceptiongroup instruction-migration revalidation blocker

- Task: `exceptiongroup`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:baf3f4d9843f069f76da6a4a8185bf1abb3faad67dfd1a079f14d4d1f2038be4`
- Frozen upstream archive digest: `sha256:70913d01619162478935e3cf3a56721e85375e4f535928aa59f1273e7572e3bd`
- Lifecycle: unchanged at `controls-passed`; this is not a lifecycle transition.
- Historical `production-evidence.json`: unchanged because its receipt paths point to an old non-durable authoring run tree.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/exceptiongroup` passed and
reported the expected current catalog source digest. Harbor `0.21.0` and the
locked Python toolchain were inspected. The private lock, verifier, and Oracle
artifacts were present with their declared sizes and SHA-256 values. All four
task-local controls were inspected and passed shell syntax checks.

## Deterministic production compiles

Both compiles used the current source, `toolchain.lock.toml`, the private CAS,
`--allow-private`, and no runtime network authorization. The outputs were byte
identical. Both generated manifests have file SHA-256
`sha256:4ac184b5934352e0763fd4e840ea4c1e249777a60f1abe98adde8af3bf443d0f`
and canonical manifest digest
`sha256:3557f36b597a8f4881bb956f556b6566666cf6d04796fbb9867c4df778ef352f`.

## NoNetwork blocker

The hash-bound Oracle artifact is
`artifact://private/sha256:beb286855eb8bdb41c23cb1303920f856b6d6448660a2d9aad5463ac48025779`.
Its only member is `solve.sh`, which executes `git clone` against
`https://github.com/agronholm/exceptiongroup` at runtime before checking out
revision `0c6cfbf677f6b50df17311cfdad01e9ff17310aa` and checking the source
archive digest. This violates the revalidation NoNetwork contract.

Harbor Oracle and all controls were not run; no Oracle, grading, network,
collection, result, or failure receipt is claimed. No external host
authorization was granted. The explicit not-run summaries are in this
directory, and `oracle-inspection.json` records the payload and script hash.

## Remediation

Register a replacement private Oracle bundle containing a local,
revision- and archive-digest-verified payload, or replace `solve.sh` with a
source-local immutable payload. Recompile twice against the replacement and
run the complete Harbor `0.21.0` Oracle, empty, stub, forgery, and offline
matrix. Persist every receipt under this evidence directory before replacing
production evidence. Do not grant GitHub authorization, reuse stale receipts,
change the frozen denominator, or alter lifecycle state solely due to this
infrastructure/verifier blocker.
