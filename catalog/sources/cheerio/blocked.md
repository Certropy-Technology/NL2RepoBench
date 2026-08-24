# `cheerio` Node Production Authoring Audit

**Status: blocked.** This file is task-local evidence for the Node production
authoring lane (batch `node-production-author-20260823`, candidate
`https-github-com-cheeriojs-cheerio-97d99ecf637b`). It is not a Harbor task, a
private test bundle, an Oracle, a dependency cache, a verifier, or a
publication approval. No upstream source bytes, test bytes, tarballs, npm
cache, or generated artifacts are stored in this directory. The only durable
write root used for this audit is `catalog/tasks/cheerio/`.

## Decision

Keep the candidate at lifecycle status `blocked`. At the frozen revision, the
root `cheerio` package contract and its official test suite require surfaces
that the first safe production scope forbids:

1. **Network loading is part of the root export contract.** The
   batteries-included entry exports `fromURL`, which constructs an `undici`
   `Client` with redirect interceptors and issues live HTTP requests
   (`src/index.ts:224-303`). `undici@8.10.0` is a required runtime dependency.
   The official `fromURL` tests bind real `node:http` loopback servers and
   fetch from `http://localhost:<port>` (`src/index.spec.ts:117-238`). The
   production contract is `no-network` for both agent and verifier, and the
   first safe scope excludes network APIs entirely.
2. **The package cannot be installed or imported without a build step.** All
   `exports` entries point at `dist/**`, `dist/` is `.gitignore`d, and zero
   `dist/` files are tracked. An `npm ci --omit=dev --offline --ignore-scripts`
   install of the runtime closure followed by `import('cheerio')` fails with
   `ERR_MODULE_NOT_FOUND`. Producing the entry points requires the `tshy`
   TypeScript dual build (`build: tshy`, `prepublishOnly: npm run build`) and
   therefore the development dependency closure.
3. **The development closure carries lifecycle, native-binary, and browser
   surfaces.** The committed v3 lock has 433 non-root entries; two carry
   `hasInstallScript` (`esbuild@0.28.1`, `fsevents@2.3.3`) and 68 are
   platform-conditional optional binaries (`@biomejs/cli-*`, `@esbuild/*`,
   `@rolldown/binding-*`, `@typescript/native-preview-*`, `lightningcss-*`,
   `fsevents`). The root package also declares a `prepare: husky` lifecycle
   script, and `tshy` emits a `browser` ESM export dialect from
   `src/index-browser.mts`. The first safe scope forbids lifecycle scripts,
   native addon binaries, and browser surfaces.
4. **The official suite is Vitest, not `node:test`, and includes type-level
   assertions.** `test:vi` runs `vitest run` (Vitest `^4.1.10` on the
   Vite/esbuild runtime). `vitest.config.ts` enables `typecheck` for
   `src/api/extract.spec.ts`, whose leaves include `expectTypeOf` assertions
   that exist only at the TypeScript type level. These cannot be carried into a
   private `node:test` bundle without dropping assertions and re-freezing a new
   denominator.
5. **The scored API does not fit the JSON candidate boundary without a major
   scope cut.** The public surface is a jQuery-style chaining object model:
   `load()` returns a callable `CheerioAPI`, selections are `Cheerio<T>`
   instances over `domhandler` nodes, and the official specs assert on
   instances and identity (267 `toBeInstanceOf`/`prevObject`/`toBe($…)` call
   sites). At least 50 spec call sites pass callback-valued arguments to
   `attr`/`prop`/`css`/`map`/`filter`/`each`/`replaceWith`. `loadBuffer` and
   `load(Buffer)` take binary `Buffer` input, and `stringStream`/`decodeStream`
   return Node `Writable` streams. Functions, class instances, node identity,
   buffers, and streams cannot cross a subprocess JSON boundary. A narrowed
   JSON-expressible subset (string-in/string-out load, select, serialize,
   string attributes) is technically deterministic but is a materially
   different task scope that has not been approved and would need its own
   boundary contract and frozen denominator.

Points 1–3 are contract violations of the first safe scope; points 4–5 make
the private `node:test` JSON-boundary bundle unauthorable without an approved
scope decision. Reopening requires an explicit scope ruling (see
"Reopen conditions").

## Candidate record

- Package: `cheerio` (npm), version `1.2.0`.
- Upstream: `https://github.com/cheeriojs/cheerio`.
- Requested and resolved revision:
  `808f8456b38a730497c675f1478d659cc4adfefe` (full SHA, not a floating ref).
