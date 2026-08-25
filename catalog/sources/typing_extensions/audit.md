# `typing_extensions` production authoring record

The source is frozen to upstream release commit
`42027aba3558c9d9133a90bca17f6fecaecc48d8` (version 4.14.1). Its unprefixed
645,120-byte `git archive --format=tar` has SHA-256
`34f3316e0c4d93aefe33a10ceb5ba35487f14b9e7751e00aed323b7c6856264f`.
The project declares PSF-2.0 licensing and has no runtime dependencies.

The inherited 535-test same-process projection was not retained as the
production contract because it mixed runtime behavior with static-checker and
upstream implementation concerns. The private custom verifier freezes 32
Python 3.12 runtime scenarios for the selected export surface, standard-library
interoperation, special forms and introspection, defaults, aliases, TypedDict,
Protocol, overloads, decorators, warnings, annotation helpers, runtime assertion
helpers, NamedTuple, NewType, Buffer, Sentinel, and error behavior. This task
does not test or claim static typechecker parity.

Only an unprivileged, resource-limited candidate subprocess imports candidate
code from the candidate installation site. Trusted expected observations and
grading remain in the separate verifier. Missing, malformed, duplicated,
timed-out, or crashing candidate responses become deterministic failed leaves.

The build closure contains only `flit_core==3.12.0`, pinned with both published
artifact hashes in a plain requirements lock. Docker build installs it with
`--require-hashes`; no wheel, wheelhouse, or `--no-index` installation is
vendored. Agent and verifier runtime phases are no-network. The Oracle bundle
contains only `solve.sh` and the frozen source archive and validates the local
archive digest before extraction.

Official Harbor 0.21.0 gates passed. Oracle collected and passed 32/32 with
`valid=true` and reward 1.0. Empty workspace, installable stub, and reward
forgery controls were verifier-valid at reward 0.0; stub and forgery each
collected 32 and passed none. All four network receipts report
`public_network_available=false` for both public probes.

The lifecycle stops at `controls-passed`. Review, pilot, dataset integration,
publication, commits, and pushes remain outside this task-only lane. Exact
receipt paths and hashes are recorded in `evidence/controls-passed.json` and
`production-evidence.json`.
