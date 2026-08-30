# `strip-final-newline` authoring provenance

## Source freeze

- Upstream: `https://github.com/sindresorhus/strip-final-newline`
- Frozen commit: `a1bfe78e3a3de2f73ed3a7600932d7cc952732b4`
- Package identity: `strip-final-newline@4.0.0`, ESM, MIT.
- Commit timestamp: `2024-10-28T05:10:24Z`; tree
  `14325a323da3cffd0a134a79e3e02e0528e272f4`.
- `git archive --format=tar` is SHA-256
  `83aae0869106aec568aae42cf3fc4cbf49c3dca21492dfc797d1b0b79a201077`.
- The MIT license bytes are SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- No submodules and no runtime dependencies.

The frozen upstream suite contains 15 executable AVA assertions plus four
TypeScript declaration assertions. The production denominator is a 29-leaf
deterministic behavior contract; it does not claim full AVA/XO/tsd parity.

## Runtime remediation

The upstream package declares development-only AVA, XO, and tsd tooling. The
Oracle solution preserves the frozen implementation and declaration, removes
development scripts/dependencies, and writes an empty npm v3 lock so the
candidate install is deterministic and offline.

## Verifier scope

The private `node:test` bundle freezes package shape, one-final-newline string
semantics, CRLF handling, byte-array behavior, view aliasing, invalid input
errors, and repeatability. The child adapter transports only bounded JSON.
Trusted grading is produced by the separate verifier runtime and never trusts
candidate-written reports.

## Residual risks

- This lane does not run a model Agent Run.
- ReDoS and large-input performance are outside the fixed denominator; each
  adapter call has a bounded timeout.
- Blind review, dataset integration, publication approval, and campaign-level
  controls remain integrator stages.

## Revalidation receipt

The first production compile attempt used the Python `toolchain.lock.toml` and
failed closed with exit code 1 because the Node compiler requires the locked
`toolchain.node.lock.toml` schema. Recompilation with that Node lock completed
with exit code 0 and emitted a 75-file production bundle. The bundle manifest
SHA-256 is `6f99813295eafcd8ddbf1d6d05aabf63fd8eb63e69541113047cdaf6acde92e5`
and its canonical manifest digest is
`sha256:075cebcccbe9d6bdbcf2f5a26639309df39bc2c05732efe41e92cb9aede0217d`.

Harbor 0.21.0 Oracle run `oracle-v4` passed 29/29 with reward 1.0. Empty,
stub, forgery, bounded hang, install-script, loader-hook, and offline controls
all exited zero and produced verifier-owned network receipts with
`public_network_available=false`. Stub and forgery each collected 29 leaves
and passed 2; the forgery reward remained verifier-owned. The loader-hook
control collected 29 and passed 12 without activating the loader. Empty and
install-script were the documented zero-leaf candidate-installation-failed
exceptions; hang was a bounded candidate-call-failed result.
