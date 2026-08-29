# Authoring audit

The exact upstream commit was verified with `git ls-remote` and detached
checkout. The package metadata and BSD license were read from
`packages/espree`; dependencies and test files were inventoried directly from
the checkout. The public contract is a deterministic adapter over parse and
tokenize, avoiding callbacks and non-serializable parser state.

Remediation performed: created an npm v3 lock/cache closure for the three
runtime dependencies, a private child-process test adapter and fixed leaf
contract, an Oracle solve script that fetches and verifies the pinned commit,
and bounded negative controls. The adapter source path was corrected to the
compiler's `/tests/private/private` projection; the final Oracle then passed
24/24. Empty, stub, forgery, and offline controls completed with verifier-owned
reports and `public_network_available=false`. No Harbor model Agent Run was
started in this lane.
