# pendulum

## Project Description

Build an installable `pendulum` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pendulum`; public import package begins at `pendulum`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Constructors and conversion`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Current time and parsing`: preserve the documented object or module behavior, including state and side effects.
3. `Date`, `Time`, and `DateTime`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Durations and intervals`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `pendulum`; public import package begins at `pendulum`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `packaging==26.3`, `python-dateutil==2.9.0.post0`, `setuptools==84.0.0`, `six==1.17.0`, `time-machine==3.5.0`, `tzdata==2026.3`, `wheel==0.46.3`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── an/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

The package root re-exports `Date`, `Time`, `DateTime`, `Duration`, `Interval`,
`Timezone`, `FixedTimezone`, `Formatter`, `WeekDay`, `UTC`, weekday constants
`MONDAY` through `SUNDAY`, transition constants `PRE_TRANSITION`,
`POST_TRANSITION`, and `TRANSITION_ERROR`, and the constructors and helpers
below.

### Constructors and conversion

```python
pendulum.datetime(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0,
    second: int = 0, microsecond: int = 0,
    tz: str | float | datetime.tzinfo | Timezone | FixedTimezone | None = UTC,
    fold: int = 1, raise_on_unknown_times: bool = False,
) -> DateTime
pendulum.local(year, month, day, hour=0, minute=0, second=0, microsecond=0) -> DateTime
pendulum.naive(year, month, day, hour=0, minute=0, second=0, microsecond=0, fold=1) -> DateTime
pendulum.date(year: int, month: int, day: int) -> Date
pendulum.time(hour: int, minute: int = 0, second: int = 0, microsecond: int = 0) -> Time
pendulum.instance(obj: datetime | date | time, tz=UTC) -> DateTime | Date | Time
pendulum.from_timestamp(timestamp: int | float, tz=UTC) -> DateTime
pendulum.from_format(string: str, fmt: str, tz=UTC, locale: str | None = None) -> DateTime
```

`datetime()` returns an aware value by default. Pass `tz=None` or use
`naive()` for a naive value. A timezone string is resolved as an IANA name;
`"local"` selects the configured local timezone. A numeric timezone value is a
fixed offset in seconds. Invalid calendar fields raise the same `ValueError`
subclasses/messages expected from standard datetime construction. Unknown
timezone names raise `pendulum.tz.exceptions.InvalidTimezone`.

Skipped and repeated local times honor `fold`. By default, a skipped time is
normalized to the post-transition instant and a repeated time uses the
post-transition occurrence. With `raise_on_unknown_times=True`, skipped times
raise `NonExistingTime` and repeated times raise `AmbiguousTime`.

```python
>>> pendulum.datetime(2024, 2, 29, 12, 30, tz="Europe/Paris").to_iso8601_string()
'2024-02-29T12:30:00+01:00'
>>> pendulum.datetime(2013, 3, 31, 2, 30, tz="Europe/Paris")
DateTime(2013, 3, 31, 3, 30, 0, tzinfo=Timezone('Europe/Paris'))
```

### Current time and parsing

```python
pendulum.now(tz: str | Timezone | None = None) -> DateTime
pendulum.today(tz: str | Timezone = "local") -> DateTime
pendulum.tomorrow(tz: str | Timezone = "local") -> DateTime
pendulum.yesterday(tz: str | Timezone = "local") -> DateTime
pendulum.parse(text: str, **options) -> Date | Time | DateTime | Duration | Interval
```

`parse()` accepts ISO-8601 dates, times, datetimes, durations, and intervals.
`exact=True` preserves the narrowest type (`Date` or `Time`) instead of
promoting it to `DateTime`. `strict=True` rejects non-ISO fallback formats.
`tz=` supplies the timezone for input without an offset. Invalid text raises
`pendulum.parsing.exceptions.ParserError`.

### `Date`, `Time`, and `DateTime`

These classes subclass their standard-library counterparts. Their
constructors, comparisons, hashing, pickling, `replace()`, and arithmetic must
remain compatible with those base types. They additionally provide immutable,
fluent operations:

