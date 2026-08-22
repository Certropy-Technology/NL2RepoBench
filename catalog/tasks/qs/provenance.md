# `qs` Node v2 Authoring Provenance

Status: **specified / development-only**. This task-local directory contains
public v2 metadata, an implementable JSON-compatible CommonJS specification,
and source/build/test evidence only. It is not a Harbor bundle, a private test
package, an Oracle, or a publication approval. No hidden test bytes, npm
cache/tarball bytes, secret, Dockerfile, verifier, or shared dataset file is
stored here.

## Candidate and exact source lock

- Candidate report: `reports/npm-package-candidates.v1.md`.
- Upstream: `https://github.com/ljharb/qs`.
- Requested and resolved revision:
  `3a890d4ecd3deb72a45d90be36f4f8c5970467c7`.
- Revision tree: `0087de81352794a9d68dbcdd1a339336a7f35c63`.
- Commit subject: `[Dev Deps] update \`eslint\`, \`evalmd\``.
- Author and commit timestamp: `2026-07-10T23:16:53-07:00`.
- The checkout was detached at the full SHA and had no submodules. The
  revision is eight commits after tag `v6.15.3`; the package metadata remains
  version `6.15.3`. The source lock is the full commit, not the tag or a
  floating branch.
- Deterministic archive command:
  `git archive --format=tar 3a890d4ecd3deb72a45d90be36f4f8c5970467c7`.
- Unprefixed archive size: `12,011,520` bytes.
- Unprefixed archive SHA-256:
  `f5bb4b5c13cb29aba6441d5781bb17de37b473f74aec203898b28f980ff95402`.

The archive and source files were inspected only under temporary `/tmp`
checkouts. No upstream source or test bytes were copied into this task.

## License evidence

The pinned `package.json` declares `BSD-3-Clause`, and the revision's tracked
`LICENSE.md` contains the BSD 3-Clause license text.

- Path: `LICENSE.md`.
- Size: `1,600` bytes.
- Git blob: `fecf6b6942d17bc7ae41a5e106dc98815c0db652`.
- File SHA-256: `e7dc37bf662d7f786efcb46c545615e70c1daf458a38385521c63cf6607cdfe1`.
- `package.json` Git blob:
  `1657d93ff001ed0b232aebb862c3f26b78abcdd7`.
- `package.json` SHA-256:
  `9f7b246fe9541c844ba3ceca54db57d65fba53e088d49c976e3eb03c151fb9fa`.

The license declaration and file agree. Dependency license review remains a
separate closure step; the diagnostic runtime resolution observed only MIT
packages, but no legal/dependency artifact is claimed here.

## Package, API, and source inventory

The pinned package metadata reports:

- package name `qs`, version `6.15.3`;
- CommonJS entry `main: lib/index.js`; no `type` or `exports` field;
- Node engine `>=0.6` (the task pins the actual runtime to Node `22.23.1`);
- root exports `formats`, `parse`, and `stringify`;
- runtime dependencies `es-define-property: ^1.0.1` and
  `side-channel: ^1.1.1`;
- 32 range/exact development dependencies, including Tape/NYC test tooling,
  Browserify build tooling, lint tooling, and README/publish helpers;
- no upstream `package-lock.json` or `npm-shrinkwrap.json`; `.npmrc` explicitly
  sets `package-lock=false` and `.gitignore` ignores package locks;
- lifecycle/build scripts include `tests-only`, `dist`, `prepack`, `pretest`,
  and a network-capable `posttest` audit.

The tracked implementation inventory is five CommonJS files under `lib/`,
1,207 physical lines in total:

| File | Bytes | Git blob |
| --- | ---: | --- |
| `lib/index.js` | 211 | `0d6a97dcf096449e7100cb63bb05f232a7f790a5` |
| `lib/parse.js` | 16,105 | `0ccb70cd95ccd348d24a6844b461a8358df5109f` |
| `lib/stringify.js` | 12,166 | `a6e23e73644c97dac46ecfb56bc609a9f8d4a82f` |
| `lib/utils.js` | 12,222 | `6fce59003d92051ea937a942ebe7be1a4c57a2a4` |
| `lib/formats.js` | 476 | `f36cf206b90ff764e9709be64d57f6da60b6307e` |

