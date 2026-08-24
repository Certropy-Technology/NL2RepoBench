# `csv-parse` static Node v2 pilot audit

**Status: `specified` / development-only; publication blocked.** This is a
static authoring record for the exact candidate revision. It contains no
upstream test bytes, hidden/private tests, private command plan, npm cache or
tarball closure, Dockerfile, verifier, Oracle, reward, secret, or shared
dataset edit. The only proposed score surface is the `csv-parse/sync`
subpath; the root, stream, browser, callback, and sibling workspace packages
are out of scope.

The static audit answers the candidate report's deferral question as follows:
**the sync-only runtime boundary is feasible**, but the upstream monorepo test
and build closure must not be carried into a Node v2 task. A future task can
use a separately authored JSON-compatible `node:test` adapter and a
standalone zero-runtime-dependency package closure. This record does not
advance the candidate to `packaged`, `oracle-passed`, or `published`.

## Candidate and immutable source lock

The candidate was selected from `reports/npm-package-candidates.v1.md`.

- Package: `csv-parse`.
- Upstream repository:
  `https://github.com/adaltas/node-csv`.
- Requested and resolved revision:
  `3591c0770f7235b203f7cbcd7805ddedfaaf3ce1`.
- Commit tree: `ff6f8187b39704546029aad8e682331eb5e5b6b1`.
- Commit subject/date: `chore(release): publish`,
  `2026-08-05T10:26:41+02:00`.
- Parent: `3a8063d0b8d00182c9ca88a35a766c01f870a12b`.
- The detached checkout had no submodules and was clean after inspection.
- `git archive --format=tar HEAD` was 9,523,200 bytes with SHA-256
  `59008cce99e32cf346af17ef0de740f1067db994043fd5819e58b4c511fe48d9`.
  Two independent archive commands produced the same digest.

License evidence is internally consistent:

- `LICENSE` is 1,074 bytes, Git blob
  `918eaf05a443125297545c5064475e6dcd4c83f8`.
- The license file SHA-256 is
  `032efe3de772e9f85c722ee9ff7ccd5cab01e024296b2b8d25893bf779be9360`.
- `packages/csv-parse/package.json` declares `MIT`; the package is not
  independently relicensed by this audit.
- The locked package manifest is 4,474 bytes, Git blob
  `4e0d8bdeb20878a1f1bdabf2daec56f23fd7448f`, with SHA-256
  `33b8d521425dae25b51242b73d6aa5194ca1112c8b69f98f13110fbedaf15cec`.

The source archive and source hashes are provenance observations only. No
source archive or source file was copied into this task directory.

## Workspace and monorepo boundary

The upstream checkout is an npm workspace monorepo, not a standalone
`csv-parse` repository:

- The root manifest is private and declares workspaces `packages/*` and
  `demo/*`, with a `nohoist` rule for Browserify packages.
- There are 14 workspace manifests: five package workspaces
  (`csv`, `csv-generate`, `csv-parse`, `csv-stringify`, `stream-transform`) and
  nine demo workspaces.
- Root scripts use Lerna for build, test, version, and publish. The root
  `.npmrc` sets `legacy-peer-deps=true`.
- The root `package-lock.json` is lockfile v3 with 1,369 `packages` entries.
  It contains 18 non-`node_modules/` workspace paths and 14 local workspace
  link entries. The root lock also contains 63 OS-marked entries, 62
  CPU-marked entries, and four install-script entries from unrelated tooling.
- The root lock cannot be passed to the repository's Node dependency
  validator. A temporary validator probe failed closed at
  `demo/browser` with `invalid package path in lockfile`; it also contains
  local links and platform packages that are outside the v2 dependency
  contract.
