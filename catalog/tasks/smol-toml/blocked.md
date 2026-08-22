# `smol-toml` Node v2 authoring audit — blocked

**Status: blocked / development-only.** This file records static authoring
and provenance evidence for the exact requested revision. It is not a Harbor
bundle, a publication approval, an Oracle, or a private test package. No
upstream test bytes, hidden assertions, npm/pnpm cache or tarballs, Docker
asset, verifier, reward file, credential, or shared dataset/index file is
stored in this task directory.

The task is intentionally not represented by a `task.toml` yet. The current
Node v2 compiler and verifier contract is npm v3 + `node:test` + a JSON
subprocess boundary; this candidate needs several explicit, owner-approved
adaptations before a declarative task source could be truthful.

## Candidate identity and exact source lock

- Package: `smol-toml` `1.8.0`.
- Upstream: `https://github.com/squirrelchat/smol-toml` (repository metadata
  names `squirrelchat/smol-toml`).
- Requested and resolved revision:
  `6d0f4774700c40ce8b5794934eb771870a9a93d3`.
- Revision tag: `v1.8.0`.
- Commit subject: `chore: bump version`.
- Commit tree: `1bb64c5e25d189e29f4c04255f9d6b0a0e9adaed`.
- Commit author: Cynthia Rey, `2026-08-11T19:52:53+02:00`.
- Committer: Cynthia Rey, `2026-08-11T21:01:18+02:00`.
- Git submodules: none.
- Detached checkout status: clean before and after inspection.
- Deterministic source archive command:
  `git archive --format=tar HEAD`.
- Unprefixed archive size: `5,232,640` bytes.
- Unprefixed archive SHA-256:
  `8c7282cdd6f53c6cccce1e87c145ec28feac8a2932af6cf3e162d4d3b79b9cf1`.

The source archive and source/test files were inspected in a disposable
`/tmp/smol-toml-audit` checkout only. They were not copied into this catalog.

### License evidence

- `package.json` declares `BSD-3-Clause`.
- Tracked `LICENSE` is 1,499 bytes and contains the BSD 3-Clause notice.
- `LICENSE` SHA-256:
  `fa5659948374d4f555594f47f6da073b40dc503e921aeeece30df4362b3051a5`.
- `LICENSE` Git blob:
  `1ed1c049b431c9af43645d3dd1354290b803a239`.
- `package.json` SHA-256:
  `878ef67f6aeda7f0a881b30685e76904bac554aa96d346d93858bd001cbc51c6`.
- `package.json` Git blob:
  `a37bdf9d01142fd221fd3dfaf7fecda554908592`.

This is source-license evidence only. It does not review the licenses of the
future build/test dependency closure or approve distribution of a generated
package.

## Package, ESM/CJS exports, and source inventory

The pinned package metadata declares:

- name `smol-toml`, version `1.8.0`, and `type: "module"`;
- `main: ./dist/index.cjs`, `module: ./dist/index.js`, and
  `types: ./dist/index.d.ts`;
- conditional root exports:
  `types -> ./dist/index.d.ts`, `import -> ./dist/index.js`, and
  `require -> ./dist/index.cjs`;
- no runtime `dependencies`;
- 11 range-based development dependencies:
  `@mitata/counters`, `@tsconfig/node-lts`, `@tsconfig/node-ts`,
  `@tsconfig/strictest`, `@types/node`, `mitata`, `pin-github-action`,
  `rolldown`, `typescript`, `vite`, and `vitest`;
- `engines.node: ">= 18"`, but `devEngines.runtime.version: "^26"`;
- `devEngines.packageManager` requiring pnpm `11.21.0` with `onFail: "error"`;
- `files: ["README.md", "LICENSE", "dist"]`;
- scripts `test: "vitest"` and
  `update-gha: "pin-github-action .github/workflows"`.

The scored library source is TypeScript, not ready-to-load JavaScript:

| area | files | physical lines | notes |
|---|---:|---:|---|
| `src/` | 9 | 1,332 | parser, serializer, dates, errors, structures, utilities |
| `test/*.test.ts` | 12 | 1,987 | Vitest source tests |
| `bench/` tracked TypeScript/metadata | 10 | 717 | performance-only, not scored API |

The exact tree has **no `dist/` directory** and no generated CommonJS or ESM
bundle. The package entry points therefore do not resolve from the frozen
source checkout until the build is run. The root tree also tracks the symlink
`test/package/node_modules/smol-toml -> ../../..`; it is a package-boundary
fixture, not a candidate runtime dependency. Generic workspace ingestion
rejects symlinks, so this fixture cannot be copied into an agent workspace or
trusted verifier tree as-is.

