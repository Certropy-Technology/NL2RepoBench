# `utility-types` authoring audit — blocked

**Status: blocked / audit-only.** This task records a frozen source identity and
the evidence for a real verifier boundary blocker. It is not a Harbor runtime,
private test bundle, Oracle payload, or publication approval. No
`catalog/tasks/utility-types/` directory is created.

## Project Description

`utility-types` 3.11.0 is a TypeScript utility-type collection. Its principal
surface consists of mapped, conditional, indexed-access, recursive, and
distributive type aliases used by a consumer program at compile time. The
revision also contains a small runtime guard surface, but those guards are not
an adequate representation of the package as a whole.

## Frozen Source

- Package: `utility-types` 3.11.0.
- Upstream: `https://github.com/piotrwitek/utility-types`.
- Full immutable revision:
  `fb06cf0c7d2768e39b78bed8b7ca94727998cb2f`.
- Commit tree: `ac59befe061fd3865362662975c5192b029b6f65`.
- Commit subject: `Update contribution guidelines for PR submissions`.
- Commit time: `2026-05-09T12:55:38+02:00`.
- Reproducible `git archive --format=tar HEAD`: 450,560 bytes,
  SHA-256 `89ef3a2ba2f2f0b8d1adfec0e2be2c0a066b1333b6fc8483539f563987d279e6`.
- `LICENSE`: MIT, SHA-256
  `eba0c3a8b90636744cc57e1a90f2d87767a57cccc86578a8168130f96896c9a9`.
- `package.json`: SHA-256
  `8fcdeaa7f9f671e378e9a3d7e6ee8b9561ce5a6fcf8da79a1c8d2386e87cc37d`.
- `package-lock.json`: SHA-256
  `7dee1211429063026504ca740ce3904ced98942d33692eecedf123dd578f161b`.
- The detached checkout was clean and had no submodules.

The source archive was generated twice and produced identical bytes and digest.
The source freeze, license, and reproducibility commands are recorded in
`evidence/source-freeze.txt`.

## Surface and Verifier Audit

The package exports 59 type aliases/interfaces and four runtime functions or
constants. The type-level surface includes `$Keys`, `$Values`, `$ReadOnly`,
`$Diff`, `$PropertyType`, `$ElementType`, `$Call`, `Assign`, `Brand`,
`DeepNonNullable`, `DeepPartial`, `DeepReadonly`, `DeepRequired`, `Diff`,
`FunctionKeys`, `Intersection`, `Mutable`, `Omit`, `Overwrite`, `PromiseType`,
`UnionToIntersection`, `ValuesType`, and related mapped/conditional utilities.

The runtime surface is `isPrimitive`, `isFalsy`, `isNullish`, and the deprecated
`getReturnOfExpression` helper. A verifier that tests only these functions would
allow an implementation with incorrect or missing type aliases to pass while
failing the package's primary purpose.

The upstream tests demonstrate this split:

- 145 `@dts-jest:pass:snap` declaration/type assertions;
- seven Jest runtime `it(...)` leaves for the guards;
- TypeScript 3.7.2 is the pinned compiler in the package development metadata;
- the package has no committed `dist/` output in this revision, so build output
  must also be produced deterministically before a candidate can be installed.

The current production Node verifier uses `node:test` leaves and a JSON
subprocess boundary for JavaScript behavior. It has no candidate-side
TypeScript compiler/type-check protocol, no declaration assertion report
format, and no way to grade the 145 compile-time assertions without adding a
new runtime/compiler contract. Replacing those assertions with declaration
file text matching or runtime guard checks would not be faithful.

## Dependency and NoNetwork Audit

The exact lock file has 698 package entries, 631 with integrity metadata, and
pins development tools including TypeScript 3.7.2, Jest 24.9.0, ts-jest,
dts-jest, TSLint, Prettier, and Jest type definitions. An offline `npm ci`
probe with an empty npm cache failed closed with `ENOTCACHED` for
`yargs-parser@7.0.0`. No dependency/cache bundle is therefore claimed.

All future agent, candidate, verifier, Oracle, and control phases must use
`network_mode=no-network`. Runtime GitHub, npm, PyPI, Go proxy, and external
service access is forbidden. A future repair must inject the complete,
hash-locked npm closure and a reviewed type-check verifier/Oracle as private
artifacts before any compilation or Harbor run.

## Blocking Decision and Remediation

This task is blocked for two coupled reasons:

1. the exact npm development/test closure is not frozen for offline execution;
2. the current verifier cannot faithfully test TypeScript compile-time behavior.

Remediation is to design and review a dedicated NoNetwork TypeScript verifier
that runs a pinned compiler in an unprivileged candidate subprocess against
private consumer programs, records compiler diagnostics in a fixed leaf report,
and separately covers the small JSON-safe runtime guard surface. Then freeze
the complete npm cache/lock closure, source/build artifacts, private tests, and
Oracle payload, rerun source-only baseline tests, and compile a fresh runtime.
Until that work is complete, this candidate remains truthfully blocked rather
than being reduced to a runtime-only task.
