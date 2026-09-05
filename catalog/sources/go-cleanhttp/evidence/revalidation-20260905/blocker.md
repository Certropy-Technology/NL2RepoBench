# go-cleanhttp instruction revalidation blocker

The migrated catalog source matches the expected digest
`sha256:81b51b3cbeea9d6cbe964503f4c182a36ce774453cec3a059ce15d211841ef3d`.
All three declared private artifacts match their sizes and SHA-256 digests. Two
production compiles using `toolchain.go.lock.toml`, private artifact resolution,
and no incomplete-mode flag produced byte-identical 68-file bundles. Their raw
manifest SHA-256 is `sha256:d002aaddec1c9b9f35d38a362e27aa1d3a320d1f94bc6402536e86847501dd2f`
and canonical manifest digest is
`sha256:02557af0142a5e6639088ad312fa1947b1f64c1b3efa7907e24866c513d9cb03`.

The private Oracle tar contains only `solve.sh`. That script initializes a Git
repository and fetches revision `2901fbf3e0ecb2512cd7d278977a6b4ae0342ac0`
from GitHub at runtime. It expects the resulting git archive to match
`sha256:e1937b5e35049788a73ef0ecbc7107a2e38a27f09876fd71ccdbf1809305d83f`,
but does not carry that archive. Runtime source-host access is forbidden for this
revalidation.

A bounded offline search checked the current Oracle bundle, task-local evidence,
repository Git history, retained local authoring sessions and task worktrees,
prior handoff metadata, and the authorized local CAS. None contained a
hash-verifiable copy of the expected 51200-byte source archive. No replacement
Oracle bundle could therefore be constructed. Oracle and controls were not run,
and historical network-authorized receipts were not reused. The lifecycle,
historical production evidence, frozen denominator, and generated projection are
unchanged.

Unblocking requires recovering the exact frozen archive from an approved
immutable local backup, embedding it in a private network-free Oracle bundle,
registering that bundle in CAS, updating the artifact reference, compiling the
new source twice, and running a fresh NoNetwork Oracle/control matrix.
