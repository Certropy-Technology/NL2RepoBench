# `fast-deep-equal` Node/npm authoring audit — blocked

**Status: blocked / evidence-only.** This task-local record freezes public
source evidence for a possible Node/npm repository-generation task. It is not
a declarative task, Harbor bundle, private test package, verifier, Oracle,
dependency bundle, or publication approval. No upstream source/test bytes,
generated package, npm cache, hidden assertions, command artifact, Docker
asset, or shared dataset file is stored here.

## Decision

Keep this candidate blocked at authoring. The exact source, license, source-only
implementation size, Node 22 source baseline, official tests, and reproducible
generated JavaScript are established. Publication gates remain missing:

- the exact Git tree does not contain the JavaScript files named by the package
  entry points; building them requires an unfrozen development dependency;
- upstream commits no dependency lock, and the disposable full development
  lock cannot install against an empty npm cache;
- no immutable Node image/toolchain lock or reviewed offline build/test bundle
  exists; and
- the JSON-only API projection has no private adapted tests, separate
  subprocess verifier, frozen denominator, Oracle runs, or negative controls.

A narrowed zero-runtime-dependency CommonJS task appears feasible, but it must
not be compiled or published from this evidence alone.

## Exact source and archive

The remote default `HEAD` of
`https://github.com/epoberezkin/fast-deep-equal.git` was fetched into a
disposable checkout and detached at:

```text
package/version: fast-deep-equal 3.1.3
revision:        a8e7172b6c411ec320d6045fd4afbd2abc1b4bde
tree:            6e99f44c1e415cba716a82029467cfff96ce5e1c
parents:         d807ffc5013e710deb1c63d463a03f729bcd144d
                 ea5b08236698c09c9cb6d458f7c768383122c2fb
subject:         Merge pull request #54 from LinusU/typescript
author date:     2020-06-09T09:59:48+01:00
committer date:  2020-06-09T09:59:48+01:00
tracked files:   21
submodules:      0
```

Two independent unprefixed `git archive --format=tar HEAD` outputs were
byte-identical:

```text
archive bytes:                     61440
archive members including dirs:    26
archive sha256: bfae19c6df85a382dc13a05ceb6ace92125e9a54e603056f3244b2f842ccf755
matching runs:                      2
```

The source archive contains `src/index.jst`, `build.js`, declarations, specs,
benchmark material, and metadata. It does **not** contain `index.js`,
`react.js`, `es6/index.js`, or `es6/react.js`, even though those generated
files are the package's runtime entry points.

## License evidence

`package.json` declares `MIT`, agreeing with the tracked root `LICENSE`:

```text
LICENSE bytes:   1074
LICENSE git blob: 7f1543566f6abbbf75914db32651cf89919cabed
LICENSE sha256:  7bf9b2de73a6b356761c948d0e9eeb4be6c1270bd04c79cd489c1e400ffdfc1a
package.json git blob: 3cfe66c68e832bf5a728395ed493492e65737441
package.json sha256: a5c63940db0260739be9e2ac67f3aac268df4db5770420ee4e34e493152f97d2
```

This clears static source-license identification only. Dependency-license and
generated-artifact redistribution review still belong to a future closure.

## Source-only LOC

The implementation source of truth is the single tracked template
`src/index.jst`. Using physical newline-delimited lines on the exact Git blob,
without counting generated JavaScript, specs, benchmarks, declarations, or the
build helper:

```text
implementation source files: 1
implementation source bytes: 2265
implementation physical LOC: 79
src/index.jst git blob: 5d4ee2fdb1197bd09eb76fc4fc774bec9ace667e
src/index.jst sha256: e6475b939b2fd0336664a9cf0f2daaba158dbd1e430caca48041507a486a3226
```

For provenance rather than implementation sizing, the tracked `build.js`
helper is 449 bytes and 12 physical lines (SHA-256
`cf0d222fd72f57be1b640b0debaac04ff8decd4737049bcc12b4ad2162cba14c`).
The four two-line declaration files are tracked but do not add runtime LOC.

## Package and generated-build provenance

The exact package is CommonJS. It has `main: "index.js"`, no `type` or
`exports` field, no runtime dependencies, and four runtime forms selected by
path:

```text
require("fast-deep-equal")           -> generated index.js
require("fast-deep-equal/react")     -> generated react.js
require("fast-deep-equal/es6")       -> generated es6/index.js
require("fast-deep-equal/es6/react") -> generated es6/react.js
```

`build.js` compiles `src/index.jst` with the development dependency `dot`.
A disposable npm resolution selected `dot@1.1.3`. Under Node `v22.23.1`, two
consecutive builds from the same template and installed tool produced
byte-identical outputs:

| generated path | bytes | SHA-256 |
|---|---:|---|
| `index.js` | 1177 | `eb469e206280321a3878f2335ec98aa2104a155079d8ed83a23029098dccd215` |
| `react.js` | 1451 | `37cbd168dbd42c73119ce7326556bddef40b3a5fbd2e215cf81a7c78fb73ff9a` |
| `es6/index.js` | 1935 | `d7f027497048c75e17268dbc66b670579d4f70f2dc0e019cdc9edf5078c247d6` |
| `es6/react.js` | 2209 | `366779cbb7821d26d18b9eaa12b6788cbb101cdbbabcae36f2919a5f48534ef0` |

These hashes are repeatability observations, not source-archive identities or
approved build artifacts. The `dot@1.1.3` tarball, npm metadata, and complete
build environment are not locked in this task. The exact manifest also
contains multiple scripts and a `prepublish` lifecycle hook, so a future
candidate needs an explicitly reviewed script-free package adaptation rather
than installing the upstream manifest as trusted executable metadata.

## Node 22 and official test evidence

