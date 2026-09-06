# jsonpointer Instruction Revalidation Blocker

Revalidation used the queue's current post-migration source digest
`sha256:6651caa330c0dcec3efa2674534e6f14d94295412b33ec21ae79fed04809ccef`,
which matches `uv run nl2repo task validate-source catalog/sources/jsonpointer`.
The declared dependency lock, verifier bundle, and Oracle bundle were each
checked offline for exact size and SHA-256. The Oracle bundle is valid bytes but
contains only `solve.sh`; it has no frozen source archive or other installable
payload.

The generated Oracle script fetches
`https://github.com/stefankoegl/python-json-pointer` at revision
`5998f951dcc5ace60f67f35afe6778c445401a07`. This revalidation used no source
host, registry, DNS, or external-service authorization, so it was not run.
The task-local generated bundle was compiled twice with the locked toolchain;
both compiles exited 0 and were byte-identical with canonical manifest
`sha256:7fedf7712504d0bd5158fd669e6c5d9a876d677f3c15b907eafdaa28efa9e59f`
and raw manifest SHA-256
`sha256:044aeb7ffa78704727ffbce73ec65013a32e26ce57cab7a2582ec9bafb11b1c9`.

## Recovery Search

- Checked `catalog/sources/jsonpointer`, `catalog/tasks/jsonpointer`, and the
  task-local revalidation outputs for a source archive or embedded payload.
- Checked the configured local CAS and unpacked the Oracle/verifier bundles.
  The Oracle inventory was exactly `solve.sh`; no `source.tar` was present.
- Checked the retained jsonpointer authoring session, worktree names, handoff
  metadata, exact revision, exact archive digest, and source archive filenames.
  The session proves a prior online fetch claim but does not retain source
  bytes; the dedicated historical worktree is absent.
- Checked local authoring worktrees, handoff artifacts, and bounded local cache
  and Git-object locations. No exact source payload was found. Broad filesystem
  hash scans exceeded their bounded timeout and are not treated as proof of
  absence.

No replacement bundle was constructed because no local bytes prove both the
frozen revision and the declared source archive digest. Existing
`task.toml`, `production-evidence.json`, lifecycle, and historical
controls-passed receipts are intentionally unchanged. This is a revalidation
artifact/verifier blocker, not a newly declared terminal task block.

## Commands and Exit Results

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run nl2repo task validate-source catalog/sources/jsonpointer` | 0 | Current source digest matched the revalidation queue. |
| Offline size/SHA-256 check of every declared private artifact | 0 | Dependency lock, verifier bundle, and Oracle bundle exactly matched their declarations. |
| `tar -tvf` of the Oracle bundle and `rg` of extracted `solve.sh` | 0 | Bundle contains only `solve.sh`, which declares a GitHub fetch. |
| Two `uv run nl2repo harbor compile ... --allow-private` commands | 0, 0 | 57-file runtime projections were byte-identical. |
| Exact-digest/filename local recovery searches | 0 | No usable source payload found in the checked task-local, CAS, historical handoff, or retained worktree scopes. |
| Bounded broad filesystem hash and historical Git-object searches | 124 | Timed out before a complete scan; not treated as proof that no payload exists. |

## Next Step

Recover an exact local source payload or CAS backup, verify its revision and
archive digest, register a replacement Oracle bundle in the shared CAS, then
recompile and rerun Oracle plus empty, stub, forgery, and offline controls for
the current instruction-migrated source. Do not authorize GitHub, package
registries, DNS, or external services.
