# Project Description

Implement `python-dateutil` as an installable Python package named
`python-dateutil`. It extends the standard library's `datetime` types with
date parsing, calendar arithmetic, recurrence rules, Easter calculations, and
time-zone helpers.

The package must expose the public modules and names described below from the
`dateutil` import package. Keep behavior deterministic and do not require
network access, a database, a service, or a platform-specific GUI.

# Natural Language Instruction

Create the `python-dateutil` project from an empty `workspace/`. Implement the
installable `dateutil` package and its public parsing, calendar, recurrence,
Easter, and time-zone APIs described below. Preserve Python datetime types,
timezone awareness, ordering, exception identity, and deterministic behavior.
The implementation must be usable through the documented import paths and must
include bundled zone data rather than consulting an external service.

The required capability groups are date-string parsing, ISO parsing, calendar
arithmetic, RFC 5545 recurrence generation, Easter calculation, and fixed or
named timezone handling. Keep the package independent of a database, network,
GUI, current locale, and machine-specific filesystem paths.

# Supports

- Python 3.12 on Linux.
- A normal PEP 517 or setuptools installation from the repository root.
- Runtime dependency `six` may be declared, but the finished package must
  install successfully with dependencies already available.
- The package layout must use the import name `dateutil` and include its
  bundled zone information data.

# Project Directory Structure

```text
workspace/
├── setup.py or pyproject.toml
├── dateutil/
│   ├── __init__.py
│   ├── parser/__init__.py
│   ├── relativedelta.py
│   ├── rrule.py
│   ├── easter.py
│   ├── tz/
│   │   ├── __init__.py
│   │   └── tz.py
│   └── zoneinfo/
│       └── __init__.py
└── README.md
```

The package root and the listed modules are public import locations. Include
only the zone information resources needed by the documented `gettz` behavior;
do not add verifier or private evaluation files to the generated project.

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

# Examples

```python
from datetime import datetime
from dateutil.parser import isoparse

value = isoparse("2024-01-02T03:04:05Z")
assert value.tzinfo is not None
```

```python
from datetime import date
from dateutil.relativedelta import relativedelta

date(2024, 1, 31) + relativedelta(months=1)  # February month-end is clamped
```

```python
from dateutil.rrule import DAILY, rrule

list(rrule(DAILY, count=3, dtstart=datetime(2024, 1, 1)))
```

# Error Handling and Boundary Conditions

- `parse` and `isoparse` must raise the documented parser exception for
  malformed strings; they must not silently return a guessed unrelated date.
- Naive input remains naive unless a timezone is explicitly supplied. A `Z` or
  numeric offset creates an aware datetime with the corresponding offset.
- Month arithmetic clamps a day to the last valid day of the target month.
  Recurrence iterables must remain ordered and finite when `count`, `until`, or
  another end condition is supplied.
- `easter` rejects unsupported method values. DST helpers distinguish ordinary,
  ambiguous, and nonexistent local times, and `resolve_imaginary` returns a
  valid adjusted datetime without network access.
- All agent, candidate, verifier, Oracle, and controls execution is NoNetwork;
  no API call may fetch timezone data or metadata at runtime.
