# `ajv` Node/npm authoring audit - blocked

**Status: blocked / audit-only.** This file is a task-local evidence record
for a possible Node/npm candidate. It is not a `task.toml`, public task
instruction, Harbor bundle, publication approval, hidden-test package, Oracle,
verifier, Docker asset, dependency cache, or shared catalog update. Only this
file is intentionally present under `catalog/tasks/ajv/`.

The source and license gates are sufficiently identified for continued
authoring review, but the package is not currently reproducible as an exact
commit in the repository's Node contract. The missing generated distribution,
missing npm lock/cache closure, script-bearing package metadata, incomplete
official-test execution, and absent task-specific JSON adapter are blocking
findings rather than reasons to guess a release artifact or denominator.

## Candidate Lock

- Package: `ajv` `8.20.0`.
- Upstream: `https://github.com/ajv-validator/ajv`.
- Resolved full commit: `f177fe323420ccb23e1a79445fd470cbf80aee7c`.
- Commit tree: `38378e369677957a50cde3e0673a94b4c7918621`.
- Commit subject: `ci: use separate token to push to ajv-dist (#2608)`.
- Commit author and committer time: `2026-04-24T14:46:21+01:00`.
- `git describe --tags --always --long HEAD`: `v8.20.0-1-gf177fe3`.
- Tag `v8.20.0` is the parent release commit
  `0fba0b8e649909613cfce0999b149cd08f4a4987`; the requested commit is one
  commit after that tag, not the registry release object.
- The detached checkout had no local modifications. It has 488 tracked
  files; the unprefixed Git archive has 550 members, including directory
  entries.
- Three independent `git archive --format=tar HEAD` runs each produced
  3,799,040 bytes and SHA-256
  `54cc5df21593d589cd905b5a9a85161c08e8fa07d10cf8739ee056ed1d12a893`.
- The superproject records two gitlinks, not embedded test sources:
  `spec/JSON-Schema-Test-Suite` at
  `e82bfdfa59c63cc74175d35fac81bb95e61db24b` and
  `spec/json-typedef-spec` at
  `71ca275847318717c36f5a2322a8061070fe185d`. The exact objects were
  reachable from their public repositories in a disposable checkout, but no
  submodule bytes were copied into this task directory.

### License evidence

The exact commit has an MIT license declaration in `package.json` and the
standard MIT text in `LICENSE`:

- `LICENSE`: 1,090 bytes, Git blob
  `139162ad2c389a18d3d66e159a2821b2e40087fc`, SHA-256
  `a05350a88e318e4f5f2c2a1ff1e2e88daa4dd38e6e78b71cccae422bdc762cc3`.
- `package.json`: Git blob
  `50fa6a639c704492f0a6c0c28a3c86d20321a395`, SHA-256
  `1f9033ee5a6515e7d76938b7072941862d1ed228a6879cc7fe10cdeb75107989`.
- The package metadata names `MIT`, repository `ajv-validator/ajv`, main
  `dist/ajv.js`, and types `dist/ajv.d.ts`.

This establishes source-license eligibility only. It does not approve the
licenses or provenance of the future build/test dependency closure.

The public registry metadata for `ajv@8.20.0` reports `gitHead`
`0fba0b8e649909613cfce0999b149cd08f4a4987`, integrity
`sha512-Thbli+OlOj+iMPYFBVBfJ3OmCAnaSyNn4M1vz9T6Gka5Jt9ba/HIR56joy65tY6kx/FCF5VXNB819Y7/GUrBGA==`,
and the MIT license. That `gitHead` is the release tag commit, not the
locked `f177fe3` commit. The registry tarball must not be substituted for the
requested source revision without a separate provenance decision.

## Source-Only LOC

The source-only boundary is the 106 tracked TypeScript files under `lib/`.
It excludes `spec/`, documentation, build configuration, scripts, generated
output, and the 19 tracked JSON reference documents. A read-only scanner over
that exact set reports:

| source boundary | files | physical lines | nonblank | noncomment |
|---|---:|---:|---:|---:|
| `lib/**/*.ts` | 106 | 9,862 | 8,797 | 8,536 |

The package is therefore a substantial TypeScript implementation, not a
small zero-dependency JavaScript utility. The JSON reference documents are
part of the runtime source inputs but are intentionally not counted as
source LOC.

## Runtime And Build

