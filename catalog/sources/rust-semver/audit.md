# rust-semver authoring audit

Scope: `catalog/sources/rust-semver/` and the generated
`catalog/tasks/rust-semver/` projection only. No shared compiler, schema,
runtime, dataset, documentation or other task file was modified.

Design. The candidate rebuilds `semver` from an empty Cargo workspace against a
frozen denominator of 26 leaves: 25 two-process bridge scenarios plus one
offline `--no-default-features` check performed by the verifier itself. The
candidate-linked adapter replays numbered scenarios and returns only bounded
hex observations. The root-only checker holds every expected value, never links
the candidate library, and always renders all 26 leaves, so an adapter that dies
mid-run cannot shrink the denominator.

Hardening. The candidate tree is copied into a private scratch root and built
unprivileged inside a private writable `CARGO_HOME` that remains pinned to the
image's vendored store. The tree is frozen root-owned and read-only before any
trusted linking, and symlinks or special files are rejected outright. Every pipe
is byte-bounded and every adapter response line is length-capped. Process
cleanup is intentionally scoped to the process groups this verifier spawned
instead of scanning the numeric candidate uid globally, because a shared host can
run unrelated concurrent Harbor tasks under the same uid; a global sweep would
both misfire and interfere. The checker is root-owned mode `0500` while the
adapter is execute-only, and the report's leaf identity, order and vocabulary are
validated before any score is produced.

Corrections found while authoring. Compiling against the frozen revision showed
that `Version` exposes `cmp_precedence` rather than `compare_precedence`, that
`Error` implements neither `Clone` nor `Eq` nor `Hash`, and that `Op` is
`#[non_exhaustive]`; the public instruction now states the true shape. Behaviour
testing exposed two independent matching code paths, `matches_req` and
`matches_comparator`, so `Comparator::matches` became its own leaf. Mutation
testing confirms the denominator discriminates: removing the pre-release gate in
`matches_req` fails exactly `prerelease-matching-rule`, while an inert stub and an
empty workspace each still collect 26 leaves at zero.

Local evidence. Reference bridge 26/26; stub 0/26; empty workspace 0/26; forgery
probe 0/26 with planted `reward.json`, `rust-report.json` and `junit.xml`
ignored; upstream offline tests 34 passed; two production compiles byte-identical.

Not claimed here. Official Harbor Oracle, Nop/stub/forgery/offline runs, model
pilots, independent review and dataset publication are parent-level gates.
