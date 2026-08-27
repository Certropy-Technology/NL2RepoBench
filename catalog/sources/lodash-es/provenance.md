# Provenance

Status: `controls-passed`. Review, pilot, and publication remain pending. The
catalog lifecycle uses the shared enum value `controls-passed`; the worker
handoff label `awaiting-agent-run` is not a valid catalog status.

- Upstream: `https://github.com/lodash/lodash`
- Revision: `a666ba591064c8011988275790ad7d625279f09c`
- Git archive SHA-256: `4b815834ee052cbd62e39ae63019905344135368cd48f0dfcbbcaf7635e3ec9a`
- License: MIT, from the frozen `LICENSE` file.
- Frozen source checkout: `.nl2repo/authoring-work/node-discovery-20260826-r1/lodash-es/source`
- Frozen public API inventory: 308 enumerable root values (306 functions and
  the `VERSION`/`templateSettings` values). The scored subprocess-safe slice
  contains 29 functions plus the default-export aliases described publicly.
- Upstream test inventory: 307 QUnit module declarations, 1,754 QUnit test
  declarations, and a frozen runtime denominator of 6,831 assertions.
- Node 24 baseline: three independent no-network runs each reported
  `6831 passed / 6831 total`, exit code `0`, in Docker image
  `node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.

The upstream npm lockfile is v1 and has a large historical development closure.
The scored package intentionally has zero runtime dependencies, so the task uses
a separate npm v3 empty-cache artifact and does not ask the model to reproduce
the upstream development install. The six Node 22 strict-mode failures are not
part of the frozen gate; the same suite is green in the locked Node 24 image.

The private Oracle payload contains the frozen revision's `lodash.js` byte-for-
byte as `lodash.cjs` (SHA-256
`9bd765def21a6704a6d7e54ecf76004811ba7df19b387b60e04740785794e376`).
`solve.sh` verifies that digest before constructing the ESM package. The model
agent receives neither this payload nor the Oracle bundle.

Private production artifacts are content-addressed under `.nl2repo/artifacts`:

- empty npm v3 dependency closure:
  `sha256:f01344b94a5615ed1db23ea6056bb1d7f0f7f71286b8cccf1db7a72b69611673`;
- command-plan bundle:
  `sha256:e9338437d214111fee4790824bfc08ed1346a2519c1bcb439d53217221ed1040`;
- 30-leaf private test bundle:
  `sha256:75dc3dbbcf630cfd96493e8e4a0cb2562e5fc653a25d3cda7a8b52ec1986a19b`;
- digest-verifying Oracle bundle:
  `sha256:d7b00b1e68ee5e4d19e3e333f9472460702c167667bdf7f3b802f2fb278b3e86`.