The repository's Node toolchain record is explicitly development-only. It
records the following intended runtime profile:

```text
image:    docker.io/library/node@sha256:8607a9064d4a571140998ae9e52a3b3fcf9cff361d04642d5971e6cd76d39e27
platform: linux/amd64
libc:     glibc
node:     22.23.1
npm:      10.9.8
```

The host probes matched Node `v22.23.1` and npm `10.9.8`. The lock file for
this repository's toolchain is `toolchain.node.lock.toml`, SHA-256
`dbc2fc03d61713a9100bc66b29cdd350cdea10cbed5ccb5aa9d4e1b09ee7498e`; its
status remains `development-only`, so this is not final image evidence. The
upstream CI matrix tests broad `18.x`, `20.x`, `22.x`, and `24.x` ranges with
`npm install`; it does not pin the requested Node patch or prove offline
behavior.

The exact package metadata has:

- no `type`, `exports`, or `module` field;
- CommonJS-style generated entry point `main: "dist/ajv.js"`;
- declarations at `dist/ajv.d.ts`;
- published paths `lib/`, `dist/`, and `.runkit_example.js`;
- four runtime dependency ranges: `fast-deep-equal`, `fast-uri`,
  `json-schema-traverse`, and `require-from-string`;
- 40 development dependency ranges, including TypeScript `5.3.3`, Mocha,
  `ts-node`, `cross-env`, `nyc`, Rollup, Browserify, Karma, `ajv-formats`,
  and the native-addon package `re2`; and
- 20 npm scripts, including build, test, browser, link, publish, and site
  operations.

The build script is:

```text
rm -rf dist && tsc && cp -r lib/refs dist && \
  rm dist/refs/json-schema-2019-09/index.ts && \
  rm dist/refs/json-schema-2020-12/index.ts && \
  rm dist/refs/jtd-schema.ts
```

`tsconfig.json` writes to `dist`, targets ES2018, resolves JSON modules, and
extends the external `@ajv-validator/config` package. The exact checkout has
no `dist/`, `node_modules/`, or generated bundle. Consequently its package
entry point is not loadable from the source checkout:

```text
require(source checkout) -> MODULE_NOT_FOUND: .../dist/ajv.js
```

`npm pack --dry-run --ignore-scripts --json` reports 129 files, 355,682
unpacked bytes, and an 85,621-byte tarball estimate. The listing contains
`lib/` TypeScript and JSON sources but no `dist/ajv.js` or `dist/ajv.d.ts`.
The package is therefore not an exact runnable distribution until a trusted,
repeatable build is frozen.

The build probe on Node 22 exited 127 because the exact source checkout has
no `tsc` executable. This is a missing toolchain observation, not a source
failure. A generated package was not retained.

The current candidate tarball policy rejects a manifest containing a
`scripts` key. Running the repository's `validate-package.mjs` against a
temporary `npm pack --ignore-scripts` tarball exited 71 because this exact
package manifest declares scripts. `--ignore-scripts` prevents lifecycle
execution; it does not remove the manifest field. A future candidate needs an
explicit, reviewed packaging adaptation and generated-dist provenance. This
audit does not silently edit the upstream manifest.

## Exports And Generated Code

The generated root entry points are CommonJS files produced by TypeScript.
There is no package `exports` map, so the published `lib/` and `dist/` paths
also create a broad deep-import surface. The root source classes are:

- `lib/ajv.ts`: draft-07 `Ajv` constructor, CommonJS default/module export;
- `lib/2019.ts`: `Ajv2019` constructor;
- `lib/2020.ts`: `Ajv2020` constructor;
- `lib/jtd.ts`: JTD `Ajv` constructor with parser/serializer methods; and
- `lib/standalone/index.ts` and `lib/standalone/instance.ts`: standalone
  code generation and `AjvPack` helpers.

The class API is stateful and includes `validate`, `compile`, `compileAsync`,
`addSchema`, `addMetaSchema`, `validateSchema`, `getSchema`, `removeSchema`,
`addVocabulary`, `addKeyword`, `getKeyword`, `removeKeyword`, `addFormat`, and
`errorsText`. A compiled validator is a process-local callable with mutable
`.errors`, `.schema`, and `.schemaEnv` state; it cannot be returned through a
plain JSON response.

The implementation deliberately generates executable JavaScript:

- `lib/compile/index.ts` constructs validator source and evaluates it with
  `new Function`.
