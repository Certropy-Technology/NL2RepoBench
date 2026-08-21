# npm / Node Pilot Candidates

Research date: 2026-08-21

This is a discovery artifact for the future `nl2repobench-node-pilot-v1`.
These packages are not part of the Python dataset and none is approved for
publication yet. Each still needs source freeze, package-manager closure,
license audit, hidden-test provenance, controls, and three valid Oracle runs
with stable collection and reward >= 0.80.

## First Wave

| Package | GitHub revision | License | Test/runtime shape | Recommendation |
|---|---|---|---|---|
| `jsonc-parser` | `900046d46a96dd5d014030e37c0055157921ef92` | MIT | Node 22, npm lockfile, Node test runner, ESM, no runtime deps | Accept first wave; scope to JSON-compatible parse/tree/edit APIs |
| `canonicalize` | `c1b08c3771d681c8bd9c4d8765e00f2f717482f8` | Apache-2.0 | Node >=18, `node:test`, ESM, no upstream lockfile | Accept first wave; generate and pin a project lockfile |
| `query-string` | `aae373a54526c7b297f60e4d7b77eb0709d2ae9c` | MIT | Node >=18, AVA/TAP, ESM, small JS dependencies, no lockfile | Accept with JSON-only options and generated lockfile |
| `qs` | `3a890d4ecd3deb72a45d90be36f4f8c5970467c7` | BSD-3-Clause | CommonJS, Tape/TAP, small JS deps, no lockfile | Accept using `tests-only`; never run network-capable posttest audit |
| `validator` | `a79ff980ab14257e795332989e497bdff3218e87` | MIT | CommonJS, Mocha, no runtime deps, generated build output | Accept; pin build toolchain and test generated package output |
| `stringify-object` | `c359727290822d9cabf7c07fb86cdb08701c1010` | BSD-2-Clause | Node test runner/TAP, ESM, small JS deps, no lockfile | Accept with JSON-only values/options; exclude callbacks/cycles |

## Second Wave

`yaml` (`b91c3747333c7379bfd6edb6000fa163ca33805b`), `smol-toml`
(`6d0f4774700c40ce8b5794934eb771870a9a93d3`), `markdown-it`
(`1e8ab89ca299351879169a79d2627fe3a356ce4a`), `fast-json-stringify`
(`6aa2ed4cc403cf68d7c31ee4dd14724372fea664`), and `fast-xml-parser`
(`7d608151078d47040841e9804d490feb5c07dfe7`) are viable after explicit
scope restrictions. They have broader build, lockfile, workspace, or dynamic
code-generation risks.

`csv-parse` (`3591c0770f7235b203f7cbcd7805ddedfaaf3ce1`) is deferred because
the source is an npm workspace monorepo; only the `csv-parse/sync` subpath
would be suitable for an initial task.

## Required Node Contract

- digest-pinned Node LTS image and package-manager binary;
- committed lockfile or a separately generated, content-addressed lockfile;
- offline install from an immutable npm tarball/cache closure;
- lifecycle scripts disabled by default and explicit build scripts allowlisted;
- no native addons, browser services, workspace monorepos, or `npx` downloads in
  the first pilot;
- candidate code imported only in an unprivileged Node child process;
- JSON request/response boundary; callbacks, streams, class instances, cycles,
  custom plugins and browser globals are excluded from the public contract;
- framework-specific structured reports (`node:test` TAP/JSON, Mocha JSON/TAP,
  Vitest JSON) with a leaf-test denominator;
- separate `fixed-leaf-test-pass-rate-node-v1` metric contract;
- agent/verifier network isolation and controls for forged reports, loader hooks,
  install scripts, symlink trees, hangs, and reporter/config tampering.

## Primary Evidence

- `jsonc-parser`: <https://github.com/microsoft/node-jsonc-parser/commit/900046d46a96dd5d014030e37c0055157921ef92>
- `canonicalize`: <https://github.com/erdtman/canonicalize/commit/c1b08c3771d681c8bd9c4d8765e00f2f717482f8>
- `query-string`: <https://github.com/sindresorhus/query-string/commit/aae373a54526c7b297f60e4d7b77eb0709d2ae9c>
- `qs`: <https://github.com/ljharb/qs/commit/3a890d4ecd3deb72a45d90be36f4f8c5970467c7>
- `validator`: <https://github.com/validatorjs/validator.js/commit/a79ff980ab14257e795332989e497bdff3218e87>
- `stringify-object`: <https://github.com/sindresorhus/stringify-object/commit/c359727290822d9cabf7c07fb86cdb08701c1010>
- Node/npm feasibility and compiler blockers: [npm-node-task-feasibility.md](../docs/npm-node-task-feasibility.md)
