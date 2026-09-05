# Project Description

Create a complete, installable Python project named `arrow` from an empty
workspace. It is a pure-Python date and time library that provides an aware
`Arrow` value type, flexible constructors, timezone conversion, formatting,
parsing, relative shifting, spans and ranges, and localized human-readable
descriptions. Reproduce the observable behavior of the pinned Arrow revision,
not a simplified datetime wrapper.

## Project Description

The frozen distribution reports version `1.4.0`. The package provides one convenient, timezone-aware value type around
`datetime.datetime`. Values are UTC by default, preserve timezone information,
and expose normal datetime-like properties and arithmetic while adding parsing,
formatting, relative calendar shifts, humanization, and range/span helpers.
The package must be importable as `arrow` and must expose the public module API
described below. Normal operations are deterministic and local; they do not
access a network, service, subprocess, or project files.

# Natural Language Instruction

Create the `arrow` project from an empty `workspace/`. Build an installable implementation, not a loose demonstration script. The public API guide below is the complete source of the task contract; preserve its import paths, signatures, return shapes, ordering, state changes, and exceptions.

Required capabilities:
- timezone-aware Arrow values: implement the documented public behavior and preserve its input/output and error contract.
- construction and timezone conversion: implement the documented public behavior and preserve its input/output and error contract.
- formatting and parsing: implement the documented public behavior and preserve its input/output and error contract.
- relative shifts, spans, ranges, and locales: implement the documented public behavior and preserve its input/output and error contract.

Do not copy an upstream checkout or tests. Keep behavior deterministic and local, and make the package usable from the installation layout described below. The principal public entry points include: `str(value)`, `repr(value)`, `replace(**kwargs)`, `clone()`.

# Supports

- Support CPython 3.8 and newer Python 3.x versions, with the evaluation image
  using Python 3.12 on Linux amd64.
- Use an installable package layout and declare runtime dependencies only on
  `python-dateutil`, `six`, and `tzdata` (the latter is needed on Python 3.9+).
  Do not depend on a preinstalled copy of Arrow or on runtime network access.
- Expose `arrow.__version__`, `arrow.__all__`, `Arrow`, `ArrowFactory`,
  `get`, `now`, and `utcnow` from the package root. The factory helper is
  available as `arrow.api.factory`; the `arrow.factory` module is also public.
  Also expose the
  `arrow.api`, `arrow.arrow`, `arrow.constants`, `arrow.factory`,
  `arrow.formatter`, `arrow.locales`, `arrow.parser`, and `arrow.util` modules.
- Keep timezone behavior aware. A missing timezone means UTC for direct
  constructors and UTC-oriented parsing; explicit timezone strings and tzinfo
  objects must be honored.
- The project must install and import without evaluation-only files being present.


## NoNetwork boundary

Agent, candidate, verifier, Oracle, controls, and normal runtime execution are network-isolated. Do not access GitHub, package registries, Go proxies, DNS, or external services during execution; use only the frozen local build inputs.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── arrow/
    ├── __init__.py
    ├── api.py
    ├── arrow.py
    ├── factory.py
    ├── formatter.py
    ├── parser.py
    ├── locales.py
    ├── util.py
    └── constants.py
