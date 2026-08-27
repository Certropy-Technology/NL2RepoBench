# Project Description

Implement `python-dateutil` as an installable Python package named
`python-dateutil`. It extends the standard library's `datetime` types with
date parsing, calendar arithmetic, recurrence rules, Easter calculations, and
time-zone helpers.

The package must expose the public modules and names described below from the
`dateutil` import package. Keep behavior deterministic and do not require
network access, a database, a service, or a platform-specific GUI.

# Supports

- Python 3.12 on Linux.
- A normal PEP 517 or setuptools installation from the repository root.
- Runtime dependency `six` may be declared, but the finished package must
  install successfully with dependencies already available.
- The package layout must use the import name `dateutil` and include its
  bundled zone information data.

# API Usage Guide

## Parsing

From `dateutil.parser`, provide `parse(timestr, **kwargs)`, `isoparse(timestr)`,
the `parser` class, and `ParserError`. `parse` accepts common human-readable
date/time strings and returns a `datetime.datetime`; it supports keyword
options such as `fuzzy`, `dayfirst`, and `yearfirst`. Invalid input raises a
dateutil parser error rather than silently returning an unrelated date.

`isoparse` accepts ISO-8601 date and date-time forms, including `Z` and numeric
offsets, and returns a `datetime.datetime` with the corresponding timezone
when the input is aware.

## Calendar arithmetic

From `dateutil.relativedelta`, provide `relativedelta` and weekday constants
`MO`, `TU`, `WE`, `TH`, `FR`, `SA`, and `SU`. A relativedelta can be added to or
subtracted from a `date` or `datetime`. Relative fields such as months, days,
hours, and minutes must normalize correctly; absolute fields and weekday
selectors must follow calendar semantics, including clamping a month-end date
when the target month is shorter.

## Recurrence rules

From `dateutil.rrule`, provide `rrule`, `rruleset`, `rrulestr`, frequency
constants such as `DAILY`, `WEEKLY`, and `MONTHLY`, and weekday constants such
as `MO`. Rules produce an ordered iterable of dates. `count`, `interval`,
`byweekday`, `bymonthday`, `dtstart`, and RFC 5545 rule strings must work
together, and an `rruleset` must support adding inclusions and exclusions.

## Easter

`dateutil.easter.easter(year, method=3)` returns the Easter date for the
requested year. Methods 1, 2, and 3 represent the supported Western and
Orthodox calculation conventions and must reject unsupported methods.

## Time zones

From `dateutil.tz`, provide `UTC`/`tzutc`, `tzoffset`, `gettz`, `tzrange`,
`tzstr`, `datetime_ambiguous`, `datetime_exists`, `resolve_imaginary`, and
`enfold`. Named zones must produce correct offsets for the requested date;
fixed offsets must preserve their sign and name; DST helpers must distinguish
ambiguous, nonexistent, and ordinary local times.

# Implementation Notes

- Preserve normal Python equality, hashing, iteration, and `repr` behavior for
  the public value objects where those operations are meaningful.
- Naive datetimes remain naive unless the API explicitly requests or supplies
  timezone information.
- Iterators and recurrence rules must be ordered and finite when a count or
  end condition is supplied.
- Do not copy the upstream implementation into the instruction or depend on
  the reference repository being reachable at runtime.
