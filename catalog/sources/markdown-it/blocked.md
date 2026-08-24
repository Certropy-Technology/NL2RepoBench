# `markdown-it` Node v2 Static Authoring Audit

**Status: blocked development-only.** This file is task-local evidence for the
Node v2 authoring lane. It is not a Harbor task, a dataset entry, or a
publication approval. No hidden tests, private test commands, Oracle solution,
verifier, Docker asset, npm cache, dependency tarball, secret, or generated
package is stored here.

## Candidate Lock

- Package: `markdown-it`.
- Upstream: `https://github.com/markdown-it/markdown-it`.
- Frozen revision:
  `1e8ab89ca299351879169a79d2627fe3a356ce4a`.
- Commit tree:
  `caa57cdec3bff822096b5a1569560b11abd9af19`.
- Commit timestamp: `2026-08-13T03:19:58+03:00`.
- Commit subject: `doc: add changelog to menu`.
- Submodules: none.
- Detached checkout: clean, with 162 tracked files.
- Repeated `git archive --format=tar HEAD` output: 1,095,680 bytes and
  SHA-256
  `4a0dd5c3aefa2a727323622c1c5a21ce6b2b1ba378444979b5938227055acd39`.
- `LICENSE` declares the MIT license; its SHA-256 is
  `792c48c5a849a15fdf9e37e8bcf9e6d1dd13b32b46c642a748a0a46a9919d473`.
- `package.json` SHA-256:
  `7f2870760c52b1b409d15c590225da59f596041f82d133a1e0d5e1e07739d1a2`.
- The source checkout and all test/fixture bytes used for this audit remained
  under `/tmp/nl2repo-markdown-it-source`; none was copied into this task
  directory.

The source and license are suitable for continued authoring review. This does
not establish a reproducible package build, an offline dependency closure, or
an executable verifier.

## Parser And Render API

The runtime source entry is `src/index.ts`. It creates a callable wrapper around
the `MarkdownIt` class and exports that wrapper as the **only runtime export**.
The remaining exports in `src/index.ts` are `export type` declarations. The
wrapper preserves the upstream ability to call the constructor with or without
`new`.

The class surface at this revision is:

| Surface | Contract evidence |
| --- | --- |
| Constructor | `MarkdownIt()`; `MarkdownIt(options)`; or `MarkdownIt(presetName, options?)`, where presets are `default`, `commonmark`, and `zero` (`src/markdownit.ts:208-241`). |
| Options | JSON-compatible booleans `html`, `xhtmlOut`, `breaks`, `linkify`, `typographer`; string `langPrefix`; string or string-array `quotes`; numeric `maxNesting`; callback-valued `highlight` (`src/types.ts:49-162`). |
| State/configuration | `set(options)`, `configure(preset)`, `enable(list, ignoreInvalid?)`, and `disable(list, ignoreInvalid?)` return the instance and mutate parser state (`src/markdownit.ts:243-346`). |
| Full parse | `parse(src: string, env: Env): Token[]` produces block and inline tokens and mutates the supplied environment (`src/markdownit.ts:369-389`). |
| HTML render | `render(src: string, env: Env = {}): string` parses and renders a complete Markdown document (`src/markdownit.ts:391-401`). |
| Inline parse | `parseInline(src: string, env: Env): Token[]` skips block rules and returns an inline token stream (`src/markdownit.ts:403-415`). |
| Inline render | `renderInline(src: string, env: Env = {}): string` renders one inline fragment without a paragraph wrapper (`src/markdownit.ts:417-425`). |
| Link behavior | `validateLink`, `normalizeLink`, and `normalizeLinkText` are instance methods that are intentionally replaceable by callers (`src/markdownit.ts:121-190`). |
| Exposed internals | `inline`, `block`, `core`, `renderer`, `linkify`, `utils`, and `helpers` are live mutable objects on every instance (`src/markdownit.ts:70-204`). |

