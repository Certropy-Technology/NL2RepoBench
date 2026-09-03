# `chokidar` Provenance

- Upstream: `https://github.com/paulmillr/chokidar`
- Revision: `0bc7bed37d6b018e5b11afcce329bbf797d6441f`
- Git archive digest: `sha256:db938843dec95dbe7faf8d926240f97429432002a760f9d68dfec049c367c0af`
- License: MIT; `LICENSE` digest `sha256:bdfd5e0edb6089e6586c8f15e6a86fab83ffbeeda3b3b7b33734ccb8c5906965`
- Package metadata digest: `sha256:af684e90d1e0f4edcabf90cc3d7dbac79c98cc3b017ebe85d6f7065571d9cea5`
- Upstream lock digest: `sha256:457c0c1602bad2d9f2c7f77acc346764f1544ee44b18a49b88dba5fcb24dd8dd`
- Source checkout: `.nl2repo/authoring-work/chokidar/source`
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian Bookworm amd64/glibc
- Base image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
- Dependency contract: exact npm v3 lock and private offline cache bundle; no candidate or verifier runtime registry access
- Ground truth probe: `npm ci --ignore-scripts --no-audit --no-fund`, `npm run build`, `npm test`; 207 upstream tests passed in 52 seconds
- Scored contract: 29 leaves, independently authored from the inspected public behavior and executed against the source-built package before packaging
