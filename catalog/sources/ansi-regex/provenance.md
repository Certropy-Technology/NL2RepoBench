# `ansi-regex` authoring provenance

## Source freeze

- Upstream: `https://github.com/chalk/ansi-regex`
- Frozen commit: `7cf0228990eb38c27f9897f4fb17d42d39075a20`
- Package identity: `ansi-regex@6.3.0`, ESM, MIT.
- Commit timestamp: `2026-08-12T16:30:02+02:00`; tree
  `ad282c6f6d7ae1b9ad77425ad6e6cd558aee8446`.
- `git archive --format=tar HEAD` is 51,200 bytes with SHA-256
  `b59d0cd17c95437b3f80a0c25a69854d3ec4a5c2f27a732a9e45eabeb84faf96`.
- The separately packed npm tarball is SHA-256
  `40ee4a98ecd1505da731fddb668733c7ff58dddfd77ac08e34debec3f309d5f8`.
- The MIT license bytes are SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- No submodules and no runtime dependencies.

The frozen upstream test suite contains 29 AVA declarations in `test.js` plus
ANSI fixtures. The production denominator is a 24-leaf deterministic slice;
it does not claim full AVA/XO/tsd parity.

The reference package is retained only in the task-local private Oracle CAS.
The public source contains metadata, specification, and digests, not reference
implementation bytes.

## Runtime remediation

The upstream package declares development-only AVA/XO/tsd tooling. The Oracle
solution applies a bounded runtime packaging adaptation: it keeps the frozen
`index.js`, `index.d.ts`, license, README, and package identity, removes
development scripts/dependencies, and writes an empty npm v3 lock. Candidate
and verifier phases use Node `24.19.0` and npm `11.17.0` with no network.

## Verifier scope

The private `node:test` bundle freezes 24 leaves for package shape, ANSI CSI and
OSC matching, option flags, text preservation, and regex factory repeatability.
The child adapter transports only bounded JSON. Trusted grading is produced by
the separate verifier runtime and never trusts candidate-written reports.

## Residual risks

- This lane does not run a model Agent Run or claim independent blind review.
- ReDoS behavior is outside the fixed denominator; the verifier applies a
  bounded child timeout to every adapter call.
- The source revision is pinned by the queue claim; archive and license digests
  are recorded above and must be rechecked by the integrator before publication.