`src/index.ts` exposes the following root API:

```text
named exports:  parse, stringify, TomlDate, TomlError
                     plus TypeScript-only TomlValue/TomlTable aliases

default export: { parse, stringify, TomlDate, TomlError }
```

The internal modules (`src/parse.ts`, `src/stringify.ts`, `src/primitive.ts`,
`src/struct.ts`, `src/extract.ts`, `src/util.ts`, `src/date.ts`, and
`src/error.ts`) are imported directly by the upstream tests but are not package
root exports. They must not become hidden candidate APIs merely because the
upstream suite reaches them.

The dual conditional export is technically compatible with a child process
that selects the **named** `parse` or `stringify` export after a successful
build and package install. It is not compatible with the first Node v2 pilot
policy that explicitly excludes dual ESM/CJS packages. Both loader conditions
would require a boundary smoke test; no such candidate package was built in
this audit.

### Root API inventory

The runtime root API and its observable types are:

- `parse(toml, options?)`: parses a TOML string into a table. The options are
  `maxDepth?: number` (default `1000`) and
  `integersAsBigInt?: false | true | "asNeeded"`. Ordinary parsing returns
  strings, booleans, JavaScript numbers, arrays, nested tables, and
  `TomlDate` instances; large integer handling changes when BigInt mode is
  enabled.
- `stringify(obj, options?)`: accepts a top-level object and returns TOML
  text ending in a newline. The options are `maxDepth?: number` (default
  `1000`) and `numbersAsFloat?: boolean` (default `false`). Object keys retain
  JavaScript own-key enumeration order; nested objects, arrays of tables,
  inline tables, strings, numbers, booleans, and TOML date values have
  distinct formatting rules.
- `TomlDate` extends `Date`. Its constructor accepts a TOML date/time string or
  a `Date`; instance methods are `isDateTime()`, `isLocal()`, `isDate()`,
  `isTime()`, `isValid()`, and an overridden `toISOString()`. Static wrappers
  create offset-date-time, local-date-time, local-date, and local-time
  representations from a `Date`.
- `TomlError` extends `Error` and exposes `line`, `column`, and `codeblock`
  fields in addition to the formatted message. Its constructor's internal
  `toml`/`ptr` context is not a JSON task input.

The TypeScript declarations also export recursive `TomlValue`, `TomlTable`,
and no-BigInt aliases. These are type-only exports and do not appear in a
runtime JSON response. The upstream implementation additionally recognizes
`Temporal` objects when available and accepts BigInt, Date, functions, and
symbols in some stringify paths; those JavaScript-only cases are deliberately
separated from the proposed candidate boundary below.

## Build, packaging, and script risks

The tracked `Justfile` defines the production-shaped build as:

```text
tsc --build tsconfig.lib.json
just _clean_dts
rolldown src/index.ts -p node -f cjs -o dist/index.cjs \
  --strict --exports named --no-comments.legal \
  --banner "`head -n27 src/index.ts`"
node test/package/package-test.mjs
```

This build has several implications:

1. `dist/index.js` and declarations come from TypeScript, while
   `dist/index.cjs` is a separate Rolldown bundle. The package cannot be
   evaluated as the exact source revision without first freezing this build
   toolchain and preserving both output forms.
2. The build requires `just`, pnpm, TypeScript 7, Rolldown, shell utilities,
   and their transitive dependencies. None of those build bytes is present in
   this task-local record.
3. `tsconfig.lib.json` uses Node/TypeScript configuration packages, declaration
   output, `ESNext.Temporal`, and `@types/node` 26. The requested Node v2
   runtime is Node `22.23.1`; the source development hint instead requests
   Node `^26`. Build and declaration parity on Node 22 has not been proven.
4. `package.json` retains a `scripts` object. The current Node package
   validator rejects candidate tarballs containing any `scripts` key, even
   when installation uses `--ignore-scripts`. A generated candidate would
   need an explicit packaging adaptation that removes scripts; this audit does
   not silently make that adaptation or claim upstream metadata parity.
5. `devEngines.packageManager` requires pnpm `11.21.0`, while the locked Node
   foundation uses npm `10.9.8`. In this checkout, `npm pack --dry-run
   --ignore-scripts --json` failed closed with `EBADDEVENGINES` because npm is
   not the required package manager; the Node `^26` runtime mismatch was also
   reported as a warning. A forced or edited pack is not evidence of a valid
   production package.
