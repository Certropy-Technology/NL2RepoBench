# `lines-and-columns` Authoring Provenance

## Frozen source

- Upstream: `https://github.com/eventualbuddha/lines-and-columns`
- Revision: `eea2581b131685f2c21de777fd037c8ddd343354`
- License: MIT; `LICENSE` SHA-256:
  `456fe85ad3e71db9523313cf7437b0f90c392d8a48c869908e46716b26d2cf53`.
- Exact archive command: `git archive --format=tar <revision> | sha256sum`.
- Exact archive SHA-256:
  `ecd2011652df85d6d95d08e80d8d1d2ce06ac5dfcc9aca7ef3f28eace03c01f9`.
- No submodules.
- License file SHA-256:
  `456fe85ad3e71db9523313cf7437b0f90c392d8a48c869908e46716b26d2cf53`.

The frozen package declares `lines-and-columns@0.0.0-dev`, uses TypeScript
source at `src/index.ts`, and has no runtime dependencies. The upstream Jest
baseline was run after an npm 10.9.8 remediation install: `npm run build` and
14/14 Jest tests passed. The frozen pnpm lock is incompatible with host pnpm
10.33.0, so that development-only chain is not copied into the candidate
contract; the scored task uses a clean zero-dependency npm package.

## Remediation and closure

The upstream revision has no npm v3 lockfile and its Jest/TypeScript development
chain is not needed for the bounded runtime contract. The task therefore uses
an exact empty npm v3 lock/cache bundle. `npm ci` and `npm pack` run with
scripts disabled; candidate and verifier execution remain offline. The private
dependency archive is `sha256:beddb6b453f8315cf2ea08b237ff6dd4bef26cc0c60e610acf1e17c9a807a887`
(10,240 bytes).

## Verifier boundary

The private `node:test` adapter invokes only the named class constructor and
the two documented methods in an unprivileged child process. Requests are
JSON-shaped and bounded. Trusted verifier code never imports candidate code
directly, and it owns the report, fixed denominator, and reward. The final
private test bundle is
`sha256:aa28d8707fda2c6e9667acbd4529610dd78116234c062a91877b41bc3a3d0a71`
(10,240 bytes). Its two package-inventory leaves assert effective UID and GID
`10001`, so the Oracle result proves that candidate imports do not run as the
trusted root verifier.
