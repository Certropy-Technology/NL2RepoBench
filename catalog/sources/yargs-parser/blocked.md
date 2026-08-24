# `yargs-parser` Node/npm authoring audit — blocked

**Status: blocked.** This task-local record is an evidence-first candidate audit,
not a published task, canonical manifest, or Harbor bundle. It contains no
private tests, hidden assertions, Oracle solution, dependency cache, generated
build output, credentials, or shared-index changes.

## Scope and evidence method

The audit used one bounded, shallow, detached fetch and removed its temporary
checkout on exit. The probe resolved `refs/heads/main`, fetched that exact object
by full hash with `--depth=1`, compared the checked-out object identity, inspected
tracked metadata, and attempted the remaining static checks. The probe stopped
when its LOC helper invoked unavailable `python`; in accordance with the bounded
probe/turn limit it was not repeated. Consequently, every check after that point
is explicitly unresolved rather than inferred or reported as passing.

This distinction is intentional: a blocked record is preferable to filling
provenance, denominator, dependency-closure, or runtime gaps from package-name
knowledge.

## Candidate lock and archive evidence

- Package: `yargs-parser`
- Upstream: <https://github.com/yargs/yargs-parser.git>
- Remote ref resolved during the audit: `refs/heads/main`
- Exact frozen revision:
  `6a974f493742dba3726cb2c3f602b25745853d99`
- Checked-out tree: `beeb043c8cdf7c5babca25fb6bac9d5340bfeee2`
- Commit subject: `docs: remove greedy arrays note (#516)`
- Author timestamp: `2026-08-17T15:07:48+08:00`
- Commit timestamp: `2026-08-17T19:07:48+12:00`
- The full hash returned by `git ls-remote` and the detached `git show %H`
  value were identical. The fetch was shallow, so an empty local `%P` result is
  not evidence that this is a root commit and is not recorded as such.
- Three independent `git archive --format=tar HEAD | sha256sum` invocations
  returned the same SHA-256:
  `9593eb25f24a6c85b12862860ccd5be07361cfcb688b05420cf99c121d1742e1`.
- The uncompressed Git archive was 573,440 bytes.
- `LICENSE.txt` is 731 bytes with SHA-256
  `365496ca1f56da40b23c9815fc40fa9005847b2f8f8fd1c1a4929ef25ec8cd1d`.
  The locked `package.json` declares `"license": "ISC"`; this is a permissive
  license and clears the candidate license gate. Publication would still need
  to preserve its notice.

The archive evidence identifies immutable public source bytes. It is not a
private artifact reference and does not imply that an npm package tarball,
compiled `build/` directory, or verifier image was frozen.

## Source-only LOC — unresolved blocker

The tracked top level contains `lib/`, `browser.js`, and `deno.ts` as source,
plus `test/`, documentation, configuration, and lock metadata. No tracked
`build/` directory appeared in the top-level tree listing.

The intended LOC rule was: count physical and nonblank lines in tracked
production JavaScript/TypeScript under `lib/` plus production browser/deno
entry points; exclude `test/`, declarations, docs, vendored dependencies,
coverage, and generated `build/`. The helper failed before producing a count:

```text
--- tracked loc ---
/bin/bash: line 23: python: command not found
```

Therefore **no source-only LOC or difficulty classification is claimed**. This
is a publication blocker. A follow-up must rerun the same definition with an
available, pinned tool and save both the file list and counts; it must not use
archive-wide `wc -l` as a substitute.

## Node 22 and packaging contract

The locked `package.json` provides these direct facts:

- package version: `22.0.0`;
- `"type": "module"`;
- engines: `^20.19.0 || ^22.12.0 || >=23`;
- main/module: `build/lib/index.js`;
- published files: `browser.js`, `build`, excluding top-level declaration
  patterns;
- no runtime `dependencies` field;
- thirteen development dependencies, including TypeScript, Mocha, c8, Chai,
  Puppeteer, lint tooling, and browser-test tooling;
