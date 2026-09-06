# msgspec instruction revalidation blocker

## Classification

- Task: `msgspec`
- Queue source digest: `sha256:a99baa922e8842fce5f95798b228271f9089bd3e6526b616e2239dd8161ee1bb`
- Validated source digest: `sha256:a99baa922e8842fce5f95798b228271f9089bd3e6526b616e2239dd8161ee1bb`
- Frozen upstream revision: `f51f378335b01dc0026dc6553a0b9e1915a8edae`
- Frozen source archive: `sha256:0583e9ecf3d8f3f233722ba02361894e01f4bdc470e8fbe74d797ae758004390`
- Failure class: `artifact/verifier`
- Existing lifecycle and `production-evidence.json` are unchanged (`packaged` / `awaiting-agent-run`).

## Checks completed

`uv run nl2repo task validate-source catalog/sources/msgspec` passed before any
mutation. All three declared private artifacts were independently checked by
exact size and SHA-256. The current generated projection was inspected and
contains no source archive payload. Detailed values are in
`artifact-check.json`.

## Blocker

The only Oracle payload is `solve.sh`. It performs a runtime Git fetch from
`https://github.com/jcrist/msgspec` before creating the frozen source archive.
This is forbidden by the current `no-network` policy for Oracle and controls.
The complete bundle inventory and inspection are in `oracle-inspection.json`.

## Local recovery

The worker checked the current generated projection, parent CAS, task-local
evidence, retained authoring state, and bounded local archive/cache locations.
No exact source archive or immutable local Git object proving the frozen
revision and archive digest was recovered. No replacement bundle is proposed;
repacking the visible projection would not prove the required private artifact
bytes. Search details and the next unblock action are in
`local-recovery-search.json`.

## Required remediation

Recover the exact frozen source archive from a trusted local payload, or
construct a replacement only after independently proving its inner revision,
archive digest, and outer bundle hash. The parent must then register the
offline Oracle bundle, compile twice with `--allow-private` and the locked
toolchain, and run fresh Oracle, empty, stub, forgery, and offline/no-egress
controls. No Harbor receipt, reward, projection refresh, or lifecycle advance
is claimed by this revalidation.
