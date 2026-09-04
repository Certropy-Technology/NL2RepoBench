# `type-fest` blocked authoring record

**Status: blocked.** This task is a source and verifier audit only. The exact
revision and licenses are frozen, but no Harbor runtime, candidate package,
private tests, Oracle, controls, or generated task is claimed.

## Project Description

`type-fest` is a collection of TypeScript type-level utilities. The requested
revision publishes declarations (`index.d.ts` and `source/**/*.d.ts`) rather
than executable library functions. Its value is observed by the TypeScript
compiler during static checking, not by a JavaScript runtime response.

## Supports

The frozen package metadata is `type-fest` version `5.9.0`, ESM package type,
Node engine `>=20`, and license expression `MIT OR CC0-1.0`. The exact tree
contains 217 declaration files, 216 source declaration files, and 221
`test-d/*.ts` type-test files. It has one declared runtime dependency,
`tagged-tag@^1.0.0`, imported as a type from `source/tagged.d.ts`, and no
committed `package-lock.json`, `npm-shrinkwrap.json`, or other npm v3 lock.

Every Agent, candidate, verifier, Oracle, and control phase must use
`network_mode=no-network`. Runtime access to GitHub, npm, PyPI, Go proxy, and
external services is forbidden. The source archive was fetched only during
authoring from the requested immutable commit and is not placed in this
public task directory.

## API Usage Guide

The package root exports TypeScript types through `index.d.ts`, including
utilities such as `Merge`, `PartialDeep`, `Jsonify`, `CamelCase`, numeric
literal predicates, string-case utilities, and collection/object helpers. The
`./globals` export is also type-only. There is no callable JavaScript API,
runtime value export, CLI, or JSON request/response contract to expose to the
current Node child-process verifier.

An ordinary faithful test would compile a fixture that imports selected types
and assert expected assignability or expected compiler errors. The upstream
`test-d` suite uses `tsd` assertions such as `expectType`,
`expectAssignable`, `expectNotAssignable`, and `expectError`; these are
TypeScript diagnostics, not `node:test` leaves.

## Implementation Notes

This candidate must remain blocked until a separate verifier is designed and
reviewed around a pinned TypeScript compiler and a JSON-safe diagnostic
protocol. Declaration text comparison, JavaScript import checks, lint-only
checks, or a synthetic runtime implementation would not be faithful to the
package's type-level behavior. The verifier must select a bounded, traceable
subset or freeze the complete type-test collection, preserve positive and
negative diagnostic semantics, and isolate compiler output from trusted
reports.

The direct runtime probe for both ESM import and CommonJS `require` returns
`ERR_PACKAGE_PATH_NOT_EXPORTED` because the package export map provides only
`types` conditions. The package also declares test scripts and range-based
development dependencies without a lock/cache closure, so no candidate build
or test installation is reproducible under the current offline contract.

Reopen only after producing a reviewed npm v3 private artifact closure,
pinning the TypeScript/tsd toolchain, authoring a separate compiler-diagnostic
verifier, freezing its denominator, and running official NoNetwork Oracle,
empty, stub, forgery, and offline controls. No `catalog/tasks/type-fest/`
directory may exist while this record remains blocked.
