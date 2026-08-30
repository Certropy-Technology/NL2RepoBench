# `strnum` authoring provenance

## Source and license freeze

- Upstream: `https://github.com/NaturalIntelligence/strnum`.
- Frozen revision: `117d6a5f59fbb8f29d2f88c0c292d7dc44d67a7f`.
- Git tree: `3466dc19198a208eaf1c3ce82cad1d8311602d13`.
- Package version: `2.4.2`.
- Deterministic Git archive SHA-256:
  `af9a609e1a8e3ded71cb69e2362710a2dfbf51dfbff0d8755f8d205be9c05e04`.
- Root `LICENSE` declares MIT; license SHA-256:
  `2aa16be0f4fad003a352a955a43314e9d1d8deef7034060a82ac9c49f32b81e2`.
- The commit contains no submodules.

The private Oracle bundle fetches only this commit, asserts the resolved commit,
and verifies the archive digest before restoring the workspace. The model Agent
does not receive the Oracle bundle or source-host authorization.

## Build, API, and tests

The package is an ESM library with one default synchronous function. The frozen
upstream suite contains 30 Jasmine specs and passed 30/30 under the locked
Node 24.19.0/npm 11.17.0 image. The production contract freezes 42 independent
`node:test` leaves, including radix flags, leading-zero policy, negative zero,
precision rejection, exponent forms, overflow modes, Unicode numerals, regex
skip behavior, whitespace preservation, and determinism.

## Dependency closure

The only runtime dependency is `anynum@1.0.1`, pinned by npm lockfileVersion 3
with SHA-512 integrity. The private npm cache contains only the exact closure
required for offline candidate installation. Lifecycle scripts are disabled;
there are no native, platform-specific, optional, or transitive runtime
packages.

## Verifier boundary

The separate no-network verifier stages and packs the candidate under bounded
resource limits, installs it from the private npm cache, and invokes it as UID
10001 in one-shot child processes. A task-specific child adapter reconstructs
`skipLike` from bounded regex source/flags and preserves special numeric values
with tagged JSON. Trusted Node and Python processes never import candidate code,
and only the verifier writes grading, report, network, and reward artifacts.

## Gate status

The lifecycle is `controls-passed`. Official Harbor Oracle and task-local empty,
stub, forgery, install-script, loader-hook, call-hang, oversized-output, and
offline controls completed against the final production bundle. Receipt paths,
hashes, counts, rewards, and the remaining model-runtime image precondition are
recorded in `production-evidence.json`. This authoring lane did not run a model
Agent, perform independent review, integrate a dataset, or publish the task.