6. `pnpm run test` invokes Vitest, not `node:test`. The `publish` recipe uses a
   staged network publish with npm provenance, and `toml-test` invokes
   `mise exec go@latest` plus an external Go tool. These commands are outside a
   no-network, fixed-command Node v2 verifier and were not run.
7. The package test fixture asserts that ESM and CJS resolve to generated
   files under `dist`, then compares named and default exports in both loader
   modes. Those assertions are packaging/build evidence, not a substitute for
   a separate candidate subprocess boundary.

No build was run. Build output hashes, repeated-build determinism, exact
TypeScript/Rolldown behavior on Node 22, and a generated package tarball remain
unproven.

## Dependency lock and offline/cache closure

The frozen source does **not** contain `package-lock.json` or
`npm-shrinkwrap.json`. It contains:

- root `pnpm-lock.yaml`, lockfile version `9.0`, 65,628 bytes, SHA-256
  `c342d2164dceae82e97320e8407d50a4e66728f0b9a2a6d0c2caa2625c16e28a`;
- root `pnpm-workspace.yaml`, SHA-256
  `7690b21777ff22e71e83bbaa3b5ac76f7444312d54144c86a55dc6fad79a7581`;
- separate benchmark `bench/pnpm-lock.yaml` and
  `bench/pnpm-workspace.yaml`, which are not needed for the scored library
  API and must not be accidentally included in a candidate runtime closure.

The root pnpm lock contains a leading package-manager dependency document for
pnpm `11.21.0` and a project dependency document for the development closure.
It records exact integrity values for the locked packages, but it is not an npm
v3 lock and is not accepted by the current `validate_npm_dependency_bundle`
contract. The lock also includes platform/native optional packages from the
build stack, including Rolldown bindings, Rollup platform packages,
Lightning CSS packages, esbuild packages, and an `@napi-rs/lzma` package. The
root workspace policy says `ignoreScripts: true` but explicitly permits an
`esbuild` build; this is a real build/cache and native-platform review surface,
not a zero-dependency closure.

The runtime library declares no npm dependencies, but the exact source has no
prebuilt `dist` and therefore still needs a reviewed build closure if the task
requires agents to reproduce the pinned package. A future authoring decision
must choose and document one of these paths:

- freeze a separate, platform-pinned pnpm build/test closure and add an
  approved pnpm-aware compiler/verifier path; or
- build the artifact in an earlier trusted authoring stage, then publish a
  runtime-only candidate contract with an npm v3 lock/cache closure and an
  exact generated-dist provenance record.

Neither path is implemented here. No pnpm store, npm cache, package tarball,
private lock artifact, or dependency license report was copied or generated in
this task directory. `npm ci --offline` was not run because the source has no
npm lockfile and the current verifier has no pnpm closure protocol.

## Upstream test shape and collection evidence

The source suite is Vitest and imports internal TypeScript modules directly.
A static scan of the exact revision found:

| file | static `it` leaves | special/notes |
|---|---:|---|
| `test/array.test.ts` | 9 | arrays and nested values |
| `test/date.test.ts` | 2 | date offsets and extremes |
| `test/dos.test.ts` | 2 | max-depth aborts |
| `test/error.test.ts` | 7 | one `describe` with code-block cases |
| `test/extract.test.ts` | 2 | internal value extraction |
| `test/inlineTable.test.ts` | 11 | inline tables and duplicate keys |
| `test/key.test.ts` | 6 | key parsing and validation |
| `test/parse.test.ts` | 34 | one `describe` with parser behavior |
| `test/string.test.ts` | 8 | strings and escapes |
| `test/stringify.test.ts` | 28 | one conditional Temporal skip |
| `test/util.test.ts` | 5 | internal cursor/whitespace helpers |
| `test/value.test.ts` | 27 | numbers, dates, special values |
| **total** | **141** | 2 `describe` declarations |

`test/stringify.test.ts` contains one `it.skipIf(!globalThis.Temporal)(...)`
leaf. Thus 141 is a static declaration count, not a frozen Node v2
denominator; the runtime status of that case depends on the exact Node image
and Temporal availability. The test files also contain assertions involving
BigInt, `Infinity`, `NaN`, `Date`/`TomlDate`, Temporal values, functions,
symbols, null/undefined handling, internal parser contexts, and class metadata.
Those assertions cannot be copied unchanged into the generic JSON boundary.