- The root package is private and has no usable standalone package identity;
  attempting to pack from the root failed with npm's `Invalid package, must
  have name and version`. Packing from the package directory succeeds.

The `packages/csv-parse` workspace itself has no runtime `dependencies`,
`optionalDependencies`, or `peerDependencies`. Its 17 declared
`devDependencies` include the sibling workspaces `csv-generate` and
`stream-transform`. The full root lock therefore proves neither an isolated
candidate lock nor an isolated test closure.

A second boundary leak is observable in the test configuration: the package
Mocha configuration requests the `tsx` loader, but `tsx` is not a direct
`csv-parse` dev dependency. In the monorepo, `npm ls --workspace
packages/csv-parse tsx` resolves it through the sibling `stream-transform`
workspace. A package-only copy with the same manifest generated a 309-entry
lock without `tsx`; after `npm ci --ignore-scripts`, its upstream `npm test`
failed at collection with `Cannot find package 'tsx'`. This is a monorepo
closure defect, not a sync runtime defect.

### Isolated sync runtime graph

A recursive import walk rooted at `packages/csv-parse/lib/sync.js` reached ten
local JavaScript files:

```text
lib/sync.js
lib/api/CsvError.js
lib/api/index.js
lib/api/init_state.js
lib/api/normalize_columns_array.js
lib/api/normalize_options.js
lib/utils/ResizeableBuffer.js
lib/utils/delimiter_discover.js
lib/utils/is_object.js
lib/utils/underscore.js
```

The walk found no third-party import and no sibling workspace import. The
implementation uses the Node `Buffer` global and local code only; it has no
native addon, filesystem, network, subprocess, loader, or dynamic-code
requirement on this path. The reachable source graph is 69,795 bytes and
2,070 physical lines. No tracked `.node`, `binding.gyp`, prebuild, symlink, or
WASM file occurs under the package tree.

This is the basis for the narrow scope decision: **copy/implement only the
`csv-parse/sync` behavior and its local parser graph; do not include the
monorepo root, demos, Lerna, or sibling CSV packages.**

## Package metadata and export audit

The locked package is `csv-parse` version `7.0.2`, ESM by default, with no
runtime dependencies. The upstream manifest does not declare an `engines`
constraint; Node `22.23.1` and npm `10.9.8` are therefore task-level locks,
not upstream compatibility claims. It declares `files: ["dist", "lib"]` and
the following export keys:

```text
.
./sync
./stream
./browser/esm
./browser/esm/sync
```

The relevant conditional export is:

```text
./sync (import)  -> ./lib/sync.js
./sync (require) -> ./dist/cjs/sync.cjs
```

`./sync` exposes named `parse`, `CsvError`, and `normalize_options` bindings
under both conditions. It does **not** provide a meaningful default binding;
`import * as sync` and CommonJS `require("csv-parse/sync")` both expose the
named keys. The future scored contract should call the named `parse` export,
not assume a default export.

The source and generated sync artifacts were syntax-checked on Node
`22.23.1`:

- reachable `lib` graph and sync bundles: `node --check` passed for 12 files;
- `dist/cjs/sync.cjs`: 68,234 bytes;
- `dist/esm/sync.js`: 122,302 bytes;
- the source `lib/sync.js` and generated CJS sync bundle returned identical
  JSON observations for ordinary CSV, delimiter, columns, cast, info, raw,
  BOM, trim, delimiter discovery, and `objname` probes;
- a temporary package-only pack/install probe loaded `csv-parse/sync` through
  both ESM import and CommonJS require and produced
  `[ ["a","b"], ["1","2"] ]` from `parse("a,b\\n1,2")`.

The other export keys are deliberately not part of this pilot. In particular,
`./stream` requires stream/event state and `./browser/*` adds a browser
projection; including either would widen the task beyond the requested sync
surface.

## Upstream test and build evidence

The source test suite is Mocha/TypeScript, not the Node v2 `node:test`
contract:

- 90 tracked test files: 40 JavaScript and 50 TypeScript files;
- the package script is
  `npx tsc --noEmit && mocha 'test/**/*.{js,ts}'`;
- the full source run under Node `22.23.1` / npm `10.9.8`, with network and
  audit/fund disabled after a temporary development install, completed with
  **608 passing, 3 pending, 0 failures**;
- two independent JSON-reporter runs both reported 164 suites, 611 tests,
  608 passes, 3 pending, and 0 failures. The stable pending tests are the
  stream-abort and stream-performance cases:
  `API stream.finished aborted (with Readable)`, `api stream perf classic`,
  and `api stream perf stream`.
- A selected five-file sync-adjacent slice (`api.sync.ts`,
  `api.types.sync.ts`, `option.delimiter_auto.ts`, `option.objname.ts`, and
  `spectrum.js`) reported 43 passing. It intentionally includes validation,
  callback/stream, buffer, and type checks, so **43 is not a proposed frozen
  denominator**.

