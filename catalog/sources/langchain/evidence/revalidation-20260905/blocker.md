# LangChain instruction-migration revalidation blocker

## Frozen input

- Queue catalog source digest: `sha256:2999c73cc3d7692b6d8d3c5608f2a15e36debfeb96b43d21e5fd14a74e3a0754`.
- Current source validation returned the same digest before changes.
- Instruction SHA-256: `sha256:bce85e577907bf4096406de77bd7c8493c23254952c38092bb91b96246c858f4`.
- Upstream revision: `502b2b445b89b753cd468df979b71503f8f99425`.
- Frozen subtree git-archive: 3,010,560 bytes, `sha256:324411670c256bcbdf4dfab75a1b099910b6fc8880a4e9722270288c5a1e4ccd`.

## Blocking finding

All three declared private artifacts exist in the parent CAS and match their declared sizes and SHA-256 values. The verifier bundle is a UID-separated custom JSON verifier with 88 fixed leaves, and its Python files compile successfully. The Oracle artifact, however, contains only a 908-byte `solve.sh`. That script initializes a Git repository and fetches the frozen revision from `github.com` at runtime. It has no embedded source archive or installable source tree.

This revalidation forbids source-host, registry, DNS, and all external-service access for Oracle as well as Agent, candidate, verifier, and controls. Therefore the current Oracle cannot be run, and the instruction-migrated manifest cannot receive fresh Oracle/control receipts. Historical receipts use the pre-migration instruction and ignored run paths and are not reusable.

## Local recovery performed

The bounded recovery searched the checked-in generated runtime, task evidence, the parent CAS, retained worker handoffs/transcripts, authoring archive receipts, local Docker containers/images/volumes/build-cache labels, and task-indexed local cache paths. No file matched the declared 3,010,560-byte source archive and SHA-256. The original authoring worktree no longer exists.

The local archive receipt proves that the prior Oracle produced a 159-file, 2,869,937-byte workspace and records every file SHA-256, but those object bytes are stored in external OSS. They were not fetched because this task explicitly forbids external-service authorization and network access. Receipt metadata alone is insufficient to reconstruct or independently verify the missing bytes.

Two initial broad, unindexed filesystem probes reached their bounded timeout. Indexed follow-up searches completed and are recorded in `local-recovery-search.json`; the timeouts did not hide a known candidate path.

## Outcome and remediation

- Revalidation classification: `artifact-or-verifier-blocked` (Oracle payload unavailable locally).
- No compile or Harbor run was started after identifying the unresolved Oracle payload.
- No replacement bundle was constructed because exact source bytes were not available.
- Existing lifecycle and `production-evidence.json` are preserved unchanged; they describe the historical pre-migration matrix and are stale for the migrated instruction.
- Parent remediation: import the exact frozen git archive, or the complete SHA-bound 159-file archived Oracle workspace, through an approved offline/local process. Construct and register a private Oracle bundle whose solution copies the embedded payload with no network operations; update the source binding, compile twice, and rerun Oracle plus empty, stub, forgery, offline, and other supported controls.

Supporting machine-readable records:

- `catalog/sources/langchain/evidence/revalidation-20260905/artifact-check.json`
- `catalog/sources/langchain/evidence/revalidation-20260905/oracle-inspection.json`
- `catalog/sources/langchain/evidence/revalidation-20260905/local-recovery-search.json`
