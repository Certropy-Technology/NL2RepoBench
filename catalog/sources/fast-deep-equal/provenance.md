# `fast-deep-equal` Authoring Provenance

This source record freezes the evidence for a Node/npm production task. Private
Oracle, test, command, and dependency bytes are content-addressed under
`.nl2repo/artifacts`; they are not stored in this public source directory.

## Immutable Source And License

- Upstream: `https://github.com/epoberezkin/fast-deep-equal.git`
- Revision: `a8e7172b6c411ec320d6045fd4afbd2abc1b4bde`
- Tree: `6e99f44c1e415cba716a82029467cfff96ce5e1c`
- Unprefixed archive command: `git archive --format=tar HEAD | sha256sum`
- Archive SHA-256: `bfae19c6df85a382dc13a05ceb6ace92125e9a54e603056f3244b2f842ccf755`
- Archive size: 61,440 bytes; no submodules.
- The root `LICENSE` and `package.json` both declare MIT. `LICENSE` SHA-256:
  `7bf9b2de73a6b356761c948d0e9eeb4be6c1270bd04c79cd489c1e400ffdfc1a`.

The source package is CommonJS (`main: index.js`) but the exact Git tree only
contains `src/index.jst`; its runtime entry files are generated. It commits no
`package-lock.json`, `npm-shrinkwrap.json`, `yarn.lock`, or `pnpm-lock.yaml`.

## Scripts-Stripped Adaptation

The reference was generated in the locked image
`node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
(Node `24.19.0`, npm `11.17.0`) with the explicit authoring-only compiler
`dot@1.1.3`. The generated root `index.js` hash is
`eb469e206280321a3878f2335ec98aa2104a155079d8ed83a23029098dccd215`, matching
the previously observed upstream build output.

The Oracle is a prebuilt adaptation with the upstream runtime JavaScript, a
scripts-free package manifest, an npm v3 zero-dependency lock, MIT license,
and a `.equal` alias pointing to the root callable. It does not fetch source
or execute build/lifecycle scripts at run time. Its root package passes
`npm ci --offline --ignore-scripts` with an empty cache and passes the npm
package validator.

## Bounded JSON Contract

The private `node:test` bundle has 20 fixed leaves and calls the candidate only
through the verifier-owned bounded JSON child process. It covers JSON
primitives, Unicode, arrays, nested objects, object key order, key-set and
value differences, `__proto__`, and observed `constructor` behavior. Values
with own `valueOf` or `toString` keys are excluded because the pinned root
implementation treats those inherited method slots as executable behavior.

The task intentionally excludes cycles, object identity, custom prototypes,
functions, special numbers, typed data, ES6/React entry points, declarations,
and build tooling. This is a documented rescope rather than hidden behavior.

## Private Artifact Closure

- npm v3 dependency bundle:
  `sha256:949eaa861a331f8273258a69eed71002b5b484228045d85cfe7ea4558f9ccf9f`
- command-plan bundle:
  `sha256:e9338437d214111fee4790824bfc08ed1346a2519c1bcb439d53217221ed1040`
- private test bundle:
  `sha256:71a7b368d85c8aea4bf5ec64900e317cb4b815793ed31d7a60e866aeb618d97f`
- scripts-stripped Oracle bundle:
  `sha256:0a878d3dc5bac73a18378cada7fcf709f586053183b0209afa73efd4e69d0a12`

The zero-dependency npm closure contains only a v3 lock and an empty cache;
the transient npm diagnostic log from authoring was removed before packing.
`validate_npm_dependency_bundle(..., expected_npm_version="11.17.0")` passed.
## Production Gate Evidence

The source compiled without `--allow-incomplete` using:

```bash
uv run nl2repo harbor compile catalog/sources/fast-deep-equal \
  --output .nl2repo/runs/fast-deep-equal-network-proof-20260825T071552Z/final/compiled \
  --toolchain toolchain.node.lock.toml \
  --artifact-root .nl2repo/artifacts --allow-private
```

The recompiled production bundle binds toolchain content digest
`sha256:f8dd709ad5723115af52174afa94ad7a80710be83d4fb643b8524a2389d21f92`
and canonical manifest digest
`sha256:b88a3e53e5559076312b9de7df1a60db42512abc30bf4a8ad18b53cd3aecbfca`.

The official Harbor `0.21.0` Oracle command used the locked runner and final
Node toolchain:

```bash
uv run --frozen --project harbor-runner harbor run \
  -p <compiled-task> -a oracle
```

Its result was `valid=true`, `collected=20`, `passed=20`, and reward `1.0`.
The exact job result, verifier reports, and generated network receipt are
hash-bound from `production-evidence.json` to the task-local run directory.

Three derived control bundles changed only `solution/solve.sh` and refreshed
their bundle manifest before the same official Harbor command:

| Control | Result |
| --- | --- |
| empty workspace | `valid=true`, candidate-installation failure, reward `0.0` |
| package stub returning a non-boolean | `valid=true`, 20 failed leaves, reward `0.0` |
| fake workspace `reward.json` and `report.json` | `valid=true`, 20 failed leaves, reward `0.0` |

The control results show that the verifier owns its report/reward paths and
does not consume candidate-written workspace score files. Oracle, empty,
stub, and forgery each generated a verifier-owned `network.json`; all four
receipts record failed probes to `registry.npmjs.org:443` and `1.1.1.1:443`
and `public_network_available=false`. The frozen denominator remains 20. The
task is at `controls-passed`; review, pilot, and publication remain out of
scope.
