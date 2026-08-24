# `query-string` Node v2 authoring audit — blocked

**Status: blocked.** This is a development-only authoring evidence record, not a
Harbor task or a production dataset entry. It contains no hidden tests, private
bytes, dependency cache, Oracle solution, Docker artifact, credentials, or
shared-index changes.

## Candidate lock and license evidence

- Package: `query-string`
- Upstream: <https://github.com/sindresorhus/query-string>
- Frozen revision: `aae373a54526c7b297f60e4d7b77eb0709d2ae9c`
- Commit subject: `9.5.0`
- Commit timestamp: `2026-08-06T19:04:10+02:00`
- Commit tree: `12b0d49165b2e1a09f58510ac121147bbf7f9dde`
- Detached checkout was clean; the tree contains 23 tracked files and 4,269
  physical lines.
- `git archive --format=tar HEAD | sha256sum` (repeated three times):
  `12cb02c8cb732a9baf76a8799c452529b1e0a7506dc250161bc5021102d1f8fb`.
- `license` is the MIT license, 1,117 bytes, SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- `package.json` SHA-256:
  `3b42454731e8600a46f849b4a04ac930a128c555c71d4f447d772d8b3deb94fa`.

The source lock is suitable for a further authoring attempt, but it is not an
approval to publish or to claim upstream/package parity through the current
Node verifier.

## Runtime and package inventory

The pinned package is ESM (`package.json:13`) and declares Node `>=18`
(`package.json:19-20`). Its package export is only a default condition pointing
to `./index.js` (`package.json:14-17`). `index.js:1-3` imports the namespace
from `base.js` and exports that namespace as the default:

```js
import * as queryString from './base.js';
export default queryString;
```

`base.js` defines the desired library functions (`parse` at lines 369-460 and
`stringify` at lines 462-540), but they are **properties of the default
namespace object**, not direct package exports. The installed package resolves
as:

```text
namespace keys: ["default"]
default type: object
default keys: ["exclude","extract","parse","parseUrl","pick","stringify","stringifyUrl"]
direct parse type: undefined
direct stringify type: undefined
```

The package has three runtime dependencies (`decode-uri-component`,
`filter-obj`, `split-on-first`) and six development dependencies (`ava`,
`benchmark`, `deep-equal`, `fast-check`, `tsd`, `xo`) in `package.json:48-59`.
The upstream tree deliberately contains `.npmrc` with `package-lock=false`
(`.npmrc:1`) and has no committed npm lockfile.

## Blocking findings

### Blocker — current JSON subprocess boundary cannot call the public API

The Node v2 runner loads an ESM package and then requires the selected export to
be a callable function (`src/nl2repobench/verification/node/candidate_runner.mjs:52-66`).
It does not resolve nested members such as `default.parse`. The allowlisted
export name is a single literal name, not a method path.

With the exact pinned package installed, local boundary probes for `export` set
to `parse`, `stringify`, and `default` all return:

```json
{"ok":false,"error":"export-is-not-callable"}
```

Thus a private `node:test` adapter cannot invoke either scored API through the
approved boundary. Changing the shared runner, adding a task-specific wrapper,
or scoring a generated re-export would be an unapproved protocol/API decision;
this candidate must remain blocked until the parent approves one of those
architectural paths. Do not compile, run Oracle, or publish this task.

### High — the exact upstream package tarball is rejected by lifecycle policy

The pinned `package.json` contains `benchmark` and `test` scripts at lines
22-24. The exact `npm pack --ignore-scripts` tarball therefore fails the Node
runtime package validator (`src/nl2repobench/verification/node/validate-package.mjs:39-44`),
which rejects any `packageJson.scripts` key. The observed validator exit code was
`71`.

An agent-generated candidate could omit scripts, but that would be an explicit
packaging adaptation rather than a verbatim upstream artifact. Any future task
instruction/Oracle must state and test that adaptation; the current audit does
not silently make it.

### High — a lockfile is generatable, but the offline cache closure is not yet a
reviewed artifact

Using Node `22.23.1` and npm `10.9.8`, a temporary copy with
`npm_config_package_lock=true` generated a v3 lockfile:

- 698 non-root package entries;
- 314,718 bytes;
- SHA-256 `5b15f3b377c4c81dc99e144e218476289d6a27af0ec78f04ef322dca9a0c8cf2`;
- all 698 entries had `sha512-` integrity and HTTPS registry resolution;
- no git/file/workspace/link sources, `hasInstallScript`, gyp/binary markers, or
  platform `os`/`cpu` fields were found;
- two optional entries were present: `@pkgjs/parseargs` and
  `xo/node_modules/@types/eslint`.

