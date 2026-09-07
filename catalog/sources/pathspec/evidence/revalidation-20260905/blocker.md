# pathspec instruction revalidation blocker

- Task: `pathspec` (Python, revision `df3de4595df6e8a1cfa5782b01926b4fe461a864`).
- Queue source digest: `sha256:a6c1a6d96b87a304adaed119ff273dd0fbe047a846ad0d333cbb1593a3c47b35`.
- `validate-source` before mutation returned exit `0` with the same source digest.
- Frozen upstream archive digest: `sha256:0d8c72748d26926b3b0e7a3a983dd3135e9ad4b462388408a1bafc936a0236d9`.
- Historical `production-evidence.json` and generated projection were not changed; their
  receipts predate the migrated instruction and are not current evidence.

## Exact artifact status

The declared private artifacts were checked at their canonical CAS locations. None was
present in this isolated checkout, so no size or digest could be verified locally:

| role | digest | declared size | status |
| --- | --- | ---: | --- |
| dependency lock | `sha256:b3d7456ecf8cd481ce5ea8a7e28ad58078a134e6dd51c1a69e1cf6d6074f7d0e` | 442 | missing |
| verifier bundle | `sha256:91cbef328f5dd0e20215ae547e6f0878e349ac4f0b3276edf01ebcce4b2e024a` | 20480 | missing |
| Oracle bundle | `sha256:41cd24eb1bcc83c0f964b4617e7269d2e6d978f02f8e8fe6a195956a58dc4807` | 10240 | missing |

The source archive itself is also not available as a trusted local payload. A bounded
inspection of task-local and historical local names found no usable exact archive. The
historical Oracle recipe performs a runtime `git clone` from the upstream GitHub host,
which is forbidden under this task's `no-network` policy.

## Checks and skipped gates

Commands run after inspection:

```text
uv run nl2repo task validate-source catalog/sources/pathspec
  exit 0; source_digest=sha256:a6c1a6d96b87a304adaed119ff273dd0fbe047a846ad0d333cbb1593a3c47b35

CAS existence checks for the three declared artifact digests
  all missing; no artifact size/hash claim made

git diff --check
  passed
```

The following gates were deliberately skipped because the verifier and Oracle bundles
are unavailable and the Oracle source fetch is network-forbidden: compile twice, bundle
inspection, Oracle, empty, stub, forgery, install-hang, call-hang, offline, and fresh
collection/reward validation. No reward, collection, valid, or control result is claimed.

## Classification and remediation

Classification: `artifact-or-verifier-blocked` (not model failure and not infrastructure).

Restore the exact lock, verifier, and Oracle CAS objects, each matching both declared
size and SHA-256. Provide a trusted local source payload matching the frozen revision and
archive digest, or replace the fetch-based Oracle with a digest-verifying local recipe.
Then compile twice with the locked Python toolchain, require byte-identical manifests,
inspect the payload, and run the complete Harbor 0.21.0 NoNetwork Oracle/control matrix
with frozen denominator `43` before updating production evidence or projection.
