# `fast-glob` Node v2 authoring audit — blocked

**Status: blocked.** This is a task-local authoring evidence record, not a
Harbor task or a production dataset entry. It contains no hidden tests, private
bytes, dependency cache, Oracle solution, Docker artifact, credentials, or
shared-index changes. No Oracle, control, or model evidence exists for this
candidate; none is claimed.

## Candidate lock and license evidence

- Package: `fast-glob` `4.0.0`
- Upstream: <https://github.com/mrmlnc/fast-glob>
- Frozen revision: `467b65a79ed1b84fd9fd18966deda8a4e57b8e0e`
- Commit subject: `Merge pull request #506 from mrmlnc/bench_extra`
- Commit timestamp: `2026-08-22 17:08:05 +0300`
- Commit tree: `fda844a9814227d7879a1fc9d496f84e31a42936`
- Detached checkout was clean; 128 tracked files.
- `git archive --format=tar HEAD | sha256sum` (repeated three times, identical):
  `becf5ae57d324fb632a7762a619a0625f566e8f2e89a3b5c55311ea394175b9a`
- `LICENSE` is the MIT license, 1,069 bytes, SHA-256
  `f735badf5add8c6d340f0b63884abb5c4f73b496839a0af2c9957fd69ad554e6`
- `package.json` SHA-256:
  `757d9fcd062288f2c3876f384358d5c1a1922d278df27ae7aa0016dbaa78edd0`
- `.npmrc` (19 bytes) contains exactly `package-lock=false`; no lockfile is
  committed at this revision.

The source lock is suitable for a further authoring attempt. It is not an
approval to publish or to claim upstream/package parity through the current
Node verifier.

## AST inventory (tools/node-inventory)

Scanner: `@nl2repobench/node-inventory` 0.1.0 (TypeScript compiler API, no
candidate code executed). Audit host ran Node `26.7.0` / npm `12.0.2`, which
does **not** match the production lock (Node `24.19.0` / npm `11.17.0` in
`toolchain.node.lock.toml`); every observation below is development evidence.

- `source_digest`:
  `sha256:95f865395cd60b75b7d5c059acdc19196b7ace48a4843754f7e2a30c0320930c`
- `implementation_loc` 8,125; `test_loc` 3,900; 54 source files; 47 test files;
  179 public symbols; 357 imports; 0 syntax diagnostics; no `bin` entries.
- `risk_flags`: `dynamic-import`, `filesystem-access`, `process-access`.
  - `dynamic-import` is confined to `src/benchmark/utils.ts:23-41` and
    `src/benchmark/suites/overhead/*.ts` (bencho suites).
  - `process-access` (`node:child_process`, `execa`) is confined to
    `herebyfile.mjs` and the benchmark tree.
  - The runtime library itself imports only `node:fs`, `node:path`, `node:os`,
    `node:stream`, `node:process`, and the five declared runtime dependencies.
  - No `native-addon`, `external-service`, or `generated-code` flags; no
    `gypfile`/`binary`/`os`/`cpu` fields in `package.json`.

Runtime dependencies (all pure JS): `@nodelib/fs.stat`, `@nodelib/fs.walk`,
`glob-parent`, `merge2`, `micromatch`. Engines: `^22.13.0 || >=24`
(compatible with the production Node 24.19.0 lock).

## Public API shape

`src/index.ts` exports directly callable functions `glob`, `globSync`,
`globStream`, deprecated aliases `async`/`sync`/`stream`, `generateTasks`,
`isDynamicPattern`, `escapePath`, `convertPathToPattern`, plus **namespace
objects** `posix` and `win32` (each with `escapePath` /
`convertPathToPattern`). Options (`src/settings.ts:14-146`) include
JSON-friendly fields (`absolute`, `baseNameMatch`, `braceExpansion`,
`caseSensitiveMatch`, `cwd`, `deep`, `dot`, `extglob`, `followSymbolicLinks`,
`globstar`, `ignore`, `markDirectories`, `objectMode`, `onlyDirectories`,
`onlyFiles`, `stats`, `suppressErrors`, `throwErrorOnBrokenSymbolicLink`,
`unique`) and non-JSON fields (`fs` adapter of functions, `signal:
AbortSignal`).