- `lib/compile/jtd/parse.ts` and `lib/compile/jtd/serialize.ts` use
  `new Function` for JTD parser/serializer generation.
- `Options.code.process`, `Options.code.source`, and `Options.code.regExp`
  expose source processing, source observation, and custom regular-expression
  engines.
- `lib/standalone/index.ts` emits a generated module; standalone instance
  support uses `require-from-string` to load generated code.
- Schema strings, property names, regex patterns, references, and custom
  keyword/format definitions all influence compilation or execution.

The official tests exercise these surfaces through codegen, standalone,
custom keyword and format callbacks, remote/local references, async loaders,
`require-from-string`, and optional `re2`. They cannot be treated as a
generic one-call export test. The candidate process must never be allowed to
choose `code.process`, a loader, a regexp engine, a package path, generated
source output, or a trusted result path.

## Official Tests And Collection

The exact tree has 74 `*.spec.ts`/`*.spec.js` files. A read-only registration
inventory found 738 syntactic `it`/`test` registration lines and 291
`describe` registration lines, including skipped registrations. These are
static call-site observations, not a frozen leaf denominator: several suites
register cases through loops or helper data, and JSON suites are generated at
runtime.

The declared commands are:

```text
test-spec    = cross-env TS_NODE_PROJECT=spec/tsconfig.json mocha -r ts-node/register "spec/**/*.spec.{ts,js}" -R dot
test-codegen = nyc cross-env TS_NODE_PROJECT=spec/tsconfig.json mocha -r ts-node/register 'spec/codegen.spec.ts' -R spec
test-cov     = nyc npm run test-spec
json-tests   = rm -rf spec/_json/*.js && node scripts/jsontests
test         = npm run json-tests && npm run prettier:check && npm run eslint && npm link && npm link --legacy-peer-deps ajv && npm run test-cov
test-ci      = AJV_FULL_TEST=true npm test
```

`scripts/jsontests.js` uses `glob` to generate JavaScript cases from eight
directories, including draft suites in the `JSON-Schema-Test-Suite`
submodule. The detached superproject contains zero files in either submodule
and zero generated `spec/_json/*.js` files. The upstream CI first runs
networked `npm install`, initializes the submodules, builds `dist`, and then
runs `npm run test-ci`.

The official test suite directly imports `../dist`, internal generated
modules, and the source-oriented helpers. It covers code generation and
standalone modules, remote references, async `loadSchema`, callbacks,
formats, regex behavior, prototype-related cases, and browser tooling. The
suite is not a ready-made separate verifier or JSON-boundary test bundle.

Official test execution is incomplete in this audit:

- `npm run build` exited 127: `tsc: command not found`.
- `npm run test-spec` exited 127: `cross-env: command not found`.
- `npm ci --offline --ignore-scripts --no-audit --no-fund` exited 1 before
  installation because no lockfile exists.
- No full upstream test, collection report, JUnit/TAP report, or fixed
  denominator was produced.

The test and security files that need explicit future traceability include
`spec/codegen.spec.ts`, `spec/standalone.spec.ts`, `spec/security.spec.ts`,
`spec/issues/cve_2025_69873_redos_attack.spec.ts`,
`spec/issues/format_prototype_pollution.spec.ts`, and the JSON Schema suite.

## npm Lock And Offline Closure

The exact source has no `package-lock.json`, `npm-shrinkwrap.json`,
`yarn.lock`, or `pnpm-lock.yaml`. `.npmrc` sets `package-lock=false`, and
`.gitignore` ignores `package-lock.json`. The source also has no npm cache,
dependency tarballs, or `node_modules`.

The four runtime dependencies are range declarations rather than a frozen
tree. The 40 development dependencies include build tools, test framework
plugins, browser/Chrome tooling, and `re2`; their transitive integrity,
lifecycle, platform, and license state is unknown. A successful public
registry lookup or a temporary network install would not establish the
required offline closure.

The repository's Node dependency contract requires, outside the task source,
an immutable bundle containing:

```text
package-lock.json       # lockfileVersion 3
npm-cache/               # exact tarballs and metadata
bundle.manifest.json     # npm 10.9.8, offline, ignore-scripts, hashes
```

No such bundle is available or copied here. Creating an unreviewed lock or
cache under this task would turn resolver output into false provenance and is
intentionally not done.

