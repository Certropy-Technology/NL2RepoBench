# `semver` Fast Blocked Audit

Status: **blocked / audit-only**.

This file records source and boundary evidence for the exact `npm/node-semver`
candidate. It is not a task instruction, Harbor bundle, private test package,
verifier, grader, Oracle result, or publication approval. No upstream source,
TAP output, npm cache, generated lockfile, secret, or shared dataset asset is
stored here. The only requested durable change is this file.

## Candidate And Source Lock

- Package: `semver` from `https://github.com/npm/node-semver`.
- Requested and frozen revision:
  `6e05b7637396ac66522cff8731f07cfe0ef49a29`.
- Revision tree:
  `9b60d2f8e9fcfb506797bcd77d703541442c11b8`.
- Parent:
  `9c8692ae05416e9dbe88d95ffe2b80e6964550fe`.
- Tag/release subject: `chore: release 7.8.5 (#879)`.
- Package version: `7.8.5`.
- Commit author and committer date: `2026-06-19T11:28:50-07:00`.
- The detached checkout had no submodules and was clean after inspection.
- `git archive --format=tar HEAD` produced 440,320 bytes and SHA-256
  `b4c4f3682bbb55f07c8125c3eecc648e75b9c378171b510dd150fa30bead6e07`.
  The frozen tree contains 154 tracked files. The archive is provenance
  evidence only and is not copied into this directory.

## ISC License Evidence

The frozen `package.json` declares `"license": "ISC"`; the tracked root
`LICENSE` contains the ISC grant and warranty disclaimer.

- `LICENSE` size: 765 bytes.
- `LICENSE` Git blob:
  `19129e315fe593965a2fdd50ec0d1253bcbd2ece`.
- `LICENSE` SHA-256:
  `4ec3d4c66cd87f5c8d8ad911b10f99bf27cb00cdfcff82621956e379186b016b`.
- `package.json` Git blob:
  `0cb7c7bb465ea49c8daff8e87350513843f89c89`.
- `package.json` SHA-256:
  `7c94cb7f2a53c27b20d76386ec144c062894dbcc909cfabd0f728c37874b1776`.

This is source-license evidence. A future development dependency closure
still needs its own license and provenance review.

## Package Shape And Runtime Scope

The frozen manifest reports:

- name `semver`, version `7.8.5`, and description `The semantic version parser
  used by npm`;
- CommonJS `main: "index.js"`, with no `type` field and no `exports` map;
- Node engine `>=10` (Node `22.23.1` is a task-level runtime lock, not a
  stronger upstream compatibility claim);
- no `dependencies`, `optionalDependencies`, or `peerDependencies`;
- development dependencies `@npmcli/eslint-config ^7.0.0`,
  `@npmcli/template-oss 5.0.0`, `benchmark ^2.1.4`, and `tap ^16.0.0`;
- the `semver` executable at `bin/semver.js`; and
- a `files` allow-list for `bin/`, `lib/`, `classes/`, `functions/`,
  `internal/`, `ranges/`, `index.js`, `preload.js`, and `range.bnf`.

The reachable runtime code uses relative CommonJS imports only. No third-party
runtime import, native addon, network client, filesystem dependency, or
subprocess dependency was found in the root/classes/functions/internal/ranges
runtime graph. The runtime implementation is therefore a **zero-runtime-
dependency** candidate. The development/test graph is materially larger and
must not be confused with that runtime scope.

The package dry-run under npm `10.9.8` listed 53 files with an unpacked size of
101,065 bytes. The manifest still lists `lib/`, but the frozen tree has no
`lib/` directory and the dry-run has no `lib/` files. This packaging mismatch
is an explicit gate for any future task artifact; it is not silently repaired
by this audit.

## Node 22 CJS And Deep Exports

The probes used Node `v22.23.1` and npm `10.9.8` on the local Linux host. The
package has no `exports` map, so CommonJS package resolution permits the root
and available deep paths rather than enforcing a subpath allow-list.

Loading the package through a temporary `node_modules/semver` link succeeded
for:

```text
semver
semver/package.json
semver/classes
semver/classes/semver
semver/functions/parse
semver/functions/compare
semver/functions/valid
semver/ranges/valid
semver/internal/re
semver/preload
```

The root namespace exposes the public functions and constructors including
`parse`, `valid`, `compare`, `compareBuild`, `SemVer`, `Range`, `Comparator`,
range helpers, sorting helpers, and the identifier/regex constants. Deep
imports also expose implementation details such as `internal/re` and
`package.json`; those are not automatically public task APIs. `semver/lib/index`
fails because `lib/` is absent from the frozen tree.

Any future contract must explicitly allow-list the root operations and selected
deep paths. It must not score arbitrary deep imports, internal regex objects,
mutable class instances, or package metadata merely because this legacy
CommonJS layout makes them resolvable.

## TAP Test Evidence

The official manifest declares:

```text
npm test  -> tap
posttest  -> npm run lint
```

The TAP configuration sets a 30-second timeout, uses `map.js` as its coverage
map, and excludes `tap-snapshots/**` from the nyc coverage argument. Static
inventory of the frozen tree found:

- 66 tracked JavaScript files below `test/`;
- 51 test files importing `tap`;
- 15 fixture files and the remaining integration, class, function, internal,
  index, map, preload, range, and CLI test modules; and
- 118 direct `test(`/`t.test(` declaration lines. This is only a source
  inventory, not a TAP leaf denominator.

The official command was **not run** in this fast blocked audit. No installed
TAP baseline, structured collection report, stable leaf IDs, or frozen test
denominator is available. `posttest` also invokes the lint/tooling closure,
so a later verifier must pin and explicitly control whether lint is part of
the score. Do not use the static 118-line count as a score denominator.

