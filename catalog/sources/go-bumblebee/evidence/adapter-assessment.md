# Adapter assessment

The frozen revision is a host inventory CLI, not a stable pure-Go library
surface. `cmd/bumblebee` exposes `scan`, `roots`, `selftest`, and `version`.
The scan path combines filesystem traversal, platform-specific default roots,
endpoint identity, random run IDs, current UTC timestamps, ten metadata
ecosystems, exposure-catalog matching, signal cancellation, and optional
authenticated HTTP output.

The upstream tests use internal packages directly and create host fixture trees
inside the test process. The production verifier cannot import candidate code
or put candidate code on the trusted test process path. A faithful child-side
adapter would therefore need to define and implement virtual-root injection,
deterministic endpoint/time/randomness controls, fixture extraction, all
ecosystem dispatches, and a local HTTP sink double. No such adapter is present
in the frozen source or the repository's generic Go bridge.

The missing adapter is a verifier-contract blocker, not a dependency failure:
the exact source builds and tests offline with the locked Go toolchain. The
network sink and host-derived fields also make an unmodified CLI invocation
non-deterministic and unsafe for the current separate-verifier contract.