The parser and renderer are not a stateless string function. `parse` and
`parseInline` return `Token` instances. A token contains nested `children`,
attribute tuples, source maps, nesting/level information, content, markup,
info, block/hidden flags, and an arbitrary plugin `meta` record
(`src/token.ts:13-83`). The renderer dispatches through a mutable
`Record<string, RendererRule>`; each renderer rule receives tokens, index,
options, environment, and the renderer and returns a string
(`src/renderer.ts:6-12`, `src/renderer.ts:147-173`).

The built-in parser chains are also mutable. `Ruler.at`, `before`, `after`, and
`push` accept executable rule functions; `enable`, `enableOnly`, `disable`, and
`getRules` control active rule chains (`src/ruler.ts:92-272`). The parser exposes
separate core, block, inline, and inline-postprocessing rulers. This is a
plugin/runtime extension surface, not plain JSON data.

## Plugin And Callback Scope

The following upstream behavior is real source API but is outside the initial
JSON task boundary:

- `use(plugin, ...params)` invokes an arbitrary plugin function with the live
  parser instance (`src/markdownit.ts:348-368`). Plugins can add rules, mutate
  renderer rules, use parser state, and place arbitrary values in `Env` or
  `Token.meta`.
- `MarkdownItOptions.highlight` is a callback receiving `(str, lang, attrs)`
  and returning escaped HTML or an empty string. The fence renderer calls it
  (`src/types.ts:145-160`, `src/renderer.ts:40-91`).
- `validateLink`, `normalizeLink`, and `normalizeLinkText` are replaceable
  methods. `md.linkify` is a live `LinkifyIt` object with its own mutable
  configuration.
- `Renderer.rules` accepts arbitrary callback-valued token renderers, and the
  `Ruler` methods accept callbacks with stateful parser arguments.
- The `utils` and `helpers` objects are explicitly exposed for plugins and
  contain functions, class wrappers, and parser-state helpers.

The upstream tests confirm that these are scored-relevant source behaviors:
`test/markdown-it/misc.test.mjs` exercises plugin registration, highlight
callbacks, custom renderer rules, link normalization/validation overrides, and
direct ruler mutation; `test/markdown-it/ruler.test.mjs` exercises callback
insertion and replacement. These cases must not be smuggled through a JSON
request by encoding source code or function strings.

## Package Exports And Build Boundary

The exact `package.json` declares version `15.0.0` and these package paths:

- `main`: `./dist/markdown-it.cjs.js`;
- `module`: `./dist/markdown-it.mjs`;
- `types`: `./dist/markdown-it.d.cts`;
- root `exports`: conditional CJS/ESM values and matching `.d.cts`/`.d.mts`
  declarations;
- `./browser`: generated UMD and ESM browser bundles;
- `./package.json`: the manifest;
- `bin/markdown-it.mjs`: the file/stdin CLI entry point.

The manifest publishes only `bin/` and `dist/`. There are **zero tracked
`dist/` files** at the pinned revision. `support/build-dist.mjs` generates the
CJS bundle, ESM bundle, browser bundles, and both declaration forms using
Vite, Rolldown, `rolldown-plugin-dts`, and TypeScript. The source `.ts` tree is
not the package export and is not a replacement for the absent generated
files.

The CJS build contract is observable in `test/build/build.test.mjs`, which
does `require('../../')()` and expects the root value itself to be callable.
The current generic Node child runner instead loads the package and invokes
`candidate[exportName]` only (`src/nl2repobench/verification/node/candidate_runner.mjs:52-66`).
It has no root-callable or method-path operation. A markdown-it-specific child
adapter or an explicitly approved runner extension is therefore required; do
not infer that selecting `default`, `render`, or `parse` will work against the
generated CJS value.

The package also has a CLI that reads files or stdin and writes files or stdout
(`bin/markdown-it.mjs`). Filesystem and process-stream behavior is excluded
from a JSON library task. Browser exports, demos, documentation, and publish
hooks are likewise outside the parser/render contract.

## Tests And Denominator Evidence

The exact tree has eight `*.test.mjs` modules plus one test helper. The package
test command is a multi-stage command:

```text
npm run lint
npm run build
npm run type-check
npm run test:cmspec
npm run test:markdown-it
npm run test:build
```

