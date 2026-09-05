# go-glob revalidation blocker

The migrated source digest is `sha256:e2b3ff94aed0705173baee23cf3866d3343e4e7b21ee30f09462bc58ba8f613b`.
All three private CAS objects are present and size/SHA-256 verified. Two production
compiles using `toolchain.go.lock.toml`, the parent artifact root, `--allow-private`,
and no `--allow-incomplete` produced byte-identical 68-file bundles with manifest
`sha256:828317a8d56180a04b74021401252f7139de0d1dab3912c2880d0af7d2871fda` and
canonical digest `sha256:1d599bd19982ba6d11a3634ce0369439c13669bde1985ad62d07341f14e08120`.

The Oracle CAS payload contains only `solve.sh`. It clones GitHub at runtime and
checks out revision `986c05fb7000e63414ddc61162d0067b7a1f5639`, which is forbidden by
the task's NoNetwork policy. The worker searched the current Oracle CAS, task-local
evidence, historical authoring worktrees, historical projections, and Git history for
matching source/module/verifier bytes. No hash-verifiable frozen source archive or
replacement payload was found, so no replacement bundle was created and no source
host was authorized.

The bounded Harbor Oracle attempt did not complete: the run remained pending while
the environment was being torn down after the 300-second bound. This is recorded as
an infrastructure/verifier blocker, not a candidate score. Empty, stub, forgery, and
offline controls were not run because they require a runnable final Oracle payload;
no control receipt is claimed.

Remediation: provide a private Oracle bundle containing the source archive or another
locally hash-verifiable materialization matching the frozen revision and
`sha256:dcf7c3e6caf75b32e832bc6236e056904ae3d96ffc23904d0a1662b84a684a07`, register
it in CAS, update the source artifact reference, recompile twice, and run the complete
Oracle/control matrix under NoNetwork.
