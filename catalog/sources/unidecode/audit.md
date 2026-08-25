# `unidecode` production authoring record

The task is frozen to upstream commit
`8d83b7c70c39678c2b95cb0caf3d3c4425cb2cc2`. Its unprefixed
`git archive --format=tar` is 1,105,920 bytes with SHA-256
`a33c1751226d4cca24d0b3cf457a31932ee496f161713d654cfc07c10ef13c28`.
The source declares GPL-2.0-or-later licensing, package version 1.4.0, Python
3.7 or later, and no runtime dependencies.

The production contract contains 20 deterministic scenario leaves. It covers
the public functions and error class, package metadata and `py.typed`, ASCII
identity, exact Western and non-Latin transliterations, symbols, non-BMP and
enclosed forms, all error policies, surrogate warnings, lazy table imports,
positive and negative cache entries, and CLI text/stdin/file operation. Every
observation is specified in `instruction.md`.

The trusted verifier runs each scenario in a fresh candidate subprocess as uid
10001. Candidate code is imported only by that child from
`/tmp/candidate-site`; the trusted parent owns expected observations and final
pass/fail decisions. Missing, malformed, crashing, or timed-out child output
becomes a failed scenario rather than a verifier exception.

The dependency closure contains only `setuptools==80.10.2`, pinned by wheel
SHA-256 in a plain requirements lock. The compiler installs it from the package
index during Docker build with `--require-hashes`; no wheel or wheelhouse is
vendored. Agent and separate verifier run phases are no-network. The Oracle
bundle contains only `solve.sh` and the frozen source tar, checks the archive
SHA-256 locally, and performs no source fetch.

## Gate outcome

Official Harbor 0.21.0 production runs completed without exceptions. The
Oracle passed 20/20 with `valid=true` and reward 1.0. Empty was the accepted
candidate-installation failure at reward 0.0. The installable stub and forgery
controls each passed only the three trivial identity/empty scenarios (3/20,
reward 0.15), below the production ceiling of 0.20. Forgery attempts against
workspace reward/test paths did not affect verifier-owned grading. Every run
emitted a verifier receipt with `public_network_available=false` and failed
probes to both `pypi.org:443` and `1.1.1.1:443`.

The lifecycle stops at `controls-passed`. Reviews, pilots, dataset integration,
publication, commits, and pushes are outside this authoring lane. Exact receipt
paths and hashes are recorded in `production-evidence.json` and
`evidence/controls-passed.json`.