The test scripts use Node's built-in test runner, but two suites register tests
dynamically from fixture files:

| Static source area | Shape counted without executing candidate code |
| --- | ---: |
| `test/fixtures/markdown-it/*.txt` (10 files) | 203 generated leaves |
| `test/fixtures/commonmark/spec.txt` | 217 generated leaves |
| Direct active `it` leaves in `misc`, `pathological`, `ruler`, `token`, and `utils` | 93 leaves |
| `test/build/build.test.mjs` | 1 leaf |
| **Static expected leaf shape** | **514 leaves** |

The 203 and 217 counts were obtained by applying the repository helper's
separator parser to the fixture text. The 93 direct count excludes one
commented-out `it` block. This is static source evidence, not a frozen final
denominator: no test command, collection, or baseline was run in this audit.

The upstream suite is not directly suitable as a separate verifier:

- most tests import `../../src/index.ts` or internal source modules rather than
  the package export;
- fixture helpers read files during test registration and generate dynamic leaf
  tests;
- tests pass callback functions for plugins, highlight, renderer rules, and
  link overrides;
- token tests inspect class instances and mutable metadata;
- pathological tests create worker threads and inputs far beyond a small
  request envelope; and
- the build test requires the generated CJS package, which is absent from the
  source tree.

The static 514 count must not be treated as a Harbor or Node v2 frozen total.
A future private adapter must select only assertions traceable to the public
JSON contract, collect the adapter tests in the final environment, and record
the leaf node list and collection errors.

## Lock And Dependency Closure

The exact tree includes a root `package-lock.json` with lockfile version 3. The
lock file SHA-256 is
`60cb18d600352d2cca3d0d6ee11f40ea9159231a0dec720ea684e1bc0eb5f08a`.
It has 454 `packages` entries including the root and 453 non-root entries.

There is a provenance-breaking manifest/lock mismatch:

```text
package.json             markdown-it 15.0.0
package-lock.json root   markdown-it 14.3.0
package-lock.json top    markdown-it 14.3.0
```

The root dependency and devDependency ranges otherwise match the manifest.
The mismatch means the committed lock cannot be accepted as the exact
dependency lock for this revision's package metadata, even if an npm version
happens to proceed with installation. It must be regenerated and reviewed
against the exact manifest before packaging.

Static lock traversal found:

- six packages in the runtime dependency closure, all direct dependencies and
  all resolved from `https://registry.npmjs.org/` with `sha512-` integrity;
- 402 reachable packages in the union of runtime and development closures;
- 48 platform-constrained optional entries, including Rolldown, Yuku, and
  Lightning CSS binding packages;
- one entry with `hasInstallScript`: optional Darwin `fsevents@2.3.3`;
- no missing integrity fields among the 453 lock entries; and
- no non-registry `resolved` URLs among the lock entries.

The runtime closure is small, but the source package's build/test closure is
not. The build depends on Vite/Rolldown and TypeScript tooling, and the lock
contains platform-specific optional packages. A lock file is not an offline
artifact: no content-addressed npm cache or tarball closure is present or
authorized here. No install, cache hydration, `npm ci`, build, or package
execution was run.

The package has many lifecycle/build scripts, including `prepack`:

```text
npm test && npm run build && npm run demo && npm run doc
```

The task package validator rejects a package manifest containing a `scripts`
key (`src/nl2repobench/verification/node/validate-package.mjs:37-45`). A future
candidate must make an explicit, reviewed packaging decision about generated
dist files and scripts. It must not silently copy the upstream manifest,
execute `prepack`, or claim that the source lock and generated package are
equivalent.

## JSON Boundary

The current bounded runner accepts a single JSON object with a package name,
one export name, and an array of JSON arguments. It limits requests to 64 KiB,
responses to 256 KiB, and arguments to 32 entries. It requires the selected
`candidate[exportName]` to be callable and serializes the return value with
`JSON.stringify`.

A conservative future markdown-it scope is:

```text
operation: "render" | "renderInline"
source: string
preset: "default" | "commonmark" | "zero" (optional)
options: JSON-safe parser options (optional)
env: {} only in the initial scope (optional)
```

The operation returns a string. JSON-safe options are the boolean parser flags,
`langPrefix`, a string or string-array `quotes`, and a bounded integer
`maxNesting`. `highlight` and all callback overrides are rejected. Each
request must create an isolated parser instance so `set`, `configure`, and
rule changes cannot leak across cases.

`parse` and `parseInline` are valuable inventory APIs but should remain
adapter-gated rather than being passed through as raw values. If they are
included later, the child adapter must normalize tokens to a documented plain
JSON schema containing only token type/tag/attrs/map/nesting/level/children/
content/markup/info/block/hidden and an explicitly restricted JSON `meta`.
Arbitrary `Env` keys, symbol keys, class identity, functions, cycles, and
plugin-owned metadata are outside the boundary. Error observations should be
normalized to an exception type/name and message in the child process.

The following values and surfaces are explicitly excluded:

- `use`, custom plugins, Ruler callbacks, renderer rule callbacks, and
  callback-valued `highlight`/link overrides;
- `Map`, `Set`, `Date`, `RegExp`, `BigInt`, `Symbol`, `undefined`, functions,
  class instances, cyclic objects, and arbitrary prototypes;
- mutable `utils`, `helpers`, `linkify`, `Token`, `Renderer`, `Ruler`, and
  parser-state objects;
- browser exports, CLI/filesystem I/O, worker-thread behavior, docs/demo
  generation, and publish/network behavior; and
- source imports such as `src/index.ts`, internal modules, or generated test
  fixture paths.

This is a deliberate JSON boundary, not a claim of complete markdown-it API
parity. The future task instruction and private tests must state it plainly.

## Blockers And Reopen Conditions

Keep `markdown-it` blocked. The blockers are:

1. `package.json` is version `15.0.0`, while the committed lock/root metadata
   are version `14.3.0`; no manifest-aligned lock has been reviewed.
2. All package export targets under `dist/` are absent from the exact source
   tree, and the generated build depends on a broad toolchain with
   platform-specific optional packages.
3. The current generic JSON runner cannot directly invoke the package's root
   callable CJS contract or its instance methods. No markdown-it-specific
   child adapter, method dispatch contract, or token normalizer exists.
4. No private JSON-adapted test/command artifact or final collection evidence
   exists. The static 514-leaf shape is not a frozen denominator.
5. No reviewed offline npm cache/tarball closure exists.
6. No Docker, Harbor, Oracle, empty/stub/forgery/offline control, or
   publication action was authorized or run here.

Reopen only after the exact manifest/lock version is reconciled; a reviewed
Node/npm build and runtime profile produces the package export files; a
separate untrusted child adapter defines root construction, render dispatch,
and any normalized parse response; private tests freeze a JSON-traceable leaf
denominator; and the runtime/build dependency closure is content-addressed
and verified for offline use. Controls and Oracle belong to a later stage and
are intentionally absent from this audit.

## Static Commands Run

All commands were read-only with respect to the repository except for adding
this task-local evidence file. Source was fetched and inspected only in
`/tmp/nl2repo-markdown-it-source`.

```text
git clone --filter=blob:none --no-checkout https://github.com/markdown-it/markdown-it /tmp/nl2repo-markdown-it-source
git -C /tmp/nl2repo-markdown-it-source checkout --detach 1e8ab89ca299351879169a79d2627fe3a356ce4a
git -C /tmp/nl2repo-markdown-it-source show -s --format=... HEAD
git -C /tmp/nl2repo-markdown-it-source archive --format=tar HEAD | sha256sum
git -C /tmp/nl2repo-markdown-it-source ls-files
sha256sum package.json package-lock.json LICENSE README.md
node --version
npm --version
node <read-only manifest/lock parity and closure scan>
rg/nl/find <read-only API, export, plugin, test, and fixture inventory>
```

No upstream tests, npm install, npm ci, cache operation, build, package
execution, Docker, Harbor, Oracle, hidden-test, or shared-index command was
run.
