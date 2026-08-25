# `six` production authoring record

The task is frozen to upstream commit
`c8e394065cd541a16c040515dc0afb85cf22a7c3`. Its unprefixed
`git archive --format=tar` is 153,600 bytes with SHA-256
`4e2ea68f7238cdb11813a33867a4caa43737d84d03bfe2c54ae5e855be8a6fe3`.
The source declares MIT licensing, version 1.17.0, Python 2.7 or 3.3+, and no
runtime dependencies. This task executes only the Python 3.12 behavior.

The inherited 200-item same-process pytest projection is not the production
contract. The private custom verifier has 21 scenario leaves derived from the
frozen implementation, upstream tests, and upstream documentation. It covers
identity and constants; byte/text coercion; I/O aliases; mapping, iterator, and
callable helpers; function and method accessors; execution, printing, and
exception chaining; metaclass/decorator behavior; unittest aliases; lazy moved
modules and iterables; urllib aliases; custom moves; and direct import protocol
behavior. Every leaf maps to a public section in `instruction.md`.

The trusted verifier launches a fresh isolated candidate subprocess as uid
10001. Only that child imports candidate code from `/tmp/candidate-site`.
Trusted expected observations and pass/fail decisions remain in the separate
verifier process. Missing, malformed, timed-out, or crashing candidate output
becomes 21 deterministic failed leaves rather than a verifier exception.

The dependency closure contains only `setuptools==80.10.2`, pinned by its wheel
SHA-256 in a plain requirements lock. The compiler installs it from the package
index during Docker build with `--require-hashes`; no wheel or wheelhouse is
vendored. Agent and verifier run phases are no-network. The Oracle artifact
contains only `solve.sh` and the digest-verified frozen source tar and performs
no source fetch.

## Control outcome

Official Harbor 0.21.0 production runs completed in order. The Oracle installed
the frozen source and passed 21/21 with `valid=true` and reward 1.0. The empty
workspace was the accepted verifier-valid candidate installation failure at
reward 0.0. The installable stub passed 1/21 (reward 0.047619), and the
installable reward-forgery candidate passed 0/21. Every run emitted a verifier
network receipt with `public_network_available=false` and both `pypi.org:443`
and `1.1.1.1:443` unavailable.

The lifecycle therefore stops at `controls-passed`. Review, pilot, dataset
integration, and publication are outside this authoring lane. Exact receipt
paths and SHA-256 values are recorded in `production-evidence.json` and
`evidence/controls-passed.json`.
