# `es-to-primitive` authoring provenance

Status: `controls-passed`; ready for independent review and later model pilot.

## Source and license freeze

- Upstream: `https://github.com/ljharb/es-to-primitive`.
- Frozen revision: `f33dccb3a8950f4abc67f43bec81f776da9cdf13`
  (`v1.3.4`), commit timestamp `2026-06-25T18:50:56-07:00`.
- `git archive --format=tar` SHA-256:
  `ed5eecf6d29ef3e59e0ef91694d2e4a5814af572b238e1c1df278189560d44bf`.
- Archive size: 81,920 bytes; 29 tracked files; no submodules.
- Root license and package metadata declare MIT. `LICENSE` SHA-256:
  `c61652db3d2808f667b48af0a358f0d85fd07ad4a0d0b1a50882dec3b764c522`.

The private Oracle fetches only the full frozen revision, asserts `FETCH_HEAD`,
recreates the exact archive, and checks this digest before writing `/workspace`.
The Oracle solution is not copied into the model environment.

## Baseline and inventory

- Locked image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian 12, linux/amd64, glibc 2.36.
- Upstream `npm run tests-only`: 400/400 Tape assertions passed, exit 0.
- Production verifier: 33 deterministic `node:test` leaves; a direct locked
  image, no-network Oracle probe passed 33/33.
- API and test inventories are recorded in `api-inventory.json` and
  `test-inventory.json`; public assertion mapping is in `traceability.md`.

## Dependency closure

- Six direct runtime dependencies resolve to a 21-package exact graph.
- Private npm v3 closure:
  `sha256:7992ea519f7fce4d9d71c308c7c5b6e245c6f753a85c2cff9d839462418ee454`
  (962,560 bytes).
- The bundle contains `package-lock.json`, 84 npm cache files, and SHA-256
  records for all 85 lock/cache files.
- Repository `validate_npm_dependency_bundle` passed for npm `11.17.0`.
- A clean Docker `--network none` `npm ci --offline --ignore-scripts` installed
  all 21 packages successfully.

## Verifier and private artifacts

- Verifier: separate no-network image; candidate install and calls use UID
  10001. Trusted `node:test` never imports candidate code.
- Task-specific scenarios construct Symbols, boxed values, custom methods, and
  exceptions only inside a bounded child. Tagged JSON returns normalized values,
  method order, identity observations, and exceptions.
- Test bundle:
  `sha256:ebdf99ae719ca7b12506da173db24d7415a419afbdc0de44fa3542f4c2dd8654`
  (20,480 bytes).
- Command-plan bundle:
  `sha256:10e70a89b271a2cd71d8dbaa6848530c6550ac4d87e65ae87d7332265e5eedd9`
  (10,240 bytes).
- Oracle bundle:
  `sha256:2baa630953d8f9411021a7c5ef57a2f93c3e16586a076f00d3ac4ce9eaa79783`
  (20,480 bytes).

## Network and lifecycle policy

Candidate and verifier phases are no-network. Task metadata contains no source,
registry, mirror, or provider host. The trusted Oracle alone needs a run-scoped
`github.com` authorization. Candidate lifecycle scripts, native addons,
workspaces, loaders, and runtime package fetches are forbidden.

## Production gates

- Canonical source validation passed.
- Full source-root network lint passed with zero errors and no
  `es-to-primitive` finding; unrelated legacy warnings remain outside this lane.
- Production compilation with `toolchain.node.lock.toml`, private artifact
  authorization, and no `--allow-incomplete` is deterministic and integrity
  clean.
- Harbor `0.21.0` Oracle: `valid=true`, 33 collected, 33 passed, reward `1.0`.
- Empty and install-script controls: verifier-owned candidate installation
  failure, reward `0.0`. Stub, forgery, loader-hook, and offline controls:
  33 collected, 1 passed, reward `1/33`. Bounded hang and oversized-output:
  33 collected, 0 passed, reward `0.0`.
- Every Oracle/control verifier network receipt reports
  `public_network_available=false`.

No Harbor model Agent Run, blind review, publication projection, or parity
experiment was performed in this authoring lane.