Only five source test files import `lib/sync.js` directly. The explicit sync
behavior is mixed with non-JSON values and callbacks:

- `api.sync.ts` covers string, `Buffer`, `Uint8Array`, columns, `on_record`,
  `objname`, `to_line`, and errors;
- `api.types.sync.ts` is primarily TypeScript signature/type coverage;
- `option.delimiter_auto.ts` contains two sync cases and several stream cases;
- `option.objname.ts` contains one sync prototype-safety case among callback
  tests; and
- `spectrum.js` uses the external `csv-spectrum` and `each` packages.

The complete 611-test Mocha result is source-baseline evidence only. It is not
a `node:test` collection, not a private test bundle, not an Oracle run, and
not a v2 denominator. A future authoring stage must write a private,
`node:test`-compatible sync adapter and collect its leaf denominator in the
final locked environment.

The package scripts also need an explicit scope policy:

- `build:rollup` invokes `npx rollup -c`;
- `test` invokes `npx tsc --noEmit`;
- `preversion` builds and stages generated `dist` files;
- the package manifest contains a `scripts` object, and the Node package
  validator rejects the unmodified packed package with
  `candidate lifecycle scripts are forbidden` (Node validator exit 71);
- root `prepare` runs Husky and root build/test/publish scripts are Lerna
  commands.

A candidate package for this pilot must therefore contain no lifecycle or
arbitrary scripts, no `npx` download path, and no workspace declaration. The
prebuilt upstream package is evidence of export shape, not an artifact that
can be copied into a production candidate unchanged.

## npm lock and cache closure

There is no package-local committed `package-lock.json` at the locked source;
only the monorepo root lock is tracked. The package has no runtime dependency
roots, so an isolated **runtime-only** lock is technically straightforward,
but it still needs to be generated and content-addressed by the later
artifact stage.

Temporary, non-repository probes demonstrate the distinction:

1. A metadata-only package copy with runtime dependencies and dev tooling
   removed generated an npm 10.9.8 lockfile v3 containing only the root entry.
   Its lock SHA-256 was
   `85cc5f9c88de9e07c92372af8a8cdbdba8b219d25d10ebe3e9111c666109c765`.
   `npm ci --offline --ignore-scripts --no-audit --no-fund` succeeded with an
   empty cache. A matching temporary bundle manifest was accepted by
   `validate_npm_dependency_bundle(..., expected_npm_version="10.9.8")`.
2. A package-only lock retaining all 17 development dependencies had 309
   package entries and SHA-256
   `4b7b38ca1e4f8d329cc984899f6ba81a79509a5269ae62dcd5a93377a42f9e43`.
   It had no `tsx`, had a missing-integrity `node_modules/dedent` entry, and
   included the platform package
   `node_modules/@napi-rs/lzma-linux-x64-gnu` through Rollup. The repository
   dependency validator rejected that closure as a native/platform package.
3. The full monorepo lock was rejected even earlier because its workspace
   paths are not valid package entries for the v2 bundle schema.

These probes establish feasibility of a zero-runtime-dependency sync task,
not completion of the required closure. No generated lock, cache, tarball, or
bundle manifest is stored here. Before packaging, the authoring pipeline must
produce and review a standalone v3 lock/cache artifact with exact npm
`10.9.8`, `offline` mode, `ignore-scripts`, registry provenance, SHA-512
integrity for every member, and no platform/native package.

## JSON subprocess boundary

The generic Node candidate boundary can invoke this surface as:

```json
{
  "package": "csv-parse/sync",
  "export": "parse",
  "args": ["a,b\n1,2", {"columns": true}]
}
```

The current child boundary limits requests to 64 KiB, responses to 256 KiB,
and 32 positional arguments. It runs the candidate in a separate Node child
process with `NODE_PATH`/custom `NODE_OPTIONS` removed and supports both
CommonJS and ESM resolution. Ordinary string input, columns, delimiters,
Unicode, `info`, `raw`, `cast: true`, `objname`, and plain object/array records
were observed to serialize as JSON successfully.

The proposed JSON-only scope must be explicit:

**In scope**

- CSV input as a UTF-8 string; bounded input and output sizes;
- a plain options object;
- booleans, finite numbers/integers, strings, `null`, arrays, and plain
  objects in options;
