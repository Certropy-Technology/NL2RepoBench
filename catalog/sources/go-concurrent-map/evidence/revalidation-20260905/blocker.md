# Revalidation checkpoint

The source digest and all three declared private CAS artifacts were verified. Two
production Go compiles using `toolchain.go.lock.toml`, private artifacts, and
`--allow-private` were byte-identical across 68 files. The Oracle payload already
contained the digest-verified `source.tar`; no replacement bundle was needed and
no source host was authorized.

The first Oracle attempt failed before a trial with
`EnvironmentStartTimeoutError`. One bounded retry completed the verifier with
`valid=true`, `1/1`, reward `1.0`, and all network probes false, but the Harbor
outer job did not finalize before the 1800-second command timeout. The parent
checkpoint then stopped continuation. Empty, stub, forgery, and offline controls
were not run. This is an infrastructure blocker for this revalidation wave, not a
candidate or source failure.

Local recovery inspection covered the current private Oracle bundle and task-local
source/evidence. The bundle's `source.tar` matched the frozen source digest and
revision, so no replacement payload proposal was created. Historical authoring
archive inspection was not allowed to run beyond the bounded checkpoint after the
Oracle retry; no claim is made about additional archives.
