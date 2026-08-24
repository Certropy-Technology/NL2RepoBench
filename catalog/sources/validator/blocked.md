# `validator` Node v2 Authoring Audit

Status: **blocked development-only**. This directory is an evidence record for
the npm pilot, not a Harbor task or a publication approval. It contains no
upstream test bytes, private artifacts, generated package, dependency cache,
Oracle solution, verifier, Dockerfile, or secret.

## Candidate and exact source lock

- Upstream: `https://github.com/validatorjs/validator.js`.
- Candidate record: `reports/npm-package-candidates.v1.md`, package `validator`.
- Requested detached revision:
  `a79ff980ab14257e795332989e497bdff3218e87`.
- Commit tree: `2135a5dc37902736cfb283785021644605318f9c`.
- Commit subject: `fix(isVAT): accept Spanish digit controls (#2849)`.
- Commit authored/committed: `2026-08-16T00:50:15+05:30` /
  `2026-08-16T01:05:15+05:45`.
- `git archive --format=tar HEAD | sha256sum`:
  `dd8284c8fa6d4345e538e15fb235326762ea106699177d041e5ed6ba2e0e064b`.
- The detached checkout had no submodules and no local modifications.
- The archive contains 150 tracked files: 114 source JavaScript files and 15
  test JavaScript files, plus metadata, build configuration, documentation,
  and license files.

The source archive digest above is the requested revision evidence. No source
archive bytes are copied into this task directory.

## License and package metadata

The pinned tree contains `LICENSE` (1,077 bytes), and `package.json` declares
MIT. The license SHA-256 is
`683b3c34623e01daad41cb2a3d0a93578c590f8d0206cbd8b0b579fb7def2603`.
`package.json` is 2,148 bytes with SHA-256
`e33c239e4e4cbd1142b7ad37e831951f45cce3e655f3164eb88c7e1eae1a2af5`.

The package metadata records:

- name `validator`, version `13.15.35`, and CommonJS `main: index.js`;
- published files `index.js`, `es`, `lib`, `README.md`, `LICENSE`,
  `validator.js`, and `validator.min.js`;
- no `dependencies` field, so the installed library declares no runtime
  dependencies;
- 17 development dependencies, all specified as ranges rather than exact
  versions;
- Node engine `>=0.10`; there is no `type: module` field.

The no-runtime-dependency statement is supported by the package metadata and
by static inspection of the generated CommonJS files: their `require()` calls
resolve only to relative package files. It does not establish a reproducible
build or an offline development/test closure. Build and test tooling remains a
large transitive dependency surface.

## CommonJS exports and generated output

`src/index.js` is authored as an ES module with one default export. The source
default object contains 112 own names: 104 callable exports, the `version`
string, and seven locale arrays. The development Babel configuration
(`.babelrc`) targets Node `0.10` and enables `add-module-exports` with
`addDefaultProperty: true`.

The exact build commands are declared in `package.json`:

```text
build:node    babel src -d .
build:es      babel src -d es --env-name=es
build:browser node --require @babel/register build-browser && npm run minify
build         run-p build:*
pretest       npm run build && npm run lint
test          nyc ... mocha --require @babel/register ... --recursive
```

`index.js`, `lib/`, `es/`, `validator.js`, and `validator.min.js` are absent
from the requested Git tree and are ignored by `.gitignore`. They are release
outputs, not source inputs. An isolated build probe using Node `22.23.1`, npm
`10.9.8`, and a temporary generated lock produced 114 CommonJS files, 114 ES
files, and the browser/minified bundles. The resulting representative hashes
were:

```text
index.js          d1eb061bfe00c85f17b684a4169608cfda57844838ae9ecc9c7eaa8f75a088cf
es/index.js       d9015c77b25c8b2e1ad3e1994afddd8d6dfb2ddd9200f31059bc6ca194ba724d
validator.js      aa942a49ade95fee672635ca1c6e3a95304acf4a9f3234356d5130635b4b0544
validator.min.js  6633f40efe3d414911836a38feca6f4ad3c013155952a869e7e80baea8320b16
```

Repeating `npm run build` in the same temporary checkout produced the same
four hashes. This is only a same-machine/same-lock probe, not a durable build
lock or publication artifact.

The generated CommonJS smoke result was:

```text
require(package) -> object, version 13.15.35
own keys -> 113 (the Babel-added enumerable `default` self-reference included)
callable keys -> 104
default === module.exports -> true
```

The root CommonJS form is therefore the suitable first boundary for this
pilot. The generated `es/index.js` retains extensionless imports; a native
Node 22 `import()` of that file fails with `ERR_MODULE_NOT_FOUND` without a
bundler or non-standard specifier resolution. Native ESM execution must not be
silently claimed as covered by a CommonJS-only task.

There is also a release provenance mismatch. Registry metadata for
`validator@13.15.35` reports `gitHead`
`7a8079709cd4cb27b2a1846e6f6508d68c9d928f`, not the requested revision. The
registry package's generated files differ from the exact-revision build in the
root bundle and multiple `lib/` and `es/` files, including the requested
`isVAT` and `isByteLength` changes. The registry dist integrity is
`sha512-TQ5pAGhd5whStmqWvYF4OjQROlmv9SMFVt37qoCBdqRffuuklWYQlCNnEs2ZaIBD1kZRNnikiZOS1eqgkar0iw==`.
The registry CommonJS smoke also returns `[object Object]` for `require("validator").toString("123")`, while the exact-revision build returns `"123"`; the registry bundle therefore does not implement the pinned source export contract.
It cannot be used as the exact-revision generated artifact without a separate
provenance decision.

