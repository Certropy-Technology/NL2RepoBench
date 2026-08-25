# `uuid` Authoring Audit

Status: **controls-passed / pre-review**.

This task-local directory contains the public task source and hash-bound
production evidence needed for authoring review. The generated Harbor bundle
is under `catalog/tasks/uuid/`; private artifact bytes remain in the
content-addressed artifact store and are not duplicated here. This record is
not a review, pilot, or publication approval.

## Candidate And Source Lock

- Candidate: `uuid` from `https://github.com/uuidjs/uuid`.
- Frozen revision:
  `fd59f0277549d22cc7ec00a7b3b5c9bccb4d3c1d`.
- Revision tree: `a89bd2806358a426dfabb4996cca7f1d3b301543`.
- Tag: `v14.0.2` points to the frozen commit; package version is `14.0.2`.
- Commit subject: `chore(main): release 14.0.2 (#967)`.
- Commit timestamp: `2026-08-18T08:19:07-10:00` for both author and committer.
- The source was cloned into an isolated temporary checkout, detached at the
  full SHA, and had no submodules or local modifications.
- Archive command: `git archive --format=tar HEAD | sha256sum` from the
  detached checkout.
- Unprefixed archive size: `808,960` bytes.
- Unprefixed archive SHA-256:
  `fbf7e9c3a1bd5132ab04286855533c2b5f1607c1f97e1878cd568c41d58bdda8`.

The archive digest in `task.toml` is the source lock. No source file is copied
into this task directory.

## License Evidence

The pinned `package.json` declares `"license": "MIT"`, and the tracked root
`LICENSE.md` contains the MIT License text.

- `LICENSE.md` size: `1,109` bytes.
- `LICENSE.md` Git blob:
  `3934168364063216aa8805f06e3a1a8605133d68`.
- `LICENSE.md` SHA-256:
  `beaa6b04fb82e41dd2ad679e19e27953afb5999b1abbb455b6564e78ebfeb332`.
- `package.json` Git blob:
  `b571536d169d24d6004478388a38887da9de2e78`.
- `package.json` SHA-256:
  `f7478df6f4ddaffacba855e97974626c264a0d022c02e4bcc1cdbc8471cbc6ee`.

This is a source-license check. License review for any future dependency
closure remains a separate gate.

## Package And Source Inventory

The pinned package metadata reports:

- name `uuid`, version `14.0.2`, description `RFC9562 UUIDs`, and
  `type: module`;
- no runtime `dependencies` and no `engines` field;
- `sideEffects: false`, `files: ["dist", "dist-node", "!**/test"]`, and a
  package-manager declaration of `npm@11.12.1`;
- a `uuid` CLI under `dist-node/bin/uuid`, which is outside the scored API;
- 17 exact `devDependencies` and 6 exact optional development dependencies;
- build, prepare, prepack, browser, documentation, lint, release, and example
  scripts. These are source-development paths, not candidate runtime
  requirements. Production installation and verification use
  `--ignore-scripts` and a verifier-owned build/package policy.

The source-only TypeScript inventory is:

- 24 tracked non-test files under `src/`;
- 1,344 physical lines and 1,146 nonblank lines across those files;
- 1,224 physical lines and 1,051 nonblank lines after excluding the type-only
  `src/types.ts` and CLI `src/uuid-bin.ts` files;
- 11 tracked `src/test/*.ts` files with 1,540 physical lines.

The source-only count excludes all tests, examples, generated `dist` trees,
package metadata, lockfiles, documentation, and workflow files. The type-only
and CLI-inclusive count is the conservative source LOC recorded for the
candidate; the implementation-only count is supplied to make the boundary
auditable.

## Node 22 Runtime And Exports

The probe used Node `v22.23.1`, npm `10.9.8`, `linux/amd64`, glibc, and the
development Node image lock from `toolchain.node.lock.toml`:

```text
docker.io/library/node@sha256:8607a9064d4a571140998ae9e52a3b3fcf9cff361d04642d5971e6cd76d39e27
```

The pinned package export is ESM and has two root branches:

```json
{
  ".": {
    "node": {
      "types": "./dist/index.d.ts",
      "default": "./dist-node/index.js"
    },
    "default": "./dist/index.js"
  },
  "./package.json": "./package.json"
}
```

After `npm run build -- --no-pack`, importing the package root on Node
`22.23.1` exposed these 14 named exports:

```text
MAX NIL parse stringify v1 v1ToV6 v3 v4 v5 v6 v6ToV1 v7 validate version
```

The probe also verified `NIL`, `MAX`, the DNS/URL namespace constants, v3/v5
known values, v4 deterministic bit masking, v7 RFC-style option output,
parse/stringify byte round-tripping, and version/validation results. The
browser fallback and CLI were inventoried but not scored.

## Official Tests And Build Probe

The pinned source uses the official `node:test` runner. The exact test command
was run three times after a clean install:

```bash
npm test -- --test-reporter=tap
```

`npm test` invokes the upstream `pretest` build first, so the probe also
verified the checked-in TypeScript build path. Every run reported:

```text
# tests 82
# suites 10
# pass 82
# fail 0
# cancelled 0
# skipped 0
# todo 0
```

The 82 count is the observed official leaf-test denominator: 11 test files,
10 suites, and 82 passing leaves. The pass/fail and collection counts were
stable across all three runs. Duration fields varied, so no byte-for-byte TAP
hash is treated as deterministic evidence.

The test modules and observed leaf counts are:

```text
src/test/parse.test.ts       5
src/test/rng.test.ts         1
src/test/stringify.test.ts   4
src/test/v1.test.ts         13
src/test/v35.test.ts        21
src/test/v4.test.ts         10
src/test/v6.test.ts         10
src/test/v7.test.ts         15
src/test/validate.test.ts    1
src/test/version.test.ts     1
src/test/test_constants.ts   0 (loaded by tests, no suite)
```

