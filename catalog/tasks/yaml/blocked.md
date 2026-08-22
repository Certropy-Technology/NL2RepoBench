# `yaml` Node v2 authoring audit

**Status: blocked.** This is a task-local development evidence record for the
exact npm candidate revision. It is not a Harbor task, a publication approval,
or a production dataset entry. No hidden tests, private test bytes, npm cache,
secret, Docker asset, Oracle solution, verifier, or shared catalog index is
included here.

## Candidate lock

- Package: `yaml`, version `3.0.0-1`.
- Upstream: `https://github.com/eemeli/yaml`.
- Frozen revision:
  `b91c3747333c7379bfd6edb6000fa163ca33805b`.
- Commit subject: `perf: various performance tweaks (#699)`.
- Commit timestamp: `2026-08-01T12:57:22+03:00`.
- Commit tree: `49f88736ed668844acb4e466b6631e4dbf67cdab`.
- `git archive --format=tar HEAD | sha256sum`:
  `f11db9769e9792d8f36072e6fa87f925070293a529f4ccb0d2e27bf92df943d3`.
  The archive hash was identical across three independent archive commands.
- The detached checkout had no local changes, 154 tracked paths, and three
  gitlink submodules:
  - `docs-slate` at `413d60f7fdbf95e379b7ff904bfee3a46e370716`;
  - `tests/json-test-suite` at
    `984defc2deaa653cb73cd29f4144a720ec9efe7c`;
  - `tests/yaml-test-suite` at
    `50861920b1fd990159811fdbdca1beeb7ab3604a`.
- `LICENSE` is present and the package declares `ISC`. The checked license
  file is 738 bytes with SHA-256
  `5bba27375d93e9119f76c1015f7672cf9ad5f70952296e0842fb2243d6376869`.
- `package.json` is 2,302 bytes with SHA-256
  `160c20163fb647215d7ae2185200553615aec4c206032d546189d56374a6c56d`.
- The committed `package-lock.json` is 115,248 bytes with SHA-256
  `c3d06817cfc782e04544feb2fb2193096870373d6205f675c34bee707be1ab13`.

The source and license evidence are sufficient to continue a development
audit, but they do not establish an exact-revision generated npm package or a
publishable dependency closure.

## ESM and package exports

The locked package metadata declares:

- `type: "module"`;
- `main: "./dist/index.js"`;
- `exports["."]` with `types: "./dist/index.d.ts"` and
  `default: "./dist/index.js"`;
- `exports["./util"]` with the corresponding `dist/util` files;
- `exports["./package.json"]`;
- no CommonJS `require` condition; and
- `bin: "./bin.js"`, where `bin.js` imports `./dist/cli.js`.

The source entry point is `src/index.ts`, and its public named runtime exports
include `parse`, `parseAllDocuments`, `parseDocument`, `stringify`, `lex`,
`visit`, `visitAsync`, `Composer`, `Document`, `Schema`, the node classes,
error classes, and the `CST` namespace. The source API declarations are
TypeScript and use explicit `.ts` relative imports. The build configuration
uses Rolldown to emit ESM JavaScript and declarations into `dist/`.

`dist/` is ignored by the exact source revision and is absent from the
checkout. Consequently, the root export points at a missing file. A direct
Node 22 import probe returned:

```text
ERR_MODULE_NOT_FOUND: Cannot find module .../dist/index.js
```

This is a packaging/build provenance blocker, not an indication that the
source API is unavailable after a separately reviewed build.

The current Node v2 candidate runner selects one direct named export and
requires it to be callable. A built root package would therefore be compatible
with the runner for the direct `parse` and `stringify` exports. It must not use
the `Document`, node-class, `CST`, `visit`, or `./util` surfaces as though they
were plain JSON functions.

## JSON-safe parse/stringify scope

The only coherent initial scored scope found in this revision is the direct
root `parse` and `stringify` functions:

```text
parse(source: string, options?: object) -> JSON-safe value
stringify(value: JSON-safe value, options?: object) -> string
```

