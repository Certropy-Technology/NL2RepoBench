# Project Description

Build an installable npm package named `pretty-ms` from an empty workspace. It
converts a finite millisecond duration into a compact, human-readable string,
such as `1337000000` to `15d 11h 23m 20s`. The package must be an ESM module
with a single default function export and deterministic behavior. Do not add a
CLI, service, native addon, network access, or lifecycle hook.

# Supports

- Node.js 24.19.0 on Linux x64 with npm 11.17.0.
- Package metadata with name `pretty-ms`, version `9.3.0`, `type: "module"`,
  and a root export of `./index.js`; provide `index.d.ts` for the public API.
- A v3 `package-lock.json` that installs with
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- The runtime dependency `parse-ms` at the exact compatible 4.0.0 release.
  Dependencies must be installed by npm and must not be copied into the
  package source.
- JSON-serializable scored calls. The upstream API also accepts `bigint`, but
  BigInt values are outside this task's JSON subprocess boundary; do not
  replace the number behavior with a string-based approximation.

# API Usage Guide

## `import prettyMilliseconds from 'pretty-ms'`

### `prettyMilliseconds(milliseconds, options?)`

Signature: `prettyMilliseconds(milliseconds: number | bigint, options?: Options): string`.
For scored calls, `milliseconds` is a finite JSON number. Negative values keep
their sign, and zero is formatted as `0ms` (or `0 milliseconds` in verbose
mode). Non-finite numbers must throw `TypeError` with the message
`Expected a finite number or bigint`.

The default output uses the largest non-zero units, in descending order:
years (365 days), days, hours, minutes, seconds, and milliseconds. Seconds use
one decimal digit by default, while a sub-second value below 1000ms is shown
as milliseconds unless `subSecondsAsDecimals` is enabled. Examples:
`1337000000` returns `15d 11h 23m 20s`, `1337` returns `1.3s`, and `133`
returns `133ms`.

The optional object accepts these properties:

- `secondsDecimalDigits` (`number`, default `1`): decimal places for seconds;
  truncate using the package's stable decimal behavior.
- `millisecondsDecimalDigits` (`number`, default `0`): decimal places when
  milliseconds are displayed separately or as the sub-second component.
- `keepDecimalsOnWholeSeconds` (`boolean`, default `false`): retain output
  such as `13.0s` instead of `13s`.
- `compact` (`boolean`, default `false`): show only the first unit and force
  both decimal-digit settings to zero. For example, `3661000` becomes `1h`.
- `unitCount` (`number`, default `Infinity`): retain at most this many output
  units; values below one still retain one unit.
- `verbose` (`boolean`, default `false`): use full unit names with correct
  singular/plural forms, such as `1 hour 1 minute 1 second`.
- `separateMilliseconds` (`boolean`, default `false`): show milliseconds as a
  separate unit instead of folding them into seconds.
- `formatSubMilliseconds` (`boolean`, default `false`): show milliseconds,
  microseconds, and nanoseconds as separate units.
- `colonNotation` (`boolean`, default `false`): use zero-padded `:` separators,
  always showing at least minutes, such as `95500` becoming `1:35.5`. It
  overrides `compact`, `verbose`, `separateMilliseconds`, and
  `formatSubMilliseconds`.
- `hideYear` (`boolean`, default `false`): express years as days using 365 days
  per year.
- `hideYearAndDays` (`boolean`, default `false`): express years and days as
  hours.
- `hideSeconds` (`boolean`, default `false`): omit seconds and smaller units.
- `subSecondsAsDecimals` (`boolean`, default `false`): format a sub-second
  duration as decimal seconds, such as `900` becoming `0.9s`.

Options are read without mutating the caller's object. Unknown properties are
ignored. The return value is always a string and does not depend on locale or
the current clock.

# Implementation Notes

Keep the root export and declaration shape intact. Use an exact npm lockfile,
and make the package usable immediately after installation without a build
step. Preserve negative values, BigInt-capable arithmetic in the implementation
where practical, unit ordering, decimal precision, colon padding, verbose
pluralization, and the interactions where `compact` or `colonNotation`
override other options. Do not expose private helpers or test-only exports.
