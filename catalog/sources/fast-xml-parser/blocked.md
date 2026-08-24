# `fast-xml-parser` Node v2 Static Audit
**Status: blocked.** This file is a task-local evidence record for the exact
upstream revision. It is not a task descriptor, a publication manifest, or a
Harbor bundle. No hidden tests, private test bytes, npm cache, secrets, Docker
files, Oracle solution, or shared files were added.

## Source Lock

- Package: `fast-xml-parser`.
- Upstream repository:
  `https://github.com/NaturalIntelligence/fast-xml-parser.git`.
- Locked revision:
  `7d608151078d47040841e9804d490feb5c07dfe7`.
- `git ls-remote` resolves that exact object on upstream `master`; the
  revision is not a floating branch reference.
- Commit subject: `docs: fix two 404 documentation links (#862)`.
- Commit date: `2026-08-19T18:07:06+05:30` (author date
  `2026-08-19T18:22:06+05:45`).
- Tree object: `02187bf4271f0e26afb653a556f19db575ccb4d7`.
- Deterministic source archive evidence from
  `git archive --format=tar 7d608151078d47040841e9804d490feb5c07dfe7`:
  `119869440` bytes, SHA-256
  `97965c88e42a83e541192fdc8838dd651beca426a768fa81a1eba9d059a6c659`.
- `LICENSE` is the MIT license, Git blob size `1073` bytes, SHA-256
  `7883225d5e84a6bbb9b170c3d891b4bf6d6259cee869c86bd86381a927071745`.
- The locked package version is `5.11.0`.

The root manifest has no `engines` or `packageManager` field. Upstream CI
tests Node `14.x`, `16.x`, `18.x`, `20.x`, and `22.x`; the publish workflow
uses Node `24` and the public repository does not lock an exact Node patch or
npm patch. A Node v2 task therefore needs an external exact runtime lock; the
upstream revision does not supply one.

## Public API Inventory

The only named exports from `src/fxp.js` are `XMLParser`, `XMLValidator`, and
`XMLBuilder`.

| Runtime surface | Locked signature/behavior | JSON-safe boundary assessment |
| --- | --- | --- |
| `XMLParser` | `new XMLParser(options?: X2jOptions)`; `parse(xmlData: string or Uint8Array, validationOptions?: validationOptions or boolean): any`; `addEntity(name: string, value: string): void`; static `getMetaDataSymbol(): Symbol`. | A fresh instance, XML as a string, plain JSON options, and a JSON-serializable result are possible. `Uint8Array`, symbols, mutable entity state, callbacks, and non-JSON option values need explicit exclusion or protocol support. |
| `XMLValidator` | The type declaration presents a class with static `validate(xmlData: string, options?: validationOptions): true or ValidationError`. The runtime export in `src/fxp.js` is a plain object containing `validate`, not a class. | The input and `true`/error-object result are JSON-safe. The runtime object shape still needs a fixed adapter operation. |
| `XMLBuilder` | `new XMLBuilder(options?: XmlBuilderOptions)` and `build(jObj: any): string`. The implementation is a backward-compatible re-export of the separate `fast-xml-builder` package. | Plain JSON objects and data-only options can cross the boundary. The delegated package and callback-capable options require a separate dependency/API audit. |
| `fxparser` bin | `src/cli/cli.js` reads XML from a file or stdin and can write a file; it imports Node `fs`, `path`, and stream APIs. | Not a JSON-only function surface. Exclude it unless a separate fixed CLI protocol and filesystem policy are authored. |
| `src/v6/*` deep files | Experimental v6 implementation is included by the package file list, but it is not a root export. The package `exports` map exposes only the root `.` condition. | Exclude v6 and deep imports from a first task. |

The package metadata has `type: "module"`, `main: "./lib/fxp.cjs"`,
`module: "./src/fxp.js"`, and conditional `exports` for `import` and
`require`. The `files` allowlist includes `lib`, `src`, and `CHANGELOG.md`,
while `bin.fxparser` points at `src/cli/cli.js`. This is a dual ESM/CJS
package, not the single-module shape supported by the first Node slice.

### JSON-safe candidate slice

If this candidate is reopened, the smallest defensible boundary is a new,
explicit task contract rather than the entire TypeScript declaration:

- Allow root-package operations for parser, validator, and (only after its
  dependency audit) builder.
- Accept XML only as a UTF-8 string and accept only plain JSON option values.
- Permit data-only booleans, strings, numbers, and string arrays such as
  `preserveOrder`, `ignoreAttributes`, `unpairedTags`, `stopNodes`, and
  bounded entity-limit fields.
- Reject callbacks (`tagValueProcessor`, `attributeValueProcessor`,
  `isArray`, `updateTag`, transforms, `tagFilter`, and `onDangerousProperty`),
  `RegExp`, `Expression`/`Matcher` objects, custom `entityDecoder`, metadata
  symbols, and arbitrary class instances.
- Require fresh parser instances per request, or define an allowlisted
  sequence for `addEntity` followed by `parse`; do not expose mutable state as
  an unconstrained remote object.
