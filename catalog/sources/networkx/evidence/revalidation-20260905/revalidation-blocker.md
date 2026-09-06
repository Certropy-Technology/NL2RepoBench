# NetworkX instruction revalidation blocker

- Task: `networkx` version `3.7.0`
- Queue source digest: `sha256:28dfa59d67930a9ed79a5cca3b69d240bd23c281a659bc8a7b6631be50aafea6`
- Frozen revision: `ff25fa8296d16ad63d6a02b2d9f979dcafbb50ae`
- Frozen source archive digest: `sha256:438319b0534eede5966d6aa88dd6bcea3e0fddb3164040fe982ef5d96580737c`
- Classification: `artifact/verifier` revalidation blocker; lifecycle and historical
  production evidence are unchanged.

`uv run nl2repo task validate-source catalog/sources/networkx` passed before this
evidence was written and reported the queue source digest. Bounded offline checks
found all three declared CAS objects (dependency lock, verifier bundle, and Oracle
bundle) with matching sizes and SHA-256 values; see `artifact-check.json`.

The exact generated Oracle bundle was inspected without execution. It contains only
`solve.sh` and no source archive. The script performs `git clone` and `git fetch` from
`github.com` before creating and checking the archive, which violates this task's
required NoNetwork contract. The payload details and normalized commands are in
`oracle-payload.json`. No Oracle, control, compile, or receipt result is claimed, and
no host authorization was used. Existing receipts were not reused.

## Remediation

Recover or register an exact source payload whose bytes match the frozen revision and
archive digest, then construct a NoNetwork Oracle bundle in parent-owned CAS. The
parent must compile twice with the locked toolchain and rerun a fresh Oracle plus all
supported controls against the new manifest. Do not alter the denominator, lifecycle,
generated projection, or historical production evidence solely for this blocker.
