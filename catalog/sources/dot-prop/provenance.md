# dot-prop authoring provenance

## Source freeze

- Upstream: `https://github.com/sindresorhus/dot-prop`
- Revision: `d5d11c71a70bfb643a45d22821ed6d284240fce5`
- Frozen archive digest: `sha256:8260136eb763c56d5b073b0365ed875ccf9ce6aaad81c8647af2f51b0f53019c`
- License: MIT, upstream `license`, SHA-256 `sha256:5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Frozen package: `dot-prop@10.2.0`, ESM, 15 tracked upstream files, no submodules.

The archive and revision were obtained with a shallow immutable-revision clone.
The Oracle `solve.sh` repeats the fetch inside the trusted Oracle run, asserts
the resolved commit, checks the archive digest, and checks the frozen
`index.js` digest before copying the reference package into `/workspace`.

## Runtime and dependency remediation

- Node `24.19.0`, npm `11.17.0`, Linux amd64, glibc, Debian Bookworm image
  digest `sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- The upstream `type-fest` dependency is type-only and is not required by the
  runtime package. The candidate contract therefore uses an empty, explicit
  npm v3 closure rather than downloading development dependencies.
- The private dependency artifact is `sha256:5755837872e1b876ff62ab45a1e0f3c32aaa109172fd7ea707af942d773b042e`,
  a 10,240-byte bundle containing the lockfile and empty npm cache. It is
  installed only at image build time; candidate and verifier phases have no
  package-registry or source-host egress.
- The private test artifact is `sha256:1a8e9e3d92119442374c30d4fb2935e7f3109670417b94e1f5486765a509a72b`
  and contains an independently authored 36-leaf node:test suite, a JSON
  child adapter, and the test client. No upstream test file is copied.
- The private Oracle artifact is `sha256:020d3838568380c53e8e4c071289b05a3bdc13bd588733733068c506afcbfa00`.

## Verifier boundary

The production verifier uses the locked `node-test-subprocess-boundary-v1`
runner and `node-test-json-v1` report format. Each test sends JSON to a
candidate-owned child process; the trusted verifier never imports candidate
source. The adapter constructs cyclic objects, functions, sparse arrays, and
undefined-valued properties inside the child, so those cases are tested
without weakening the boundary.

## Observed authoring infrastructure note

The first Oracle build attempt exhausted the shared `/data` filesystem while
Docker was writing build metadata. This was classified as infrastructure, not
as a package or verifier failure. After bounded Docker builder/image cleanup,
the locked agent image tag was locally reconstructed from an already-running
Node/Python task image with the required SDK Python path; the successful Oracle
and control receipts below are therefore valid for this authoring host but the
integrator should retain the official immutable agent image reference from the
toolchain registry before publication.