The eventual subprocess adapter should accept requests and return responses
through the existing bounded JSON protocol. The following boundary is
necessary for the result to remain JSON-safe:

- Input values are `null`, booleans, finite numbers, strings, arrays, and plain
  objects with string keys, recursively.
- `parse` accepts a YAML source string. Its options may use only JSON scalar
  and object values, such as `version`, `schema`, `logLevel`, `prettyErrors`,
  `strict`, `stringKeys`, `merge`, `resolveKnownTags`, `keepSourceTokens`,
  `intAsBigInt: false`, `mapAsMap: false`, and a bounded numeric
  `maxAliasCount`.
- `stringify` accepts JSON-safe values and only JSON-valued formatting/schema
  options. Its result is text and includes the upstream document-ending
  newline.
- Error observations should be normalized at the child-process boundary to
  the exception class/name and bounded message. The exact source error object
  is not a JSON contract.
- Mapping keys and parsed values must remain serializable by the protocol;
  inputs that produce non-JSON keys, cyclic aliases, or unsupported object
  identity are outside the scope.

The adapter must exclude the following rather than silently serializing them:

- `parseDocument` and `parseAllDocuments`, whose results are `Document`
  instances or arrays of documents rather than plain JSON values;
- `reviver`, `replacer`, `customTags`, `mapKey`, `onAnchor`, `onTagObj`,
  `commentString`, and function-valued `sortMapEntries` options;
- `BigInt` output from `intAsBigInt`, `Map` output from `mapAsMap`, dates and
  buffers from YAML 1.1 tags, custom tag objects, symbols, class instances,
  and other non-JSON values;
- cyclic or otherwise non-serializable anchor/alias graphs; and
- filesystem, CLI, dynamic visitor imports, network, loader, and browser
  behavior.

The default parser can warn through `console.warn`, and malformed input can
raise `YAMLParseError`. The adapter and private tests must define whether
warnings are suppressed with `logLevel: "silent"` or captured separately;
stdout cannot be used for diagnostics because it is the protocol channel.
This scope is a proposed authoring boundary only. No private adapter or hidden
test artifact was created in this audit.

## Tests and denominator

The exact source declares `vitest run` as its test command, not `node:test`.
The locked development dependency is Vitest `^4.0.15`; the current Node v2
metric and runner require a separate `node:test` adapter and structured
`node-test-json-v1` report.

Static inventory of the 25 tracked TypeScript test files found:

- 705 direct `test(...)` call tokens;
- 184 direct `describe(...)` call tokens; and
- 3 literal `test.skip(...)` call tokens.

These are not a frozen leaf denominator. In particular:

- `tests/yaml-test-suite.ts` generates tests by reading the
  `tests/yaml-test-suite` git submodule at collection time;
- `tests/json-test-suite.ts` generates tests by reading the
  `tests/json-test-suite` git submodule at collection time;
- both submodule working trees are absent in the detached source checkout;
- the YAML suite has data-dependent skip entries and conditional test nodes;
- the JSON suite has seven named skip cases; and
- CLI tests, test artifacts, aliases, nodes, dates, binary tags, and other
  JavaScript-only values are outside a plain JSON parse/stringify boundary.

The source tree has seven tracked test artifact files totaling 12,382 bytes,
but no test bundle has been copied into this task directory. A future private
adapter must select assertions traceable to the JSON scope, freeze the leaf
collection, and retain the skipped/todo/error policy explicitly.

No upstream test run is claimed. With no installed dependency tree:

```text
npm test
# status 127: vitest: command not found
```

This does not establish a source baseline or an Oracle result.

## Lock and offline cache closure

The source does contain a committed npm lockfile v3. Its static inventory is:

- 220 `packages` entries including the root, 219 non-root entries;
- zero runtime dependencies in the root and 11 development dependencies;
- all 219 non-root entries marked as development dependencies;
- all non-root entries have integrity and HTTPS npm registry resolution in the
  locked metadata scan;
