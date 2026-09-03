# `npm-run-path` authoring provenance

## Frozen source

- Upstream: `https://github.com/sindresorhus/npm-run-path`
- Revision: `b9128591fc59429d8b0df7047d5283f259dc5e77`
- Tree: `c02e747e5d191f16b9baf3e9454381fbcd1aa503`
- Package version: `6.0.0`
- License: MIT; tracked `license` SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Deterministic `git archive --format=tar --prefix=npm-run-path/ HEAD`
  SHA-256: `8b7133f569873efe624778419ce87b94a9df78ac19f80a4a7217f9adbd67664f`
- No submodules. `.gitattributes` only fixes LF text normalization.

The remote `main` ref resolved to the same full revision during authoring.
The trusted Oracle fetches that exact commit, asserts it, recreates the
prefixed archive, and checks this digest before extracting into the workspace.

## API and tests

The runtime has two named ESM exports, `npmRunPath` and `npmRunPathEnv`. The
full frozen upstream `xo && ava && tsd` command passed under Node `24.19.0` and
npm `11.17.0`; AVA reported 28/28 passed.

The production verifier has 33 deterministic `node:test` leaves. It covers
both functions, package metadata, declarations, parent traversal, PATH edge
segments, option switches, deduplication, URL arguments, Linux PATH-key
selection, environment cloning, errors, and repeatability. A fixed adapter
constructs URL objects inside an unprivileged candidate child. No trusted
process imports candidate code.

## Runtime and dependency closure

- Image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, glibc `2.36`,
  `linux/amd64`.
- The upstream `.npmrc` disables lockfiles and its development manifest names
  AVA, XO, and tsd. Production packaging replaces only that manifest with a
  lifecycle-free runtime manifest and an npm v3 lock.
- Exact runtime packages: `path-key@4.0.0` and `unicorn-magic@0.3.0`. Both have
  SHA-512 lock integrity. Neither has transitive, native, platform, or install
  script dependencies.
- Private npm closure: `sha256:eb2735cb44d12c947427bbffca5584cef231a219fcf932310feb6d08b7801de4`
  (`92160` bytes). Its internal validator passed for npm `11.17.0`.
- A clean `npm ci --offline --ignore-scripts --no-audit --no-fund` followed by
  `npm pack --ignore-scripts` passed in the pinned image with Docker network
  disabled.

## Private artifacts

| Purpose | SHA-256 | Bytes |
| --- | --- | ---: |
| npm dependency closure | `eb2735cb44d12c947427bbffca5584cef231a219fcf932310feb6d08b7801de4` | 92160 |
| verifier command plan | `ecade7e4a7652dc33367d2c5ce2971815591d9ae5bc4482e009eb1fa3af6552a` | 176 |
| private 33-leaf tests and adapter | `d643682871092029801cc946b76fe08f4f473f669c7d48b2a3f0c10557ebd953` | 20480 |
| Oracle solution | `bfb67879e82bc99dfe8e2ae2ed14225ab5c8ab06e90b377b41bb0b1a3a4e0652` | 10240 |

The model Agent receives none of these source, test, adapter, or Oracle bytes.
The compiled environment contains only the offline dependency cache needed to
install candidate-declared runtime dependencies.
