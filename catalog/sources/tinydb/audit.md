# TinyDB production authoring record

Status: `controls-passed`. Review, pilot, dataset integration, commit, and push
are outside this task-only lane.

The task freezes upstream commit
`4aa53111d72c9cbaafcdc039211caf49f4face6f`, version 4.9.0. Its direct,
unprefixed 583,680-byte `git archive --format=tar` has SHA-256
`13f1c7b200e863ebd48ee328ecfa90cf844f746b4f9bba70d8008b62e7f17094`.
The root MIT `LICENSE` has SHA-256
`b0e2a2d39271e3d96b717d7be8235ac413d74797bf7f742f0801cfaad6c8c912`.
The frozen tree has no submodules.

The bounded 36-leaf contract covers package exports; abstract, memory, and
JSON storage; file creation, truncation, serialization options, read-only
errors, and warnings; query comparisons, paths, logic, regex, collections,
fragments, custom tests, errors, and cacheability; document and table insert,
read, update, operation, multi-update, remove, upsert, truncate, and error
behavior; database table management, default forwarding, persistence, and
context cleanup; middleware forwarding, nesting, caching, flushing, and JSON
persistence; query-cache invalidation and sharing; LRU eviction; and recursive
freezing. Every file path exercised by candidate behavior is created inside a
process-local temporary directory.

Only the unprivileged, resource-limited child imports candidate code. It emits
bounded JSON observations to the trusted parent, which owns expected values
and pass/fail decisions. Candidate code cannot write verifier rewards or
trusted result files.

The 945-byte dependency lock pins Hatchling 1.27.0 and its complete Packaging,
Pathspec, Pluggy, and Trove Classifiers closure with package-index hashes.
Docker build installs it with `--require-hashes`; no wheel, wheelhouse,
`--no-index`, or vendor dependency bytes are present. Agent and verifier runs
are no-network. The Oracle bundle contains only `solve.sh` and the local
digest-verified source archive and performs no fetch.

Harbor 0.21.0 passed the production gate: Oracle was valid at 36/36 and reward
1.0; empty was valid at 0; the installable stub was valid at 2/36; and the
forgery control remained at 2/36 despite a forged workspace reward of 1.0.
Every verifier network receipt reports `public_network_available=false`.
Exact task-local paths and hashes are recorded in `production-evidence.json`.