The scored API intentionally narrows the root surface to `parse`, `stringify`,
and the string format constants. Callback-valued formatters and internal
`lib/utils` helpers are not public task APIs.

## JSON-compatible contract review

A child-side JSON adapter can represent the task-local contract without
shipping executable callbacks or JavaScript object handles:

- `parse` receives a query-string string (or JSON `null` for the empty-query
  case) and a JSON object of scalar/string options. String delimiters are
  supported; RegExp delimiters and decoder callbacks are excluded.
- `stringify` receives recursively JSON-compatible nulls, booleans, finite
  numbers, strings, arrays, and plain objects plus JSON options. Array-valued
  `filter` is supported; encoder, date-serializer, filter-callback, formatter,
  and sort-callback options are excluded.
- Buffers, dates, symbols, BigInts, functions, RegExps, sparse-array holes,
  custom prototypes/`toJSON`, and cyclic values are excluded because a JSON
  request/response cannot preserve their identity or behavior. Non-finite
  numbers are excluded; JSON `-0` is accepted only with the upstream numeric
  stringification semantics, not as a separately observable identity.
- The contract preserves the upstream distinction between parse values (text
  strings by default) and stringify output (a query-string string). It does
  not claim lexicographic key sorting: stringify follows JavaScript own-key
  enumeration order for the received JSON object.
- Error observations are JSON-normalized by the future adapter as an error
  class/name and message. Invalid option types are `TypeError`; strict depth
  and configured parameter/array limit failures are `RangeError`.

This is a deliberate task boundary, not a claim of complete upstream parity.
A future private test bundle must select only assertions traceable to this
contract and freeze its own leaf denominator before packaging.

## Upstream test revalidation

The source suite uses Tape/NYC rather than the v2 `node:test` report contract.
The exact test files and their Git blobs are recorded without copying their
contents here:

| Suite | Bytes | Git blob | Direct Tape leaves |
| --- | ---: | --- | ---: |
| `test/parse.js` | 80,338 | `17f30b6adcee299c3f2da4e7d3ac7f47d8ae36db` | 461 |
| `test/stringify.js` | 68,302 | `1990e57419da989d6cefaa6640ac87869ae604e6` | 426 |
| `test/utils.js` | 24,083 | `713b89b42edb98262da5898575e49658290baf70` | 158 |
| `test/empty-keys-cases.js` | 7,698 | `2b1190ef5a4fe07d96e137a062a5eb41c1170e35` | fixture data, no direct leaves |
| **Total** | **180,421** | — | **1,045** |

Using Node `22.23.1` and npm `10.9.8`, a diagnostic network-backed install
with lifecycle scripts disabled completed, then the local test runner was
invoked directly:

```text
node --version                         # v22.23.1
npm --version                          # 10.9.8
npm install --ignore-scripts --no-audit --no-fund   # temporary diagnostic cache only
./node_modules/.bin/tape 'test/**/*.js'               # 1045 pass, 0 fail
npm run tests-only                                    # 1045 pass; NYC coverage emitted
```

The direct TAP stream was byte-identical across three independent invocations:

- leaf plan: `1..1045`;
- pass count: `1045`;
- fail count: `0`;
- direct TAP SHA-256 on each run:
  `cabe2c0a4dae5f62accfc804a68cd0545babdfb9d813ce4253bc336f96de02dd`.
- The stream contains two `# SKIP TODO` assertions and feature-gated skip
  branches. They did not reduce the direct Tape summary, but a future
  `node:test` adapter must preserve an explicit todo/skipped status policy
  instead of silently treating those lines as ordinary passes.

The `npm run tests-only` output reported 100% statements, functions, and
lines, with 99.85% branches. Its complete output includes coverage paths and
is not treated as a frozen v2 report. The task TOML records 1,045 as a
development source observation only; a private JSON-adapted `node:test`
suite may use a narrower denominator and must version that change.

Static checks also passed for all nine tracked JavaScript files:

```text
node --check lib/*.js test/*.js
CommonJS root require: qs.parse and qs.stringify are callable
```

No Docker, Harbor, Oracle, hidden-test, negative-control, or trusted-process
candidate run was performed.

## Build and package review

The scored library entry does not need the browser bundle, and the task
instruction explicitly excludes `dist/qs.js` and publish/lint hooks. This is
necessary because the upstream Browserify build is not byte-deterministic in
the observed environment:

