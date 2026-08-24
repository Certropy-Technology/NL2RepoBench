# Project Description

Build an installable ESM npm package named `date-fns` from an empty workspace.
The package provides deterministic, timezone-independent date utilities for
JSON callers. The scored contract is a bounded public slice of the upstream
`date-fns` package.

# Supports

- Node.js 24.19.0 and npm 11.17.0.
- Package name `date-fns`, version `4.4.0`, and an ESM package root export.
- A committed npm lockfile with `lockfileVersion: 3`.
- No runtime dependencies, lifecycle scripts, workspaces, native addons,
  loaders, registry configuration, or network access.
- The verifier runs with `TZ=UTC`; date-only and local-calendar operations are
  therefore deterministic.

# API Usage Guide

Export these named functions from the package root. Every date argument is
either an ISO-8601 string or a finite Unix timestamp in milliseconds. Plain
objects and arrays in the examples contain only JSON values. A returned `Date`
is observed through the JSON boundary as its ISO string; an invalid `Date` is
observed as `null`.

## Date arithmetic and boundaries

- `addDays(date, amount)` returns a new date shifted by the integer day amount
  without mutating the input. Month and leap-year boundaries must be handled.
- `addMonths(date, amount)` shifts by calendar months and clamps an overflowing
  day to the last day of the destination month.
- `setHours(date, hours)` returns a new date with the UTC hour replaced and the
  other fields preserved.
- `differenceInCalendarDays(later, earlier)` returns the signed difference
  between the UTC calendar dates, ignoring time-of-day.
- `eachDayOfInterval({ start, end }, options?)` returns an inclusive array of
  UTC day starts. `options.step` defaults to 1; its magnitude selects the
  number of calendar days between entries, and a negative step reverses the
  produced array.
- `startOfWeek(date, options?)` returns the UTC start of the week. The optional
  `weekStartsOn` is an integer from 0 (Sunday) through 6 (Saturday), defaulting
  to Sunday.
- `endOfMonth(date)` returns the last millisecond of the UTC month.

## Parsing and formatting

- `parseISO(value)` parses the supported ISO calendar forms, including
  `YYYY-MM-DD`, compact calendar dates, date-times with `Z` or a numeric offset,
  and ISO week dates such as `2014-W02-7`. Invalid input returns an invalid
  date, observed as `null`.
- `formatISO(date, options?)` returns ISO-8601 text. `options.format` is
  `"extended"` or `"basic"`, defaulting to `"extended"`; `options.representation`
  is `"complete"`, `"date"`, or `"time"`, defaulting to `"complete"`.
- `formatRFC3339(date, options?)` returns RFC 3339 text. `fractionDigits` is an
  integer from 0 through 3 and defaults to 0.

## Predicates and selection

- `getISOWeek(date)` returns the ISO week number from 1 through 53.
- `isWeekend(date)` returns true for UTC Saturday or Sunday and false for an
  invalid date.
- `isLeapYear(date)` returns whether the UTC year is a Gregorian leap year.
- `isWithinInterval(date, { start, end })` returns true when the instant is
  within the inclusive interval and false otherwise.
- `min(dates)` and `max(dates)` return a new date representing the earliest or
  latest valid input in the array. An empty array is observed as `null`.

# Implementation Notes

Keep the package usable through the root ESM export and keep all observable
behavior deterministic under UTC. Preserve input objects and dates. The
JSON-only boundary intentionally excludes locale objects, context functions,
custom `Date` subclasses, callbacks, FP modules, browser builds, CLI behavior,
and the upstream TypeScript type-level tests. Do not add a dependency or a
build step that requires downloading tools or running lifecycle scripts.
