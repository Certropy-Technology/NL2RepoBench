# cross-fetch instruction revalidation blocker

## Source and compile checks

- Expected migrated catalog source digest: `sha256:3ff447ee9e5d7fedecafc2cffc947015bd20823bcfa2065329ff7e5cfd941b10`.
- `uv run nl2repo task validate-source catalog/sources/cross-fetch` passed and reported that exact digest.
- `uv run python scripts/validate_instruction_quality.py` passed.
- `uv run nl2repo task lint-network --tasks-root catalog/sources` passed with zero
  `cross-fetch` findings and zero error findings.
- Two production compiles used Harbor `0.21.0`, `toolchain.node.lock.toml`, the
  parent CAS exposed as `.nl2repo/artifacts`, and
  `--allow-private`. Both produced 118 files, canonical manifest
  `sha256:9143c392410ccfe34a058898597a08c1256b0856c953ebb4b69f02083bed4934`,
  and identical manifest-file SHA-256
  `sha256:3efad7a7e324cac8273466a6c62944593bf0d7270a878c4d4893d7ca1f01343d`.
- The complete compile trees passed `diff -rq` byte identity.

## Blocker

All four declared CAS artifacts are present and digest/size verified. The Oracle
artifact is not runnable under the required NoNetwork contract. Its `solve.sh`
executes `git clone` and `git fetch` against `github.com` at runtime before
materializing `/workspace`. This is a revalidation artifact/verifier blocker,
not a claim that the package is unsupported. No Oracle, empty, stub, forgery, or
offline Harbor run was started, and no host authorization was granted.

The historical `production-evidence.json` remains unchanged because its receipt
paths point into ignored run trees and its old Oracle command authorizes
`github.com`; those receipts cannot be reused for this migrated instruction.
The current compiled bundle and inspection data are summarized in the adjacent
tracked JSON files. No new Harbor run ID or raw receipt hash exists for this
blocked attempt.

## Remediation

Replace the Oracle materializer with a locally supplied, hash-bound source archive
for revision `9e6898ee848ba6dc942f787f2c35ca6fa30eb014`, and verify archive digest
`sha256:2924f22280494620dfee8fd974a0a85f6668334b16eed7b540b7fe4d24706491`
before copying into `/workspace`. Then compile the changed source again and run
the complete Oracle, empty, stub, forgery, and offline matrix with no external
network authorization. Persist all resulting collection, grading, network,
result, and failure-set receipts under this directory before updating production
evidence.