## Blocking findings

### Blocker — TypeScript source requires a build step the production contract forbids

The exact revision is TypeScript-only (`src/**/*.ts`; `package.json` `main:
"out/index.js"`, `files: ["out", ...]`). The `out/` tree does not exist in the
frozen tree; producing the installable package requires running `tsc`
(`scripts.compile` / `scripts._build:compile`). The production contract and
`docs/node-foundation-plan.v1.md` prohibit executing lifecycle/build scripts in
the verifier lane, and TypeScript is explicitly out of scope for the current
slice. An Oracle bundle would have to be a pre-compiled, scripts-stripped
adaptation of upstream — an unapproved packaging/architecture decision this
audit does not make.

### Blocker — no freezable public-API denominator exists yet

- The 14 e2e suites (`src/tests/e2e/**/*.e2e.ts`) generate their leaf tests at
  **runtime** through `runner.suite()` (`src/tests/e2e/runner.ts:46-83`),
  emitting three leaves (`sync`/`async`/`stream`) per declared entry. The
  static AST scan sees only the runner template (1 declaration), so a frozen
  denominator cannot be derived from static evidence; it requires a runtime
  collection under the locked toolchain, which was not run here.
- Assertions are snapshot-based via `snap-shot-it`
  (`src/tests/e2e/runner.ts:186-199`, `__snapshots__/*.e2e.js`), keyed by
  JSON-stringified titles. A private `node:test` bundle must materialize every
  expected value from the snapshots — an authored rewrite that needs blind
  review, not a mechanical adaptation.
- Of the 400 static Mocha declarations, roughly 399 target internal modules
  (`src/providers/**`, `src/readers/**`, `src/managers/**`, `src/utils/**`,
  `src/settings.spec.ts`, `src/index.spec.ts` with sinon/`@nodelib/fs.macchiato`
  mocks). These are not observable through the public package boundary and
  cannot become hidden assertions without leaking implementation structure.

### High — upstream `package.json` is rejected by the package lifecycle validator

`package.json` declares `prepublishOnly` (`scripts` block, line 90). The Node
runtime package validator
(`src/nl2repobench/verification/node/validate-package.mjs:40-53`) rejects any
lifecycle hook including `prepublishonly` (exit 71). A candidate- or
Oracle-generated package must omit it — an explicit, testable adaptation that
must be stated in the spec, not silently applied.

### High — no committed lockfile; offline v3 closure not produced

`.npmrc` pins `package-lock=false` and no `package-lock.json` exists. A
reviewed npm v3 lock plus offline cache closure generated with the exact
production npm `11.17.0` is required and was **not** produced: the audit host
has npm `12.0.2`, so any lock generated here would not be a production
artifact. The five runtime dependencies and their transitive closure are pure
JS per package metadata, but offline reproducibility is unproven.

### High — the JSON child boundary excludes part of the observable API

`src/nl2repobench/verification/node/candidate_runner.mjs` accepts one bounded
JSON request (64 KiB) and one bounded JSON response (256 KiB) and only invokes
a **directly callable** export:

- `globStream` returns a `ReadableStream`; one of every three e2e leaves is the
  stream variant and cannot cross the JSON boundary.
- `posix`/`win32` are namespace objects; `candidate["posix.escapePath"]` does
  not resolve, so those four functions are not invocable (same class as the
  `query-string` blocker, though here the primary API is directly callable).
- `objectMode`/`stats: true` results contain `fs.Dirent`/`fs.Stats` instances
  whose JSON serialization is not a defined contract.
- The `fs` adapter (functions) and `signal` (`AbortSignal`) options cannot be
  expressed in JSON; every upstream test using them is out of boundary.

### Medium — filesystem fixture protocol is undefined

