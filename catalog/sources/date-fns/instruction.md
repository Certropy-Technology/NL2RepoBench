# Project Description

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

The public module is imported with `import dateFns from date-fns`-style ESM
syntax (the package export itself is named below); all scored functions are
named exports and accept JSON-safe date values.

```js
import * as dateFns from 'date-fns';
```

Build an installable ESM npm package named `date-fns` from an empty workspace.
It provides a bounded set of date arithmetic, parsing, formatting, calendar,
predicate, and selection utilities. Evaluation uses a JSON subprocess boundary
and fixes the process timezone to UTC so all local-calendar behavior is
deterministic.

# Supports

- Node.js 24.19.0 and npm 11.17.0.
- Package name `date-fns`, version `4.4.0`, and named ESM exports at the package
  root.
- A committed npm lockfile with `lockfileVersion: 3`.
- No runtime dependencies, lifecycle scripts, workspaces, native addons,
  loaders, registry configuration, or runtime network access.
- Date inputs are ISO-8601 strings or finite Unix timestamps in milliseconds.
  Interval inputs are plain objects and collections are arrays of those JSON
  date values.

# API Usage Guide

Export all functions below from the package root. Functions that return a
`Date` are observed as ISO strings through JSON serialization. An invalid
`Date` serializes as `null`; arrays of dates serialize as arrays of ISO strings.
Unless an exception is stated, inputs in the documented domain return normally.

## Date arithmetic and boundaries

- `addDays(date, amount)` returns a new date shifted by `amount` calendar days.
  Positive and negative integer amounts cross month, year, and leap-day
  boundaries without mutating the input.
- `addMonths(date, amount)` shifts by calendar months. If the source day does
  not exist in the destination month, clamp to that month's final day while
  preserving the UTC time fields.
- `setHours(date, hours)` returns a new date with its UTC hour replaced by the
  integer `hours`; preserve the other fields.
- `differenceInCalendarDays(later, earlier)` returns the signed integer
  difference between UTC calendar dates and ignores time of day.
- `eachDayOfInterval({ start, end }, options?)` returns inclusive UTC day starts.
  Normalize reversed interval endpoints. `options.step` defaults to `1`; use
  its absolute value as the day stride, reverse the result when it is negative,
  and return `[]` when it is zero.
- `startOfWeek(date, options?)` returns the UTC start of the containing week.
  `options.weekStartsOn` accepts integers `0` (Sunday) through `6` (Saturday)
  and defaults to `0`.
- `endOfMonth(date)` returns the last millisecond of the UTC month.

## Parsing and formatting

- `parseISO(value)` accepts an ISO string and returns its date. Supported forms
  include `YYYY-MM-DD`, compact calendar dates, date-times with `Z` or numeric
  offsets, and ISO week dates such as `2014-W02-7`. Impossible or malformed
  input returns an invalid date.
- `formatISO(date, options?)` returns ISO-8601 text. `options.format` is
  `"extended"` (default) or `"basic"`. `options.representation` is
  `"complete"` (default), `"date"`, or `"time"`. Invalid dates throw
  `RangeError`.
- `formatRFC3339(date, options?)` returns RFC 3339 text.
  `options.fractionDigits` is an integer from `0` through `3` and defaults to
  `0`. Invalid dates throw `RangeError`.

## Predicates and selection

- `getISOWeek(date)` returns the ISO week number from `1` through `53`, including
  dates whose ISO week-year differs from the calendar year.
- `isWeekend(date)` returns `true` for UTC Saturday or Sunday. It returns
  `false` for weekdays and invalid dates.
- `isLeapYear(date)` applies Gregorian rules: divisible by 4, except centuries
  not divisible by 400.
- `isWithinInterval(date, { start, end })` compares instants against an inclusive
  interval, normalizes reversed endpoints, and returns `false` for an invalid
  date.
- `min(dates)` and `max(dates)` return new dates representing the earliest and
  latest input instant. An empty array or any invalid member produces an
  invalid date.

# Implementation Notes

Keep every observable operation deterministic under `TZ=UTC` and preserve
input values. The scored JSON boundary intentionally excludes locale and
context objects, custom `Date` subclasses, callbacks, FP modules, browser
builds, CLIs, and TypeScript-only behavior. The package must install and pack
entirely offline with lifecycle scripts disabled.

# Natural Language Instruction

Create `date-fns` from an empty workspace. Implement the documented date
arithmetic, parsing, formatting, calendar predicates, and selection functions
as named root exports. Return fresh date values, preserve UTC determinism, and
keep the package self-contained.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── src/
    ├── arithmetic.js
    ├── calendar.js
    ├── format.js
    ├── parse.js
    └── predicates.js
```

The package root exports every function named in this instruction. The source
module split represents responsibilities; do not add a CLI or runtime
dependency not stated in `package.json`.

# Examples

```js
import {addDays, parseISO, formatISO} from 'date-fns';

const date = addDays(parseISO('2024-02-28'), 1);
formatISO(date, {representation: 'date'});
```

```js
import {eachDayOfInterval} from 'date-fns';

const days = eachDayOfInterval({start: '2024-01-01', end: '2024-01-03'});
```

# Error Handling and Boundary Conditions

Invalid dates produce invalid dates for parsing and predicates as specified;
formatters throw `RangeError` for invalid dates. Reversed intervals and leap
days follow the documented normalization rules. No function may consult the
network, locale, wall clock, or host timezone during evaluation.
