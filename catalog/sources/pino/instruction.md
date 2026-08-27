# Project Description

Build an installable CommonJS Node.js package named `pino` from an empty workspace. It is a fast structured logger: calls create newline-delimited JSON records, expose standard log levels, support child loggers, serializers, redaction, and deterministic formatting options.

The evaluator uses only JSON-compatible inputs and an in-memory writable destination. Do not require a network service, browser, database, native addon, worker transport, or external process.

# Supports

- Node.js 24.19.0 and npm 11.17.0 on Linux amd64/glibc.
- CommonJS package metadata with `name: "pino"`, an exact semantic version, `main` pointing to the package entry, and a package-root callable export.
- Installation must succeed with `npm ci --offline --ignore-scripts` from a v3 `package-lock.json`. Runtime dependencies must be exact, reproducible npm packages in the supplied offline closure; do not use git, URL, workspace, native, or lifecycle dependencies.
- The public task surface is the package root export and its deterministic in-memory logging behavior. Network transports, browser builds, TypeScript checking, and benchmarking are out of scope.

# API Usage Guide

## `require('pino')(options?, destination?)`

Return a logger function. The second argument may be a writable stream-like destination with `write(string)`; when omitted, logging may use the process output. `options` may contain `level`, `base`, `timestamp`, `messageKey`, `nestedKey`, `formatters`, `customLevels`, `useOnlyCustomLevels`, `redact`, `serializers`, and `mixin`.

The logger is callable with `(object, message?, ...args)`, `(message, ...args)`, or `(error, message?)`. Object fields are included in the JSON record. A message uses printf-style `%s`, `%d`, `%j`, and `%o` placeholders for subsequent arguments; extra arguments are represented consistently by the implementation. Records are newline-terminated JSON strings.

## Standard levels and thresholding

Expose `trace`, `debug`, `info`, `warn`, `error`, and `fatal` methods, plus `silent`. The default threshold is `info`; setting `level` suppresses methods below the threshold. Each record contains the level number under `level` and the level name is available through `level`/`levels` metadata as supported by the package.

`isLevelEnabled(name)` returns a boolean. `level` is readable and writable, and invalid level names raise an error. `setLevel(name)` changes the threshold and returns the logger.

## Child loggers

`logger.child(bindings, options?)` returns a logger that includes the supplied bindings in every subsequent record. Child bindings do not mutate the parent. Child options may override `level` and may set `msgPrefix`; the prefix is added to child messages.

## Serializers and errors

`serializers` is an object mapping field names to functions. When configured, matching object fields are transformed before output. The standard error serializer is available through the exported `stdSerializers.err` and preserves useful error properties such as type, message, and stack. Error objects passed as the first argument are serialized as error records rather than discarded.

## Redaction

`redact` accepts an array of dot-separated paths and optionally an object with `paths` and `censor`. Matching fields are replaced with the configured censor value, including nested object paths. Redaction applies to child bindings and logged objects while leaving unrelated fields intact.

## Metadata and utilities

Expose `pino.levels.values` and `pino.levels.labels` for the standard numeric mapping, `pino.stdSerializers`, `pino.stdTimeFunctions`, `pino.version`, and `pino.destination` as package utilities. `logger.flush()` and `logger.flushSync()` must be safe for the in-memory destination. The implementation may provide additional upstream APIs, but the deterministic contract above is the scored surface.

# Implementation Notes

Keep the package modular and installable from the empty workspace. Preserve JSON record determinism by using a stable field order for base fields, bindings, and logged fields where the API contract requires it. Thresholding must happen before destination writes. Child loggers must keep independent bindings and configuration.

The hidden tests use a fixed collection of 25 leaves covering the package root, installation metadata, standard levels and thresholding, printf formatting, object/error logging, child isolation and prefixes, custom levels, serializers, redaction, base/message-key options, and flush behavior. They do not require real sockets, transports, browser globals, native modules, or network access. Do not copy upstream source or tests.