```

# API Usage Guide

### Root constructors and factory

`arrow.get(*args, locale="en_us", tzinfo=None, normalize_whitespace=False)`
returns an `Arrow`. With no positional arguments it returns the current UTC
time. It accepts an Arrow, aware or naive `datetime`, `date`, `time.struct_time`,
numeric timestamp, ISO string, or ISO calendar tuple `(year, week, weekday)`.
It also accepts `(datetime_or_date, timezone)` and `(text, format_or_formats)`.
Three or more positional date-time components are passed to the Arrow
constructor. Invalid arity or input types raise `TypeError`; invalid date/time
text raises the documented parser/value exception rather than silently
coercing it. `tzinfo` may be a `datetime.tzinfo` or a timezone expression such
as `"UTC"`, `"US/Pacific"`, `"Europe/Berlin"`, `"local"`, or `"+05:30"`.

`arrow.utcnow()` returns the current UTC Arrow. `arrow.now(tz=None)` returns
the current time in the supplied timezone, or local time when omitted.
`arrow.api.factory(ArrowSubclass)` returns an `ArrowFactory`; its `get`, `now`,
and `utcnow` methods mirror the root functions and construct the selected class.

### Arrow values

Import path: `arrow.Arrow`.

`Arrow(year, month, day, hour=0, minute=0, second=0, microsecond=0,
tzinfo=None, **kwargs)` constructs an aware value. It exposes the datetime
properties `year`, `month`, `day`, `hour`, `minute`, `second`, `microsecond`,
`tzinfo`, `fold`, `date`, `time`, and `datetime`, plus `utcoffset`,
`dst`, `tzname`, `timestamp`, `utctimetuple`, `timetuple`, `isocalendar`,
and `toordinal`. `str(value)` is the ISO-8601 datetime text with a `T`
separator and timezone offset; `repr(value)` is `<Arrow [ISO-8601 text]>`.
Values compare by instant where Python datetime
values do, and support addition/subtraction with `timedelta`; subtracting two
Arrow values returns a `timedelta`.

Class methods `fromtimestamp`, `utcfromtimestamp`, `fromdatetime`, `fromdate`,
`fromordinal`, and `strptime` construct values from their corresponding
standard-library representations. `replace(**kwargs)` returns a new Arrow;
`clone()` returns an equivalent value; `to(tz)` converts the instant to a new
timezone and `to UTC`/`to GMT` are accepted case-insensitively. `naive` returns
the timezone-free datetime copy.

### Relative operations and intervals

`shift(**kwargs)` returns a new value after applying relative calendar or
fixed-time offsets such as `years`, `months`, `weeks`, `days`, `hours`,
`minutes`, `seconds`, `microseconds`, and weekday selectors such as
`weekday=0` or `weekday=MO(+1)`. Calendar month ends clamp to a valid day.
`floor(frame)` and `ceil(frame)` accept `second`, `minute`, `hour`, `day`,
`week`, `month`, `quarter`, and `year` and return a new Arrow.

`span(frame, count=1, bounds="[)")` returns `(start, end)` for one interval;
`span_range(frame, start, end, bounds="[)")` yields intervals across a range;
`range(frame, start, end, limit=None)` yields Arrow values at frame steps.
The helpers `interval(frame, start, end, interval=1, bounds="[)")` and
`span_range` preserve chronological ordering and use the documented inclusive
or exclusive bounds.

### Formatting, parsing, and locales

`format(fmt="YYYY-MM-DD HH:mm:ssZZ", locale="en_us")` uses Arrow tokens such
as `YYYY`, `MM`, `DD`, `HH`, `mm`, `ss`, `SSS`, `Z`, `ZZ`, `ZZZ`, `X`, `x`,
`dddd`, `ddd`, `MMMM`, `MMM`, `Do`, `A`, and `a`. Text in square brackets is
literal. `for_json()` returns an ISO string. `humanize(other=None, locale="en_us",
granularity="auto", only_distance=False, threshold=10)` describes the
relative distance in the selected locale; `dehumanize(text, locale="en_us")`
shifts from the value by a natural-language duration. Invalid locale names
raise `ValueError`.

`arrow.parser.DateTimeParser(locale="en_us", cache_size=0)` exposes `parse`,
`parse_iso`, and `parse_time` for format-driven and ISO parsing. `arrow.locales`
provides `get_locale(name)` and `get_locale_by_class_name(name)` plus locale
classes and their `describe`/`day_name`/`month_name` behavior. `arrow.formatter`
provides `DateTimeFormatter` for token formatting.

### Utility and module contracts

`arrow.util.next_weekday`, `is_timestamp`, `validate_ordinal`,
`normalize_timestamp`, `iso_to_gregorian`, and `validate_bounds` are public
helpers with ordinary Python return types and validation exceptions. Constants
such as `DEFAULT_LOCALE` and the public time-frame maps are available from
`arrow.constants`. Preserve the module re-exports and exception classes.

# Implementation Notes

- Keep the `Arrow` value immutable from the caller's perspective: operations
  return new values and do not mutate the original datetime.
- Preserve timezone offsets when formatting and convert instants correctly
  across DST-aware `dateutil`/`zoneinfo` timezones. Do not implement timezone
  names with a fixed-offset-only lookup.
- Preserve deterministic ordering for ranges, spans, locale names, and parser
  format alternatives. Do not use current time in scored scenarios.
- Match the standard datetime protocol for valid inputs and raise clear
  `TypeError`, `ValueError`, or parser exceptions for invalid inputs. Do not
  add a CLI, server, or unrelated command-line behavior.
- Keep the package's public root small and compatible with the documented
  `__all__`; private helpers may be organized across modules but must not be
  required by the evaluation environment.

# Examples

## Ordinary construction and shifting

```python
import arrow

value = arrow.get(2024, 1, 2, tzinfo="UTC")
tomorrow = value.shift(days=1)
```

## Ordinary formatting and range

```python
import arrow

label = value.format("YYYY-MM-DD HH:mm:ss ZZ")
days = list(arrow.Arrow.range("day", value, tomorrow))
```

## Boundary: invalid locale

```python
value.humanize(locale="not-a-locale")  # raises ValueError
```

## Boundary: immutable-style operation

```python
shifted = value.shift(hours=1)
assert shifted is not value
```

# Error Handling and Boundary Conditions

Reject invalid inputs using the documented exception or error result. Preserve empty-input behavior, ordering, Unicode/encoding behavior, cancellation or timeout semantics, and local filesystem boundaries where the API specifies them. Never turn a failed local operation into a network request, subprocess, or silent success.
