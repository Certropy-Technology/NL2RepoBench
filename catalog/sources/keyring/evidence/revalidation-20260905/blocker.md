# Keyring instruction revalidation blocker

- Task: `keyring`
- Queue source digest: `sha256:930b142979344e3f758403d1caf80fc564f8d86eee4629a618e3b5e0b5b7a83e`
- Instruction digest: `sha256:7f79b6baa320b0c233806d433086e70425768fdf0064b467db73ec3cd4b8d5b3`
- Frozen revision: `7603e7cadc254b4c6e3fc2b2f0916a005e78087d`
- Frozen source archive: 235,520 bytes, `sha256:30dfe6cd4dcf67495e2ff1d8a3196593b5263f8d9180fe2cabc5cdc3582815a9`
- Failure class: `artifact`
- Status: revalidation blocked; the existing `task.toml` lifecycle and historical `production-evidence.json` are preserved unchanged.

## Artifact validation

The dependency lock (`sha256:724d58a9...`) and verifier bundle
(`sha256:385ca65e...`) were found in the parent private CAS and matched their
declared sizes and SHA-256 values. The Oracle bundle
(`sha256:26a926da...`) also matched its declared size and SHA-256, but its only
source material is a `solve.sh` that performs a runtime `git fetch` from
`github.com`. It contains no `source.tar` or other installable source payload.
The complete inventory and hash checks are recorded in
`evidence/revalidation-20260905/artifact-check.json`.

## Local recovery

Recovery checked the generated `catalog/tasks/keyring` runtime, source-local
evidence, the historical authoring path recorded by the keyring session,
bounded archived authoring records, worker handoffs/worktree diffs, preserved
worktree, local caches, and 351 local Git object repositories. No exact archive matching
the frozen revision, size, and digest was found. The historical authoring work
directory has been removed, so its prior direct-verifier receipt is not durable
source payload evidence. Search results are recorded in
`evidence/revalidation-20260905/local-recovery-search.json`.

## Why compilation and Harbor were not run

Running the current Oracle would require source-host access, which violates the
task's declared `no-network` policy and the instruction-revalidation contract.
Compilation and Harbor execution were therefore not attempted after the
artifact blocker was confirmed. No replacement bundle is proposed because no
hash-verifiable local payload exists.

## Next step

Parent integration must provide or restore an immutable local source archive
matching the frozen revision and `sha256:30dfe6cd...` digest, register a
replacement Oracle bundle in the parent CAS, regenerate the runtime projection,
and rerun Oracle plus the complete supported control matrix under no-network.
Until then, prior receipts must not be treated as current revalidation evidence.