`test/package/package-test.mjs` is a separate non-Vitest package-resolution
smoke test. It checks that ESM and CJS imports resolve under `dist`, verifies
that the default object and named `parse`/`stringify` exports are identical,
and rejects imports that resolve back to the repository source. It is useful
source evidence but is not a `node:test` report and cannot define the v2 leaf
metric.

The repository also advertises an external `toml-test` suite. Its script uses
an external Go binary and a dynamic `go@latest`/`toml-test@latest` resolution;
README notes known semantic gaps such as invalid UTF-8 and certain invalid
calendar dates. This suite is not included in the 141 static Vitest leaves and
must not silently change a future denominator.

No Vitest run or collection report was produced in this audit: the disposable
checkout had Node `22.23.1` and npm `10.9.8`, but no installed Vitest binary, and
installing/hydrating a package cache was outside this static-only task. The
actual `node:test` collection, status policy, report artifact, and fixed
numerator/denominator remain absent.

## JSON-safe contract review (proposal, not frozen)

A bounded JSON child process could represent a deliberately narrowed **root
API** contract, but it cannot represent complete upstream JavaScript parity.
The following is the smallest coherent candidate boundary identified by this
audit:

### `parse`

- Call only the named root export `parse(toml, options?)`.
- `toml` is a UTF-8 JSON string containing a TOML document.
- Permit only JSON-safe options: `maxDepth` as a finite non-negative integer;
  omit `integersAsBigInt` or require it to be `false`.
- Score documents whose returned values are recursively JSON-safe strings,
  booleans, finite safe numbers, arrays, and plain objects. Preserve object key
  order and test prototype-sensitive keys such as `__proto__` through the
  adapter without mutating the host prototype.
- Exclude TOML local/offset dates and times, `nan`, `inf`, and integers that
  require BigInt. `TomlDate` is a `Date` subclass and its identity/type cannot
  cross an ordinary JSON response; BigInt and non-finite numbers cannot be
  encoded by `JSON.stringify` at all.
- Preserve parser errors as a structured child response. At minimum the
  generic boundary can report `TomlError`/`Error` name and message. If hidden
  behavior includes `TomlError.line`, `.column`, or `.codeblock`, a
  task-specific child adapter must return those fields explicitly; the generic
  runner does not expose arbitrary error properties.

### `stringify`

- Call only the named root export
  `stringify(value, { maxDepth?, numbersAsFloat? })`.
- Restrict `value` to a top-level plain JSON object recursively containing
  strings, booleans, finite safe numbers, arrays, nested plain objects, and
  (only if explicitly specified) `null` object members. The pinned behavior
  ignores null/undefined object members and rejects null/undefined array
  members; this distinction must be stated rather than inferred from JSON.
- Restrict `maxDepth` to a finite non-negative integer and
  `numbersAsFloat` to a boolean.
- Exclude BigInt, Date/TomlDate, Temporal objects, `Infinity`, `NaN`, symbols,
  functions, custom prototypes, custom `toJSON`, sparse arrays, and cycles.
- Return the deterministic TOML string. Document JavaScript own-key
  enumeration order; do not promise lexicographic sorting unless a future
  adapter deliberately adds it.

This proposal deliberately omits the exported `TomlDate` and `TomlError`
constructors as callable task APIs, all internal helper exports, Temporal
support, and the BigInt/type-preservation options. It is not a claim that the
full upstream API is JSON-compatible. A private test bundle would need to
trace every assertion to this narrowed contract and freeze a new leaf count.

## Candidate boundary and verifier blockers

The current generic Node runner accepts a bounded JSON request with a package
name, one export name, and JSON arguments; it imports ESM packages when
`require()` reports `ERR_REQUIRE_ESM`, invokes a callable named export in a
child process, and JSON-serializes the response. That is sufficient in
principle for named `parse`/`stringify` **after** a built package is installed,
but it does not solve the following task-specific issues:

1. The upstream tests import `src/*.ts`, construct `ParseContext` objects,
   compare `TomlDate` instances, inspect `TomlError` fields, and use values that
   JSON cannot carry. Direct trusted-process imports would violate the required
   candidate/verifier separation. A child-side scenario adapter and private
   `node:test` tests are required.
2. `parse` can return Date subclasses, BigInt, `NaN`, or infinities. A generic
   `JSON.stringify` response either changes semantics (dates) or fails (BigInt
   and non-finite values). The adapter must reject, tag, or exclude these cases
   before collection is frozen.
