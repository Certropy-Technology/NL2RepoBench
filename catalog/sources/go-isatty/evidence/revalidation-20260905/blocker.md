# go-isatty instruction revalidation blocker

## Status

Revalidation is blocked at the local Oracle-payload recovery gate. The current
source remains lifecycle `controls-passed`; this file does not change
`task.toml` or `production-evidence.json`.

## Frozen source authority

- Task: `go-isatty` version `0.1.0`
- Queue instruction/source digest: `sha256:a862cf539c285eae3bd0a9fb86c2eaf3a3b31ef9db491d4d78c4a846204c6cbc`
- Upstream revision: `c44dc0b9c702c76577fdb7898032969e0611efc2`
- Required source archive: git-archive tar, `30720` bytes,
  `sha256:777f5b348771b16c22295784ad7b225254e1408ff983df7827b65ca819c5c3db`

The queue digest was validated before any change with:

```text
uv run nl2repo task validate-source catalog/sources/go-isatty
exit 0; source_digest=sha256:a862cf539c285eae3bd0a9fb86c2eaf3a3b31ef9db491d4d78c4a846204c6cbc
```

## Declared artifact checks

All three declared private artifacts were checked against the parent CAS and
were present with exact bytes:

| artifact | size | SHA-256 |
| --- | ---: | --- |
| Oracle bundle | 803 | `273286a92a013f3ef23bf257d2b05082142cb6f02abe6b3f99aca1620531fe76` |
| Go module bundle | 1024779 | `b554361552d902f2c8142f59144953aaac6371e5b563cd0dbcd79e7e563d16c7` |
| verifier bundle | 773 | `9461107536ec53fa791702bf3c8cf295f27cb0d57ee20ec4e95bb96548ab56ef` |

The Oracle bundle was inspected offline with `tar -tf`; it contains only
`./solve.sh`, so it does not contain `source.tar` or another installable
reference payload.

## Bounded local recovery

The following local sources were checked without network access:

1. Parent private CAS path for the Oracle bundle and its complete tar listing.
2. The prior supervisor compile output for `go-isatty`, which contains the
   generated runtime and module/verifier material but no source archive.
3. Task-local source/evidence and the two retained Go authoring archive
   receipts. The receipts record
   `source_snapshot_included=true` and source metadata, but retain only object
   metadata; no source bytes are materialized locally.
4. Task-specific authoring state and retained `go-isatty` run metadata. These
   contain claims/logs and receipts, not a
   hash-matching `30720`-byte source archive.
5. The local vendored `github.com/mattn/go-isatty` package in the unrelated
   `go-gron` run. It is a partial module directory rather than the frozen
   git-archive tar and cannot establish the required archive digest.

No exact payload matching both the frozen revision and the required archive
digest/size was proven. The existing `solve.sh` would fetch GitHub at runtime;
that path was not run and no source host was authorized.

## Offline compile probes

Because all declared CAS artifacts were present, the source was compiled twice
with the locked Go toolchain and parent CAS. Both commands exited `0`:

```text
uv run nl2repo harbor compile catalog/sources/go-isatty --output <compile-a-output> --toolchain toolchain.go.lock.toml --artifact-root <parent private CAS root> --allow-private
uv run nl2repo harbor compile catalog/sources/go-isatty --output <compile-b-output> --toolchain toolchain.go.lock.toml --artifact-root <parent private CAS root> --allow-private
```

Each output contains 706 files. The two trees are byte-identical. Both bundle
manifest files have SHA-256
`ef07e6936d83f47d4228b49fe0d56fa330d4f72ad1f14f065c9495088bc93cfb` and
canonical manifest digest `sha256:074adad08a7661fd976e8d21b98c384aab0de7ba40e0a5becf2e8ad389289b57`.
The compile outputs are temporary worker artifacts and are not used as
production evidence.

## Failure class and next step

- Failure class: `artifact-oracle-payload-unavailable`
- Network policy: `no-network`; no GitHub, codeload, Go proxy, DNS, or registry
  access was attempted.
- Next step: parent must recover or register an independently verified private
  source payload whose bytes match revision
  `c44dc0b9c702c76577fdb7898032969e0611efc2` and the exact archive digest
  above. After parent registration, recompute the source/bundle digests and run
  a fresh compile, Oracle, and complete control matrix. Existing production
  receipts must not be reused for the migrated instruction.
