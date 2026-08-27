# Oracle And Remediation Evidence

The task-local public source is backed by an opaque private dependency bundle,
private custom JSON verifier bundle, and private exact-revision Oracle bundle.
The generic compiler materializes those bytes only inside the separate
no-network verifier/Oracle environments.

Historical Oracle output reported `valid=true`, `collected=20`, `passed=20`,
and `reward=1.0`, but its private CAS artifacts were absent from this lane and
its generated Oracle script downloaded an unchecked GitHub archive. It is not
used as current production evidence.

The current private Oracle bundle uses a pinned `git fetch`, asserts the full
commit SHA, and verifies `sha256(git archive --format=tar <revision>)` against
the `source_digest` in `task.toml`. The frozen source and rebuilt private CAS
are recorded in `evidence/source-freeze.json` and the final compile/control
outcomes are recorded in task-local `.nl2repo` handoff evidence.
