# Winston Authoring Provenance

## Frozen Source

- Upstream: `https://github.com/winstonjs/winston`
- Revision: `ff0b79de8562bb322c390fbc82fe71c11f373428`
- Revision date: `2026-07-15`
- License: MIT; `source/LICENSE` SHA-256 is
  `e61f2ace04e689d21ba1a7bc54d933bcb6e35ebeb887fb5831b880be5de192a7`.
- Exact archive command: `git archive --format=tar ff0b79de8562bb322c390fbc82fe71c11f373428 | sha256sum`.
- Exact archive SHA-256: `fea87801fd76da125ac8cdb0c29a1026fa8870c0f13552648bea1a4b54a3d282`.
- No submodules.

The frozen upstream Jest suite contains 21 suites, 236 tests including 3
TODOs, and one file-stress suite that is excluded from the bounded task slice.
The non-stress baseline completed 21 suites, 233 passing tests, and 3 TODOs.

## Runtime Remediation

The task uses Node `24.19.0` and npm `11.17.0` from the digest-pinned Debian
Bookworm image in `toolchain.node.lock.toml`. The runtime package was packed
after removing development-only dependencies and lifecycle scripts. Its
private Oracle archive is `winston-3.19.0.tgz` with SHA-256
`374f7e6a1a59b7d9300e0e6f64d234caad65c4aa7598813c939807952de983e2`.

The candidate dependency closure is an npm v3 lock/cache bundle. A clean
staging install with `npm ci --offline --ignore-scripts --no-audit --no-fund`
passed using the retained cache. The private bundle digest is
`sha256:603ce4138f7c02c8a4f610bc6dd6c3ceeff6219afe4064d340fb688b67665e61`.

## Verifier Scope

The private `node:test` adapter freezes 24 leaves for package exports, npm
levels, record emission, JSON/simple/printf/timestamp/error/splat formats,
metadata inheritance, filtering, custom transports, containers, profiling,
configuration, and lifecycle behavior. Tests run in a separate verifier
environment and import the candidate only through the packed candidate site.
File/HTTP transport side effects, process termination, and the upstream stress
suite are outside this deterministic local contract.

Private artifacts:

- commands: `sha256:fda65a1fae7a54d9433921e0c28ac2311ec9dbefc0b8c54efe69c954ad4433f7`
- tests: `sha256:48941be9e66e63994be4b052dc6537387a1edcf1488d531bdf7e5f0e9031af6c`
- Oracle: `sha256:0f7c00a9d0cee6ace869ec35f48455e08bb923a01ff5fb433c4b4339a364db0c`

All private bytes are stored in the worktree-local `.nl2repo/artifacts` CAS;
they are not copied into the public catalog source.
