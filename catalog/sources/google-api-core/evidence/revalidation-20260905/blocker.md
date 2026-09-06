# Revalidation Blocker: Missing Offline Oracle Payload

## Source freeze

- Task: `google-api-core` version `1.0.0`
- Upstream: `https://github.com/googleapis/google-cloud-python`
- Package path: `packages/google-api-core`
- Revision: `082a99a2c4a3e8d5df28eaeab9b2c710dd4296d5`
- Frozen source archive: `sha256:673b703e9c4d227ea29b4f1ad06aba4c7f872cbaa634424ceb08991b113d6b07`
- Frozen source archive size: `1,351,680` bytes
- Current queue source digest: `sha256:d623ef7009df015d6b3a129cb98aa337f0acb6e7ff834dc349fa8b0eae0a67e1`

## Artifact gate

The three declared private artifacts were present and matched their declared bytes:

| Artifact | Expected size | Expected SHA-256 | Result |
| --- | ---: | --- | --- |
| dependency lock | 30,519 | `sha256:caec483297b1c9ba10d20812b953cd84c3bd53efae4da16d67f5c6fc85eafc2d` | passed |
| verifier bundle | 20,480 | `sha256:71451eab7339331daf1af5f771eba9563ed91a4d604a4d6454dab3a917ff9c08` | passed |
| Oracle bundle | 10,240 | `sha256:3f04d6bc515c93c26a6711d9505e30de176c1792b4b93517a1a2b28aaad465ef` | passed |

The Oracle bundle contains only `solve.sh`. Its source acquisition step invokes
`git fetch` against GitHub at runtime, which is forbidden by this revalidation's
NoNetwork policy.

## Local recovery search

The following bounded, offline checks were run from the repository and returned no
exact payload matching the frozen source archive:

1. Listed and extracted the current Oracle bundle; it contained only `solve.sh`.
2. Searched task-local `evidence/`, current generated-task remnants, retained run
   roots, historical authoring handoffs, archive receipts, preserved worktrees, and
   local package/archive caches for `google-api-core` payloads and the frozen digest.
3. Checked archive candidates at the frozen archive size and compared SHA-256; no
   candidate matched `sha256:673b703e9c4d227ea29b4f1ad06aba4c7f872cbaa634424ceb08991b113d6b07`.
4. Checked repository text and receipts for the frozen digest and revision; these
   contained metadata only, not source archive bytes.

No cache zip, alternate archive format, generated source tree, or different archive
was treated as equivalent.

## Commands and results

| Command | Exit/result |
| --- | --- |
| `python3` queue lookup for `google-api-core` | exit `0`; expected source digest confirmed |
| `uv run nl2repo --help` | exit `0` |
| `uv run --frozen --project harbor-runner harbor --version` | exit `0`; Harbor `0.21.0` |
| offline SHA-256/size check of all three declared private artifacts | exit `0`; all three matched |
| `tar -tvf .nl2repo/artifacts/private/sha256/3f/3f04d6bc515c93c26a6711d9505e30de176c1792b4b93517a1a2b28aaad465ef` | exit `0`; only `solve.sh` present |
| bounded local payload/archive search | no exact frozen archive found |

Compilation, Oracle, and controls were intentionally not run after the recovery
search because running the current Oracle would require forbidden network access.

## Next step

Provide a trusted local `source.tar` whose bytes are exactly the frozen revision and
whose SHA-256 and size equal the values above. The parent integrator should inspect
the archive contents and `solve.sh`, construct an ignored replacement private
Oracle bundle, verify its outer and inner hashes, register it in the shared CAS,
recompute the task binding, compile twice, and rerun the complete Oracle/control
matrix. No lifecycle or production-evidence status was changed by this blocker.
