# es-to-primitive instruction revalidation blocker

## Source and compile checks

- Expected migrated catalog source digest: `sha256:c7cbcebde4015a87a462c26075662726c489f58c28f2151d67f94d9c9f226836`.
- `uv run nl2repo task validate-source catalog/sources/es-to-primitive` passed and reported that exact digest.
- `uv run python scripts/validate_instruction_quality.py` passed.
- `uv run nl2repo task lint-network --tasks-root catalog/sources` passed with zero `es-to-primitive` findings and zero source-root errors.
- All four declared private artifacts were present and verified by size and SHA-256.
- Two production compiles used Harbor `0.21.0`, `toolchain.node.lock.toml`, the parent CAS, and `--allow-private`. Both produced 244 files, canonical manifest `sha256:bc88768cc44c82bd393c5ea4ddfeca2bc55a8ccc1c641c47fa54ec4eb7241113`, and identical manifest-file SHA-256 `sha256:5a054c9d9c0c4e21c1aafb041c38d2b2a6ed7920097466fcf163a745e527e86`. The complete compile trees passed `diff -rq` byte identity.

## NoNetwork blocker

The hash-bound Oracle artifact is present and internally inspected. Its `solve.sh` initializes a Git repository, adds `https://github.com/ljharb/es-to-primitive`, and executes `git fetch` for the frozen revision at runtime before producing the source archive. This violates the required NoNetwork contract. No host authorization was granted; Oracle, empty, stub, forgery, and offline Harbor runs were not started. No Harbor run ID or raw receipt hash is claimed.

The existing lifecycle and historical `production-evidence.json` remain unchanged because their receipts belong to an older non-durable run tree and their Oracle command authorizes `github.com`. The current deterministic compile and payload inspection are summarized in the adjacent tracked JSON files.

## Remediation

Replace the Oracle materializer with a locally supplied, revision- and archive-digest-verified source archive, or register a replacement private Oracle bundle with an immutable local payload. Then compile the migrated source twice again and run the complete Harbor `0.21.0` Oracle, empty, stub, forgery, and offline matrix with no external network authorization. Persist all receipts under this evidence directory before updating production evidence. Do not grant `github.com`, reuse historical receipts, change the frozen denominator, or alter lifecycle state solely because of this artifact/verifier blocker.