The separate tracked `test/browser/browser.spec.js` suite uses a browser
webdriver configuration and was not run. Browser behavior is outside the
Node-only JSON contract.

Those source-development probes predate the production task. Fresh production
Harbor Oracle and negative-control results are recorded in
`production-evidence.json`; they preserve the frozen 11-leaf private contract
rather than replacing it with the 82-leaf upstream development suite.

## Lockfile And Offline Closure

The exact source commits `package-lock.json` with lockfile version `3`:

- lockfile size: `478,764` bytes;
- lockfile SHA-256:
  `b9875ca19d381c7beecdbc16e28d641ca44e80cd2dae6d3500ec7646f8b7c1ac`;
- 947 `packages` entries including the root and 946 non-root entries;
- all 946 non-root entries resolved from the npm registry and include
  integrity fields;
- 47 entries are optional and 3 dependency entries declare install scripts.

The lock above is the upstream development dependency graph and is not the
production candidate-runtime lock. A temporary npm 10.9.8 cache was used only
as an early evidence probe:

```text
npm ci --ignore-scripts --no-audit --no-fund       passed with the temporary cache
npm ci --offline --ignore-scripts --no-audit --no-fund  passed with that cache
npm ci --offline --ignore-scripts --no-audit --no-fund  failed with an empty cache
```

The empty-cache failure was closed with `ENOTCACHED` for
`yocto-queue@0.1.0`. Production does not install that development graph. The
candidate runtime is dependency-free and now uses an immutable npm v3 lock
plus an empty cache closure, installed offline with npm `11.17.0` and
`--ignore-scripts`. The content-addressed dependency artifact and exact Node
`24.19.0`/npm `11.17.0` toolchain are declared in `task.toml`.

## Crypto, Time, And Randomness Policy

The pinned source obtains default random bytes through Web Crypto
`crypto.getRandomValues()`. `v4()` uses `crypto.randomUUID()` when called with
no options and falls back to the byte path when options are supplied. `v1`,
`v6`, and `v7` use secure random bytes and current time when their options do
not fully specify deterministic inputs; v1/v7 also maintain upstream
process-local monotonic state in those default paths.

The public instruction therefore separates deterministic and nondeterministic
assertions:

- v3 and v5 are exact deterministic name/namespace functions;
- v4 uses a supplied 16-byte `random_hex` value for exact tests;
- v1/v6 use explicit time, sequence/node, and random fields as needed;
- v7 uses explicit `msecs`, `seq`, and `random_hex` for exact tests;
- default v1/v4/v6/v7 tests assert only format, version, variant, documented
  ordering, or bounded non-equality, never a fixed random or wall-clock value.

The candidate must not replace cryptographic randomness with `Math.random`, a
fixed seed, host identity, or network input. Callback `rng` injection and
direct typed-array identity are upstream test surfaces but are excluded from
the JSON boundary.

## JSON-Safe Generate/Parse/Validate Boundary

The public API remains the upstream ESM API. A future verifier-owned child
adapter maps bounded JSON requests to named exports and maps results back to
JSON; the candidate must not add a server or CLI for this purpose.

The task instruction defines these operations:

| Operation | JSON request | JSON result |
| --- | --- | --- |
| `generate` v1/v4/v6/v7 | version plus finite-number/string options | UUID string |
| `generate` v3/v5 | name string plus namespace UUID string | UUID string |
| `parse` | UUID string | `bytes_hex`, exactly 32 lowercase hex digits |
| `stringify` | `bytes_hex`, exactly 32 hex digits | lowercase UUID string |
| `validate` | JSON value, normally string | boolean |
| `version` | UUID string | number |
| `v1ToV6`/`v6ToV1` | UUID string | UUID string |

The adapter converts hexadecimal byte fields to fresh `Uint8Array` instances
and converts returned byte arrays back to `bytes_hex`. Successful values must
not expose `Uint8Array`, `Buffer`, functions, `BigInt`, `Date`, or object
handles. Error responses carry an exception name and message, preserving
observable `TypeError` versus `RangeError` versus ordinary `Error` behavior.
Requests, responses, child CPU/time, and stateful probes must be bounded.

The JSON subset excludes callbacks, direct typed arrays, buffers, symbols,
functions, BigInts, dates, regular expressions, custom classes, cyclic values,
and non-finite numbers. This is an explicit transport boundary, not a claim
of complete in-process upstream parity. In particular, upstream tests that
mock `crypto`, inspect mutable buffers, or call private state helpers require
a task-specific private adapter and are not copied into this public directory.

## Production Terminalization

The production Node compiler was run with `toolchain.node.lock.toml`, private
artifact authorization, and without `--allow-incomplete`. The source digest,
public instruction, private assertions, and frozen denominator of 11 were not
changed. Official Harbor `0.21.0` then produced fresh task-local receipts for:

- Oracle: valid, 11 collected, 11 passed, reward `1.0`;
- empty workspace: valid model-zero with installation failure, reward `0.0`;
- importable stub: valid, 11 collected, 0 passed, reward `0.0`;
- forged workspace test/reward files: valid, 11 collected, 0 passed, verifier
  reward `0.0`;
- all four verifier runs: `network.json` present, both registry-host and
  numeric-address probes unavailable, and `public_network_available=false`.

The exact paths and SHA-256 digests are in `production-evidence.json` and the
task-local `evidence/` summaries. The lifecycle stops at `controls-passed`.
Blind review, traceability review, pilot execution, dataset integration, and
publication were not performed and remain separate gates.
