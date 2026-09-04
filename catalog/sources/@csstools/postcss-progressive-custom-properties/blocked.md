# @csstools/postcss-progressive-custom-properties

Status: **blocked**

## Project Description

The frozen upstream package is an ESM PostCSS plugin that wraps progressive
custom-property overrides in a suitable `@supports` rule. The package exports
one `PluginCreator<null>` from `dist/index.mjs` and declares the CommonJS
compatibility export required by its package metadata.

## Supports

The source and package metadata are frozen and licensed as MIT-0. The package
metadata identifies `postcss-value-parser` as a runtime dependency, `postcss`
as a peer dependency, and Node `>=20.19.0` as the engine requirement.

## API Usage Guide

The public entry point is the default export from
`@csstools/postcss-progressive-custom-properties`. Its creator signature is
`creator(options?: null): Plugin`, as declared in `dist/index.d.ts`. It is
intended to be used in a PostCSS plugin pipeline, where declarations containing
custom-property fallbacks are transformed deterministically. The package is
not a standalone CSS parser or command-line tool.

## Implementation Notes

The source revision, package metadata, license, and upstream CSS fixtures were
inspected. The source-only test inventory contains two CSS fixture pairs and
three module harness files. A production task cannot yet be compiled because
the exact private npm cache/lock closure for the monorepo test harness is not
available. A bounded `npm ci --offline --ignore-scripts` probe fails with
`ENOTCACHED` for `zod@4.4.3` before collection. The runtime peer boundary also
needs a reviewed child-side PostCSS adapter so a trusted verifier never imports
candidate code directly.

No Oracle, controls, generated Harbor runtime, or reward is claimed.

Remediation: freeze a package-scoped npm lock/cache containing the runtime
dependency and PostCSS peer, define a child-side JSON CSS processing adapter,
collect a fixed source-only denominator, then compile and rerun Oracle and all
required controls against the final manifest.
