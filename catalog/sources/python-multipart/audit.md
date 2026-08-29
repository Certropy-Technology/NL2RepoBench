# Audit

The frozen package is a pure-Python streaming parser with no runtime
dependencies. It has no native extension, service dependency, network client,
CLI entry point, or interactive terminal requirement. File uploads use the
standard library's temporary files; the verifier bounds the exercised payloads
and runs the candidate adapter as UID `candidate`.

The upstream suite collected 160 leaves. Five benchmark leaves are marked for
deselection, and the remaining 155 passed on CPython 3.12.11. The production
task uses 48 newly authored deterministic custom-json-v1 leaves. Randomized
chunking is represented by fixed splits, and the private verifier never places
candidate source on the trusted verifier's import path.

Candidate dependencies are empty at runtime. The only build-time dependency
closure is the exact Hatchling backend and its transitive requirements in the
private hash lock. The agent and verifier execution profiles remain
`no-network`; only a trusted Oracle run may use the exact upstream source host
to fetch the pinned revision through `harbor/solution/solve.sh`.