- Require results and errors to be normalized to bounded JSON before scoring.

This proposed slice is not approved or published; it is the boundary needed
to make the API discussable under a JSON subprocess contract.

## Security and XXE Scope

The parser core is a string parser. A static scan of the locked `src/` parser
files found no imports of `fs`, `net`, `http`, `https`, or `child_process`.
The CLI does use `fs` and is excluded above. No code path in the parser core
resolves a URI, opens an external entity, or fetches a network resource.

`src/xmlparser/DocTypeReader.js` handles internal DTD declarations. Its
`readEntityExp` path explicitly rejects `SYSTEM` declarations as unsupported,
rejects parameter entities, and reads only quoted internal replacement text.
`PUBLIC` external identifiers are not accepted as an internal quoted value and
fail parsing; there is no PUBLIC/SYSTEM resolver. `XMLParser.addEntity` adds a
literal in-memory mapping and rejects ampersands in the value, so the method is
not a file or URL loader even though the documentation calls these mappings
external entities.

Entity processing is enabled by default in `src/xmlparser/OptionsBuilder.js`.
The exact boolean normalization in this revision supplies these defaults:

- `maxEntitySize`: `10000` characters;
- `maxExpansionDepth`: `10000`, but this field is marked reserved and is not
  passed to the entity decoder by the parser;
- `maxTotalExpansions`: `Infinity` for the boolean/default form, not a finite
  default count limit;
- `maxExpandedLength`: `100000` characters;
- `maxEntityCount`: `1000` declarations.

The parser passes total-expansion and expanded-length limits to
`@nodable/entities` and enforces size/count limits while reading the DTD. The
security suite also exercises explicit small limits, disabled processing, and
allowed-tag filters. These controls reduce entity-expansion risk, but this
audit does not claim that the default configuration is a complete denial of
service guarantee: the default expansion count is unbounded, input size is
not globally capped by the library, and depth is not enforced by the parser.
The verifier must impose its own input, CPU, memory, output, and process
limits. A safe task contract should default `processEntities` to `false` for
untrusted XML and test any opt-in entity behavior separately.

The parser sanitizes dangerous property names and rejects critical names such
as `__proto__`, `constructor`, and `prototype` in its normal path. That is a
prototype-pollution defense for parsed object keys, not a general sanitizer
for HTML, SVG, SQL, or application content. Custom callbacks and the
delegated builder are outside this claim. In particular, the builder's own
dependency must be audited before any builder security statement is made.

## Exports, Packaging, and Tests

Static package metadata and a dry-run `npm pack --ignore-scripts` inspection
show:

- package name/version `fast-xml-parser@5.11.0`;
- 53 packed files and `1,294,433` unpacked bytes;
- the package includes `lib` bundles, ESM `src`, the CLI, the experimental
  `src/v6` tree, `README.md`, and `LICENSE`, but no `spec` directory;
- `lib/fxp.cjs` is a generated bundle (no external `require(...)` calls were
  found by the static scan), while ESM `src/fxp.js` imports six runtime
  packages;
- the manifest declares eight scripts, including `preversion: npm test`.

The root test command is:

```text
c8 --reporter=lcov --reporter=text jasmine spec/*spec.js
```

A static, anchored source inventory of the 27 root `spec/*_spec.js` files found 323
active `it`/`fit` declarations and 2 `xit` declarations. This is an inventory,
not a frozen collection denominator. Notable groups include 31 active entity
security cases, 29 active entity cases plus one skipped case, 65 validator
cases, and 38 parser cases. The tests use Jasmine and import `../src/fxp.js`
directly rather than testing only the packed package export. Several tests
read XML/assets with `fs` and `path`; many exercise callbacks, `RegExp`,
`Expression` objects, matcher instances, and metadata symbols. The nested
legacy import smoke tests are not selected by the root `spec/*spec.js` glob;
one also attempts a deep `fast-xml-parser/src/v6/...` import that conflicts
with the locked `exports` map.

The upstream test command has no `node:test` JSON report and no fixed leaf-test
contract. It cannot be copied directly into the current separate verifier.
Selected assertions would need to be re-authored as private `node:test`
files with stable IDs and a reviewed frozen denominator.

## npm Lock, Cache, and Scripts

The locked root has six direct runtime dependencies:

```text
@nodable/entities       ^3.0.0
fast-xml-builder        ^1.2.0
is-unsafe                ^2.0.0
path-expression-matcher ^1.6.2
strnum                  ^2.4.2
xml-naming              ^0.3.0
```

The committed `package-lock.json` is lockfile **version 2**, with 439
`packages` entries including the root: 8 entries in the transitive runtime
closure and 430 development entries. All 438 non-root entries use registry
URLs and SHA-512 integrity strings in the locked metadata. No git, `file:`,
workspace, link, registry override, native-addon marker, or
`hasInstallScript` flag was found in the lock. One optional entry is
`@pkgjs/parseargs`; it is development-only. The repository also commits a
Yarn lockfile v1, but does not declare a package-manager policy.