The disposable probe used exactly Node `v22.23.1` and npm `10.9.8`. The
upstream manifest has no `engines` declaration, so Node 22 compatibility is
empirical at this revision, not an upstream support promise.

After a disposable network-backed `npm ci --ignore-scripts`, the official
`npm test` command exited zero on Node 22. It ran the upstream build, ESLint,
TypeScript declaration check, and Mocha/nyc specs. The observed result was:

```text
626 passing
0 failing
statement coverage: 188/188 (100%)
branch coverage:    188/188 (100%)
function coverage:      4/4 (100%)
line coverage:        134/134 (100%)
```

The generated CommonJS root and `es6` forms also loaded on Node 22. A bounded
smoke probe returned the expected booleans for equal and unequal JSON values.
This is one source baseline, not three Oracle runs, a frozen private
collection, or an immutable OS/image claim. The official suite is Mocha and
uses broader JavaScript values; it cannot be copied into a `node:test`
separate-verifier contract or treated as its scoring denominator.

## npm lock and offline closure

The exact revision commits no `package-lock.json`, `npm-shrinkwrap.json`,
`yarn.lock`, or `pnpm-lock.yaml`. A disposable npm `10.9.8`
`--package-lock-only` resolution of the unmodified manifest produced:

```text
lockfile version: 3
lock bytes:       229240
lock sha256:      1c618eb18e363d761bd2fdbdcede53cf2e5bbb263d35e7d4112c80b1b0990ae0
package records:  488 (487 non-root)
resolved fields:  487
integrity fields: 487
install-script records: 3
OS-constrained records: 1
link records:     0
```

The lock was not copied here. With a fresh empty cache, the required full
closure probe

```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

failed closed with `ENOTCACHED` for
`yargs-unparser-1.6.0.tgz`. Consequently neither the build/test closure nor its
licenses and lifecycle/platform risks are available offline.

Because the package declares no runtime dependencies, the same disposable
lock with `--omit=dev` completed against an empty cache without downloading a
package. That only proves a zero-dependency **runtime** install is feasible
after trustworthy runtime files already exist. It does not solve the missing
generated files or freeze the `dot` build closure.

Reopening requires a content-addressed npm v3 lock/cache artifact accepted by
the repository bundle validator, including all selected build/test packages,
integrity and license review, lifecycle policy, and exact Node/npm/platform
metadata. A source-free trusted build output would instead need its own
approved generated-artifact provenance and deterministic packaging policy.

## Proposed JSON-safe equality boundary

The only suitable first scored API is the root CommonJS default function:

```text
equal(left, right) -> boolean
```

A verifier-owned child process should parse line-delimited JSON and invoke this
one function. The admissible domain is strictly JSON data: `null`, booleans,
strings, finite JSON numbers, arrays of admissible values, and objects whose
own string-keyed values are admissible. For that domain the intended observable
contract is:

- strict primitive equality (`0` and `-0` are not distinguishable through a
  JSON serialization boundary);
- arrays compare by length, order, and recursive element equality;
- objects compare by own enumerable string-key set and recursive values,
  independent of key insertion order; and
- the call returns a boolean, is deterministic, and does not mutate either
  parsed request value.

Before freezing this contract, private tests and review must explicitly cover
empty/nested inputs, Unicode strings, finite-number edges, key-order changes,
`null`, arrays versus objects, and JSON keys such as `constructor` and
`__proto__`. In particular, the implementation reads the `constructor`
property before walking keys; an own JSON `constructor` key containing an
object can affect results and must be specified from observed behavior rather
than normalized away silently.

The following are intentionally outside the JSON protocol even where an
upstream entry point has JavaScript behavior for them:

- cyclic or shared-reference object graphs: JSON cannot encode identity or
  cycles, and comparing two separately created self-cycles in the root build
  raised `RangeError` rather than providing cycle-aware equality;
- typed arrays and `ArrayBuffer` views: JSON serialization loses their
  constructor and byte-view semantics; the explicit typed-array behavior of
  `fast-deep-equal/es6` is therefore not part of this task;
- `Map`, `Set`, `Date`, `RegExp`, `BigInt`, `NaN`, infinities, `undefined`,
  symbols, functions, sparse-array holes, class instances, custom prototypes,
  accessors, and custom `valueOf`, `toString`, or `toJSON` behavior; and
- React elements, `_owner` cycle suppression, the `/react`, `/es6`, and
  `/es6/react` entry points, TypeScript-only checking, benchmarks, filesystem,
  CLI, network, and loader behavior.

The typed-array exclusion is a transport limitation, not a claim that the
upstream comparator lacks such support. A future JavaScript-native adapter
could widen the task only through a separately reviewed, non-JSON protocol;
it must not infer typed arrays from ordinary JSON objects.

## Candidate/verifier requirements and blockers

If reopened, the task should require a candidate package produced from an
empty workspace with a script-free npm v3 lock, the root CommonJS import, no
runtime dependencies, and no registry/loader/workspace/native-addon settings.
The verifier must pack and inspect the candidate, install it offline with
lifecycle scripts disabled, and import it only in an unprivileged child. The
trusted side must own commands, request corpus, report and reward paths,
collection, timeouts, and the fixed leaf denominator.

Do not compile or publish this record until all of these are versioned and
reviewed:

1. immutable Node 22/npm 10.9.8 OS, architecture, libc, and base-image digest;
2. approved generated-build provenance plus a complete offline dependency
   closure, or an approved source-level adaptation that removes the build;
3. public instruction and private `node:test` JSON-adapter bundle with
   bidirectional assertion traceability and a frozen structured denominator;
4. separate subprocess verifier with install, collection, timeout, and
   forgery protections; and
5. three valid Oracle runs plus empty, stub, forgery, install-failure, hang,
   and offline controls, followed by blind and traceability review.
