# `mdast-util-phrasing` Authoring Provenance

## Frozen Source

- Upstream: `https://github.com/syntax-tree/mdast-util-phrasing`
- Revision: `67d563d643f75cf4fd26bc3121ddebb89e3a0a9c` (`4.1.0`)
- Git tree: `c3d4e6b34f4eade0b566afa3a11691a9b9fbcd32`
- License: MIT
- License SHA-256: `b6d1a4e1831b177acc96f22a817d4f0f4c18419355badc3125754445fc69e3a7`
- `package.json` SHA-256: `c020a54303d9d422c9def6ba5416db74c0f30b2783f2a84b7248b0d61c2ac113`
- `lib/index.js` SHA-256: `cfba43614dcc2d644d7f0b2a83a172b6119aa70ba10a504f03528a0fb4c873eb`
- `test.js` SHA-256: `7530c720cf994aabdc710811291098140de62bada5526175bba974b8fcccebfe`
- Exact archive command: `git archive --format=tar 67d563d643f75cf4fd26bc3121ddebb89e3a0a9c`
- Archive SHA-256: `fe71915a39869c97b9a9132886ff511654b42d4109183853592b580db458650b`
- The source has 13 tracked files and no submodules.

The unmodified package was tested in the pinned Node 24 image. `npm run build`
reported 73/73 type coverage and `npm run test-api` passed all 10 reported
`node:test` nodes (one parent plus nine leaf subtests). The broader `npm test`
probe reached the formatting stage but failed because the digest-pinned slim
Node image does not contain `git`, which `remark-preset-wooorm` invokes to
inspect repository metadata. This non-runtime formatting failure is retained in
task-local logs and is not treated as a package behavior failure.

## Runtime and Dependency Closure

The production runtime is Debian Bookworm Node `24.19.0`, npm `11.17.0`,
linux/amd64/glibc, image digest
`sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
The private npm v3 bundle pins `@types/mdast@4.0.4`, `@types/unist@3.0.3`, and
`unist-util-is@6.0.1` with registry integrity metadata and complete npm cache
bytes. Candidate installation and verifier execution are offline with lifecycle
scripts ignored.

## Verifier and Oracle Boundary

The frozen denominator is 36 independently named leaves. The verifier packs
and installs the candidate into a candidate-owned site and every behavior call
runs as UID/GID 10001 in a bounded child. Trusted code owns collection, network
checks, normalized reports, JUnit, grading, and reward.

The private Oracle solution alone fetches the exact revision from the upstream
host. It asserts `FETCH_HEAD`, recomputes the git archive digest, extracts the
frozen tree, removes development and lifecycle metadata, supplies the frozen
runtime lock, and writes only the package distribution to `/workspace`. The
future model Agent receives neither the Oracle bundle nor source-host access.

## Gate State

Production compile, Oracle, controls, and receipt bindings are recorded in
`production-evidence.json` after execution. This lane does not run a model
Agent, blind review, dataset integration, pilot, or publication.