- License: MIT (declared and verified below).
- Language: Node (TypeScript source, tshy ESM+CJS+browser dual build).
- Candidate source: `reports/npm-production-queue-20260823.json`
  (`candidate_id` `https-github-com-cheeriojs-cheerio-97d99ecf637b`,
  `risk_flags: []` at queue time; this audit supersedes that empty risk list
  with the evidence below).
- Batch plan: `reports/node-production-author-batch-20260823.json`, worker
  boundary `catalog/tasks/cheerio/** only`.

## Source lock

- Detached checkout of the full SHA; no `.gitmodules`; 126 tracked files.
- Commit tree: `b84ec85d60926863ada71bf857c849873d17a649`.
- Commit subject:
  `build(deps): bump astro from 7.2.1 to 7.2.2 in /website (#5447)`.
- Commit timestamp: `2026-08-21T03:14:10Z`.
- Deterministic archive command: `git archive --format=tar HEAD`.
- Three independent archive streams were each `1,525,760` bytes with SHA-256
  `bc9a92fdbe3d61dfc45561a119d1a3264ba9241ca3ead179d40b5c75e676cbdf`.
- The checkout lived only under `/tmp/nl2repo-cheerio-source/repo`; after the
  probes, `git status --porcelain` and `git clean -fdx` verification showed a
  clean tree (one probe-time `package.json` key reordering by `tshy` was
  restored and re-verified against the original hash). No source bytes were
  copied into this task directory.

## License evidence

- `package.json` declares `"license": "MIT"`; the tracked `LICENSE` file is
  the standard MIT grant ("Copyright (c) 2022 The Cheerio contributors").
- `LICENSE`: 1,081 bytes, Git blob `b0c8b1935816c646c0d6707cf4e2cdcd16c447f3`,
  SHA-256 `61c1e21d3a8ff20f9b69abe15104a75584688080febc22f60a4cbf3854becf4e`.
- `package.json`: 4,470 bytes, Git blob
  `68b662577124466da8fa5a824fedd00291538bd3`, SHA-256
  `6f271b85ccc23b078fe5c71a719733d03bef0aa9899a5134c9270a63eab60bb2`.
- Runtime dependency licenses observed in the lock: MIT, BSD-2-Clause, and ISC
  only. Formal dependency license review remains a separate closure step and
  is not claimed here.

## Package and exports evidence

The frozen `package.json` reports:

- `name: cheerio`, `version: 1.2.0`, `type: module`, `sideEffects: false`;
- Node engine `>=22.19.0` (satisfied by the production contract Node
  `24.19.0`);
- conditional `exports` for `.`, `./slim`, `./utils`, and `./package.json`,
  each with `import` (plus a `browser` dialect), `require`, and `types`
  conditions — every runtime target under untracked `dist/esm/**`,
  `dist/esm/browser/**`, or `dist/commonjs/**`;
- `main`/`module`/`browser`/`types` legacy fields also pointing at `dist/**`;
- `files` publishing `dist` and `src` while excluding `*.spec.*`,
  `__tests__`, and `__fixtures__`;
- scripts: `build: tshy`, `prepare: husky`, `prepublishOnly: npm run build`,
  `test: npm run lint && npm run test:vi`, `test:vi: vitest run`;
- 11 runtime dependencies and 24 development dependencies;
- no `bin` entries and no workspaces at the root (the tracked `website/`
  directory is an independent Astro docs site with its own
  `website/package-lock.json` and is not part of the npm package).

After a diagnostic build, the runtime ESM namespace exposed exactly these
value exports:

```text
contains decodeStream fromURL load loadBuffer merge stringStream
```

`fromURL`, `loadBuffer`, `stringStream`, and `decodeStream` — four of the
seven root value exports — are network, buffer, or stream surfaces. CJS
`require` interop resolved the same functions through `dist/commonjs`.
`npm pack --dry-run --ignore-scripts --json` after the build listed 227 files
(206 under `dist/`, 18 under `src/`, plus `LICENSE`, `Readme.md`,
`package.json`) with unpacked size `1,022,539` bytes. Packaging evidence only;
no tarball retained.

## Static inventory (tools/node-inventory)

`tools/node-inventory` was built from its committed lock (`npm ci`,
`npm run build`; scanner identity `node-typescript-compiler-api`) and run
twice, without importing or executing candidate code:

- Whole-repository scan (`node dist/cli.js /tmp/nl2repo-cheerio-source/repo`):
  `source_digest`
  `sha256:3eb9cfc6fbdf0a1ef3e53687e79d0dd04a4224f545cf035972773e9883e4799b`,
  39 source files, 14 test files, implementation LOC 4,099, test LOC 6,067,
  public symbols 193, imports 216, risk flags
  `dynamic-import`, `external-service`, `filesystem-access`, zero syntax
  diagnostics, module systems `esm` + `commonjs` (the `commonjs` signal comes
  from website/config tooling, not `src/`).