- tracked source `dist/qs.js`: 53,175 bytes,
  SHA-256 `d138d8ca2c999d5c729fa9a29ec1efc6b54f60c45c9a08602e67b44fb4f1bc1b`;
- repeated `npm run dist` invocations in the same detached checkout produced
  different 53,431-byte outputs with hashes:
  `97c7e1ddc272dd81a0b688f89ddb3dbfe1a317826e182379c03e1b4c7a38a3e0`,
  `623619194f4617711595da000cda55c7297fbf029fe8c153519a43e61029cb33`,
  `44b3ac3571d90c1597937d7d052ffd1806310cf3fc14e7e16369ec3b553dd82d`, and
  `0fc050a605165b7bee4745ea57a9decc0ca146aaf88b277a245121c904125735`.

`npm pack --ignore-scripts` is the safe production-shaped packaging mode;
it does not execute the upstream `prepack` script. In a detached Git checkout,
`npm pack` with scripts enabled generated a 20-entry, 73,944-byte package after
running `npmignore --auto` and `npm run dist`, but the same prepack command in
a source copy without Git metadata failed because `npmignore --auto` requires
`.npmignore` to be Git-ignored. The task therefore requires a working CommonJS
`main` entry and ignores the prepack/browser-bundle path rather than claiming a
reproducible build artifact.

## Dependency closure evidence and gap

The exact source has no committed lock or offline cache. A diagnostic npm
10.9.8 resolution was performed in a temporary network-backed cache only; it
is not an approved dependency bundle and its bytes are not committed.

Runtime-only diagnostic resolution:

- generated v3 lock: 19 package entries including the root;
- root runtime dependency graph: 18 packages;
- all 18 observed runtime packages resolved from the npm registry with
  integrity fields and MIT metadata;
- generated runtime-only lock SHA-256:
  `eac2d826d96e8b18ea2e98c91c55791dc46074385bff3757878d3134100559de`;
- an offline `npm ci --ignore-scripts --no-audit --no-fund` succeeded when the
  temporary cache was populated and failed closed with `ENOTCACHED` when an
  empty temporary cache was used.

Full development-tool resolution was much larger and unsuitable as a
candidate runtime closure:

- generated v3 lock: 934 package entries including the root;
- 32 declared development dependencies;
- 182 legacy nested entries lacked integrity fields in the diagnostic lock,
  mostly under `nyc`'s old dependency tree;
- `npm ci --offline --ignore-scripts` succeeded only with the temporary
  network-populated cache and generated lock.

The task keeps `[dependencies].status = "unknown"` intentionally. Before
production packaging, create a reviewed content-addressed runtime lock/cache
artifact, verify every member/integrity/license/registry URL, and let the
verifier consume it with exact npm `10.9.8`. A network install is evidence that
resolution is possible, not proof of offline reproducibility.

## Explicit posttest exclusion

The source `package.json` defines:

```text
"posttest": "npx npm@'>=10.2' audit --production"
```

This is network-capable and outside the authoring contract. The audit did **not**
run `npm test`, `npm audit`, `npx npm ... audit`, or any posttest hook. It ran
only the local `tests-only` command and a direct local Tape invocation after a
temporary diagnostic install. No audit result is inferred or reported.

## Production gate and recommendation

Keep `qs` at **specified / development-only**. The source revision, BSD license,
CommonJS entry, JSON-compatible parse/stringify boundary, and deterministic
source test observation are coherent. It is not publishable yet. Reopen the
production path only after:

1. a private `node:test` adapter selects and traces JSON-compatible upstream
   behavior, including exact error/result normalization, and freezes a leaf
   denominator;
2. a content-addressed npm v3 runtime lock/cache closure is reviewed; the
   diagnostic network resolution above must not be promoted by hash alone;
3. the verifier runs candidate code only through the bounded JSON subprocess
   boundary and keeps hidden tests/report/reward paths trusted and isolated;
4. the no-network verifier, forged-report, install-script, loader, hang, empty,
   and stub controls pass; and
5. three independent valid Oracle runs have stable collection and reward at
   least `0.80`.

The task remains in the separate Node pilot and must not be added to the Python
dataset or used for a cross-language parity claim.