```python
value.add(years=0, months=0, weeks=0, days=0, hours=0, minutes=0,
          seconds=0, microseconds=0)
value.subtract(years=0, months=0, weeks=0, days=0, hours=0, minutes=0,
               seconds=0, microseconds=0)
value.set(**components)
value.start_of(unit: str)
value.end_of(unit: str)
value.next(day_of_week: WeekDay | None = None, keep_time: bool = False)
value.previous(day_of_week: WeekDay | None = None, keep_time: bool = False)
value.diff(other=None, abs: bool = True) -> Interval | Duration
value.diff_for_humans(other=None, absolute=False, locale=None, separator=" ") -> str
value.format(fmt: str, locale: str | None = None) -> str
```

Supported boundary units include `second`, `minute`, `hour`, `day`, `week`,
`month`, `quarter`, `year`, `decade`, and `century` where meaningful. Calendar
arithmetic clamps an invalid target day to the final day of the target month;
adding one month to January 31 therefore yields the final day of February.
Datetime arithmetic preserves timezone rules across DST changes rather than
blindly adding an offset.

With no weekday argument, `next()` and `previous()` move to the next or
previous occurrence of the value's current weekday, one week away. Supplying a
weekday chooses that weekday explicitly. Unless `keep_time=True`, these
operations return the start of the selected day.

`DateTime` exposes `int_timestamp`, `float_timestamp`, `offset`,
`offset_hours`, `timezone`, `timezone_name`, `is_local()`, `is_utc()`,
`is_dst()`, `date()`, `time()`, `naive()`, `in_timezone()` (alias `in_tz()`),
and string helpers `to_date_string()`, `to_time_string()`,
`to_datetime_string()`, `to_iso8601_string()`, `to_atom_string()`,
`to_cookie_string()`, `to_rfc822_string()`, `to_rfc850_string()`,
`to_rfc1036_string()`, `to_rfc1123_string()`, `to_rfc2822_string()`,
`to_rfc3339_string()`, `to_rss_string()`, and `to_w3c_string()`.

### Durations and intervals

```python
pendulum.duration(days=0, seconds=0, microseconds=0, milliseconds=0,
                  minutes=0, hours=0, weeks=0, years=0, months=0) -> Duration
pendulum.interval(start: DateTime, end: DateTime, absolute: bool = False) -> Interval
```

`Duration` subclasses `timedelta` while preserving separate calendar `years`
and `months`. It supports normal timedelta arithmetic and exposes
`years`, `months`, `weeks`, `days`, `remaining_days`, `hours`, `minutes`,
`seconds`, `remaining_seconds`, `microseconds`, `total_minutes()`,
`total_hours()`, `total_days()`, `total_weeks()`, `in_weeks()`, `in_days()`,
`in_hours()`, `in_minutes()`, `in_seconds()`, `in_words(locale=None,
separator=" ")`, and `as_timedelta()`.

`Interval` is a `Duration` with immutable `start` and `end` endpoints. It
supports containment, iteration, arithmetic, `range(unit, amount=1)`,
`as_duration()`, and localized `in_words()`. A forward range includes its
start and advances by the requested positive amount without stepping beyond
the end.

### Timezones, locale, and formatting

```python
pendulum.timezone(name: str | int) -> Timezone | FixedTimezone
pendulum.fixed_timezone(offset: int) -> FixedTimezone
pendulum.local_timezone() -> Timezone | FixedTimezone
pendulum.timezones() -> set[str]
pendulum.set_locale(name: str) -> None
pendulum.get_locale() -> str
pendulum.locale(name: str) -> Locale
pendulum.week_starts_at(wday: WeekDay) -> None
pendulum.week_ends_at(wday: WeekDay) -> None
```

