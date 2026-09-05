# Build `winston`

```text
workspace/
├── package.json
├── package-lock.json
└── lib/winston.js
```

## Project Description

Create a complete installable npm package named `winston`, version `3.19.0`,
from an empty workspace. Winston is a CommonJS logging library. It creates
loggers with configurable severity levels, formats records, and delivers them
to stream-like transports.

This is a repository-generation task. Implement the behavior described below
with your own source files. Do not copy the reference repository or its tests.

## Natural Language Instruction

Create the CommonJS package from an empty `workspace/`. Implement the listed
logger, format, transport, container, profiling, and lifecycle APIs with local
stream behavior. Preserve levels, metadata, callbacks, and EventEmitter
conventions.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc.
- CommonJS package semantics. The package root must be importable with
  `require('winston')` and have `main: "./lib/winston.js"`.
- A committed npm v3 lockfile must make the package installable with:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Runtime dependencies must be declared in `package.json` and resolved by the
  lockfile. Do not use git, file, workspace, native-addon, or network
  dependencies. Do not add lifecycle hooks that execute candidate code during
  installation.
- The scored behavior is deterministic and local. File rotation, HTTP
  delivery, process exit handling, and stress-scale concurrency are outside
  this task.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── lib/{winston.js,winston/logger.js,winston/create-logger.js}
```

The package root resolves to `lib/winston.js` and retains documented CommonJS
submodules.

## API Usage Guide

### Package exports and configuration

`require('winston')` returns an object exposing `version`, `config`, `format`,
`transports`, `createLogger`, `Logger`, `Container`, `Transport`, `loggers`,
and the default logger methods `error`, `warn`, `info`, `http`, `verbose`,
`debug`, `silly`, `log`, `child`, `profile`, and `startTimer`.

`winston.config.npm.levels` is the ordered npm level map:
`error: 0`, `warn: 1`, `info: 2`, `http: 3`, `verbose: 4`, `debug: 5`, and
`silly: 6`. Lower numeric values are more severe. `config.syslog.levels` and
`config.cli.levels` are also available maps.

`winston.createLogger(options)` returns a Logger. It accepts `level`,
`levels`, `format`, `defaultMeta`, `silent`, `transports`, `exitOnError`, and
the exception/rejection handler options. `level` defaults to `info` for npm
levels. `defaultMeta` is merged into every emitted record, with per-call
metadata taking precedence.

### Logging and records

The level methods accept `logger.info(message, ...meta)` and the generic method
accepts `logger.log(level, message, ...meta)` or an object containing at least
`level` and `message`. A call returns the same logger. Records preserve the
level and message and may contain metadata fields.

Messages may be strings, numbers, objects, or Errors. Error records must retain
the error message and stack information when the error format is used. A
logger with `silent: true` emits no records. A logger only emits levels at or
above its configured threshold. `isLevelEnabled(level)` and the convenience
checks report the same decision.

`logger.child(meta)` returns a logger that inherits the parent configuration
and merges the child metadata into its records. `logger.configure(options)`
replaces the logger configuration. `add(transport)`, `remove(transport)`,
`clear()`, and `close()` manage its transports and return the documented
logger result where applicable.

### Formats

`winston.format` exposes format factories including `json()`, `simple()`,
`prettyPrint()`, `splat()`, `errors(options)`, `colorize(options)`,
`timestamp(options)`, `label(options)`, `ms()`, `align()`, and `combine(...)`.
Formats are composable. `format.combine(a, b)` applies formats in order, and
`format.printf(fn)` creates a format whose returned string is emitted by a
transport. JSON output is one JSON record per line; simple output includes the
level and message in a human-readable line.

### Transports and lifecycle

`winston.transports.Stream` writes formatted records to a supplied writable
stream. `winston.transports.Console` targets stdout/stderr and accepts the
usual logger options. A custom transport may extend the exported `Transport`
base class and implement `log(info, callback)`. The logger must preserve
transport order and allow a stream transport to receive records without a
network service.

`logger.startTimer()` returns an object with `done(meta)` that records the
elapsed operation. `logger.profile(id, meta)` starts a profile on first use and
completes it on the next use. These methods are deterministic in shape; tests
do not require a particular wall-clock duration.

`winston.Container` manages named loggers. `get(id, options)` creates or
returns a logger, `has(id)` reports membership, and `close(id)` closes one or
all managed loggers. `winston.loggers` is the default Container.

## Examples

```js
const winston = require('winston');
const logger = winston.createLogger({format: winston.format.json(), transports: []});
logger.info('started', {service: 'demo'});
logger.startTimer().done('finished');
```

Use local stream transports to inspect records, configure levels and formats,
and manage named loggers with a `Container`.

## Error Handling and Boundary Conditions

Unknown levels, invalid transport options, missing callbacks, and lifecycle
changes follow the documented errors and return values. File, HTTP, and
process-termination behavior is outside this local task.

## Implementation Notes

- Keep public entry points and transport modules under the package exports.
- Preserve Node stream and EventEmitter behavior, callback completion, level
  filtering, metadata merging, and CommonJS imports.
- Installation and packaging must work from a clean checkout with the offline
  commands above. Do not depend on a globally installed Winston copy.