E2e behavior depends on the committed `fixtures/` tree (12 files including
dot-entries `.file` and `.directory/`) resolved relative to `process.cwd()`,
and `src/tests/e2e/errors.e2e.ts` plus symlink-related options require
runtime-created fixtures. Hidden `node:test` files would need an approved
bounded fixture-materialization protocol (temp trees plus explicit JSON `cwd`)
under the child boundary; `run_tests.mjs` currently fixes the child cwd to the
candidate site. Result ordering is not guaranteed by the library; upstream
sorts before asserting and any adapter must do the same.

### Medium — audit toolchain mismatch

All commands ran under Node `26.7.0` / npm `12.0.2`, not the locked production
Node `24.19.0` / npm `11.17.0`. No observation here may be promoted to
production evidence without re-execution under the locked image.

## Not run (explicitly)

- npm lock/cache generation, `npm ci --offline`, `npm pack`, package
  validation execution, Docker/Harbor compile, Oracle, and every control run.
  These are prohibited while the blockers above stand; no results are claimed.

## Required unblock actions

1. Approve the TypeScript handling decision: pre-compiled scripts-stripped
   Oracle adaptation, or reject TS-source candidates for this slice.
2. Approve a public-API-only scope (JSON-safe `glob`/`globSync`/
   `generateTasks`/`isDynamicPattern`/`escapePath`/`convertPathToPattern`
   subset), the exclusion or adaptation of `globStream`, `posix`/`win32`,
   `objectMode`/`stats`, `fs`, and `signal`, and a bounded fixture/cwd
   protocol for filesystem assertions.
3. Author and review a private `node:test` bundle with materialized snapshot
   expectations, then freeze a new runtime-collected denominator under the
   locked Node 24.19.0 image.
4. Produce a reviewed npm v3 lock and offline cache closure with exact npm
   `11.17.0`, and define the lifecycle-script-stripping packaging adaptation.
5. Only then compile, run one Oracle gate, and run the
   empty/stub/forgery/install-script/loader-hook/hang/offline controls.

## Current v2 revalidation

The source and private artifact references were revalidated in the locked Node
lane after the historical blockers above were recorded. This addendum is
evidence only; it does not claim publication approval or replace review/pilot
gates.

- `uv run nl2repo task validate-source catalog/sources/fast-glob` passed.
  The validator reported task `fast-glob`, version `0.1.0`, lifecycle status
  `controls-passed`, and source content digest
  `sha256:3942bcc242b8e70ddb0bc42d8a0b14418951f4a98d605ad0f67091af6ea3605f`.
- Production compilation passed without `--allow-incomplete` using
  `toolchain.node.lock.toml`, `--allow-private`, and
  `.nl2repo/artifacts`; output was written to a temporary directory outside
  the catalog source. No compiler or schema failure remains for this source.
- The declared production bundle path
  `catalog/tasks/fast-glob/bundle.manifest.json` exists and hashes to the
  declared `sha256:54d540fa9c2b0dbe5bf6c15340dd3c283a89b380209d6d393090501363a279da`.
- Every path in `production-evidence.json` was present and its bytes matched
  the declared SHA-256: all four grading records, the shared network probe,
  and the bundle manifest.
- The four private artifact references used by the source were present in
  `.nl2repo/artifacts/private/` and matched their declared digests: dependency
  bundle `4ff767f70cfda06d60fbd4e9ee866c75437de276004a049c2925041101e9ca0b`,
  command bundle `ae0d5dc22c9d5bf46ee967a7fffef897063c31a78046afc47d753287d5a61081`,
  test bundle `56428100ac69806e55c009c8465c530d88dd3021637e8a33dc4c8d21793e5854`,
  and Oracle bundle `e448c9fec7a1a8809a6ec6dda68be55673e54cca44f391a770b6beceaa8558d0`.

No source-local remediation was necessary. The historical TypeScript,
denominator, lifecycle, lock/cache, and JSON-boundary findings remain
authoring-history context and should not be treated as current compiler
failures; any remaining publication work is review/pilot or production
execution policy, not a fast-glob source/schema defect.