The lock is internally consistent with the root manifest (`name`, `version`,
and dependency sections match), but lock metadata is not an offline closure.
The upstream checkout contains no `node_modules`, `npm-cache`, or
`bundle.manifest.json`. No dependency tarballs or cache entries were copied
into this task.

The repository Node v2 validator requires the private bundle layout
`package-lock.json`, `npm-cache/`, and `bundle.manifest.json`; it rejects any
lockfile whose `lockfileVersion` is not `3` and requires each listed cache
entry to exist. A temporary metadata-only directory containing the exact
upstream lock and the existing empty-cache manifest was checked without
writing to the repository. The validator failed closed with:

```text
NodeDependencyError: npm dependency lockfile must use lockfileVersion 3
```

This is a deterministic authoring blocker, not an indication that any npm
package failed at runtime. Reopening requires a separately reviewed,
content-addressed v3 lock/cache bundle generated for one exact npm patch. The
six runtime packages, especially the delegated `fast-xml-builder`, also need
their package contents and lifecycle metadata audited from that closure.

The upstream CI install uses `npm install --ignore-scripts`, while the publish
workflow uses `npm ci` against the public registry. Neither workflow proves
the required offline cache contract. The source manifest's `scripts` object is
also incompatible with the current candidate tar policy: the Node package
validator rejects a packed manifest containing any `scripts` key. Therefore
the unchanged upstream package cannot simultaneously be treated as the exact
package metadata and pass that candidate policy. A reopened task must either
make scripts explicitly out of scope and require a script-free candidate
manifest, or obtain an approved verifier-policy decision; this audit does
not choose between them.

## Candidate Verifier Feasibility

The current Node runner is designed for the zero-dependency synthetic task,
not class-based package APIs:

- `candidate_runner.mjs` loads a package, looks up one literal property, and
  requires that property to be a function (`candidate_runner.mjs:52-66`).
- It invokes the function as `value(...args)` and never constructs a class or
  traverses a static/member path.
- `XMLParser` and `XMLBuilder` are classes, and runtime `XMLValidator` is an
  object; none is a callable free-function export under this protocol.
  `XMLValidator.validate` cannot be selected by passing a dotted name because
  the runner performs `candidate[exportName]`, not member traversal.
- The synthetic test client hardcodes `NODE_ALLOWED_PACKAGE=node-synthetic`.
  A task-local client could change the package name, but that would not solve
  class construction/static dispatch or mutable parser state.

The current install sequence (`install_candidate.mjs`) runs offline `npm ci`,
`npm pack`, package validation, and offline installation. The unchanged
upstream manifest reaches the package validator's `scripts` rejection before
any API test. The current test runner (`run_tests.mjs`) executes `node:test`
files and parses TAP; it cannot collect the upstream Jasmine suites or infer a
stable denominator from them.

Consequently, a candidate verifier is not feasible in this checkout without
an explicitly approved protocol extension. At minimum, reopening needs:

1. A fixed, allowlisted Node adapter that can construct `XMLParser` and
   `XMLBuilder`, call `XMLValidator.validate`, and normalize errors/results
   through the JSON boundary. The adapter must not import candidate code in
   the trusted test process and must keep class state bounded.
2. A decision on whether the task tests ESM, CJS, or both. Testing both would
   require parity checks for the generated `lib/fxp.cjs` and ESM source path;
   the first Node slice explicitly defers dual ESM/CJS packages.
3. A private `node:test` test/command artifact with a frozen leaf collection,
   including only the scoped parser/validator behavior and any separately
   reviewed builder behavior.
4. A reviewed v3 npm lock/cache artifact and dependency tarball audit, with
   lifecycle scripts disabled and no candidate-controlled registry, loader,
   test-root, or report paths.
5. Explicit limits and assertions for XXE/non-resolution, entity expansion,
   prototype-pollution names, malformed XML, JSON serialization, and process
   resource bounds.

## Decision and Validation Record

Keep this task **blocked** for `dependency-lock`, `offline-cache`,
`class-api-adapter`, `dual-module-scope`, and `test-framework/collection`.
Do not create `task.toml`, `instruction.md`, private tests, an Oracle bundle,
or a Harbor projection from this evidence.

Commands and static checks completed:

- `git ls-remote` against the upstream repository: exact locked object found.
- Detached fetch/checkout of the requested revision: `HEAD` matched the full
  SHA; commit, tree, archive, and license hashes recorded above.
- Node JSON inventory of `package.json` and `package-lock.json`: manifest and
  lock root matched; runtime/dev counts and integrity/protocol properties
  recorded above.
- `npm pack --dry-run --ignore-scripts --json`: 53 files and 1,294,433
  unpacked bytes; no tarball was retained.
- Static source/test scans: exports, signatures, security paths, scripts, and
  test inventory recorded above.
- Temporary invocation of `validate_npm_dependency_bundle` with the exact
  lockfile: failed with the expected lockfile-v3 error above.

No `npm ci`, dependency download, upstream test execution, Docker build,
Harbor run, Oracle trial, hidden-test authoring, or candidate behavior run was
performed in this static lane.
