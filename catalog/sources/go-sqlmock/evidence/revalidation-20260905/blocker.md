# go-sqlmock revalidation blocker

Revalidation date: 2026-09-05
Task: `go-sqlmock`
Source revision: `4e29cb9ba9984db4da4003b5c813f3747f450bc7`
Current queue/source digest: `sha256:acc384f3a623ed6f4c8e60249df55d0233bb850eb39e14f33e48e7180bb1a4bc`
Frozen upstream archive: 256000 bytes, `sha256:359bb2e809bade7c01d70eb5cb05a4ebef6c2a835a63293f0471c53d12b05734`

## Exact artifact checks

- Declared Oracle bundle: 918 bytes, `sha256:ce2edb98dc8ea4703395bd088015ea9f04d5044b83c2f42052dbf2b961a1a920`.
  CAS check returned `exists=True`, actual size `918`, and the declared SHA-256.
- Declared Go module bundle: 5169 bytes, `sha256:29e8f7f65b020cd6014fd6ede4761ddb9e8d8f93a8870b4ced96930754a6f8f2`.
  CAS check returned `exists=True`, actual size `5169`, and the declared SHA-256.
- Oracle bundle inventory command (`tar -tf` plus per-file hashing) returned only `.` and
  `./solve.sh`; it contains no `source.tar`, source directory, or installable source payload.
- The frozen source path recorded in `evidence/source-freeze.json` was checked with `test -f`:
  exit `1`, path missing.

## Local recovery search

The current Oracle bundle, current task-local evidence, historical handoff receipts, and the
bounded local authoring archive/CAS locations were inspected without network access. The
bounded archive command searched for `source.tar` and `upstream-source.tar` files of exactly
256000 bytes under the local authoring-live archive (depth 8): exit `0`, zero matches. The
private CAS size-filter search found one unrelated 256000-byte object with digest
`sha256:ba57de80e0aeee35c76b6564fbd64d2ce8b9a775d8b35413af259075baed1f72`; it does not match
the frozen digest. Historical receipts identify a source snapshot, but do not materialize its
bytes in the available local filesystem, so they cannot establish archive equivalence.

No replacement payload was constructed. A cache/module bundle or a different archive format
would not be equivalent to the declared frozen Git archive.

## Revalidation checks completed

- `uv run nl2repo harbor compile ... --toolchain toolchain.go.lock.toml --artifact-root <parent CAS> --allow-private`: exit `0`.
- The same compile was run twice into separate outputs. Both bundle manifests have SHA-256
  `sha256:f596ac35f902efea7bcc1932cf9e3eec1f4816daa6e5c9b323a523b8e933bb8a` and are byte-identical.
- No Harbor Oracle or control was run because the only Oracle path requires runtime source
  fetching and the mandatory NoNetwork policy forbids authorizing GitHub/codeload or any
  package/source host.

## Next step

Parent must restore the exact 256000-byte archive with the declared frozen SHA-256, or register
an independently proven replacement private Oracle bundle whose internal source payload is
bound to the revision and digest. Then update the private CAS/reference through the parent-only
path, recompile twice, and rerun Oracle plus the complete supported control matrix. Lifecycle
and `production-evidence.json` remain unchanged by this blocker.