- 48 optional entries and 24 nested `node_modules` entries; and
- 42 entries with platform restrictions or install-script metadata. These
  include Rolldown binding variants, LightningCSS platform variants, nested
  Rolldown bindings under Vite, and `fsevents@2.3.3` with
  `hasInstallScript: true`.

The lockfile alone is not an offline closure. With a fresh temporary npm
cache, the exact runtime versions Node `v22.23.1` and npm `10.9.8` were used
with:

```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

The command failed closed with:

```text
ENOTCACHED ... yocto-queue-0.1.0.tgz
```

The temporary cache was not promoted or copied. No content-addressed cache,
tarball bundle, registry credential, or dependency artifact exists here.

The repository's current Node dependency validator rejected a metadata-only
fixture made from this exact lock with:

```text
NodeDependencyError: native or platform package is forbidden:
node_modules/@rolldown/binding-android-arm64
```

That validator checks every lock entry, including optional development
entries, so the current lock cannot be accepted as a Node v2 bundle. A future
build-tool separation or normalized lock is an authoring decision that must be
reviewed; this record does not alter the upstream lock.

## Build and lifecycle policy

The exact package manifest contains these relevant scripts:

```text
build           rolldown -c
test            vitest run
test:all        npm test && npm run test:types && npm run test:dist && npm run test:dist:types
test:dist       npm run build && vitest run
test:types      tsc --noEmit && tsc --noEmit -p tests/tsconfig.json
preversion      npm test && npm run build
prepublishOnly  npm run clean && npm test && npm run build
```

It also contains documentation/deploy scripts that invoke `bundle install`,
`bundle exec`, shell deployment code, or the submodule-backed docs tree. Those
scripts are outside the scored library scope and must not run in the verifier.
The build probe without an installed dependency tree returned:

```text
npm run build
# status 127: rolldown: command not found
```

The source package's `files` list contains only `dist/`. Running
`npm pack --ignore-scripts` before building produced a four-file tarball
(`LICENSE`, `README.md`, `package.json`, and `bin.js`) with no `dist/` output.
The package tarball validator rejected that exact tarball because the manifest
still contains a `scripts` object:

```text
NodeDependencyError: candidate lifecycle scripts are forbidden
```

The validator rejects any package `scripts` object, not only install hooks.
Therefore a candidate package would need an explicit packaging adaptation that
removes scripts and supplies a provenance-reviewed built `dist/` tree. This
must not be silently presented as a verbatim npm artifact from the locked
revision.

## Blocking findings and reopen conditions

Keep this task blocked. The blockers are:

1. The exact source revision has no tracked/generated `dist/` tree even though
   the root exports and `main` require it; the unbuilt npm tarball is not
   importable.
2. The committed lock is a development/build lock, not a reviewed offline
   closure, and the current Node v2 validator rejects its platform/native
   binding entries.
3. The exact package manifest contains scripts rejected by the candidate
   package validator; packaging adaptation and build provenance are not yet
   approved.
4. The upstream suite is Vitest with data-dependent dynamic collection and
   git submodule inputs, while Node v2 requires a private `node:test` adapter,
   bounded JSON calls, and a frozen leaf denominator.
5. No private test/command artifact, separate verifier, Oracle, or control
   result exists, by design.

Reopen only after a separately reviewed authoring decision supplies all of the
following without modifying this locked source revision to make tests pass:

- exact-revision build/package provenance for the ESM `dist/` export, including
  the package metadata adaptation required by the validator;
- a v3 npm lock and content-addressed offline closure accepted by
  `validate_npm_dependency_bundle`, with platform/native/lifecycle policy
  resolved explicitly;
- a private `node:test` adapter and command plan covering only the JSON-safe
  `parse`/`stringify` contract, with collection and error normalization frozen;
  and
- subsequent verifier, empty/stub/forgery/offline controls and Oracle runs in
  the later validation stage.

No Harbor, Docker, hidden-test, cache, secret, or Oracle action was taken in
this authoring lane.