## JSON-Safe Validation Boundary

The following is a **proposed boundary, not a frozen task contract**. It is
the smallest coherent shape identified by this audit and is deliberately
narrower than the full Ajv API.

### Operation

Use a task-specific child adapter with one operation:

```json
{
  "op": "validate",
  "schema": {},
  "data": {},
  "allErrors": false
}
```

The adapter creates a fresh draft-07 `Ajv` instance in the untrusted child,
then calls `instance.validate(schema, data)` in that same child. It returns
only:

```json
{
  "ok": true,
  "valid": false,
  "errors": [
    {
      "keyword": "required",
      "instancePath": "",
      "schemaPath": "#/required",
      "params": {"missingProperty": "name"},
      "message": "must have required property 'name'"
    }
  ]
}
```

For schema compilation or invocation errors it should return a bounded,
JSON-safe `{ok:false,error:{name,message}}` object. It must not return a
compiled function, `Error` instance, stack, generated source, Ajv instance,
logger output, or arbitrary object graph. The adapter must validate its own
response before writing it to stdout.

### Input restrictions

- `schema` and `data` are JSON values only: null, booleans, finite numbers,
  strings, arrays, and string-keyed objects with no cycles or custom
  prototypes. Reject non-finite values and integer magnitudes outside the
  safe JavaScript integer range to avoid silent boundary rounding.
- Use a fixed, reviewed draft-07 keyword subset. A defensible first slice can
  cover `type`, `enum`, `const`, numeric/string/array/object limits,
  `required`, `properties`, `additionalProperties`, `items`, and the
  boolean applicators. It must not imply complete JSON Schema parity.
- Permit only local fragment `$ref` references that resolve within the one
  request. Reject remote, filesystem, `data:`, and network URI references;
  do not provide `loadSchema`, `compileAsync`, or user-supplied URI resolvers.
- Do not expose `$async`, custom keywords, custom vocabularies, custom
  formats, `$data`, `code.process`, `code.source`, custom regexp engines,
  standalone generation, JTD, draft-2019-09, or draft-2020-12 constructors.
- Regex-derived keywords (`pattern`, `patternProperties`,
  `propertyNames`) and format behavior require a separate ReDoS/resource
  decision. They must be excluded from the first slice or covered by a
  separately frozen regex policy; a generic `RegExp` call is not a security
  boundary.
- Fix mutation-related options off (`removeAdditional`, `useDefaults`, and
  `coerceTypes`) unless a future contract returns the mutated data and tests
  it explicitly. Set `ownProperties` deliberately and include object keys
  such as `__proto__`, `constructor`, and `prototype` in the security review.
- The inherited child protocol caps requests at 64 KiB and responses at 256
  KiB. The final adapter must add bounded schema depth, string/array/object
  sizes, CPU, memory, process, and timeout limits before collection is
  frozen. A fresh child per request prevents generated code and mutable
  schema caches from crossing cases.

This boundary can express boolean validation and normalized validation errors,
but it does not establish full Ajv API parity. The current generic Node
runner only selects one callable property and invokes it with positional JSON
arguments; it cannot construct `Ajv` and dispatch `instance.validate`. No
Ajv-specific child adapter exists in this task directory.

### Dynamic-code and security review

Ajv treats schemas as inputs to a code generator. The `new Function` calls are
expected implementation behavior, but they make the schema and every
code-generation option untrusted input. The future verifier must:

1. run the candidate package only in an unprivileged child with `--no-addons`,
   sanitized loader/registry environment, no network, and bounded resources;
2. use a fresh process for each schema/data request or a tightly scoped
   session with explicit state reset;
3. prevent candidate access to the reporter, private tests, npm cache,
   loader hooks, generated source, and reward/result paths;
4. test escaped schema strings, malicious property names, local reference
   cycles, malformed schemas, output-size limits, and the selected security
   cases; and
5. classify regex denial of service, missing submodules, build failures, and
   verifier/collection failures separately from model failures.

The source scan found no direct filesystem, network, or child-process import
in `lib/`, but async loading and user callbacks deliberately provide such
extension points. Absence of a direct import is not evidence that an
unrestricted adapter is safe.

## Blocking Findings And Reopen Conditions

Keep this candidate **blocked**. The blocking findings are:

1. The exact full commit is a post-tag commit, while the registry tarball for
   the same version points to the parent release commit. The registry package
   cannot stand in for the requested source.