- string forms of `comment`, `delimiter`, `escape`, `quote`, and
  `record_delimiter` (including arrays where the API accepts them);
- boolean/finite-number options such as `bom`, `cast`, `columns`, `from`,
  `from_line`, `group_columns_by_name`, `ignore_last_delimiters`, `info`,
  `max_record_size`, `raw`, the relax/skip/trim flags, `to`, and `to_line`;
- `columns` as `true`/`false` or a JSON array of string/number/null/false
  column definitions, but not a callback;
- `delimiter_auto` as a JSON configuration containing only its preferred
  numeric map and size; its internal scoring callback remains implementation
  state and is not supplied by the request; and
- JSON-array/object/string/boolean/number results, including null-prototype
  `objname` maps after JSON serialization.

**Out of scope unless a reviewed adapter defines a projection**

- `Buffer`, `Uint8Array`, typed arrays, and `encoding: null` binary results;
- callback-valued `cast`, `cast_date`, `columns`, `on_record`, `on_skip`, and
  `delimiter_auto.score` options;
- `Date` objects produced by `cast_date: true` (JSON.stringify would turn
  them into strings, but that is a projection decision, not transparent API
  parity);
- `CsvError`, `Parser`, `normalize_options`, stream objects, and browser
  globals as directly invoked exports;
- cycles, symbols, BigInts, functions, RegExp values, custom prototypes, and
  non-finite numbers; and
- any source or result that exceeds the child request/response bounds.

Parser failures are `CsvError` instances with a stable `code`, message, and
optional context. The current generic child runner normalizes an exception to
only `exception_type` and `message`; it does not return `code` or context.
The private sync adapter must either restrict assertions to the generic error
projection or add a reviewed JSON error projection before any denominator is
frozen. It must never let an untrusted candidate write the report or reward.

## Node validator and packaging probes

The locked development runtime matches the Node v2 foundation lock:

```text
node --version  -> v22.23.1
npm --version   -> 10.9.8
```

The unmodified upstream package tarball produced by
`npm pack --ignore-scripts` contains 32 files and exposes the expected sync
conditional exports, but the Node package validator rejects it because the
manifest retains the upstream `scripts` object. A temporary metadata-only
copy with scripts, dev dependencies, and build/test metadata removed:

- generated a root-only lock;
- installed with `npm ci --offline --ignore-scripts --no-audit --no-fund`;
- packed successfully;
- passed both the Node `validate-package.mjs` check (exit 0) and the Python
  dependency/package policy check; and
- loaded and called the named `parse` export through ESM and CommonJS.

This is a compatibility probe, not a candidate solution or a committed
artifact. It shows that the requested sync boundary can satisfy the current
validator if the future task explicitly requires a clean package manifest.

## Decision and reopen gates

Retain `csv-parse` as a **sync-only, development-only static pilot**. Do not
create a Harbor bundle or add a dataset entry from this evidence. The next
stage may author a public task source only after the following are resolved:

1. Freeze the task contract to package `csv-parse`/`./sync` and named `parse`,
   with ESM and CommonJS export probes; exclude root/stream/browser APIs and
   all sibling workspaces.
2. Generate a standalone npm v3 runtime lock/cache closure under npm
   `10.9.8`; do not reuse the monorepo lock or the temporary metadata-only
   lock hash above as a production artifact.
3. Add a private adapter-owned `node:test` bundle whose every assertion is
   traceable to the JSON scope, with automatic collection and a frozen leaf
   denominator. Do not copy the upstream Mocha/TypeScript tests or
   `csv-spectrum` fixtures into this public directory.
4. Define the JSON error projection, binary/date policy, output bounds, and
   option aliases before review; keep callback/stream state out of the task.
5. Require candidate packages to omit scripts, workspaces, registry config,
   native addons, loaders, and `npx` downloads; verify the packed tarball and
   both export conditions in the separate verifier.
6. Run the Node Oracle/control matrix only in the later approved stage:
   three valid stable Oracle runs, empty/stub, forged-report, install-script,
   loader, hang, and offline controls. None of those runs was performed here.

No Docker command, Harbor compile, Oracle trial, hidden/private artifact
materialization, shared catalog/index update, or secret use occurred in this
audit.
