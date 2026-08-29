# `string.prototype.trim` authoring provenance

## Frozen source

- Upstream: `https://github.com/es-shims/String.prototype.trim`
- Revision: `81993cc9f134d72f778bea27d77a4b1ac0e98244`
- Commit tree: `7bed88b878618229326c3c7e3d6ee1cbb10a3df4`
- Raw `git archive --format=tar HEAD` SHA-256:
  `7bc78bdfb13f9647ad7de4835d75f48624d143fa48bc1b37d4ce75ef6c225609`
- Root `LICENSE` is MIT; its SHA-256 is
  `c16d06f1808d8d8c6ec0f6b6fb7e951126c46730fbb67320863a81f8aa8ca033`.
- The archive has 13 tracked files and no submodules.

The frozen package is CommonJS `string.prototype.trim@1.2.11`. Its public
root is a bound callable with `implementation`, `getPolyfill`, and `shim`
helpers. The upstream source-only probe ran 57 Tape assertions successfully;
the production contract is an independent 31-leaf JSON adaptation.

## Environment and dependency closure

The production runtime is Node `24.19.0`/npm `11.17.0`, Debian bookworm,
linux/amd64, glibc, from the digest-pinned Node image in `task.toml`.
The eight runtime dependencies resolve to a 91-package npm v3 lock closure.
All lock entries have integrity and HTTPS registry resolution, and the
closure has no native package, install script, platform marker, workspace,
registry override, or git/file dependency. The cache and lock are private
content-addressed artifacts; candidate install uses `npm ci`/pack/install with
offline mode and lifecycle scripts disabled.

## Verifier boundary

The separate verifier uses `node:test` and the canonical
`node-test-leaf-pass-rate-v1` metric. Each contract call spawns a fresh Node
child with a minimal environment and JSON request/response, so trusted tests
never import candidate code. The test runner, report normalizer, fixed
denominator, and reward remain verifier-owned.

## Scope and traceability

The public contract intentionally covers deterministic JSON-observable string
behavior and helper shape. Browser engine matrices, source lint tooling,
posttest audit networking, and non-JSON host objects are outside scope and are
recorded in `traceability.json` rather than silently omitted.