2. The exact source has no generated `dist`, so its declared main entry point
   does not load. The build depends on an unpinned-at-source toolchain and
   cannot run in the disposable Node 22 checkout without dependencies.
3. The package declares scripts and fails the current candidate tarball
   policy. Any script-removal or generated-dist packaging adaptation needs a
   public contract, build provenance, and tests.
4. There is no npm lockfile, no npm v3 offline cache closure, and no verified
   dependency/license/lifecycle/native-addon manifest. `npm ci --offline`
   fails closed before installation.
5. Official tests use Mocha/TypeScript, generated JSON cases, two submodules,
   direct internal imports, and dynamic/callback/standalone surfaces. No
   final-environment collection or frozen denominator exists.
6. Generated validators, JTD parser/serializer code, standalone modules,
   async loaders, custom keywords/formats, regex behavior, and native `re2`
   are outside a generic JSON-only call and require explicit scope decisions.
7. No task-specific child adapter, private test/command artifact, separate
   verifier, Oracle, empty/stub/forgery/offline control, or Harbor asset was
   authorized or created.

Reopen only after all of these are separately reviewed:

- an exact-revision build strategy produces deterministic `dist` output and
  a script-free, provenance-preserving candidate package;
- Node 22.23.1/npm 10.9.8 and a digest-pinned image are fixed, with a
  content-addressed npm v3 lock/cache closure and dependency license report;
- the JSON validation boundary and keyword/reference/regex policy are
  approved, including prototype-key and generated-code resource controls;
- a task-specific child adapter never imports candidate code in trusted test
  code and returns only schema-checked JSON;
- private `node:test` tests are rewritten from selected official behavior,
  every assertion traces to the public contract, and final collection yields
  a stable fixed denominator; and
- Oracle and empty, stub, forged-report, lifecycle, loader, hang, and offline
  controls are run later in a separate Node pilot release.

Do not add this candidate to the Python dataset, claim Harbor parity, claim
official tests passed, or use the static registration count as a score
denominator.

## Commands And Evidence Run

The source was inspected only in disposable `/tmp` checkouts. No source
archive, package tarball, npm cache, submodule bytes, private tests, or
generated output was copied into this task directory.

```text
GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none --no-checkout \
  https://github.com/ajv-validator/ajv.git /tmp/nl2repo-ajv-source
git -C /tmp/nl2repo-ajv-source checkout --detach \
  f177fe323420ccb23e1a79445fd470cbf80aee7c
git -C /tmp/nl2repo-ajv-source rev-parse HEAD HEAD^{tree}
git -C /tmp/nl2repo-ajv-source describe --tags --always --long HEAD
git -C /tmp/nl2repo-ajv-source submodule status
git -C /tmp/nl2repo-ajv-source ls-tree HEAD \
  spec/JSON-Schema-Test-Suite spec/json-typedef-spec
git -C /tmp/nl2repo-ajv-source archive --format=tar HEAD | sha256sum
sha256sum LICENSE package.json
node --version                         # v22.23.1
npm --version                          # 10.9.8
sha256sum toolchain.node.lock.toml
npm view ajv@8.20.0 name version gitHead dist.integrity license --json
npm pack --dry-run --ignore-scripts --json
npm pack --ignore-scripts --pack-destination /tmp/<bounded-temp>
node src/nl2repobench/verification/node/validate-package.mjs <tarball>
npm run build
npm run test-spec
npm ci --offline --ignore-scripts --no-audit --no-fund
rg/node read-only source, export, build, test, security, and LOC scans
```

Observed outcomes were:

- source lock, detached checkout, repeated archive hash, MIT/license hash,
  Node/npm versions, package metadata, npm registry metadata, and static
  inventories: passed;
- `npm pack --dry-run --ignore-scripts`: passed as a packaging listing but
  showed no generated `dist` entrypoint;
- `validate-package.mjs` on the temporary packed source: exit 71 because the
  package manifest contains `scripts`;
- `npm run build`: exit 127 because `tsc` is unavailable;
- `npm run test-spec`: exit 127 because `cross-env` is unavailable;
- `npm ci --offline`: exit 1 with npm `EUSAGE` because no lockfile exists;
- full official tests, final collection, npm cache hydration, Docker,
  Harbor, Oracle, hidden tests, negative controls, and shared index edits:
  intentionally not run.
