# `string.prototype.trimstart` authoring provenance

## Frozen source

- Upstream: `https://github.com/es-shims/String.prototype.trimStart`
- Revision: `6f8ee88da5b570d3addc1e8c6caf1461013bce45`
- Commit tree: `127dec998b54db809f26665908303e88ffb9c46c`
- The commit was verified with the GitHub commit API and is used only by the
  trusted Oracle `solve.sh`; the model Agent receives no source-host access.
- Root `LICENSE` is MIT. The source archive digest is recorded in `task.toml`
  after the Oracle fetch probe.

The upstream package is CommonJS `string.prototype.trimstart@1.0.8`. Its
production boundary is an independent 31-leaf JSON adaptation rather than a
copy of the upstream Tape suite.

## Environment and dependency closure

The production runtime is Node `24.19.0`/npm `11.17.0`, Debian bookworm,
linux/amd64, from the digest-pinned Node image in `task.toml`. The three
runtime dependencies resolve to a private npm v3 lock/cache closure. All lock
entries have integrity and HTTPS resolution; the closure has no native package,
install script, platform marker, workspace, registry override, or git/file
dependency. Candidate install uses npm offline mode and lifecycle scripts are
disabled.

## Verifier boundary

The separate verifier uses `node:test` and the canonical
`node-test-leaf-pass-rate-v1` metric. Each contract call spawns a fresh Node
child with a minimal environment and JSON request/response, so trusted tests
never import candidate code. The test runner, report normalizer, fixed
denominator, and reward remain verifier-owned.

## Scope and traceability

The public contract intentionally covers deterministic JSON-observable leading
trim behavior and helper shape. Browser engine matrices, source lint tooling,
posttest audit networking, and non-JSON host objects are outside scope and are
recorded in `traceability.json` rather than silently omitted.

## Authoring receipts

- `uv run nl2repo task validate-source catalog/sources/string.prototype.trimstart`
  passed with lifecycle `packaged`.
- `uv run nl2repo harbor compile catalog/sources/string.prototype.trimstart`
  passed twice with byte-identical bundle manifest
  `sha256:ed39a783a9dc4d6d5b1240a8ed9796bd5c4585479022ed8e41d589be21b79568`.
- The independent contract collection passed 31/31 in the local bounded child
  verifier. `npm ci --offline --ignore-scripts --no-audit --no-fund` also passed
  using the generated private cache bundle.
- Harbor Oracle was attempted once with Harbor `0.21.0`; Docker built the task
  environment but failed to allocate its default network because all predefined
  address pools were subnetted. No Oracle grading or Harbor `network.json` was
  claimed. Empty/stub/forgery/timeout/offline controls are therefore awaiting
  an infrastructure retry.