## npm Lock And Offline Closure

The exact source commits no `package-lock.json` or `npm-shrinkwrap.json`, and
`.npmrc` contains:

```text
package-lock=false
```

The runtime graph has no dependency roots, so a future runtime-only package can
likely use a root-only lock. That does not close the official TAP/lint test
graph: the four development roots expand to a substantial transitive tree,
and the manifest has lifecycle scripts.

For diagnostic evidence only, npm `10.9.8` generated a disposable lock with
the source manifest, `--package-lock=true`, `--ignore-scripts`, and `--offline`:

- lockfile version 3;
- 933 `packages` entries including the root;
- lock SHA-256
  `9bc79890e22e5be39dee2980b13df82e85022fe792abb5b9fed8be1bacce0d6a`;
- install-script metadata for `@npmcli/template-oss` and `fsevents`.

The generated file was deleted. A subsequent disposable
`npm ci --offline --ignore-scripts --no-audit --no-fund` failed closed before
installation because the package manifest and generated lock were not in
sync (`conventional-commits-filter@3.0.0` in the lock versus `5.0.0` required
by the manifest's resolved tree). This is evidence that no reviewed,
reproducible offline development closure exists; it is not an Oracle or model
failure. No cache or generated lock is retained in the catalog.

Therefore the dependency gate remains **unknown**. Before packaging, authoring
must produce a content-addressed npm v3 lock/cache closure for the selected
runtime and test policy, verify every integrity/license/provenance record,
decide the `ignore-scripts` policy, and prove clean offline installation in
the final Node 22 image. The runtime's zero-dependency observation does not
waive the test-tool closure gate.

## JSON-Safe Parse/Compare/Valid Boundary

The narrow candidate boundary should expose only bounded JSON requests to a
separate Node child process. The candidate itself should not add a server or
CLI for this protocol.

| Operation | JSON request | JSON result |
| --- | --- | --- |
| `parse` | `{ "version": string, "loose": boolean? }` | `null`, or a plain object with normalized `version`, integer `major`/`minor`/`patch`, and string/number arrays `prerelease` and `build` |
| `compare` | `{ "a": string, "b": string, "loose": boolean? }` | exactly `-1`, `0`, or `1` |
| `valid` | `{ "version": string, "loose": boolean? }` | normalized version string or `null` |

The adapter must accept only bounded strings for version operands and an
optional boolean `loose` flag. It must reject arrays, objects, functions,
symbols, BigInts, dates, regular expressions, cyclic values, non-finite
numbers, and unbounded input. Returned `SemVer` instances must be projected to
plain JSON; no class identity, prototype, method, regex, or mutable object is
part of the boundary. Error responses should be bounded JSON such as
`{ "error": { "name": "TypeError", "message": "..." } }` and must be
written by the verifier-owned adapter, not by the candidate.

Observed Node 22 results from the frozen source were:

```json
{"operation":"valid","input":"v1.2.3","result":"1.2.3"}
{"operation":"valid","input":"1.2","result":null}
{"operation":"compare","a":"1.2.3","b":"1.2.4","result":-1}
{"operation":"parse","input":"1.2.3-beta.2+build.7","result":{"version":"1.2.3-beta.2","major":1,"minor":2,"patch":3,"prerelease":["beta",2],"build":["build","7"]}}
```

`valid(123)` returns `null` upstream, while `compare("1.2", "1.2.3")`
throws `TypeError: Invalid Version: 1.2`. The public JSON contract should keep
non-string inputs out of scoring and preserve only a reviewed typed-error
projection. Strict versus loose parsing must be explicit: for example,
`valid("4.2.0foo", true)` returns `"4.2.0-foo"`, while the strict form is
invalid. Build metadata is preserved by `parse`/`valid` normalization but does
not affect ordinary `compare` ordering; `compareBuild` is outside this narrow
three-operation boundary unless separately specified.

## Unknown Gates And Reopen Conditions

The following gates are intentionally unresolved:

1. **Environment:** no digest-pinned Node 22 OS/image and npm toolchain record
   is attached to this task-local audit.
2. **Dependency closure:** no committed lock exists; the disposable development
   lock did not pass offline `npm ci`; no reviewed cache/tarball closure exists.
3. **Packaging:** the manifest's `lib/` allow-list does not match the frozen
   source tree, and lifecycle scripts have not been policy-reviewed for a
   candidate package.
4. **Tests:** the TAP suite was not run; no private JSON adapter, collection
   report, frozen denominator, or test-to-contract trace exists.
5. **Verifier:** no separate verifier, report writer, hidden tests, Oracle,
   empty/stub/forgery/install-script/loader/hang/offline controls, or three-run
   stability evidence exists.
6. **Review:** no blind review or bidirectional specification traceability has
   been completed.

Reopen only after the exact source lock, selected JSON boundary, package
projection, immutable environment, offline closure, private TAP adapter, and
separate-verifier controls are reviewed. This candidate must remain blocked;
this file does not authorize a task directory beyond the audit record.

## Validation Record

Completed read-only or disposable checks:

- detached checkout and full-SHA/tree/parent/package-version inspection;
- repeated source archive hashing and license/package hashing;
- Node 22 CommonJS root and deep-path loading probes;
- JSON-safe `parse`, `compare`, and `valid` behavior probes;
- npm pack dry-run inventory with scripts ignored; and
- disposable npm v3 lock generation and offline `npm ci` failure capture.

Not run by design: official `npm test`, Harbor commands, private/hidden test
authoring, Oracle, negative controls, publication, or shared catalog/index
updates. No file other than this audit was requested or changed.