3. The package contains a dual ESM/CJS conditional export and no built files in
   source. The verifier must pack and inspect the generated candidate, exercise
   both intended loader conditions, and prevent the candidate from selecting
   the reporter, loader, test root, npm cache, registry configuration, or
   trusted result paths.
4. The exact package metadata contains scripts, and the current package tarball
   validator rejects any `scripts` key. Removing scripts/devEngines or changing
   package metadata is a packaging adaptation that needs an explicit public
   contract and Oracle coverage; it is not performed by this audit.
5. The tracked test-package symlink and internal `.ts` imports cannot be copied
   into a bounded candidate workspace. The eventual adapter must use only the
   installed package root and verifier-owned test assets.
6. The generic request/response size and process limits remain relevant to
   parser denial-of-service cases. The two upstream `dos` tests and any larger
   benchmark documents need an explicit bounded-input policy rather than being
   silently omitted or counted.

No candidate package, separate verifier, command plan, private test bundle,
Oracle, negative control, or structured Node report exists for this task.

## Blocking findings and reopen conditions

Keep this lane **blocked**. The blockers are:

- the frozen implementation is TypeScript and has no `dist`; exact ESM/CJS
  package behavior cannot be reproduced without a locked build stage;
- the source uses pnpm lockfile v9 and a pnpm 11.21 toolchain, while the current
  Node v2 compiler/closure validator is npm v3 + npm 10.9.8;
- the build/test closure includes platform/native optional packages and an
  explicit esbuild build allowance; no reviewed content-addressed closure or
  platform-specific image evidence exists;
- `npm pack` in the requested Node/npm environment fails the package-manager
  `devEngines` gate, and the source package declares scripts rejected by the
  candidate tarball validator;
- the upstream test framework is Vitest with 141 static leaves, not
  `node:test`; no exact collection report or fixed denominator exists;
- the complete upstream surface crosses the generic JSON boundary through
  dates, BigInt, non-finite numbers, Temporal, class/error metadata, and
  internal module imports; and
- no task-specific adapter, private command/test artifacts, separate verifier,
  controls, or Oracle evidence is authorized or present.

Reopen only after all of the following are separately reviewed:

1. an owner-approved build/packaging strategy (pnpm-aware build closure or a
   trusted prebuilt-dist/runtime split) with exact Node/tool versions and
   repeated output hashes;
2. a content-addressed, platform-reviewed dependency artifact, with any npm
   v3 conversion explicitly justified and no unreviewed native/build scripts;
3. a public JSON contract for parse/stringify, including date/BigInt/non-finite
   exclusion or tagged normalization and structured `TomlError` behavior;
4. a child-side adapter that never imports candidate code in the trusted test
   process and a verifier-owned `node:test` rewrite of the selected assertions;
5. fresh collection in the final image with a stable frozen denominator and
   `node-test-json-v1` report semantics; and
6. only then, the required Oracle, empty/stub/forgery/offline/install-script,
   loader, and hang controls in a later validation stage.

Do not publish this candidate, add it to the Python dataset, claim Harbor
parity, or run Oracle from this blocked record.

## Commands and evidence run

Static evidence was gathered with public source metadata and a disposable
checkout:

```text
GIT_TERMINAL_PROMPT=0 git clone https://github.com/squirrelchat/smol-toml.git /tmp/smol-toml-audit
git -C /tmp/smol-toml-audit checkout --detach 6d0f4774700c40ce8b5794934eb771870a9a93d3
git -C /tmp/smol-toml-audit rev-parse HEAD
git -C /tmp/smol-toml-audit show -s --format=... HEAD
git -C /tmp/smol-toml-audit archive --format=tar HEAD | sha256sum
git -C /tmp/smol-toml-audit ls-tree -r --name-only HEAD
git -C /tmp/smol-toml-audit submodule status
node <static package/API inventory script>
node <static Vitest declaration-count script>
git grep -nE '^(import|export)|it/describe' -- src test
npm view smol-toml@1.8.0 dist.integrity dist.tarball --json
npm pack --dry-run --ignore-scripts --json
```

The static inventory, hash, and grep commands completed. The final pack
command was **not** a successful package validation: npm `10.9.8` returned
`EBADDEVENGINES` because the source requires pnpm `11.21.0` while the command
uses npm; it also reported the Node `^26` development-runtime mismatch.

Intentionally not run for this static-only audit:

```text
pnpm install / pnpm test
just build / npm ci
Docker or Harbor compilation
Oracle, hidden tests, negative controls, or a candidate installation
```
