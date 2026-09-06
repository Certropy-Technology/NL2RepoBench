# Instruction Revalidation Blocker

- Task: `json-parse-even-better-errors`
- Expected current source digest from the revalidation queue: `sha256:fc6aceb4c59ec801b501148dcc74382e64e94f688c6a6a4dcf7e4cc914746d2c`
- Frozen revision: `098b8d00e72e4807adba733c2cdde686b2b9bf82`
- Frozen source archive: `112640` bytes, `sha256:6bcf80e775ad5481a30fc401ede155fc49ebc44ae03a2f76f323430ce28c5f9f`
- Failure class: `artifact/verifier`
- Revalidation status: `blocked`

## Findings

The four declared private artifacts were checked against the parent CAS. Dependency,
commands, test, and Oracle bundle bytes all matched their declared sizes and SHA-256
digests. The Oracle bundle is only a 737-byte `solve.sh`; it contains no frozen source
archive and fetches `https://github.com/npm/json-parse-even-better-errors.git` at runtime.
That behavior cannot run under the required NoNetwork policy.

The bounded local recovery search checked the generated task projection, tracked Git
objects, task-local evidence, the retained authoring session, retained local worktrees
and handoffs, retained `.tar.zst` state archives, and local CAS. No exact 112640-byte
archive matching the declared source digest was found. The detailed command log and
results are in `evidence/revalidation-20260905/local-recovery-search.json`.

## Commands and Results

1. `uv run nl2repo task validate-source catalog/sources/json-parse-even-better-errors`: exit `0`; queue source digest matched.
2. Offline CAS size/SHA checks for all four declared artifacts: exit `0`; all four matched.
3. Oracle bundle inventory: exit `0`; only `solve.sh`, with runtime GitHub fetch.
4. Bounded local source-payload search: exit `0` for completed searches; no exact frozen archive found.
5. `git rev-list --objects --all` exact archive search: exit `0`; no matching tracked payload.

## Remediation

Provide a trusted local archive for revision `098b8d00e72e4807adba733c2cdde686b2b9bf82`
with size `112640` and SHA-256
`sha256:6bcf80e775ad5481a30fc401ede155fc49ebc44ae03a2f76f323430ce28c5f9f`. The parent
must register it in private CAS, replace the runtime-fetching Oracle bundle, perform two
deterministic production compiles, and rerun Oracle plus empty/stub/forgery/offline
controls against the new final manifest. Existing production evidence and lifecycle
status are intentionally unchanged; no new Oracle or control receipt was asserted here.