- `src/`-scoped scan (`node dist/cli.js …/repo/src`): `source_digest`
  `sha256:62d7707d065139a894013e1b565975f42f076c08a39cae7ed9ee557afbecc907`,
  implementation LOC 2,667, public symbols 139, module system `esm` only,
  risk flags `dynamic-import` + `external-service`, 911 recorded
  test/describe declarations across the 14 spec files.

Risk-flag attribution from the import table: `src/index.ts:33` imports
`undici` (type import plus lazy `await import('undici')` inside `fromURL`,
which also explains `dynamic-import`); `src/index.spec.ts:1` imports
`node:http`; `filesystem-access`/other service hits outside `src/` come from
`benchmark/benchmark.ts`, `scripts/fetch-sponsors.mts` (network sponsor
fetcher), and `website/astro.config.mjs`.

Tracked source shape: 18 runtime files under `src/` (5,499 physical lines
including comments; 2,667 scanner LOC), 14 `*.spec.ts` files (7,411 physical
lines), one fixture module `src/__fixtures__/fixtures.ts`.

## Lockfile and dependency evidence

The repository commits `package-lock.json` (228,728 bytes, SHA-256
`bef450757287b38d4075bd010a0c940cfb41b3deda6f259d7befc7885b3b3f5e`,
`lockfileVersion: 3`, 433 non-root entries, all 433 with integrity hashes, no
`link:` entries).

Runtime closure (transitive from the 11 declared dependencies): exactly 20
packages, all with integrity, none optional, none with install scripts, none
platform-conditional:

```text
boolbase@1.0.0 (ISC)                cheerio-select@2.1.0 (BSD-2-Clause)
css-select@5.2.2 (BSD-2-Clause)     css-what@6.2.2 (BSD-2-Clause)
dom-serializer@2.0.0 (MIT)          domelementtype@2.3.0 (BSD-2-Clause)
domhandler@5.0.3 (BSD-2-Clause)     domutils@4.0.2 (BSD-2-Clause)
encoding-sniffer@0.2.1 (MIT)        entities@4.5.0 (BSD-2-Clause)
htmlparser2@10.1.0 (MIT)            iconv-lite@0.6.3 (MIT)
nth-check@2.1.1 (BSD-2-Clause)      parse5@7.3.0 (MIT)
parse5-htmlparser2-tree-adapter@7.1.0 (MIT)
parse5-parser-stream@7.1.2 (MIT)    safer-buffer@2.1.2 (MIT)
undici@8.10.0 (MIT)                 whatwg-encoding@3.1.1 (MIT)
whatwg-mimetype@5.0.0 (MIT)
```

The runtime closure alone is offline-clean, but it includes `undici` (HTTP
client) and stream/encoding machinery whose only consumers are the network,
stream, and buffer entry points listed above.

Development closure (needed for `tshy` build and Vitest suite): the remaining
413 entries, including `hasInstallScript` on `esbuild@0.28.1` and
`fsevents@2.3.3` and 68 optional platform binary packages. Diagnostic installs
below used `--ignore-scripts` throughout; no lifecycle script ran.

Offline-closure probes with npm (disposable cache, deleted afterwards):

- empty-cache `npm ci --offline --ignore-scripts --no-audit --no-fund` failed
  closed with `ENOTCACHED`;
- after one network-backed `npm ci --ignore-scripts` populated a 77 MiB cache,
  the same offline command completed (371 packages installed);
- `npm ci --omit=dev --offline --ignore-scripts --no-audit --no-fund`
  installed exactly the 20-package runtime closure offline.

This demonstrates a viable npm v3 offline diagnostic path; it is not a
reviewed content-addressed lock/cache artifact.

## Test-shape evidence

Official command chain: `npm test` = lint (eslint + tsc + biome) then
`vitest run`. The scored path is `vitest run`.

Diagnostic network-backed baseline on the host toolchain (Node `26.7.0`, npm
`12.0.2` — **not** the production contract Node `24.19.0` / npm `11.17.0`;
diagnostic evidence only):

```text
Test Files  15 passed (15)
     Tests  799 passed (799)
Type Errors  no errors
  Duration  8.32s
```

Vitest JSON reporter leaf counts (799 total, 141 suites; `extract.spec.ts`
appears once as runtime tests and once as a typecheck project, giving 15 test
files over 14 spec modules):