## Build lock and dependency closure

The exact tree contains no `package-lock.json`, `npm-shrinkwrap.json`,
`yarn.lock`, or `pnpm-lock.yaml`; `package-lock.json` is explicitly ignored.
The development ranges include Babel, Rollup, Mocha, nyc, ESLint, and the
deprecated `rollup-plugin-babel` toolchain. The CI workflow runs
`npm install --legacy-peer-deps`, not an immutable install.

For evidence only, `npm install --package-lock-only --ignore-scripts
--legacy-peer-deps --no-audit --no-fund` with npm `10.9.8` generated a v3 lock
with 541 package entries and 273,995 bytes, SHA-256
`d4232e733bac81e6050b2b3ef18dae426e96b363037bbd7c1098240901fd9486`.
That lock is not committed or included here. With an empty npm cache,
`npm ci --offline --ignore-scripts --legacy-peer-deps --no-audit --no-fund`
failed with `ENOTCACHED` for `yargs-unparser-1.6.0.tgz`.

With network access, the same temporary lock installed 539 packages and the
build/test probe passed. This proves only that the current host can resolve a
temporary dependency graph; it is not an authorized offline artifact. A
future task must provide a reviewed v3 lock plus a content-addressed npm cache
closure, with lifecycle scripts disabled for installation and an explicit
allowlist for the build commands.

## Upstream tests and denominator

The exact tree has 14 `*.test.js` files, 24 `describe` declarations, and 323
Mocha `it` leaf declarations. No `skip`, `only`, or pending marker was found.
The helper calls in `test/testFunctions.js` expand many valid/invalid input
examples inside a leaf; they must not be counted as additional test leaves.

In the isolated temporary checkout, `npm test` ran the build, lint, and Mocha
suite and reported:

```text
323 passing (336ms)
Statements 100% (2744/2744)
Branches 96.59% (1697/1757)
Functions 100% (427/427)
Lines 100% (2429/2429)
```

This is an upstream source baseline, not a Harbor Oracle result. The tests
directly import source modules and generated CommonJS/browser bundles. They
also use values that cannot cross a plain JSON request unchanged, including
`Date` instances, `undefined`, `NaN`, `Buffer`, regular expressions, and
environment/time-dependent values. Several tests exercise regex entries in
`host_whitelist`/`host_blacklist`, VM/browser globals, and generated bundle
files. A separate verifier cannot import the candidate in its trusted test
process or copy this suite as a public task artifact.

## JSON subprocess contract

The reusable Node child runner accepts one bounded JSON request of the shape
`{"package":"...","export":"...","args":[...]}` and emits one bounded
JSON response. It enforces 64 KiB request, 32-argument, and 256 KiB response
limits, uses `--no-addons`, and supports sanitized candidate execution. After
installing the built package into a candidate site, smoke calls through this
runner returned:

```text
isEmail("foo@example.com")           -> {"ok":true,"value":true}
normalizeEmail("User+tag@Gmail.com") -> {"ok":true,"value":"user@gmail.com"}
toDate("2020-01-02")                 -> {"ok":true,"value":"2020-01-02T00:00:00.000Z"}
isEmail("not-an-email")               -> {"ok":true,"value":false}
```

The generic runner is not a task contract: it accepts any callable export
matching a name pattern and cannot expose the seven locale arrays or the
`version` scalar. A validator-specific private adapter is still required to:

1. enforce a reviewed fixed allowlist of callable CommonJS exports;
2. restrict arguments to the JSON-compatible subset, including only string
   patterns and string host allow/deny entries where applicable;
3. define normalization for `Date` results or exclude date-returning APIs;
4. reject unsupported `RegExp`, callable, `undefined`, non-finite-number,
   Buffer, VM, and browser cases; and
5. preserve structured exception type/message observations without importing
   candidate code in the trusted test process.

The adapter, private test bundle, command plan, and frozen collection artifact
do not exist in this task-local record.

## Blockers and reopening criteria

Keep this task blocked. The blockers are:

- generated distributions are not in the exact source revision and the
  registry artifact for the same version has a different `gitHead` and code;
- no durable build lock or offline npm cache closure exists;
- the upstream Mocha suite is not directly usable as a separate JSON-boundary
  verifier and no validator-specific adapter has been reviewed;
- no private test/command artifact, verifier/grader artifact, or Oracle bundle
  exists; and
- no Docker, Harbor, Oracle, negative-control, or publication action was
  authorized or run for this audit.

Reopen only after an exact-revision generated package is rebuilt from a locked
toolchain, the npm cache/lock closure is content-addressed, the CommonJS
JSON-only adapter and its normalization rules are reviewed, and private tests
freeze a structured leaf denominator. Oracle and empty/stub/forgery/offline
controls belong to a later validation stage and are intentionally absent here.
