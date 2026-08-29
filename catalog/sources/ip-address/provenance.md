# `ip-address` Authoring Provenance

## Source freeze

- Upstream: `https://github.com/beaugunderson/ip-address`
- Revision: `ef98e0a0e77fbef1fdf8bc3bd33288b00b3103c9`
- Release tag: `v10.5.0`
- License: MIT, verified from the frozen `LICENSE` file
- Git archive digest: `sha256:5003fe0f3466d3c7b6a494d5aae4df4ca87d165fbede1e50b87fceaaa7f4977d`
- Frozen upstream baseline: Node `24.19.0`, npm `11.17.0`, `npm ci`, `npm run build`, and `npm test` passed; Mocha reported `3594 passing`.

The upstream checkout contains TypeScript sources and a large development lock
closure. The task runtime is adapted to a zero-runtime-dependency CommonJS
package containing the generated `dist` output and a minimal package manifest.
The reference bytes remain private; the public instruction describes behavior,
not implementation.

## Boundary and scope

The verifier uses `custom-json-v1` through a child process. It covers the root
exports, JSON-safe scalar methods, address projections, subnet and conversion
operations, classifiers, helper behavior, and error contracts. `BigInt`, class
instances, and regular expressions are projected by the private adapter; no
candidate module is imported into the trusted verifier process. Callback,
filesystem, random, clock, browser, native-addon, and network behavior is not
part of this task.

## Dependency and environment remediation

The release's devDependencies are not needed at runtime. A verifier-owned npm v3
lock/cache bundle is supplied even though the candidate runtime has no package
dependencies, so `npm ci --offline --ignore-scripts` is deterministic. The
candidate and separate verifier are network-isolated. Only the trusted Oracle
solution receives a run-scoped authorization for the exact upstream source host
to re-fetch and verify the frozen revision.
