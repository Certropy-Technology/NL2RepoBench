# go-ordered-map instruction revalidation blocker

The current queue entry was validated before revalidation. The expected
catalog source digest is
`sha256:950d67f2098f5dab946ee32be22713996dbc387b32349381cf1517f828aa4ee9`.
The declared frozen upstream source is revision
`01810fd7f1123a3e2e52a7320d5eb49215ca2474` with source archive digest
`sha256:08ed69c80663ed3926e5bce8db647519324b4b20ca9eec839acbd4d5c3fae9cc`
and size `30720` bytes.

All declared private CAS artifacts were present and independently verified:

| Artifact | Digest | Size |
| --- | --- | ---: |
| Oracle bundle | `sha256:d74c263d619e19173deccb24aabeac70127680e7ad68bd8d94345d6c7a4a1cd7` | 561 |
| Go module bundle | `sha256:35ac13a1fe5b594d8d1d30790f83bd289de7f47a8691931c726736f367039bb9` | 541 |
| Verifier bundle | `sha256:446ebe8bc905364baec4a1530b1fed91f41e9da074f9f862a4e2b27a85902b05` | 1250 |

The Oracle bundle was unpacked and contains only `solve.sh` (SHA-256
`sha256:833d63a4170a28af4a0acfdcfaa3eabfeea611e9b3db7123e50d7bceb58faad4`).
That script performs a runtime GitHub fetch and constructs the source archive;
it does not contain `source.tar` or another installable source payload. Runtime
GitHub, codeload, package registries, DNS, Go proxy, and all other external
services are forbidden by this task's NoNetwork policy.

## Local recovery search

The bounded offline search checked these trusted local locations and sources:

- the unpacked current Oracle bundle and generated `catalog/tasks/go-ordered-map`
  payload;
- `catalog/sources/go-ordered-map/evidence/` and all task-local source files;
- repository Git-tracked history and retained authoring handoffs/state;
- retained authoring worktrees and archive files under the local retained
  authoring archive root;
- the authorized private CAS under `.nl2repo/artifacts/`;
- local Go module cache entries for `github.com/iancoleman/orderedmap`.

The exact commands and results were:

```text
CAS_ROOT=<authorized-private-cas>
tar -tf "$CAS_ROOT/private/sha256/d7/d74c263d619e19173deccb24aabeac70127680e7ad68bd8d94345d6c7a4a1cd7"
exit=0; entries: ./ and solve.sh only

find "$CAS_ROOT" -type f -name 08ed69c80663ed3926e5bce8db647519324b4b20ca9eec839acbd4d5c3fae9cc
exit=0; no matching source archive

find "$RETAINED_AUTHORING_ROOT" -type f \( -name source.tar -o -name oracle.tar -o -name orderedmap.go \) -path '*go-ordered-map*'
exit=0; no matching source payload

GOMODCACHE_DOWNLOAD_ROOT=<local-go-module-cache-download>
find "$GOMODCACHE_DOWNLOAD_ROOT/github.com/iancoleman/orderedmap/@v" -maxdepth 1 -type f
exit=0; only v0.3.0.info (123 bytes), no module zip or source archive

rg '01810fd7f1123a3e2e52a7320d5eb49215ca2474|08ed69c80663ed3926e5bce8db647519324b4b20ca9eec839acbd4d5c3fae9cc' "$RETAINED_AUTHORING_STATE_ROOT"
exit=0; only metadata and prior log references, no source bytes

rg -l '01810fd7f1123a3e2e52a7320d5eb49215ca2474|08ed69c80663ed3926e5bce8db647519324b4b20ca9eec839acbd4d5c3fae9cc' "$RETAINED_ARTIFACT_ROOT" "$CATALOG_ROOT"
exit=124 after 240 seconds; infrastructure timeout on the broad recursive scan
of retained worktrees, followed by the narrower exact-path/name searches above
and below
```

No exact source archive or revision-associated installable payload was found.
The only source-like files in retained worktrees belong to other tasks or are
task metadata; they are not equivalent to the required 30720-byte Git archive.
No replacement private bundle was constructed or proposed.

## Compile verification

Because all declared private artifacts were available, the source was compiled
twice with Go 1.26.5 and Harbor 0.21.0 using the locked toolchain and private
artifact root, without `--allow-incomplete`:

```text
CAS_ROOT=<authorized-private-cas>
uv run nl2repo harbor compile catalog/sources/go-ordered-map --output .nl2repo/go-ordered-map-revalidation-compile-a --toolchain toolchain.go.lock.toml --artifact-root "$CAS_ROOT" --allow-private
exit=0
uv run nl2repo harbor compile catalog/sources/go-ordered-map --output .nl2repo/go-ordered-map-revalidation-compile-b --toolchain toolchain.go.lock.toml --artifact-root "$CAS_ROOT" --allow-private
exit=0
```

Both generated manifests were 12574 bytes with identical SHA-256
`sha256:19c8f1b844775412ecd7a99d061ab20e589ff9c4101daf033a4fc875c4f3dec7`.
The compile outputs are ignored and are not cited as durable production
evidence.

## Status and next step

The existing lifecycle and `production-evidence.json` remain unchanged. No
Oracle, control, reward, collection, or fresh production receipt is claimed.
This is an artifact/verifier blocker, not a model result.

Unblocking requires recovering the exact 30720-byte archive for revision
`01810fd7f1123a3e2e52a7320d5eb49215ca2474` from an approved immutable local
backup, embedding it in a replacement private Oracle bundle whose inner and
outer hashes are verified, registering that bundle in shared CAS, updating the
artifact reference, compiling the source twice again, and then running a fresh
NoNetwork Oracle plus the complete supported control matrix. Source-host access
must remain forbidden.
