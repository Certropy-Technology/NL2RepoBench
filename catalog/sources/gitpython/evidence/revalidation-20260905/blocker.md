# GitPython instruction revalidation blocker

- Revalidation date: 2026-09-05.
- Current catalog source digest: `sha256:b4a4979c5e53fa9603ed95ccd4689b33c5bfe032f02bac97b65751144916e253`.
- Frozen upstream archive digest: `sha256:8d6e3300bf477e7276e3a7280abf0bcb84c0f6b63ce05caa1ca70bfa4e50e8d8`.
- Source validation and instruction quality passed.
- The three declared private CAS artifacts are present and hash/size verified; see `artifact-check.json`.
- Two fresh Harbor 0.21.0 production compiles completed with `--allow-private` and no `--allow-incomplete`. Both contain 59 files and are byte-identical; see `compile-a-summary.json` and `compile-b-summary.json`.

## NoNetwork blocker

The hash-bound Oracle bundle contains only `solve.sh`. It executes `git clone` and
`git fetch` against the frozen GitHub repository at runtime before creating the
source archive. This violates the required NoNetwork contract for Oracle and
controls. No Oracle, empty, stub, forgery, or offline Harbor run was started, and
no reward, collection, or fresh production receipt is claimed.

The existing `production-evidence.json`, lifecycle status, denominator, and
generated projection were left unchanged because their historical receipts are
not current revalidation evidence.

## Remediation

Register a replacement Oracle payload containing a local, revision- and
archive-digest-verified source materialization, or otherwise remove runtime
network fetching while preserving the frozen source digest. Recompile twice,
inspect the replacement payload, and run the complete Harbor 0.21.0 Oracle,
empty, stub, forgery, and offline matrix under NoNetwork. Persist all
collection, grading, network, result, and failure-set summaries before updating
production evidence or lifecycle status.