| spec module | leaves |
| --- | ---: |
| `src/api/traversing.spec.ts` | 244 |
| `src/api/manipulation.spec.ts` | 197 |
| `src/api/attributes.spec.ts` | 127 |
| `src/cheerio.spec.ts` | 49 |
| `src/static.spec.ts` | 40 |
| `src/parse.spec.ts` | 35 |
| `src/api/extract.spec.ts` (runtime + typecheck) | 26 |
| `src/__tests__/deprecated.spec.ts` | 20 |
| `src/api/css.spec.ts` | 16 |
| `src/api/forms.spec.ts` | 16 |
| `src/index.spec.ts` | 14 |
| `src/__tests__/xml.spec.ts` | 7 |
| `src/load.spec.ts` | 4 |
| `src/utils.spec.ts` | 4 |

Boundary-incompatible content observed in the suite:

- `src/index.spec.ts` `describe('fromURL')` starts live `node:http` servers
  on ephemeral loopback ports and asserts fetch, redirect history,
  content-type rejection, and charset sniffing over real sockets;
- stream leaves assert `toBeInstanceOf(Writable)` and drive chunked writes,
  including UTF-16/BOM `Buffer` payloads;
- 50+ call sites pass callbacks into `attr`/`prop`/`css`/`map`/`filter`/
  `each`/`replaceWith`;
- 267 instance/identity assertions (`toBeInstanceOf`, `prevObject`,
  `toBe($…)`) depend on same-process object identity;
- `src/api/extract.spec.ts` mixes runtime leaves with `expectTypeOf`
  type-level assertions that only exist under the Vitest typecheck runner.

No frozen denominator is claimed. The static scanner records 911 declaration
sites (including `describe` blocks and loop-generated declarations), while the
runtime leaf count is 799; any future adaptation must freeze its own
collection.

## Build evidence

- With only the runtime closure installed and no build, `import('cheerio')`
  fails with `ERR_MODULE_NOT_FOUND` (exports target untracked `dist/**`).
- With the dev closure installed offline (`--ignore-scripts`), `npm run build`
  (`tshy`) completed in ~9 s on the host and emitted `dist/esm`,
  `dist/esm/browser`, and `dist/commonjs`. `tshy` also rewrote the
  `package.json` exports key order as a build side effect; the checkout was
  restored to the frozen bytes afterwards.
- After the build, three repeated in-process probes of the JSON-expressible
  core produced identical output:

  ```json
  {"html":"Apple","text":"AppleOrange","attr":"apple","count":2,
   "serialized":"<li class=\"orange\">Orange</li>"}
  ```

  This confirms the load/select/serialize core is deterministic and
  JSON-expressible in isolation; it does not make the full scored surface
  boundary-safe.

## Reopen conditions

Reopen only with an explicit, supervisor-approved scope decision that either:

1. narrows the task to a JSON-expressible `slim`-style subset (string-in
   `load`, selector queries, string/array attribute and serialization
   outputs; no `fromURL`, `loadBuffer`, streams, callbacks, or identity
   assertions), with its own boundary contract, a re-frozen private
   `node:test` denominator derived from — but not equal to — the 799-leaf
   Vitest suite, and a committed-`dist`-or-build ruling for the entry points;
   or
2. accepts a broader scope in a later campaign wave that permits loopback
   networking, buffers, and streams under a revised production contract.

Until then this candidate must not receive an instruction, a Harbor bundle, a
private test package, an Oracle, controls, or a dataset entry.

## Validation record

Completed read-only or disposable checks (host: Node `26.7.0`, npm `12.0.2`,
git `2.55.0`; all mutable state under `/tmp`, deleted or restored afterwards):

- exact full-SHA fetch and detached checkout; tree, subject, timestamp, and
  tracked-file inventory; triple archive hashing;
- `LICENSE`, `package.json`, and `package-lock.json` size/blob/SHA-256
  evidence;
- `tools/node-inventory` build from its committed lock and two AST scans
  (whole repository and `src/`), with risk-flag attribution;
- lockfile analysis: runtime/dev closure split, integrity coverage, install
  scripts, optional platform binaries;
- empty-cache offline fail-closed probe, network-backed cache population,
  populated-cache offline full and runtime-only `npm ci` probes;
- no-build import failure probe; offline `tshy` build; ESM/CJS export
  namespace probes; repeated deterministic core-output probe; `npm pack`
  dry run;
- disposable network-backed `vitest run` official baseline (799/799 passed)
  and JSON-reporter leaf census;
- cleanup verification: checkout restored to frozen bytes, caches and
  `node_modules`/`dist` deleted.

Not run by design: Docker, the production Node `24.19.0` image, Harbor
compilation, private test authoring, Oracle, negative controls, publication.
No shared script, doc, dataset, toolchain, or other task file was modified.
