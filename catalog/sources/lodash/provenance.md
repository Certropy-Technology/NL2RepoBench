# `lodash` Node v2 Authoring Provenance

## Immutable source and license

- Upstream: `https://github.com/lodash/lodash`.
- Revision: `a666ba591064c8011988275790ad7d625279f09c`.
- Tree: `db33bf300e327a383356d4187e7608df93242969`.
- Commit timestamp: `2026-07-03T15:48:01-04:00`.
- Commit subject: `docs: fix some minor docs inconsistencies (#6249)`.
- Unprefixed `git archive --format=tar` size: 4,771,840 bytes.
- Source archive SHA-256:
  `4b815834ee052cbd62e39ae63019905344135368cd48f0dfcbbcaf7635e3ec9a`.
- Submodules: none.
- Root `package.json` declares package `lodash`, version `4.18.1`, main
  `lodash.js`, Node `>=4`, and MIT.
- Root `LICENSE` SHA-256:
  `f71e8ed126b46346494aad5486874cd8f0aafe95092ed67d2e3cb6110f939abc`.
- Frozen `lodash.js` SHA-256:
  `9bd765def21a6704a6d7e54ecf76004811ba7df19b387b60e04740785794e376`.

The detached checkout and all large working material are under
`.nl2repo/authoring-work/node-author-wide-20260826-remediation/lodash/`.

## Locked upstream baseline

The exact source was tested in
`docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
(Node `24.19.0`, npm `11.17.0`). `npm ci --ignore-scripts` installed the
legacy development lock successfully. `npm test` rebuilt the main and FP
distributions, then passed 6,831 main assertions and 327 FP assertions with no
failures. Logs are retained in task-local `evidence/logs/`.

The committed upstream lock is npm lockfile v1 and covers the historical build
and test toolchain. It is not promoted into the scored candidate environment.

## Static and bounded inventories

The repository has 160 tracked files and 119,147 physical JavaScript lines
under the broad checkout accounting used during freeze. The isolated static
Node inventory scanned 34,076 implementation lines and 30,173 test lines,
reported 841 public symbols, no syntax diagnostics, and a generated/dynamic
surface. Its 960,904-byte raw result has SHA-256
`e968f6db2fd553dd3e5a44c2afaecf7ccc376eaf2767fa379c6539baf6dfd4c1`
and remains in task-local authoring work.

The built CommonJS root has 308 enumerable properties. The scored task selects
71 deterministic callables that accept and return bounded JSON values. It
excludes callbacks, executable iteratees, non-JSON values, wrappers, lazy
chains, templates, mixins, FP entry points, per-method modules, and browser/CLI
behavior. `api-inventory.json` and `instruction.md` define the exact slice.

## Production adaptation and closure

The scored package has no dependencies or build step. Its scripts-free Oracle
contains the exact frozen source archive, verifies the archive and `lodash.js`
digests, validates upstream package identity/license, and materializes only
`lodash.js`, `LICENSE`, a scripts-free package manifest, and a matching npm v3
root lock. A direct locked-runtime baseline collected and passed all 63 private
leaves in 8.99 seconds.

The private dependency artifact is a validated zero-entry npm cache plus an npm
11.17.0 v3 root lock. Candidate and verifier phases require no registry access.
The task-specific adapter imports only package `lodash`, accepts only the 71
documented method names, bounds JSON request/response sizes, and executes each
call as UID 10001 in a fresh subprocess.

Private content-addressed artifacts:

- npm v3 lock/cache:
  `sha256:0518ee80b4df32f3e5ceff4095154a9eea283650152fa9cc5b55f2ea90432b03`
  (10,240 bytes);
- command declaration:
  `sha256:a832562812d78324c3ac1b16a15a9ab97c6e9e92ad7de119f2da7bb997be8661`
  (10,240 bytes);
- private test/adapter bundle:
  `sha256:0bfac49f72b66befde0675f872b39095596a8f7273bff05f3edef58ca2302b4c`
  (20,480 bytes); and
- digest-verified Oracle source/distribution bundle:
  `sha256:a2e7311466ffb7e3ed6774bb8ade582d984ba6293d571f059f3109cfd2d2168c`
  (4,782,080 bytes).

## Network and handoff boundary

The source declares `mode=no-network`, an empty Agent allowlist, and
`reference_source_fetch=forbidden`. No source or provider host is stored in task
metadata. The model Agent never receives the Oracle archive, private tests, or
verifier adapter. This lane does not start a model Agent Run and does not add
the task to a shared dataset.

## Harbor gate outcome

The production compiler resolved all private artifacts. Harbor `0.21.0` then
reported Oracle `63/63`, reward `1.0`; empty reward `0`; installable stub and
forgery `1/63`; and `public_network_available=false` in every official network
receipt. The forged workspace reward did not affect trusted grading.

Two official timeout-control attempts were invalidated by concurrent host
pressure before candidate installation: npm could not create a thread because
all authoring containers share UID 10001 while the verifier imposes
`RLIMIT_NPROC=32`. A locked-image direct probe using task-local UID 11063
separated that infrastructure condition from task behavior: it collected all
63 leaves, terminated the five-second hanging call, and completed with 1 pass
and 62 failures in 13.7 seconds. Exact receipts and failure logs are bound in
`production-evidence.json`.