Timezone objects implement `tzinfo`, `convert()`, `utcoffset()`, `dst()`, and
`tzname()`. Equal named/fixed zones compare and hash consistently. `set_locale`
and week-boundary helpers update process-local package state and reject unknown
locale names or weekday values outside Monday through Sunday. Formatting uses
Pendulum tokens such as `YYYY`, `MM`, `DD`, `HH`, `mm`, `ss`, `SSSSSS`, `Z`,
`ZZ`, `dddd`, and escaped literals in square brackets. Locale-specific month,
weekday, relative-time, and unit strings must be deterministic.

### Controlled time travel

```python
pendulum.travel_to(dt: DateTime, freeze: bool = False) -> Traveller
pendulum.travel(*, years=0, months=0, weeks=0, days=0, hours=0,
                minutes=0, seconds=0, microseconds=0, freeze=False) -> Traveller
pendulum.freeze() -> Traveller
```

Each helper returns a context manager/decorator backed by `time-machine` when
that optional dependency is installed. It affects `pendulum.now()` only for
the context's lifetime and restores the previous clock even when the body
raises. Without `time-machine`, entering the context raises `NotImplementedError`.


Keep locale and timezone data available from the installed distribution; do
not assume the source tree remains present. Avoid host locale settings and
wall-clock assertions in deterministic operations. Calendar objects are not
directly JSON serializable, so the scored verifier invokes documented API
sequences in an isolated child process and returns only normalized strings,
numbers, booleans, lists, dictionaries, and exception names. Native object
identity, callback objects, arbitrary `tzinfo` subclasses, private helpers,
filesystem probing, and platform-specific local-time discovery are outside the
scored boundary.

Do not include upstream tests, verifier code, reference source, or build caches
in the generated repository.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
pendulum.datetime(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0,
    second: int = 0, microsecond: int = 0,
    tz: str | float | datetime.tzinfo | Timezone | FixedTimezone | None = UTC,
    fold: int = 1, raise_on_unknown_times: bool = False,
) -> DateTime
pendulum.local(year, month, day, hour=0, minute=0, second=0, microsecond=0) -> DateTime
pendulum.naive(year, month, day, hour=0, minute=0, second=0, microsecond=0, fold=1) -> DateTime
pendulum.date(year: int, month: int, day: int) -> Date
pendulum.time(hour: int, minute: int = 0, second: int = 0, microsecond: int = 0) -> Time
pendulum.instance(obj: datetime | date | time, tz=UTC) -> DateTime | Date | Time
pendulum.from_timestamp(timestamp: int | float, tz=UTC) -> DateTime
pendulum.from_format(string: str, fmt: str, tz=UTC, locale: str | None = None) -> DateTime
```

### Example 2: ordinary usage
```text
>>> pendulum.datetime(2024, 2, 29, 12, 30, tz="Europe/Paris").to_iso8601_string()
'2024-02-29T12:30:00+01:00'
>>> pendulum.datetime(2013, 3, 31, 2, 30, tz="Europe/Paris")
DateTime(2013, 3, 31, 3, 30, 0, tzinfo=Timezone('Europe/Paris'))
```

### Example 3: boundary or error behavior
```text
pendulum.now(tz: str | Timezone | None = None) -> DateTime
pendulum.today(tz: str | Timezone = "local") -> DateTime
pendulum.tomorrow(tz: str | Timezone = "local") -> DateTime
pendulum.yesterday(tz: str | Timezone = "local") -> DateTime
pendulum.parse(text: str, **options) -> Date | Time | DateTime | Duration | Interval
```

### Example 4: boundary or error behavior
```text
value.add(years=0, months=0, weeks=0, days=0, hours=0, minutes=0,
          seconds=0, microseconds=0)
value.subtract(years=0, months=0, weeks=0, days=0, hours=0, minutes=0,
               seconds=0, microseconds=0)
value.set(**components)
value.start_of(unit: str)
value.end_of(unit: str)
value.next(day_of_week: WeekDay | None = None, keep_time: bool = False)
value.previous(day_of_week: WeekDay | None = None, keep_time: bool = False)
value.diff(other=None, abs: bool = True) -> Interval | Duration
value.diff_for_humans(other=None, absolute=False, locale=None, separator=" ") -> str
value.format(fmt: str, locale: str | None = None) -> str
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