- lifecycle/build scripts include `pretest`, `precompile`, `compile`, and
  `prepare`; `prepare` runs `npm run compile`.

This declares support for Node 22 only from **22.12.0 onward**, not all Node 22
releases. A future environment lock must pin a concrete Node 22 version in that
range and a concrete npm version; `package.json` contains no `packageManager`
field to supply the npm pin. No Node 22 execution was completed in this audit,
so compatibility is metadata-supported but not runtime-validated.

The Git source archive is not directly package-loadable through its declared
entry point because `build/lib/index.js` is generated and was absent from the
tracked top-level listing. An offline install using `--ignore-scripts` will not
run `prepare` and therefore cannot silently create this output. A production
candidate would need a reviewed build step followed by a lifecycle-free
pack/install path; neither was authored here.

## ESM and CommonJS export audit

The root export is declared as an array whose first condition maps `import` to
`./build/lib/index.js` and whose fallback maps to that same path. The package is
`type: module`. There is also a `./browser` subpath mapped to `./browser.js`.

Static consequences of the exact manifest are:

- the root package contract is ESM;
- there is no `require` condition and no `.cjs` root target;
- the fallback does not create a CommonJS implementation because it still
  names a `.js` file inside a `type: module` package;
- CommonJS `require('yargs-parser')` support must therefore not be promised by
  a task instruction without a successful concrete probe and an explicit
  packaging decision;
- the source checkout could not be import-probed before compilation because
  its declared `build/` target was absent.

No ESM/CJS re-export shim is approved or included. A future task should score
the package's actual ESM API rather than adding an unannounced compatibility
surface.

## Official tests — identified, not frozen

The upstream scripts identify the official test lanes:

```text
pretest          rimraf build && tsc -p tsconfig.test.json
test             c8 --reporter=text --reporter=html mocha test/*.mjs
test:browser     start-server-and-test ... test/browser/yargs-test.cjs
pretest:typescript npm run pretest
test:typescript  c8 mocha ./build/test/typescript/*.js
```

These are Mocha/c8 and browser/TypeScript suites, not `node:test`. The bounded
probe stopped before enumerating declarations, running compilation, collecting
Mocha leaves, or checking skips/hooks/dynamic test generation. No frozen total
is claimed. Puppeteer/browser tests also introduce a browser binary and possible
install/download behavior that must be separately preprovisioned and audited;
they cannot be treated as an ordinary offline Node-only lane.

A follow-up must select and justify official upstream suites, adapt them to the
trusted subprocess boundary without changing assertions, produce a stable leaf
report, and repeat collection. This record includes no tests and is not usable
as a denominator.

## npm lock and offline closure — unresolved blocker

A tracked `package-lock.json` exists, while the root manifest declares zero
runtime dependencies and thirteen development dependencies. That means the
runtime library may be dependency-free, but the official build/test closure is
not. The probe stopped before parsing lockfile version, entry count, integrity
algorithms, registry origins, optional/platform packages, lifecycle markers, or
lock SHA-256. It also did not execute an empty-cache offline install.

Accordingly, none of the following is claimed: npm v3 lock compliance, exact
npm version compatibility, complete cache closure, all-`sha512` integrity,
script-free transitive installation, browser availability, or reproducible
`npm ci --offline --ignore-scripts`. No npm cache was retained or committed.

This is a hard blocker. Reopening requires a small content manifest for a
private, reviewed npm cache (not cache bytes in this catalog), exact Node/npm
pins, lock validation, and an empty-network `npm ci --offline --ignore-scripts`
run. Compilation must be an explicit trusted command, not an install lifecycle
side effect.

## Dynamic, filesystem, and process risks

`yargs-parser` cannot be assumed to be a pure JSON function across its full
option surface. Before tests are adapted, source-level traceability must inspect
at least these documented/high-risk behaviors:

- environment-derived options (`envPrefix`) can read process environment;
- normalization and path-related behavior can depend on process CWD, OS path
  rules, and filesystem semantics;
- configuration-file options can resolve/load external files or modules;
- coercion hooks accept executable callbacks;
- defaults/config objects can introduce values that JSON cannot represent;
- numeric parsing can produce non-finite numbers, which ordinary
  `JSON.stringify` silently converts to `null`;
- dotted keys, aliases, `__proto__`/constructor-like keys, duplicate options,
  and object merging require an explicit prototype-pollution audit;
- browser and Deno entry points have different host capabilities from the Node
  entry point;
- official build/test scripts launch compilers, test runners, a local server,
  and browser tooling.

The interrupted probe did not save source-line evidence for these items, so they
are risk hypotheses to verify, not findings attributed to particular lines.
They prohibit publishing a broad “all options are supported” contract from this
record.

## Proposed JSON-safe parsing boundary (not yet approved)

A defensible future task-local boundary can be narrower than the package's full
host API while preserving its core parser behavior:

1. Invoke only the ESM package default parse function through the trusted
   subprocess runner. Separately inventory any named string helpers before
   deciding whether they are scored.
2. Accept one JSON request containing `args` as an array of strings and
   `options` as an object. Do not accept a shell command string: tokenization by
   a shell is outside the parser contract.
3. Allow only data-only option families whose recursively validated members are
   JSON values: aliases; string/number/boolean/count/array option names; finite
   integer `narg`; JSON-safe defaults; and an explicitly enumerated set of
   boolean parser-configuration flags.
4. Reject, before package invocation, `envPrefix`, config-file/module loading,
   config objects unless separately specified, coercion callbacks, normalize/
   path behavior, functions, accessors, symbols, bigint, `undefined`, cycles,
   non-finite numbers, and prototype-sensitive keys.
5. Recursively validate the result before serialization: plain objects/arrays,
   strings, booleans, null, and finite numbers only; own enumerable properties;
   bounded depth, key count, request bytes, and response bytes. Do not rely on
   lossy `JSON.stringify` behavior as validation.
6. Run with a fixed CWD, minimal explicit environment, no network, and no
   candidate-controlled module/config lookup. Return protocol errors separately
   from parser assertion failures.
7. Specify ordering, duplicate-key accumulation, aliases, `--`, negative
   numbers, empty tokens, Unicode, dotted keys, and prototype-sensitive names
   only after mapping each behavior to the frozen revision's official tests.

This boundary is a proposal for the next authoring stage, not a hidden-test
specification and not approval to alter the shared runner. Its purpose is to
make host-dependent and lossy values visibly out of scope.

## Decision and unblock requirements

The immutable source and permissive-license gates pass, and the manifest
explicitly includes supported Node 22 releases. The candidate remains
**blocked** because source LOC, runtime execution, official test collection,
lock/cache closure, source-backed dynamic-risk review, compiled ESM import, and
CommonJS behavior are not fully evidenced.

Do not compile, publish, or add this candidate to a dataset from this record.
Reopen only after all of the following task-local evidence exists:

1. reproducible source-only LOC with the exact tracked file list;
2. pinned Node 22.12+ and npm versions with successful build and ESM probes,
   plus a recorded CJS expected-failure or supported-path result;
3. parsed lock audit and reviewed offline cache closure, with scripts disabled
   during installation and compilation performed explicitly;
4. official-suite inventory and stable trusted leaf collection;
5. source-line traceability for environment, config loading, normalization,
   coercion, object safety, and non-finite values;
6. an approved strict JSON request/result schema and subprocess API inventory;
7. later, in separate work, private tests, three Oracle runs, and the required
   empty/stub/forgery/offline controls.

Items 1–6 are evidence gaps in this candidate. Item 7 is deliberately outside
the requested audit-only scope.
