# `ow` blocked authoring record

Status: **blocked**. This source-local record freezes the assigned upstream
revision and documents the dependency and verifier boundary blockers. It is
not a Harbor runtime or publication approval. No `catalog/tasks/ow/` projection,
private dependency cache, hidden test bundle, Oracle payload, or control result
is present.

## Frozen Source

- Package: `ow` `3.1.1`.
- Upstream: `https://github.com/sindresorhus/ow`.
- Exact revision: `3975eab08762ba1823f07e2aa3cb05f20c86296c`.
- Commit tree: `0f6785555daf2cdd3ecd25e721c8bdd10404977f`.
- Commit date: `2025-10-17T02:10:05+09:00`.
- The detached checkout contains 89 tracked files, 34 source files, and 40 upstream test files.
- Reproducible source archive: 634,880 bytes, SHA-256 `bc70bf80d6125a8869d314ea7c1004e61eefdef9763eeda6fd3945d8bb1cb183`.
- `license` is MIT, 1,117 bytes, SHA-256 `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- The revision contains `.npmrc` with `package-lock=false` and no committed `package-lock.json`.

## Dependency Blocker

The package declares six runtime dependencies:

```text
@sindresorhus/is ^7.1.0
callsites ^4.2.0
dot-prop ^10.1.0
environment ^1.1.0
fast-equals ^5.3.2
is-identifier ^1.0.1
```

The required authoring probe was run from the exact source tree:

```text
npm install --package-lock-only --ignore-scripts --offline --no-audit --no-fund
```

It exited `1` with npm `ENOTCACHED` for
`https://registry.npmjs.org/@sindresorhus%2fis`. Cache inspection found no
complete cached closure: `@sindresorhus/is`, `dot-prop`, `environment`,
`fast-equals`, and `is-identifier` had zero matching cache entries; only
unrelated `callsites` entries were present. Because runtime registry access is
forbidden, an immutable npm v3 lock/cache artifact cannot be produced in this
lane.

## Verifier / Adapter Assessment

The public package is a broad TypeScript ESM predicate framework. Its root
exports `ow`, `ArgumentError`, `Predicate`, `isPredicate`, and predicate
families for strings, numbers, arrays, objects, dates, errors, Maps, Sets,
typed arrays, buffers, promises, iterables, and modifiers (`optional`,
`nullable`, `absent`). It also supports `any`, `not`, `create`, `isValid`, and
`validate`.

Several APIs use values that cannot cross the trusted JSON subprocess boundary
directly: callbacks for `ow.create` and `.validate`, regular expressions,
symbols, functions, native objects such as `Map`, `Set`, `Date`, `Error`, and
typed arrays, plus assertion errors carrying `validationErrors` Maps. A safe
reopen requires a reviewed child-side scenario adapter that accepts only a
bounded declarative JSON grammar, constructs these values inside the candidate
child, and returns bounded normalized success/error records. The adapter must
cover representative predicate families, modifiers, shape validation,
negation, reusable validators, and malformed-request rejection without
exposing arbitrary executable strings, module paths, filesystem input, or
network access.

The upstream test suite is broad (40 files, 5,173 test-file lines) and cannot
be used as a frozen denominator until that adapter and a source-only test
collection are authored. No Oracle or controls were run, and no reward is
claimed.

## Remediation

1. Materialize a complete npm v3 lock/cache closure for the six declared runtime dependencies under Node 24.19.0/npm 11.17.0, with every tarball digest and size recorded as a private artifact.
2. Review and approve a bounded JSON scenario adapter for predicates, callback-free custom scenarios, native values, symbols, and normalized `ArgumentError` output; freeze its private tests and collection.
3. Compile a production task only after the private dependency, verifier, test, and Oracle artifacts resolve offline; then run the official NoNetwork Oracle and empty/stub/forgery/offline controls.

Until these steps are complete, `ow` remains blocked and has no generated task.