The lockfile-only probe did **not** establish offline reproducibility:
`npm ci --offline --ignore-scripts --no-audit --no-fund` failed with
`ENOTCACHED` for `yocto-queue@0.1.0`. After an explicitly networked temporary
cache hydration, the same exact command passed. The hydrated npm cache had
1,149 verified index entries / 241,423,867 verified content bytes (2,303 files,
243,230,555 bytes including cache metadata and logs). The fully installed development tree contained 495 package manifests with ordinary
`test`, `build`, or other npm scripts; the lock scan found no install/preinstall/postinstall
markers, and every install was run with `--ignore-scripts`. This distinction matters:
ordinary package scripts remain untrusted even when npm does not execute them.

This proves the need for a separately reviewed, content-addressed private npm
cache/tarball bundle and `bundle.manifest.json`; neither the generated lockfile
nor the cache is committed here. The compiler's fail-closed checks require
lockfile v3, exact npm `10.9.8`, offline mode, `ignore-scripts`, complete cache
entry listing, and integrity checks (`src/nl2repobench/harbor/node_dependencies.py:90-175`).

### Medium — upstream tests do not match the locked verifier framework

The exact checkout declares `npm test = xo && ava && tsd` (`package.json:22-24`),
not `node:test`. The source contains 183 AVA declarations: 182 ordinary tests
plus one `test.failing` property test. The full temporary run under the locked
Node/npm versions reported:

| suite | declarations |
| --- | ---: |
| `test/parse.js` | 83 |
| `test/stringify.js` | 57 |
| `test/parse-url.js` | 6 |
| `test/exclude.js` | 18 |
| `test/stringify-url.js` | 11 |
| `test/pick.js` | 4 |
| `test/extract.js` | 3 |
| `test/properties.js` | 1 expected failure |
| **total** | **183** |

`npm test` completed with 182 passing and one expected failure after offline
installation. This is source/test evidence only; no private test bundle or
Oracle evidence was created. A future task would need a reviewed `node:test`
adapter and a new frozen leaf collection rather than treating the AVA count as
the Harbor denominator.

## JSON-only scope audit

A possible task-local semantic scope is limited to the default package's
`parse(query, options)` and `stringify(object, options)` behavior where every
request and response is JSON-serializable:

- `parse` input is a string; JSON options can include `decode`, the six documented
  `arrayFormat` values, one-character `arrayFormatSeparator`, `parseNumbers`,
  `parseBooleans`, `sort: false`, and string-valued `types` entries
  (`boolean`, `number`, `string`, `string[]`, `number[]`).
- `stringify` input is a JSON object containing strings, finite JSON numbers,
  booleans, `null`, and arrays of those values. JSON options can include
  `encode`, `strict`, the documented array formats and separator, `sort: false`,
  `skipNull`, and `skipEmptyString`.
- Custom sort functions, `types` callback functions, `replacer`, `BigInt`,
  `undefined`, `Symbol`, `Date`, cycles, and arbitrary class/object values are
  outside this boundary. The URL helpers (`parseUrl`, `stringifyUrl`, `extract`,
  `pick`, `exclude`) are also outside the requested parse/stringify scope.

The current request limit is 64 KiB and response limit is 256 KiB
(`candidate_runner.mjs:5-7`). Several upstream behavior/performance tests cannot
cross it unchanged: the parse suite constructs roughly 80 KiB, 120 KiB,
400 KiB, and 5 MiB requests (`test/parse.js:97-174`), and stringify constructs a
roughly 400 KiB array request (`test/stringify.js:40-85`). These tests must be
excluded or deliberately reduced and must not be silently counted as covered.

One source semantic edge also needs an explicit contract decision before hidden
tests are written: `stringify` copies keys into a plain object
(`base.js:484-490`), so a JSON object containing an own `"__proto__"` key is
not emitted (`queryString.stringify(JSON.parse('{"__proto__":"x","a":"1"}'))`
returns `a=1`). Either preserve/document this pinned behavior or constrain the
JSON key domain; do not leave it implicit.

## Required unblock actions

1. Approve a task-specific way to invoke methods on the default namespace while
   preserving the fixed JSON subprocess and separate-verifier isolation (or
   select a candidate with direct callable exports).
2. Define the explicit packaging adaptation that removes lifecycle scripts from
   the generated candidate and test it through `npm ci --offline --ignore-scripts`
   and package validation.
3. Produce a reviewed private npm v3 lock/cache closure, a private `node:test`
   adapter, frozen collection evidence, and a separate command artifact.
4. Re-run boundary, empty/stub/forgery/offline controls and three independent
   Oracle attempts. No such artifacts were produced in this audit.
