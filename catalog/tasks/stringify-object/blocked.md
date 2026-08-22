# `stringify-object` Node v2 Development Evidence / Blocked Record

**Status: blocked.** This is a task-local development audit, not a Harbor
bundle or a publication approval. It contains no hidden tests, private test
commands, Oracle solution, verifier, Docker asset, dependency cache, secret,
or generated candidate package.

## Candidate Lock

- Package: `stringify-object` `7.0.0`
- Upstream: `https://github.com/sindresorhus/stringify-object`
- Frozen revision: `c359727290822d9cabf7c07fb86cdb08701c1010`
- Commit tree: `ec2212a53155afeea2c5f86b92c5cc8883ddb895`
- Commit timestamp: `2026-07-03T00:24:32+02:00`
- Commit subject: `7.0.0`
- Git archive SHA-256:
  `4076617d57ba117f7bc776c0a1124d544441bdbaa7572d2afcc17e2e28811dc3`
- License: BSD-2-Clause, declared by `package.json` and present in `license`.
  The checked license file SHA-256 is
  `301f5b704b9d17d0a00e3dd51b743bd20bd999678d085db60c8d5ed513a163e6`.
- The detached checkout was clean, has no submodules, and contains 13 tracked
  files. The upstream `.npmrc` sets `package-lock=false`; there is no
  committed `package-lock.json` or `npm-shrinkwrap.json` at this revision.

## ESM and Public JSON Boundary

The pinned `package.json` declares `type: module`, Node `>=22`, and the root
export with `types: ./index.d.ts` and `default: ./index.js`. The scored API
candidate is the default export:

```js
stringifyObject(input, options?) -> string
```

The development v2 contract must restrict requests to values representable by
JSON: `null`, booleans, finite numbers, strings, arrays of JSON values, and
objects with string keys whose values are JSON values. JSON input is handled
through a bounded child-process request/response boundary; JavaScript object
identity and prototypes are not part of the request format.

The JSON-compatible options subset is an object containing only these
JSON-serializable values:

- `indent`: string, default `"\t"`, including the empty string;
- `singleQuotes`: boolean, default `true`; and
- `inlineCharacterLimit`: finite number when supplied.

The output is JavaScript-style, human-readable source text: arrays and
objects are formatted with the selected indentation, strings use the selected
quote style, object keys are quoted only when required, and own `__proto__`
keys are omitted. Array order and JSON object enumeration order are preserved.
Empty arrays and objects are emitted in their compact forms. Repeated calls
with the same JSON request and options must be deterministic and must not
mutate the request.

The following upstream surface is deliberately **excluded** from this JSON
contract and must not be smuggled through the adapter:

- callback-valued `filter` and `transform` options;
- cyclic object graphs, including the upstream `"[Circular]"` behavior;
- `Map`, `Set`, `Date`, `RegExp`, `BigInt`, `Symbol`, `undefined`, functions,
  class instances, custom prototypes, and custom `toJSON` behavior;
- the undocumented third `rootPad` parameter; and
- filesystem, CLI, network, loader, and test-helper entry points.

The callback and cycle exclusions are intentional. They keep the candidate
protocol JSON-only rather than claiming complete JavaScript parity with the
upstream implementation.

## ESM and `node:test` Evidence

- `index.js` imports five runtime packages and exports one default function.
- `index.d.ts` exposes one default function and documents the callback options
  and broader JavaScript input types; those declarations are evidence of the
  upstream surface, not permission to widen the scored JSON boundary.
- `test/index.js` contains 22 top-level `node:test` declarations in one suite.
  The upstream command portion is `node --test test/index.js`; the package
  `test` script additionally runs `xo` before that command.
- With Node `22.23.1` and npm `10.9.8`, a temporary dependency install using
  `npm install --ignore-scripts --omit=dev --no-audit --no-fund` followed by
  `node --test test/index.js` passed all 22 tests (`22` passed, `0` failed,
  `0` skipped, `0` todo).
- The upstream suite intentionally covers callbacks, cycles, Maps, Sets,
  symbols, dates, regular expressions, `undefined`, and BigInt. Those tests
  are useful source evidence but cannot be copied or treated as the frozen
  denominator for the narrowed JSON task.

## npm Lock and Cache Evidence

The source has five range-based runtime dependencies:

```text
get-own-enumerable-keys ^1.0.0
is-identifier            ^1.0.1
is-obj                   ^3.0.0
is-regexp                ^3.1.0
quote-js-string          ^0.1.0
```

It has one range-based development dependency, `xo ^3.0.2`. A temporary npm
`10.9.8` metadata-only probe generated a lockfile v3 with 405 `packages` keys
(404 non-root entries), all resolved from `registry.npmjs.org` with integrity
metadata. The temporary lockfile was 194,661 bytes with SHA-256
`1838e8baa94f58e46ff4a5c0c1ecca8eef6ef4ff620a6e029da261efefe0a833`.
It was not copied into this task directory.

The generated lock alone is not an offline closure. Against a fresh empty
cache:

```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

failed with `ENOTCACHED` for `zwitch-2.0.4.tgz`. A second probe using
`--omit=dev` against the same generated lock also failed against an empty
cache, first reporting `web-worker-1.5.0.tgz`. These are expected evidence of
missing cache material, not claims that the upstream implementation is broken.
The successful temporary network install and its cache were discarded; no
cache bytes or registry credentials are part of this record.

Before reopening the task, produce a separately reviewed, content-addressed
public/private dependency artifact containing:

- a manifest-aligned v3 `package-lock.json` generated with npm `10.9.8`;
- every package tarball required by the selected runtime/test closure;
- integrity and registry provenance checks, with no `git`, `file`, `workspace`,
  `link`, native addon, or unreviewed lifecycle dependency; and
- a bundle manifest accepted by `validate_npm_dependency_bundle`.

The verifier must install only from that closure using
`npm ci --offline --ignore-scripts --no-audit --no-fund`. Network installation
success is not evidence of an acceptable offline bundle.

## Candidate Protocol

The eventual candidate/verifier contract should be:

1. The candidate package is built from an empty workspace with ESM metadata,
   the root `exports` entry, and the exact Node 22/npm 10.9.8 runtime profile.
2. The candidate is packed with `npm pack` and the tarball contents are
   inspected before installation. Installation occurs in an isolated target
   from the reviewed cache closure with lifecycle scripts disabled.
3. A verifier-owned, unprivileged Node child process imports only the default
   package export. Requests and responses are line-delimited JSON; stdout is
   reserved for protocol data and diagnostics do not control grading.
4. The trusted runner owns test files, command plans, report paths, collection,
   and the fixed leaf-test denominator. Candidate code cannot select the
   reporter, loader, `NODE_PATH`, npm cache, registry config, protected paths,
   or reward/result files.
5. Private adapter tests must exercise the JSON values/options above and must
   record callback, cycle, and other JavaScript-only inputs as out of scope,
   rather than silently passing them through a non-JSON channel.

## Blockers and Reopen Conditions

Do not compile or publish this candidate. The lane remains blocked because:

- no reviewed lock/cache closure or durable dependency artifact exists;
- no private JSON-boundary test bundle or command artifact exists;
- no stringify-object-specific separate verifier, structured reporter, or
  frozen private collection exists; and
- no Oracle, empty/stub, forgery, install-failure, hang, or offline controls
  have been authorized or run.

Reopen only after the dependency closure, final Node image/runtime lock, JSON
adapter and private tests, separate verifier, and control plan are reviewed.
Then freeze the scoped leaf denominator and run the Node Oracle and controls
separately from the Python dataset.
